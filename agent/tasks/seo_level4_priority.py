import json
import os
from datetime import datetime, timezone
from pathlib import Path

def load_priority_weights():
    config_path = Path(__file__).parent.parent.parent / "config" / "seo" / "business_priority_weights.json"
    if not config_path.exists():
        return None
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_registry_policies():
    """Returns a map of cluster_id -> full policy details based on the real registry."""
    registry_path = Path(__file__).parent.parent.parent / "config" / "seo" / "query_ownership_registry.json"
    if not registry_path.exists():
        return {}
    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data.get("registry", {})

def calculate_cluster_priority(cluster_id, cluster_data, weights, registry_map):
    if not weights:
        return None

    # Retrieve explicit policy for this cluster (or fallback)
    policy = registry_map.get(cluster_id, {})
    
    tier = policy.get("risk_tier", "C")
    biz_priority = policy.get("business_priority", "low")
    
    # --- 1. IMPORTANCE SCORE ---
    imp_cfg = weights.get("importance", {})
    tier_pts = imp_cfg.get("tier_points", {}).get(tier, 10)
    biz_pts = imp_cfg.get("business_priority_points", {}).get(biz_priority, 0)
    money_bonus = imp_cfg.get("is_money_cluster_bonus", 0) if cluster_data.get("is_money_cluster", False) else 0
    
    vol_pts = 0
    impressions = cluster_data.get("total_impressions", 0)
    v_cfg = imp_cfg.get("volume_thresholds", {})
    if impressions >= v_cfg.get("high", 1000):
        vol_pts = v_cfg.get("high_bonus", 20)
    elif impressions >= v_cfg.get("medium", 100):
        vol_pts = v_cfg.get("medium_bonus", 5)
        
    importance_score = tier_pts + biz_pts + money_bonus + vol_pts

    # --- 2. RISK SCORE (Multiplier) ---
    risk_cfg = weights.get("risk", {})
    risk_score = risk_cfg.get("base_risk", 1.0)
    owner_missing_mult = 1.0
    forbidden_penalty = 0.0
    unknown_penalty = 0.0
    
    if not cluster_data.get("owner_present", True):
        owner_missing_mult = risk_cfg.get("owner_missing_multiplier", 2.0)
        risk_score *= owner_missing_mult
        
    # Conflicts penalty summation based on warnings array
    high_count = 0
    med_count = 0
    warnings = cluster_data.get("cannibalization_warnings", [])
    for w in warnings:
        if w.get("severity") == "high" or w.get("classification") == "forbidden":
            high_count += 1
        elif w.get("severity") == "medium" or w.get("classification") == "unknown":
            med_count += 1

    if high_count > 0:
        forbidden_penalty = high_count * risk_cfg.get("conflict_multipliers", {}).get("high_severity", 0.5)
        risk_score += forbidden_penalty
    if med_count > 0:
        unknown_penalty = med_count * risk_cfg.get("conflict_multipliers", {}).get("medium_severity", 0.2)
        risk_score += unknown_penalty
        
    # --- 3. FINAL PRIORITY SCORE ---
    priority_score = int(importance_score * risk_score)
    
    # --- 4. PRIORITY BAND ---
    bands = weights.get("priority_bands", {})
    band = "low"
    if priority_score >= bands.get("critical", 300):
        band = "critical"
    elif priority_score >= bands.get("high", 150):
        band = "high"
    elif priority_score >= bands.get("medium", 50):
        band = "medium"
        
    # --- 5. RECOMMENDED ACTION ---
    action = "monitor_only"

    if risk_score > 1.0:
        if high_count > 0 and tier == "A":
            action = "escalate_tier_a_conflict"
        elif not cluster_data.get("owner_present", True) and cluster_data.get("is_money_cluster", False):
            action = "investigate_owner_drift"
        elif high_count > 0:
            action = "review_internal_linking_and_content"
        elif med_count > 0 and tier in ["A", "B"]:
            action = "review_registry_mapping"
        else:
            action = "defer_to_weekly_review"
    else:
        # Risk == 1.0 -> Heathy Cluster
        action = "monitor_only"
        
    # --- 6. EXPLANATION BLOCK ---
    explanation = {
        "tier_points": tier_pts,
        "business_priority_points": biz_pts,
        "money_bonus": money_bonus,
        "volume_bonus": vol_pts,
        "base_importance": importance_score,
        "owner_missing_multiplier": owner_missing_mult,
        "forbidden_penalty_added": forbidden_penalty,
        "unknown_penalty_added": unknown_penalty,
        "total_risk_multiplier": round(risk_score, 2)
    }

    return {
        "cluster_id": cluster_id,
        "tier": tier,
        "importance_score": importance_score,
        "risk_score": round(risk_score, 2),
        "priority_score": priority_score,
        "priority_band": band,
        "recommended_action": action,
        "business_priority_source": biz_priority,
        "explanation": explanation
    }

def run_business_priority_scoring(out_path: Path = None):
    reports_dir = Path(__file__).parent.parent.parent / "reports" / "superparty"
    health_path = reports_dir / "seo_cluster_health.json"
    priority_path = out_path if out_path else reports_dir / "seo_cluster_priority.json"
    
    if not health_path.exists():
        print("No cluster_health report found to score.")
        return False
        
    with open(health_path, "r", encoding="utf-8") as f:
        health_report = json.load(f)
        
    weights = load_priority_weights()
    registry_map = load_registry_policies()
    
    clusters = health_report.get("clusters", {})
    priority_clusters = {}
    
    for cluster_id, c_data in clusters.items():
        scored_data = calculate_cluster_priority(cluster_id, c_data, weights, registry_map)
        if scored_data:
            # Reconstruct the object safely for the new report
            # We copy all base observability metrics, then append the intelligence block
            enriched = dict(c_data)
            enriched["intelligence"] = scored_data
            priority_clusters[cluster_id] = enriched
            
    priority_report = {
        "metadata": {
            "schema_version": "2.0",
            "source_report_generated_at": health_report.get("metadata", {}).get("generated_at", ""),
            "priority_generated_at": datetime.now(timezone.utc).isoformat(),
            "clusters_scored": len(priority_clusters)
        },
        "clusters": priority_clusters
    }
    
    with open(priority_path, "w", encoding="utf-8") as f:
        json.dump(priority_report, f, indent=2, ensure_ascii=False)
        
    return True

if __name__ == "__main__":
    success = run_business_priority_scoring()
    print(f"Business Priority Scoring (Full Enterprise) ran successfully: {success}")
