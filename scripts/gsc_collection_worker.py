import os
import sys
import json
import logging
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

from agent.services.gsc_client import fetch_search_analytics, generate_gsc_date_range
from agent.tasks.seo_level7_gsc_contract import validate_raw_gsc_snapshot, enforce_retention_policy

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("gsc_worker")

PROPERTY_URI = "sc-domain:superparty.ro"
REPORTS_DIR = Path("reports/superparty/gsc")

def format_gsc_to_contract(api_response: dict, interval_days: int) -> dict:
    """
    Transforms the raw API response into the strict L7.1 snapshot format.
    """
    collected_at = datetime.now(timezone.utc).isoformat()
    # If GSC returns no rows, 'rows' key might be missing in API response
    api_rows = api_response.get("rows", [])
    
    formatted_rows = []
    for r in api_rows:
        formatted_rows.append({
            "keys": r.get("keys", []),
            "clicks": r.get("clicks", 0.0),
            "impressions": r.get("impressions", 0.0),
            "ctr": r.get("ctr", 0.0),
            "position": r.get("position", 0.0)
        })

    snapshot = {
        "metadata": {
            "schema_version": "1.0",
            "source": "google_search_console",
            "property": PROPERTY_URI,
            "collected_at": collected_at,
            "data_interval_days": interval_days,
            "dimensions": ["query", "page"],
            "metrics": ["clicks", "impressions", "ctr", "position"],
            "row_count": len(formatted_rows)
        },
        "rows": formatted_rows
    }
    return snapshot

def save_snapshot_atomically(snapshot: dict, dest_dir: Path) -> Path:
    """
    Persists the snapshot payload atomically to disk.
    File format: collect_YYYYMMDDTHHMMSS.json
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    filename = f"collect_{timestamp}.json"
    final_path = dest_dir / filename
    
    # Atomic write pattern
    fd, tmp_path = tempfile.mkstemp(dir=dest_dir, suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(snapshot, f, indent=2)
        
    shutil.move(tmp_path, final_path)
    return final_path

def main():
    log.info("Starting GSC Collector Worker...")
    
    # 1. Generate temporal window
    start_date, end_date, interval_days = generate_gsc_date_range(days_lookback=30, days_delay=2)
    
    # 2. Fetch API Layer (fail-closed, will raise exception on quota/auth issues)
    try:
        raw_response = fetch_search_analytics(
            property_uri=PROPERTY_URI,
            start_date=start_date,
            end_date=end_date,
            dimensions=["query", "page"]
        )
    except Exception as e:
        log.error("API Error encountered. Aborting fetch. No data spoofing allowed.")
        sys.exit(1)
        
    # 3. Transform
    snapshot = format_gsc_to_contract(raw_response, interval_days)
    
    # 4. Strict Contract Validation (L7.1)
    if not validate_raw_gsc_snapshot(snapshot):
        log.error("Snapshot failed L7.1 structural validation. Aborting persistence.")
        sys.exit(1)
        
    # 5. Persist Atomically
    try:
        final_path = save_snapshot_atomically(snapshot, REPORTS_DIR)
        log.info(f"Snapshot atomically saved to {final_path}")
    except OSError as e:
        log.error(f"Failed to persist snapshot: {e}")
        sys.exit(1)
        
    # 6. Retention Policy
    enforce_retention_policy(REPORTS_DIR, max_snapshots=30)
    
    log.info("GSC Collector Worker run complete: SUCCESS.")

if __name__ == "__main__":
    main()
