"""
tests/test_seo_level6_ops_tools.py

Suite de teste pentru L6 Ops Tools (PR #94):
  - seo_level6_gsc_ingestion: CSV/JSON parsing, URL normalization, ingestie outcome memory
  - seo_level6_run_readiness: readiness report blocat/permis
  - seo_level6_run2_planner: candidate planner cu gating complet
"""
import json
import uuid
import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from agent.tasks.seo_level6_gsc_ingestion import (
    normalize_url,
    parse_gsc_csv,
    parse_gsc_json,
    parse_gsc_export,
    ingest_gsc_into_outcome_memory,
)
from agent.tasks.seo_level6_run_readiness import (
    generate_run_readiness_report,
    MIN_IMPRESSIONS_FOR_SCORING,
    MIN_REAPPLY_DAYS,
)
from agent.tasks.seo_level6_run2_planner import (
    generate_run2_candidates,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_memory(tmp_path, experiments: list) -> Path:
    p = tmp_path / "outcome_memory.json"
    p.write_text(json.dumps(experiments, ensure_ascii=False), encoding="utf-8")
    return p


def _make_pillar_registry(tmp_path, pillar_pages: list) -> Path:
    p = tmp_path / "pillar_registry.json"
    p.write_text(json.dumps({"pillar_pages": pillar_pages}), encoding="utf-8")
    return p


def _make_experiment(
    url="/test/pagina",
    strategy="local_intent",
    result_label="pending",
    rollback=False,
    applied_days_ago=0,
    observation_window_days=14,
    impressions_after=None,
    ctr_after=None,
):
    now = datetime.now(timezone.utc)
    applied_at = now - timedelta(days=applied_days_ago)
    deadline = applied_at + timedelta(days=observation_window_days)
    return {
        "experiment_id": str(uuid.uuid4()),
        "url": url,
        "applied_at": applied_at.isoformat(),
        "strategy": strategy,
        "before_meta": "Text vechi.",
        "after_meta": "Text nou.",
        "observation_window_days": observation_window_days,
        "observation_deadline": deadline.isoformat(),
        "gsc_before": {"impressions": None, "ctr": None, "position": None},
        "gsc_after": {"impressions": impressions_after, "ctr": ctr_after, "position": None},
        "result_label": result_label,
        "rollback_happened": rollback,
        "closed_at": None if result_label == "pending" else now.isoformat(),
        "score_explanation": None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 1. URL NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestUrlNormalization:

    def test_full_url_stripped(self):
        assert normalize_url("https://www.superparty.ro/petreceri/voluntari") == "/petreceri/voluntari"

    def test_non_www_stripped(self):
        assert normalize_url("https://superparty.ro/petreceri/mogosoaia") == "/petreceri/mogosoaia"

    def test_trailing_slash_removed(self):
        assert normalize_url("https://www.superparty.ro/petreceri/voluntari/") == "/petreceri/voluntari"

    def test_already_path_unchanged(self):
        assert normalize_url("/petreceri/voluntari") == "/petreceri/voluntari"

    def test_root_url(self):
        assert normalize_url("https://www.superparty.ro/") == "/"

    def test_path_without_leading_slash(self):
        result = normalize_url("petreceri/voluntari")
        assert result.startswith("/")

    def test_http_variant(self):
        assert normalize_url("http://superparty.ro/balonase") == "/balonase"

    def test_whitespace_stripped(self):
        assert normalize_url("  https://www.superparty.ro/test  ") == "/test"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. GSC CSV PARSING
# ═══════════════════════════════════════════════════════════════════════════════

class TestGscCsvParsing:

    def test_standard_csv_parsed(self):
        csv_content = (
            "page,clicks,impressions,ctr,position\n"
            "https://www.superparty.ro/petreceri/voluntari,5,120,4.17%,8.3\n"
            "https://www.superparty.ro/petreceri/mogosoaia,2,45,4.44%,12.1\n"
        )
        rows = parse_gsc_csv(csv_content)
        assert len(rows) == 2
        assert rows[0]["url"] == "/petreceri/voluntari"
        assert rows[0]["impressions"] == 120
        assert rows[0]["clicks"] == 5
        assert rows[1]["url"] == "/petreceri/mogosoaia"
        assert rows[1]["impressions"] == 45

    def test_ctr_percent_converted(self):
        csv_content = "page,impressions,ctr\nhttps://www.superparty.ro/test,100,5.2%\n"
        rows = parse_gsc_csv(csv_content)
        assert rows[0]["ctr"] == pytest.approx(0.052, abs=0.001)

    def test_ctr_decimal_not_doubled(self):
        csv_content = "page,impressions,ctr\nhttps://www.superparty.ro/test,100,0.052\n"
        rows = parse_gsc_csv(csv_content)
        assert rows[0]["ctr"] == pytest.approx(0.052, abs=0.001)

    def test_empty_csv_returns_empty(self):
        rows = parse_gsc_csv("page,impressions,ctr\n")
        assert rows == []

    def test_missing_values_become_none(self):
        csv_content = "page,impressions,ctr\nhttps://www.superparty.ro/test,,\n"
        rows = parse_gsc_csv(csv_content)
        assert rows[0]["impressions"] is None
        assert rows[0]["ctr"] is None

    def test_url_normalized_in_csv(self):
        csv_content = "page,impressions\nhttps://www.superparty.ro/petreceri/voluntari/,100\n"
        rows = parse_gsc_csv(csv_content)
        assert rows[0]["url"] == "/petreceri/voluntari"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. GSC JSON PARSING
# ═══════════════════════════════════════════════════════════════════════════════

class TestGscJsonParsing:

    def test_standard_gsc_api_format(self):
        data = {
            "rows": [
                {"keys": ["https://www.superparty.ro/petreceri/voluntari"], "impressions": 120, "clicks": 5, "ctr": 0.0417, "position": 8.3},
                {"keys": ["https://www.superparty.ro/petreceri/pantelimon"], "impressions": 35, "clicks": 1, "ctr": 0.0286, "position": 14.2},
            ]
        }
        rows = parse_gsc_json(json.dumps(data))
        assert len(rows) == 2
        assert rows[0]["url"] == "/petreceri/voluntari"
        assert rows[0]["impressions"] == 120

    def test_list_format(self):
        data = [
            {"keys": ["https://www.superparty.ro/test"], "impressions": 50},
        ]
        rows = parse_gsc_json(json.dumps(data))
        assert len(rows) == 1
        assert rows[0]["impressions"] == 50

    def test_empty_rows(self):
        rows = parse_gsc_json(json.dumps({"rows": []}))
        assert rows == []


# ═══════════════════════════════════════════════════════════════════════════════
# 4. AUTO-DETECT FORMAT
# ═══════════════════════════════════════════════════════════════════════════════

class TestAutoDetect:

    def test_json_detected_automatically(self):
        content = '{"rows": [{"keys": ["https://www.superparty.ro/test"], "impressions": 50}]}'
        rows = parse_gsc_export(content, format="auto")
        assert rows[0]["impressions"] == 50

    def test_csv_detected_automatically(self):
        content = "page,impressions\nhttps://www.superparty.ro/test,50\n"
        rows = parse_gsc_export(content, format="auto")
        assert rows[0]["impressions"] == 50


# ═══════════════════════════════════════════════════════════════════════════════
# 5. INGESTION ÎN OUTCOME MEMORY
# ═══════════════════════════════════════════════════════════════════════════════

class TestOutcomeMemoryIngestion:

    def test_ingestion_updates_gsc_after(self, tmp_path):
        memory = _make_memory(tmp_path, [_make_experiment(url="/petreceri/voluntari")])
        gsc_rows = [{"url": "/petreceri/voluntari", "impressions": 120, "clicks": 5, "ctr": 0.042, "position": 8.3}]
        result = ingest_gsc_into_outcome_memory(gsc_rows, memory, mode="after")
        assert "/petreceri/voluntari" in result["injected"]
        data = json.loads(memory.read_text(encoding="utf-8"))
        assert data[0]["gsc_after"]["impressions"] == 120

    def test_url_not_in_export_marked_not_found(self, tmp_path):
        memory = _make_memory(tmp_path, [_make_experiment(url="/petreceri/voluntari")])
        gsc_rows = []  # export gol
        result = ingest_gsc_into_outcome_memory(gsc_rows, memory, mode="after")
        assert "/petreceri/voluntari" in result["not_found"]

    def test_missing_impressions_marked_insufficient(self, tmp_path):
        memory = _make_memory(tmp_path, [_make_experiment(url="/petreceri/test")])
        gsc_rows = [{"url": "/petreceri/test", "impressions": None, "clicks": None, "ctr": None, "position": None}]
        result = ingest_gsc_into_outcome_memory(gsc_rows, memory, mode="after")
        assert "/petreceri/test" in result["insufficient_data"]

    def test_missing_memory_file_returns_error(self, tmp_path):
        fake_path = tmp_path / "nonexistent.json"
        result = ingest_gsc_into_outcome_memory([], fake_path)
        assert result["status"] == "error"
        assert "outcome_memory_not_found" in result["reason"]

    def test_mode_before_updates_gsc_before(self, tmp_path):
        memory = _make_memory(tmp_path, [_make_experiment(url="/petreceri/test")])
        gsc_rows = [{"url": "/petreceri/test", "impressions": 80, "clicks": 3, "ctr": 0.037, "position": 10.1}]
        ingest_gsc_into_outcome_memory(gsc_rows, memory, mode="before")
        data = json.loads(memory.read_text(encoding="utf-8"))
        assert data[0]["gsc_before"]["impressions"] == 80


# ═══════════════════════════════════════════════════════════════════════════════
# 6. RUN READINESS REPORT — BLOCAT
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunReadinessBlocked:

    def test_blocked_when_all_insufficient_data(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/a", applied_days_ago=8, impressions_after=None),
        ])
        report = generate_run_readiness_report(memory)
        assert report["run2_allowed"] is False
        reasons = " ".join(report["blocked_reasons"])
        assert "insufficient_data" in reasons

    def test_blocked_when_cooldown_active(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/a", applied_days_ago=3),  # 3 < 7 MIN_REAPPLY_DAYS
        ])
        report = generate_run_readiness_report(memory)
        assert report["run2_allowed"] is False
        assert "/a" in report["cooldown_active_urls"]

    def test_blocked_when_observation_window_not_closed(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/a", applied_days_ago=1, observation_window_days=14),
        ])
        report = generate_run_readiness_report(memory)
        assert report["run2_allowed"] is False

    def test_blocked_when_rollback_active(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/a", applied_days_ago=10, rollback=True, impressions_after=100),
        ])
        report = generate_run_readiness_report(memory)
        assert report["run2_allowed"] is False
        assert "active_rollback_conflict" in report["blocked_reasons"]

    def test_cooldown_active_urls_correct(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/a", applied_days_ago=2),
            _make_experiment(url="/b", applied_days_ago=8),
        ])
        report = generate_run_readiness_report(memory)
        assert "/a" in report["cooldown_active_urls"]
        assert "/b" in report["cooldown_lifted_urls"]


