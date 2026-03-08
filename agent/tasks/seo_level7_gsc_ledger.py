import json
import logging
import uuid
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

log = logging.getLogger("gsc_ledger")

LEDGER_PATH = Path("reports/superparty/gsc_collection_ledger.json")
MAX_LEDGER_ENTRIES = 30
PROPERTY_URI = "sc-domain:superparty.ro"

def initialize_ledger_file(path: Path = LEDGER_PATH):
    """Ensures the ledger directory and file exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        _atomic_write_ledger(path, [])

def read_ledger(path: Path = LEDGER_PATH) -> List[Dict[str, Any]]:
    """Reads the current ledger as a list of dictionaries."""
    initialize_ledger_file(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        log.warning(f"Ledger file corrupted or unreadable. Initializing a new one. Backup created. Error: {e}")
        if path.exists():
            backup_path = path.with_suffix(".json.bak")
            try:
                shutil.copy(path, backup_path)
            except OSError:
                pass
        return []

def _atomic_write_ledger(path: Path, entries: List[Dict[str, Any]]):
    """Atomically writes the ledger array to disk."""
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
        shutil.move(tmp_path, path)
    except Exception as e:
        log.error(f"Failed to atomically write ledger to {path}: {e}")
        if Path(tmp_path).exists():
            Path(tmp_path).unlink()
        raise

import os

def append_to_ledger(
    status: str, 
    failing_stage: str = None, 
    error_reason: str = None, 
    row_count: int = None, 
    snapshot_filename: str = None,
    path: Path = LEDGER_PATH
):
    """
    Appends a new status entry to the source acquisition ledger.
    """
    entries = read_ledger(path)
    
    entry = {
        "run_id": str(uuid.uuid4()),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "property": PROPERTY_URI
    }
    
    if failing_stage:
        entry["failing_stage"] = failing_stage
    if error_reason:
        entry["error_reason"] = error_reason
    if row_count is not None:
        entry["row_count"] = row_count
    if snapshot_filename:
        entry["snapshot_filename"] = snapshot_filename
        
    entries.append(entry)
    
    # Rotate
    if len(entries) > MAX_LEDGER_ENTRIES:
        entries = entries[-MAX_LEDGER_ENTRIES:]
        
    _atomic_write_ledger(path, entries)
    return entry

def summarize_ledger(path: Path = LEDGER_PATH):
    """CLI utility function to print a summary of the source acquisition ledger."""
    entries = read_ledger(path)
    if not entries:
        print("GSC Collection Ledger is empty.")
        return
        
    print(f"--- GSC Collection Ledger Summary (Max {MAX_LEDGER_ENTRIES}) ---")
    for entry in reversed(entries[-5:]):  # Show last 5
        date_str = entry['collected_at'][:19].replace("T", " ")
        status = entry['status']
        row_count = entry.get('row_count', 'N/A')
        state_msg = f"ROWS: {row_count}" if status == "SUCCESS" else f"FAIL: {entry.get('failing_stage')} - {entry.get('error_reason')}"
        print(f"[{date_str}] Status: {status.ljust(10)} | {state_msg}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GSC Source Acquisition Ledger Utility")
    parser.add_argument("--summary", action="store_true", help="Print recent GSC collection status.")
    args = parser.parse_args()
    
    if args.summary:
        summarize_ledger()
