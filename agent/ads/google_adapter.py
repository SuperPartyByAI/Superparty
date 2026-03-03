"""google_adapter.py v4 — load_from_env() with correct v25 env var format."""
import logging, os
from datetime import date
log = logging.getLogger(__name__)
API_VERSION = 'v19'


def _load_client():
    from google.ads.googleads.client import GoogleAdsClient
    return GoogleAdsClient.load_from_env(version=API_VERSION)


def _ga_err(ex):
    parts = [f"GoogleAdsException(id={getattr(ex,'request_id','?')})"]
    try:
        for e in ex.failure.errors:
            parts.append(f"  {e.message}")
    except Exception:
        parts.append(str(ex)[:300])
    return "\n".join(parts)


def _create_budget(client, cid, eur):
    from google.ads.googleads.errors import GoogleAdsException
    svc = client.get_service("CampaignBudgetService")
    op = client.get_type("CampaignBudgetOperation")
    b = op.create
    b.name = f"SP budget {date.today()}"
    b.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    b.amount_micros = int(eur * 1_000_000)
    b.explicitly_shared = False
    try:
        return svc.mutate_campaign_budgets(customer_id=cid, operations=[op]).results[0].resource_name
    except GoogleAdsException as ex:
        raise RuntimeError(f"Budget: {_ga_err(ex)}")


def create_search_campaign_paused(manifest, customer_id=None):
    from google.ads.googleads.errors import GoogleAdsException
    cid = (customer_id or os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "")).replace("-", "")
    if not cid: raise EnvironmentError("GOOGLE_ADS_CUSTOMER_ID not set")
    client = _load_client()
    budget_rn = _create_budget(client, cid, manifest.get("daily_budget_eur", 10))
    co = client.get_type("CampaignOperation")
    camp = co.create
    camp.name = manifest["campaign_name"]
    camp.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    camp.status = client.enums.CampaignStatusEnum.PAUSED
    camp.campaign_budget = budget_rn
    camp.network_settings.target_google_search = True
    camp.network_settings.target_search_network = True
    camp.manual_cpc.enhanced_cpc_enabled = True
    try:
        camp_rn = client.get_service("CampaignService").mutate_campaigns(
            customer_id=cid, operations=[co]).results[0].resource_name
        log.info("Campaign: %s", camp_rn)
    except GoogleAdsException as ex:
        raise RuntimeError(f"Campaign: {_ga_err(ex)}")
    ao = client.get_type("AdGroupOperation")
    ag = ao.create
    ag.name = f"{manifest['campaign_name'][:60]} AdG"
    ag.campaign = camp_rn
    ag.status = client.enums.AdGroupStatusEnum.ENABLED
    ag.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    ag.cpc_bid_micros = 400_000
    try:
        ag_rn = client.get_service("AdGroupService").mutate_ad_groups(
            customer_id=cid, operations=[ao]).results[0].resource_name
    except GoogleAdsException as ex:
        raise RuntimeError(f"AdGroup: {_ga_err(ex)}")
    kw_ops = []
    for kw in manifest.get("keywords", []):
        op = client.get_type("AdGroupCriterionOperation")
        op.create.ad_group = ag_rn
        op.create.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        op.create.keyword.text = kw[:80]
        op.create.keyword.match_type = client.enums.KeywordMatchTypeEnum.BROAD
        kw_ops.append(op)
    neg_ops = []
    for neg in manifest.get("negative_keywords", []):
        op = client.get_type("CampaignCriterionOperation")
        op.create.campaign = camp_rn
        op.create.negative = True
        op.create.keyword.text = neg[:80]
        op.create.keyword.match_type = client.enums.KeywordMatchTypeEnum.BROAD
        neg_ops.append(op)
    try:
        if kw_ops: client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(customer_id=cid, operations=kw_ops)
        if neg_ops: client.get_service("CampaignCriterionService").mutate_campaign_criteria(customer_id=cid, operations=neg_ops)
    except GoogleAdsException as ex:
        log.warning("Keywords: %s", _ga_err(ex))
    ad_op = client.get_type("AdGroupAdOperation")
    ad = ad_op.create; ad.ad_group = ag_rn
    ad.status = client.enums.AdGroupAdStatusEnum.PAUSED
    rsa = ad.ad.responsive_search_ad
    for hl in manifest.get("creatives", {}).get("headlines", [])[:3]:
        a = client.get_type("AdTextAsset"); a.text = hl[:30]; rsa.headlines.append(a)
    for desc in manifest.get("creatives", {}).get("descriptions", [])[:2]:
        a = client.get_type("AdTextAsset"); a.text = desc[:90]; rsa.descriptions.append(a)
    rsa.path1 = "animatori"; rsa.path2 = "copii"
    ad.ad.final_urls.append(manifest.get("creatives", {}).get("final_url", "https://superparty.ro"))
    try:
        ad_rn = client.get_service("AdGroupAdService").mutate_ad_group_ads(
            customer_id=cid, operations=[ad_op]).results[0].resource_name
    except GoogleAdsException as ex:
        log.warning("Ad: %s", _ga_err(ex)); ad_rn = "ad_error"
    return {"platform":"google","status":"PAUSED","customer_id":cid,
             "campaign_resource_name":camp_rn,"ad_group_resource_name":ag_rn,
             "ad_resource_name":ad_rn,"budget_resource_name":budget_rn,
             "campaign_name":manifest["campaign_name"],
             "keywords_count":len(kw_ops),"negative_keywords_count":len(neg_ops)}
