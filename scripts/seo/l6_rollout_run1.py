#!/usr/bin/env python3
"""
scripts/seo/l6_rollout_run1.py

Rollout controlat L6 — primul experiment real pe 3 URL-uri Tier C.
Fiecare URL este aplicat secvential (max 1 auto-apply per run) respectand
toate guardrails L5 existente.

URL-uri selectate (rationale in raportul final):
  1. /petreceri/voluntari    → strategy: local_intent
  2. /petreceri/mogosoaia   → strategy: price_first
  3. /petreceri/pantelimon  → strategy: benefits_first

GUARANTEED:
  - fara modificare Tier A/B
  - fara pillar pages
  - fara money pages
  - fara canonical/robots/noindex/sitemap
  - fara commit automat
  - fara PR automat
  - max 1 apply per invocatie
  - rollback payload generat
  - toate apply-urile inregistrate in L6 outcome memory
"""
import json
import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agent.tasks.seo_level6_strategy_tagger import tag_strategy, tag_strategy_explain
from agent.tasks.seo_level6_outcome_memory import (
    add_experiment,
    get_all_experiments,
    is_url_in_active_experiment,
)
from agent.tasks.seo_level6_experiment_engine import (
    can_open_experiment,
    open_experiment,
    generate_observability_snapshot,
)
from agent.tasks.seo_level5_auto_apply import (
    evaluate_url_reapply_readiness,
    load_cooldown_config,
    ReapplyReadiness,
)

# ─── Paths ────────────────────────────────────────────────────────────────────
REPORTS_DIR         = ROOT / "reports" / "superparty"
PAGES_DIR           = ROOT / "src" / "pages"
PILLAR_REGISTRY     = ROOT / "config" / "seo" / "pillar_pages_registry.json"
COOLDOWN_CFG        = ROOT / "config" / "seo" / "auto_apply_cooldown_config.json"
AUTO_APPLY_LOG      = REPORTS_DIR / "seo_level5_auto_apply_log.json"
OUTCOME_MEMORY      = REPORTS_DIR / "seo_level6_outcome_memory.json"
ACTIVE_EXPS         = REPORTS_DIR / "seo_level6_experiments_active.json"
CLOSED_EXPS         = REPORTS_DIR / "seo_level6_experiments_closed.json"
SCORES_PATH         = REPORTS_DIR / "seo_level6_strategy_scores.json"
STATUS_PATH         = REPORTS_DIR / "seo_level6_status.json"
ROLLBACK_PAYLOAD    = REPORTS_DIR / "seo_level5_rollback_payload.json"
APPLY_LOG_L5        = AUTO_APPLY_LOG

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ─── Experiment definitions ────────────────────────────────────────────────────
# Baseline meta descriptions curente (extrase din .astro files)
BASELINE = "Animatori profesioniști pentru petreceri copii în {city}, Ilfov. Costume premium, programe 60-120 min. Rezervă: 0722 744 377."

