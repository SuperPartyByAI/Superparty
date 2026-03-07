import pytest
import datetime
from pathlib import Path

from scripts.gsc_collection_worker import format_gsc_to_contract, save_snapshot_atomically
from agent.services.gsc_client import generate_gsc_date_range

def test_generate_gsc_date_range():
    start, end, interval = generate_gsc_date_range(days_lookback=30, days_delay=2)
    # Validate formats
    datetime.datetime.strptime(start, "%Y-%m-%d")
    datetime.datetime.strptime(end, "%Y-%m-%d")
    assert interval == 30

def test_format_gsc_to_contract_0_rows():
    api_response = {} # Simulat cand GSC response nu are key "rows" deloc
    snapshot = format_gsc_to_contract(api_response, 30)
    
    assert snapshot["metadata"]["row_count"] == 0
    assert len(snapshot["rows"]) == 0
    assert snapshot["metadata"]["schema_version"] == "1.0"
    assert snapshot["metadata"]["source"] == "google_search_console"
    assert snapshot["metadata"]["property"] == "sc-domain:superparty.ro"

def test_format_gsc_to_contract_with_data():
    api_response = {
        "rows": [
            {"keys": ["animatori", "https://superparty.ro/"], "clicks": 1.0, "impressions": 10.0, "ctr": 0.1, "position": 1.0}
        ]
    }
    snapshot = format_gsc_to_contract(api_response, 30)
    
    assert snapshot["metadata"]["row_count"] == 1
    row = snapshot["rows"][0]
    assert len(row["keys"]) == 2
    assert row["clicks"] == 1.0
    assert "ctr" in row

def test_save_snapshot_atomically(tmp_path):
    snapshot = {"test": "data"}
    dest_dir = tmp_path / "gsc"
    dest_dir.mkdir()
    
    final_path = save_snapshot_atomically(snapshot, dest_dir)
    assert final_path.exists()
    assert final_path.name.startswith("collect_")
    assert final_path.name.endswith(".json")
    assert "test" in final_path.read_text()
    
    # Assert temp files are cleaned
    tmp_files = list(dest_dir.glob("*.tmp"))
    assert len(tmp_files) == 0
