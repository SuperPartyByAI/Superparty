import json
import logging
from pathlib import Path
from typing import Dict, List
from agent.tasks.seo_level4_clusters import get_cluster_for_query, is_money_cluster
from agent.tasks.seo_level4_registry import classify_url_vs_cluster, is_cannibalizing, get_owner_url

log = logging.getLogger(__name__)

REPORT_DIR = Path("reports/superparty")
REPORT_FILE = REPORT_DIR / "seo_cluster_health.json"

def generate_cluster_health(gsc_rows: List[Dict]) -> Dict:
    """
    Produce un raport pur consultativ (read-only) al riscurilor de canibalizare pe clustere.
    Asteapta randuri extrase din GSC/DB cu formatul: 
    {"query": "...", "page": "...", "impressions": 100, "clicks": 10}
    """
    health_data = {}
    
    for row in gsc_rows:
        query = row.get("query", "")
        page = row.get("page", "")
        if not query or not page:
            continue
            
        cluster = get_cluster_for_query(query)
        if not cluster:
            continue
            
        cluster_id = cluster["cluster_id"]
        if cluster_id not in health_data:
            health_data[cluster_id] = {
                "owner_url": get_owner_url(cluster_id),
                "is_money_cluster": is_money_cluster(cluster_id),
                "total_impressions": 0,
                "total_clicks": 0,
                "urls": {},
                "cannibalization_warnings": []
            }
            
        c_data = health_data[cluster_id]
        
        c_data["total_impressions"] += row.get("impressions", 0)
        c_data["total_clicks"] += row.get("clicks", 0)
        
        if page not in c_data["urls"]:
            # Evaluate Level 4 role
            classification = classify_url_vs_cluster(page, cluster_id)
            cannibalizing = is_cannibalizing(page, cluster_id)
            
            c_data["urls"][page] = {
                "classification": classification,
                "is_cannibalizing": cannibalizing,
                "impressions": 0,
                "clicks": 0
            }
            if cannibalizing:
                c_data["cannibalization_warnings"].append(page)
                
        c_data["urls"][page]["impressions"] += row.get("impressions", 0)
        c_data["urls"][page]["clicks"] += row.get("clicks", 0)

    # Deduplicate warning arrays if any overlap occurred
    for cid, data in health_data.items():
        data["cannibalization_warnings"] = list(set(data["cannibalization_warnings"]))
        
    return {"clusters": health_data}

def save_cluster_health_report(health_data: Dict) -> None:
    """Salvează raportul generat JSON in disk pentru ops.superparty.ro/dashboard."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        REPORT_FILE.write_text(json.dumps(health_data, indent=4), encoding="utf-8")
        log.info(f"Level 4 Advisory Report saved proactively to {REPORT_FILE}")
    except Exception as e:
        log.error(f"Failed to save cluster health report: {e}")
