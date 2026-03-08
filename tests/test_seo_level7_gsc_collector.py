import pytest
import datetime
from pathlib import Path

from scripts.gsc_collection_worker import format_gsc_to_contract, save_snapshot_atomically, main
from agent.services.gsc_client import generate_gsc_date_range
from unittest.mock import patch

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

@patch("scripts.gsc_collection_worker.fetch_search_analytics")
def test_worker_main_fails_closed_on_api_error(mock_fetch):
    # Simulate API failure
    mock_fetch.side_effect = Exception("Google Cloud Quota Exceeded")
    
    with pytest.raises(SystemExit) as excinfo:
        main()
        
    assert excinfo.value.code == 1

@patch("scripts.gsc_collection_worker.validate_raw_gsc_snapshot")
@patch("scripts.gsc_collection_worker.format_gsc_to_contract")
@patch("scripts.gsc_collection_worker.fetch_search_analytics")
def test_worker_main_fails_closed_on_contract_failure(mock_fetch, mock_format, mock_validate):
    # Simulate API success but Contract rejection
    mock_fetch.return_value = {"rows": []}
    mock_format.return_value = {"metadata": {}}
    mock_validate.return_value = False
    
    with pytest.raises(SystemExit) as excinfo:
        main()
        
    assert excinfo.value.code == 1

@patch("scripts.gsc_collection_worker.save_snapshot_atomically")
@patch("scripts.gsc_collection_worker.validate_raw_gsc_snapshot")
@patch("scripts.gsc_collection_worker.format_gsc_to_contract")
@patch("scripts.gsc_collection_worker.fetch_search_analytics")
def test_worker_main_fails_closed_on_persist_failure(mock_fetch, mock_format, mock_validate, mock_save):
    # Simulate valid data but OSError on disk write
    mock_validate.return_value = True
    mock_save.side_effect = OSError("Permission Denied")
    
    with pytest.raises(SystemExit) as excinfo:
        main()
        
    assert excinfo.value.code == 1
