"""
Unit + E2E tests for seo_level4_gap_detector.py
"""
import pytest
import json
from pathlib import Path
from agent.tasks.seo_level4_gap_detector import (
    analyze_cluster_gap,
    run_gap_detection,
    load_gap_thresholds,
)

# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def default_thresholds():
    return load_gap_thresholds()

@pytest.fixture
def conservative_policy():
    return {"expansion_policy": "conservative"}

@pytest.fixture
def flexible_policy():
    return {"expansion_policy": "flexible"}


# ─── Unit Tests: analyze_cluster_gap ────────────────────────────────────────

class TestAnalyzeClusterGap:

    def test_missing_owner_tier_a_is_high_confidence(self, default_thresholds, conservative_policy):
        cluster = {
            "total_impressions": 500,
            "owner_present": False,
            "forbidden_count": 0,
            "unknown_count": 1,
            "supporter_count": 2,
            "cannibalization_warnings": [],
            "intelligence": {"tier": "A", "importance_score": 200, "risk_score": 2.0}
        }
        result = analyze_cluster_gap("test_a", cluster, conservative_policy, default_thresholds)
        assert result is not None
        assert "missing_owner" in result["gap_signals"]
        assert result["opportunity_type"] == "optimize_owner"
        assert result["confidence"] == "high"

    def test_missing_owner_tier_c_is_medium_confidence(self, default_thresholds, conservative_policy):
        cluster = {
            "total_impressions": 30,
            "owner_present": False,
            "forbidden_count": 0,
            "unknown_count": 0,
            "supporter_count": 0,
            "cannibalization_warnings": [],
            "intelligence": {"tier": "C", "importance_score": 10, "risk_score": 1.0}
        }
        result = analyze_cluster_gap("test_c_no_owner", cluster, conservative_policy, default_thresholds)
        assert result is not None
        assert result["confidence"] == "medium"

    def test_high_unknown_ratio_triggers_review_signal(self, default_thresholds, conservative_policy):
        cluster = {
            "total_impressions": 200,
            "owner_present": True,
            "forbidden_count": 0,
            "unknown_count": 5,
            "supporter_count": 1,
            "cannibalization_warnings": [],
            "intelligence": {"tier": "B", "importance_score": 80, "risk_score": 1.2}
        }
        result = analyze_cluster_gap("test_high_unknown", cluster, conservative_policy, default_thresholds)
        assert result is not None
        assert "high_unknown_ratio" in result["gap_signals"]
        assert result["opportunity_type"] == "review_registry_mapping"

    def test_weak_owner_via_owner_share_below_threshold(self, default_thresholds, conservative_policy):
        """Tier B cluster cu owner present dar owner_share < 0.4 trebuie detectat ca weak_owner."""
        cluster = {
            "total_impressions": 800,
            "owner_present": True,
            "owner_share": 0.25,  # < 0.4 threshold => weak_owner
            "forbidden_count": 0,
            "unknown_count": 0,
            "supporter_count": 3,
            "cannibalization_warnings": [],
            "intelligence": {"tier": "B", "importance_score": 60, "risk_score": 1.0}
        }
        result = analyze_cluster_gap("test_b_weak_owner", cluster, conservative_policy, default_thresholds)
        assert result is not None
        assert "weak_owner" in result["gap_signals"]
        assert result["opportunity_type"] == "optimize_owner"
        assert result["confidence"] == "medium"
        assert result["context"]["owner_share"] == 0.25

    def test_strong_owner_share_does_not_trigger_weak_owner(self, default_thresholds, conservative_policy):
        """Tier B cu owner_share > 0.4 NU trebuie sa fie weak_owner."""
        cluster = {
            "total_impressions": 800,
            "owner_present": True,
            "owner_share": 0.75,  # > 0.4 => healthy
            "forbidden_count": 0,
            "unknown_count": 0,
            "supporter_count": 2,
            "cannibalization_warnings": [],
            "intelligence": {"tier": "B", "importance_score": 60, "risk_score": 1.0}
        }
        result = analyze_cluster_gap("test_b_strong_owner", cluster, conservative_policy, default_thresholds)
        assert result is None, "Cluster cu owner_share > threshold nu este un gap"

    def test_tier_a_conservative_healthy_cluster_returns_none(self, default_thresholds, conservative_policy):
        """Healthy Tier A conservative cluster should NOT be a gap — it is the ideal state."""
        cluster = {
            "total_impressions": 5000,
            "owner_present": True,
            "owner_share": 0.85,
            "forbidden_count": 0,
            "unknown_count": 0,
            "supporter_count": 3,
            "cannibalization_warnings": [],
            "intelligence": {"tier": "A", "importance_score": 220, "risk_score": 1.0}
        }
        result = analyze_cluster_gap("test_a_healthy", cluster, conservative_policy, default_thresholds)
        assert result is None, "A healthy conservative Tier A cluster is NOT a gap and must return None"

    def test_healthy_tier_c_cluster_returns_none(self, default_thresholds, flexible_policy):
        """A healthy, small, flexible cluster with no gaps should return None."""
        cluster = {
            "total_impressions": 500,
            "owner_present": True,
            "owner_share": 0.8,
            "forbidden_count": 0,
            "unknown_count": 0,
            "supporter_count": 2,
            "cannibalization_warnings": [],
            "intelligence": {"tier": "C", "importance_score": 20, "risk_score": 1.0}
        }
        result = analyze_cluster_gap("test_c_healthy", cluster, flexible_policy, default_thresholds)
        assert result is None


