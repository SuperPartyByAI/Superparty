"""
test_rules_engine.py — Tests for the SEO Agent Rules Engine + Owner Mapper.

Test cases from spec:
  1. Happy path: valid owner → allow
  2. Freeze blocked: site with freeze_until in future → deny
  3. Duplicate owner: same head-term claimed → deny
  4. Canary revert: canary not completed → deny non-canary
  5. Internal links minimum not met → deny
  6. Homepage modification during freeze → deny
  7. Owner mapper conflicts
"""
import pytest
from datetime import datetime, timezone, timedelta

from agent.seo_agent.rules_engine import (
    RuleResult,
    SiteContext,
    OwnerPageContext,
    check_freeze,
    validate_owner_uniqueness,
    enforce_canary,
    verify_internal_links,
    validate_canonical_pattern,
    check_homepage_modification,
    evaluate_all,
)
from agent.seo_agent.owner_mapper import OwnerMapper, SEED_OWNERS


# ═══════════════════════════════════════════════════════════════════════════════
# check_freeze
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckFreeze:

    def test_no_freeze_allows(self):
        site = SiteContext(domain="animatopia.ro", freeze_until=None)
        result = check_freeze(site)
        assert result.allowed is True
        assert len(result.reasons) == 0

    def test_expired_freeze_allows(self):
        past = datetime.now(timezone.utc) - timedelta(days=1)
        site = SiteContext(domain="superparty.ro", freeze_until=past)
        result = check_freeze(site)
        assert result.allowed is True

    def test_active_freeze_denies(self):
        future = datetime.now(timezone.utc) + timedelta(days=5)
        site = SiteContext(domain="superparty.ro", freeze_until=future)
        result = check_freeze(site)
        assert result.allowed is False
        assert "frozen" in result.reasons[0].lower()

    def test_superparty_freeze_until_march_21(self):
        """Exact scenario: SP frozen until 2026-03-21."""
        freeze = datetime(2026, 3, 21, 23, 59, 59, tzinfo=timezone.utc)
        site = SiteContext(domain="superparty.ro", freeze_until=freeze)
        now = datetime(2026, 3, 15, 2, 0, 0, tzinfo=timezone.utc)
        result = check_freeze(site, now=now)
        assert result.allowed is False
        assert "superparty.ro" in result.reasons[0]

    def test_superparty_after_freeze_allows(self):
        freeze = datetime(2026, 3, 21, 23, 59, 59, tzinfo=timezone.utc)
        site = SiteContext(domain="superparty.ro", freeze_until=freeze)
        now = datetime(2026, 3, 22, 0, 0, 1, tzinfo=timezone.utc)
        result = check_freeze(site, now=now)
        assert result.allowed is True


# ═══════════════════════════════════════════════════════════════════════════════
# validate_owner_uniqueness
# ═══════════════════════════════════════════════════════════════════════════════

class TestOwnerUniqueness:

    def test_no_existing_owners_allows(self):
        result = validate_owner_uniqueness("animatori petreceri copii", "superparty.ro", [])
        assert result.allowed is True

    def test_same_site_owner_allows(self):
        """Re-registering same owner on same site is OK."""
        existing = [{"domain": "superparty.ro", "path": "/animatori-petreceri-copii"}]
        result = validate_owner_uniqueness("animatori petreceri copii", "superparty.ro", existing)
        assert result.allowed is True

    def test_different_site_owner_denies(self):
        """Another site already owns this term."""
        existing = [{"domain": "animatopia.ro", "path": "/animatori-petreceri-copii"}]
        result = validate_owner_uniqueness("animatori petreceri copii", "superparty.ro", existing)
        assert result.allowed is False
        assert "animatopia.ro" in result.reasons[0]

    def test_nested_domain_format(self):
        """Handle Supabase join format with nested sites object."""
        existing = [{"sites": {"domain": "wowparty.ro"}, "path": "/animatori"}]
        result = validate_owner_uniqueness("animatori petreceri copii", "superparty.ro", existing)
        assert result.allowed is False
        assert "wowparty.ro" in result.reasons[0]


# ═══════════════════════════════════════════════════════════════════════════════
# enforce_canary
# ═══════════════════════════════════════════════════════════════════════════════

class TestCanaryEnforcement:

    def test_no_canary_required_allows(self):
        result = enforce_canary({}, is_canary_site=False)
        assert result.allowed is True

    def test_canary_site_always_allowed(self):
        rules = {"canary_required": True, "canary_site": "animatopia.ro"}
        result = enforce_canary(rules, is_canary_site=True)
        assert result.allowed is True

    def test_non_canary_blocked_when_canary_incomplete(self):
        rules = {"canary_required": True, "canary_site": "animatopia.ro"}
        result = enforce_canary(rules, is_canary_site=False, canary_completed=False)
        assert result.allowed is False
        assert "canary" in result.reasons[0].lower()

    def test_non_canary_allowed_when_canary_completed(self):
        rules = {"canary_required": True, "canary_site": "animatopia.ro"}
        result = enforce_canary(rules, is_canary_site=False, canary_completed=True)
        assert result.allowed is True


