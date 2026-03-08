import pytest
import json
from pathlib import Path
from agent.tasks.seo_level7_gsc_ledger import (
    append_to_ledger,
    read_ledger,
    initialize_ledger_file,
    MAX_LEDGER_ENTRIES
)

def test_initialize_ledger(tmp_path):
    ledger_path = tmp_path / "gsc_ledger.json"
    initialize_ledger_file(ledger_path)
    assert ledger_path.exists()
    
    # Needs to be valid empty JSON array
    data = json.loads(ledger_path.read_text("utf-8"))
    assert data == []

def test_append_status_success(tmp_path):
    ledger_path = tmp_path / "gsc_ledger.json"
    entry = append_to_ledger(
        status="SUCCESS",
        row_count=50,
        snapshot_filename="collect_123.json",
        path=ledger_path
    )
    
    data = read_ledger(ledger_path)
    assert len(data) == 1
    assert data[0]["status"] == "SUCCESS"
    assert data[0]["row_count"] == 50
    assert data[0]["snapshot_filename"] == "collect_123.json"
    assert "collected_at" in data[0]
    assert "run_id" in data[0]

def test_append_status_failure(tmp_path):
    ledger_path = tmp_path / "gsc_ledger.json"
    append_to_ledger(
        status="FAILED",
        failing_stage="API_FETCH",
        error_reason="Quota Exceeded",
        path=ledger_path
    )
    
    data = read_ledger(ledger_path)
    assert len(data) == 1
    assert data[0]["status"] == "FAILED"
    assert data[0]["failing_stage"] == "API_FETCH"
    assert data[0]["error_reason"] == "Quota Exceeded"
    assert "row_count" not in data[0]

def test_ledger_rotation(tmp_path):
    ledger_path = tmp_path / "gsc_ledger.json"
    
    # Insert more than max allowed
    for i in range(MAX_LEDGER_ENTRIES + 5):
        append_to_ledger(f"STATUS_{i}", path=ledger_path)
        
    data = read_ledger(ledger_path)
    assert len(data) == MAX_LEDGER_ENTRIES
    
    # The oldest 5 should be gone. 
    # Index 5 was 'STATUS_5', so first should be STATUS_5
    assert data[0]["status"] == "STATUS_5"
    assert data[-1]["status"] == f"STATUS_{MAX_LEDGER_ENTRIES + 4}"

def test_read_corrupted_ledger_recovers(tmp_path):
    ledger_path = tmp_path / "gsc_ledger.json"
    ledger_path.write_text("invalid json { content")
    
    # Should detect corruption, backup, and return empty
    data = read_ledger(ledger_path)
    assert data == []
    
    # Backup should exist
    backup_path = ledger_path.with_suffix(".json.bak")
    assert backup_path.exists()
    assert backup_path.read_text() == "invalid json { content"
