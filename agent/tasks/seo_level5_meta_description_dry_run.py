"""
SEO Level 5 — Meta Description Dry Run Executor (PR #54)

STRICT DRY-RUN ONLY.
- Does NOT modify files
- Does NOT create commits
- Does NOT create PRs
- Does NOT touch Tier A
- Does NOT touch Tier B
- Does NOT touch money pages
- Produces only a machine-readable report:
    reports/superparty/seo_level5_dry_run_actions.json
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = ROOT_DIR / "config" / "seo"
REPORTS_DIR = ROOT_DIR / "reports" / "superparty"

POLICY_PATH = CONFIG_DIR / "level5_action_policy.json"
HEALTH_PATH = REPORTS_DIR / "seo_cluster_health.json"
PRIORITY_PATH = REPORTS_DIR / "seo_cluster_priority.json"
TREND_PATH = REPORTS_DIR / "seo_trend_delta.json"
OUTPUT_PATH = REPORTS_DIR / "seo_level5_dry_run_actions.json"

ACTION_TYPE = "meta_description_update"

# PR #55: import read-only page metadata extractor
try:
    from agent.tasks.seo_level5_page_metadata_extractor import enrich_candidates_with_real_metadata as _enrich
    _EXTRACTOR_AVAILABLE = True
except ImportError:
    _EXTRACTOR_AVAILABLE = False
    log.warning("Page metadata extractor not available — current_meta_description will be blank")


class PolicyValidationError(RuntimeError):
    """Raised when Level 5 policy does not permit the requested dry-run."""


@dataclass
class Candidate:
    url: str
    tier: str
    is_money_page: bool
    is_pillar_page: bool
    current_meta_description: str
    reason_flags: List[str]
    score: float
    # PR #62: True = from health_clusters (proven non-money classification).
    # False = from pages-dir fallback scan (money status unproven — diagnostic only,
    # never eligible for apply).
    health_classified: bool = True


def _load_json(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_level5_policy() -> dict:
    policy = _load_json(POLICY_PATH)
    if not policy:
        raise PolicyValidationError(f"Policy file missing: {POLICY_PATH}")
    return policy


# Modes under which dry-run is permitted to run.
# PR #59: forward-compatible with policy v1.2 (controlled_single_apply) —
# the dry-run phase remains proposal-only regardless of the policy mode.
_DRY_RUN_PERMITTED_MODES = {
    "controlled_dry_run_only",   # policy v1.1
    "controlled_single_apply",  # policy v1.2 — chain is still initiated by dry-run
}

# Execution modes that still represent a dry/proposal-only step.
_DRY_RUN_EXECUTION_MODES = {
    "dry_run_only",     # policy v1.1
    "single_apply_only",  # policy v1.2 — dry-run phase does not execute apply
}


def validate_action_activation(policy: dict, action_type: str = ACTION_TYPE) -> dict:
    mode = policy.get("mode")
    if mode not in _DRY_RUN_PERMITTED_MODES:
        raise PolicyValidationError(
            f"Level 5 policy mode '{mode}' is not permitted for dry-run. "
            f"Allowed: {sorted(_DRY_RUN_PERMITTED_MODES)}"
        )

    allowed_actions = policy.get("allowed_actions", [])
    if action_type not in allowed_actions:
        raise PolicyValidationError(
            f"Action '{action_type}' is not allowed by current policy"
        )

    if policy.get("dry_run_required") is not True:
        raise PolicyValidationError("dry_run_required must be true")

    if policy.get("approval_gate") != "manual":
        raise PolicyValidationError("approval_gate must be 'manual'")

    if policy.get("max_actions_per_run") != 1:
        raise PolicyValidationError("max_actions_per_run must be 1 in PR #54")

    activation = (policy.get("action_activation") or {}).get(action_type)
    if not activation:
        raise PolicyValidationError(
            f"Missing action_activation block for '{action_type}'"
        )

    exec_mode = activation.get("execution_mode")
    if exec_mode not in _DRY_RUN_EXECUTION_MODES:
        raise PolicyValidationError(
            f"execution_mode='{exec_mode}' not recognized. "
            f"Allowed: {sorted(_DRY_RUN_EXECUTION_MODES)}"
        )

    # PR #59: dry-run does NOT require global write_files=False.
    # The policy v1.2 sets write_files=True for the apply executor only.
    # What we MUST verify: dry-run itself never writes — that is enforced
    # in generate_dry_run_report() and save_dry_run_report() (report-only).
    # Cross-phase write guard:
    if activation.get("create_pull_request") is not False:
        raise PolicyValidationError("create_pull_request must be false")

    if activation.get("commit_changes") is not False:
        raise PolicyValidationError("commit_changes must be false")

    return activation


def load_candidate_inputs() -> dict:
    """
    Load existing reports used only for selection/observability.
    This function is intentionally read-only.
    """
    return {
        "health": _load_json(HEALTH_PATH) or {},
        "priority": _load_json(PRIORITY_PATH) or {},
        "trend": _load_json(TREND_PATH) or {},
    }


# ─── Tier + Pillar heuristics ──────────────────────────────────────────────────

_PILLAR_URLS = {
    "/animatori-petreceri-copii",
    "/petreceri/bucuresti",
    "/petreceri/ilfov",
}

_TIER_A_URLS = {
    "/animatori-petreceri-copii",
    "/petreceri/bucuresti",
    "/petreceri/ilfov",
}

_TIER_B_URLS = {
    "/petreceri/sector-1",
    "/petreceri/sector-2",
    "/petreceri/sector-3",
    "/petreceri/sector-4",
    "/petreceri/sector-5",
    "/petreceri/sector-6",
}


def is_pillar_page(url: str) -> bool:
    return url in _PILLAR_URLS


def infer_tier_from_url(url: str) -> str:
    """
    Conservative placeholder.
    If tier cannot be proven as C, treat as ineligible.
    """
    if url in _TIER_A_URLS:
        return "A"
    if url in _TIER_B_URLS:
        return "B"
    return "C"


def is_money_cluster(cluster_data: dict) -> bool:
    return bool(cluster_data.get("is_money_cluster", False))


def description_is_missing_or_weak(current_meta_description: str) -> bool:
    """Conservative deterministic gate."""
    if not current_meta_description:
        return True
    text = current_meta_description.strip()
    if len(text) < 70:
        return True
    if len(text) > 170:
        return True
    return False


def extract_candidate_pool(inputs: dict) -> List[Candidate]:
    """
    Conservative candidate extraction.
    Primary: derive URLs from health report clusters (Level 4 report).
    Fallback (PR #61): when health_clusters is missing/empty, scan src/pages/ directly.
    Considers only Tier C, non-money, non-pillar URLs.
    """
    health_clusters = (inputs.get("health") or {}).get("clusters", {})
    candidates: List[Candidate] = []

    if health_clusters:
        # Primary path: health report clusters available
        for _cluster_id, cluster_data in health_clusters.items():
            urls = cluster_data.get("urls", {}) or {}
            cluster_is_money = is_money_cluster(cluster_data)

            for url, _url_data in urls.items():
                tier = infer_tier_from_url(url)
                pillar = is_pillar_page(url)
                current_meta_description = ""  # enriched later by extractor

                flags: List[str] = []
                if tier == "C":
                    flags.append("tier_c_only")
                if not cluster_is_money:
                    flags.append("non_money_page")
                if not pillar:
                    flags.append("non_pillar_page")
                if description_is_missing_or_weak(current_meta_description):
                    flags.append("description_missing_or_weak")

                score = 0.0
                if tier == "C":
                    score += 10
                if not cluster_is_money:
                    score += 10
                if not pillar:
                    score += 10
                if "description_missing_or_weak" in flags:
                    score += 20

                candidates.append(
                    Candidate(
                        url=url,
                        tier=tier,
                        is_money_page=cluster_is_money,
                        is_pillar_page=pillar,
                        current_meta_description=current_meta_description,
                        reason_flags=flags,
                        score=score,
                    )
                )
    else:
        # Fallback (PR #61): no health report — scan src/pages/ directly for .astro files
        # This is the active path when Level 4 reports are not yet generated.
        log.info("health_clusters empty — using pages-dir fallback scan (PR #61)")
        pages_dir = ROOT_DIR / "src" / "pages"
        try:
            from agent.tasks.seo_level5_page_metadata_extractor import (
                extract_meta_description_from_file,
                url_to_astro_file,
            )
            extractor_available = True
        except ImportError:
            extractor_available = False

        for astro_file in sorted(pages_dir.rglob("*.astro")):
            # Skip dynamic routes ([slug].astro) and layout files
            if "[" in astro_file.name or astro_file.name == "index.astro" and astro_file.parent == pages_dir:
                continue
            # Skip non-content files
            if astro_file.stem.startswith("_"):
                continue

            # Derive canonical URL from file path relative to pages_dir
            rel = astro_file.relative_to(pages_dir)
            if rel.name == "index.astro":
                url = "/" + "/".join(rel.parts[:-1])
            else:
                url = "/" + "/".join(rel.with_suffix("").parts)
            if not url:
                url = "/"

            tier = infer_tier_from_url(url)
            pillar = is_pillar_page(url)
            is_money = False  # conservative: no cluster data available

            # Read real meta description via extractor
            current_meta_description = ""
            if extractor_available:
                try:
                    meta_info = extract_meta_description_from_file(astro_file)
                    current_meta_description = meta_info.get("meta_description") or ""
                except Exception:
                    pass

            flags: List[str] = []
            if tier == "C":
                flags.append("tier_c_only")
            flags.append("non_money_page")  # assumed safe in fallback
            if not pillar:
                flags.append("non_pillar_page")
            if description_is_missing_or_weak(current_meta_description):
                flags.append("description_missing_or_weak")

            score = 0.0
            if tier == "C":
                score += 10
            score += 10  # non_money assumed
            if not pillar:
                score += 10
            if "description_missing_or_weak" in flags:
                score += 20

            candidates.append(
                Candidate(
                    url=url,
                    tier=tier,
                    is_money_page=is_money,
                    is_pillar_page=pillar,
                    current_meta_description=current_meta_description,
                    reason_flags=flags,
                    score=score,
                    health_classified=False,  # PR #62: unproven money status
                )
            )
        log.info("Fallback scan found %d raw candidates from pages-dir (all diagnostic_only)", len(candidates))

    return candidates


def resolve_eligible_candidates(inputs: dict, policy: dict) -> List[Candidate]:
    activation = validate_action_activation(policy, ACTION_TYPE)

    allow_tiers = set(activation.get("tier_allowlist", []))
    deny_tiers = set(activation.get("tier_denylist", []))
    max_candidates = int(activation.get("max_candidates_per_run", 1))

    pool = extract_candidate_pool(inputs)
    eligible: List[Candidate] = []

    for candidate in pool:
        # PR #62: pages-dir fallback candidates are diagnostic_only.
        # Without proven health_clusters classification, money status is unproven — blocked.
        if not candidate.health_classified:
            continue
        if candidate.tier in deny_tiers:
            continue
        if candidate.tier not in allow_tiers:
            continue
        if candidate.is_money_page:
            continue
        if candidate.is_pillar_page:
            continue
        if not description_is_missing_or_weak(candidate.current_meta_description):
            continue

        eligible.append(candidate)

    eligible.sort(key=lambda c: c.score, reverse=True)
    return eligible[:max_candidates]


def build_meta_description_proposal(candidate: Candidate) -> dict:
    """
    Deterministic placeholder proposal.
    Keep PR #54 simple and predictable — no LLM, no free-form generation.
    """
    url_slug = candidate.url.strip("/").replace("/", " • ")
    if not url_slug:
        url_slug = "superparty"

    proposed = (
        f"Descopera informatii utile despre {url_slug} pe SuperParty. "
        f"Continut clar, relevant si usor de parcurs pentru parinti."
    )
    # Keep bounded conservatively
    proposed = proposed[:160].rstrip()
    return {"meta_description": proposed}


def build_action_record(candidate: Candidate, policy: dict) -> dict:
    return {
        "action_id": (
            f"mdesc-dryrun-{candidate.url.strip('/').replace('/', '-') or 'root'}"
        ),
        "action_type": ACTION_TYPE,
        "status": "proposed_only",
        "tier": candidate.tier,
        "is_money_page": candidate.is_money_page,
        "is_pillar_page": candidate.is_pillar_page,
        "url": candidate.url,
        "eligibility": {
            "tier_allowed": candidate.tier == "C",
            "money_page_allowed": False,
            "manual_review_required_before_apply": True,
            "dry_run_required": True,
        },
        "before": {
            "meta_description": candidate.current_meta_description,
        },
        "proposal": build_meta_description_proposal(candidate),
        "reasoning": {
            "why_selected": candidate.reason_flags,
            "why_safe": [
                "no_runtime_apply",
                "dry_run_only",
                "single_candidate",
            ],
        },
        "feedback_tracking": {
            "allowed_signals": policy.get("feedback_loop_permitted_signals", []),
            "forbidden_claims": policy.get("feedback_loop_forbidden_claims", []),
        },
    }


from agent.tasks.seo_level6_report_readiness import assert_inputs_ready, ReportReadinessError

def generate_dry_run_report(action_type: str = ACTION_TYPE) -> dict:
    if action_type != ACTION_TYPE:
        raise PolicyValidationError(f"Unsupported action type: {action_type}")

    # [L6.1] Input Integrity & Freshness Gate
    # Strict fail-closed if source reports are stale, invalid, or missing.
    try:
        readiness_status = assert_inputs_ready()
        log.info(f"Input reports readiness: {readiness_status['status']}")
    except ReportReadinessError as e:
        log.error(f"BLOCKED BY REPORTS FRESHNESS GATE: {e}")
        raise

    policy = load_level5_policy()
    validate_action_activation(policy, action_type)

    inputs = load_candidate_inputs()
    candidates = resolve_eligible_candidates(inputs, policy)

    # PR #55: enrich candidates with real meta description from Astro source files (read-only)
    if _EXTRACTOR_AVAILABLE and candidates:
        candidate_dicts = [
            {"url": c.url, "tier": c.tier, "is_money_page": c.is_money_page,
             "is_pillar_page": c.is_pillar_page, "current_meta_description": c.current_meta_description,
             "reason_flags": c.reason_flags, "score": c.score}
            for c in candidates
        ]
        enriched = _enrich(candidate_dicts)
        # Update candidates with real descriptions
        from agent.tasks.seo_level5_meta_description_dry_run import Candidate
        candidates = [
            Candidate(
                url=e["url"],
                tier=e["tier"],
                is_money_page=e["is_money_page"],
                is_pillar_page=e["is_pillar_page"],
                current_meta_description=e.get("current_meta_description", ""),
                reason_flags=e["reason_flags"],
                score=e["score"],
            )
            for e in enriched
        ]

    actions = [build_action_record(c, policy) for c in candidates]

    return {
        "metadata": {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": "dry_run_only",
            "policy_version": policy.get("schema_version", ""),
            "action_type": action_type,
            "total_candidates": len(actions),
            "applied": 0,
            "extractor_active": _EXTRACTOR_AVAILABLE,
        },
        "actions": actions,
    }


def save_dry_run_report(report: dict) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log.info("Level 5 dry-run report written to %s", OUTPUT_PATH)


def run_meta_description_dry_run() -> bool:
    try:
        report = generate_dry_run_report(ACTION_TYPE)
        save_dry_run_report(report)
        print(
            f"Level 5 dry-run complete: "
            f"{report['metadata']['total_candidates']} proposed, "
            f"{report['metadata']['applied']} applied."
        )
        return True
    except PolicyValidationError as e:
        log.error("Policy validation failed: %s", e)
        print(f"Level 5 dry-run blocked by policy: {e}")
        return False
    except Exception as e:
        log.exception("Unexpected dry-run failure")
        print(f"Level 5 dry-run failed: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_meta_description_dry_run()
