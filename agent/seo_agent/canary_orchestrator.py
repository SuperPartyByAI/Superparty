"""
canary_orchestrator.py — Canary → Wave rollout coordination.

Flow:
  1. Select canary site (from json_rules or default: animatopia.ro)
  2. Generate PR for canary site only
  3. Monitor canary for 48-72h
  4. If OK: generate replica PRs for remaining sites in waves
  5. If NOT OK: initiate rollback on canary
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .rules_engine import (
    SiteContext, OwnerPageContext, RuleResult,
    check_freeze, evaluate_all,
)
from .monitor import OwnerShareResult, AlertResult, AlertThresholds, check_thresholds

log = logging.getLogger("seo_agent.canary")


@dataclass
class CanaryConfig:
    """Configuration for a canary rollout."""
    canary_site: str = "animatopia.ro"
    monitoring_hours: int = 72
    min_owner_share_for_proceed: float = 0.40
    max_ctr_regression_for_proceed: float = 0.10
    wave_size: int = 1  # sites per wave after canary


@dataclass
class CanaryState:
    """State of a canary rollout."""
    head_term: str
    canary_site: str
    status: str = "pending"  # pending, deployed, monitoring, passed, failed, rolled_back
    pr_branch: str = ""
    deployed_at: Optional[datetime] = None
    decision_at: Optional[datetime] = None
    decision_reason: str = ""
    metrics_snapshot: Optional[dict] = None


@dataclass
class WaveResult:
    """Result of a wave deployment."""
    wave_number: int
    sites: list[str] = field(default_factory=list)
    pr_branches: list[str] = field(default_factory=list)
    status: str = "pending"


def select_canary_site(
    all_sites: list[SiteContext],
    config: CanaryConfig,
    now: Optional[datetime] = None,
) -> Optional[SiteContext]:
    """
    Select the canary site from available sites.
    Must not be frozen.
    """
    now = now or datetime.now(timezone.utc)

    for site in all_sites:
        if site.domain == config.canary_site:
            freeze = check_freeze(site, now=now)
            if freeze.allowed:
                return site
            else:
                log.warning(f"Canary site {config.canary_site} is frozen: {freeze.reasons}")
                return None

    log.warning(f"Canary site {config.canary_site} not found in available sites")
    return None


def evaluate_canary_decision(
    current_metrics: OwnerShareResult,
    baseline_metrics: Optional[OwnerShareResult],
    config: CanaryConfig,
) -> tuple[str, str]:
    """
    Evaluate canary metrics and decide: proceed or rollback.
    
    Returns: (decision, reason)
      decision: "proceed" | "rollback" | "extend"
    """
    thresholds = AlertThresholds(
        min_owner_share=config.min_owner_share_for_proceed * 0.5,  # critical threshold
        target_owner_share=config.min_owner_share_for_proceed,
        max_ctr_regression=config.max_ctr_regression_for_proceed,
    )

    alert = check_thresholds(current_metrics, baseline=baseline_metrics, thresholds=thresholds)

    if alert.severity == "critical":
        return "rollback", f"Critical alerts: {'; '.join(alert.alerts)}"

    if current_metrics.owner_share >= config.min_owner_share_for_proceed:
        return "proceed", (
            f"Canary passed: owner_share={current_metrics.owner_share:.1%} "
            f"(>= {config.min_owner_share_for_proceed:.0%} target)"
        )

    if alert.severity == "warning":
        return "extend", f"Warnings present, extending monitoring: {'; '.join(alert.alerts)}"

    return "extend", (
        f"owner_share={current_metrics.owner_share:.1%} not yet at target "
        f"{config.min_owner_share_for_proceed:.0%}"
    )


def plan_waves(
    all_sites: list[SiteContext],
    canary_site: str,
    wave_size: int = 1,
    now: Optional[datetime] = None,
) -> list[list[str]]:
    """
    Plan deployment waves after canary succeeds.
    Returns list of waves, each containing site domains.
    Frozen sites are excluded.
    """
    now = now or datetime.now(timezone.utc)

    eligible = []
    for site in all_sites:
        if site.domain == canary_site:
            continue  # skip canary
        freeze = check_freeze(site, now=now)
        if freeze.allowed:
            eligible.append(site.domain)
        else:
            log.info(f"Skipping frozen site {site.domain} in wave planning")

    waves = []
    for i in range(0, len(eligible), wave_size):
        waves.append(eligible[i:i + wave_size])

    return waves


def create_canary_state(
    head_term: str,
    config: CanaryConfig,
) -> CanaryState:
    """Initialize a new canary state."""
    return CanaryState(
        head_term=head_term,
        canary_site=config.canary_site,
        status="pending",
    )


def transition_canary(
    state: CanaryState,
    new_status: str,
    reason: str = "",
    metrics: Optional[dict] = None,
) -> CanaryState:
    """
    Transition canary to a new state.
    Valid transitions:
      pending → deployed
      deployed → monitoring
      monitoring → passed | failed
      failed → rolled_back
    """
    valid_transitions = {
        "pending": ["deployed"],
        "deployed": ["monitoring"],
        "monitoring": ["passed", "failed", "extended"],
        "extended": ["passed", "failed"],
        "failed": ["rolled_back"],
    }

    allowed = valid_transitions.get(state.status, [])
    if new_status not in allowed:
        log.error(
            f"Invalid canary transition: {state.status} → {new_status}. "
            f"Allowed: {allowed}"
        )
        return state

    state.status = new_status
    state.decision_reason = reason
    state.decision_at = datetime.now(timezone.utc)
    if metrics:
        state.metrics_snapshot = metrics

    log.info(f"Canary [{state.head_term}] on {state.canary_site}: "
             f"{state.status} — {reason}")
    return state
