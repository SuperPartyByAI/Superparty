"""
SEO Level 5 — LLM Proposal Generator for Meta Descriptions

Generates a single meta description via Ollama (local LLM).
This module is intentionally ISOLATED from apply, approval, and rollback.

Contract:
  - Input: Candidate (url, current_meta_description, reason_flags)
  - Output: str (validated meta description) or None (→ caller uses deterministic fallback)
  - Side-effects: NONE (read-only, no file writes)
  - Timeout: 30s (LLM unresponsive → None → fallback)
"""
from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from agent.tasks.seo_level5_meta_description_dry_run import Candidate

log = logging.getLogger(__name__)

# ─── Configuration (env-overridable) ──────────────────────────────────────────

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.2:3b")

# Validator constraints
_MIN_CHARS = 140
_MAX_CHARS = 160
_TIMEOUT_SEC = 30

# ─── Prompt ───────────────────────────────────────────────────────────────────

_PROMPT_TEMPLATE = """\
Generează o singură meta description în limba română pentru pagina de mai jos.

Constrângeri OBLIGATORII:
- 140-160 caractere (numără exact)
- text simplu, fără HTML
- fără ghilimele duble sau simple
- fără promisiuni absolute (ex: "garantat", "cel mai bun")
- fără clickbait
- relevant strict pentru URL și conținut
- ton clar, util, pentru părinți
- nu inventa servicii, prețuri sau locații care nu apar în context
- returnează DOAR textul final, nimic altceva, fără explicații

URL: {url}
Meta actuală: {current_meta}
Semnale selecție: {reason_flags}
"""

# ─── Validator ────────────────────────────────────────────────────────────────

def validate_proposal(text: str, current_meta: str = "") -> bool:
    """
    Returns True only if 'text' passes all safety constraints.
    Any failure → False → caller falls back to deterministic template.
    """
    if not text or not isinstance(text, str):
        return False
    # Length
    if not (_MIN_CHARS <= len(text) <= _MAX_CHARS):
        log.debug("LLM proposal failed length check: %d chars", len(text))
        return False
    # No quotes (quote-safety required by apply executor)
    if '"' in text or "'" in text:
        log.debug("LLM proposal contains quotes — rejected")
        return False
    # No HTML
    if '<' in text or '>' in text:
        log.debug("LLM proposal contains HTML — rejected")
        return False
    # No newlines
    if '\n' in text or '\r' in text:
        log.debug("LLM proposal contains newlines — rejected")
        return False
    # Not identical to current (no-op change)
    if current_meta and text.strip() == current_meta.strip():
        log.debug("LLM proposal identical to current meta — rejected")
        return False
    return True


# ─── LLM client ───────────────────────────────────────────────────────────────

def _call_ollama(prompt: str) -> str | None:
    """
    Calls Ollama /api/generate. Returns raw response text or None on any error.
    """
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
            timeout=_TIMEOUT_SEC,
        )
        resp.raise_for_status()
        data = resp.json()
        raw = data.get("response", "").strip()
        return raw if raw else None
    except requests.exceptions.Timeout:
        log.warning("Ollama timeout after %ds — falling back to deterministic", _TIMEOUT_SEC)
        return None
    except requests.exceptions.ConnectionError:
        log.warning("Ollama not reachable at %s — falling back to deterministic", OLLAMA_URL)
        return None
    except Exception as exc:
        log.warning("Ollama call failed: %s — falling back to deterministic", exc)
        return None


def _clean_response(raw: str) -> str:
    """
    Strip LLM artifacts: leading/trailing whitespace, markdown fences, quotes.
    Ollama sometimes wraps output in ``` or starts with 'Meta description:'.
    """
    text = raw.strip()
    # Strip markdown code fences
    text = re.sub(r"^```.*?```$", "", text, flags=re.DOTALL).strip()
    text = re.sub(r"^`|`$", "", text).strip()
    # Strip common LLM prefixes
    for prefix in ("Meta description:", "Meta Description:", "Descriere:", "Răspuns:"):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    # Take only the first line (should be a single line)
    text = text.split('\n')[0].strip()
    return text


# ─── Public API ───────────────────────────────────────────────────────────────

def build_llm_meta_description(candidate: "Candidate") -> str | None:
    """
    Attempts to generate a validated meta description via LLM.

    Returns:
        str  — validated meta description (140-160 chars, quote-safe, no HTML)
        None — LLM unavailable, response invalid, or validation failed
               Caller MUST fall back to deterministic template.

    This function has NO side-effects: it does NOT write files, create commits,
    or touch the approval/apply pipeline.
    """
    prompt = _PROMPT_TEMPLATE.format(
        url=candidate.url,
        current_meta=candidate.current_meta_description or "(lipsă)",
        reason_flags=", ".join(candidate.reason_flags) if candidate.reason_flags else "(none)",
    )

    raw = _call_ollama(prompt)
    if raw is None:
        return None

    text = _clean_response(raw)

    if not validate_proposal(text, candidate.current_meta_description):
        log.info(
            "LLM proposal for %s failed validation (len=%d) — using deterministic fallback",
            candidate.url, len(text)
        )
        return None

    log.info("LLM proposal accepted for %s (%d chars)", candidate.url, len(text))
    return text
