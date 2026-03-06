"""
Level 4 Gap Detector — Read-Only Intelligence Module
Fase 14: Identifies coverage gaps, under-covered clusters, and expansion opportunities.

Output: reports/superparty/seo_gap_opportunities.json (SEPARATE from health and priority reports)
"""
import json
from datetime import datetime, timezone
from pathlib import Path

# ─── Loaders ───────────────────────────────────────────────────────────────────

def load_priority_report():
    """Load the scored cluster priority report (output of Phase 12)."""
    p = Path(__file__).parent.parent.parent / "reports" / "superparty" / "seo_cluster_priority.json"
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def load_registry():
    """Load the query ownership registry to understand intended cluster scope."""
    p = Path(__file__).parent.parent.parent / "config" / "seo" / "query_ownership_registry.json"
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f).get("registry", {})

def load_gap_thresholds():
    """Load gap detection thresholds from config if exists, else use defaults."""
    p = Path(__file__).parent.parent.parent / "config" / "seo" / "gap_detector_config.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    # Sensible defaults
    return {
        "min_impressions_for_coverage": 50,
        "weak_owner_threshold_impressions": 100,
        "max_allowed_unknown_ratio": 0.5,
        "expansion_allowed_tiers": ["B", "C"],
        "opportunity_types": {
            "missing_owner": "optimize_owner",
            "weak_owner": "optimize_owner",
            "high_unknown_ratio": "review_registry_mapping",
            "low_coverage": "add_support",
            "risky_expansion": "reject_risky_expansion",
            "healthy_expandable": "defer"
        }
    }

# ─── Core Analysis ─────────────────────────────────────────────────────────────

def analyze_cluster_gap(cluster_id, cluster_data, registry_policy, thresholds):
    """
    Analyzes a single cluster for coverage gaps.
    Returns a gap opportunity object or None if no gap is detected.
    """
    intel = cluster_data.get("intelligence", {})
    tier = intel.get("tier", "C")
    importance_score = intel.get("importance_score", 0)
    risk_score = intel.get("risk_score", 1.0)

    total_impressions = cluster_data.get("total_impressions", 0)
    owner_present = cluster_data.get("owner_present", True)
    forbidden_count = cluster_data.get("forbidden_count", 0)
    unknown_count = cluster_data.get("unknown_count", 0)
    supporter_count = cluster_data.get("supporter_count", 0)
    warnings = cluster_data.get("cannibalization_warnings", [])

    min_impressions = thresholds["min_impressions_for_coverage"]
    weak_threshold = thresholds["weak_owner_threshold_impressions"]
    max_unknown_ratio = thresholds["max_allowed_unknown_ratio"]
    opp_types = thresholds["opportunity_types"]

    gap_signals = []
    opportunity_type = None
    confidence = "low"

    # --- Signal 1: Missing Owner (no declared owner URL for a ranked cluster)
    if not owner_present:
        gap_signals.append("missing_owner")
        opportunity_type = opp_types["missing_owner"]
        confidence = "high" if tier in ["A", "B"] else "medium"

    # --- Signal 2: Weak Owner (owner present but very low impressions)
    elif total_impressions < weak_threshold and tier in ["A", "B"]:
        gap_signals.append("weak_owner")
        opportunity_type = opp_types["weak_owner"]
        confidence = "medium"

    # --- Signal 3: High Unknown Ratio (many unclassified competing URLs)
    total_urls = forbidden_count + unknown_count + supporter_count + (1 if owner_present else 0)
    unknown_ratio = unknown_count / total_urls if total_urls > 0 else 0
    if unknown_ratio > max_unknown_ratio:
        gap_signals.append("high_unknown_ratio")
        if not opportunity_type:
            opportunity_type = opp_types["high_unknown_ratio"]
        if confidence == "low":
            confidence = "medium"

    # --- Signal 4: Low Coverage (below minimum traffic threshold for ranked cluster)
    if total_impressions < min_impressions and not gap_signals:
        gap_signals.append("low_coverage")
        opportunity_type = opp_types["low_coverage"]
        confidence = "low"

    # --- Signal 5: Risky Expansion Guard (conservative policy check)
    expansion_policy = registry_policy.get("expansion_policy", "conservative")
    if expansion_policy == "conservative" and tier in ["A"] and not gap_signals:
        # Tier A + healthy = defer, do NOT recommend expansion
        gap_signals.append("risky_expansion")
        opportunity_type = opp_types["risky_expansion"]
        confidence = "high"

    # No meaningful gap detected
    if not gap_signals:
        return None

    return {
        "cluster_id": cluster_id,
        "tier": tier,
        "opportunity_type": opportunity_type,
        "confidence": confidence,
        "gap_signals": gap_signals,
        "context": {
            "total_impressions": total_impressions,
            "owner_present": owner_present,
            "supporter_count": supporter_count,
            "forbidden_count": forbidden_count,
            "unknown_count": unknown_count,
            "unknown_ratio": round(unknown_ratio, 2),
            "importance_score": importance_score,
            "risk_score": risk_score,
            "expansion_policy": expansion_policy
        },
        "suggested_action": _map_action_label(opportunity_type),
    }


def _map_action_label(opportunity_type):
    """Maps internal opportunity_type to a human-readable suggested action label."""
    labels = {
        "optimize_owner": "Optimize or assign a dedicated owner URL for this cluster",
        "add_support": "Add supporting content urls to improve cluster coverage",
        "review_registry_mapping": "Review and update ownership registry for unknown URLs",
        "reject_risky_expansion": "Do NOT expand — cluster is Tier A with conservative policy",
        "defer": "Cluster is healthy; no action needed now. Review in next cycle."
    }
    return labels.get(opportunity_type, "No specific action suggested.")


# ─── Runner ───────────────────────────────────────────────────────────────────

def run_gap_detection():
    """
    Main entry point for gap detection.
    Reads from priority report, emits gap opportunities to a separate output file.
    """
    priority_report = load_priority_report()
    if not priority_report:
        print("No priority report found. Run seo_level4_priority.py first.")
        return False

    registry = load_registry()
    thresholds = load_gap_thresholds()

    clusters = priority_report.get("clusters", {})
    gap_opportunities = []

    for cluster_id, cluster_data in clusters.items():
        policy = registry.get(cluster_id, {})
        gap = analyze_cluster_gap(cluster_id, cluster_data, policy, thresholds)
        if gap:
            gap_opportunities.append(gap)

    # Sort by confidence then tier
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    tier_order = {"A": 0, "B": 1, "C": 2}
    gap_opportunities.sort(key=lambda g: (
        confidence_order.get(g["confidence"], 9),
        tier_order.get(g["tier"], 9)
    ))

    output = {
        "metadata": {
            "schema_version": "1.0",
            "source_priority_report_at": priority_report.get("metadata", {}).get("priority_generated_at", ""),
            "gap_detected_at": datetime.now(timezone.utc).isoformat(),
            "total_clusters_analyzed": len(clusters),
            "gaps_found": len(gap_opportunities),
            "mode": "read_only"
        },
        "opportunities": gap_opportunities
    }

    out_path = Path(__file__).parent.parent.parent / "reports" / "superparty" / "seo_gap_opportunities.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Gap Detector complete: {len(gap_opportunities)} gaps found across {len(clusters)} clusters.")
    return True


if __name__ == "__main__":
    run_gap_detection()
