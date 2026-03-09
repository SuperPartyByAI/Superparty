"""
SEO Level 6 — Strategy Tagger

Etichetează o propunere de meta description cu una dintre strategiile din taxonomy.
Reguli complet explicabile — keyword matching cu prioritate.
Nu folosește ML sau modele externe.

Strategii (in ordinea prioritatii):
  1. price_first       – prețuri, lei, pachete
  2. benefits_first    – premium, garantat, profesionist
  3. services_list     – baloane, pictură, jocuri, etc.
  4. local_intent      – București, Ilfov, sector, localitate
  5. urgency_soft      – rezervă acum, disponibilitate limitată
  6. family_trust      – copii, părinți, siguranță
  7. brand_first       – SuperParty în primele 20 chars

Fallback: "uncategorized"
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent
TAXONOMY_PATH = ROOT_DIR / "config" / "seo" / "snippet_strategy_taxonomy.json"


def _load_taxonomy(taxonomy_path: Path = TAXONOMY_PATH) -> dict:
    if not taxonomy_path.exists():
        return {}
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        return json.load(f)


def tag_strategy(
    text: str,
    taxonomy_path: Path = TAXONOMY_PATH,
) -> str:
    """
    Returns a strategy label for the given meta description text.

    Rules applied in priority order:
    1. brand_first: "superparty" in first 20 chars (case-insensitive)
    2. price_first: price keywords + optional number
    3. benefits_first: quality/guarantee keywords
    4. services_list: service activity keywords (baloane, pictură, etc.)
    5. local_intent: location keywords (București, sector, etc.)
    6. urgency_soft: CTA + urgency keywords
    7. family_trust: family/trust keywords

    Returns "uncategorized" if no keyword matches.
    """
    if not text:
        return "uncategorized"

    taxonomy = _load_taxonomy(taxonomy_path)
    strategies = taxonomy.get("strategies", {})
    fallback = taxonomy.get("fallback_strategy", "uncategorized")

    text_lower = text.lower()
    text_first20 = text_lower[:20]

    # ── 1. brand_first (special: positional check) ────────────────────────────
    brand_kw = strategies.get("brand_first", {}).get("keywords", ["superparty"])
    if any(kw in text_first20 for kw in brand_kw):
        return "brand_first"

    # ── Build sorted strategy list by priority (skip brand_first already done) ─
    ordered = sorted(
        [(name, cfg) for name, cfg in strategies.items() if name != "brand_first"],
        key=lambda x: x[1].get("priority", 99),
    )

    for strategy_name, cfg in ordered:
        keywords = cfg.get("keywords", [])
        if any(kw in text_lower for kw in keywords):
            return strategy_name

    return fallback


def tag_strategy_explain(
    text: str,
    taxonomy_path: Path = TAXONOMY_PATH,
) -> dict:
    """
    Returns tag_strategy result with matched keywords for transparency.
    """
    if not text:
        return {"strategy": "uncategorized", "matched_keywords": [], "text_sample": ""}

    taxonomy = _load_taxonomy(taxonomy_path)
    strategies = taxonomy.get("strategies", {})
    fallback = taxonomy.get("fallback_strategy", "uncategorized")

    text_lower = text.lower()
    text_first20 = text_lower[:20]

    # brand_first
    brand_kw = strategies.get("brand_first", {}).get("keywords", ["superparty"])
    matched = [kw for kw in brand_kw if kw in text_first20]
    if matched:
        return {"strategy": "brand_first", "matched_keywords": matched, "text_sample": text[:60]}

    ordered = sorted(
        [(name, cfg) for name, cfg in strategies.items() if name != "brand_first"],
        key=lambda x: x[1].get("priority", 99),
    )

    for strategy_name, cfg in ordered:
        keywords = cfg.get("keywords", [])
        matched = [kw for kw in keywords if kw in text_lower]
        if matched:
            return {
                "strategy": strategy_name,
                "matched_keywords": matched,
                "text_sample": text[:60],
            }

    return {"strategy": fallback, "matched_keywords": [], "text_sample": text[:60]}


def get_all_strategy_names(taxonomy_path: Path = TAXONOMY_PATH) -> list:
    """Returns all valid strategy names from taxonomy."""
    taxonomy = _load_taxonomy(taxonomy_path)
    names = list(taxonomy.get("strategies", {}).keys())
    fallback = taxonomy.get("fallback_strategy", "uncategorized")
    if fallback not in names:
        names.append(fallback)
    return names