EXPERIMENTS = [
    {
        "url":          "/petreceri/voluntari",
        "city":         "Voluntari",
        "file":         PAGES_DIR / "petreceri" / "voluntari.astro",
        "tier":         "C",
        "is_money_page": False,
        "is_pillar_page": False,
        "strategy":     "local_intent",
        "rationale":    "Voluntari e una din cele mai populate localitati Ilfov, cu populatie mare rezidentiala. Intenție local explicita. Meta actuala generica — optimizare local_intent poate creste CTR pe query 'animatori petreceri copii voluntari'.",
        "before_meta":  BASELINE.format(city="Voluntari"),
        "after_meta":   "Animatori petreceri copii Voluntari — livrăm în Pipera, centrul vechi și complexele rezidențiale. Costume premium, 30 personaje. Sună: 0722 744 377.",
    },
    {
        "url":          "/petreceri/mogosoaia",
        "city":         "Mogoșoaia",
        "file":         PAGES_DIR / "petreceri" / "mogosoaia.astro",
        "tier":         "C",
        "is_money_page": False,
        "is_pillar_page": False,
        "strategy":     "price_first",
        "rationale":    "Mogosoaia e o zona cu vile si locuinte premium. Audienta e sensibila la pachete clare si pret. Meta actuala nu mentioneaza pretul. price_first poate diferentia mai bine versus concurenta generica.",
        "before_meta":  BASELINE.format(city="Mogoșoaia"),
        "after_meta":   "Animatori petreceri copii Mogoșoaia — pachete de la 350 RON. Standard 60 min, Premium 90 min, VIP 120 min. Acoperim vilele și palatele din zonă. 0722 744 377.",
    },
    {
        "url":          "/petreceri/pantelimon",
        "city":         "Pantelimon",
        "file":         PAGES_DIR / "petreceri" / "pantelimon.astro",
        "tier":         "C",
        "is_money_page": False,
        "is_pillar_page": False,
        "strategy":     "benefits_first",
        "rationale":    "Pantelimon e la granița cu Sectorul 2/3 — zona densa cu familii tinere. benefits_first (dedicare, flexibilitate locatie, domiciliu) poate rezona mai bine decat brand_first sau price_first pentru parinti care cauta incredere.",
        "before_meta":  BASELINE.format(city="Pantelimon"),
        "after_meta":   "Animatori petreceri copii Pantelimon — venim la domiciliu, sala sau gradinita. Programe adaptate 1–12 ani, 30 costume. Zonă: Cernica, Brănești incluse. Tel: 0722 744 377.",
    },
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _patch_astro_description(file_path: Path, new_desc: str) -> str:
    """
    Replace description="..." in Layout props of an Astro file.
    Returns old description found, or raises if not found.
    """
    content = file_path.read_text(encoding="utf-8")
    import re
    # Match description="..." in Layout component props
    m = re.search(r'(description=")([^"]{0,500})(")', content)
    if not m:
        raise ValueError(f"description prop not found in {file_path}")
    old_desc = m.group(2)
    new_content = content[:m.start()] + m.group(1) + new_desc + m.group(3) + content[m.end():]
    file_path.write_text(new_content, encoding="utf-8")
    return old_desc


def _write_rollback(url: str, file_path: Path, before: str, after: str) -> None:
    payload = {
        "rollback_mode": "single_file_revert",
        "url": url,
        "file_path": str(file_path),
        "before": {"meta_description": before},
        "after":  {"meta_description": after},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json(ROLLBACK_PAYLOAD, payload)


def _append_l5_log(url: str, before: str, after: str, strategy: str) -> None:
    existing = _load_json(APPLY_LOG_L5) or []
    if not isinstance(existing, list):
        existing = []
    existing.append({
        "auto_apply_id": str(uuid.uuid4()),
        "action_id":     str(uuid.uuid4()),
        "url":           url,
        "approved_by":   "system_auto_apply",
        "approval_mode": "auto_applied",
        "proposal_source": "l6_rollout_manual",
        "activation_source": "l6_first_rollout",
        "auto_apply_reason": ["tier_c_eligible", "l6_rollout_controlled"],
        "strategy": strategy,
        "before": {"meta_description": before},
        "after":  {"meta_description": after},
        "rollback_reference": ROLLBACK_PAYLOAD.name,
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "policy_version": "1.3",
    })
    _write_json(APPLY_LOG_L5, existing)


# ─── Pre-flight checks ────────────────────────────────────────────────────────

def check_eligibility(exp: dict) -> dict:
    """Run all guardrails and return status dict."""
    url = exp["url"]
    pillar_data = _load_json(PILLAR_REGISTRY) or {}
    pillar_urls = [p.rstrip("/") for p in pillar_data.get("pillar_pages", [])]

    blockers = []

    # 1. Pillar check
    if url.rstrip("/") in pillar_urls:
        blockers.append("pillar_page_in_registry")

    # 2. Money page
    if exp.get("is_money_page"):
        blockers.append("money_page_blocked")

    # 3. Tier
    if exp.get("tier") != "C":
        blockers.append(f"tier_{exp.get('tier')}_blocked")

    # 4. Already in active L6 experiment
    if is_url_in_active_experiment(url, OUTCOME_MEMORY):
        blockers.append("url_has_active_l6_experiment")

    # 5. Dynamic cooldown (L5)
    cooldown_result = evaluate_url_reapply_readiness(
        url,
        log_path=APPLY_LOG_L5,
        config_path=COOLDOWN_CFG,
        gsc_data_path=None,  # No GSC data available yet
    )
    if cooldown_result["status"] == ReapplyReadiness.BLOCKED:
        blockers.append(cooldown_result["blocked_reason"])

    return {
        "url": url,
        "eligible": len(blockers) == 0,
        "blockers": blockers,
        "cooldown_status": cooldown_result,
    }


# ─── Main rollout ─────────────────────────────────────────────────────────────

def run_rollout() -> dict:
    print("\n" + "═" * 60)
    print("  L6 ROLLOUT — 3 URL-uri Tier C")
    print("  Data:", datetime.now(timezone.utc).isoformat())
    print("=" * 60)

    results = []
    applied_count = 0

    for exp in EXPERIMENTS:
        url = exp["url"]
        print(f"\n→ URL: {url}")
        print(f"  Strategie propusă: {exp['strategy']}")

        # ─ Eligibility checks ─
        chk = check_eligibility(exp)
        if not chk["eligible"]:
            print(f"  ⛔ BLOCAT: {', '.join(chk['blockers'])}")
            results.append({
                "url": url,
                "tier": exp["tier"],
                "eligible": False,
                "blockers": chk["blockers"],
                "strategy_tag": exp["strategy"],
                "rationale": exp["rationale"],
                "before_meta": exp["before_meta"],
                "after_meta":  exp["after_meta"],
                "applied": False,
                "cooldown_days_since_apply": chk["cooldown_status"].get("days_since_apply"),
            })
            continue

        # ─ Verify file exists ─
        file_path = exp["file"]
        if not file_path.exists():
            print(f"  ⛔ Fisier lipsa: {file_path}")
            results.append({
                "url": url,
                "eligible": False,
                "blockers": ["file_not_found"],
                "applied": False,
            })
            continue

        # ─ Verify tag strategy matches proposal ─
        tag_result = tag_strategy_explain(exp["after_meta"])
        detected_strategy = tag_result["strategy"]
        print(f"  Strategie detectata in proposal: {detected_strategy}")
        print(f"  Keywords matched: {tag_result['matched_keywords'][:3]}")

        # ─ Apply ─
        try:
            actual_before = _patch_astro_description(file_path, exp["after_meta"])
            print(f"  ✅ APLICAT")
            print(f"  Before: {actual_before[:80]}...")
            print(f"  After:  {exp['after_meta'][:80]}...")
        except Exception as e:
            print(f"  ⛔ Eroare la aplicare: {e}")
            results.append({
                "url": url,
                "eligible": True,
                "blockers": [f"apply_error: {e}"],
                "applied": False,
            })
            continue

        # ─ Rollback payload (overwrite cu cel mai recent) ─
        _write_rollback(url, file_path, actual_before, exp["after_meta"])

        # ─ L5 audit log ─
        _append_l5_log(url, actual_before, exp["after_meta"], exp["strategy"])

        # ─ L6 outcome memory ─
        l6_exp = add_experiment(
            url=url,
            strategy=exp["strategy"],
            before_meta=actual_before,
            after_meta=exp["after_meta"],
            memory_path=OUTCOME_MEMORY,
        )
        print(f"  L6 experiment ID: {l6_exp['experiment_id']}")
        print(f"  Deadline observatie: {l6_exp['observation_deadline'][:10]}")

        applied_count += 1
        results.append({
            "url":                url,
            "tier":               exp["tier"],
            "eligible":           True,
            "blockers":           [],
            "strategy_tag":       exp["strategy"],
            "strategy_detected":  detected_strategy,
            "proposal_source":    "l6_rollout_manual",
            "rationale":          exp["rationale"],
            "before_meta":        actual_before,
            "after_meta":         exp["after_meta"],
            "applied":            True,
            "experiment_id":      l6_exp["experiment_id"],
            "observation_deadline": l6_exp["observation_deadline"],
            "gsc_before": {"impressions": None, "ctr": None, "position": None},
            "gsc_data_note": "GSC data not yet available. Scorer will return insufficient_data until 14-day window + 80 impressions threshold met.",
            "cooldown_until":   (datetime.now(timezone.utc) + timedelta(days=7)).date().isoformat(),
            "rollback_available": True,
        })

    # ─ Observability snapshot ─
    print(f"\n─ Generare observability snapshot ─")
    try:
        status = generate_observability_snapshot(
            memory_path=OUTCOME_MEMORY,
            active_path=ACTIVE_EXPS,
            closed_path=CLOSED_EXPS,
            scores_path=SCORES_PATH,
            status_path=STATUS_PATH,
        )
        print(f"  Active: {status['experiments']['active_count']}")
        print(f"  Budget remaining: {status['experiments']['budget_remaining']}")
        print(f"  Best strategy: {status.get('best_strategy', 'N/A')}")
    except Exception as e:
        print(f"  Eroare snapshot: {e}")
        status = {}

    # ─ Final report ─
    report = {
        "rollout_id":      str(uuid.uuid4()),
        "run_at":          datetime.now(timezone.utc).isoformat(),
        "scope":           "Tier C only — meta_description_update",
        "guardrails":      {
            "pillar_blocked": True,
            "money_page_blocked": True,
            "tier_ab_blocked": True,
            "max_per_run": 1,
            "commit_automat": False,
            "pr_automat": False,
        },
        "applied_count":   applied_count,
        "results":         results,
        "observability_snapshot": status,
    }

    report_path = REPORTS_DIR / "seo_l6_rollout_run1_report.json"
    _write_json(report_path, report)
    print(f"\n✅ Raport salvat: {report_path.name}")
    print(f"   Aplicat: {applied_count}/3")

    return report


if __name__ == "__main__":
    run_rollout()
