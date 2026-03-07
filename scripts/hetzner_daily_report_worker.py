#!/usr/bin/env python3
import sys
import shutil
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is in path if run outside module
sys.path.append(str(Path(__file__).parent.parent))

from agent.tasks.seo_level4_cluster_health import run_cluster_health
from agent.tasks.seo_level4_priority import run_business_priority_scoring
from agent.tasks.seo_trend_analyzer import run_trend_analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("hetzner_worker")

REPORTS_DIR = Path("reports/superparty")
TMP_DIR = REPORTS_DIR / ".tmp_runs"

def validate_tmp_file(tmp_path: Path, expected_schema_version: str, expected_root_keys: list, timestamp_key: str = "generated_at") -> bool:
    """
    Validare asertivă strictă pe contractul real produs de engine-urile L4.
    Refuză mutarea atomică la cea mai mică eroare de structură sau dacă versiunea 
    de schemă a producerului a denaturat.
    """
    try:
        data = json.loads(tmp_path.read_text(encoding="utf-8"))
        for k in expected_root_keys:
            if k not in data:
                log.error(f"Validation failed for {tmp_path.name}: missing key '{k}'")
                return False
                
        if "metadata" not in data:
            log.error(f"Validation failed for {tmp_path.name}: missing 'metadata'")
            return False
            
        real_schema = data["metadata"].get("schema_version")
        if real_schema != expected_schema_version:
             log.error(f"Validation failed for {tmp_path.name}: schema_version mismatch. Expected {expected_schema_version}, got {real_schema}")
             return False
             
        # Fallback tolerant for priority which might have generated_at or priority_generated_at
        if timestamp_key not in data["metadata"] and "generated_at" not in data["metadata"]:
             log.error(f"Validation failed for {tmp_path.name}: missing timestamp '{timestamp_key}'")
             return False
             
        return True
    except Exception as e:
        log.error(f"Validation failed for {tmp_path.name}: {e}")
        return False

def atomic_deploy(tmp_path: Path, final_path: Path, expected_schema_version: str, expected_root_keys: list, timestamp_key: str = "generated_at") -> bool:
    if not tmp_path.exists():
        log.error(f"Temp file {tmp_path} not found.")
        return False
        
    if not validate_tmp_file(tmp_path, expected_schema_version, expected_root_keys, timestamp_key):
        return False
    
    # Atomic replace
    final_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp_path), str(final_path))
    log.info(f"Deployed {final_path.name} atomically.")
    return True

def run_all_reports():
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    
    status = {
        "health": "skipped",
        "priority": "skipped",
        "trend": "skipped",
        "overall_status": "failed"
    }

    # 1. Health
    try:
        tmp_health = TMP_DIR / "seo_cluster_health.json"
        final_health = REPORTS_DIR / "seo_cluster_health.json"
        log.info("Starting Health Report Engine...")
        res = run_cluster_health(out_path=tmp_health)
        
        if res and atomic_deploy(tmp_health, final_health, "1.0", ["metadata", "clusters"]):
            status["health"] = "success"
        else:
            status["health"] = "failed"
            log.error("Health report failed, preserving old file.")
    except Exception as e:
        log.error(f"Fatal error in health engine: {e}")
        traceback.print_exc()
        status["health"] = "failed"

    # 2. Priority
    if status["health"] == "success": # Requires fresh health
        try:
            tmp_pri = TMP_DIR / "seo_cluster_priority.json"
            final_pri = REPORTS_DIR / "seo_cluster_priority.json"
            log.info("Starting Priority Report Engine...")
            res = run_business_priority_scoring(out_path=tmp_pri)
            
            # Priorty validat pe schema_version "2.0", root "clusters", field datetime "priority_generated_at"
            if res and atomic_deploy(tmp_pri, final_pri, "2.0", ["metadata", "clusters"], "priority_generated_at"):
                status["priority"] = "success"
            else:
                status["priority"] = "failed"
        except Exception as e:
            log.error(f"Fatal error in priority engine: {e}")
            traceback.print_exc()
            status["priority"] = "failed"
    else:
        log.warning("Skipping Priority Engine because Health failed.")

    # 3. Trends (can run even if priority fails, relying on previous cache if needed, but optimally needs priority)
    try:
        tmp_trend = TMP_DIR / "seo_trend_delta.json"
        final_trend = REPORTS_DIR / "seo_trend_delta.json"
        log.info("Starting Trend Analyzer Engine...")
        res = run_trend_analysis(out_path=tmp_trend)
        
        # Trends validat pe schema_version "1.1", root "clusters"
        if res and atomic_deploy(tmp_trend, final_trend, "1.1", ["metadata", "clusters"]):
            status["trend"] = "success"
        else:
            status["trend"] = "failed"
    except Exception as e:
        log.error(f"Fatal error in trend engine: {e}")
        traceback.print_exc()
        status["trend"] = "failed"

    # Overall Resolution
    if status["health"] == "success" and status["priority"] == "success" and status["trend"] == "success":
        status["overall_status"] = "success"
    elif status["health"] == "success":
        status["overall_status"] = "partial_failure"
    else:
        status["overall_status"] = "failed"
        
    status["run_at"] = datetime.now(timezone.utc).isoformat()
        
    print(f"\nReport Pipeline Complete: {status['overall_status'].upper()}")
    print(f"- Health:   {status['health']}")
    print(f"- Priority: {status['priority']}")
    print(f"- Trend:    {status['trend']}\n")
    
    status_file = REPORTS_DIR / "seo_report_worker_status.json"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)
    
    return status

if __name__ == "__main__":
    run_all_reports()
