import pytest
from pathlib import Path
from agent.tasks.seo_level4_priority import calculate_cluster_priority

@pytest.fixture
def mock_weights():
    return {
        "importance": {
            "tier_points": {"A": 100, "B": 50, "C": 10},
            "business_priority_points": {"critical": 50, "high": 30, "medium": 10, "low": 0},
            "is_money_cluster_bonus": 50,
            "volume_thresholds": {"high": 1000, "high_bonus": 20, "medium": 100, "medium_bonus": 5}
        },
        "risk": {
            "base_risk": 1.0,
            "owner_missing_multiplier": 2.0,
            "conflict_multipliers": {"high_severity": 0.5, "medium_severity": 0.2}
        },
        "priority_bands": {"critical": 300, "high": 150, "medium": 50, "low": 0}
    }

@pytest.fixture
def mock_registry():
    return {
        "tier_a_money": {
            "risk_tier": "A",
            "business_priority": "critical"
        },
        "tier_b_sector": {
            "risk_tier": "B",
            "business_priority": "high"
        },
        "tier_c_blog": {
            "risk_tier": "C",
            "business_priority": "low"
        }
    }

def test_formula_distinguishes_healthy_but_important_cluster(mock_weights, mock_registry):
    cluster_data = {
        "is_money_cluster": True,
        "total_impressions": 5000,
        "owner_present": True,
        "cannibalization_warnings": []
    }
    
    # Needs: Tier A (100) + Biz Crit (50) + Money (50) + High Vol (20) = Importance 220
    # Risk Base = 1.0. Priority = 220 => High Band
    res = calculate_cluster_priority("tier_a_money", cluster_data, mock_weights, mock_registry)
    
    assert res["importance_score"] == 220
    assert res["risk_score"] == 1.0
    assert res["priority_score"] == 220
    assert res["priority_band"] == "high"
    assert res["recommended_action"] == "monitor_only"
    assert res["explanation"]["base_importance"] == 220


def test_formula_flags_tier_A_forbidden_conflict(mock_weights, mock_registry):
    cluster_data = {
        "is_money_cluster": True,
        "total_impressions": 5000,
        "owner_present": True,
        "cannibalization_warnings": [
            {"severity": "high", "classification": "forbidden"},
            {"severity": "medium", "classification": "unknown"}
        ]
    }
    
    # Importance: 220
    # Risk: base (1.0) + 1*forbidden(0.5) + 1*unknown(0.2) = 1.7
    # Priority = 220 * 1.7 = 374 -> Critical
    res = calculate_cluster_priority("tier_a_money", cluster_data, mock_weights, mock_registry)
    
    assert res["risk_score"] == 1.7
    assert res["priority_score"] == 374
    assert res["priority_band"] == "critical"
    assert res["recommended_action"] == "escalate_tier_a_conflict"


def test_formula_owner_missing_tier_b(mock_weights, mock_registry):
    cluster_data = {
        "is_money_cluster": True,
        "total_impressions": 50,
        "owner_present": False,
        "cannibalization_warnings": []
    }
    
    # Tier B (50) + High (30) + Money (50) + Low Vol (0) = 130
    # Risk = 1.0 * Missing (2.0) = 2.0
    # Priority = 260 -> Critical (missing owner on money is bad)
    res = calculate_cluster_priority("tier_b_sector", cluster_data, mock_weights, mock_registry)
    assert res["risk_score"] == 2.0
    assert res["priority_score"] == 260
    assert res["recommended_action"] == "investigate_owner_drift"
