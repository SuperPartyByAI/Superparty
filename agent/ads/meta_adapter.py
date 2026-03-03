"""meta_adapter.py - Meta (FB/IG) Ads adapter. Creates PAUSED campaigns only."""
import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

GRAPH_URL = "https://graph.facebook.com/v19.0"


def _api(method, endpoint, params=None, data=None):
    import urllib.request, urllib.error, urllib.parse
    token = os.environ.get("META_ACCESS_TOKEN", "")
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN not set")
    q = urllib.parse.urlencode({"access_token": token})
    url = f"{GRAPH_URL}/{endpoint}?{q}"
    payload = json.dumps(data or {}).encode() if data else None
    req = urllib.request.Request(url, data=payload, method=method,
                                  headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        body = e.read()
        raise RuntimeError(f"Meta API {e.code}: {body.decode()[:200]}")


def load_manifest(manifest_path):
    """Load an ads manifest JSON file."""
    p = Path(manifest_path)
    if not p.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    return json.loads(p.read_text(encoding="utf-8"))


def build_utm_url(landing_page, campaign_name, medium="paid_social", source="facebook"):
    """Build UTM-tagged URL from landing page."""
    import urllib.parse
    params = urllib.parse.urlencode({
        "utm_source": source,
        "utm_medium": medium,
        "utm_campaign": campaign_name.lower().replace(" ", "_")[:50],
    })
    sep = "&" if "?" in landing_page else "?"
    return f"{landing_page}{sep}{params}"


def create_paused_campaign(manifest):
    """
    Create a PAUSED campaign from a manifest dict.
    
    Manifest schema:
      campaign_name: str
      objective: str (OUTCOME_TRAFFIC | OUTCOME_LEADS | OUTCOME_SALES)
      daily_budget_eur: float
      landing_page: str (URL)
      targeting: dict (age_min, age_max, geo_locations, interests)
      creatives: list of {title, body, image_path (optional)}
    
    Returns: dict with campaign_id, adset_id, ad_ids, status=PAUSED
    
    IMPORTANT: All created objects are PAUSED. Publish is MANUAL only.
    """
    ad_account = os.environ.get("META_AD_ACCOUNT", "")
    if not ad_account:
        raise RuntimeError("META_AD_ACCOUNT not set (format: act_123456)")

    campaign_name = manifest["campaign_name"]
    objective = manifest.get("objective", "OUTCOME_TRAFFIC")
    daily_budget_cents = int(manifest.get("daily_budget_eur", 5) * 100)
    landing_page = manifest.get("landing_page", "https://superparty.ro")
    targeting = manifest.get("targeting", {
        "age_min": 18, "age_max": 65,
        "geo_locations": {"countries": ["RO"]},
    })

    # 1. Create Campaign (PAUSED)
    camp, _ = _api("POST", f"{ad_account}/campaigns", data={
        "name": campaign_name,
        "objective": objective,
        "status": "PAUSED",
        "buying_type": "AUCTION",
        "special_ad_categories": [],
    })
    campaign_id = camp.get("id")
    log.info("Campaign created: %s (PAUSED)", campaign_id)

    # 2. Create Ad Set (PAUSED)
    utm_url = build_utm_url(landing_page, campaign_name)
    adset_data = {
        "name": f"{campaign_name} - AdSet",
        "campaign_id": campaign_id,
        "daily_budget": daily_budget_cents,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "LINK_CLICKS",
        "targeting": targeting,
        "status": "PAUSED",
        "promoted_object": {"page_id": os.environ.get("META_PAGE_ID", "")},
    }
    adset, _ = _api("POST", f"{ad_account}/adsets", data=adset_data)
    adset_id = adset.get("id")
    log.info("Ad set created: %s (PAUSED)", adset_id)

    ad_ids = []
    for creative in manifest.get("creatives", [{"title": campaign_name, "body": ""}]):
        # 3. Create Ad Creative
        creative_data = {
            "name": f"{campaign_name} - Creative",
            "object_story_spec": {
                "page_id": os.environ.get("META_PAGE_ID", ""),
                "link_data": {
                    "link": utm_url,
                    "message": creative.get("body", ""),
                    "name": creative.get("title", campaign_name),
                },
            },
        }
        cr, _ = _api("POST", f"{ad_account}/adcreatives", data=creative_data)
        creative_id = cr.get("id")

        # 4. Create Ad (PAUSED)
        ad, _ = _api("POST", f"{ad_account}/ads", data={
            "name": f"{campaign_name} - Ad",
            "adset_id": adset_id,
            "creative": {"creative_id": creative_id},
            "status": "PAUSED",
        })
        ad_ids.append(ad.get("id"))
        log.info("Ad created: %s (PAUSED)", ad.get("id"))

    result = {
        "ok": True,
        "campaign_id": campaign_id,
        "adset_id": adset_id,
        "ad_ids": ad_ids,
        "status": "PAUSED",
        "utm_url": utm_url,
        "note": "All objects PAUSED. Publish is MANUAL only.",
    }

    # Save to reports
    out_dir = Path(f"reports/ads_drafts/{manifest.get('site_id','superparty')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    import datetime as _dt
    out_file = out_dir / f"meta_campaign_{_dt.date.today()}.json"
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    log.info("Saved to %s", out_file)

    return result


def create_from_seo_manifest(manifest_path):
    """
    Create a paused Meta campaign from an SEO-approved manifest file.
    Wrapper for use in agent tasks.
    """
    manifest = load_manifest(manifest_path)
    return create_paused_campaign(manifest)
