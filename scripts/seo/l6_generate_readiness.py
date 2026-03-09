#!/usr/bin/env python3
"""
scripts/seo/l6_generate_readiness.py

CLI: generează Run Readiness Report + Run 2 Candidate Planner.
Rulează zilnic pentru a verifica dacă Run 2 este permis sau nu.

Usage:
  python scripts/seo/l6_generate_readiness.py
  python scripts/seo/l6_generate_readiness.py --verbose
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agent.tasks.seo_level6_run_readiness import generate_run_readiness_report
from agent.tasks.seo_level6_run2_planner import generate_run2_candidates

REPORTS_DIR   = ROOT / "reports" / "superparty"
OUTCOME_MEMORY = REPORTS_DIR / "seo_level6_outcome_memory.json"
PILLAR_REGISTRY = ROOT / "config" / "seo" / "pillar_pages_registry.json"
COOLDOWN_CFG   = ROOT / "config" / "seo" / "auto_apply_cooldown_config.json"

READINESS_PATH  = REPORTS_DIR / "seo_level6_run_readiness.json"
CANDIDATES_PATH = REPORTS_DIR / "seo_level6_run2_candidates.json"

def main():
    verbose = "--verbose" in sys.argv
    
    print("\n╔══════════════════════════════════════════════════╗")
    print("║   L6 Run Readiness + Candidate Planner           ║")
    print("╚══════════════════════════════════════════════════╝\n")

    # 1. Readiness report
    print("─ Run Readiness Report ─")
    readiness = generate_run_readiness_report(
        outcome_memory_path=OUTCOME_MEMORY,
        cooldown_config_path=COOLDOWN_CFG,
        output_path=READINESS_PATH,
    )
    
    status = "✅ PERMIS" if readiness["run2_allowed"] else "🟡 BLOCAT"
    print(f"  Run 2: {status}")
    
    if not readiness["run2_allowed"]:
        for reason in readiness["blocked_reasons"]:
            print(f"    ⛔ {reason}")
    
    print(f"  Deadline observatie: {readiness.get('observation_deadline', 'N/A')[:10] if readiness.get('observation_deadline') else 'N/A'}")
    print(f"  Cooldown activ: {readiness['cooldown_active_urls']}")
    print(f"  URL-uri cu date suficiente: {readiness['urls_with_sufficient_impressions']}")
    print(f"  Actiune recomandata: {readiness['recommended_action']}")
    print(f"  Next check: {readiness['recommended_next_check_at']}")
    print(f"  Raport salvat: {READINESS_PATH.name}\n")

    # 2. Run 2 planner
    print("─ Run 2 Candidate Planner ─")
    candidates = generate_run2_candidates(
        outcome_memory_path=OUTCOME_MEMORY,
        pillar_registry_path=PILLAR_REGISTRY,
        output_path=CANDIDATES_PATH,
        max_candidates=3,
    )
    
    print(f"  Candidati eligibili acum: {candidates['run2_ready_count']}")
    
    if candidates["top_candidates"]:
        print("  Top candidati:")
        for c in candidates["top_candidates"]:
            icon = "✅" if c["eligible_now"] else "⏳"
            print(f"    {icon} {c['url']} → {c['suggested_strategy']} | data: {c['data_quality']} | eligible: {c['earliest_possible_run_date']}")
    else:
        print("  Nicio pagina imediat eligibila. Candidatii sunt blocati:")
        for c in candidates["excluded"][:3]:
            print(f"    ⛔ {c['url']}: {', '.join(c['blocked_reasons'])}")
    
    if candidates.get("provisory_note"):
        print(f"\n  ⚠️  {candidates['provisory_note']}")
    
    print(f"\n  Plan Run 2 salvat: {CANDIDATES_PATH.name}")

    if verbose:
        print("\n─ Detalii complete ─")
        print(json.dumps(readiness, indent=2, ensure_ascii=False))

    print("\n" + "═" * 50)


if __name__ == "__main__":
    main()
