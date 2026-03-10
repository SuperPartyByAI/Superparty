"""
core/run2_planner.py — Run 2 Candidate Planner (adapter-aware)

Versiunea platformizată a seo_level6_run2_planner.py.
Funcționează cu orice SiteAdapter.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.site_adapter import SiteAdapter


def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _get_active_urls(outcome_memory_path: Path) -> set:
    experiments = _load_json(outcome_memory_path) or []
    return {e["url"].rstrip("/") for e in experiments if e.get("result_label") == "pending"}


def _get_rollback_urls(outcome_memory_path: Path) -> set:
    experiments = _load_json(outcome_memory_path) or []
    return {e["url"].rstrip("/") for e in experiments if e.get("rollback_happened")}


def _get_cooldown_urls(outcome_memory_path: Path, min_reapply_days: int, now: datetime) -> set:
    experiments = _load_json(outcome_memory_path) or []
    active = set()
    for exp in experiments:
        if exp.get("result_label") != "pending":
            continue
        applied_at = exp.get("applied_at", "")
        if not applied_at:
            continue
        dt = datetime.fromisoformat(applied_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if (now - dt).total_seconds() / 86400 < min_reapply_days:
            active.add(exp["url"].rstrip("/"))
    return active


def _earliest_run_date(url: str, outcome_memory_path: Path, min_reapply_days: int, now: datetime) -> str:
    experiments = _load_json(outcome_memory_path) or []
    active = [e for e in experiments if e.get("url") == url and e.get("result_label") == "pending"]
    if not active:
        return now.date().isoformat()

    latest_apply = max(e.get("applied_at", "") for e in active)
    dt = datetime.fromisoformat(latest_apply)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    cooldown_lifted = dt + timedelta(days=min_reapply_days)

    deadlines = []
    for e in active:
        d = e.get("observation_deadline")
        if d:
            dd = datetime.fromisoformat(d)
            if dd.tzinfo is None:
                dd = dd.replace(tzinfo=timezone.utc)
            deadlines.append(dd)

    if deadlines:
        earliest = max(cooldown_lifted, max(deadlines))
    else:
        earliest = cooldown_lifted

    return earliest.date().isoformat()


def generate_run2_candidates(
    adapter: "SiteAdapter",
    output_path: Optional[Path] = None,
    max_candidates: int = 3,
    now: Optional[datetime] = None,
) -> dict:
    """
    Generează shortlist Run 2 candidates pentru un site.

    Args:
      adapter: SiteAdapter — configurația și regulile site-ului
      output_path: unde salvăm shortlist-ul (optional)
      max_candidates: câți candidați top vrei
      now: datetime UTC (pentru testare)
    """
    if now is None:
        now = datetime.now(timezone.utc)

    memory_path = adapter.reports_dir / "seo_level6_outcome_memory.json"
    active_urls = _get_active_urls(memory_path)
    rollback_urls = _get_rollback_urls(memory_path)
    cooldown_urls = _get_cooldown_urls(memory_path, adapter.min_reapply_days, now)

    quality_order = {"good": 0, "limited": 1, "insufficient": 2}
    candidates = []
    excluded = []

    for item in adapter.get_tier_c_catalog():
        url = item["url"].rstrip("/")
        blockers = []

        if adapter.is_pillar_page(url):
            blockers.append("pillar_page_blocked")
        if adapter.is_money_page(url):
            blockers.append("money_page_blocked")
        if url in rollback_urls:
            blockers.append("rollback_recent")
        if url in active_urls:
            blockers.append("active_experiment_in_progress")
        if url in cooldown_urls:
            blockers.append("cooldown_active")

        gsc = item.get("gsc_data") or {}
        impressions = gsc.get("impressions")
        if impressions is not None and impressions >= adapter.min_impressions_for_scoring:
            data_quality = "good"
        elif impressions is not None:
            data_quality = "limited"
        else:
            data_quality = "insufficient"

        earliest = _earliest_run_date(url, memory_path, adapter.min_reapply_days, now)
        eligible_now = len(blockers) == 0

        entry = {
            "url": url,
            "tier": "C",
            "suggested_strategy": item.get("suggested_strategy"),
            "selection_reason": item.get("selection_rationale"),
            "data_quality": data_quality,
            "gsc_impressions": impressions,
            "eligible_now": eligible_now,
            "blocked_reasons": blockers,
            "earliest_possible_run_date": earliest,
        }
        (candidates if eligible_now else excluded).append(entry)

    candidates.sort(key=lambda x: (quality_order.get(x["data_quality"], 3), x["earliest_possible_run_date"]))
    top = candidates[:max_candidates]

    result = {
        "site_id": adapter.site_id,
        "generated_at": now.isoformat(),
        "max_candidates_requested": max_candidates,
        "run2_ready_count": len(candidates),
        "top_candidates": top,
        "all_eligible": candidates,
        "excluded": excluded,
        "guardrails_applied": ["pillar_page_blocked", "money_page_blocked", "rollback_recent",
                               "active_experiment_in_progress", "cooldown_active"],
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result
