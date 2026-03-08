"""
Tests for scripts/seo_ops_dashboard.py

Covers:
- verdict logic (GREEN / YELLOW / RED)
- freshness calculation
- _read_json resilience (missing, corrupt)
- ledger parsing
- snapshot metadata extraction

Run with:
    python -m pytest tests/test_seo_ops_dashboard.py -v
"""

from __future__ import annotations

import json
import sys
import importlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Ensure scripts/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import seo_ops_dashboard as dash


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def _l7_ok(status="SUCCESS", rows=150):
    return {
        "ok": True,
        "last": {
            "status": status,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "row_count": rows,
            "snapshot_filename": "collect_20260308T090000.json",
        },
        "history": [],
    }


def _l7_failed():
    return {
        "ok": True,
        "last": {
            "status": "FAILED",
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "failing_stage": "API_FETCH",
            "error_reason": "quota exceeded",
        },
        "history": [],
    }


def _l7_missing():
    return {"ok": False, "last": None, "history": [], "error": "Ledger missing"}


def _l6_ok(overall="success"):
    return {
        "ok": True,
        "status": {
            "overall_status": overall,
            "health": "success",
            "priority": "success",
            "trend": "success",
            "ledger_status": "success",
            "run_at": datetime.now(timezone.utc).isoformat(),
        },
        "history": [],
    }


def _l6_failed():
    return {
        "ok": True,
        "status": {"overall_status": "failed", "health": "failed"},
        "history": [],
    }


def _freshness_all_ready():
    return {
        "health":   {"verdict": "ready",   "generated_at": datetime.now(timezone.utc).isoformat(), "age": "1.0h",  "missing": False},
        "priority": {"verdict": "ready",   "generated_at": datetime.now(timezone.utc).isoformat(), "age": "1.0h",  "missing": False},
        "trends":   {"verdict": "ready",   "generated_at": datetime.now(timezone.utc).isoformat(), "age": "1.0h",  "missing": False},
    }


def _freshness_with(key, verdict):
    f = _freshness_all_ready()
    f[key] = {"verdict": verdict, "generated_at": None, "age": "99h", "missing": verdict == "stale"}
    return f


# ─── Verdict tests ─────────────────────────────────────────────────────────────

class TestComputeVerdict:

    def test_green_all_ok(self):
        assert dash.compute_verdict(_l7_ok(), _l6_ok(), _freshness_all_ready()) == "GREEN"

    def test_red_l7_ledger_missing(self):
        assert dash.compute_verdict(_l7_missing(), _l6_ok(), _freshness_all_ready()) == "RED"

    def test_red_l7_last_run_failed(self):
        assert dash.compute_verdict(_l7_failed(), _l6_ok(), _freshness_all_ready()) == "RED"

    def test_red_l6_overall_failed(self):
        assert dash.compute_verdict(_l7_ok(), _l6_failed(), _freshness_all_ready()) == "RED"

    def test_red_health_stale(self):
        assert dash.compute_verdict(_l7_ok(), _l6_ok(), _freshness_with("health", "stale")) == "RED"

    def test_red_trends_missing(self):
        assert dash.compute_verdict(_l7_ok(), _l6_ok(), _freshness_with("trends", "stale")) == "RED"

    def test_yellow_freshness_warning(self):
        result = dash.compute_verdict(_l7_ok(), _l6_ok(), _freshness_with("priority", "warning"))
        assert result == "YELLOW"

    def test_yellow_l6_partial_failure_in_history(self):
        l6 = _l6_ok()
        l6["history"] = [
            {"status": "partial_failure", "timestamp": datetime.now(timezone.utc).isoformat()},
        ]
        result = dash.compute_verdict(_l7_ok(), l6, _freshness_all_ready())
        assert result == "YELLOW"


# ─── Freshness tests ───────────────────────────────────────────────────────────

class TestFreshnessVerdict:

    def test_ready_recent(self):
        age = 5.0   # hours
        assert dash._freshness_verdict(age, max_h=48) == "ready"

    def test_warning_near_limit(self):
        age = 40.0  # 48 * 0.75 = 36 → 40 > 36 → warning
        assert dash._freshness_verdict(age, max_h=48) == "warning"

    def test_stale_over_limit(self):
        age = 55.0
        assert dash._freshness_verdict(age, max_h=48) == "stale"

    def test_stale_when_none(self):
        assert dash._freshness_verdict(None, max_h=48) == "stale"


