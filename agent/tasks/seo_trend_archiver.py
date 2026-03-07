"""
SEO Trend Archiver — Level 4.1 PR #51
Read-only. Copies current Level 4 reports to a dated history folder.
One snapshot per day; re-runs on the same day overwrite the previous snapshot.
"""
import json
import shutil
import logging
from datetime import datetime, timezone, date
from pathlib import Path

log = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports" / "superparty"
HISTORY_DIR = REPORTS_DIR / "history"

SOURCE_FILES = [
    "seo_cluster_health.json",
    "seo_cluster_priority.json",
    "seo_gap_opportunities.json",
]


def archive_snapshots(snapshot_date: str = None) -> dict:
    """
    Copies current Level 4 report files to history/YYYY-MM-DD/.
    Returns a manifest dict with metadata about what was archived.

    Args:
        snapshot_date: Override date string (YYYY-MM-DD). Defaults to today UTC.

    Returns:
        dict with 'archived', 'missing', 'snapshot_date', 'archived_at'.
    """
    today = snapshot_date or date.today().isoformat()
    dest_dir = HISTORY_DIR / today
    dest_dir.mkdir(parents=True, exist_ok=True)

    archived = []
    missing = []

    for fname in SOURCE_FILES:
        src = REPORTS_DIR / fname
        if not src.exists():
            log.warning(f"Source missing, skipping: {src}")
            missing.append(fname)
            continue

        dest = dest_dir / fname
        shutil.copy2(str(src), str(dest))

        # Read generated_at from source metadata if present
        source_generated_at = ""
        try:
            with open(src, "r", encoding="utf-8") as f:
                data = json.load(f)
            source_generated_at = (
                data.get("metadata", {}).get("generated_at")
                or data.get("metadata", {}).get("priority_generated_at")
                or data.get("metadata", {}).get("gap_detected_at")
                or ""
            )
        except Exception:
            pass

        archived.append({
            "file": fname,
            "source_generated_at": source_generated_at
        })
        log.info(f"Archived {fname} → {dest}")

    manifest = {
        "snapshot_date": today,
        "archived_at": datetime.now(timezone.utc).isoformat(),
        "mode": "read_only",
        "archived": archived,
        "missing": missing,
    }

    manifest_path = dest_dir / "snapshot_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    log.info(f"Snapshot manifest written → {manifest_path}")
    return manifest


def get_latest_snapshot_dates() -> list:
    """
    Returns sorted list of snapshot date strings found in history dir.
    Most recent last.
    """
    if not HISTORY_DIR.exists():
        return []
    dates = sorted([
        d.name for d in HISTORY_DIR.iterdir()
        if d.is_dir() and len(d.name) == 10 and d.name[4] == "-"
    ])
    return dates


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = archive_snapshots()
    print(f"Archived {len(result['archived'])} files, {len(result['missing'])} missing.")
    print(f"Snapshot date: {result['snapshot_date']}")