# ═══════════════════════════════════════════════════════════════════════════════
# verify_internal_links
# ═══════════════════════════════════════════════════════════════════════════════

class TestInternalLinks:

    def test_sufficient_links_allows(self):
        result = verify_internal_links(5, min_required=3)
        assert result.allowed is True

    def test_exact_minimum_allows(self):
        result = verify_internal_links(3, min_required=3)
        assert result.allowed is True

    def test_insufficient_links_denies(self):
        result = verify_internal_links(1, min_required=3)
        assert result.allowed is False
        assert "2 more" in result.reasons[0]

    def test_zero_links_denies(self):
        result = verify_internal_links(0, min_required=3)
        assert result.allowed is False


# ═══════════════════════════════════════════════════════════════════════════════
# validate_canonical_pattern
# ═══════════════════════════════════════════════════════════════════════════════

class TestCanonicalPattern:

    def test_correct_canonical_allows(self):
        result = validate_canonical_pattern(
            "https://www.superparty.ro/animatori-petreceri-copii",
            "www.superparty.ro",
            "/animatori-petreceri-copii",
        )
        assert result.allowed is True

    def test_wrong_canonical_denies(self):
        result = validate_canonical_pattern(
            "https://www.superparty.ro/animatori-petreceri-copii/",
            "www.superparty.ro",
            "/animatori-petreceri-copii",
        )
        assert result.allowed is False


# ═══════════════════════════════════════════════════════════════════════════════
# check_homepage_modification
# ═══════════════════════════════════════════════════════════════════════════════

class TestHomepageProtection:

    def test_non_homepage_during_freeze_allows(self):
        site = SiteContext(
            domain="superparty.ro",
            freeze_until=datetime.now(timezone.utc) + timedelta(days=5)
        )
        result = check_homepage_modification("/animatori-petreceri-copii", site)
        assert result.allowed is True

    def test_homepage_during_freeze_denies(self):
        site = SiteContext(
            domain="superparty.ro",
            freeze_until=datetime.now(timezone.utc) + timedelta(days=5)
        )
        result = check_homepage_modification("/", site)
        assert result.allowed is False
        assert "homepage" in result.reasons[0].lower()

    def test_homepage_without_freeze_allows(self):
        site = SiteContext(domain="animatopia.ro", freeze_until=None)
        result = check_homepage_modification("/", site)
        assert result.allowed is True


# ═══════════════════════════════════════════════════════════════════════════════
# evaluate_all (aggregate)
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvaluateAll:

    def test_happy_path_all_pass(self):
        """Valid owner on non-frozen site with enough links → all pass."""
        site = SiteContext(domain="animatopia.ro", freeze_until=None)
        owner = OwnerPageContext(
            head_term="mascote si personaje",
            path="/mascote-si-personaje",
            title="Mascote | Animatopia",
            h1="Mascote și Personaje",
            existing_owners=[],
            internal_link_count=4,
            json_rules={},
        )
        result = evaluate_all(site, owner)
        assert result.allowed is True
        assert len(result.reasons) == 0

    def test_frozen_site_blocks_everything(self):
        now = datetime(2026, 3, 15, 2, 0, 0, tzinfo=timezone.utc)
        site = SiteContext(
            domain="superparty.ro",
            freeze_until=datetime(2026, 3, 21, 23, 59, 59, tzinfo=timezone.utc),
        )
        owner = OwnerPageContext(
            head_term="animatori petreceri copii",
            path="/animatori-petreceri-copii",
            existing_owners=[],
            internal_link_count=5,
            json_rules={},
        )
        result = evaluate_all(site, owner, now=now)
        assert result.allowed is False
        assert any("frozen" in r.lower() for r in result.reasons)

    def test_duplicate_owner_blocks(self):
        site = SiteContext(domain="wowparty.ro", freeze_until=None)
        owner = OwnerPageContext(
            head_term="animatori petreceri copii",
            path="/animatori-petreceri-copii",
            existing_owners=[{"domain": "superparty.ro", "path": "/animatori-petreceri-copii"}],
            internal_link_count=5,
            json_rules={},
        )
        result = evaluate_all(site, owner)
        assert result.allowed is False
        assert any("already owned" in r.lower() for r in result.reasons)

    def test_multiple_violations_all_reported(self):
        """Multiple rules violated → all reasons collected."""
        now = datetime(2026, 3, 15, 2, 0, 0, tzinfo=timezone.utc)
        site = SiteContext(
            domain="superparty.ro",
            freeze_until=datetime(2026, 3, 21, 23, 59, 59, tzinfo=timezone.utc),
        )
        owner = OwnerPageContext(
            head_term="animatori petreceri copii",
            path="/",
            existing_owners=[{"domain": "animatopia.ro", "path": "/apc"}],
            internal_link_count=0,
            json_rules={"canary_required": True, "canary_site": "animatopia.ro"},
        )
        result = evaluate_all(site, owner, is_canary_site=False, now=now)
        assert result.allowed is False
        assert len(result.reasons) >= 3  # freeze + duplicate + homepage + links + canary