# ═══════════════════════════════════════════════════════════════════════════════
# 7. RUN READINESS REPORT — PERMIS
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunReadinessAllowed:

    def test_allowed_when_conditions_met(self, tmp_path):
        """Run 2 permis: cooldown lifted, impressions ok, past deadline, no rollback."""
        memory = _make_memory(tmp_path, [
            _make_experiment(
                url="/a",
                applied_days_ago=15,          # > MIN_REAPPLY_DAYS=7 ✓
                observation_window_days=14,    # past deadline ✓
                impressions_after=100,         # > MIN_IMPRESSIONS=80 ✓
                result_label="positive",       # non-pending ✓
            ),
        ])
        report = generate_run_readiness_report(memory)
        assert report["run2_allowed"] is True
        assert report["blocked_reasons"] == []

    def test_sufficient_impressions_detected(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/a", applied_days_ago=10, impressions_after=MIN_IMPRESSIONS_FOR_SCORING),
        ])
        report = generate_run_readiness_report(memory)
        assert "/a" in report["urls_with_sufficient_impressions"]

    def test_insufficient_impressions_below_threshold(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/a", applied_days_ago=10, impressions_after=MIN_IMPRESSIONS_FOR_SCORING - 1),
        ])
        report = generate_run_readiness_report(memory)
        assert "/a" in report["urls_with_insufficient_data"]

    def test_empty_memory_returns_no_blockers_related_to_experiments(self, tmp_path):
        memory = _make_memory(tmp_path, [])
        report = generate_run_readiness_report(memory)
        # Fara experimente, nu exista blockers din cooldown/impressions
        assert report["cooldown_active_urls"] == []
        assert report["run2_allowed"] is True

    def test_recommended_next_check_at_populated(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/a", applied_days_ago=2),
        ])
        report = generate_run_readiness_report(memory)
        assert report["recommended_next_check_at"] is not None
        assert len(report["recommended_next_check_at"]) == 10  # YYYY-MM-DD


