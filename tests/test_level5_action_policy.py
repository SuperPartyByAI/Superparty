"""
tests/test_level5_action_policy.py — PR #54 Level 5 Dry-Run Activation

Valideaza ca policy-ul pentru PR #54:
- activeaza EXCLUSIV meta_description_update
- ramane dry-run only
- nu permite Tier A / Tier B
- nu permite money pages / pillar pages / registry touches
- limiteaza executia la max 1 candidat per run
"""

import json
import pytest
from pathlib import Path

POLICY_PATH = Path(__file__).parent.parent / "config" / "seo" / "level5_action_policy.json"


@pytest.fixture(scope="module")
def policy():
    assert POLICY_PATH.exists(), f"Policy file missing: {POLICY_PATH}"
    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ─── Schema & Mode ────────────────────────────────────────────────────────────

def test_schema_version_present(policy):
    assert "schema_version" in policy
    assert policy["schema_version"] == "1.1"


def test_mode_is_controlled_dry_run_only(policy):
    assert policy.get("mode") == "controlled_dry_run_only", (
        "PR #54 trebuie sa fie controlled_dry_run_only"
    )


# ─── Safety Invariants ────────────────────────────────────────────────────────

def test_allowed_actions_is_only_meta_description_update(policy):
    allowed = policy.get("allowed_actions")
    assert isinstance(allowed, list), "allowed_actions trebuie sa fie lista"
    assert allowed == ["meta_description_update"], (
        "PR #54 activeaza EXCLUSIV meta_description_update"
    )


def test_max_actions_per_run_is_one(policy):
    assert policy.get("max_actions_per_run") == 1, (
        "max_actions_per_run trebuie sa fie 1 in PR #54"
    )


def test_dry_run_required(policy):
    assert policy.get("dry_run_required") is True


def test_approval_gate_is_manual(policy):
    assert policy.get("approval_gate") == "manual"


def test_rollback_required(policy):
    assert policy.get("rollback_required") is True


def test_feedback_loop_is_observability_only(policy):
    assert policy.get("feedback_loop_mode") == "observability_only"


# ─── Forbidden Actions ────────────────────────────────────────────────────────

REQUIRED_FORBIDDEN = [
    "change_canonical",
    "change_robots",
    "change_noindex",
    "change_registry",
    "change_cluster_schema",
    "change_internal_ownership",
    "modify_pillar_page",
    "modify_sitemap_policy",
]


def test_forbidden_actions_present(policy):
    forbidden = policy.get("forbidden_actions", [])
    for action in REQUIRED_FORBIDDEN:
        assert action in forbidden, f"'{action}' trebuie sa fie in forbidden_actions"


# ─── Tier Restrictions ────────────────────────────────────────────────────────

def test_tier_a_is_read_only(policy):
    tier_restrictions = policy.get("tier_restrictions", {})
    assert tier_restrictions.get("A") == "read_only", (
        "Tier A trebuie sa ramana read_only"
    )


def test_tier_b_is_restricted(policy):
    tier_restrictions = policy.get("tier_restrictions", {})
    assert tier_restrictions.get("B") == "restricted", (
        "Tier B nu trebuie activat in PR #54"
    )


def test_tier_c_is_low_risk_eligible(policy):
    tier_restrictions = policy.get("tier_restrictions", {})
    assert tier_restrictions.get("C") == "low_risk_eligible"


# ─── Human Review Gates ───────────────────────────────────────────────────────

REQUIRED_REVIEW_GATES = [
    "all_tier_a",
    "all_money_pages",
    "all_registry_touches",
]


def test_human_review_gates_present(policy):
    requires_review = policy.get("requires_human_review_for", [])
    for gate in REQUIRED_REVIEW_GATES:
        assert gate in requires_review, (
            f"'{gate}' trebuie sa fie in requires_human_review_for"
        )


# ─── Feedback Loop Signals ────────────────────────────────────────────────────

REQUIRED_PERMITTED_SIGNALS = [
    "impressions", "clicks", "ctr", "average_position",
    "owner_share_delta", "forbidden_delta", "trend_status",
]


def test_permitted_signals_defined(policy):
    signals = policy.get("feedback_loop_permitted_signals", [])
    for sig in REQUIRED_PERMITTED_SIGNALS:
        assert sig in signals, f"Signal permis '{sig}' lipseste"


REQUIRED_FORBIDDEN_CLAIMS = [
    "serp_rank_1_claim",
    "business_outcome_validation_without_real_serp",
    "auto_interpreted_seo_win",
]


def test_forbidden_claims_defined(policy):
    claims = policy.get("feedback_loop_forbidden_claims", [])
    for claim in REQUIRED_FORBIDDEN_CLAIMS:
        assert claim in claims, f"Claim interzis '{claim}' lipseste"


# ─── Low-Risk Eligible / Allowed ─────────────────────────────────────────────

def test_low_risk_eligible_contains_meta_title_and_meta_description(policy):
    eligible = policy.get("low_risk_eligible_actions", [])
    assert "meta_title_update" in eligible
    assert "meta_description_update" in eligible


def test_only_meta_description_is_activated_now(policy):
    eligible = policy.get("low_risk_eligible_actions", [])
    allowed = policy.get("allowed_actions", [])
    assert "meta_description_update" in allowed
    assert "meta_title_update" in eligible
    assert "meta_title_update" not in allowed, (
        "meta_title_update ramane neactivat in PR #54"
    )


# ─── Action Activation Block ──────────────────────────────────────────────────

def test_action_activation_block_exists(policy):
    activation = policy.get("action_activation", {})
    assert "meta_description_update" in activation, (
        "PR #54 trebuie sa defineasca action_activation pentru meta_description_update"
    )


def test_meta_description_update_is_dry_run_only(policy):
    cfg = policy["action_activation"]["meta_description_update"]
    assert cfg.get("execution_mode") == "dry_run_only"
    assert cfg.get("report_only") is True
    assert cfg.get("write_files") is False
    assert cfg.get("create_pull_request") is False
    assert cfg.get("commit_changes") is False


def test_meta_description_update_is_tier_c_only(policy):
    cfg = policy["action_activation"]["meta_description_update"]
    assert cfg.get("tier_allowlist") == ["C"]
    assert "A" in cfg.get("tier_denylist", [])
    assert "B" in cfg.get("tier_denylist", [])


def test_meta_description_update_forbids_money_and_pillar_pages(policy):
    cfg = policy["action_activation"]["meta_description_update"]
    assert cfg.get("money_pages") == "forbidden"
    assert cfg.get("pillar_pages") == "forbidden"
    assert cfg.get("registry_touches") == "forbidden"


def test_meta_description_update_requires_manual_approval_before_apply(policy):
    cfg = policy["action_activation"]["meta_description_update"]
    assert cfg.get("requires_manual_approval_before_apply") is True


def test_meta_description_update_limits_to_one_candidate(policy):
    cfg = policy["action_activation"]["meta_description_update"]
    assert cfg.get("max_candidates_per_run") == 1
