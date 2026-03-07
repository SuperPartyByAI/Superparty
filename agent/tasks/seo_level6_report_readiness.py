"""
SEO Level 6 — Report Readiness Gate (PR #64)

Validates the integrity, schema, and freshness of source input reports before
allowing any downstream processing (like dry-runs).
Fails hard (exit 1 or Exception) if inputs are stale or invalid.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent
REPORTS_DIR = ROOT_DIR / "reports" / "superparty"

# Requirements for input files
REQUIRED_REPORTS = {
    "health": {
        "filename": "seo_cluster_health.json",
        "max_age_hours": 48,
        "required_keys": ["metadata", "clusters"],
        "schema_version": "1.0",
    },
    "priority": {
        "filename": "seo_cluster_priority.json",
        "max_age_hours": 48,
        "required_keys": ["metadata", "priorities"],
        "schema_version": "1.0",
        "optional": True, # For now, until L6.2 creates it officially
    },
    "trends": {
        "filename": "seo_trend_delta.json",
        "max_age_hours": 72,
        "required_keys": ["metadata", "trends"],
        "schema_version": "1.0",
        "optional": True, # L6.2
    }
}

class ReportReadinessError(Exception):
    """Raised when an input report fails validation."""
    pass


def _parse_iso_date(date_str: str) -> datetime:
    """Safely parse an ISO date string to a timezone-aware datetime."""
    try:
        # Provide fallback for older python versions if missing fromisoformat tz support
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError as e:
        raise ReportReadinessError(f"Invalid generated_at format: {date_str}") from e


def validate_report(report_id: str, config: Dict[str, Any], now: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Validate a single report against its schema, keys, and freshness rules.
    Returns a status dict. Raises ReportReadinessError if validation fails 
    and the report is strictly required.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    file_path = REPORTS_DIR / config["filename"]
    
    if not file_path.exists():
        if config.get("optional"):
            return {"status": "missing_optional", "reason": "File not found but marked optional."}
        raise ReportReadinessError(f"Missing required report: {config['filename']}")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ReportReadinessError(f"Invalid JSON in {config['filename']}: {e}")

    # Root keys check
    for key in config["required_keys"]:
        if key not in data:
            raise ReportReadinessError(f"Missing root key '{key}' in {config['filename']}")

    meta = data["metadata"]
    
    # Schema check
    if meta.get("schema_version") != config["schema_version"]:
        raise ReportReadinessError(
            f"Schema mismatch in {config['filename']}. Expected {config['schema_version']}, "
            f"got {meta.get('schema_version')}"
        )

    # Freshness check
    gen_at_str = meta.get("generated_at")
    if not gen_at_str:
        raise ReportReadinessError(f"Missing metadata.generated_at in {config['filename']}")
        
    generated_at = _parse_iso_date(gen_at_str)
    age = now - generated_at
    
    # Avoid negative age edge cases (future dating)
    if age.total_seconds() < -3600:
         raise ReportReadinessError(f"Report {config['filename']} is future-dated (> 1h): {gen_at_str}")

    max_age = timedelta(hours=config["max_age_hours"])
    if age > max_age:
        raise ReportReadinessError(
            f"Report stale: {config['filename']} is {age.total_seconds() / 3600:.1f}h old "
            f"(max allowed: {config['max_age_hours']}h)."
        )

    return {
        "status": "ready",
        "generated_at": gen_at_str,
        "age_hours": round(age.total_seconds() / 3600, 2)
    }


def assert_inputs_ready() -> Dict[str, Any]:
    """
    Validates all configured input reports.
    Returns an aggregated readiness status dictionary.
    Raises ReportReadinessError immediately if any required report fails.
    """
    now = datetime.now(timezone.utc)
    results = {}
    
    for report_id, config in REQUIRED_REPORTS.items():
        results[report_id] = validate_report(report_id, config, now=now)
        
    return {
        "status": "ready",
        "checked_at": now.isoformat(),
        "reports": results
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys
    try:
        res = assert_inputs_ready()
        print(json.dumps(res, indent=2))
        sys.exit(0)
    except ReportReadinessError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
