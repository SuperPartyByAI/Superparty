"""ads_google.py - Agent task for Google Ads campaign creation.

Reads site config (keyword_seeds, promotion accent) → builds Google Ads manifest
→ (dry_run=False) creates PAUSED campaign via google_adapter.

Usage:
    docker exec -it sp_worker_ads python3 -c \
        "from agent.tasks.ads_google import google_ads_plan_task; import json; \
         print(json.dumps(google_ads_plan_task(dry_run=True), indent=2))"
"""
import json
import logging
import os
from datetime import date
from pathlib import Path

log = logging.getLogger(__name__)


def _build_manifest(site: dict, accent: str = None) -> dict:
    """Build a Google Ads Search campaign manifest from site config."""
    promo = site.get("promotion", {})
    ks = site.get("keyword_seeds", {})
    creative_cfg = site.get("creative", {})
    audience = site.get("audience", {})
    domain = site.get("domain", {})

    accent = accent or promo.get("accent", "general")

    # Keywords from seeds
    primary_kws = ks.get("primary", [])
    accent_kws = ks.get(f"{accent}_specific", ks.get("kids_specific", []))
    local_kws = ks.get("local_variants", [])
    all_kws = list(dict.fromkeys(primary_kws + accent_kws + local_kws))[:20]  # max 20

    neg_kws = ks.get("negative_keywords", [])
    forbidden = creative_cfg.get("forbidden_phrases", [])
    # Remove any forbidden terms that snuck into keywords
    all_kws = [k for k in all_kws if not any(f.lower() in k.lower() for f in forbidden)]

    # Landing page
    landing_pages = creative_cfg.get("landing_pages", {})
    final_url = landing_pages.get(accent, creative_cfg.get("landing_page_default",
        domain.get("primary", "https://superparty.ro")))
    final_url_utm = final_url + f"?utm_source=google&utm_medium=cpc&utm_campaign={accent}"

    # Budget
    budget_eur = promo.get("budget", {}).get("campaign_daily_default_eur", 10)
    cpa_eur = promo.get("cpa_target_eur", 20)

    # Creatives — placeholders (LLM would generate, but for Google RSA: max 30 chars headline, 90 desc)
    cta = creative_cfg.get("cta", "Solicita oferta")
    headlines = [
        "Animatori petreceri copii",
        "Petreceri copii Bucuresti",
        "Oferta animatori copii",
    ]
    descriptions = [
        "Animatori profesionisti petreceri copii Bucuresti. Solicita oferta azi!",
        "Pachete complete animatori copii – distractie garantata pentru copilul tau.",
    ]

    return {
        "platform": "google",
        "type": "search",
        "campaign_name": f"Superparty — {accent.title()} Search ({date.today()})",
        "daily_budget_eur": budget_eur,
        "bidding_strategy": "MANUAL_CPC",
        "target_cpa_eur": cpa_eur,
        "geo": audience.get("geos", ["RO"]),
        "language": audience.get("languages", ["ro"]),
        "keywords": all_kws,
        "negative_keywords": neg_kws,
        "creatives": {
            "headlines": headlines,
            "descriptions": descriptions,
            "final_url": final_url_utm,
            "cta": cta,
        },
        "accent": accent,
        "created_at": date.today().isoformat(),
        "status": "PAUSED",
    }


def google_ads_plan_task(site_id: str = "superparty",
                          accent: str = None,
                          dry_run: bool = True) -> dict:
    """
    Google Ads plan task.

    Steps:
      1. Load site config (keyword_seeds, promotion accent)
      2. Build Google Ads Search campaign manifest
      3. Validate keywords (forbidden phrases, budget caps)
      4. Write manifest to reports/ads_drafts/<site_id>/
      5. If dry_run=False and creds available: create PAUSED campaign via google_adapter

    Returns: {"ok": bool, "manifest": dict, "google_result": dict|None}
    """
    # Load site
    try:
        from agent.services.site_loader import get_site
        site = get_site(site_id)
    except Exception as e:
        return {"ok": False, "error": f"site_loader: {e}"}

    # Guardrails
    promo = site.get("promotion", {})
    budget_cap = promo.get("budget", {}).get("account_daily_cap_eur", 50)
    daily_budget = promo.get("budget", {}).get("campaign_daily_default_eur", 10)
    if daily_budget > budget_cap:
        return {"ok": False, "error": f"Budget {daily_budget} exceeds cap {budget_cap}"}

    # Build manifest
    manifest = _build_manifest(site, accent)

    # Write manifest
    out_dir = Path(f"reports/ads_drafts/{site_id}")
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"ads_plan_google_{date.today()}_{manifest['accent']}.json"
    out_path = out_dir / fname
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Google Ads manifest written: %s", out_path)

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "manifest_path": str(out_path),
            "manifest": manifest,
            "note": "dry_run — no Google Ads API call",
            "keywords_count": len(manifest["keywords"]),
            "campaign_name": manifest["campaign_name"],
        }

    # Live — check env vars
    missing = [k for k in [
        "GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET", "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_CUSTOMER_ID",
    ] if not os.environ.get(k, "").strip()]

    if missing:
        return {
            "ok": False,
            "dry_run": False,
            "manifest_path": str(out_path),
            "error": f"Missing env vars: {missing}",
            "note": "Add to .env.agent and restart sp_worker_ads",
        }

    # Create PAUSED campaign
    try:
        from agent.ads.google_adapter import create_search_campaign_paused
        result = create_search_campaign_paused(manifest)

        # Write created_paused report
        cp_path = out_dir / f"created_paused_google_{date.today()}_{manifest['accent']}.json"
        cp_path.write_text(
            json.dumps({"manifest": manifest, "google": result}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        log.info("Google campaign created: %s", result.get("campaign_resource_name"))

        return {
            "ok": True,
            "dry_run": False,
            "manifest_path": str(out_path),
            "campaign_name": result["campaign_name"],
            "campaign_resource_name": result["campaign_resource_name"],
            "status": "PAUSED",
            "keywords_count": result["keywords_count"],
            "note": "campaign_created_paused — review in Google Ads Manager",
        }
    except Exception as e:
        log.error("Google Ads error: %s", e)
        return {"ok": False, "error": str(e), "manifest_path": str(out_path)}
