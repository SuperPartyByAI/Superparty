import pytest
import tempfile
import json
from pathlib import Path
from agent.tasks import seo_level4_priority

import agent.tasks.seo_level4_priority as priority_module

def test_run_business_priority_scoring_real_function(monkeypatch, tmp_path):
    """
    Test E2E by patching the reports directory resolution inside the module,
    then running the actual `run_business_priority_scoring` function.
    """
    # 1. Setup mock reports directory
    reports_dir = tmp_path / "reports" / "superparty"
    reports_dir.mkdir(parents=True)
    
    health_path = reports_dir / "seo_cluster_health.json"
    priority_path = reports_dir / "seo_cluster_priority.json"
    
    # Create the mock health data
    mock_health = {
        "metadata": {"generated_at": "2026-03-07T00:00:00Z"},
        "clusters": {
            "mock_cluster_a": {
                "is_money_cluster": True,
                "total_impressions": 1500,
                "owner_present": False,
                "cannibalization_warnings": []
            }
        }
    }
    with open(health_path, "w", encoding="utf-8") as f:
        json.dump(mock_health, f)
        
    # We also need to mock the json loaders so the test is deterministic regardless of the repo's real JSONs.
    mock_weights = {
        "importance": {
            "tier_points": {"A": 100},
            "business_priority_points": {"critical": 50},
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
    mock_registry = {
        "mock_cluster_a": {
            "risk_tier": "A",
            "business_priority": "critical"
        }
    }
    
    monkeypatch.setattr(priority_module, "load_priority_weights", lambda: mock_weights)
    monkeypatch.setattr(priority_module, "load_registry_policies", lambda: mock_registry)
    
    # 2. Patch the reports directory resolution dynamically inside the module
    # We patch the Path object in the module to return our tmp_path when it resolves parents
    # An easier way is to monkeypatch the specific lines if refactored, but since it's hardcoded:
    # reports_dir = Path(__file__).parent.parent.parent / "reports" / "superparty"
    # We can patch pathlib.Path to return our mocked reports dir when called with specific args,
    # OR redefine the function logic slightly. Since we shouldn't change the source just for tests,
    # let's write a small dummy wrapper inside the test that overrides the python globals.
    
    # Instead of fighting Path(), we can just modify the module's file text or temporarily override where reports_dir points if it was a module variable.
    # Since `reports_dir` is local:
    
    # The most robust way without changing source is to patch open() and Path.exists() just for these files.
    # But for a stable enterprise test, let's modify the source code of `seo_level4_priority.py` to accept an optional `reports_dir` argument!
    # Wait, the prompt says do not change the source code just for tests unless necessary, but making it dependency-injectable is enterprise standard.
    # For now, I'll use Python's mock to patch `Path` in the module namespace.
    
    class MockPath:
        def __init__(self, *args, **kwargs):
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
            
    monkeypatch.setattr(priority_module, "Path", MockPath)
    
    # 3. Call the actual function
    result = priority_module.run_business_priority_scoring()
    
    # 4. Assertions
    assert result is True, "The function should execute successfully"
    
    # Assert health report remains completely intact
    with open(health_path, "r", encoding="utf-8") as f:
        intact_health = json.load(f)
        assert "clusters" in intact_health
        assert "intelligence" not in intact_health["clusters"]["mock_cluster_a"], "Source health report must NOT be mutated"
        
    # Assert priority report was created safely
    assert priority_path.exists(), "Priority output JSON must be created separately"
    
    with open(priority_path, "r", encoding="utf-8") as f:
        priority_data = json.load(f)
        
        # Verify Metadata
        assert "metadata" in priority_data
        assert "source_report_generated_at" in priority_data["metadata"]
        assert priority_data["metadata"]["source_report_generated_at"] == "2026-03-07T00:00:00Z"
        assert "priority_generated_at" in priority_data["metadata"]
        
        # Verify Clusters Payload
        cluster = priority_data["clusters"]["mock_cluster_a"]
        assert "intelligence" in cluster, "Priority root must contain intelligence key"
        
        intel = cluster["intelligence"]
        # Scoring Math: Tier A(100) + Money(50) + HighVol(20) + CritBiz(50) = 220 Importance
        # Risk: Missing Owner (x2.0) = 2.0
        # Priority: 440
        assert intel["importance_score"] == 220
        assert intel["risk_score"] == 2.0
        assert intel["priority_score"] == 440
        assert intel["priority_band"] == "critical"
        assert intel["recommended_action"] == "investigate_owner_drift"
        assert "explanation" in intel
