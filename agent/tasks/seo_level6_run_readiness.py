"""
agent/tasks/seo_level6_run_readiness.py

Run Readiness Report — L6 Learning Loop

Generează zilnic un raport read-only care spune dacă sistemul
este gata pentru Run 2 sau nu, și de ce.

Schema output (seo_level6_run_readiness.json):
  generated_at, run1_status, observation_deadline, days_until_deadline,
  cooldown_lifted_urls, cooldown_active_urls,
  urls_with_sufficient_impressions, urls_with_insufficient_data,
  run2_allowed: bool, blocked_reasons: [...],
  recommended_next_check_at, recommended_action
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent

# Praguri
MIN_IMPRESSIONS_FOR_SCORING = 80      # min impresii post-apply pentru verdict util
MIN_REAPPLY_DAYS = 7                  # zile min cooldown dupa apply (dynamic cooldown minim)
MIN_EXPERIMENTS_WITH_DATA = 1         # cel putin 1 experiment cu date reale
MIN_EXPERIMENTS_NON_INSUFFICIENT = 1  # cel putin 1 verdict != insufficient_data pt Run 2


def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _days_until(deadline_iso: str, now: datetime) -> float:
    deadline = datetime.fromisoformat(deadline_iso)
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return (deadline - now).total_seconds() / 86400


def _days_since(applied_at_iso: str, now: datetime) -> float:
    applied = datetime.fromisoformat(applied_at_iso)
    if applied.tzinfo is None:
        applied = applied.replace(tzinfo=timezone.utc)
    return (now - applied).total_seconds() / 86400


def generate_run_readiness_report(
    outcome_memory_path: Path,
    cooldown_config_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    run1_url_set: Optional[set] = None,
    now: Optional[datetime] = None,
) -> dict:
    """
    Generează raportul de readiness pentru Run 2.

    Args:
      outcome_memory_path: calea la seo_level6_outcome_memory.json
      cooldown_config_path: configuratie cooldown (optional, se foloseste MIN_REAPPLY_DAYS ca fallback)
      output_path: unde sa scrie raportul JSON
      run1_url_set: set de URL-uri din Run 1 (daca nu e specificat, se detecteaza din memory)
      now: data curenta (pentru testare)

    Returns dict cu raportul complet.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    experiments = _load_json(outcome_memory_path) or []

    # Determina min_reapply_days din config sau fallback
    min_reapply_days = MIN_REAPPLY_DAYS
    if cooldown_config_path and cooldown_config_path.exists():
        try:
            cfg = _load_json(cooldown_config_path)
            min_reapply_days = cfg.get("min_reapply_days", MIN_REAPPLY_DAYS)
        except Exception:
            pass

    # Analizeaza fiecare experiment
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

        days_since_apply = _days_since(applied_at, now) if applied_at else 0
        days_until_deadline = _days_until(deadline, now) if deadline else 0
        past_deadline = days_until_deadline <= 0

        # Cooldown
        cooldown_closed = days_since_apply >= min_reapply_days
        if cooldown_closed:
            cooldown_lifted_urls.append(url)
        else:
            cooldown_active_urls.append(url)

        # Deadline globala
        if deadline:
            observation_deadlines.append(deadline)

        # GSC data
        gsc_after = exp.get("gsc_after", {})
        impressions_after = gsc_after.get("impressions") if gsc_after else None

        if impressions_after is not None and impressions_after >= MIN_IMPRESSIONS_FOR_SCORING:
            urls_with_sufficient_impressions.append(url)
        else:
            urls_with_insufficient_data.append(url)

        # Verdict curent
        result_label = exp.get("result_label", "pending")

        url_details.append({
            "url": url,
            "strategy": exp.get("strategy"),
            "applied_at": applied_at[:10] if applied_at else None,
            "observation_deadline": deadline[:10] if deadline else None,
            "days_since_apply": round(days_since_apply, 2),
            "days_until_deadline": round(max(0, days_until_deadline), 2),
            "past_deadline": past_deadline,
            "cooldown_closed": cooldown_closed,
            "impressions_after": impressions_after,
            "min_impressions_needed": MIN_IMPRESSIONS_FOR_SCORING,
            "has_sufficient_impressions": impressions_after is not None and impressions_after >= MIN_IMPRESSIONS_FOR_SCORING,
            "rollback_happened": rollback,
            "result_label": result_label,
        })

    # Verdictul global asupra datelor din Run 1
    all_insufficient_data = bool(urls_with_insufficient_data) and not bool(urls_with_sufficient_impressions)
    any_non_insufficient = any(
        e.get("result_label") not in ("pending", "insufficient_data")
        for e in experiments
    )

    # Gating Run 2
    blocked_reasons = []

    if any_rollback:
        blocked_reasons.append("active_rollback_conflict")

    if cooldown_active_urls:
        blocked_reasons.append(
            f"cooldown_not_lifted ({len(cooldown_active_urls)} URL-uri in cooldown)"
        )

    if all_insufficient_data and active_experiments:
        blocked_reasons.append("all_experiments_insufficient_data")

    if not urls_with_sufficient_impressions and active_experiments:
        blocked_reasons.append(
            f"no_url_above_min_impressions (threshold: {MIN_IMPRESSIONS_FOR_SCORING})"
        )

    if active_experiments and all(
        (datetime.fromisoformat(d) if "+" in d else datetime.fromisoformat(d).replace(tzinfo=timezone.utc)) > now
        for d in observation_deadlines if d
    ):
        blocked_reasons.append("observation_window_not_closed_for_all")

    run2_allowed = len(blocked_reasons) == 0

    # Recomandata next check
    if cooldown_active_urls and observation_deadlines:
        earliest_deadline = min(observation_deadlines)
        applied_times = [e.get("applied_at", "") for e in active_experiments if e.get("applied_at")]
        if applied_times:
            earliest_apply = min(applied_times)
            applied_dt = datetime.fromisoformat(earliest_apply)
            cooldown_lifted_at = applied_dt + timedelta(days=min_reapply_days)
            next_check = min(
                cooldown_lifted_at,
                datetime.fromisoformat(earliest_deadline) - timedelta(days=1),
            )
            recommended_next_check_at = next_check.date().isoformat()
        else:
            recommended_next_check_at = (now + timedelta(days=7)).date().isoformat()
    elif blocked_reasons:
        recommended_next_check_at = (now + timedelta(days=1)).date().isoformat()
    else:
        recommended_next_check_at = now.date().isoformat()

    # Actiunea recomandata
    if run2_allowed:
        recommended_action = "Run 2 permis. Verifică planner-ul Run 2 și selectează candidații."
    elif "observation_window_not_closed" in " ".join(blocked_reasons):
        recommended_action = f"Asteapta inchiderea ferestrei de observatie Run 1. Next check: {recommended_next_check_at}"
    elif "cooldown_not_lifted" in " ".join(blocked_reasons):
        recommended_action = f"Asteapta ridicarea cooldown-ului. Next check: {recommended_next_check_at}"
    elif "insufficient_data" in " ".join(blocked_reasons):
        recommended_action = "Injecteaza date GSC din export Search Console, apoi re-ruleaza acest raport."
    else:
        recommended_action = f"Verifica motivele de blocare si re-ruleaza pe {recommended_next_check_at}."

    # Schema finala
    report = {
        "generated_at": now.isoformat(),
        "run1_status": {
            "active_experiments": len(active_experiments),
            "closed_experiments": len(closed_experiments),
            "any_rollback": any_rollback,
        },
        "observation_deadline": min(observation_deadlines) if observation_deadlines else None,
        "days_until_earliest_deadline": round(
            min(_days_until(d, now) for d in observation_deadlines), 2
        ) if observation_deadlines else None,
        "min_impressions_threshold": MIN_IMPRESSIONS_FOR_SCORING,
        "min_reapply_days": min_reapply_days,
        "cooldown_lifted_urls": cooldown_lifted_urls,
        "cooldown_active_urls": cooldown_active_urls,
        "urls_with_sufficient_impressions": urls_with_sufficient_impressions,
        "urls_with_insufficient_data": urls_with_insufficient_data,
        "run2_allowed": run2_allowed,
        "blocked_reasons": blocked_reasons,
        "recommended_next_check_at": recommended_next_check_at,
        "recommended_action": recommended_action,
        "url_details": url_details,
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    return report
