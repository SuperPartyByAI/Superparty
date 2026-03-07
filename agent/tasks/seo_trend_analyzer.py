"""
SEO Trend Analyzer — Level 4.1 PR #51
Read-only. Compares current Level 4 reports with the previous snapshot
and produces seo_trend_delta.json — the machine-readable temporal intelligence
contract for AI consumption.

Inputs (from reports/superparty/):
  - seo_cluster_health.json      (owner_share, forbidden_count)
  - seo_cluster_priority.json    (priority_band)
  - seo_gap_opportunities.json   (optional, for future extension)

Output:
  - reports/superparty/seo_trend_delta.json
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports" / "superparty"
HISTORY_DIR = REPORTS_DIR / "history"
DELTA_FILE = REPORTS_DIR / "seo_trend_delta.json"


# ─── Loaders ───────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.warning(f"Could not load {path}: {e}")
        return None


def load_current_reports() -> dict:
    """Load current health + priority reports."""
    return {
        "health": _load_json(REPORTS_DIR / "seo_cluster_health.json"),
        "priority": _load_json(REPORTS_DIR / "seo_cluster_priority.json"),
    }


def load_previous_snapshot(snapshot_date: str) -> dict:
    """Load health + priority from a specific history snapshot date (YYYY-MM-DD)."""
    snap_dir = HISTORY_DIR / snapshot_date
    return {
        "health": _load_json(snap_dir / "seo_cluster_health.json"),
        "priority": _load_json(snap_dir / "seo_cluster_priority.json"),
        "date": snapshot_date,
    }


def get_previous_snapshot_date(exclude_today: str = None) -> Optional[str]:
    """Return the most recent snapshot date, optionally excluding today."""
    if not HISTORY_DIR.exists():
        return None
    dates = sorted([
        d.name for d in HISTORY_DIR.iterdir()
        if d.is_dir() and len(d.name) == 10 and d.name[4] == "-"
    ])
    if exclude_today:
        dates = [d for d in dates if d != exclude_today]
    return dates[-1] if dates else None


# ─── State Normalization ────────────────────────────────────────────────────────

def normalize_cluster_state(health_data: dict, priority_data: dict) -> dict:
    """
    Builds a normalized per-cluster state dict for delta computation.
    Machine-readable contract: cluster_id -> {priority_band, forbidden_count, owner_share}
    """
    states = {}

    health_clusters = (health_data or {}).get("clusters", {})
    priority_clusters = (priority_data or {}).get("clusters", {})

    all_ids = set(health_clusters.keys()) | set(priority_clusters.keys())

    for cid in all_ids:
        h = health_clusters.get(cid, {})
        p = priority_clusters.get(cid, {})
        intel = p.get("intelligence", {})

        # owner_share: keep None if absent from health report (pre-PR50 snapshots).
        # Do NOT fall back to 0.0 — 0.0 means "real zero share", not "unknown".
        # delta_owner_share will be None if either side is None, preventing false signals.
        raw_owner_share = h.get("owner_share", None)
        owner_share = round(float(raw_owner_share), 4) if raw_owner_share is not None else None

        states[cid] = {
            "priority_band": intel.get("priority_band", p.get("priority_band", "")),
            "forbidden_count": h.get("forbidden_count", 0),
            "owner_share": owner_share,
        }

    return states


# ─── Delta Engine ───────────────────────────────────────────────────────────────

def _compute_status(delta_owner_share, delta_forbidden: int) -> str:
    """
    Status: improved / regressed / stable / mixed.
    delta_owner_share may be None (pre-PR50 snapshot without owner_share).
    None = unknown data — excluded from signals to avoid false improved/regressed.
    Only criteria with valid (non-None) values are evaluated.
    """
    improved_signals = []
    regressed_signals = []

    if delta_owner_share is not None:
        if delta_owner_share > 0:
            improved_signals.append(True)
        elif delta_owner_share < 0:
            regressed_signals.append(True)

    if delta_forbidden < 0:
        improved_signals.append(True)
    elif delta_forbidden > 0:
        regressed_signals.append(True)

    if improved_signals and not regressed_signals:
        return "improved"
    if regressed_signals and not improved_signals:
        return "regressed"
    if improved_signals and regressed_signals:
        return "mixed"
    return "stable"


def compute_deltas(current_states: dict, previous_states: dict) -> list:
    """
    Computes per-cluster deltas between current and previous states.
    Handles: new clusters, disappeared clusters, stable/improved/regressed.
    """
    all_ids = set(current_states.keys()) | set(previous_states.keys())
    deltas = []

    for cid in sorted(all_ids):
        curr = current_states.get(cid)
        prev = previous_states.get(cid)

        if curr is None:
            # Cluster disappeared
            deltas.append({
                "cluster_id": cid,
                "status": "missing",
                "delta_priority_band": f"{prev['priority_band']}->N/A",
                "delta_forbidden": None,
                "delta_owner_share": None,
                "current": None,
                "previous": prev,
            })
            continue

        if prev is None:
            # New cluster (no previous snapshot)
            deltas.append({
                "cluster_id": cid,
                "status": "new",
                "delta_priority_band": f"N/A->{curr['priority_band']}",
                "delta_forbidden": None,
                "delta_owner_share": None,
                "current": curr,
                "previous": None,
            })
            continue

        # Both present — compute real deltas
        d_forbidden = curr["forbidden_count"] - prev["forbidden_count"]

        # delta_owner_share is None if either side is None (schema mismatch pre-PR50).
        # This prevents false improved/regressed from a schema change, not from SEO reality.
        curr_share = curr["owner_share"]
        prev_share = prev["owner_share"]
        if curr_share is not None and prev_share is not None:
            d_owner_share = round(curr_share - prev_share, 4)
        else:
            d_owner_share = None

        # delta_priority_band: always X->Y format for uniform contract (even if stable: A->A)
        band_transition = f"{prev['priority_band']}->{curr['priority_band']}"

        deltas.append({
            "cluster_id": cid,
            "status": _compute_status(d_owner_share, d_forbidden),
            "delta_priority_band": band_transition,
            "delta_forbidden": d_forbidden,
            "delta_owner_share": d_owner_share,
            "current": curr,
            "previous": prev,
        })

    return deltas


# ─── Runner ────────────────────────────────────────────────────────────────────

def run_trend_analysis(current_date: str = None, out_path: Path = None) -> bool:
    """
    Main entry point. Loads current + previous snapshots, computes deltas,
    writes seo_trend_delta.json. Returns True on success.

    If no previous snapshot exists: writes baseline_only=True output with empty clusters.
    """
    from datetime import date as date_cls
    today = current_date or date_cls.today().isoformat()

    current = load_current_reports()
    if not current["health"] and not current["priority"]:
        log.error("No current reports found. Run health + priority engines first.")
        return False

    prev_date = get_previous_snapshot_date(exclude_today=today)
    baseline_only = prev_date is None

    current_states = normalize_cluster_state(current["health"], current["priority"])

    if baseline_only:
        log.info("No previous snapshot found. Writing baseline_only output.")
        deltas = []
        previous_date_str = None
    else:
        prev_snap = load_previous_snapshot(prev_date)
        previous_states = normalize_cluster_state(prev_snap["health"], prev_snap["priority"])
        deltas = compute_deltas(current_states, previous_states)
        previous_date_str = prev_date

    output = {
        "metadata": {
            "schema_version": "1.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "current_snapshot_date": today,
            "previous_snapshot_date": previous_date_str,
            "baseline_only": baseline_only,
            "mode": "read_only",
            "clusters_analyzed": len(current_states),
        },
        "clusters": deltas,
    }

    target_file = out_path if out_path else DELTA_FILE
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    log.info(f"Trend delta written → {target_file}")
    print(f"Trend analysis complete: {len(deltas)} clusters, baseline_only={baseline_only}")
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_trend_analysis()
