"""
tests/test_adapters.py — Suite de teste pentru adapters

Teste pentru:
  - SiteAdapter ABC contract
  - SuperPartyAdapter: path classification, pillar/money, Tier C
  - AnimatopiaAdapter: path classification, editorial guard, pillar/money
  - core/run_readiness: adapter-aware
  - core/run2_planner: adapter-aware
"""
import json
import uuid
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta, timezone

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters.superparty.adapter import SuperPartyAdapter
from adapters.animatopia.adapter import AnimatopiaAdapter, COMMERCIAL_THRESHOLD
from core.run_readiness import generate_run_readiness_report
from core.run2_planner import generate_run2_candidates


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_sp_adapter(tmp_path: Path) -> SuperPartyAdapter:
    """SuperPartyAdapter cu structura minimala in tmp_path."""
    (tmp_path / "config" / "seo").mkdir(parents=True)
    (tmp_path / "reports" / "superparty").mkdir(parents=True)
    (tmp_path / "src" / "pages" / "petreceri").mkdir(parents=True)
    # Pillar registry minimal
    registry = {"pillar_pages": ["/animatori-petreceri-copii", "/acasa"]}
    (tmp_path / "config" / "seo" / "pillar_pages_registry.json").write_text(
        json.dumps(registry), encoding="utf-8"
    )
    return SuperPartyAdapter(superparty_root=tmp_path)


def _make_at_adapter(tmp_path: Path) -> AnimatopiaAdapter:
    """AnimatopiaAdapter cu structura minimala."""
    (tmp_path / "src" / "content" / "articole").mkdir(parents=True)
    (tmp_path / "reports" / "animatopia").mkdir(parents=True)
    return AnimatopiaAdapter(animatopia_root=tmp_path)


def _make_experiment(
    url="/test/pagina",
    result_label="pending",
    rollback=False,
    applied_days_ago=0,
    observation_window_days=14,
    impressions_after=None,
):
    now = datetime.now(timezone.utc)
    applied_at = now - timedelta(days=applied_days_ago)
    deadline = applied_at + timedelta(days=observation_window_days)
    return {
        "experiment_id": str(uuid.uuid4()),
        "url": url,
        "applied_at": applied_at.isoformat(),
        "strategy": "local_intent",
        "before_meta": "Vechi.",
        "after_meta": "Nou.",
        "observation_window_days": observation_window_days,
        "observation_deadline": deadline.isoformat(),
        "gsc_before": {"impressions": None},
        "gsc_after": {"impressions": impressions_after},
        "result_label": result_label,
        "rollback_happened": rollback,
    }


def _write_memory(adapter, experiments: list):
    path = adapter.reports_dir / "seo_level6_outcome_memory.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(experiments), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SITE ADAPTER ABC
# ═══════════════════════════════════════════════════════════════════════════════

