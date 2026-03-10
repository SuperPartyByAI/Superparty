"""
core/run_readiness.py — Run Readiness Report (adapter-aware)

Versiunea platformizată a seo_level6_run_readiness.py.
Funcționează cu orice SiteAdapter în loc de paths hardcodate SuperParty.
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


def _days_until(deadline_iso: str, now: datetime) -> float:
    dt = datetime.fromisoformat(deadline_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (dt - now).total_seconds() / 86400


def _days_since(applied_at_iso: str, now: datetime) -> float:
    dt = datetime.fromisoformat(applied_at_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).total_seconds() / 86400


def generate_run_readiness_report(
    adapter: "SiteAdapter",
    output_path: Optional[Path] = None,
    now: Optional[datetime] = None,
) -> dict:
    """
    Generează raportul de readiness pentru Run 2 al unui site.

    Args:
      adapter: SiteAdapter — configurația și regulile site-ului
      output_path: unde salvăm raportul (optional)
      now: datetime UTC curent (pentru testare)
    """
    if now is None:
        now = datetime.now(timezone.utc)

    outcome_memory_path = adapter.reports_dir / "seo_level6_outcome_memory.json"
    experiments = _load_json(outcome_memory_path) or []

    min_reapply_days = adapter.min_reapply_days
    min_impressions = adapter.min_impressions_for_scoring

    active_experiments = [e for e in experiments if e.get("result_label") == "pending"]
    closed_experiments = [e for e in experiments if e.get("result_label") != "pending"]

    cooldown_active_urls = []
    cooldown_lifted_urls = []
    urls_with_sufficient_impressions = []
    urls_with_insufficient_data = []
    any_rollback = False
    observation_deadlines = []
    url_details = []

    for exp in active_experiments:
        url = exp["url"]
        applied_at = exp.get("applied_at", "")
        deadline = exp.get("observation_deadline", "")
        rollback = exp.get("rollback_happened", False)

        if rollback:
            any_rollback = True

        days_since = _days_since(applied_at, now) if applied_at else 0
        days_until = _days_until(deadline, now) if deadline else 0

        cooldown_closed = days_since >= min_reapply_days
        (cooldown_lifted_urls if cooldown_closed else cooldown_active_urls).append(url)

        if deadline:
            observation_deadlines.append(deadline)

        gsc_after = exp.get("gsc_after", {}) or {}
        impressions = gsc_after.get("impressions")

        if impressions is not None and impressions >= min_impressions:
            urls_with_sufficient_impressions.append(url)
        else:
            urls_with_insufficient_data.append(url)

        url_details.append({
            "url": url,
            "strategy": exp.get("strategy"),
            "applied_at": applied_at[:10] if applied_at else None,
            "observation_deadline": deadline[:10] if deadline else None,
            "days_since_apply": round(days_since, 2),
            "days_until_deadline": round(max(0, days_until), 2),
            "past_deadline": days_until <= 0,
            "cooldown_closed": cooldown_closed,
            "impressions_after": impressions,
            "min_impressions_needed": min_impressions,
            "has_sufficient_impressions": impressions is not None and impressions >= min_impressions,
            "rollback_happened": rollback,
            "result_label": exp.get("result_label"),
        })

    blocked_reasons = []
    all_insufficient = bool(urls_with_insufficient_data) and not bool(urls_with_sufficient_impressions)

    if any_rollback:
        blocked_reasons.append("active_rollback_conflict")
    if cooldown_active_urls:
        blocked_reasons.append(f"cooldown_not_lifted ({len(cooldown_active_urls)} URL-uri)")
    if all_insufficient and active_experiments:
        blocked_reasons.append("all_experiments_insufficient_data")
    if not urls_with_sufficient_impressions and active_experiments:
        blocked_reasons.append(f"no_url_above_min_impressions (threshold: {min_impressions})")
    if active_experiments and observation_deadlines:
        all_open = all(
            (datetime.fromisoformat(d) if d.endswith("Z") or "+" in d
             else datetime.fromisoformat(d).replace(tzinfo=timezone.utc)) > now
            for d in observation_deadlines
        )
        if all_open:
            blocked_reasons.append("observation_window_not_closed_for_all")

    run2_allowed = len(blocked_reasons) == 0

    if observation_deadlines:
        next_check = (now + timedelta(days=1)).date().isoformat()
    elif blocked_reasons:
        next_check = (now + timedelta(days=1)).date().isoformat()
    else:
        next_check = now.date().isoformat()

    if run2_allowed:
        recommended_action = "Run 2 permis. Verifică planner-ul Run 2 și selectează candidații."
    elif "cooldown_not_lifted" in " ".join(blocked_reasons):
        recommended_action = f"Asteapta ridicarea cooldown-ului. Next check: {next_check}"
    elif "insufficient_data" in " ".join(blocked_reasons):
        recommended_action = "Injecteaza date GSC din export Search Console."
    else:
        recommended_action = f"Verifica motivele de blocare si re-ruleaza pe {next_check}."

    report = {
        "site_id": adapter.site_id,
        "generated_at": now.isoformat(),
        "run1_status": {
            "active_experiments": len(active_experiments),
            "closed_experiments": len(closed_experiments),
            "any_rollback": any_rollback,
        },
        "observation_deadline": min(observation_deadlines) if observation_deadlines else None,
        "min_impressions_threshold": min_impressions,
        "min_reapply_days": min_reapply_days,
        "cooldown_lifted_urls": cooldown_lifted_urls,
        "cooldown_active_urls": cooldown_active_urls,
        "urls_with_sufficient_impressions": urls_with_sufficient_impressions,
        "urls_with_insufficient_data": urls_with_insufficient_data,
        "run2_allowed": run2_allowed,
        "blocked_reasons": blocked_reasons,
        "recommended_next_check_at": next_check,
        "recommended_action": recommended_action,
        "url_details": url_details,
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    return report
