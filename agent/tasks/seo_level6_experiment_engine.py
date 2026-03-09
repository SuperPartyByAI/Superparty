"""
SEO Level 6 — Experiment Engine

Gestioneaza ciclul de viata al experimentelor de snippet optimization:
- deschidere experiment (cu guardrails)
- inchidere experimente expirate
- status si observabilitate

GARANTII:
  - MAX_EXPERIMENTS = 3 simultan (nu mai mult)
  - Pillar pages blocate (din registry L5)
  - URL cu experiment activ nu poate fi redeschis
  - Fereastra minima de observare: 14 zile
  - ZERO modificari de fisiere site. Scrie NUMAI in reports/superparty/seo_level6_*.json
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, List

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR  = ROOT_DIR / "config" / "seo"
REPORTS_DIR = ROOT_DIR / "reports" / "superparty"

PILLAR_REGISTRY_PATH     = CONFIG_DIR  / "pillar_pages_registry.json"
OUTCOME_MEMORY_PATH      = REPORTS_DIR / "seo_level6_outcome_memory.json"
EXPERIMENTS_ACTIVE_PATH  = REPORTS_DIR / "seo_level6_experiments_active.json"
EXPERIMENTS_CLOSED_PATH  = REPORTS_DIR / "seo_level6_experiments_closed.json"
STRATEGY_SCORES_PATH     = REPORTS_DIR / "seo_level6_strategy_scores.json"
STATUS_PATH              = REPORTS_DIR / "seo_level6_status.json"

MAX_EXPERIMENTS: int = 3
OBSERVATION_WINDOW_DAYS: int = 14


# ─── I/O ─────────────────────────────────────────────────────────────────────

def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ─── Pillar registry ──────────────────────────────────────────────────────────

def _load_pillar_registry(registry_path: Path = PILLAR_REGISTRY_PATH) -> list:
    data = _load_json(registry_path)
    if not data:
        return []
    return data.get("pillar_pages", [])


def _is_pillar(url: str, registry_path: Path = PILLAR_REGISTRY_PATH) -> bool:
    pillar_urls = _load_pillar_registry(registry_path)
    url_norm = url.rstrip("/")
    return any(p.rstrip("/") == url_norm for p in pillar_urls)


# ─── Experiment guardrails ────────────────────────────────────────────────────

def can_open_experiment(
    url: str,
    pillar_registry_path: Path = PILLAR_REGISTRY_PATH,
    memory_path: Path = OUTCOME_MEMORY_PATH,
    max_experiments: int = MAX_EXPERIMENTS,
) -> tuple[bool, list]:
    """
    Returns (can_open: bool, blockers: list[str]).

    Blockers:
      - "pillar_page_in_registry"    — URL is a pillar page
      - "url_has_active_experiment"  — URL already has a pending experiment
      - "max_experiments_reached"    — global experiment budget exhausted
    """
    blockers = []

    # Check pillar registry
    if _is_pillar(url, pillar_registry_path):
        blockers.append("pillar_page_in_registry")

    # Check for existing active experiment on this URL
    from agent.tasks.seo_level6_outcome_memory import is_url_in_active_experiment
    if is_url_in_active_experiment(url, memory_path):
        blockers.append("url_has_active_experiment")

    # Check global budget
    from agent.tasks.seo_level6_outcome_memory import get_pending
    active_count = len(get_pending(memory_path))
    if active_count >= max_experiments:
        blockers.append(f"max_experiments_reached_{active_count}_of_{max_experiments}")

    return (len(blockers) == 0, blockers)


def get_active_experiment_count(memory_path: Path = OUTCOME_MEMORY_PATH) -> int:
    from agent.tasks.seo_level6_outcome_memory import get_pending
    return len(get_pending(memory_path))


# ─── Experiment lifecycle ─────────────────────────────────────────────────────

def open_experiment(
    url: str,
    strategy: str,
    before_meta: str,
    after_meta: str,
    proposal_source: str = "unknown",
    gsc_before: Optional[dict] = None,
    pillar_registry_path: Path = PILLAR_REGISTRY_PATH,
    memory_path: Path = OUTCOME_MEMORY_PATH,
    max_experiments: int = MAX_EXPERIMENTS,
    observation_window_days: int = OBSERVATION_WINDOW_DAYS,
) -> dict:
    """
    Open a new experiment after checking all guardrails.
    Returns {"experiment": record, "blocked": bool, "blockers": list}.
    """
    can_open, blockers = can_open_experiment(
        url, pillar_registry_path, memory_path, max_experiments
    )
    if not can_open:
        return {
            "experiment": None,
            "blocked": True,
            "blockers": blockers,
        }

    from agent.tasks.seo_level6_outcome_memory import add_experiment
    record = add_experiment(
        url=url,
        strategy=strategy,
        before_meta=before_meta,
        after_meta=after_meta,
        proposal_source=proposal_source,
        observation_window_days=observation_window_days,
        gsc_before=gsc_before,
        memory_path=memory_path,
    )
    return {
        "experiment": record,
        "blocked": False,
        "blockers": [],
    }


def close_expired_experiments(
    memory_path: Path = OUTCOME_MEMORY_PATH,
) -> List[dict]:
    """
    For all pending experiments past their observation deadline,
    scores them and marks as closed.
    Returns list of newly closed experiments.
    """
    from agent.tasks.seo_level6_outcome_memory import (
        get_experiments_past_deadline,
        update_outcome,
    )
    from agent.tasks.seo_level6_scorer import score_experiment

    expired = get_experiments_past_deadline(memory_path)
    closed = []

    for exp in expired:
        scored = score_experiment(exp)
        updated = update_outcome(
            experiment_id=exp["experiment_id"],
            result_label=scored["result_label"],
            gsc_after=exp.get("gsc_after"),
            rollback_happened=exp.get("rollback_happened", False),
            score_explanation=scored["explanation"],
            memory_path=memory_path,
        )
        if updated:
            closed.append(updated)

    return closed


def inject_gsc_data(
    experiment_id: str,
    impressions_after: Optional[int],
    ctr_after: Optional[float],
    position_after: Optional[float],
    memory_path: Path = OUTCOME_MEMORY_PATH,
) -> Optional[dict]:
    """
    Inject GSC data after the observation window.
    Updates gsc_after in the experiment record.
    Does NOT auto-close — call close_expired_experiments() for that.
    """
    records = []
    if memory_path.exists():
        with open(memory_path, "r", encoding="utf-8") as f:
            records = json.load(f)

    for rec in records:
        if rec.get("experiment_id") == experiment_id:
            rec["gsc_after"] = {
                "impressions": impressions_after,
                "ctr": ctr_after,
                "position": position_after,
            }
            _write_json(memory_path, records)
            return rec

    return None


# ─── Observability snapshot ───────────────────────────────────────────────────

def generate_observability_snapshot(
    memory_path: Path = OUTCOME_MEMORY_PATH,
    active_path: Path = EXPERIMENTS_ACTIVE_PATH,
    closed_path: Path = EXPERIMENTS_CLOSED_PATH,
    scores_path: Path = STRATEGY_SCORES_PATH,
    status_path: Path = STATUS_PATH,
) -> dict:
    """
    Generate all read-only observability artefacts:
      - seo_level6_experiments_active.json
      - seo_level6_experiments_closed.json
      - seo_level6_strategy_scores.json
      - seo_level6_status.json
    Returns the status dict.
    """
    from agent.tasks.seo_level6_outcome_memory import (
        get_pending, get_closed, get_all_experiments
    )
    from agent.tasks.seo_level6_scorer import (
        compute_strategy_scores, get_best_strategy
    )

    now = datetime.now(timezone.utc).isoformat()
    all_exps = get_all_experiments(memory_path)
    pending = get_pending(memory_path)
    closed = get_closed(memory_path)

    # Active experiments: pending + annotate deadline proximity
    active_annotated = []
    for exp in pending:
        deadline_str = exp.get("observation_deadline", "")
        days_remaining = None
        past_deadline = False
        try:
            deadline = datetime.fromisoformat(deadline_str)
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            delta = deadline - datetime.now(timezone.utc)
            days_remaining = round(delta.total_seconds() / 86400, 1)
            past_deadline = days_remaining < 0
        except (ValueError, TypeError):
            pass
        active_annotated.append({
            **exp,
            "days_remaining": days_remaining,
            "past_deadline": past_deadline,
        })

    _write_json(active_path, active_annotated)

    # Closed experiments + rollback list
    closed_annotated = []
    rollback_urls = []
    for exp in closed:
        closed_annotated.append(exp)
        if exp.get("rollback_happened"):
            rollback_urls.append(exp.get("url"))

    _write_json(closed_path, closed_annotated)

    # Strategy scores
    strategy_scores = compute_strategy_scores(all_exps)
    best_strategy = get_best_strategy(strategy_scores)
    _write_json(scores_path, {
        "generated_at": now,
        "scores": strategy_scores,
        "best_strategy": best_strategy,
    })

    # Status overview
    # URLs in cooldown from outcome memory (applied in last OBSERVATION_WINDOW_DAYS)
    cutoff = datetime.now(timezone.utc) - timedelta(days=OBSERVATION_WINDOW_DAYS)
    cooldown_urls = []
    seen_cooldown = set()
    for exp in sorted(all_exps, key=lambda e: e.get("applied_at", ""), reverse=True):
        url = exp.get("url", "")
        if url in seen_cooldown:
            continue
        applied_str = exp.get("applied_at", "")
        try:
            applied = datetime.fromisoformat(applied_str)
            if applied.tzinfo is None:
                applied = applied.replace(tzinfo=timezone.utc)
            if applied >= cutoff:
                cooldown_urls.append(url)
                seen_cooldown.add(url)
        except (ValueError, TypeError):
            continue

    status = {
        "generated_at": now,
        "experiments": {
            "active_count": len(pending),
            "closed_count": len(closed),
            "total": len(all_exps),
            "max_allowed": MAX_EXPERIMENTS,
            "budget_remaining": max(0, MAX_EXPERIMENTS - len(pending)),
        },
        "outcomes": {
            "positive": sum(1 for e in closed if e.get("result_label") == "positive"),
            "neutral": sum(1 for e in closed if e.get("result_label") == "neutral"),
            "negative": sum(1 for e in closed if e.get("result_label") == "negative"),
            "strong_negative": sum(1 for e in closed if e.get("result_label") == "strong_negative"),
            "insufficient_data": sum(1 for e in closed if e.get("result_label") == "insufficient_data"),
        },
        "best_strategy": best_strategy,
        "strategy_scores": strategy_scores,
        "cooldown_urls": cooldown_urls,
        "rollback_urls": rollback_urls,
        "active_experiments": [
            {
                "experiment_id": e["experiment_id"],
                "url": e["url"],
                "strategy": e["strategy"],
                "applied_at": e["applied_at"],
                "observation_deadline": e["observation_deadline"],
                "days_remaining": e.get("days_remaining"),
                "past_deadline": e.get("past_deadline"),
            }
            for e in active_annotated
        ],
    }

    _write_json(status_path, status)
    return status