class TestSiteAdapterABC:

    def test_superparty_adapter_implements_abc(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert adapter.site_id == "superparty"
        assert "superparty.ro" in adapter.site_domain

    def test_animatopia_adapter_implements_abc(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert adapter.site_id == "animatopia"
        assert "animatopia.ro" in adapter.site_domain

    def test_describe_returns_required_fields(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        desc = adapter.describe()
        required = ["site_id", "site_domain", "reports_dir", "config_dir"]
        for f in required:
            assert f in desc

    def test_normalize_url_strips_domain(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert adapter.normalize_url("https://www.superparty.ro/petreceri/test") == "/petreceri/test"
        assert adapter.normalize_url("/petreceri/test/") == "/petreceri/test"

    def test_is_blocked_returns_tuple(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        blocked, reasons = adapter.is_blocked("/animatori-petreceri-copii")
        assert blocked is True
        assert "pillar_page" in reasons


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SUPERPARTY ADAPTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestSuperPartyAdapter:

    def test_pillar_page_detected_from_registry(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert adapter.is_pillar_page("/animatori-petreceri-copii")

    def test_non_pillar_not_detected(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert not adapter.is_pillar_page("/petreceri/voluntari")

    def test_money_page_detected(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert adapter.is_money_page("/animatori-petreceri-copii")
        assert adapter.is_money_page("/contact")

    def test_tier_c_petreceri_eligible(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert adapter.is_tier_c_eligible("/petreceri/voluntari")
        assert adapter.is_tier_c_eligible("/petreceri/otopeni")

    def test_tier_c_excludes_root(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert not adapter.is_tier_c_eligible("/")

    def test_tier_c_excludes_pillar(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert not adapter.is_tier_c_eligible("/animatori-petreceri-copii")

    def test_tier_c_excludes_money(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert not adapter.is_tier_c_eligible("/contact")

    def test_get_page_type_pillar(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert adapter.get_page_type("/animatori-petreceri-copii") == "pillar"

    def test_get_page_type_tier_c(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert adapter.get_page_type("/petreceri/voluntari") == "tier_c"

    def test_tier_c_catalog_returns_list(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        catalog = adapter.get_tier_c_catalog()
        assert isinstance(catalog, list)
        assert all("url" in c and "suggested_strategy" in c for c in catalog)

    def test_extract_meta_from_astro_file(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        astro_file = tmp_path / "src" / "pages" / "petreceri" / "test.astro"
        astro_file.write_text(
            '<Layout description="Animatori pentru copii in Test, Ilfov. 0722 744 377." />',
            encoding="utf-8"
        )
        meta = adapter.extract_meta_description("/petreceri/test")
        assert meta is not None
        assert "Animatori" in meta

    def test_reports_dir_correct(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert "superparty" in str(adapter.reports_dir).lower()

    def test_min_reapply_days_default(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        assert adapter.min_reapply_days == 7


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ANIMATOPIA ADAPTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestAnimatopiaAdapter:

    def test_pillar_root(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert adapter.is_pillar_page("/")

    def test_pillar_articole_index(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert adapter.is_pillar_page("/articole")
        assert adapter.is_pillar_page("/blog")

    def test_pillar_despre_contact(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert adapter.is_pillar_page("/despre")
        assert adapter.is_pillar_page("/contact")

    def test_money_servicii(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert adapter.is_money_page("/servicii")
        assert adapter.is_money_page("/servicii/animatori-premium")
        assert adapter.is_money_page("/pachete")

    def test_tier_c_article_slug_eligible(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        # Fara fisier, intent=unknown -> eligibil
        result = adapter.is_tier_c_eligible("/articole/cum-organizezi-petrecere")
        assert result is True

    def test_tier_c_excludes_pillar(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert not adapter.is_tier_c_eligible("/")
        assert not adapter.is_tier_c_eligible("/articole")

    def test_tier_c_excludes_money(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert not adapter.is_tier_c_eligible("/servicii/ceva")

    def test_tier_c_excludes_paginare(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert not adapter.is_tier_c_eligible("/articole/page/2")

    def test_money_like_article_excluded(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        # Scrie un articol cu multe semnale comerciale
        article = tmp_path / "src" / "content" / "articole" / "oferta-animatori.md"
        text = f"---\ndescription: Oferta animatori la cel mai bun pret\n---\n"
        # Adaugă COMMERCIAL_THRESHOLD semnal comerciale
        text += " ".join(["preț tarif ofertă comanda rezerva discount"] * 3)
        article.write_text(text, encoding="utf-8")
        assert adapter.is_money_like_article("/articole/oferta-animatori")
        assert not adapter.is_tier_c_eligible("/articole/oferta-animatori")

    def test_editorial_article_eligible(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        article = tmp_path / "src" / "content" / "articole" / "jocuri-copii.md"
        text = "---\ndescription: Ghid cu jocuri distractive pentru copii acasa\n---\n"
        text += "Cum sa organizezi jocuri creative si activitati pentru parinti si copii mici"
        article.write_text(text, encoding="utf-8")
        assert adapter.is_editorial_article("/articole/jocuri-copii")
        assert adapter.is_tier_c_eligible("/articole/jocuri-copii")

    def test_extract_meta_yaml_frontmatter(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        article = tmp_path / "src" / "content" / "articole" / "test-articol.md"
        article.write_text(
            '---\ndescription: Ghid complet pentru organizarea petrecerilor de copii\n---\nContiut articol.',
            encoding="utf-8"
        )
        meta = adapter.extract_meta_description("/articole/test-articol")
        assert meta is not None
        assert "Ghid" in meta

    def test_reports_dir_correct(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert "animatopia" in str(adapter.reports_dir).lower()

    def test_get_page_type_pillar(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert adapter.get_page_type("/") == "pillar"
        assert adapter.get_page_type("/despre") == "pillar"

    def test_get_page_type_money(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        assert adapter.get_page_type("/servicii/test") == "money"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CORE RUN READINESS (adapter-aware)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoreRunReadiness:

    def test_readiness_empty_memory_allowed(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        _write_memory(adapter, [])
        report = generate_run_readiness_report(adapter)
        assert report["run2_allowed"] is True
        assert report["site_id"] == "superparty"

    def test_readiness_blocked_cooldown(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        _write_memory(adapter, [_make_experiment(url="/petreceri/test", applied_days_ago=2)])
        report = generate_run_readiness_report(adapter)
        assert report["run2_allowed"] is False
        assert any("cooldown" in r for r in report["blocked_reasons"])

    def test_readiness_blocked_insufficient_data(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        _write_memory(adapter, [_make_experiment(url="/petreceri/test", applied_days_ago=8)])
        report = generate_run_readiness_report(adapter)
        assert report["site_id"] == "superparty"
        assert not report["run2_allowed"]

    def test_readiness_allowed_conditions_met(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        _write_memory(adapter, [
            _make_experiment(url="/petreceri/test", applied_days_ago=15,
                           observation_window_days=14, impressions_after=100,
                           result_label="positive")
        ])
        report = generate_run_readiness_report(adapter)
        assert report["run2_allowed"] is True

    def test_animatopia_readiness_no_memory(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        report = generate_run_readiness_report(adapter)
        assert report["site_id"] == "animatopia"
        assert report["run2_allowed"] is True  # No active experiments

    def test_readiness_site_id_in_report(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        report = generate_run_readiness_report(adapter)
        assert "site_id" in report


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CORE RUN2 PLANNER (adapter-aware)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoreRun2Planner:

    def test_planner_uses_adapter_catalog(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        _write_memory(adapter, [])
        result = generate_run2_candidates(adapter)
        assert result["site_id"] == "superparty"
        assert isinstance(result["top_candidates"], list)

    def test_planner_animatopia_empty_catalog(self, tmp_path):
        adapter = _make_at_adapter(tmp_path)
        _write_memory(adapter, [])
        result = generate_run2_candidates(adapter)
        assert result["site_id"] == "animatopia"

    def test_planner_excludes_active_experiments(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        _write_memory(adapter, [_make_experiment(url="/petreceri/otopeni", applied_days_ago=2)])
        result = generate_run2_candidates(adapter)
        otopeni = next((c for c in result["excluded"] if c["url"] == "/petreceri/otopeni"), None)
        if otopeni:
            assert "active_experiment_in_progress" in otopeni["blocked_reasons"]

    def test_planner_max_candidates_respected(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        _write_memory(adapter, [])
        result = generate_run2_candidates(adapter, max_candidates=2)
        assert len(result["top_candidates"]) <= 2

    def test_planner_guardrails_listed(self, tmp_path):
        adapter = _make_sp_adapter(tmp_path)
        _write_memory(adapter, [])
        result = generate_run2_candidates(adapter)
        assert "pillar_page_blocked" in result["guardrails_applied"]
        assert "money_page_blocked" in result["guardrails_applied"]
