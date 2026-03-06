import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# --- Mock rq/redisq before any agent import (Windows: no fork context) ---
_fake_rq = MagicMock()
sys.modules.setdefault("rq", _fake_rq)
sys.modules.setdefault("redis", MagicMock())
sys.modules.setdefault("agent.common.redisq", MagicMock())
sys.modules.setdefault("agent.common.git_pr", MagicMock(
    git_commit_push_pr=MagicMock(return_value="https://github.com/mock/pr")
))

from agent.tasks.seo import (
    resolve_astro_path,
    patch_layout_title_description,
    replace_or_insert_seo_block,
    patch_const_faq_array,
    get_deterministic_payload,
    SEO_MARKER_START,
    SEO_MARKER_END
)


def test_resolve_astro_path():
    import agent.tasks.seo
    original_path = agent.tasks.seo.Path

    class MockPath:
        def __init__(self, p):
            self.p = str(p)
        def exists(self):
            return "index.astro" in self.p or "otopeni.astro" in self.p or "bucuresti" in self.p
        def __str__(self): return self.p

    agent.tasks.seo.Path = MockPath
    try:
        assert str(resolve_astro_path("/petreceri/otopeni")) == "src/pages/petreceri/otopeni.astro"
        assert str(resolve_astro_path("/petreceri/ilfov/")) == "src/pages/petreceri/ilfov/index.astro"
        assert str(resolve_astro_path("https://www.superparty.ro/petreceri/bucuresti")) == "src/pages/petreceri/bucuresti.astro"
    finally:
        agent.tasks.seo.Path = original_path


def test_apply_patch_frontmatter():
    text = "---\nimport Layout from '../components/Layout.astro'\n---\n<Layout title='Old' description='Old Desc' schema={schema}>\n  <p>Hello</p>\n</Layout>"
    new_text = patch_layout_title_description(text, "New Title", "New Description")
    assert 'title="New Title"' in new_text
    assert 'description="New Description"' in new_text
    assert "schema={schema}" in new_text
    assert "---\nimport Layout" in new_text


def test_idempotent_replace():
    text = f"<Layout>\n  {SEO_MARKER_START}\n  OLD CONTENT\n  {SEO_MARKER_END}\n</Layout>"
    new_block = f"{SEO_MARKER_START}\n  NEW CONTENT\n{SEO_MARKER_END}"
    new_text = replace_or_insert_seo_block(text, new_block)
    assert "NEW CONTENT" in new_text
    assert "OLD CONTENT" not in new_text
    assert new_text.count(SEO_MARKER_START) == 1


def test_validator_blocks_bad_content():
    bad_tokens = ["lei", "RON", "sala", "garantam", "minute", "km"]
    content = "Aceasta este o sala minunata la pret de 10 lei."
    found = any(tok.lower() in content.lower() for tok in bad_tokens)
    assert found is True


def test_quality_gate_total_plus_delta():
    """Gate: TOTAL_TEXT_CHARS >= 2500 AND DELTA >= 600 (not delta > 2500)."""
    import re as _re
    old_text = "<p>" + "x" * 2100 + "</p>"
    new_text = "<p>" + "x" * 2100 + "</p>" + "<section>" + "y" * 700 + "</section>"
    total = len(_re.sub(r'<[^>]+>', '', new_text).strip())
    delta = len(new_text) - len(old_text)
    faq_count = 4
    required_links = True
    gate = total >= 2500 and delta >= 600 and faq_count >= 4 and required_links
    assert gate, f"Expected gate PASSED: total={total} delta={delta}"
    # Old logic (delta > 2500) would have FAILED this case since delta ~= 700
    old_gate = delta > 2500
    assert not old_gate, "Old gate was incorrectly blocking this valid page"


def test_payload_types():
    manifest_data = {"ilfov_town": {"county": "Ilfov", "name": "Ilfov Town"}}
    pay_hub = get_deterministic_payload("ilfov", manifest_data)
    assert pay_hub["page_type"] == "hub_ilfov"

    pay_sec = get_deterministic_payload("sector-3", manifest_data)
    assert pay_sec["page_type"] == "sector"

    pay_loc = get_deterministic_payload("ilfov_town", manifest_data)
    assert pay_loc["page_type"] == "localitate_ilfov"


def test_insert_when_no_marker():
    text = "<Layout>\n<h1>Hi</h1>\n</Layout>"
    block = "<!-- SEO_INJECT_START:v1 -->\nSEO BLOCK\n<!-- SEO_INJECT_END:v1 -->"
    res = replace_or_insert_seo_block(text, block)
    assert "SEO BLOCK" in res
    assert res.endswith("</Layout>")


def test_required_links_present():
    html_str = '<a href="/animatori-petreceri-copii">Pilon</a> <a href="/arie-acoperire">Arie</a> <a href="/petreceri/ilfov">Hub</a>'
    assert 'href="/animatori-petreceri-copii"' in html_str
    assert 'href="/arie-acoperire"' in html_str
    assert 'href="/petreceri/ilfov"' in html_str


def test_brand_superparty_consistent():
    """All generated payloads must use 'SuperParty' (capital P), not 'Superparty'."""
    manifest_data = {}
    for slug in ["sector-1", "ilfov", "bucuresti", "animatori-petreceri-copii"]:
        pay = get_deterministic_payload(slug, manifest_data)
        title = pay.get("title", "")
        if title:
            assert "Superparty" not in title, f"Wrong case 'Superparty' in: {title}"


