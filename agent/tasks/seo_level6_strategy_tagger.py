"""
SEO Level 6 — Strategy Tagger v2.0

Versiunea 2.0 inlocuieste algoritmul first-match cu scoring cumulativ:
  - Fiecare keyword din taxonomy contribuie cu keyword_weight la scorul strategiei
  - tier_keywords contribuie cu tier_keyword_weight (implicit 2x)
  - Strategia cu scorul TOTAL mai mare castiga
  - Tie-breaker: strategia mai SPECIFICA (priority mai mare ca valoare) castiga

Observability extinsa:
  - tag_strategy(text) → str (label final)
  - tag_strategy_explain(text) → dict cu scor per strategie, matched keywords,
                                  winning_strategy_reason, all_candidates
  - tag_strategy_debug(text) → dict complet cu toate scoreurile si keyword matches

REGULI TIE-BREAK DOCUMENTATE:
  Daca doua strategii au acelasi scor total:
  1. local_intent bate price_first (localitate specifica > pret generic)
  2. benefits_first bate price_first (beneficii operationale > pret generic)
  3. In rest: prioritatea din taxonomy decide (valoare numerica mai mare = mai specific)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent
TAXONOMY_PATH = ROOT_DIR / "config" / "seo" / "snippet_strategy_taxonomy.json"


def _load_taxonomy(taxonomy_path: Path = TAXONOMY_PATH) -> dict:
    if not taxonomy_path.exists():
        return {}
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _score_text(text: str, taxonomy: dict) -> dict:
    """
    Core scoring engine.

    Returns a dict of:
    {
      "strategy_name": {
        "score": float,
        "matched_keywords": [str, ...],
        "matched_tier_keywords": [str, ...],
        "priority": int,
      },
      ...
    }
    """
    strategies = taxonomy.get("strategies", {})
    text_lower = text.lower()

    results = {}
    for name, cfg in strategies.items():
        positional_check = cfg.get("_positional_check", False)
        if positional_check:
            # brand_first: only match in first N chars
            n_chars = cfg.get("_positional_chars", 20)
            text_scope = text_lower[:n_chars]
        else:
            text_scope = text_lower

        kw_weight = cfg.get("keyword_weight", 1)
        tier_weight = cfg.get("tier_keyword_weight", 2)

        tier_kws = cfg.get("tier_keywords", [])
        regular_kws = cfg.get("keywords", [])

        matched_tier = [kw for kw in tier_kws if kw in text_scope]
        matched_regular = [kw for kw in regular_kws if kw in text_scope]

        score = len(matched_tier) * tier_weight + len(matched_regular) * kw_weight

        results[name] = {
            "score": score,
            "matched_keywords": matched_regular,
            "matched_tier_keywords": matched_tier,
            "priority": cfg.get("priority", 99),
        }

    return results


def _apply_tie_break(candidates: list[tuple[str, dict]]) -> str:
    """
    Applies explicit tie-break rules when two strategies have equal scores.
    candidates: list of (name, score_dict) sorted by score descending.

    Tie-break rules (documented in taxonomy):
    1. local_intent beats price_first at equal score
    2. benefits_first beats price_first at equal score
    3. Otherwise: higher priority value (more specific) wins
    """
    if not candidates:
        return "uncategorized"
    if len(candidates) == 1:
        return candidates[0][0]

    top_score = candidates[0][1]["score"]
    tied = [(n, d) for n, d in candidates if d["score"] == top_score]

    if len(tied) == 1:
        return tied[0][0]

    names_tied = {n for n, _ in tied}

    # Tie-break rule 1: local_intent > price_first
    if "local_intent" in names_tied and "price_first" in names_tied:
        return "local_intent"

    # Tie-break rule 2: benefits_first > price_first
    if "benefits_first" in names_tied and "price_first" in names_tied:
        return "benefits_first"

    # Tie-break rule 3: more specific strategy wins (higher priority value)
    return max(tied, key=lambda x: x[1]["priority"])[0]


def _winner_reason(winner: str, score_data: dict, candidates: list) -> str:
    """Human-readable explanation of why winner was chosen."""
    winner_score = score_data[winner]["score"]
    top_tier_kws = score_data[winner]["matched_tier_keywords"]
    top_kws = score_data[winner]["matched_keywords"]

    tied_names = [n for n, d in score_data.items() if d["score"] == winner_score and n != winner]

    if top_tier_kws:
        reason = f"dominant tier_keywords: {top_tier_kws[:3]}"
    elif top_kws:
        reason = f"keyword match: {top_kws[:3]}"
    else:
        reason = "no matches (fallback)"

    if tied_names:
        reason += f"; tie-break over {tied_names} by rule"

    return reason


# ── Public API ─────────────────────────────────────────────────────────────────

def tag_strategy(
    text: str,
    taxonomy_path: Path = TAXONOMY_PATH,
) -> str:
    """
    Returns a strategy label for the given meta description text.

    Algorithm v2.0 — scoring cumulativ:
    1. Score each strategy: tier_keywords * 2 + keywords * 1
    2. Strategia cu scor total mai mare castiga
    3. Tie-break explicit: local_intent > price_first, benefits_first > price_first
    4. Fallback: strategie cu priority mai mare (mai specifica)
    5. Daca niciun keyword nu se potriveste → 'uncategorized'
    """
    if not text:
        return "uncategorized"

    taxonomy = _load_taxonomy(taxonomy_path)
    fallback = taxonomy.get("fallback_strategy", "uncategorized")

    score_data = _score_text(text, taxonomy)

    # Filter to only strategies with score > 0
    candidates = [(n, d) for n, d in score_data.items() if d["score"] > 0]
    if not candidates:
        return fallback

    candidates.sort(key=lambda x: (-x[1]["score"], -x[1]["priority"]))
    return _apply_tie_break(candidates)


def tag_strategy_explain(
    text: str,
    taxonomy_path: Path = TAXONOMY_PATH,
) -> dict:
    """
    Returns tag_strategy result WITH full observability:
    {
      "strategy": str,
      "matched_keywords": [str],            # regular keywords matched
      "matched_tier_keywords": [str],       # tier keywords matched (2x weight)
      "score": float,                       # winning strategy score
      "winning_strategy_reason": str,       # human-readable explanation
      "all_candidates": [                   # all strategies with score > 0
        {"strategy": str, "score": float, "matched_keywords": [...], "matched_tier_keywords": [...]}
      ],
      "text_sample": str,
    }
    """
    if not text:
        return {
            "strategy": "uncategorized",
            "matched_keywords": [],
            "matched_tier_keywords": [],
            "score": 0,
            "winning_strategy_reason": "empty text",
            "all_candidates": [],
            "text_sample": "",
        }

    taxonomy = _load_taxonomy(taxonomy_path)
    fallback = taxonomy.get("fallback_strategy", "uncategorized")

    score_data = _score_text(text, taxonomy)
    candidates = [(n, d) for n, d in score_data.items() if d["score"] > 0]

    if not candidates:
        return {
            "strategy": fallback,
            "matched_keywords": [],
            "matched_tier_keywords": [],
            "score": 0,
            "winning_strategy_reason": "no keywords matched in any strategy",
            "all_candidates": [],
            "text_sample": text[:80],
        }

    candidates.sort(key=lambda x: (-x[1]["score"], -x[1]["priority"]))
    winner = _apply_tie_break(candidates)
    winner_data = score_data[winner]

    return {
        "strategy": winner,
        "matched_keywords": winner_data["matched_keywords"],
        "matched_tier_keywords": winner_data["matched_tier_keywords"],
        "score": winner_data["score"],
        "winning_strategy_reason": _winner_reason(winner, score_data, candidates),
        "all_candidates": [
            {
                "strategy": n,
                "score": d["score"],
                "matched_keywords": d["matched_keywords"],
                "matched_tier_keywords": d["matched_tier_keywords"],
            }
            for n, d in candidates
        ],
        "text_sample": text[:80],
    }


def tag_strategy_debug(
    text: str,
    taxonomy_path: Path = TAXONOMY_PATH,
) -> dict:
    """
    Full scoring debug: returns scores for ALL strategies, including those with score=0.
    Use for debugging / observability pipeline.
    """
    if not text:
        return {"winner": "uncategorized", "all_scores": {}, "text": ""}

    taxonomy = _load_taxonomy(taxonomy_path)
    score_data = _score_text(text, taxonomy)
    winner = tag_strategy(text, taxonomy_path)

    return {
        "winner": winner,
        "text_sample": text[:120],
        "all_scores": {
            name: {
                "score": d["score"],
                "matched_tier_keywords": d["matched_tier_keywords"],
                "matched_keywords": d["matched_keywords"],
                "priority": d["priority"],
            }
            for name, d in sorted(score_data.items(), key=lambda x: -x[1]["score"])
        },
    }


def get_all_strategy_names(taxonomy_path: Path = TAXONOMY_PATH) -> list:
    """Returns all valid strategy names from taxonomy."""
    taxonomy = _load_taxonomy(taxonomy_path)
    names = list(taxonomy.get("strategies", {}).keys())
    fallback = taxonomy.get("fallback_strategy", "uncategorized")
    if fallback not in names:
        names.append(fallback)
    return names
