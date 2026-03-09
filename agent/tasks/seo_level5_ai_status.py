"""
SEO Level 5 — AI Proposal Layer Status Artifact (Read-Only Observability)

Generates reports/superparty/seo_level5_ai_status.json with operational
visibility into the LLM proposal layer introduced in PR #82.

Contract:
  - READ-ONLY: no writes to Astro pages, no approval/apply/rollback changes
  - Schema-stable: additive fields only, no breaking changes to L5 artifacts
  - Runs independently: can be called after dry-run or standalone
  - Failure-safe: always writes a degraded artifact if Ollama unreachable
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

log = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AI_STATUS_PATH = _REPO_ROOT / "reports" / "superparty" / "seo_level5_ai_status.json"
_DRY_RUN_PATH = _REPO_ROOT / "reports" / "superparty" / "seo_level5_dry_run_actions.json"

# ─── Configuration ────────────────────────────────────────────────────────────

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.2:3b")

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _check_ollama_reachable() -> tuple[bool, list[str]]:
    """
    Checks if Ollama is reachable and returns (reachable, available_models).
    Never raises — returns (False, []) on any error.
    """
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        models = [m["name"] for m in data.get("models", [])]
        return True, models
    except Exception as exc:
        log.debug("Ollama not reachable: %s", exc)
        return False, []


def _read_dry_run_artifact() -> dict | None:
    """Reads the latest dry-run artifact. Returns None if absent/invalid."""
    try:
        with open(_DRY_RUN_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _count_proposal_sources(actions: list[dict]) -> dict[str, int]:
    """Counts proposal_source values across all actions."""
    counts: dict[str, int] = {"llm": 0, "deterministic_fallback": 0, "unknown": 0}
    for action in actions:
        source = action.get("proposal", {}).get("proposal_source", "unknown")
        if source not in counts:
            counts[source] = 0
        counts[source] += 1
    return counts

# ─── Main ─────────────────────────────────────────────────────────────────────

def collect_ai_status() -> dict:
    """
    Collects the current AI proposal layer status and returns the status dict.
    Never raises.
    """
    now = datetime.now(timezone.utc).isoformat()
    ollama_reachable, available_models = _check_ollama_reachable()
    model_available = LLM_MODEL in available_models

    dry_run = _read_dry_run_artifact()
    if dry_run:
        last_dry_run_at = dry_run.get("metadata", {}).get("generated_at", None)
        actions = dry_run.get("actions", [])
        candidate_count = len(actions)
        proposal_source_counts = _count_proposal_sources(actions)
    else:
        last_dry_run_at = None
        candidate_count = 0
        proposal_source_counts = {"llm": 0, "deterministic_fallback": 0, "unknown": 0}

    return {
        "generated_at": now,
        "schema_version": "1.0",
        "llm_enabled": True,
        "ollama_reachable": ollama_reachable,
        "ollama_url": OLLAMA_URL,
        "model": LLM_MODEL,
        "model_available": model_available,
        "available_models": available_models,
        "last_dry_run_at": last_dry_run_at,
        "candidate_count": candidate_count,
        "proposal_source_counts": proposal_source_counts,
        "notes": (
            "Ollama is reachable and model is available — LLM proposals active."
            if ollama_reachable and model_available
            else (
                f"Ollama reachable but model '{LLM_MODEL}' not found in available models."
                if ollama_reachable
                else "Ollama not reachable — dry-run will use deterministic fallback."
            )
        ),
    }


def write_ai_status(status: dict | None = None) -> Path:
    """
    Writes the AI status artifact. Returns the path written.
    Reads from collect_ai_status() if status is None.
    """
    if status is None:
        status = collect_ai_status()
    _AI_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_AI_STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    log.info("AI status written to %s", _AI_STATUS_PATH)
    return _AI_STATUS_PATH


if __name__ == "__main__":
    import logging as _logging
    _logging.basicConfig(level=_logging.INFO)
    status = collect_ai_status()
    path = write_ai_status(status)
    print(json.dumps(status, indent=2, ensure_ascii=False))
    print(f"\nWritten to: {path}")
