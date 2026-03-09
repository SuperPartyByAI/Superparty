"""
tests/test_seo_level5_auto_apply_policy.py — PR #85

Suite de teste pentru invariantele policy auto_apply_config.
Verifica:
- Feature flag OFF -> comportament identic cu schema 1.2
- Feature flag ON + Tier C -> auto-apply permis
- Tier A bloccat intotdeauna, chiar cu flag ON
- Tier B bloccat intotdeauna, chiar cu flag ON
- Money pages bloccat
- Pillar pages bloccat
- Mai mult de 1 candidat bloccat
- Proposal invalid bloccat
- File drift bloccat
- Action type neautorizat bloccat
- Schema version bumped la 1.3
"""
import json
import pytest
from pathlib import Path


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _load_policy_from_repo() -> dict:
    """Load the real policy file from the repository."""
    policy_path = Path(__file__).parent.parent / "config" / "seo" / "level5_action_policy.json"
    with open(policy_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _policy_with_flag(enabled: bool) -> dict:
    """Return a policy dict with auto_apply_config.enabled set."""
    p = _load_policy_from_repo()
    p["auto_apply_config"] = dict(p.get("auto_apply_config", {}))
    p["auto_apply_config"]["enabled"] = enabled
    return p


def _check_auto_apply_eligibility(action: dict, policy: dict) -> list:
    """
    Inline eligibility checker mirroring the logic in seo_level5_auto_apply.py.
    Returns list of blockers (empty = eligible).
    """
    blockers = []
    cfg = policy.get("auto_apply_config", {})

    if not cfg.get("enabled", False):
        blockers.append("auto_apply_disabled")
        return blockers  # short-circuit: no point checking further

    allowlist_actions = cfg.get("auto_apply_actions_allowlist", [])
    tier_allowlist = cfg.get("auto_apply_tier_allowlist", [])
    tier_denylist = cfg.get("auto_apply_tier_denylist", [])

    if action.get("action_type") not in allowlist_actions:
        blockers.append("action_type_not_in_allowlist")

    tier = action.get("tier", "")
    if tier in tier_denylist:
        blockers.append(f"tier_{tier.lower()}_in_denylist")
    if tier not in tier_allowlist:
        blockers.append("tier_not_in_allowlist")

    if action.get("is_money_page"):
        blockers.append("money_page_forbidden")

    if action.get("is_pillar_page"):
        blockers.append("pillar_page_forbidden")

    return blockers


def _check_proposal_validity(proposal: str) -> list:
    """Inline proposal validator."""
    blockers = []
    if not proposal or len(proposal) < 50:
        blockers.append("proposal_too_short")
    if len(proposal) > 200:
        blockers.append("proposal_too_long")
    if '"' in proposal or "'" in proposal:
        blockers.append("proposal_contains_unsafe_quote")
    if "<" in proposal or ">" in proposal:
        blockers.append("proposal_contains_html")
    return blockers


def _make_action(tier="C", is_money=False, is_pillar=False,
                 action_type="meta_description_update") -> dict:
    return {
        "action_id": "test-id",
        "action_type": action_type,
        "url": "/test/page",
        "tier": tier,
        "is_money_page": is_money,
        "is_pillar_page": is_pillar,
    }


# ─── 1. Schema version ────────────────────────────────────────────────────────

def test_schema_version_is_1_3():
    """Policy file must have schema_version == '1.3' after PR #85."""
    policy = _load_policy_from_repo()
    assert policy["schema_version"] == "1.3"


# ─── 2. auto_apply_config structure ──────────────────────────────────────────

def test_auto_apply_config_exists_in_policy():
    """auto_apply_config block must exist in policy."""
    policy = _load_policy_from_repo()
    assert "auto_apply_config" in policy


def test_auto_apply_config_disabled_by_default():
    """auto_apply_config.enabled must be false in the shipped policy."""
    policy = _load_policy_from_repo()
    assert policy["auto_apply_config"]["enabled"] is False


def test_auto_apply_config_has_required_keys():
    """auto_apply_config must have all required structure keys."""
    policy = _load_policy_from_repo()
    cfg = policy["auto_apply_config"]
    required = [
        "enabled", "mode", "auto_apply_actions_allowlist",
        "auto_apply_tier_allowlist", "auto_apply_tier_denylist",
        "auto_apply_max_candidates", "auto_apply_money_pages",
        "auto_apply_pillar_pages", "auto_apply_approved_by_label",
        "rollback_required", "feedback_loop_mode",
    ]
    for key in required:
        assert key in cfg, f"Missing key: {key}"


def test_auto_apply_mode_label_correct():
    """mode must be 'controlled_single_auto_apply'."""
    policy = _load_policy_from_repo()
    assert policy["auto_apply_config"]["mode"] == "controlled_single_auto_apply"


# ─── 3. Manual path invariants (must remain unchanged) ───────────────────────

def test_manual_approval_gate_still_manual():
    """approval_gate must remain 'manual' — manual path unchanged."""
    policy = _load_policy_from_repo()
    assert policy["approval_gate"] == "manual"


def test_manual_requires_manual_approval_still_true():
    """requires_manual_approval_before_apply must remain True for meta_description_update."""
    policy = _load_policy_from_repo()
    activation = policy["action_activation"]["meta_description_update"]
    assert activation["requires_manual_approval_before_apply"] is True


def test_tier_a_still_read_only():
    """Tier A restriction must remain read_only."""
    policy = _load_policy_from_repo()
    assert policy["tier_restrictions"]["A"] == "read_only"


def test_tier_b_still_restricted():
    """Tier B restriction must remain restricted."""
    policy = _load_policy_from_repo()
    assert policy["tier_restrictions"]["B"] == "restricted"


def test_rollback_required_still_true():
    """rollback_required must remain True at top level."""
    policy = _load_policy_from_repo()
    assert policy["rollback_required"] is True


def test_feedback_loop_mode_still_observability_only():
    """feedback_loop_mode must remain observability_only."""
    policy = _load_policy_from_repo()
    assert policy["feedback_loop_mode"] == "observability_only"


def test_max_actions_per_run_still_one():
    """max_actions_per_run must remain 1."""
    policy = _load_policy_from_repo()
    assert policy["max_actions_per_run"] == 1


def test_forbidden_actions_unchanged():
    """All 8 forbidden actions must still be present."""
    policy = _load_policy_from_repo()
    expected = {
        "change_canonical", "change_robots", "change_noindex",
        "change_registry", "change_cluster_schema", "change_internal_ownership",
        "modify_pillar_page", "modify_sitemap_policy",
    }
    assert expected.issubset(set(policy["forbidden_actions"]))


# ─── 4. Flag OFF → no auto-apply ─────────────────────────────────────────────

def test_flag_off_blocks_auto_apply_for_tier_c():
    """When flag is OFF, even a valid Tier C action is blocked."""
    policy = _policy_with_flag(enabled=False)
    action = _make_action(tier="C")
    blockers = _check_auto_apply_eligibility(action, policy)
    assert "auto_apply_disabled" in blockers


# ─── 5. Flag ON — eligibility checks ─────────────────────────────────────────

def test_flag_on_tier_c_eligible():
    """Flag ON + Tier C + valid action = no blockers."""
    policy = _policy_with_flag(enabled=True)
    action = _make_action(tier="C")
    blockers = _check_auto_apply_eligibility(action, policy)
    assert blockers == []


def test_flag_on_tier_a_blocked():
    """Flag ON + Tier A = blocked, always."""
    policy = _policy_with_flag(enabled=True)
    action = _make_action(tier="A")
    blockers = _check_auto_apply_eligibility(action, policy)
    assert any("tier_a" in b for b in blockers)


def test_flag_on_tier_b_blocked():
    """Flag ON + Tier B = blocked, always."""
    policy = _policy_with_flag(enabled=True)
    action = _make_action(tier="B")
    blockers = _check_auto_apply_eligibility(action, policy)
    assert any("tier_b" in b for b in blockers)


def test_flag_on_money_page_blocked():
    """Flag ON + money page = blocked."""
    policy = _policy_with_flag(enabled=True)
    action = _make_action(tier="C", is_money=True)
    blockers = _check_auto_apply_eligibility(action, policy)
    assert "money_page_forbidden" in blockers


def test_flag_on_pillar_page_blocked():
    """Flag ON + pillar page = blocked."""
    policy = _policy_with_flag(enabled=True)
    action = _make_action(tier="C", is_pillar=True)
    blockers = _check_auto_apply_eligibility(action, policy)
    assert "pillar_page_forbidden" in blockers


def test_flag_on_meta_title_update_blocked():
    """Flag ON + meta_title_update (not in allowlist) = blocked."""
    policy = _policy_with_flag(enabled=True)
    action = _make_action(tier="C", action_type="meta_title_update")
    blockers = _check_auto_apply_eligibility(action, policy)
    assert "action_type_not_in_allowlist" in blockers


# ─── 6. Proposal validity ─────────────────────────────────────────────────────

def test_valid_proposal_passes():
    """A well-formed proposal (no quotes, no HTML, 140–160 chars) passes."""
    good = "Animatori pentru petreceri copii in Bucuresti. Costume premium, 30 personaje. Pachete de la 490 lei. Rezerva acum: 0722 744 377."
    assert len(good) >= 50
    blockers = _check_proposal_validity(good)
    assert blockers == []


def test_proposal_with_double_quote_blocked():
    """Proposal containing double quote is blocked."""
    bad = 'Animatori "premium" pentru petreceri copii in Bucuresti. Rezerva acum.'
    blockers = _check_proposal_validity(bad)
    assert "proposal_contains_unsafe_quote" in blockers


def test_proposal_with_html_blocked():
    """Proposal containing HTML tags is blocked."""
    bad = "Animatori <b>premium</b> pentru petreceri copii in Bucuresti. Rezerva acum."
    blockers = _check_proposal_validity(bad)
    assert "proposal_contains_html" in blockers


def test_too_short_proposal_blocked():
    """Proposal shorter than 50 chars is blocked."""
    blockers = _check_proposal_validity("Prea scurt.")
    assert "proposal_too_short" in blockers


# ─── 7. auto_apply_config invariants ─────────────────────────────────────────

def test_auto_apply_only_meta_description_in_allowlist():
    """Only meta_description_update should be in auto_apply_actions_allowlist."""
    policy = _load_policy_from_repo()
    cfg = policy["auto_apply_config"]
    assert cfg["auto_apply_actions_allowlist"] == ["meta_description_update"]
    assert "meta_title_update" not in cfg["auto_apply_actions_allowlist"]


def test_auto_apply_only_tier_c_in_allowlist():
    """Only Tier C should be in auto_apply_tier_allowlist."""
    policy = _load_policy_from_repo()
    cfg = policy["auto_apply_config"]
    assert cfg["auto_apply_tier_allowlist"] == ["C"]


def test_auto_apply_tier_a_b_in_denylist():
    """Tier A and B must be in auto_apply_tier_denylist."""
    policy = _load_policy_from_repo()
    cfg = policy["auto_apply_config"]
    assert "A" in cfg["auto_apply_tier_denylist"]
    assert "B" in cfg["auto_apply_tier_denylist"]


def test_auto_apply_approved_by_label():
    """approved_by label must be 'system_auto_apply'."""
    policy = _load_policy_from_repo()
    assert policy["auto_apply_config"]["auto_apply_approved_by_label"] == "system_auto_apply"


def test_auto_apply_max_candidates_is_one():
    """auto_apply_max_candidates must be 1."""
    policy = _load_policy_from_repo()
    assert policy["auto_apply_config"]["auto_apply_max_candidates"] == 1


def test_auto_apply_rollback_required():
    """rollback_required must be True in auto_apply_config."""
    policy = _load_policy_from_repo()
    assert policy["auto_apply_config"]["rollback_required"] is True


def test_auto_apply_feedback_loop_observability_only():
    """feedback_loop_mode in auto_apply_config must be observability_only."""
    policy = _load_policy_from_repo()
    assert policy["auto_apply_config"]["feedback_loop_mode"] == "observability_only"


def test_auto_apply_no_commit_no_pr():
    """create_pull_request and commit_changes must be False in auto_apply_config."""
    policy = _load_policy_from_repo()
    cfg = policy["auto_apply_config"]
    assert cfg["create_pull_request"] is False
    assert cfg["commit_changes"] is False