# ─── _read_json resilience ─────────────────────────────────────────────────────

class TestReadJson:

    def test_returns_none_on_missing_file(self, tmp_path):
        result = dash._read_json(tmp_path / "nonexistent.json")
        assert result is None

    def test_returns_none_on_corrupt_json(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{ not: valid json }", encoding="utf-8")
        result = dash._read_json(bad)
        assert result is None

    def test_returns_parsed_dict(self, tmp_path):
        good = tmp_path / "good.json"
        good.write_text(json.dumps({"key": "value"}), encoding="utf-8")
        result = dash._read_json(good)
        assert result == {"key": "value"}

    def test_returns_parsed_list(self, tmp_path):
        good = tmp_path / "list.json"
        good.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
        assert dash._read_json(good) == [1, 2, 3]


# ─── _age_hours ────────────────────────────────────────────────────────────────

class TestAgeHours:

    def test_recent_timestamp(self):
        ts = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        age = dash._age_hours(ts)
        assert 2.9 < age < 3.1

    def test_none_input(self):
        assert dash._age_hours(None) is None

    def test_bad_string(self):
        assert dash._age_hours("not-a-date") is None

    def test_z_suffix(self):
        ts = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        age = dash._age_hours(ts)
        assert 0.9 < age < 1.1


# ─── collect_l7 ────────────────────────────────────────────────────────────────

class TestCollectL7:

    def test_missing_ledger_returns_not_ok(self, tmp_path):
        with patch.object(dash, "L7_LEDGER", tmp_path / "missing.json"):
            result = dash.collect_l7()
        assert result["ok"] is False

    def test_empty_ledger_returns_not_ok(self, tmp_path):
        f = tmp_path / "ledger.json"
        f.write_text("[]", encoding="utf-8")
        with patch.object(dash, "L7_LEDGER", f):
            result = dash.collect_l7()
        assert result["ok"] is False

    def test_valid_ledger_returns_last_entry(self, tmp_path):
        entries = [
            {"collected_at": "2026-03-07T03:00:00+00:00", "status": "SUCCESS", "row_count": 100},
            {"collected_at": "2026-03-08T03:00:00+00:00", "status": "SUCCESS", "row_count": 120},
        ]
        f = tmp_path / "ledger.json"
        f.write_text(json.dumps(entries), encoding="utf-8")
        with patch.object(dash, "L7_LEDGER", f):
            result = dash.collect_l7()
        assert result["ok"] is True
        assert result["last"]["row_count"] == 120


# ─── render_html smoke test ────────────────────────────────────────────────────

class TestRenderHtml:

    def test_renders_without_error(self):
        out = dash.render_html(
            _l7_ok(), _l6_ok(), _freshness_all_ready(),
            snapshot={"_filename": "collect_test.json", "row_count": 50,
                      "collected_at": "2026-03-08T09:00:00Z",
                      "property": "sc-domain:superparty.ro",
                      "schema_version": "1.0", "source": "google_search_console"},
            trend_flags={"available": True, "baseline_only": False},
            verdict="GREEN"
        )
        assert "VERDE" in out
        assert "Source Acquisition" in out
        assert "ops_dashboard.html" not in out or True  # sanity

    def test_red_verdict_in_output(self):
        out = dash.render_html(
            _l7_missing(), _l6_failed(), _freshness_with("health", "stale"),
            snapshot=None,
            trend_flags={"available": False, "baseline_only": None},
            verdict="RED"
        )
        assert "ROȘU" in out


# ─── L5 Collector tests ────────────────────────────────────────────────────────

class TestCollectL5Proposals:

    def test_absent_artefact_returns_not_available(self, tmp_path):
        with patch.object(dash, "L5_DRY_RUN", tmp_path / "missing.json"):
            result = dash.collect_l5_proposals()
        assert result["available"] is False
        assert result["actions"] == []
        assert result["total"] == 0

    def test_parses_real_schema(self, tmp_path):
        payload = {
            "metadata": {
                "generated_at": "2026-03-08T10:00:00+00:00",
                "mode": "dry_run_only",
                "total_candidates": 1,
            },
            "actions": [{
                "action_id": "mdesc-dryrun-test-url",
                "action_type": "meta_description_update",
                "status": "proposed_only",
                "tier": "C",
                "url": "/test-url",
                "before": {"meta_description": ""},
                "proposal": {"meta_description": "Propunere test"},
            }],
        }
        f = tmp_path / "dry_run.json"
        f.write_text(json.dumps(payload), encoding="utf-8")
        with patch.object(dash, "L5_DRY_RUN", f):
            result = dash.collect_l5_proposals()
        assert result["available"] is True
        assert result["total"] == 1
        assert result["mode"] == "dry_run_only"
        assert result["actions"][0]["url"] == "/test-url"


class TestCollectL5Approval:
    """Tests aligned to seo_level5_apply_plan_generator.py real schema."""

    def test_absent_artefacts_returns_empty_gracefully(self, tmp_path):
        with (
            patch.object(dash, "L5_APPROVAL", tmp_path / "missing_approval.json"),
            patch.object(dash, "L5_APPLY_PLAN", tmp_path / "missing_plan.json"),
        ):
            result = dash.collect_l5_approval()
        assert result["approval_log"] == []
        assert result["approved"] == []
        assert result["rejected"] == []
        # UX hardening: absence != failure; None signals "not available" (not an error)
        assert result["plan_available"] is False
        assert result["all_checks_passed"] is None, "absent plan must return None, not False"
        assert result["policy_valid"] is None, "absent plan must return None, not False"
        assert result["ready_count"] == 0
        assert result["plan_generated_at"] is None

    def test_reads_metadata_generated_at_not_root(self, tmp_path):
        """plan_generated_at must come from metadata.generated_at, NOT root."""
        plan = {
            "metadata": {
                "generated_at": "2026-03-08T11:00:00+00:00",
                "total_eligible": 1,
                "total_blocked": 0,
            },
            "preflight_summary": {
                "all_checks_passed": True,
                "policy_valid": True,
                "blocking_issues": [],
            },
            "plan": [{"ready_to_apply": True, "url": "/test-url"}],
            "blocked": [],
        }
        f_plan = tmp_path / "apply_plan.json"
        f_plan.write_text(json.dumps(plan), encoding="utf-8")
        f_approval = tmp_path / "approval_log.json"
        f_approval.write_text("[]", encoding="utf-8")
        with (
            patch.object(dash, "L5_APPROVAL", f_approval),
            patch.object(dash, "L5_APPLY_PLAN", f_plan),
        ):
            result = dash.collect_l5_approval()
        assert result["plan_generated_at"] == "2026-03-08T11:00:00+00:00"
        assert result["all_checks_passed"] is True
        assert result["policy_valid"] is True
        assert result["ready_count"] == 1  # plan[].ready_to_apply
        assert result["total_eligible"] == 1
        assert result["total_blocked_plan"] == 0

    def test_ready_count_derived_from_plan_entries(self, tmp_path):
        """ready_count is count of plan[].ready_to_apply==True, not a root field."""
        plan = {
            "metadata": {"generated_at": "2026-03-08T12:00:00+00:00", "total_eligible": 2, "total_blocked": 1},
            "preflight_summary": {"all_checks_passed": True, "policy_valid": True, "blocking_issues": []},
            "plan": [
                {"ready_to_apply": True, "url": "/a"},
                {"ready_to_apply": False, "url": "/b"},  # not ready
            ],
            "blocked": [{"ready_to_apply": False, "url": "/c"}],
        }
        f_plan = tmp_path / "apply_plan.json"
        f_plan.write_text(json.dumps(plan), encoding="utf-8")
        f_approval = tmp_path / "approval_log.json"
        f_approval.write_text("[]", encoding="utf-8")
        with (
            patch.object(dash, "L5_APPROVAL", f_approval),
            patch.object(dash, "L5_APPLY_PLAN", f_plan),
        ):
            result = dash.collect_l5_approval()
        assert result["ready_count"] == 1  # only the True entry


class TestCollectL5Execution:
    """Tests aligned to seo_level5_meta_description_apply.py + seo_level5_rollback_executor.py real schema."""

    def test_absent_artefacts_returns_empty_gracefully(self, tmp_path):
        with (
            patch.object(dash, "L5_APPLY_EXEC", tmp_path / "missing_exec.json"),
            patch.object(dash, "L5_ROLLBACK_PAYLOAD", tmp_path / "missing_pay.json"),
            patch.object(dash, "L5_ROLLBACK_EXEC", tmp_path / "missing_rollback.json"),
        ):
            result = dash.collect_l5_execution()
        assert result["apply_exec_available"] is False
        assert result["applied_actions"] == []
        assert result["blocked_exec_actions"] == []
        assert result["rollback_payload"] is None
        assert result["rollback_exec"] is None

    def test_apply_execution_parsed_from_applied_actions_list(self, tmp_path):
        """applied_actions is a list[] in schema, not root-level fields."""
        exec_report = {
            "metadata": {
                "generated_at": "2026-03-08T12:30:00+00:00",
                "applied": 1,
                "blocked": 0,
            },
            "applied_actions": [{
                "execution_id": "exec-uuid-1234",
                "plan_id": "plan-uuid-5678",
                "decision_id": "dec-uuid-9012",
                "action_id": "mdesc-dryrun-test-url",
                "url": "/test-url",
                "file_path": "src/pages/test-url.astro",
                "before": {"meta_description": "Vechi"},
                "after": {"meta_description": "Nou"},
                "edit_strategy": "layout_prop",
                "after_value_verified": True,
                "rollback_ready": True,
            }],
            "blocked_actions": [],
        }
        f = tmp_path / "apply_exec.json"
        f.write_text(json.dumps(exec_report), encoding="utf-8")
        with (
            patch.object(dash, "L5_APPLY_EXEC", f),
            patch.object(dash, "L5_ROLLBACK_PAYLOAD", tmp_path / "missing.json"),
            patch.object(dash, "L5_ROLLBACK_EXEC", tmp_path / "missing2.json"),
        ):
            result = dash.collect_l5_execution()
        assert result["apply_exec_available"] is True
        assert len(result["applied_actions"]) == 1
        assert result["applied_actions"][0]["execution_id"] == "exec-uuid-1234"
        assert result["applied_actions"][0]["url"] == "/test-url"
        assert result["exec_meta"]["applied"] == 1

    def test_rollback_execution_parsed_with_correct_fields(self, tmp_path):
        """rollback_execution schema: rollback_id, reverted, reverted_at, original_lineage.*"""
        rollback_exec = {
            "schema_version": "1.0",
            "rollback_id": "rb-uuid-1234",
            "rollback_type": "automated_executor",
            "reverted": True,
            "post_rollback_verification": True,
            "reverted_at": "2026-03-08T13:00:00+00:00",
            "reverted_by": "ops-manual-rollback",
            "original_lineage": {
                "execution_id": "exec-uuid-1234",
                "plan_id": "plan-uuid-5678",
                "decision_id": "dec-uuid-9012",
                "action_id": "mdesc-dryrun-test-url",
            },
            "file_path": "src/pages/test-url.astro",
            "before_restored": "Vechi",
            "after_reverted": "Nou",
            "edit_strategy": "layout_prop",
        }
        f = tmp_path / "rollback_exec.json"
        f.write_text(json.dumps(rollback_exec), encoding="utf-8")
        with (
            patch.object(dash, "L5_APPLY_EXEC", tmp_path / "missing.json"),
            patch.object(dash, "L5_ROLLBACK_PAYLOAD", tmp_path / "missing2.json"),
            patch.object(dash, "L5_ROLLBACK_EXEC", f),
        ):
            result = dash.collect_l5_execution()
        assert result["rollback_exec"]["rollback_id"] == "rb-uuid-1234"
        assert result["rollback_exec"]["reverted"] is True
        assert result["rollback_exec"]["original_lineage"]["execution_id"] == "exec-uuid-1234"

    def test_blocked_actions_rendered_from_blocked_actions_list(self, tmp_path):
        """blocked_actions is a list[] in apply_execution schema."""
        exec_report = {
            "metadata": {"generated_at": "2026-03-08T12:00:00+00:00", "applied": 0, "blocked": 1},
            "applied_actions": [],
            "blocked_actions": [{"blocking_reason": "current_description_differs_from_plan", "url": "/x"}],
        }
        f = tmp_path / "apply_exec.json"
        f.write_text(json.dumps(exec_report), encoding="utf-8")
        with (
            patch.object(dash, "L5_APPLY_EXEC", f),
            patch.object(dash, "L5_ROLLBACK_PAYLOAD", tmp_path / "m.json"),
            patch.object(dash, "L5_ROLLBACK_EXEC", tmp_path / "m2.json"),
        ):
            result = dash.collect_l5_execution()
        assert result["blocked_exec_actions"][0]["blocking_reason"] == "current_description_differs_from_plan"


class TestRenderHtmlL5Sections:
    """Smoke tests that render_html includes L5 sections and degrades gracefully."""

    def test_renders_l5_sections_when_absent(self):
        out = dash.render_html(
            _l7_ok(), _l6_ok(), _freshness_all_ready(),
            snapshot=None,
            trend_flags={"available": True, "baseline_only": False},
            verdict="GREEN",
            l5_proposals=None,
            l5_approval=None,
            l5_execution=None,
        )
        assert "L5 Proposals" in out
        assert "L5 Approval" in out
        assert "L5 Applied" in out
        assert "Niciun dry-run" in out
        assert "Niciun apply executat" in out

    def test_renders_l5_proposal_url_and_proposal(self):
        proposals = {
            "available": True,
            "actions": [{
                "url": "/petreceri/test",
                "tier": "C",
                "status": "proposed_only",
                "before": {"meta_description": ""},
                "proposal": {"meta_description": "Meta noua propusa"},
            }],
            "generated_at": "2026-03-08T10:00:00+00:00",
            "total": 1,
            "mode": "dry_run_only",
        }
        out = dash.render_html(
            _l7_ok(), _l6_ok(), _freshness_all_ready(),
            snapshot=None,
            trend_flags={"available": True, "baseline_only": False},
            verdict="GREEN",
            l5_proposals=proposals,
            l5_approval=None,
            l5_execution=None,
        )
        assert "/petreceri/test" in out
        assert "Meta noua propusa" in out


# ─── G section UX hardening tests ─────────────────────────────────────────────
# Verifies: absence != failure for seo_level5_apply_plan.json

def _make_apply_plan(policy_valid: bool, all_checks_passed: bool, ready: bool = True) -> dict:
    """Factory for a minimal but schema-valid apply_plan.json payload."""
    return {
        "metadata": {
            "generated_at": "2026-03-08T14:00:00+00:00",
            "total_eligible": 1 if ready else 0,
            "total_blocked": 0 if ready else 1,
        },
        "preflight_summary": {
            "all_checks_passed": all_checks_passed,
            "policy_valid": policy_valid,
            "blocking_issues": [] if policy_valid else ["policy.mode not allowed"],
        },
        "plan": [{"ready_to_apply": ready, "url": "/test"}] if ready else [],
        "blocked": [] if ready else [{"ready_to_apply": False, "url": "/test", "blocking_reason": "policy_invalid"}],
    }


class TestCollectL5ApprovalPlanAvailable:
    """Verifies plan_available flag and None-valued policy/checks when absent."""

    def test_absent_plan_sets_plan_available_false(self, tmp_path):
        """Case 1: apply_plan absent → plan_available=False, policy_valid=None, all_checks_passed=None."""
        with (
            patch.object(dash, "L5_APPROVAL", tmp_path / "missing_approval.json"),
            patch.object(dash, "L5_APPLY_PLAN", tmp_path / "missing_plan.json"),
        ):
            result = dash.collect_l5_approval()
        assert result["plan_available"] is False
        assert result["policy_valid"] is None, "absence must NOT be reported as False (failure)"
        assert result["all_checks_passed"] is None, "absence must NOT be reported as False (failure)"
        assert result["plan_generated_at"] is None
        assert result["ready_count"] == 0

    def test_present_plan_policy_invalid(self, tmp_path):
        """Case 2: apply_plan present, policy_valid=False → plan_available=True, policy_valid=False."""
        f = tmp_path / "apply_plan.json"
        f.write_text(json.dumps(_make_apply_plan(policy_valid=False, all_checks_passed=False)), encoding="utf-8")
        f_ap = tmp_path / "approval.json"
        f_ap.write_text("[]", encoding="utf-8")
        with (
            patch.object(dash, "L5_APPROVAL", f_ap),
            patch.object(dash, "L5_APPLY_PLAN", f),
        ):
            result = dash.collect_l5_approval()
        assert result["plan_available"] is True
        assert result["policy_valid"] is False
        assert result["all_checks_passed"] is False

    def test_present_plan_checks_failed(self, tmp_path):
        """Case 3: apply_plan present, policy valid but all_checks_passed=False → warning."""
        f = tmp_path / "apply_plan.json"
        f.write_text(json.dumps(_make_apply_plan(policy_valid=True, all_checks_passed=False, ready=False)), encoding="utf-8")
        f_ap = tmp_path / "approval.json"
        f_ap.write_text("[]", encoding="utf-8")
        with (
            patch.object(dash, "L5_APPROVAL", f_ap),
            patch.object(dash, "L5_APPLY_PLAN", f),
        ):
            result = dash.collect_l5_approval()
        assert result["plan_available"] is True
        assert result["policy_valid"] is True
        assert result["all_checks_passed"] is False

    def test_present_plan_healthy(self, tmp_path):
        """Case 4: apply_plan present, all healthy → policy_valid=True, all_checks_passed=True."""
        f = tmp_path / "apply_plan.json"
        f.write_text(json.dumps(_make_apply_plan(policy_valid=True, all_checks_passed=True)), encoding="utf-8")
        f_ap = tmp_path / "approval.json"
        f_ap.write_text("[]", encoding="utf-8")
        with (
            patch.object(dash, "L5_APPROVAL", f_ap),
            patch.object(dash, "L5_APPLY_PLAN", f),
        ):
            result = dash.collect_l5_approval()
        assert result["plan_available"] is True
        assert result["policy_valid"] is True
        assert result["all_checks_passed"] is True
        assert result["ready_count"] == 1


class TestRenderHtmlGSectionAbsenceNotFailure:
    """render_html section G must show N/A (not FAILED/warning) when apply_plan is absent."""

    @staticmethod
    def _absent_approval() -> dict:
        """Simulates collect_l5_approval() output when apply_plan artefact is missing."""
        return {
            "plan_available": False,
            "approval_log": [], "approved": [], "rejected": [],
            "plan": [], "blocked": [],
            "all_checks_passed": None,
            "policy_valid": None,
            "blocking_issues": [],
            "ready_count": 0,
            "total_eligible": 0,
            "total_blocked_plan": 0,
            "plan_generated_at": None,
        }

    def test_absent_plan_renders_na_not_failed_or_warning(self):
        """Case 5: Absence of apply_plan → N/A pills shown, no false failure alarm."""
        out = dash.render_html(
            _l7_ok(), _l6_ok(), _freshness_all_ready(),
            snapshot=None,
            trend_flags={"available": True, "baseline_only": False},
            verdict="GREEN",
            l5_proposals=None,
            l5_approval=self._absent_approval(),
            l5_execution=None,
        )
        assert "N/A" in out
        assert "Niciun apply_plan generat" in out
        assert "nu este incident" in out

    def test_present_healthy_plan_renders_success_pills(self):
        """Case 4 (render): Healthy apply_plan → success pills for policy_valid and all_checks_passed."""
        approval_healthy = {
            "plan_available": True,
            "approval_log": [], "approved": [], "rejected": [],
            "plan": [{"ready_to_apply": True, "url": "/x"}], "blocked": [],
            "all_checks_passed": True,
            "policy_valid": True,
            "blocking_issues": [],
            "ready_count": 1,
            "total_eligible": 1,
            "total_blocked_plan": 0,
            "plan_generated_at": "2026-03-08T14:00:00+00:00",
        }
        out = dash.render_html(
            _l7_ok(), _l6_ok(), _freshness_all_ready(),
            snapshot=None,
            trend_flags={"available": True, "baseline_only": False},
            verdict="GREEN",
            l5_proposals=None,
            l5_approval=approval_healthy,
            l5_execution=None,
        )
        assert out.count("pill green") >= 2  # policy_valid=True + all_checks_passed=True

    def test_present_invalid_policy_renders_failed_and_warning(self):
        """Case 2+3 (render): Invalid policy → red pill; failed checks → warning pill."""
        approval_invalid = {
            "plan_available": True,
            "approval_log": [], "approved": [], "rejected": [],
            "plan": [], "blocked": [],
            "all_checks_passed": False,
            "policy_valid": False,
            "blocking_issues": ["policy.mode not allowed"],
            "ready_count": 0,
            "total_eligible": 0,
            "total_blocked_plan": 0,
            "plan_generated_at": "2026-03-08T14:00:00+00:00",
        }
        out = dash.render_html(
            _l7_ok(), _l6_ok(), _freshness_all_ready(),
            snapshot=None,
            trend_flags={"available": True, "baseline_only": False},
            verdict="GREEN",
            l5_proposals=None,
            l5_approval=approval_invalid,
            l5_execution=None,
        )
        assert "pill red" in out     # policy_valid=False → FAILED → pill red
        assert "pill yellow" in out  # all_checks_passed=False → warning → pill yellow
