"""google_adapter.py - Google Ads API adapter for Superparty agent.

Creates PAUSED Search / PMax campaigns using Google Ads API (google-ads library).

Required env vars:
    GOOGLE_ADS_DEVELOPER_TOKEN  — Google Ads developer token (MCC)
    GOOGLE_ADS_CLIENT_ID        — OAuth2 client ID
    GOOGLE_ADS_CLIENT_SECRET    — OAuth2 client secret
    GOOGLE_ADS_REFRESH_TOKEN    — OAuth2 refresh token
    GOOGLE_ADS_CUSTOMER_ID      — Target account/customer ID (without dashes)
    GOOGLE_ADS_LOGIN_CUSTOMER_ID — MCC customer ID (if using MCC; same as customer_id otherwise)

Installation:
    pip install google-ads==33.0.0

Setup guide: docs/google-ads-setup.md
"""
import json
import logging
import os
import pathlib
from datetime import date
from typing import Optional

log = logging.getLogger(__name__)

# ── Internal helpers ──────────────────────────────────────────────

def _check_env():
    """Raise if required env vars missing."""
    required = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_CUSTOMER_ID",
    ]
    missing = [k for k in required if not os.environ.get(k, "").strip()]
    if missing:
        raise EnvironmentError(f"Missing Google Ads env vars: {missing}")


def _load_client():
    """Load GoogleAdsClient from env vars."""
    _check_env()
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError:
        raise ImportError(
            "google-ads package not installed. Run: pip install google-ads==33.0.0"
        )

    config = {
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "oauth2_client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "oauth2_client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "oauth2_refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "use_proto_plus": True,
    }
    login_cid = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip()
    if login_cid:
        config["login_customer_id"] = login_cid

    return GoogleAdsClient.load_from_dict(config)


def _ga_err(ex) -> str:
    """Format GoogleAdsException to readable string."""
    lines = [f"GoogleAdsException: {ex}"]
    try:
        for error in ex.failure.errors:
            lines.append(f"  Code: {error.error_code}")
            lines.append(f"  Message: {error.message}")
    except Exception:
        pass
    return "\n".join(lines)


# ── Budget ────────────────────────────────────────────────────────

def _create_campaign_budget(client, customer_id: str, budget_eur: float) -> str:
    """Create a non-shared daily campaign budget. Returns resource name."""
    from google.ads.googleads.errors import GoogleAdsException

    budget_service = client.get_service("CampaignBudgetService")
    op = client.get_type("CampaignBudgetOperation")
    budget = op.create
    budget.name = f"Superparty budget {date.today()}"
    budget.delivery_method = (
        client.enums.BudgetDeliveryMethodEnum.STANDARD
    )
    budget.amount_micros = int(budget_eur * 1_000_000)
    budget.explicitly_shared = False

    try:
        resp = budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[op]
        )
        rn = resp.results[0].resource_name
        log.info("Budget created: %s (%.2f EUR/day)", rn, budget_eur)
        return rn
    except GoogleAdsException as ex:
        raise RuntimeError(f"Budget creation failed: {_ga_err(ex)}")


# ── Search Campaign ───────────────────────────────────────────────