# ═══════════════════════════════════════════════════════════════════════════════
# OwnerMapper
# ═══════════════════════════════════════════════════════════════════════════════

class TestOwnerMapper:

    def test_seed_data_loaded(self):
        mapper = OwnerMapper()
        assert mapper.is_term_owned("animatori petreceri copii")
        assert mapper.is_term_owned("mascote si personaje")
        assert mapper.is_term_owned("pachete animatori")

    def test_get_owner_returns_correct_site(self):
        mapper = OwnerMapper()
        owner = mapper.get_owner("animatori petreceri copii")
        assert owner is not None
        assert owner.domain == "superparty.ro"
        assert owner.path == "/animatori-petreceri-copii"

    def test_get_owner_for_site(self):
        mapper = OwnerMapper()
        owner = mapper.get_owner_for_site("wowparty.ro", "pachete animatori")
        assert owner is not None
        assert owner.path == "/pachete"

    def test_get_all_owners_for_site(self):
        mapper = OwnerMapper()
        an_owners = mapper.get_all_owners_for_site("animatopia.ro")
        assert len(an_owners) == 3  # mascote, tematice, acasa

    def test_is_term_owned_by_other(self):
        mapper = OwnerMapper()
        assert mapper.is_term_owned_by_other("animatori petreceri copii", "wowparty.ro") is True
        assert mapper.is_term_owned_by_other("animatori petreceri copii", "superparty.ro") is False

    def test_register_new_term_succeeds(self):
        mapper = OwnerMapper()
        ok, msg = mapper.register_owner(
            "wowparty.ro", "animatori ieftini", "/animatori-ieftini",
            "Animatori Ieftini | WowParty", "Animatori Ieftini"
        )
        assert ok is True
        assert mapper.is_term_owned("animatori ieftini")

    def test_register_duplicate_term_fails(self):
        mapper = OwnerMapper()
        ok, msg = mapper.register_owner(
            "wowparty.ro", "animatori petreceri copii", "/apc",
            "APC | WP", "APC"
        )
        assert ok is False
        assert "already owned" in msg.lower()

    def test_no_conflicts_in_seed_data(self):
        mapper = OwnerMapper()
        conflicts = mapper.validate_no_conflicts()
        assert len(conflicts) == 0

    def test_conflict_detection_works(self):
        mapper = OwnerMapper()
        # Force a conflict
        mapper._local_cache["wowparty.ro:animatori petreceri copii"] = mapper._local_cache[
            "superparty.ro:animatori petreceri copii"
        ]
        mapper._local_cache["wowparty.ro:animatori petreceri copii"] = type(
            mapper._local_cache["superparty.ro:animatori petreceri copii"]
        )(
            domain="wowparty.ro",
            head_term="animatori petreceri copii",
            path="/apc",
            title="APC | WP",
            h1="APC",
        )
        conflicts = mapper.validate_no_conflicts()
        assert len(conflicts) == 1
        assert "animatori petreceri copii" in conflicts[0]

    def test_ownership_report(self):
        mapper = OwnerMapper()
        report = mapper.get_ownership_report()
        assert len(report) == len(SEED_OWNERS)
        assert all("domain" in r and "head_term" in r for r in report)


# ═══════════════════════════════════════════════════════════════════════════════
# RuleResult
# ═══════════════════════════════════════════════════════════════════════════════

class TestRuleResult:

    def test_default_is_allowed(self):
        r = RuleResult(allowed=True)
        assert r.allowed is True
        assert r.to_dict() == {"allowed": True, "reasons": []}

    def test_deny_changes_allowed(self):
        r = RuleResult(allowed=True)
        r.deny("test reason")
        assert r.allowed is False
        assert "test reason" in r.reasons

    def test_multiple_denials(self):
        r = RuleResult(allowed=True)
        r.deny("reason 1")
        r.deny("reason 2")
        assert r.allowed is False
        assert len(r.reasons) == 2
