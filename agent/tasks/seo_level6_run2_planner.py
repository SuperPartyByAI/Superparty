"""
agent/tasks/seo_level6_run2_planner.py

Run 2 Candidate Planner — L6 Learning Loop

Generează shortlist read-only de URL-uri Tier C candidate pentru Run 2,
cu justificare detaliată și earliest_possible_run_date.

Nu aplică nimic. Nu modifică paginile. Pur planificare.

Reguli de selecție:
  - doar Tier C
  - exclude pillar pages
  - exclude money pages
  - exclude URL-uri cu rollback recent
  - exclude URL-uri în experiment activ
  - exclude URL-uri în cooldown activ
  - prioritizează: impresii existente + CTR slab + poziție mediocra
  - dacă nu există date GSC, marchează data_quality: "insufficient"
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent

MIN_IMPRESSIONS_NICE = 80   # pragul minim pentru date utile
MIN_REAPPLY_DAYS = 7        # cooldown minim


def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_pillar_urls(pillar_registry_path: Path) -> set:
    data = _load_json(pillar_registry_path)
    if not data:
        return set()
    return {u.rstrip("/") for u in data.get("pillar_pages", [])}


def _active_experiment_urls(outcome_memory_path: Path) -> set:
    experiments = _load_json(outcome_memory_path) or []
    return {
        e["url"].rstrip("/")
        for e in experiments
        if e.get("result_label") == "pending"
    }


def _rollback_urls(outcome_memory_path: Path) -> set:
    experiments = _load_json(outcome_memory_path) or []
    return {
        e["url"].rstrip("/")
        for e in experiments
        if e.get("rollback_happened", False)
    }


def _cooldown_active_urls(outcome_memory_path: Path, min_reapply_days: int, now: datetime) -> set:
    experiments = _load_json(outcome_memory_path) or []
    active = set()
    for exp in experiments:
        if exp.get("result_label") != "pending":
            continue
        applied_at = exp.get("applied_at", "")
        if not applied_at:
            continue
        applied_dt = datetime.fromisoformat(applied_at)
        if applied_dt.tzinfo is None:
            applied_dt = applied_dt.replace(tzinfo=timezone.utc)
        days_since = (now - applied_dt).total_seconds() / 86400
        if days_since < min_reapply_days:
            active.add(exp["url"].rstrip("/"))
    return active


def _earliest_run_date(
    url: str,
    outcome_memory_path: Path,
    min_reapply_days: int,
    now: datetime,
) -> str:
    """Calculează cea mai devreme dată la care URL-ul devine eligibil."""
    experiments = _load_json(outcome_memory_path) or []
    active_exps = [e for e in experiments if e.get("url") == url and e.get("result_label") == "pending"]
    
    if not active_exps:
        return now.date().isoformat()  # imediat eligible
    
    latest_apply = max(e.get("applied_at", "") for e in active_exps)
    applied_dt = datetime.fromisoformat(latest_apply)
    if applied_dt.tzinfo is None:
        applied_dt = applied_dt.replace(tzinfo=timezone.utc)
    
    # Cea mai tarzie dintre: cooldown_lifted si observation_deadline
    cooldown_lifted = applied_dt + timedelta(days=min_reapply_days)
    deadlines = [
        datetime.fromisoformat(e.get("observation_deadline", ""))
        for e in active_exps
        if e.get("observation_deadline")
    ]
    if deadlines:
        latest_deadline = max(deadlines)
        if latest_deadline.tzinfo is None:
            latest_deadline = latest_deadline.replace(tzinfo=timezone.utc)
        earliest = max(cooldown_lifted, latest_deadline)
    else:
        earliest = cooldown_lifted
    
    return earliest.date().isoformat()


# ─── Catalog Tier C URLs pentru Run 2 ─────────────────────────────────────────
# Lista statica de URL-uri Tier C eligibile pentru experimente L6
# (expandabila manual sau din pipeline)

TIER_C_CATALOG = [
    {
        "url": "/petreceri/otopeni",
        "tier": "C",
        "is_money_page": False,
        "suggested_strategy": "local_intent",
        "selection_rationale": (
            "Otopeni = zona aeroport, inalta cerere pentru animatori si evenimente. "
            "Meta actuala generica, fara mentionarea zonei specifice. "
            "local_intent poate diferentia fata de concurenta prin zone (aproape aeroport, etc.)."
        ),
        "gsc_data": None,  # Se populeaza daca exista date GSC
    },
    {
        "url": "/petreceri/popesti-leordeni",
        "tier": "C",
        "is_money_page": False,
        "suggested_strategy": "services_list",
        "selection_rationale": (
            "Popesti-Leordeni: zona populata la granita Sector 4, familii tinere. "
            "services_list nu a fost testata in Run 1 — oportunitate de a testa o strategie noua. "
            "Parinti cauta frecvent activitati specifice (baloane, face painting) = services_list relevant."
        ),
        "gsc_data": None,
    },
    {
        "url": "/petreceri/chitila",
        "tier": "C",
        "is_money_page": False,
        "suggested_strategy": "benefits_first",
        "selection_rationale": (
            "Chitila: zona industriala-rezidentiala in expansiune. "
            "Familii care cauta valoare, nu pret. benefits_first (venim la tine, adaptam) "
            "mai relevant decat price_first pentru profil demografic."
        ),
        "gsc_data": None,
    },
    {
        "url": "/petreceri/bragadiru",
        "tier": "C",
        "is_money_page": False,
        "suggested_strategy": "price_first",
        "selection_rationale": (
            "Bragadiru: zona cu venituri medii, sensibila la pret. "
            "price_first a functionat in Run 1 pe mogosoaia (nu a primit date inca). "
            "Bragadiru e candidat natural pentru confirmarea strategiei price_first."
        ),
        "gsc_data": None,
    },
    {
        "url": "/petreceri/buftea",
        "tier": "C",
        "is_money_page": False,
        "suggested_strategy": "local_intent",
        "selection_rationale": (
            "Buftea: oras cu identitate locala puternica, studiouri de film. "
            "Audienta locala apreciaza referinte geografice concrete. local_intent evident."
        ),
        "gsc_data": None,
    },
    # URL-uri din Run 1 — reeligibile dupa inchiderea ferestrei
    {
        "url": "/petreceri/voluntari",
        "tier": "C",
        "is_money_page": False,
        "suggested_strategy": "local_intent",
        "selection_rationale": "Run 1 ongoing. Re-eligibil dupa deadline 23 martie.",
        "gsc_data": None,
    },
    {
        "url": "/petreceri/mogosoaia",
        "tier": "C",
        "is_money_page": False,
        "suggested_strategy": "price_first",
        "selection_rationale": "Run 1 ongoing. Re-eligibil dupa deadline 23 martie.",
        "gsc_data": None,
    },
    {
        "url": "/petreceri/pantelimon",
        "tier": "C",
        "is_money_page": False,
        "suggested_strategy": "benefits_first",
        "selection_rationale": "Run 1 ongoing. Re-eligibil dupa deadline 23 martie.",
        "gsc_data": None,
    },
]


def generate_run2_candidates(
    outcome_memory_path: Path,
    pillar_registry_path: Path,
    output_path: Optional[Path] = None,
    min_reapply_days: int = MIN_REAPPLY_DAYS,
    now: Optional[datetime] = None,
    max_candidates: int = 3,
) -> dict:
    """
    Generează shortlist Run 2 candidates cu gating complet.

    Returns dict cu:
      candidates: lista de candidati propusi (max max_candidates)
      excluded: lista de URL-uri excluse cu motiv
      run2_ready_count: cate URL-uri sunt imediat eligibile
    """
    if now is None:
        now = datetime.now(timezone.utc)

    pillar_urls = _load_pillar_urls(pillar_registry_path)
    active_urls = _active_experiment_urls(outcome_memory_path)
    rollback_urls_set = _rollback_urls(outcome_memory_path)
    cooldown_urls = _cooldown_active_urls(outcome_memory_path, min_reapply_days, now)

    candidates = []
    excluded = []

    for item in TIER_C_CATALOG:
        url = item["url"].rstrip("/")
        blockers = []

        # Guardrails
        if url in pillar_urls:
            blockers.append("pillar_page_blocked")
        if item.get("is_money_page"):
            blockers.append("money_page_blocked")
        if url in rollback_urls_set:
            blockers.append("rollback_recent")
        if url in active_urls:
            blockers.append("active_experiment_in_progress")
        if url in cooldown_urls:
            blockers.append("cooldown_active")

        eligible_now = len(blockers) == 0
        earliest = _earliest_run_date(url, outcome_memory_path, min_reapply_days, now)

        # Data quality
        gsc = item.get("gsc_data")
        if gsc and gsc.get("impressions") is not None and gsc.get("impressions") >= MIN_IMPRESSIONS_NICE:
            data_quality = "good"
        elif gsc and gsc.get("impressions") is not None:
            data_quality = "limited"
        else:
            data_quality = "insufficient"

        entry = {
            "url": url,
            "tier": item.get("tier", "C"),
            "suggested_strategy": item["suggested_strategy"],
            "selection_reason": item["selection_rationale"],
            "data_quality": data_quality,
            "gsc_impressions": gsc.get("impressions") if gsc else None,
            "gsc_ctr": gsc.get("ctr") if gsc else None,
            "gsc_position": gsc.get("position") if gsc else None,
            "eligible_now": eligible_now,
            "blocked_reasons": blockers,
            "earliest_possible_run_date": earliest,
        }

        if eligible_now:
            candidates.append(entry)
        else:
            excluded.append(entry)

    # Sortare: data_quality desc, earliest asc
    quality_order = {"good": 0, "limited": 1, "insufficient": 2}
    candidates.sort(key=lambda x: (quality_order.get(x["data_quality"], 3), x["earliest_possible_run_date"]))
    top_candidates = candidates[:max_candidates]

    # Nota daca nu se pot selecta 3
    provisory_note = None
    if len(candidates) < max_candidates:
        provisory_note = (
            f"Numai {len(candidates)} candidati sunt imediat eligibili (din {max_candidates} dorite). "
            f"Restul sunt blocati: verifica 'excluded' pentru detalii si date_quality."
        )

    result = {
        "generated_at": now.isoformat(),
        "max_candidates_requested": max_candidates,
        "run2_ready_count": len(candidates),
        "top_candidates": top_candidates,
        "all_eligible": candidates,
        "excluded": excluded,
        "provisory_note": provisory_note,
        "guardrails_applied": [
            "pillar_page_blocked",
            "money_page_blocked",
            "rollback_recent",
            "active_experiment_in_progress",
            "cooldown_active",
        ],
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    return result
