"""
index_notify.py — GSC Indexing API + Sitemap Submit.

Handles:
  - URL Notification via Indexing API (if eligible)
  - Sitemap submission via Search Console API
  - Fallback: logs requests to Supabase for manual action
"""
from __future__ import annotations

import logging
from typing import Optional

log = logging.getLogger("seo_agent.index_notify")


def notify_indexing(url: str, credentials_path: Optional[str] = None) -> dict:
    """
    Submit URL notification via Google Indexing API.
    
    Returns: {ok: bool, response: dict|str, method: str}
    
    Note: Indexing API has restrictions (mostly for JobPosting/BroadcastEvent).
    If not eligible, returns fallback result for manual action.
    """
    try:
        import os
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path:
            return {
                "ok": False,
                "response": "No credentials configured",
                "method": "none",
            }

        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/indexing"],
        )
        service = build("indexing", "v3", credentials=credentials, cache_discovery=False)

        result = service.urlNotifications().publish(
            body={"url": url, "type": "URL_UPDATED"}
        ).execute()

        log.info(f"Indexing API success for {url}")
        return {"ok": True, "response": result, "method": "indexing_api"}

    except ImportError:
        return {
            "ok": False,
            "response": "google-api-python-client not installed",
            "method": "none",
        }
    except Exception as e:
        error_str = str(e)
        # Common: 403 = not eligible for Indexing API
        if "403" in error_str or "Permission" in error_str:
            log.warning(f"Indexing API not eligible for {url}: {error_str}")
            return {
                "ok": False,
                "response": f"Not eligible (403): {error_str}",
                "method": "manual_required",
            }
        log.error(f"Indexing API error for {url}: {error_str}")
        return {"ok": False, "response": error_str, "method": "error"}


def submit_sitemap(
    site_url: str,
    sitemap_url: str,
    credentials_path: Optional[str] = None,
) -> dict:
    """
    Submit sitemap via Google Search Console API.
    
    site_url: e.g. 'sc-domain:superparty.ro'
    sitemap_url: e.g. 'https://www.superparty.ro/sitemap.xml'
    """
    try:
        import os
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path:
            return {"ok": False, "response": "No credentials configured"}

        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/webmasters"],
        )
        service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)

        service.sitemaps().submit(
            siteUrl=site_url,
            feedpath=sitemap_url,
        ).execute()

        log.info(f"Sitemap submitted: {sitemap_url} for {site_url}")
        return {"ok": True, "response": "Sitemap submitted"}

    except ImportError:
        return {"ok": False, "response": "google-api-python-client not installed"}
    except Exception as e:
        log.error(f"Sitemap submit error: {e}")
        return {"ok": False, "response": str(e)}


def fetch_url_inspection(
    url: str,
    site_url: str,
    credentials_path: Optional[str] = None,
) -> dict:
    """
    Fetch URL Inspection data via Search Console API.
    Returns index status, last crawl time, and coverage details.
    """
    try:
        import os
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path:
            return {"ok": False, "response": "No credentials configured"}

        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)

        result = service.urlInspection().index().inspect(
            body={
                "inspectionUrl": url,
                "siteUrl": site_url,
            }
        ).execute()

        return {"ok": True, "response": result}

    except ImportError:
        return {"ok": False, "response": "google-api-python-client not installed"}
    except Exception as e:
        return {"ok": False, "response": str(e)}
