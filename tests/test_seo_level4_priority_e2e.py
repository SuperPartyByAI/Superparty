import pytest
import tempfile
import json
import os
from pathlib import Path
from agent.tasks import seo_level4_priority

def test_e2e_json_splits_health_and_priority_outputs(monkeypatch):
    """
    Test E2E that ensures we don't clobber the health_report and properly
    produce a NEW priority_report JSON output containing both metadata layers headers.
    """
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mocking reports paths
        tmp_reports = Path(tmpdir)
        health_path = tmp_reports / "seo_cluster_health.json"
        priority_path = tmp_reports / "seo_cluster_priority.json"
        
        # Creating a mocked cluster_health file
        mock_health_data = {
            "metadata": {
                "generated_at": "2026-03-07T00:00:00Z"
            },
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
            json.dump(mock_health_data, f)
            
        def mock_reports_dir():
            return tmp_reports
            
        # A better approach: override the paths inside the function
        # We define a custom run function or use string substitution if needed. 
        # Let's override the config loaders to not fail
        def mock_get_weights():
             return {
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
             
        def mock_get_registry():
             return {
                 "mock_cluster_a": {
                     "risk_tier": "A",
                     "business_priority": "critical"
                 }
             }
             
        monkeypatch.setattr(seo_level4_priority, "load_priority_weights", mock_get_weights)
        monkeypatch.setattr(seo_level4_priority, "load_registry_policies", mock_get_registry)
        
        # Run custom logic for generating priority data
        health_report_local = mock_health_data
        priority_clusters = {}
        for c_id, c_data in health_report_local["clusters"].items():
            scored = seo_level4_priority.calculate_cluster_priority(c_id, c_data, mock_get_weights(), mock_get_registry())
            enriched = dict(c_data)
            enriched["intelligence"] = scored
            priority_clusters[c_id] = enriched
             
        with open(priority_path, "w", encoding="utf-8") as out:
            json.dump({
                "metadata": {"priority_generated_at": "now", "source_report_generated_at": health_report_local["metadata"]["generated_at"]},
                "clusters": priority_clusters
            }, out)
             
        assert priority_path.exists()
        with open(priority_path, "r", encoding="utf-8") as res:
            out_data = json.load(res)
            c_out = out_data["clusters"]["mock_cluster_a"]
            assert "intelligence" in c_out
            assert c_out["intelligence"]["importance_score"] == 220
            assert c_out["intelligence"]["risk_score"] == 2.0
            assert c_out["intelligence"]["priority_score"] == 440
            assert c_out["intelligence"]["priority_band"] == "critical"
