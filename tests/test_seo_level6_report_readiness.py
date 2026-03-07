import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest
from agent.tasks.seo_level6_report_readiness import (
    validate_report,
    _parse_iso_date,
    ReportReadinessError,
    REQUIRED_REPORTS
)

@pytest.fixture
def mock_reports_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("agent.tasks.seo_level6_report_readiness.REPORTS_DIR", tmp_path)
    return tmp_path

def test_parse_iso_date_valid():
    dt = _parse_iso_date("2026-03-07T20:34:37+00:00")
    assert dt.year == 2026
    assert dt.tzinfo is not None

def test_parse_iso_date_zulu():
    dt = _parse_iso_date("2026-03-07T20:34:37Z")
    assert dt.tzinfo is not None

def test_parse_iso_date_invalid():
    with pytest.raises(ReportReadinessError):
        _parse_iso_date("not-a-date")

def test_validate_report_missing_required(mock_reports_dir):
    config = REQUIRED_REPORTS["health"]
    with pytest.raises(ReportReadinessError, match="Missing required report"):
        validate_report("health", config)

def test_validate_report_missing_optional(mock_reports_dir):
    config = REQUIRED_REPORTS["priority"]  # This is marked optional
    res = validate_report("priority", config)
    assert res["status"] == "missing_optional"

def test_validate_report_invalid_json(mock_reports_dir):
    config = REQUIRED_REPORTS["health"]
    f = mock_reports_dir / config["filename"]
    f.write_text("{bad_json")
    
    with pytest.raises(ReportReadinessError, match="Invalid JSON"):
        validate_report("health", config)

def test_validate_report_missing_keys(mock_reports_dir):
    config = REQUIRED_REPORTS["health"]
    f = mock_reports_dir / config["filename"]
    f.write_text(json.dumps({"metadata": {}}))  # Missing 'clusters'
    
    with pytest.raises(ReportReadinessError, match="Missing root key 'clusters'"):
        validate_report("health", config)

def test_validate_report_stale(mock_reports_dir):
    config = REQUIRED_REPORTS["health"]
    f = mock_reports_dir / config["filename"]
    
    # 50 hours ago
    past_date = (datetime.now(timezone.utc) - timedelta(hours=50)).isoformat()
    
    data = {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": past_date
        },
        "clusters": {}
    }
    f.write_text(json.dumps(data))
    
    with pytest.raises(ReportReadinessError, match="Report stale"):
        validate_report("health", config)

def test_validate_report_success(mock_reports_dir):
    config = REQUIRED_REPORTS["health"]
    f = mock_reports_dir / config["filename"]
    
    # 2 hours ago
    valid_date = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    
    data = {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": valid_date
        },
        "clusters": {}
    }
    f.write_text(json.dumps(data))
    
    res = validate_report("health", config)
    assert res["status"] == "ready"
    assert "age_hours" in res

def test_priority_timestamp_fallback(mock_reports_dir):
    config = REQUIRED_REPORTS["priority"]
    f = mock_reports_dir / config["filename"]
    
    valid_date = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    
    data = {
        "metadata": {
            "schema_version": "2.0",
            "generated_at": valid_date # Priority allows fallback to generated_at
        },
        "clusters": {}
    }
    f.write_text(json.dumps(data))
    
    res = validate_report("priority", config)
    assert res["status"] == "ready"

def test_priority_timestamp_direct(mock_reports_dir):
    config = REQUIRED_REPORTS["priority"]
    f = mock_reports_dir / config["filename"]
    
    valid_date = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    
    data = {
        "metadata": {
            "schema_version": "2.0",
            "priority_generated_at": valid_date 
        },
        "clusters": {}
    }
    f.write_text(json.dumps(data))
    
    res = validate_report("priority", config)
    assert res["status"] == "ready"

def test_trends_schema_success(mock_reports_dir):
    config = REQUIRED_REPORTS["trends"]
    f = mock_reports_dir / config["filename"]
    
    valid_date = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    
    data = {
        "metadata": {
            "schema_version": "1.1",
            "generated_at": valid_date 
        },
        "clusters": {}
    }
    f.write_text(json.dumps(data))
    
    res = validate_report("trends", config)
    assert res["status"] == "ready"
