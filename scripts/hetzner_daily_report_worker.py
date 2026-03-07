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
from agent.tasks.seo_level6_report_readiness import assert_inputs_ready

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("hetzner_worker")

REPORTS_DIR = Path("reports/superparty")
TMP_DIR = REPORTS_DIR / ".tmp_runs"

def validate_tmp_file(tmp_path: Path, required_root_keys: list) -> bool:
    try:
        data = json.loads(tmp_path.read_text(encoding="utf-8"))
        for k in required_root_keys:
            if k not in data:
                log.error(f"Validation failed for {tmp_path.name}: missing key '{k}'")
                return False
        if "metadata" not in data or "generated_at" not in data["metadata"]:
            log.error(f"Validation failed for {tmp_path.name}: missing 'generated_at' in metadata")
            return False
        return True
    except Exception as e:
        log.error(f"Validation failed for {tmp_path.name}: {e}")
        return False

def atomic_deploy(tmp_path: Path, final_path: Path, required_root_keys: list) -> bool:
    if not tmp_path.exists():
        log.error(f"Temp file {tmp_path} not found.")
        return False
    if not validate_tmp_file(tmp_path, required_root_keys):
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
        
        if res and atomic_deploy(tmp_health, final_health, ["clusters"]):
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
            
            if res and atomic_deploy(tmp_pri, final_pri, ["clusters"]):
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
        
        if res and atomic_deploy(tmp_trend, final_trend, ["clusters"]):
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
        
    print(f"\nReport Pipeline Complete: {status['overall_status'].upper()}")
    print(f"- Health:   {status['health']}")
    print(f"- Priority: {status['priority']}")
    print(f"- Trend:    {status['trend']}\n")
    
    return status

if __name__ == "__main__":
    run_all_reports()
