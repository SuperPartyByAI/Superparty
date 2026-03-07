import json
from pathlib import Path
from agent.tasks.seo_level6_report_ledger import append_to_ledger, print_ledger_summary

def test_ledger_records_failures_correctly(tmp_path):
    ledger_file = tmp_path / "ledger.json"
    
    status = {
        "health": "failed",
        "priority": "skipped",
        "trend": "skipped",
        "overall_status": "failed",
        "run_at": "2026-03-08T10:00:00Z"
    }
    
    append_to_ledger(status, ledger_path=ledger_file)
    
    data = json.loads(ledger_file.read_text())
    assert len(data) == 1
    assert data[0]["status"] == "failed"
    assert data[0]["failing_stage"] == "health"
    assert data[0]["health_status"] == "failed"
    assert "run_id" in data[0]

def test_ledger_rotation_max_entires(tmp_path):
    ledger_file = tmp_path / "ledger.json"
    
    # simulate 35 runs
    for i in range(35):
        status = {
            "health": "success" if i % 2 == 0 else "failed",
            "priority": "success" if i % 2 == 0 else "skipped",
            "trend": "success" if i % 2 == 0 else "skipped",
            "overall_status": "success" if i % 2 == 0 else "failed",
            "run_at": f"2026-03-08T10:00:{i:02d}Z"
        }
        append_to_ledger(status, ledger_path=ledger_file, max_entries=30)
        
    data = json.loads(ledger_file.read_text())
    # Should only keep the last 30
    assert len(data) == 30
    # First entry should be index 5, which means 2026-03-08T10:00:05Z
    assert data[0]["timestamp"] == "2026-03-08T10:00:05Z"
    # Last entry should be index 34
    assert data[-1]["timestamp"] == "2026-03-08T10:00:34Z"

def test_ledger_backup_on_corrupt_file(tmp_path):
    ledger_file = tmp_path / "ledger.json"
    
    # Write corrupt JSON
    ledger_file.write_text("{corrupt: true", encoding="utf-8")
    
    status = {
        "health": "success",
        "priority": "success",
        "trend": "success",
        "overall_status": "success",
        "run_at": "2026-03-08T10:00:00Z"
    }
    
    res = append_to_ledger(status, ledger_path=ledger_file)
    assert res is True
    
    # Verify backup was created
    backups = list(tmp_path.glob("ledger.json.corrupt.*.bak"))
    assert len(backups) == 1
    
    # Verify new ledger was started cleanly
    data = json.loads(ledger_file.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["status"] == "success"
