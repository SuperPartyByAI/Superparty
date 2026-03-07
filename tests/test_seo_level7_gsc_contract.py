import pytest
import json
from pathlib import Path
from agent.tasks.seo_level7_gsc_contract import validate_raw_gsc_snapshot, enforce_retention_policy

@pytest.fixture
def valid_snapshot():
    return {
        "metadata": {
            "schema_version": "1.0",
            "source": "google_search_console",
            "property": "sc-domain:superparty.ro",
            "collected_at": "2026-03-08T00:00:00Z",
            "data_interval_days": 30,
            "dimensions": ["query", "page"],
            "metrics": ["clicks", "impressions", "ctr", "position"],
            "row_count": 2
        },
        "rows": [
            {"keys": ["animatori", "https://superparty.ro/animatori"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 2.5},
            {"keys": ["petreceri", "https://superparty.ro/petreceri"], "clicks": 5, "impressions": 50, "ctr": 0.1, "position": 4.0}
        ]
    }

def test_validate_success(valid_snapshot):
    assert validate_raw_gsc_snapshot(valid_snapshot) is True

def test_validate_missing_roots(valid_snapshot):
    del valid_snapshot["metadata"]
    assert validate_raw_gsc_snapshot(valid_snapshot) is False

def test_validate_wrong_schema_version(valid_snapshot):
    valid_snapshot["metadata"]["schema_version"] = "2.0"
    assert validate_raw_gsc_snapshot(valid_snapshot) is False

def test_validate_wrong_source(valid_snapshot):
    valid_snapshot["metadata"]["source"] = "google_analytics"
    assert validate_raw_gsc_snapshot(valid_snapshot) is False

def test_validate_wrong_property(valid_snapshot):
    valid_snapshot["metadata"]["property"] = "https://superparty.ro" # Not sc-domain:
    assert validate_raw_gsc_snapshot(valid_snapshot) is False

def test_validate_missing_metric(valid_snapshot):
    valid_snapshot["metadata"]["metrics"] = ["clicks", "impressions", "ctr"] # omitted "position"
    assert validate_raw_gsc_snapshot(valid_snapshot) is False

def test_validate_row_count_mismatch(valid_snapshot):
    valid_snapshot["metadata"]["row_count"] = 5
    assert validate_raw_gsc_snapshot(valid_snapshot) is False

def test_validate_0_rows_valid(valid_snapshot):
    # Tests the semantic that 0 rows is acceptable IF explicitly declared
    valid_snapshot["metadata"]["row_count"] = 0
    valid_snapshot["rows"] = []
    assert validate_raw_gsc_snapshot(valid_snapshot) is True

def test_enforce_retention_policy(tmp_path):
    snapshots_dir = tmp_path / "gsc"
    snapshots_dir.mkdir()
    
    # Create 35 dummy snapshot files
    for i in range(1, 36):
        # Naming them sequentially ensures sort works identically to timestamp suffix sort
        f = snapshots_dir / f"collect_202603{i:02d}.json"
        f.touch()
        
    deleted = enforce_retention_policy(snapshots_dir, max_snapshots=30)
    
    # Assert 5 files were deleted
    assert len(deleted) == 5
    # Assert files remaining is exactly 30
    remaining_files = list(snapshots_dir.glob("collect_*.json"))
    assert len(remaining_files) == 30
    
    # Ensure the oldest ones were deleted (01, 02, 03, 04, 05)
    names = [p.name for p in remaining_files]
    assert "collect_20260301.json" not in names
    assert "collect_20260335.json" in names
