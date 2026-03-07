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


def validate_action_activation(policy: dict, action_type: str = ACTION_TYPE) -> dict:
    if policy.get("mode") != "controlled_dry_run_only":
        raise PolicyValidationError(
            "Level 5 policy mode must be 'controlled_dry_run_only' in PR #54"
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

    if activation.get("execution_mode") != "dry_run_only":
        raise PolicyValidationError("execution_mode must be 'dry_run_only'")

    if activation.get("report_only") is not True:
        raise PolicyValidationError("report_only must be true")

    if activation.get("write_files") is not False:
        raise PolicyValidationError("write_files must be false")

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
    Conservative candidate extraction from existing reports.
    Derive URLs from health report clusters.
    Consider only clearly non-money, Tier C, non-pillar URLs.
    PR #54: current_meta_description left blank (no page-file reads yet).
    """
    health_clusters = (inputs.get("health") or {}).get("clusters", {})
    candidates: List[Candidate] = []

    for _cluster_id, cluster_data in health_clusters.items():
        urls = cluster_data.get("urls", {}) or {}
        cluster_is_money = is_money_cluster(cluster_data)

        for url, _url_data in urls.items():
            tier = infer_tier_from_url(url)
            pillar = is_pillar_page(url)

            # PR #54: no page file reads yet — keep blank
            current_meta_description = ""

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

    return candidates


def resolve_eligible_candidates(inputs: dict, policy: dict) -> List[Candidate]:
    activation = validate_action_activation(policy, ACTION_TYPE)

    allow_tiers = set(activation.get("tier_allowlist", []))
    deny_tiers = set(activation.get("tier_denylist", []))
    max_candidates = int(activation.get("max_candidates_per_run", 1))

    pool = extract_candidate_pool(inputs)
    eligible: List[Candidate] = []

    for candidate in pool:
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


def generate_dry_run_report(action_type: str = ACTION_TYPE) -> dict:
    if action_type != ACTION_TYPE:
        raise PolicyValidationError(f"Unsupported action type: {action_type}")

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
