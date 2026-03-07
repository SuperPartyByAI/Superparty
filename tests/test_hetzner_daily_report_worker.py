import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts.hetzner_daily_report_worker import validate_tmp_file, atomic_deploy, run_all_reports

def test_validate_tmp_file_success(tmp_path):
    f = tmp_path / "dummy.json"
    data = {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": "2026-03-08T00:00:00Z"
        },
        "clusters": {}
    }
    f.write_text(json.dumps(data))
    assert validate_tmp_file(f, "1.0", ["metadata", "clusters"]) is True

def test_validate_tmp_file_wrong_schema(tmp_path):
    f = tmp_path / "dummy.json"
    data = {
        "metadata": {
            "schema_version": "2.0",  # WRONG
            "generated_at": "2026-03-08T00:00:00Z"
        },
        "clusters": {}
    }
    f.write_text(json.dumps(data))
    assert validate_tmp_file(f, "1.0", ["metadata", "clusters"]) is False

def test_atomic_deploy_success_and_no_overwrite_on_failure(tmp_path):
    final_dir = tmp_path / "final"
    final_dir.mkdir()
    final_doc = final_dir / "target.json"
    final_doc.write_text("OLD_CONTENT")
    
    tmp_doc = tmp_path / "temp.json"
    data = {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": "2026-03-08T00:00:00Z"
        },
        "clusters": {}
    }
    tmp_doc.write_text(json.dumps(data))
    
    # 1. Fail: Wrong schema - should NOT overwrite final_doc
    assert atomic_deploy(tmp_doc, final_doc, "2.0", ["metadata", "clusters"]) is False
    assert final_doc.read_text() == "OLD_CONTENT"
    
    # 2. Success: Right schema - should overwrite final_doc atomically
    assert atomic_deploy(tmp_doc, final_doc, "1.0", ["metadata", "clusters"]) is True
    assert not tmp_doc.exists()  # Was moved
    assert "2026-03-08" in final_doc.read_text()

@patch("scripts.hetzner_daily_report_worker.run_cluster_health")
@patch("scripts.hetzner_daily_report_worker.run_business_priority_scoring")
@patch("scripts.hetzner_daily_report_worker.run_trend_analysis")
@patch("scripts.hetzner_daily_report_worker.TMP_DIR")
@patch("scripts.hetzner_daily_report_worker.REPORTS_DIR")
def test_run_all_reports_health_fails_priority_skipped(mock_reports, mock_tmp, mock_trend, mock_pri, mock_health):
    # Setup mock paths to prevent real writes
    mock_tmp.mkdir = MagicMock()
    
    # Force health engine to fail
    mock_health.return_value = False
    mock_trend.return_value = False
    
    status = run_all_reports()
    
    assert status["health"] == "failed"
    # Priority should be strictly skipped if health fails
    assert status["priority"] == "skipped"
    # Trend continues its run, but since mock_trend returns False it will be failed
    assert status["trend"] == "failed"
    assert status["overall_status"] == "failed"
    
    # Assert priority was never even called
    mock_pri.assert_not_called()

@patch("scripts.hetzner_daily_report_worker.run_cluster_health")
@patch("scripts.hetzner_daily_report_worker.run_business_priority_scoring")
@patch("scripts.hetzner_daily_report_worker.run_trend_analysis")
@patch("scripts.hetzner_daily_report_worker.TMP_DIR")
@patch("scripts.hetzner_daily_report_worker.REPORTS_DIR")
@patch("scripts.hetzner_daily_report_worker.json.dump")
@patch("builtins.open")
def test_worker_propagates_ledger_status_failure(mock_open, mock_dump, mock_reports, mock_tmp, mock_trend, mock_pri, mock_health):
    mock_tmp.mkdir = MagicMock()
    mock_reports.parent.mkdir = MagicMock()
    
    mock_health.return_value = True
    mock_pri.return_value = True
    mock_trend.return_value = True
    
    # We want atomic_deploy to return True so the engines succeed
    with patch("scripts.hetzner_daily_report_worker.atomic_deploy", return_value=True):
        # We force append_to_ledger to return False
        with patch("agent.tasks.seo_level6_report_ledger.append_to_ledger", return_value=False):
            status = run_all_reports()
    
    # Assert worker engines ran and succeeded
    assert status["health"] == "success"
    assert status["overall_status"] == "success"
    
    # Assert ledger failure was correctly logged into the status
    assert status["ledger_status"] == "failed"
