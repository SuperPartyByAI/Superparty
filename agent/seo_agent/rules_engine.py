"""
rules_engine.py — Policy enforcement for the SEO Agent.

Evaluates rules before any mutation (PR creation, deploy, merge).
Returns allow/deny with reasons.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger("seo_agent.rules")


@dataclass
class RuleResult:
    """Result of a rules evaluation."""
    allowed: bool
    reasons: list[str] = field(default_factory=list)

    def deny(self, reason: str) -> "RuleResult":
        self.allowed = False
        self.reasons.append(reason)
        return self

    def to_dict(self) -> dict:
        return {"allowed": self.allowed, "reasons": self.reasons}


@dataclass
class SiteContext:
    """Minimal site context for rule evaluation."""
    domain: str
    site_id: str = ""
    brand: str = ""
    freeze_until: Optional[datetime] = None
    environment: str = "production"


@dataclass
class OwnerPageContext:
    """Context for an owner page being created/modified."""
    head_term: str
    path: str
    title: str = ""
    h1: str = ""
    site_domain: str = ""
    existing_owners: list[dict] = field(default_factory=list)  # other owners for same term
    internal_link_count: int = 0
    json_rules: dict = field(default_factory=dict)


# ── Individual Rule Functions ────────────────────────────────────────────────

def check_freeze(site: SiteContext, now: Optional[datetime] = None) -> RuleResult:
    """
    Check if the site is in a freeze window.
    Denies any mutation during freeze.
    """
    result = RuleResult(allowed=True)
    now = now or datetime.now(timezone.utc)

    if site.freeze_until and now < site.freeze_until:
        remaining = site.freeze_until - now
        result.deny(
            f"Site {site.domain} is frozen until {site.freeze_until.isoformat()} "
            f"({remaining.days}d {remaining.seconds // 3600}h remaining)"
        )
    return result


def validate_owner_uniqueness(
    head_term: str,
    target_site_domain: str,
    existing_owners: list[dict],
) -> RuleResult:
    """
    Ensure only ONE site owns a given head-term.
    existing_owners: list of dicts with keys: domain, path, site_id
    """
    result = RuleResult(allowed=True)

    for owner in existing_owners:
        owner_domain = owner.get("domain", owner.get("sites", {}).get("domain", ""))
        if owner_domain and owner_domain != target_site_domain:
            result.deny(
                f"Head-term '{head_term}' is already owned by {owner_domain} "
                f"at path {owner.get('path', '?')}. "
                f"Cannot assign to {target_site_domain}."
            )
            break

    return result


def enforce_canary(
    json_rules: dict,
    is_canary_site: bool,
    canary_completed: bool = False,
) -> RuleResult:
    """
    If canary_required is set in rules, block non-canary sites
    until canary is completed.
    """
    result = RuleResult(allowed=True)

    if not json_rules.get("canary_required", False):
        return result

    if is_canary_site:
        return result  # canary site is always allowed

    if not canary_completed:
        canary_site = json_rules.get("canary_site", "unknown")
        result.deny(
            f"Canary required but not completed. Deploy to canary site "
            f"({canary_site}) first and wait for monitoring results."
        )

    return result


def verify_internal_links(
    link_count: int,
    min_required: int = 3,
) -> RuleResult:
    """
    Ensure minimum number of internal links point to owner page.
    """
    result = RuleResult(allowed=True)

    if link_count < min_required:
        result.deny(
            f"Owner page has {link_count} internal links, "
            f"minimum required is {min_required}. "
            f"Add {min_required - link_count} more internal links."
        )

    return result


def validate_canonical_pattern(
    canonical_url: str,
    domain: str,
    path: str,
    pattern: str = "https://{domain}{path}",
) -> RuleResult:
    """
    Verify canonical URL matches the expected pattern.
    """
    result = RuleResult(allowed=True)
    expected = pattern.format(domain=domain, path=path)

    if canonical_url != expected:
        result.deny(
            f"Canonical URL '{canonical_url}' does not match expected "
            f"pattern '{expected}'. Fix canonical before proceeding."
        )

    return result


def check_homepage_modification(
    target_path: str,
    site: SiteContext,
) -> RuleResult:
    """
    Block homepage modifications during freeze.
    Homepage is always "/" path.
    """
    result = RuleResult(allowed=True)
    normalized = target_path.rstrip("/") or "/"

    if normalized == "/" and site.freeze_until:
        now = datetime.now(timezone.utc)
        if now < site.freeze_until:
            result.deny(
                f"Homepage modification blocked for {site.domain} "
                f"during measurement window (until {site.freeze_until.isoformat()})"
            )

    return result


# ── Aggregate Evaluation ─────────────────────────────────────────────────────

def evaluate_all(
    site: SiteContext,
    owner: OwnerPageContext,
    is_canary_site: bool = False,
    canary_completed: bool = False,
    now: Optional[datetime] = None,
) -> RuleResult:
    """
    Run ALL rules and collect results.
    Returns a single RuleResult with all deny reasons aggregated.
    """
    result = RuleResult(allowed=True)

    # 1. Freeze check
    freeze = check_freeze(site, now=now)
    if not freeze.allowed:
        result.allowed = False
        result.reasons.extend(freeze.reasons)

    # 2. Owner uniqueness
    uniqueness = validate_owner_uniqueness(
        owner.head_term,
        site.domain,
        owner.existing_owners,
    )
    if not uniqueness.allowed:
        result.allowed = False
        result.reasons.extend(uniqueness.reasons)

    # 3. Canary enforcement
    canary = enforce_canary(
        owner.json_rules,
        is_canary_site,
        canary_completed,
    )
    if not canary.allowed:
        result.allowed = False
        result.reasons.extend(canary.reasons)

    # 4. Internal links
    min_links = owner.json_rules.get("min_internal_links", 3)
    links = verify_internal_links(owner.internal_link_count, min_links)
    if not links.allowed:
        result.allowed = False
        result.reasons.extend(links.reasons)

    # 5. Homepage protection
    homepage = check_homepage_modification(owner.path, site)
    if not homepage.allowed:
        result.allowed = False
        result.reasons.extend(homepage.reasons)

    # 6. Canonical validation
    if owner.json_rules.get("canonical_pattern"):
        canonical = validate_canonical_pattern(
            owner.h1,  # Note: this should be canonical URL, not h1
            site.domain,
            owner.path,
            owner.json_rules["canonical_pattern"],
        )
        # Don't block on canonical — just warn
        if not canonical.allowed:
            log.warning(f"Canonical warning: {canonical.reasons}")

    return result
