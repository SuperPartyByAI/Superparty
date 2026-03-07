"""
tests/test_level5_action_policy.py — PR #53 Level 5 Design Boundary
Validates that level5_action_policy.json satisfies all required invariants
BEFORE any runtime implementation exists.

If these tests fail, PR #54 (first executor) must NOT be opened.
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
    assert "schema_version" in policy, "schema_version este obligatoriu"
    assert policy["schema_version"] == "1.0"


def test_mode_is_design_boundary_only(policy):
    """PR #53 este design boundary ONLY — nicio execuție permisă."""
    assert policy.get("mode") == "design_boundary_only", \
        "mode trebuie sa fie 'design_boundary_only' in PR #53"


# ─── Safety Invariants ────────────────────────────────────────────────────────

def test_allowed_actions_is_empty(policy):
    """PR #53: allowed_actions trebuie sa fie lista goala — nicio actiune activata."""
    assert isinstance(policy.get("allowed_actions"), list), "allowed_actions trebuie sa fie o lista"
    assert len(policy["allowed_actions"]) == 0, \
        "allowed_actions trebuie sa fie [] in PR #53 — nu se activeaza nicio actiune inca"


def test_max_actions_per_run_is_zero(policy):
    """Nicio actiune nu se executa in PR #53."""
    assert policy.get("max_actions_per_run") == 0, \
        "max_actions_per_run trebuie sa fie 0 in PR #53"


def test_dry_run_required(policy):
    assert policy.get("dry_run_required") is True, \
        "dry_run_required trebuie sa fie true"


def test_approval_gate_is_manual(policy):
    assert policy.get("approval_gate") == "manual", \
        "approval_gate trebuie sa fie 'manual' — nu 'automatic'"


def test_rollback_required(policy):
    assert policy.get("rollback_required") is True, \
        "rollback_required trebuie sa fie true"


def test_feedback_loop_is_observability_only(policy):
    assert policy.get("feedback_loop_mode") == "observability_only", \
        "feedback_loop_mode trebuie sa fie 'observability_only'"


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
        assert action in forbidden, f"'{action}' trebuie sa fie explicit in forbidden_actions"


# ─── Tier Restrictions ────────────────────────────────────────────────────────

def test_tier_a_is_read_only(policy):
    """Tier A = read_only este absolut — nicio exceptie permisa."""
    tier_restrictions = policy.get("tier_restrictions", {})
    assert tier_restrictions.get("A") == "read_only", \
        "Tier A trebuie sa fie 'read_only' — absolut, fara exceptii"


def test_tier_b_is_restricted(policy):
    tier_restrictions = policy.get("tier_restrictions", {})
    assert tier_restrictions.get("B") == "restricted"


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
        assert gate in requires_review, \
            f"'{gate}' trebuie sa fie in requires_human_review_for"


# ─── Feedback Loop Signals ────────────────────────────────────────────────────

REQUIRED_PERMITTED_SIGNALS = [
    "impressions", "clicks", "ctr", "average_position",
    "owner_share_delta", "forbidden_delta", "trend_status"
]

def test_permitted_signals_defined(policy):
    signals = policy.get("feedback_loop_permitted_signals", [])
    for sig in REQUIRED_PERMITTED_SIGNALS:
        assert sig in signals, f"Signal permis '{sig}' lipseste din policy"


REQUIRED_FORBIDDEN_CLAIMS = [
    "serp_rank_1_claim",
    "business_outcome_validation_without_real_serp",
    "auto_interpreted_seo_win",
]

def test_forbidden_claims_defined(policy):
    claims = policy.get("feedback_loop_forbidden_claims", [])
    for claim in REQUIRED_FORBIDDEN_CLAIMS:
        assert claim in claims, f"Claim interzis '{claim}' lipseste din policy"


# ─── Low-Risk Eligible — definit dar neactivat ───────────────────────────────

def test_low_risk_eligible_not_in_allowed_actions(policy):
    """
    low_risk_eligible_actions sunt descrise in policy dar NU in allowed_actions.
    Niciun low-risk action nu trebuie sa fie activ in PR #53.
    """
    eligible = policy.get("low_risk_eligible_actions", [])
    allowed = policy.get("allowed_actions", [])
    for action in eligible:
        assert action not in allowed, \
            f"'{action}' este low_risk_eligible dar NU trebuie sa fie in allowed_actions in PR #53"
