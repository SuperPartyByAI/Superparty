"""ads_google.py — Google Ads plan task."""
import json, logging, os, re
from datetime import date
from pathlib import Path

log = logging.getLogger(__name__)


def _build_manifest(site, accent=None):
    promo = site.get("promotion", {})
    ks = site.get("keyword_seeds", {})
    creative_cfg = site.get("creative", {})
    audience = site.get("audience", {})
    domain = site.get("domain", {})
    accent = accent or promo.get("accent", "kids")
    primary_kws = ks.get("primary", [])
    accent_kws = ks.get(accent + "_specific", ks.get("kids_specific", []))
    local_kws = ks.get("local_variants", [])
    forbidden = creative_cfg.get("forbidden_phrases", [])
    all_kws = list(dict.fromkeys(primary_kws + accent_kws + local_kws))[:20]
    all_kws = [k for k in all_kws if not any(f.lower() in k.lower() for f in forbidden)]
    neg_kws = ks.get("negative_keywords", [])
    landing_pages = creative_cfg.get("landing_pages", {})
    base_url = domain.get("primary", "https://superparty.ro") if isinstance(domain, dict) else "https://superparty.ro"
    final_url = landing_pages.get(accent, base_url)
    final_url_utm = final_url + "?utm_source=google&utm_medium=cpc&utm_campaign=" + accent
    budget_eur = promo.get("budget", {}).get("campaign_daily_default_eur", 10)
    return {
        "platform": "google", "type": "search",
        "campaign_name": f"Superparty — {accent.title()} Search ({date.today()})",
        "daily_budget_eur": budget_eur,
        "geo": audience.get("geos", ["RO"]),
        "language": audience.get("languages", ["ro"]),
        "keywords": all_kws, "negative_keywords": neg_kws,
        "creatives": {
            "headlines": ["Animatori petreceri copii", "Petreceri copii Bucuresti", "Oferta animatori copii"],
            "descriptions": [
                "Animatori profesionisti petreceri copii. Solicita oferta azi!",
                "Pachete complete animatori copii – distractie garantata.",
            ],
            "final_url": final_url_utm, "cta": "Solicita oferta",
        },
        "accent": accent, "created_at": date.today().isoformat(), "status": "PAUSED",
    }


def google_ads_plan_task(site_id="superparty", accent=None, dry_run=True):
    """Build manifest and optionally create PAUSED Google Ads Search campaign."""
    try:
        from agent.services.site_loader import get_site
        site = get_site(site_id)
    except Exception as e:
        return {"ok": False, "error": f"site_loader: {e}"}

    promo = site.get("promotion", {})
    budget_cap = promo.get("budget", {}).get("account_daily_cap_eur", 50)
    daily_budget = promo.get("budget", {}).get("campaign_daily_default_eur", 10)
    if daily_budget > budget_cap:
        return {"ok": False, "error": f"Budget {daily_budget} exceeds cap {budget_cap}"}

    manifest = _build_manifest(site, accent)
    out_dir = Path(f"reports/ads_drafts/{site_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"ads_plan_google_{date.today()}_{manifest['accent']}.json"
    out_path = out_dir / fname
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    if dry_run:
        return {
            "ok": True, "dry_run": True, "manifest_path": str(out_path),
            "note": "dry_run — no Google Ads API call",
            "keywords_count": len(manifest["keywords"]),
            "campaign_name": manifest["campaign_name"],
        }

    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "8598361550")
    try:
        from agent.ads.google_adapter import create_search_campaign_paused
        result = create_search_campaign_paused(manifest, customer_id=customer_id)
        cp_path = out_dir / f"created_paused_google_{date.today()}_{manifest['accent']}.json"
        cp_path.write_text(json.dumps({"manifest": manifest, "google": result},
                                       indent=2, ensure_ascii=False), encoding="utf-8")
        return {
            "ok": True, "dry_run": False, "manifest_path": str(out_path),
            "campaign_name": result["campaign_name"],
            "campaign_resource_name": result["campaign_resource_name"],
            "status": "PAUSED", "keywords_count": result["keywords_count"],
        }
    except Exception as e:
        log.error("Google Ads error: %s", e)
        return {"ok": False, "error": str(e), "manifest_path": str(out_path)}
