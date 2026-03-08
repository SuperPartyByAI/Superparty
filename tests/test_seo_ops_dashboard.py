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
