import json
import logging
from typing import Dict, Any, List
from pathlib import Path

log = logging.getLogger("gsc_contract")

REQUIRED_SCHEMA_VERSION = "1.0"
REQUIRED_SOURCE = "google_search_console"
REQUIRED_METRICS = {"clicks", "impressions", "ctr", "position"}
REQUIRED_DIMENSIONS = {"query", "page"}

def validate_raw_gsc_snapshot(data: Dict[str, Any]) -> bool:
    """
    Validates a raw GSC API JSON dump against the strict L7 contract.
    Fails closed on any schema, source, or structural mismatch.
    """
    
    # 1. Structure check
    if "metadata" not in data or "rows" not in data:
        log.error("Missing mandatory root keys: 'metadata' or 'rows'.")
        return False
        
    meta = data["metadata"]
    
    # 2. Schema and Source validation
    if meta.get("schema_version") != REQUIRED_SCHEMA_VERSION:
        log.error(f"Invalid schema_version. Expected {REQUIRED_SCHEMA_VERSION}, got {meta.get('schema_version')}")
        return False
        
    if meta.get("source") != REQUIRED_SOURCE:
        log.error(f"Invalid source. Expected {REQUIRED_SOURCE}, got {meta.get('source')}")
        return False
        
    # 3. Property validation
    if not meta.get("property") or not meta["property"].startswith("sc-domain:"):
        log.error(f"Invalid property format. Expected sc-domain:..., got {meta.get('property')}")
        return False
        
    # 4. Collection timings validation
    if not meta.get("collected_at") or not meta.get("data_interval_days"):
        log.error("Missing collection temporal context (collected_at, data_interval_days)")
        return False
        
    # 5. Dimensions and metrics declaration
    declared_dims = set(meta.get("dimensions", []))
    declared_metrics = set(meta.get("metrics", []))
    
    if not REQUIRED_DIMENSIONS.issubset(declared_dims):
        log.error(f"Missing required dimensions. Got: {declared_dims}")
        return False
        
    if not REQUIRED_METRICS.issubset(declared_metrics):
        log.error(f"Missing required metrics. Got: {declared_metrics}")
        return False
        
    # 6. Row counts mismatch check
    declared_rows = meta.get("row_count")
    actual_rows = len(data.get("rows", []))
    
    if declared_rows is None or declared_rows != actual_rows:
        log.error(f"Row count mismatch. Declared {declared_rows}, actual {actual_rows}")
        return False
        
    # 7. Semantic Check: 0 rows is acceptable ONLY IF explicitly declared as such. 
    # API drops should usually cause exception at Http client layer, but if Google legally says "0 traffic today", we accept it iff it passes integrity.
    # However, if data is completely empty, it might be an anomaly. L7 accepts it structurally, Report Plane (L6) might skip processing.
    
    return True

def enforce_retention_policy(snapshots_dir: Path, max_snapshots: int = 30) -> List[Path]:
    """
    Rotates raw GSC JSON dumps, keeping only the most recent `max_snapshots`.
    Returns a list of deleted paths.
    File format expected: collect_YYYYMMDD*.json
    """
    if not snapshots_dir.exists():
        return []
        
    files = list(snapshots_dir.glob("collect_*.json"))
    # Sort by name, which typically includes the timestamp collect_20260308T...
    # The newest files will be at the end of the list.
    files.sort(key=lambda p: p.name)
    
    deleted = []
    if len(files) > max_snapshots:
        files_to_delete = files[:-max_snapshots]
        for f in files_to_delete:
            try:
                f.unlink()
                deleted.append(f)
            except OSError as e:
                log.error(f"Failed to delete stale snapshot {f}: {e}")
                
    if deleted:
        log.info(f"Retention policy applied. Deleted {len(deleted)} old snapshots.")
        
    return deleted
    