def create_search_campaign_paused(manifest: dict, customer_id: str = None) -> dict:
    """
    Create a PAUSED Search campaign from manifest dict.

    Manifest expected keys:
        campaign_name, daily_budget_eur, bidding_strategy (MANUAL_CPC|TARGET_CPA|MAXIMIZE_CONVERSIONS),
        target_cpa_eur (if TARGET_CPA), geo (list of country codes), language (["ro"]),
        keywords (list of str), negative_keywords (list of str),
        creatives: {headlines (3), descriptions (2), final_url}

    Returns dict with resource names and status.
    """
    from google.ads.googleads.errors import GoogleAdsException

    cid = customer_id or os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "")
    if not cid:
        raise EnvironmentError("GOOGLE_ADS_CUSTOMER_ID not set")

    client = _load_client()

    # 1. Budget
    budget_rn = _create_campaign_budget(
        client, cid, manifest.get("daily_budget_eur", 10)
    )

    # 2. Campaign
    campaign_service = client.get_service("CampaignService")
    camp_op = client.get_type("CampaignOperation")
    camp = camp_op.create
    camp.name = manifest["campaign_name"]
    camp.advertising_channel_type = (
        client.enums.AdvertisingChannelTypeEnum.SEARCH
    )
    camp.status = client.enums.CampaignStatusEnum.PAUSED
    camp.campaign_budget = budget_rn
    camp.network_settings.target_google_search = True
    camp.network_settings.target_search_network = True
    camp.network_settings.target_content_network = False

    bidding = manifest.get("bidding_strategy", "MANUAL_CPC")
    if bidding == "TARGET_CPA":
        camp.target_cpa.target_cpa_micros = int(
            manifest.get("target_cpa_eur", 20) * 1_000_000
        )
    elif bidding == "MAXIMIZE_CONVERSIONS":
        camp.maximize_conversions.target_cpa_micros = 0
    else:
        camp.manual_cpc.enhanced_cpc_enabled = True

    # Geo targets (country criterion IDs — RO = 2642)
    GEO_MAP = {"RO": "2642", "MD": "2498", "HU": "2348"}
    geo_targets = manifest.get("geo", ["RO"])
    geo_rns = [
        client.get_service("GeoTargetConstantService").geo_target_constant_path(
            GEO_MAP.get(g, "2642")
        )
        for g in geo_targets
    ]

    try:
        camp_resp = campaign_service.mutate_campaigns(
            customer_id=cid, operations=[camp_op]
        )
        camp_rn = camp_resp.results[0].resource_name
        log.info("Campaign created: %s", camp_rn)
    except GoogleAdsException as ex:
        raise RuntimeError(f"Campaign creation failed: {_ga_err(ex)}")

    # 3. Campaign criteria: geo + language
    try:
        crit_service = client.get_service("CampaignCriterionService")
        crit_ops = []
        for geo_rn in geo_rns:
            op = client.get_type("CampaignCriterionOperation")
            crit = op.create
            crit.campaign = camp_rn
            crit.location.geo_target_constant = geo_rn
            crit_ops.append(op)
        # Language: Romanian = 1056, English = 1000
        lang_op = client.get_type("CampaignCriterionOperation")
        lang_op.create.campaign = camp_rn
        lang_op.create.language.language_constant = (
            client.get_service("LanguageConstantService")
            .language_constant_path("1056")
        )
        crit_ops.append(lang_op)
        if crit_ops:
            crit_service.mutate_campaign_criteria(
                customer_id=cid, operations=crit_ops
            )
    except GoogleAdsException as ex:
        log.warning("Criteria creation warning: %s", _ga_err(ex))

    # 4. AdGroup
    ag_service = client.get_service("AdGroupService")
    ag_op = client.get_type("AdGroupOperation")
    ag = ag_op.create
    ag.name = f"{manifest['campaign_name']} — AdGroup 1"
    ag.campaign = camp_rn
    ag.status = client.enums.AdGroupStatusEnum.ENABLED
    ag.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ag.cpc_bid_micros = 500_000  # 0.50 EUR CPC default

    try:
        ag_resp = ag_service.mutate_ad_groups(
            customer_id=cid, operations=[ag_op]
        )
        ag_rn = ag_resp.results[0].resource_name
    except GoogleAdsException as ex:
        raise RuntimeError(f"AdGroup creation failed: {_ga_err(ex)}")

    # 5. Keywords
    kw_service = client.get_service("AdGroupCriterionService")
    kw_ops = []
    for kw in manifest.get("keywords", []):
        op = client.get_type("AdGroupCriterionOperation")
        cr = op.create
        cr.ad_group = ag_rn
        cr.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        cr.keyword.text = kw
        cr.keyword.match_type = client.enums.KeywordMatchTypeEnum.BROAD
        kw_ops.append(op)
    # Negative keywords at campaign level
    neg_ops = []
    neg_service = client.get_service("CampaignCriterionService")
    for neg_kw in manifest.get("negative_keywords", []):
        op = client.get_type("CampaignCriterionOperation")
        cr = op.create
        cr.campaign = camp_rn
        cr.negative = True
        cr.keyword.text = neg_kw
        cr.keyword.match_type = client.enums.KeywordMatchTypeEnum.BROAD
        neg_ops.append(op)

    try:
        if kw_ops:
            kw_service.mutate_ad_group_criteria(customer_id=cid, operations=kw_ops)
        if neg_ops:
            neg_service.mutate_campaign_criteria(customer_id=cid, operations=neg_ops)
        log.info("Keywords added: %d pos, %d neg", len(kw_ops), len(neg_ops))
    except GoogleAdsException as ex:
        log.warning("Keyword warning: %s", _ga_err(ex))

    # 6. Responsive Search Ad
    creatives = manifest.get("creatives", {})
    final_url = creatives.get("final_url", "https://superparty.ro")
    headlines_raw = creatives.get("headlines", [])[:3]
    descriptions_raw = creatives.get("descriptions", [])[:2]

    ad_service = client.get_service("AdGroupAdService")
    ad_op = client.get_type("AdGroupAdOperation")
    ad = ad_op.create
    ad.ad_group = ag_rn
    ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
    rsa = ad.ad.responsive_search_ad
    for i, hl in enumerate(headlines_raw):
        asset = client.get_type("AdTextAsset")
        asset.text = hl[:30]  # max 30 chars for Google RSA headline
        if i < 3:
            asset.pinned_field = getattr(
                client.enums.ServedAssetFieldTypeEnum, f"HEADLINE_{i+1}", None
            ) or client.enums.ServedAssetFieldTypeEnum.UNSPECIFIED
        rsa.headlines.append(asset)
    for desc in descriptions_raw:
        asset = client.get_type("AdTextAsset")
        asset.text = desc[:90]  # max 90 chars
        rsa.descriptions.append(asset)
    rsa.path1 = "animatori"
    rsa.path2 = "copii"
    ad.ad.final_urls.append(final_url)

    try:
        ad_resp = ad_service.mutate_ad_group_ads(
            customer_id=cid, operations=[ad_op]
        )
        ad_rn = ad_resp.results[0].resource_name
        log.info("Ad created: %s", ad_rn)
    except GoogleAdsException as ex:
        log.warning("Ad creation warning: %s", _ga_err(ex))
        ad_rn = "error"

    return {
        "platform": "google",
        "status": "PAUSED",
        "customer_id": cid,
        "campaign_resource_name": camp_rn,
        "ad_group_resource_name": ag_rn,
        "ad_resource_name": ad_rn,
        "budget_resource_name": budget_rn,
        "campaign_name": manifest["campaign_name"],
        "keywords_count": len(kw_ops),
        "negative_keywords_count": len(neg_ops),
    }