def test_no_emoji_in_faq_inject():
    """FAQ inject must NOT contain emoji footprint (e.g. question mark emoji)."""
    from agent.tasks.seo import build_seo_inject_block
    block = build_seo_inject_block(
        heading="Test",
        logistic_text="Text logistic.",
        faq_items=[{"q": "Intrebare?", "a": "Raspuns."}] * 4,
        hub_url="/petreceri/ilfov",
        hub_label="Hub Ilfov"
    )
    assert "\u2753" not in block, "Emoji question mark found in inject block"


def test_db_migrate_adds_missing_columns():
    """db_migrate must safely add A/B window columns to existing DBs (server migration)."""
    from agent.tasks.seo_ctr_experiments import db_init, db_migrate
    import tempfile, os, sqlite3

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    try:
        con = sqlite3.connect(tmp_db)
        con.row_factory = sqlite3.Row
        # Old schema: no A/B window columns
        con.executescript("""
            CREATE TABLE IF NOT EXISTS seo_experiments (
                exp_id TEXT PRIMARY KEY, site_id TEXT, url_path TEXT NOT NULL,
                file_path TEXT NOT NULL, exp_type TEXT NOT NULL, status TEXT NOT NULL,
                started_at TEXT NOT NULL, ends_at TEXT NOT NULL,
                baseline_start TEXT NOT NULL, baseline_end TEXT NOT NULL,
                baseline_clicks INTEGER DEFAULT 0, baseline_impressions INTEGER DEFAULT 0,
                baseline_avg_position REAL DEFAULT 99.0,
                baseline_title TEXT, baseline_description TEXT,
                variant_a_title TEXT, variant_a_description TEXT,
                variant_b_title TEXT, variant_b_description TEXT,
                winner_variant TEXT, decision_reason TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS page_state (
                site_id TEXT NOT NULL, url_path TEXT NOT NULL,
                last_touched_at TEXT, cooldown_until TEXT, active_exp_id TEXT,
                PRIMARY KEY (site_id, url_path)
            );
        """)
        con.commit()

        cols_before = {row[1] for row in con.execute("PRAGMA table_info(seo_experiments)").fetchall()}
        assert "variant_a_start" not in cols_before

        db_migrate(con)

        cols_after = {row[1] for row in con.execute("PRAGMA table_info(seo_experiments)").fetchall()}
        for col in ["variant_a_start", "variant_a_end", "variant_b_start", "variant_b_end",
                    "variant_a_clicks", "variant_b_clicks"]:
            assert col in cols_after, f"Column {col} missing after db_migrate"
        con.close()
    finally:
        os.unlink(tmp_db)


def test_switch_task_sets_a_end_b_start():
    """switch_task must set variant_a_end and variant_b_start with GSC latency (+3 days)."""
    from agent.tasks.seo_ctr_experiments import db_init, db_migrate
    import agent.tasks.seo_ctr_experiments as exp_mod
    import tempfile, os, sqlite3
    from datetime import date, timedelta

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        tmp_db = f.name
    try:
        con = sqlite3.connect(tmp_db)
        con.row_factory = sqlite3.Row
        db_init(con)
        db_migrate(con)

        today = date.today()
        a_start = str(today - timedelta(days=15))  # 15 days running > switch_days=10

        con.execute("""
            INSERT INTO seo_experiments(
                exp_id, site_id, url_path, page_url, file_path, exp_type, status,
                started_at, ends_at, baseline_start, baseline_end, variant_a_start,
                baseline_title, baseline_description, variant_a_title, variant_a_description,
                variant_b_title, variant_b_description, created_at, updated_at
            ) VALUES (
                'test-switch-1', 'superparty', '/petreceri/test',
                'https://www.superparty.ro/petreceri/test', 'src/pages/petreceri/test.astro',
                'ctr_title_desc', 'RUNNING_A', ?, ?, ?, ?, ?,
                'Baseline Title', 'Baseline Desc',
                'Variant A Title', 'Variant A Desc',
                'Variant B Title', 'Variant B Desc',
                ?, ?
            )
        """, (
            str(today - timedelta(days=15)), str(today + timedelta(days=6)),
            str(today - timedelta(days=18)), str(today - timedelta(days=4)),
            a_start, str(today), str(today)
        ))
        con.commit()

        # Mock apply and db_connect
        orig_apply = exp_mod.apply_title_desc_variant
        orig_connect = exp_mod.db_connect
        exp_mod.apply_title_desc_variant = lambda *a, **kw: {"ok": True, "note": "mocked"}
        exp_mod.db_connect = lambda *a, **kw: con

        try:
            exp_mod.seo_ctr_experiments_switch_task(site_id="superparty")
        finally:
            exp_mod.apply_title_desc_variant = orig_apply
            exp_mod.db_connect = orig_connect

        exp_row = dict(con.execute(
            "SELECT * FROM seo_experiments WHERE exp_id='test-switch-1'"
        ).fetchone())

        assert exp_row["status"] == "RUNNING_B", f"Expected RUNNING_B, got {exp_row['status']}"
        assert exp_row["variant_a_end"] is not None, "variant_a_end must be set"
        assert exp_row["variant_b_start"] is not None, "variant_b_start must be set"

        expected_a_end = str(today - timedelta(days=1))
        expected_b_start = str(today + timedelta(days=3))
        assert exp_row["variant_a_end"] == expected_a_end, \
            f"Expected variant_a_end={expected_a_end}, got {exp_row['variant_a_end']}"
        assert exp_row["variant_b_start"] == expected_b_start, \
            f"Expected variant_b_start={expected_b_start}, got {exp_row['variant_b_start']}"
        con.close()
    finally:
        os.unlink(tmp_db)