# ─── E2E Test: run_gap_detection ────────────────────────────────────────────

import agent.tasks.seo_level4_gap_detector as gap_module

def test_run_gap_detection_e2e(monkeypatch, tmp_path):
    """
    Full E2E: mocks priority report + registry, calls run_gap_detection(),
    asserts output file exists and is structurally correct.
    """
    reports_dir = tmp_path / "reports" / "superparty"
    reports_dir.mkdir(parents=True)

    # Mock a priority report with 2 clusters: one with gap, one healthy
    mock_priority = {
        "metadata": {"priority_generated_at": "2026-03-07T00:00:00Z"},
        "clusters": {
            "cluster_with_gap": {
                "total_impressions": 200,
                "owner_present": False,
                "forbidden_count": 1,
                "unknown_count": 2,
                "supporter_count": 0,
                "cannibalization_warnings": [],
                "intelligence": {"tier": "A", "importance_score": 150, "risk_score": 2.0}
            },
            "cluster_healthy": {
                "total_impressions": 1000,
                "owner_present": True,
                "forbidden_count": 0,
                "unknown_count": 0,
                "supporter_count": 3,
                "cannibalization_warnings": [],
                "intelligence": {"tier": "C", "importance_score": 20, "risk_score": 1.0}
            }
        }
    }

    priority_path = reports_dir / "seo_cluster_priority.json"
    with open(priority_path, "w", encoding="utf-8") as f:
        json.dump(mock_priority, f)

    mock_registry = {
        "cluster_with_gap": {"expansion_policy": "conservative"},
        "cluster_healthy": {"expansion_policy": "flexible"}
    }

    # Monkeypatch loaders
    monkeypatch.setattr(gap_module, "load_priority_report", lambda: mock_priority)
    monkeypatch.setattr(gap_module, "load_registry", lambda: mock_registry)

    # Patch the output path to write to tmp_path
    class MockPath:
        def __init__(self, *args):
            self.args = args
        @property
        def parent(self):
            return self
        def __truediv__(self, other):
            if other == "reports":
                return self
            elif other == "superparty":
                return Path(reports_dir)
            return Path(reports_dir) / other

    monkeypatch.setattr(gap_module, "Path", MockPath)

    result = gap_module.run_gap_detection()
    assert result is True

    gap_path = reports_dir / "seo_gap_opportunities.json"
    assert gap_path.exists(), "Gap opportunities output must be created"

    with open(gap_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "metadata" in data
    assert data["metadata"]["mode"] == "read_only"
    assert data["metadata"]["total_clusters_analyzed"] == 2
    assert "opportunities" in data

    # The gap cluster should appear; healthy Tier C flexible should not
    ids_in_output = [o["cluster_id"] for o in data["opportunities"]]
    assert "cluster_with_gap" in ids_in_output, "Cluster with gap must be flagged"

    # Verify structure of each opportunity
    for opp in data["opportunities"]:
        assert "tier" in opp
        assert "opportunity_type" in opp
        assert "confidence" in opp
        assert "gap_signals" in opp
        assert "context" in opp
        assert "suggested_action" in opp