# ═══════════════════════════════════════════════════════════════════════════════
# 8. RUN 2 CANDIDATE PLANNER
# ═══════════════════════════════════════════════════════════════════════════════

class TestRun2Planner:

    def test_pillar_page_excluded(self, tmp_path):
        memory = _make_memory(tmp_path, [])
        pillar = _make_pillar_registry(tmp_path, ["/petreceri/otopeni"])
        result = generate_run2_candidates(memory, pillar)
        excluded_urls = [c["url"] for c in result["excluded"]]
        assert "/petreceri/otopeni" in excluded_urls
        # Verifica ca motivul e pillar
        otopeni_entry = next(c for c in result["excluded"] if c["url"] == "/petreceri/otopeni")
        assert "pillar_page_blocked" in otopeni_entry["blocked_reasons"]

    def test_active_experiment_excluded(self, tmp_path):
        # Pune /petreceri/popesti-leordeni ca experiment activ
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/petreceri/popesti-leordeni", applied_days_ago=1)
        ])
        pillar = _make_pillar_registry(tmp_path, [])
        result = generate_run2_candidates(memory, pillar)
        excluded_urls = [c["url"] for c in result["excluded"]]
        assert "/petreceri/popesti-leordeni" in excluded_urls
        entry = next(c for c in result["excluded"] if c["url"] == "/petreceri/popesti-leordeni")
        assert "active_experiment_in_progress" in entry["blocked_reasons"]

    def test_cooldown_active_excluded(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/petreceri/otopeni", applied_days_ago=2)  # 2 < 7 MIN_REAPPLY
        ])
        pillar = _make_pillar_registry(tmp_path, [])
        result = generate_run2_candidates(memory, pillar)
        excluded_urls = [c["url"] for c in result["excluded"]]
        assert "/petreceri/otopeni" in excluded_urls
        entry = next(c for c in result["excluded"] if c["url"] == "/petreceri/otopeni")
        assert "cooldown_active" in entry["blocked_reasons"]

    def test_rollback_url_excluded(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/petreceri/chitila", rollback=True, result_label="strong_negative")
        ])
        pillar = _make_pillar_registry(tmp_path, [])
        result = generate_run2_candidates(memory, pillar)
        excluded_urls = [c["url"] for c in result["excluded"]]
        assert "/petreceri/chitila" in excluded_urls
        entry = next(c for c in result["excluded"] if c["url"] == "/petreceri/chitila")
        assert "rollback_recent" in entry["blocked_reasons"]

    def test_earliest_possible_run_date_in_future_for_blocked(self, tmp_path):
        memory = _make_memory(tmp_path, [
            _make_experiment(url="/petreceri/voluntari", applied_days_ago=1, observation_window_days=14)
        ])
        pillar = _make_pillar_registry(tmp_path, [])
        result = generate_run2_candidates(memory, pillar)
        voluntari_entry = next(
            (c for c in result["excluded"] if c["url"] == "/petreceri/voluntari"),
            None
        )
        if voluntari_entry:
            earliest = voluntari_entry["earliest_possible_run_date"]
            from datetime import date
            assert earliest > date.today().isoformat()

    def test_max_candidates_respected(self, tmp_path):
        memory = _make_memory(tmp_path, [])
        pillar = _make_pillar_registry(tmp_path, [])
        result = generate_run2_candidates(memory, pillar, max_candidates=2)
        assert len(result["top_candidates"]) <= 2

    def test_all_candidates_have_required_fields(self, tmp_path):
        memory = _make_memory(tmp_path, [])
        pillar = _make_pillar_registry(tmp_path, [])
        result = generate_run2_candidates(memory, pillar)
        required = ["url", "tier", "suggested_strategy", "selection_reason", "data_quality",
                    "eligible_now", "blocked_reasons", "earliest_possible_run_date"]
        for c in result["all_eligible"] + result["excluded"]:
            for field in required:
                assert field in c, f"Camp lipsa '{field}' in candidat: {c.get('url')}"

    def test_guardrails_listed_in_output(self, tmp_path):
        memory = _make_memory(tmp_path, [])
        pillar = _make_pillar_registry(tmp_path, [])
        result = generate_run2_candidates(memory, pillar)
        assert "guardrails_applied" in result
        assert "pillar_page_blocked" in result["guardrails_applied"]
        assert "money_page_blocked" in result["guardrails_applied"]

    def test_report_has_run2_ready_count(self, tmp_path):
        memory = _make_memory(tmp_path, [])
        pillar = _make_pillar_registry(tmp_path, [])
        result = generate_run2_candidates(memory, pillar)
        assert "run2_ready_count" in result
        assert isinstance(result["run2_ready_count"], int)
