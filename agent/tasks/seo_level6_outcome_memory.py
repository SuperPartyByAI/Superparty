"""
SEO Level 6 — Outcome Memory

Read/write model pentru memoria experimentelor per URL.
Pastreaza istoricul: ce s-a schimbat, cand, cu ce strategie, si care a fost outcome-ul.

IMPORTANT: Acest modul SCRIE DOAR in reports/superparty/seo_level6_outcome_memory.json.
Nu modifica niciodata fisiere .astro sau .md ale site-ului.

Schema per inregistrare (experiment):
{
  "experiment_id": "uuid",
  "url": "/slug-pagina",
  "applied_at": "ISO8601",
  "strategy": "local_intent",
  "proposal_source": "deterministic_fallback",
  "before_meta": "...",
  "after_meta": "...",
  "observation_window_days": 14,
  "observation_deadline": "ISO8601",
  "gsc_before": {"impressions": null, "ctr": null, "position": null},
  "gsc_after": {"impressions": null, "ctr": null, "position": null},
  "result_label": "pending",
  "rollback_happened": false,
  "closed_at": null,
  "score_explanation": null
}

result_label valori:
  "pending"           — experiment in derulare, fereastra de observare nu s-a scurs
  "positive"          — CTR a crescut cu minim 5%, date suficiente
  "neutral"           — CTR in marja, date suficiente
  "negative"          — CTR a scazut cu minim 5%, date suficiente
  "insufficient_data" — date GSC insuficiente sau fereastra nu s-a scurs
  "strong_negative"   — rollback a avut loc (override orice alt rezultat)
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, List

ROOT_DIR = Path(__file__).parent.parent.parent
OUTCOME_MEMORY_PATH = ROOT_DIR / "reports" / "superparty" / "seo_level6_outcome_memory.json"

VALID_RESULT_LABELS = {
    "pending",
    "positive",
    "neutral",
    "negative",
    "insufficient_data",
    "strong_negative",
}


# ─── I/O ─────────────────────────────────────────────────────────────────────

def _load_memory(memory_path: Path = OUTCOME_MEMORY_PATH) -> List[dict]:
    if not memory_path.exists():
        return []
    with open(memory_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _save_memory(records: List[dict], memory_path: Path = OUTCOME_MEMORY_PATH) -> None:
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


# ─── Add / Update ─────────────────────────────────────────────────────────────

def add_experiment(
    url: str,
    strategy: str,
    before_meta: str,
    after_meta: str,
    proposal_source: str = "unknown",
    observation_window_days: int = 14,
    gsc_before: Optional[dict] = None,
    memory_path: Path = OUTCOME_MEMORY_PATH,
) -> dict:
    """
    Register a new experiment in outcome memory.
    Returns the created experiment record.
    """
    now = datetime.now(timezone.utc)
    deadline = now + timedelta(days=observation_window_days)

    record = {
        "experiment_id": str(uuid.uuid4()),
        "url": url,
        "applied_at": now.isoformat(),
        "strategy": strategy,
        "proposal_source": proposal_source,
        "before_meta": before_meta,
        "after_meta": after_meta,
        "observation_window_days": observation_window_days,
        "observation_deadline": deadline.isoformat(),
        "gsc_before": gsc_before or {"impressions": None, "ctr": None, "position": None},
        "gsc_after": {"impressions": None, "ctr": None, "position": None},
        "result_label": "pending",
        "rollback_happened": False,
        "closed_at": None,
        "score_explanation": None,
    }

    records = _load_memory(memory_path)
    records.append(record)
    _save_memory(records, memory_path)
    return record


def update_outcome(
    experiment_id: str,
    result_label: str,
    gsc_after: Optional[dict] = None,
    rollback_happened: bool = False,
    score_explanation: Optional[str] = None,
    memory_path: Path = OUTCOME_MEMORY_PATH,
) -> Optional[dict]:
    """
    Update outcome for an existing experiment.
    result_label must be one of VALID_RESULT_LABELS.
    Returns updated record or None if not found.
    """
    if result_label not in VALID_RESULT_LABELS:
        raise ValueError(f"Invalid result_label: {result_label}. Must be one of {VALID_RESULT_LABELS}")

    records = _load_memory(memory_path)
    for rec in records:
        if rec.get("experiment_id") == experiment_id:
            if rollback_happened:
                rec["rollback_happened"] = True
                rec["result_label"] = "strong_negative"  # rollback overrides everything
            else:
                rec["result_label"] = result_label
            if gsc_after is not None:
                rec["gsc_after"] = gsc_after
            if score_explanation is not None:
                rec["score_explanation"] = score_explanation
            rec["closed_at"] = datetime.now(timezone.utc).isoformat()
            _save_memory(records, memory_path)
            return rec

    return None


def mark_rollback(
    url: str,
    memory_path: Path = OUTCOME_MEMORY_PATH,
) -> Optional[dict]:
    """
    Mark the most recent pending experiment for a URL as strong_negative (rollback).
    """
    records = _load_memory(memory_path)
    # Find most recent pending record for this URL
    candidates = [
        r for r in records
        if r.get("url") == url and r.get("result_label") == "pending"
    ]
    if not candidates:
        return None

    # Sort by applied_at, take most recent
    candidates.sort(key=lambda r: r.get("applied_at", ""), reverse=True)
    target = candidates[0]
    target["rollback_happened"] = True
    target["result_label"] = "strong_negative"
    target["closed_at"] = datetime.now(timezone.utc).isoformat()
    target["score_explanation"] = "rollback_happened"
    _save_memory(records, memory_path)
    return target


# ─── Queries ──────────────────────────────────────────────────────────────────

def get_all_experiments(memory_path: Path = OUTCOME_MEMORY_PATH) -> List[dict]:
    return _load_memory(memory_path)


def get_pending(memory_path: Path = OUTCOME_MEMORY_PATH) -> List[dict]:
    """Returns experiments with result_label == 'pending'."""
    return [r for r in _load_memory(memory_path) if r.get("result_label") == "pending"]


def get_closed(memory_path: Path = OUTCOME_MEMORY_PATH) -> List[dict]:
    """Returns experiments with a final result_label (not pending)."""
    return [r for r in _load_memory(memory_path) if r.get("result_label") != "pending"]


def get_by_url(url: str, memory_path: Path = OUTCOME_MEMORY_PATH) -> List[dict]:
    """Returns all experiments for a given URL, sorted oldest-first."""
    return sorted(
        [r for r in _load_memory(memory_path) if r.get("url") == url],
        key=lambda r: r.get("applied_at", ""),
    )


def get_experiments_past_deadline(memory_path: Path = OUTCOME_MEMORY_PATH) -> List[dict]:
    """Returns pending experiments whose observation window has already elapsed."""
    now = datetime.now(timezone.utc)
    result = []
    for r in _load_memory(memory_path):
        if r.get("result_label") != "pending":
            continue
        deadline_str = r.get("observation_deadline", "")
        if not deadline_str:
            continue
        try:
            deadline = datetime.fromisoformat(deadline_str)
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            if now >= deadline:
                result.append(r)
        except (ValueError, TypeError):
            continue
    return result


def is_url_in_active_experiment(
    url: str,
    memory_path: Path = OUTCOME_MEMORY_PATH,
) -> bool:
    """Returns True if the URL has a pending (active) experiment."""
    return any(
        r.get("url") == url and r.get("result_label") == "pending"
        for r in _load_memory(memory_path)
    )
