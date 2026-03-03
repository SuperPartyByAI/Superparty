"""ads_manager.py - Create campaign manifests using site promotion config.

Reads site YAML (accent, audience, creative) → calls LLM for copy →
builds validated manifest → writes to reports/ads_drafts/<site_id>/
"""
import json
import logging
import os
import re
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

SITES_DIR = Path("agent/sites")
REPORTS_DIR = Path("reports")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://sp_ollama:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")


def _load_site(site_id: str) -> dict:
    """Load site YAML config. Falls back to minimal dict if yaml not installed."""
    yml_path = SITES_DIR / f"{site_id}.yml"
    if not yml_path.exists():
        raise FileNotFoundError(f"Site config not found: {yml_path}")
    try:
        import yaml
        return yaml.safe_load(yml_path.read_text(encoding="utf-8"))
    except ImportError:
        # minimal parser for simple YAML
        data: dict = {}
        for line in yml_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and ":" in line and not line.startswith("-"):
                k, _, v = line.partition(":")
                v = v.strip().strip('"').strip("'")
                if v:
                    data[k.strip()] = v
        return data


def _call_llm(prompt: str, model: str = None) -> str:
    """Call Ollama LLM and return generated text."""
    m = model or LLM_MODEL
    url = f"{OLLAMA_URL}/api/generate"
    payload = json.dumps({"model": m, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        data = json.loads(resp.read())
        return data.get("response", "").strip()
    except Exception as e:
        log.warning("LLM call failed: %s — using fallback", e)
        return ""


def _validate_creative(headlines: list, descriptions: list, forbidden: list,
                        max_h: int, max_d: int) -> tuple:
    """Validate creative copy. Returns (ok, errors)."""
    errors = []
    for h in headlines:
        if len(h) > max_h:
            errors.append(f"Headline too long ({len(h)}>{max_h}): {h[:30]}...")
        for f in forbidden:
            if f.lower() in h.lower():
                errors.append(f"Forbidden phrase in headline: {f!r}")
    for d in descriptions:
        if len(d) > max_d:
            errors.append(f"Description too long ({len(d)}>{max_d}): {d[:30]}...")
        for f in forbidden:
            if f.lower() in d.lower():
                errors.append(f"Forbidden phrase in description: {f!r}")
    return len(errors) == 0, errors


def generate_creative_copy(site: dict, accent: str = None) -> dict:
    """Generate headlines + descriptions via LLM using site accent config."""
    promo = site.get("promotion", {})
    creative = site.get("creative", {})
    domain = site.get("domain", {})
    audience = site.get("audience", {})

    effective_accent = accent or promo.get("accent", "general")
    tone = creative.get("tone", "professional")
    style = creative.get("style", "dynamic")
    forbidden = creative.get("forbidden_phrases", [])
    cta = creative.get("cta", "Afla mai mult")
    max_h = creative.get("max_headline_chars", 60)
    max_d = creative.get("max_description_chars", 155)
    kpi = promo.get("primary_kpi", "lead")
    cpa = promo.get("cpa_target_eur", 0)
    industry = domain.get("industry", "events")
    activity = domain.get("domain_of_activity", "events")
    persona = audience.get("primary", "general")

    prompt = f"""You are a copywriter for {industry} ({activity}), targeting {persona}.
Accent: {effective_accent}. Tone: {tone}. Style: {style}.
Objective: {kpi} (CPA target: {cpa} EUR). CTA: {cta}.
Forbidden phrases: {', '.join(forbidden)}.
Language: Romanian (ro).

Generate exactly 3 headlines and 3 descriptions for a Facebook/Instagram ad.
Headlines must be <= {max_h} characters. Descriptions must be <= {max_d} characters.
No testimonials, no guarantees, no superlatives.
Respond ONLY with valid JSON, no explanation:
{{
  "headlines": ["...", "...", "..."],
  "descriptions": ["...", "...", "..."],
  "cta": "{cta}"
}}"""

    raw = _call_llm(prompt)

    # Parse JSON from LLM response
    try:
        m = re.search(r"\{[\s\S]+\}", raw)
        if m:
            data = json.loads(m.group())
            headlines = data.get("headlines", [])
            descriptions = data.get("descriptions", [])
        else:
            raise ValueError("No JSON found")
    except Exception as e:
        log.warning("LLM JSON parse failed: %s — using fallback copy", e)
        headlines = [
            f"Organizăm {effective_accent} de neuitat",
            f"Evenimente {effective_accent} personalizate",
            f"Petrecerea perfectă pentru echipa ta",
        ]
        descriptions = [
            f"Superparty organizează evenimente {effective_accent} complete. Solicită ofertă gratuită.",
            f"De la corporate la private — pachetele noastre includ tot. {cta} azi.",
            f"Evenimente memorabile în București. Experiență, creativitate, profesionalism.",
        ]

    # Validate
    ok, errors = _validate_creative(headlines, descriptions, forbidden, max_h, max_d)
    if not ok:
        log.warning("Creative validation errors: %s", errors)

    return {
        "headlines": headlines[:3],
        "descriptions": descriptions[:3],
        "cta": cta,
        "validation_ok": ok,
        "validation_errors": errors,
        "accent": effective_accent,
        "tone": tone,
    }


def create_campaign_manifest_for_site(site_id: str, accent: str = None,
                                        dry_run: bool = False) -> dict:
    """
    Build a complete campaign manifest for site_id using promotion config.

    Returns manifest dict and writes to reports/ads_drafts/<site_id>/.
    """
    site = _load_site(site_id)
    promo = site.get("promotion", {})
    audience = site.get("audience", {})
    creative_cfg = site.get("creative", {})
    ads_cfg = site.get("ads", {})
    domain = site.get("domain", {})

    effective_accent = accent or promo.get("accent", "general")
    kpi = promo.get("primary_kpi", "lead")
    daily_budget = promo.get("budget", {}).get("campaign_daily_default_eur", 10)
    canary_daily = promo.get("canary_daily_eur", daily_budget)
    canary_days = promo.get("canary_days", 7)
    site_url = site.get("domain", {}).get("primary", "https://superparty.ro")

    # Landing page by accent
    landing_pages = creative_cfg.get("landing_pages", {})
    landing_page = landing_pages.get(effective_accent,
                   creative_cfg.get("landing_page_default", site_url + "/contact"))

    # Objective mapping
    obj_map = ads_cfg.get("objective_map", {
        "lead": "OUTCOME_LEADS",
        "booking": "OUTCOME_TRAFFIC",
        "ticket_sales": "OUTCOME_SALES",
        "awareness": "OUTCOME_AWARENESS",
    })
    objective = obj_map.get(kpi, "OUTCOME_TRAFFIC")

    # Targeting
    targeting = {
        "age_min": audience.get("age_range", [25, 55])[0],
        "age_max": audience.get("age_range", [25, 55])[1],
        "geo_locations": {"countries": audience.get("geos", ["RO"])},
        "locales": audience.get("languages", ["ro"]),
    }
    interests = audience.get("interests", [])
    if interests:
        targeting["interests"] = [{"name": i} for i in interests]

    # Generate copy
    log.info("Generating creative copy via LLM (accent=%s)...", effective_accent)
    copy = generate_creative_copy(site, effective_accent)

    manifest = {
        "site_id": site_id,
        "campaign_name": f"Superparty — {effective_accent.title()} ({date.today()})",
        "accent": effective_accent,
        "objective": objective,
        "primary_kpi": kpi,
        "cpa_target_eur": promo.get("cpa_target_eur", 0),
        "daily_budget_eur": canary_daily,  # canary first
        "canary_days": canary_days,
        "landing_page": landing_page,
        "targeting": targeting,
        "creatives": [
            {
                "title": copy["headlines"][i] if i < len(copy["headlines"]) else "",
                "body": copy["descriptions"][i] if i < len(copy["descriptions"]) else "",
                "cta": copy["cta"],
            }
            for i in range(3)
        ],
        "platforms": ads_cfg.get("default_platforms", ["meta"]),
        "placements": ads_cfg.get("placements", ["feed", "stories"]),
        "status": "PAUSED",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
        "copy_validation_ok": copy["validation_ok"],
        "copy_validation_errors": copy["validation_errors"],
        "dry_run": dry_run,
    }

    # Write to reports
    out_dir = REPORTS_DIR / "ads_drafts" / site_id
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today()
    fname = f"ads_plan_{today}_{effective_accent}.json"
    out_path = out_dir / fname
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Manifest written: %s", out_path)

    manifest["manifest_path"] = str(out_path)
    return {"ok": True, "manifest": manifest, "path": str(out_path)}


# Import datetime here for use inside function
import datetime  # noqa: E402 (needed for utcnow in manifest)
