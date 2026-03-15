"""
test_seo_agent_p2.py — Tests for Canary Orchestrator + Rollback.
"""
import pytest
from datetime import datetime, timezone, timedelta

from agent.seo_agent.canary_orchestrator import (
    CanaryConfig,
    CanaryState,
    select_canary_site,
    evaluate_canary_decision,
    plan_waves,
    create_canary_state,
    transition_canary,
)
from agent.seo_agent.rollback import (
    RollbackRequest,
    RollbackResult,
    execute_rollback,
    generate_rollback_audit_entry,
    request_cdn_purge,
    request_reindex,
)
from agent.seo_agent.rules_engine import SiteContext
from agent.seo_agent.monitor import OwnerShareResult


# ═══════════════════════════════════════════════════════════════════════════════
# Canary Orchestrator
# ═══════════════════════════════════════════════════════════════════════════════

SITES = [
    SiteContext(domain="superparty.ro", freeze_until=datetime(2026, 3, 21, 23, 59, 59, tzinfo=timezone.utc)),
    SiteContext(domain="animatopia.ro", freeze_until=None),
    SiteContext(domain="wowparty.ro", freeze_until=None),
]


class TestSelectCanary:

    def test_selects_animatopia_by_default(self):
        config = CanaryConfig(canary_site="animatopia.ro")
        site = select_canary_site(SITES, config)
        assert site is not None
        assert site.domain == "animatopia.ro"

    def test_rejects_frozen_canary(self):
        config = CanaryConfig(canary_site="superparty.ro")
        now = datetime(2026, 3, 15, 0, 0, 0, tzinfo=timezone.utc)
        site = select_canary_site(SITES, config, now=now)
        assert site is None

    def test_returns_none_for_unknown_site(self):
        config = CanaryConfig(canary_site="unknown.ro")
        site = select_canary_site(SITES, config)
        assert site is None


class TestCanaryDecision:

    def test_proceed_when_share_good(self):
        current = OwnerShareResult(owner_share=0.65, owner_ctr=0.02)
        config = CanaryConfig(min_owner_share_for_proceed=0.40)
        decision, reason = evaluate_canary_decision(current, None, config)
        assert decision == "proceed"

    def test_rollback_on_critical(self):
        current = OwnerShareResult(owner_share=0.10, owner_ctr=0.005)
        config = CanaryConfig(min_owner_share_for_proceed=0.40)
        decision, reason = evaluate_canary_decision(current, None, config)
        assert decision == "rollback"

    def test_extend_on_warning(self):
        current = OwnerShareResult(owner_share=0.35, owner_ctr=0.015)
        config = CanaryConfig(min_owner_share_for_proceed=0.40)
        decision, reason = evaluate_canary_decision(current, None, config)
        assert decision == "extend"

    def test_rollback_on_ctr_regression(self):
        baseline = OwnerShareResult(owner_share=0.5, owner_ctr=0.03)
        current = OwnerShareResult(owner_share=0.5, owner_ctr=0.01)  # 66% drop
        config = CanaryConfig(max_ctr_regression_for_proceed=0.10)
        decision, reason = evaluate_canary_decision(current, baseline, config)
        assert decision == "rollback"


class TestWavePlanning:

    def test_excludes_canary_and_frozen(self):
        now = datetime(2026, 3, 15, 0, 0, 0, tzinfo=timezone.utc)
        waves = plan_waves(SITES, "animatopia.ro", wave_size=1, now=now)
        # superparty is frozen, animatopia is canary → only wowparty
        assert len(waves) == 1
        assert waves[0] == ["wowparty.ro"]

    def test_wave_size_grouping(self):
        sites = [
            SiteContext(domain="a.ro"),
            SiteContext(domain="b.ro"),
            SiteContext(domain="c.ro"),
            SiteContext(domain="d.ro"),
        ]
        waves = plan_waves(sites, "a.ro", wave_size=2)
        assert len(waves) == 2  # b+c, d
        assert len(waves[0]) == 2


class TestCanaryState:

    def test_create_initial_state(self):
        config = CanaryConfig(canary_site="animatopia.ro")
        state = create_canary_state("mascote si personaje", config)
        assert state.status == "pending"
        assert state.canary_site == "animatopia.ro"

    def test_valid_transition(self):
        state = CanaryState(head_term="test", canary_site="a.ro", status="pending")
        state = transition_canary(state, "deployed", "PR merged")
        assert state.status == "deployed"

    def test_invalid_transition_stays(self):
        state = CanaryState(head_term="test", canary_site="a.ro", status="pending")
        state = transition_canary(state, "passed")  # invalid: pending → passed
        assert state.status == "pending"  # unchanged

    def test_full_happy_path(self):
        state = CanaryState(head_term="t", canary_site="a.ro", status="pending")
        state = transition_canary(state, "deployed")
        state = transition_canary(state, "monitoring")
        state = transition_canary(state, "passed", "owner_share=65%")
        assert state.status == "passed"


# ═══════════════════════════════════════════════════════════════════════════════
# Rollback
# ═══════════════════════════════════════════════════════════════════════════════

class TestRollback:

    def test_dry_run_succeeds(self):
        req = RollbackRequest(
            site_domain="animatopia.ro",
            pr_branch="agent/seo/animatopia-owner-mascote-202603150200",
            head_term="mascote si personaje",
            reason="CTR dropped 20%",
            severity="critical",
        )
        result = execute_rollback(req, repo_dir=".", dry_run=True)
        assert result.success is True
        assert len(result.steps_completed) == 3
        assert "DRY RUN" in result.steps_completed[0]

    def test_cdn_purge(self):
        ok, msg = request_cdn_purge("animatopia.ro", ["/mascote"])
        assert ok is True
        assert "Vercel" in msg

    def test_reindex_queue(self):
        results = request_reindex("animatopia.ro", ["/mascote", "/"])
        assert len(results) == 2
        assert results[0]["status"] == "queued"
        assert "animatopia.ro/mascote" in results[0]["url"]


class TestRollbackAudit:

    def test_audit_entry_structure(self):
        req = RollbackRequest(
            site_domain="superparty.ro",
            pr_branch="agent/seo/sp-test",
            head_term="animatori petreceri copii",
            reason="test",
        )
        result = RollbackResult(
            success=True,
            revert_branch="revert/agent/seo/sp-test",
            steps_completed=["step1"],
        )
        entry = generate_rollback_audit_entry(req, result)
        assert entry["actor"] == "seo-agent"
        assert entry["action"] == "rollback"
        assert entry["payload"]["site"] == "superparty.ro"
        assert entry["payload"]["success"] is True
