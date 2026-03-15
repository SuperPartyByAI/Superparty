"""
test_template_engine.py — Tests for JSON-LD template generation.

test_pr_generator.py — Tests for PR generation (dry-run mode).
test_monitor.py — Tests for owner_share calculation and alerting.
"""
import json
import pytest

from agent.seo_agent.template_engine import (
    OwnerPageData,
    PackageOffer,
    FAQItem,
    generate_local_business,
    generate_offer_catalog,
    generate_faq_page,
    generate_breadcrumb,
    generate_combined_jsonld,
    generate_meta_title,
    generate_meta_description,
    generate_internal_link_html,
    validate_jsonld,
)
from agent.seo_agent.pr_generator import (
    PRRequest,
    generate_branch_name,
    generate_pr_body,
    generate_pr,
)
from agent.seo_agent.monitor import (
    PageMetrics,
    OwnerShareResult,
    AlertThresholds,
    AlertResult,
    calculate_owner_share,
    check_thresholds,
    parse_gsc_response,
    generate_daily_report,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Template Engine — JSON-LD
# ═══════════════════════════════════════════════════════════════════════════════

SAMPLE_DATA = OwnerPageData(
    brand="SuperParty",
    domain="superparty.ro",
    path="/animatori-petreceri-copii",
    phone="+40722744377",
    head_term="animatori petreceri copii",
    h1="Animatori Petreceri Copii",
    city="București",
    area="Ilfov",
    rating="5.0",
    review_count="1498",
    event_count="10.000+",
    packages=[
        PackageOffer("Super 1", "490", "RON", "1 Personaj, 2 ore"),
        PackageOffer("Super 3", "840", "RON", "2 Personaje, 2 ore"),
        PackageOffer("Super 7", "1290", "RON", "1 Animator + 4 Ursitoare"),
    ],
    faqs=[
        FAQItem("Ce acoperire geografică aveți?", "Acoperim Bucureștiul și Ilfov."),
        FAQItem("Materialele sunt sigure?", "Da, folosim culori certificate."),
    ],
)


class TestLocalBusiness:

    def test_basic_structure(self):
        lb = generate_local_business(SAMPLE_DATA)
        assert lb["@context"] == "https://schema.org"
        assert lb["@type"] == "LocalBusiness"
        assert lb["name"] == "SuperParty"
        assert lb["telephone"] == "+40722744377"

    def test_url_correct(self):
        lb = generate_local_business(SAMPLE_DATA)
        assert lb["url"] == "https://www.superparty.ro/animatori-petreceri-copii"

    def test_area_served(self):
        lb = generate_local_business(SAMPLE_DATA)
        assert len(lb["areaServed"]) == 2
        assert lb["areaServed"][0]["name"] == "București"

    def test_aggregate_rating(self):
        lb = generate_local_business(SAMPLE_DATA)
        assert lb["aggregateRating"]["ratingValue"] == "5.0"
        assert lb["aggregateRating"]["reviewCount"] == "1498"

    def test_price_range(self):
        lb = generate_local_business(SAMPLE_DATA)
        assert lb["priceRange"] == "490-1290 RON"

    def test_no_rating_when_empty(self):
        data = OwnerPageData(
            brand="T", domain="t.ro", path="/t", phone="+40",
            head_term="t", h1="T", rating="", review_count=""
        )
        lb = generate_local_business(data)
        assert "aggregateRating" not in lb


class TestOfferCatalog:

    def test_generates_offers(self):
        cat = generate_offer_catalog(SAMPLE_DATA)
        assert cat is not None
        assert cat["@type"] == "OfferCatalog"
        assert len(cat["itemListElement"]) == 3

    def test_offer_prices(self):
        cat = generate_offer_catalog(SAMPLE_DATA)
        prices = [o["price"] for o in cat["itemListElement"]]
        assert "490" in prices
        assert "1290" in prices

    def test_no_offers_returns_none(self):
        data = OwnerPageData(
            brand="T", domain="t.ro", path="/t", phone="+40",
            head_term="t", h1="T"
        )
        assert generate_offer_catalog(data) is None


class TestFAQPage:

    def test_generates_faqs(self):
        faq = generate_faq_page(SAMPLE_DATA)
        assert faq is not None
        assert faq["@type"] == "FAQPage"
        assert len(faq["mainEntity"]) == 2

    def test_no_faqs_returns_none(self):
        data = OwnerPageData(
            brand="T", domain="t.ro", path="/t", phone="+40",
            head_term="t", h1="T"
        )
        assert generate_faq_page(data) is None


class TestCombinedJsonld:

    def test_produces_valid_json(self):
        jsonld = generate_combined_jsonld(SAMPLE_DATA)
        data = json.loads(jsonld)
        assert isinstance(data, list)

    def test_contains_all_schemas(self):
        jsonld = generate_combined_jsonld(SAMPLE_DATA)
        data = json.loads(jsonld)
        types = [s["@type"] for s in data]
        assert "LocalBusiness" in types
        assert "FAQPage" in types
        assert "BreadcrumbList" in types

    def test_local_business_has_offer_catalog(self):
        jsonld = generate_combined_jsonld(SAMPLE_DATA)
        data = json.loads(jsonld)
        lb = [s for s in data if s["@type"] == "LocalBusiness"][0]
        assert "hasOfferCatalog" in lb

    def test_validates_successfully(self):
        jsonld = generate_combined_jsonld(SAMPLE_DATA)
        valid, errors = validate_jsonld(jsonld)
        assert valid is True, f"Validation errors: {errors}"


class TestMetaGeneration:

    def test_meta_title(self):
        title = generate_meta_title(SAMPLE_DATA)
        assert "SuperParty" in title
        assert "București" in title

    def test_meta_description_has_ctr_triggers(self):
        desc = generate_meta_description(SAMPLE_DATA)
        assert "490" in desc  # price
        assert "5.0" in desc  # rating
        assert "+40722744377" in desc  # phone CTA

    def test_custom_overrides(self):
        data = OwnerPageData(
            brand="T", domain="t.ro", path="/t", phone="+40",
            head_term="t", h1="T",
            meta_title="Custom Title",
            meta_description="Custom Desc"
        )
        assert generate_meta_title(data) == "Custom Title"
        assert generate_meta_description(data) == "Custom Desc"


class TestValidation:

    def test_valid_jsonld_passes(self):
        valid, errors = validate_jsonld(generate_combined_jsonld(SAMPLE_DATA))
        assert valid is True

    def test_invalid_json_fails(self):
        valid, errors = validate_jsonld("{broken")
        assert valid is False
        assert "Invalid JSON" in errors[0]

    def test_missing_type_reported(self):
        valid, errors = validate_jsonld(json.dumps([{"@context": "https://schema.org"}]))
        assert valid is False


class TestInternalLinkHtml:

    def test_basic_link(self):
        html = generate_internal_link_html("/animatori-petreceri-copii/", "animatori petreceri copii")
        assert 'href="/animatori-petreceri-copii/"' in html
        assert "animatori petreceri copii" in html

    def test_with_context(self):
        html = generate_internal_link_html("/apc/", "animatori", "Vezi și")
        assert "Vezi și" in html
        assert "<p" in html


# ═══════════════════════════════════════════════════════════════════════════════
# PR Generator
# ═══════════════════════════════════════════════════════════════════════════════

class TestPRGenerator:

    def test_branch_name_format(self):
        name = generate_branch_name("superparty.ro", "animatori-petreceri-copii")
        assert name.startswith("agent/seo/superparty-owner-")
        assert "animatori-petreceri-copii" in name

    def test_pr_body_has_checklist(self):
        req = PRRequest(
            site_domain="superparty.ro",
            head_term="animatori petreceri copii",
            slug="animatori-petreceri-copii",
            files_changed=["src/pages/animatori-petreceri-copii/index.astro"],
        )
        body = generate_pr_body(req)
        assert "Automated Checklist" in body
        assert "- [ ] Title & H1" in body
        assert "- [ ] JSON-LD" in body
        assert "- [ ] Canonical" in body
        assert "- [ ] Sitemap updated" in body
        assert "- [ ] Freeze check" in body

    def test_pr_body_includes_files(self):
        req = PRRequest(
            site_domain="animatopia.ro",
            head_term="mascote",
            slug="mascote",
            files_changed=["src/pages/mascote/index.astro", "public/sitemap.xml"],
        )
        body = generate_pr_body(req)
        assert "src/pages/mascote/index.astro" in body
        assert "public/sitemap.xml" in body

    def test_dry_run_succeeds(self):
        req = PRRequest(
            site_domain="animatopia.ro",
            head_term="mascote",
            slug="mascote",
        )
        result = generate_pr(req, repo_dir=".", dry_run=True)
        assert result.success is True
        assert result.branch_name.startswith("agent/seo/")
        assert "Automated Checklist" in result.pr_body


# ═══════════════════════════════════════════════════════════════════════════════
# Monitor — owner_share calculation
# ═══════════════════════════════════════════════════════════════════════════════

class TestOwnerShare:

    def test_basic_calculation(self):
        """Day 2 scenario: homepage 354 impr vs owner 223 impr."""
        metrics = [
            PageMetrics(url="/", impressions=354, clicks=0, ctr=0.0, avg_position=12.7),
            PageMetrics(url="/animatori-petreceri-copii", impressions=223, clicks=3, ctr=0.013, avg_position=12.8),
        ]
        result = calculate_owner_share(metrics, "/animatori-petreceri-copii")
        assert result.owner_share == pytest.approx(223 / 577, rel=0.01)
        assert result.owner_impressions == 223
        assert result.homepage_impressions == 354

    def test_full_urls(self):
        """Handle full URLs from GSC."""
        metrics = [
            PageMetrics(url="https://www.superparty.ro/", impressions=100, clicks=0),
            PageMetrics(url="https://www.superparty.ro/animatori-petreceri-copii", impressions=200, clicks=5),
        ]
        result = calculate_owner_share(metrics, "/animatori-petreceri-copii")
        assert result.owner_share == pytest.approx(200 / 300, rel=0.01)

    def test_zero_impressions(self):
        result = calculate_owner_share([], "/animatori-petreceri-copii")
        assert result.owner_share == 0.0

    def test_owner_only_is_100pct(self):
        metrics = [
            PageMetrics(url="/animatori-petreceri-copii", impressions=500, clicks=50),
        ]
        result = calculate_owner_share(metrics, "/animatori-petreceri-copii")
        assert result.owner_share == 1.0

    def test_trailing_slash_normalized(self):
        metrics = [
            PageMetrics(url="/animatori-petreceri-copii/", impressions=200, clicks=5),
            PageMetrics(url="/", impressions=100),
        ]
        result = calculate_owner_share(metrics, "/animatori-petreceri-copii")
        assert result.owner_impressions == 200


class TestAlertThresholds:

    def test_ok_when_above_target(self):
        current = OwnerShareResult(owner_share=0.65)
        alert = check_thresholds(current)
        assert alert.severity == "ok"
        assert not alert.has_alerts

    def test_warning_below_target(self):
        current = OwnerShareResult(owner_share=0.45)
        alert = check_thresholds(current)
        assert alert.severity == "warning"
        assert alert.has_alerts

    def test_critical_below_minimum(self):
        current = OwnerShareResult(owner_share=0.20)
        alert = check_thresholds(current)
        assert alert.severity == "critical"

    def test_ctr_regression_detected(self):
        baseline = OwnerShareResult(owner_ctr=0.02, owner_share=0.5)
        current = OwnerShareResult(owner_ctr=0.01, owner_share=0.5)
        alert = check_thresholds(current, baseline=baseline)
        assert alert.has_alerts
        assert any("CTR" in a for a in alert.alerts)

    def test_clicks_regression_detected(self):
        baseline = OwnerShareResult(owner_clicks=10, owner_share=0.5)
        current = OwnerShareResult(owner_clicks=5, owner_share=0.5)
        alert = check_thresholds(current, baseline=baseline)
        assert alert.has_alerts

    def test_custom_thresholds(self):
        current = OwnerShareResult(owner_share=0.35)
        custom = AlertThresholds(min_owner_share=0.40)
        alert = check_thresholds(current, thresholds=custom)
        assert alert.severity == "critical"


class TestGSCParsing:

    def test_parse_rows(self):
        rows = [
            {"keys": ["https://www.superparty.ro/"], "impressions": 354, "clicks": 0, "ctr": 0, "position": 12.7},
            {"keys": ["https://www.superparty.ro/animatori-petreceri-copii"], "impressions": 223, "clicks": 3, "ctr": 0.013, "position": 12.8},
        ]
        metrics = parse_gsc_response(rows, "animatori petreceri copii")
        assert len(metrics) == 2
        assert metrics[0].impressions == 354
        assert metrics[1].clicks == 3


class TestDailyReport:

    def test_report_structure(self):
        share = OwnerShareResult(
            owner_impressions=223, homepage_impressions=354,
            owner_share=0.386, owner_clicks=3, owner_ctr=0.013,
            owner_position=12.8, homepage_position=12.7,
        )
        alert = AlertResult(severity="warning", alerts=["below target"])
        alert.has_alerts = True

        report = generate_daily_report("superparty.ro", "animatori petreceri copii", share, alert)
        assert report["owner_share"] == 38.6
        assert report["verdict"] == "warning"
        assert report["site"] == "superparty.ro"
