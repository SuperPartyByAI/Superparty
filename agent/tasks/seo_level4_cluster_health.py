import json
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, List
from agent.tasks.seo_level4_clusters import get_cluster_for_query, is_money_cluster
from agent.tasks.seo_level4_registry import classify_url_vs_cluster, is_cannibalizing, get_owner_url

log = logging.getLogger(__name__)

REPORT_DIR = Path("reports/superparty")
REPORT_FILE = REPORT_DIR / "seo_cluster_health.json"

def normalize_page_url(raw_url: str) -> str:
    """Normalizează pagina din GSC: taie domeniul dacă există, asigură format cu /."""
    if not raw_url:
        return ""
    parsed = urlparse(raw_url)
    path = parsed.path
    if not path.startswith("/"):
        path = "/" + path
    return path.rstrip("/") or "/"

def generate_cluster_health(gsc_rows: List[Dict]) -> Dict:
    """
    Produce un raport pur consultativ (read-only) al riscurilor de canibalizare pe clustere.
    Asteapta randuri extrase din GSC/DB cu formatul: 
    {"query": "...", "page": "...", "impressions": 100, "clicks": 10}
    """
    health_data = {}
    
    for row in gsc_rows:
        query = row.get("query", "")
        raw_page = row.get("page", "")
        if not query or not raw_page:
            continue
            
        page = normalize_page_url(raw_page)
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
                "owner_present": False,
                "owner_impressions": 0,
                "owner_clicks": 0,
                "owner_share": 0.0,
                "supporter_count": 0,
                "forbidden_count": 0,
                "unknown_count": 0,
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
            if classification == "owner":
                c_data["owner_present"] = True
            elif classification == "supporter":
                c_data["supporter_count"] += 1
            elif classification == "forbidden":
                c_data["forbidden_count"] += 1
            else:
                c_data["unknown_count"] += 1
                
        c_data["urls"][page]["impressions"] += row.get("impressions", 0)
        c_data["urls"][page]["clicks"] += row.get("clicks", 0)
        
        if c_data["urls"][page]["classification"] == "owner":
            c_data["owner_impressions"] += row.get("impressions", 0)
            c_data["owner_clicks"] += row.get("clicks", 0)

    # Compile structured warnings arrays
    for cid, data in health_data.items():
        warnings = []
        for url, stats in data["urls"].items():
            if stats["is_cannibalizing"]:
                warnings.append({
                    "url": url,
                    "classification": stats["classification"],
                    "impressions": stats["impressions"],
                    "clicks": stats["clicks"],
                    "severity": "high" if stats["classification"] == "forbidden" else "medium"
                })
        data["cannibalization_warnings"] = sorted(warnings, key=lambda x: x["impressions"], reverse=True)

        # Compute owner_share: owner_impressions / total_impressions (0.0 if total = 0)
        total = data.get("total_impressions", 0)
        data["owner_share"] = round(data["owner_impressions"] / total, 4) if total > 0 else 0.0
        
    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0",
            "input_rows": len(gsc_rows),
            "clusters_count": len(health_data)
        },
        "clusters": health_data
    }

def save_cluster_health_report(health_data: Dict) -> None:
    """Salvează raportul generat JSON in disk pentru ops.superparty.ro/dashboard."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        REPORT_FILE.write_text(json.dumps(health_data, indent=4), encoding="utf-8")
        log.info(f"Level 4 Advisory Report saved proactively to {REPORT_FILE}")
    except Exception as e:
        log.error(f"Failed to save cluster health report: {e}")
