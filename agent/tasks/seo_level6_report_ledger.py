import json
import logging
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone

log = logging.getLogger("seo_ledger")

LEDGER_FILE = Path("reports/superparty/seo_reports_ledger.json")
MAX_LEDGER_ENTRIES = 30

def append_to_ledger(worker_status: dict, ledger_path: Path = None, max_entries: int = MAX_LEDGER_ENTRIES) -> bool:
    """
    Appends the daily worker status to the ledger, keeping a maximum of 30 days of history.
    """
    target_file = ledger_path if ledger_path else LEDGER_FILE
    
    # Read existing ledger
    ledger_data = []
    if target_file.exists():
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    ledger_data = json.loads(content)
        except Exception as e:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            backup_file = target_file.with_name(f"{target_file.name}.corrupt.{ts}.bak")
            log.error(f"Could not read existing ledger to append: {e}. Backing up corrupt ledger to {backup_file.name}")
            try:
                target_file.rename(backup_file)
            except Exception as move_e:
                log.error(f"Failed to backup corrupt ledger: {move_e}")
                return False
            ledger_data = []
    # Create the new entry based on the worker status
    new_entry = {
        "run_id": str(uuid.uuid4()),
        "timestamp": worker_status.get("run_at", datetime.now(timezone.utc).isoformat()),
        "status": worker_status.get("overall_status", "failed"),
        "failing_stage": None,
        "health_status": worker_status.get("health", "skipped"),
        "priority_status": worker_status.get("priority", "skipped"),
        "trend_status": worker_status.get("trend", "skipped")
    }
    
    # Determine failing stage if any
    if new_entry["health_status"] == "failed":
        new_entry["failing_stage"] = "health"
    elif new_entry["priority_status"] == "failed":
        new_entry["failing_stage"] = "priority"
    elif new_entry["trend_status"] == "failed":
        new_entry["failing_stage"] = "trend"
        
    ledger_data.append(new_entry)
    
    # Sort by timestamp (newest last) and truncate
    ledger_data = sorted(ledger_data, key=lambda x: x["timestamp"])
    if len(ledger_data) > max_entries:
        ledger_data = ledger_data[-max_entries:]
        
    # Write back
    target_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(ledger_data, f, indent=2)
            
        log.info(f"Appended run {new_entry['run_id']} to ledger {target_file.name}. Total entries: {len(ledger_data)}")
        return True
    except Exception as e:
        log.error(f"Failed to write ledger append: {e}")
        return False

def print_ledger_summary(ledger_path: Path = None) -> None:
    """
    CLI command to read the ledger and print the status of the latest run in a human-readable format.
    """
    target_file = ledger_path if ledger_path else LEDGER_FILE
    
    if not target_file.exists():
        print("ERROR: Ledger file does not exist. No reports have run yet.")
        return
        
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            ledger_data = json.load(f)
            
        if not ledger_data:
            print("ERROR: Ledger is empty.")
            return
            
        latest = sorted(ledger_data, key=lambda x: x["timestamp"])[-1]
        
        # [2026-03-08 03:00:00] Status: SUCCESS | Health: Fresh | Priorities: Fresh | Trends: Fresh
        ts_pretty = latest["timestamp"].split(".")[0].replace("T", " ")
        if latest["timestamp"].endswith("Z"):
            ts_pretty = latest["timestamp"].replace("Z", "").replace("T", " ")

        status = latest["status"].upper()
        
        def to_human(state):
            return "Fresh" if state == "success" else ("Failed" if state == "failed" else "Skipped")
            
        h_str = to_human(latest["health_status"])
        p_str = to_human(latest["priority_status"])
        t_str = to_human(latest["trend_status"])
        
        print(f"[{ts_pretty}] Status: {status} | Health: {h_str} | Priorities: {p_str} | Trends: {t_str}")
        
    except Exception as e:
        print(f"ERROR reading ledger: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        print_ledger_summary()
    else:
        print("Usage: python seo_level6_report_ledger.py --summary")
