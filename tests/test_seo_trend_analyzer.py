"""
Tests for seo_trend_analyzer.py — Level 4.1 PR #51
Covers: baseline_only, cluster présent în ambele snapshot-uri,
cluster nou, cluster dispărut, owner_share null/absent tratat sigur.
"""
import json
import pytest
from pathlib import Path
import agent.tasks.seo_trend_analyzer as analyzer_module
from agent.tasks.seo_trend_analyzer import (
    normalize_cluster_state,
    compute_deltas,
    run_trend_analysis,
    get_previous_snapshot_date,
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _make_health(clusters: dict) -> dict:
    return {"metadata": {"generated_at": "2026-03-07T10:00:00Z"}, "clusters": clusters}


def _make_priority(clusters: dict) -> dict:
    return {"metadata": {"priority_generated_at": "2026-03-07T10:01:00Z"}, "clusters": clusters}


# ─── Unit Tests: normalize_cluster_state ─────────────────────────────────────

class TestNormalizeClusterState:

    def test_normalizes_basic_fields(self):
        health = _make_health({
            "cluster_a": {"forbidden_count": 2, "owner_share": 0.625}
        })
        priority = _make_priority({
            "cluster_a": {"intelligence": {"priority_band": "A"}}
        })
        states = normalize_cluster_state(health, priority)
        assert states["cluster_a"]["priority_band"] == "A"
        assert states["cluster_a"]["forbidden_count"] == 2
        assert states["cluster_a"]["owner_share"] == 0.625

    def test_owner_share_none_defaults_to_zero(self):
        """Pre-PR50 health report senza owner_share — trebuie tratat ca 0.0."""
        health = _make_health({
            "cluster_b": {"forbidden_count": 1}  # fara owner_share
        })
        priority = _make_priority({
            "cluster_b": {"intelligence": {"priority_band": "B"}}
        })
        states = normalize_cluster_state(health, priority)
        assert states["cluster_b"]["owner_share"] == 0.0

    def test_handles_cluster_in_priority_but_not_health(self):
        """Cluster prezent în priority dar absent din health — fara crash."""
        health = _make_health({})
        priority = _make_priority({
            "cluster_c": {"intelligence": {"priority_band": "C"}}
        })
        states = normalize_cluster_state(health, priority)
        assert "cluster_c" in states
        assert states["cluster_c"]["forbidden_count"] == 0


# ─── Unit Tests: compute_deltas ──────────────────────────────────────────────

class TestComputeDeltas:

    def test_stable_cluster(self):
        curr = {"cluster_x": {"priority_band": "B", "forbidden_count": 1, "owner_share": 0.5}}
        prev = {"cluster_x": {"priority_band": "B", "forbidden_count": 1, "owner_share": 0.5}}
        deltas = compute_deltas(curr, prev)
        assert deltas[0]["status"] == "stable"
        assert deltas[0]["delta_forbidden"] == 0
        assert deltas[0]["delta_owner_share"] == 0.0

    def test_improved_cluster(self):
        curr = {"cluster_x": {"priority_band": "A", "forbidden_count": 1, "owner_share": 0.7}}
        prev = {"cluster_x": {"priority_band": "B", "forbidden_count": 3, "owner_share": 0.4}}
        deltas = compute_deltas(curr, prev)
        d = deltas[0]
        assert d["status"] == "improved"
        assert d["delta_forbidden"] == -2
        assert d["delta_owner_share"] == round(0.7 - 0.4, 4)
        assert d["delta_priority_band"] == "B->A"

    def test_regressed_cluster(self):
        curr = {"cluster_x": {"priority_band": "C", "forbidden_count": 4, "owner_share": 0.2}}
        prev = {"cluster_x": {"priority_band": "B", "forbidden_count": 1, "owner_share": 0.6}}
        deltas = compute_deltas(curr, prev)
        d = deltas[0]
        assert d["status"] == "regressed"
        assert d["delta_forbidden"] == 3

    def test_new_cluster(self):
        curr = {"cluster_new": {"priority_band": "C", "forbidden_count": 0, "owner_share": 0.0}}
        prev = {}
        deltas = compute_deltas(curr, prev)
        assert deltas[0]["status"] == "new"
        assert deltas[0]["previous"] is None
        assert "N/A->" in deltas[0]["delta_priority_band"]

    def test_missing_cluster(self):
        curr = {}
        prev = {"cluster_gone": {"priority_band": "A", "forbidden_count": 0, "owner_share": 0.8}}
        deltas = compute_deltas(curr, prev)
        assert deltas[0]["status"] == "missing"
        assert deltas[0]["current"] is None
        assert "->N/A" in deltas[0]["delta_priority_band"]


# ─── E2E Test: run_trend_analysis ────────────────────────────────────────────

def test_run_trend_analysis_baseline_only(tmp_path, monkeypatch):
    """
    Primul run fara snapshot anterior: baseline_only=True, clusters=[], nu fail.
    """
    reports = tmp_path / "reports" / "superparty"
    reports.mkdir(parents=True)
    history = reports / "history"
    history.mkdir()

    _write_json(reports / "seo_cluster_health.json", _make_health({
        "cluster_a": {"forbidden_count": 1, "owner_share": 0.5}
    }))
    _write_json(reports / "seo_cluster_priority.json", _make_priority({
        "cluster_a": {"intelligence": {"priority_band": "A"}}
    }))

    monkeypatch.setattr(analyzer_module, "REPORTS_DIR", reports)
    monkeypatch.setattr(analyzer_module, "HISTORY_DIR", history)
    monkeypatch.setattr(analyzer_module, "DELTA_FILE", reports / "seo_trend_delta.json")

    result = run_trend_analysis(current_date="2026-03-07")
    assert result is True

    delta_path = reports / "seo_trend_delta.json"
    assert delta_path.exists()

    with open(delta_path) as f:
        data = json.load(f)

    assert data["metadata"]["baseline_only"] is True
    assert data["metadata"]["mode"] == "read_only"
    assert data["clusters"] == []


def test_run_trend_analysis_with_previous_snapshot(tmp_path, monkeypatch):
    """
    Al doilea run cu snapshot anterior: produce delte reale, baseline_only=False.
    """
    reports = tmp_path / "reports" / "superparty"
    history = reports / "history"
    history.mkdir(parents=True)

    # Current reports
    _write_json(reports / "seo_cluster_health.json", _make_health({
        "cluster_a": {"forbidden_count": 1, "owner_share": 0.7}
    }))
    _write_json(reports / "seo_cluster_priority.json", _make_priority({
        "cluster_a": {"intelligence": {"priority_band": "A"}}
    }))

    # Previous snapshot (2026-03-06)
    snap_dir = history / "2026-03-06"
    snap_dir.mkdir()
    _write_json(snap_dir / "seo_cluster_health.json", _make_health({
        "cluster_a": {"forbidden_count": 3, "owner_share": 0.4}
    }))
    _write_json(snap_dir / "seo_cluster_priority.json", _make_priority({
        "cluster_a": {"intelligence": {"priority_band": "B"}}
    }))

    monkeypatch.setattr(analyzer_module, "REPORTS_DIR", reports)
    monkeypatch.setattr(analyzer_module, "HISTORY_DIR", history)
    monkeypatch.setattr(analyzer_module, "DELTA_FILE", reports / "seo_trend_delta.json")

    result = run_trend_analysis(current_date="2026-03-07")
    assert result is True

    with open(reports / "seo_trend_delta.json") as f:
        data = json.load(f)

    assert data["metadata"]["baseline_only"] is False
    assert data["metadata"]["previous_snapshot_date"] == "2026-03-06"
    assert len(data["clusters"]) == 1

    cluster = data["clusters"][0]
    assert cluster["cluster_id"] == "cluster_a"
    assert cluster["status"] == "improved"
    assert cluster["delta_forbidden"] == -2
    assert cluster["delta_owner_share"] == round(0.7 - 0.4, 4)
    assert cluster["delta_priority_band"] == "B->A"
    assert cluster["current"]["owner_share"] == 0.7
    assert cluster["previous"]["owner_share"] == 0.4
