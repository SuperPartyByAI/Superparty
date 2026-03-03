"""ads.py - Agent task for ads planning and campaign creation.

Tasks:
    ads_plan_task(site_id, accent) → create manifest, open PR if approved
    ads_status_task(site_id) → check spend vs cap, report in Slack
"""
import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


def ads_plan_task(site_id: str = "superparty", accent: str = None,
                  dry_run: bool = True) -> dict:
    """
    Generate an ads campaign manifest from site promotion config.

    Steps:
      1. Load site config (promotion accent, audience, creative)
      2. Call LLM for copy generation (headlines + descriptions)
      3. Validate creative (forbidden phrases, char limits)
      4. Write manifest to reports/ads_drafts/<site_id>/
      5. If ads.enabled and not dry_run: create PAUSED campaign via meta_adapter
      6. Create GitHub PR with manifest for human review

    Args:
        site_id: site identifier (must have agent/sites/<site_id>.yml)
        accent: override accent (default: site config promotion.accent)
        dry_run: if True, skip actual Meta API call (default: True)

    Returns: {"ok": True, "manifest_path": str, "pr_url": str | None}
    """
    try:
        from agent.ads.ads_manager import create_campaign_manifest_for_site
    except ImportError as e:
        return {"ok": False, "error": f"import error: {e}"}

    try:
        result = create_campaign_manifest_for_site(
            site_id=site_id,
            accent=accent,
            dry_run=dry_run,
        )
    except Exception as e:
        log.error("ads_plan_task failed: %s", e)
        return {"ok": False, "error": str(e)}

    manifest = result.get("manifest", {})
    path = result.get("path", "")
    log.info("Manifest created: %s (validation_ok=%s)",
             path, manifest.get("copy_validation_ok"))

    # If ads not enabled or dry_run: just return manifest path (PR optional)
    from agent.services.site_loader import get_site
    site = get_site(site_id)
    ads_enabled = site.get("ads", {}).get("enabled", False)

    if not ads_enabled or dry_run:
        log.info("Ads not enabled or dry_run=True — skipping Meta API call")
        return {
            "ok": True,
            "dry_run": True,
            "manifest_path": path,
            "note": "manifest_created_no_meta_call",
            "copy_ok": manifest.get("copy_validation_ok", False),
            "accent": manifest.get("accent"),
        }

    # If enabled: create PAUSED campaign
    try:
        from agent.ads.meta_adapter import create_paused_campaign
        meta_result = create_paused_campaign(manifest)
        log.info("Meta campaign created: %s", meta_result)
        return {
            "ok": True,
            "manifest_path": path,
            "meta_campaign_id": meta_result.get("campaign_id"),
            "status": "PAUSED",
            "note": "campaign_created_paused_publish_manually",
        }
    except Exception as e:
        log.error("Meta API error: %s", e)
        return {
            "ok": False,
            "manifest_path": path,
            "meta_error": str(e),
            "note": "manifest_saved_meta_failed",
        }


def ads_status_task(site_id: str = "superparty") -> dict:
    """
    Check latest ads manifests and report status.
    Returns list of drafts and whether any need review.
    """
    drafts_dir = Path(f"reports/ads_drafts/{site_id}")
    if not drafts_dir.exists():
        return {"ok": True, "drafts": [], "note": "no_drafts_yet"}

    drafts = []
    for f in sorted(drafts_dir.glob("ads_plan_*.json"), reverse=True)[:5]:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            drafts.append({
                "file": f.name,
                "accent": data.get("accent"),
                "campaign_name": data.get("campaign_name"),
                "copy_ok": data.get("copy_validation_ok"),
                "dry_run": data.get("dry_run"),
                "created_at": data.get("created_at"),
            })
        except Exception:
            pass

    return {"ok": True, "site_id": site_id, "drafts": drafts}
