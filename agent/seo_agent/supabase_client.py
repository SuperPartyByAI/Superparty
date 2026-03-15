"""
supabase_client.py — Thin CRUD wrapper for Supabase.

Reads SUPABASE_URL and SUPABASE_KEY from environment.
Falls back to in-memory dicts for testing when env vars are missing.
"""
from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from typing import Any, Optional

log = logging.getLogger("seo_agent.supabase")


class SupabaseClient:
    """Wrapper around Supabase REST API (via supabase-py)."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self._url = url or os.getenv("SUPABASE_URL", "")
        self._key = key or os.getenv("SUPABASE_KEY", "")
        self._client = None

        if self._url and self._key:
            try:
                from supabase import create_client
                self._client = create_client(self._url, self._key)
                log.info("Supabase client initialized (live)")
            except ImportError:
                log.warning("supabase-py not installed — running in stub mode")
            except Exception as e:
                log.error(f"Supabase init failed: {e}")
        else:
            log.info("Supabase credentials not set — running in stub mode")

    @property
    def is_live(self) -> bool:
        return self._client is not None

    # ── Sites ────────────────────────────────────────────────────────────────

    def get_site(self, domain: str) -> Optional[dict]:
        if not self._client:
            return None
        resp = self._client.table("sites").select("*").eq("domain", domain).execute()
        return resp.data[0] if resp.data else None

    def get_all_sites(self) -> list[dict]:
        if not self._client:
            return []
        resp = self._client.table("sites").select("*").execute()
        return resp.data or []

    def is_frozen(self, domain: str) -> bool:
        site = self.get_site(domain)
        if not site or not site.get("freeze_until"):
            return False
        freeze_until = datetime.fromisoformat(site["freeze_until"].replace("Z", "+00:00"))
        return datetime.now(timezone.utc) < freeze_until

    # ── Head Terms ───────────────────────────────────────────────────────────

    def get_head_term(self, canonical_term: str) -> Optional[dict]:
        if not self._client:
            return None
        resp = (self._client.table("head_terms")
                .select("*")
                .eq("canonical_term", canonical_term)
                .execute())
        return resp.data[0] if resp.data else None

    # ── Owner Pages ──────────────────────────────────────────────────────────

    def get_owner_page(self, site_id: str, head_term_id: str) -> Optional[dict]:
        if not self._client:
            return None
        resp = (self._client.table("owner_pages")
                .select("*")
                .eq("site_id", site_id)
                .eq("head_term_id", head_term_id)
                .execute())
        return resp.data[0] if resp.data else None

    def get_all_owners_for_term(self, head_term_id: str) -> list[dict]:
        """Returns ALL owner pages across ALL sites for a given head-term."""
        if not self._client:
            return []
        resp = (self._client.table("owner_pages")
                .select("*, sites(domain, brand)")
                .eq("head_term_id", head_term_id)
                .execute())
        return resp.data or []

    def upsert_owner_page(self, data: dict) -> dict:
        if not self._client:
            return {"error": "stub mode"}
        resp = (self._client.table("owner_pages")
                .upsert(data, on_conflict="site_id,head_term_id")
                .execute())
        return resp.data[0] if resp.data else {}

    # ── Internal Links ───────────────────────────────────────────────────────

    def get_internal_links(self, owner_page_id: str) -> list[dict]:
        if not self._client:
            return []
        resp = (self._client.table("internal_links")
                .select("*")
                .eq("target_owner_page_id", owner_page_id)
                .execute())
        return resp.data or []

    def count_internal_links(self, owner_page_id: str) -> int:
        return len(self.get_internal_links(owner_page_id))

    # ── PR Queue ─────────────────────────────────────────────────────────────

    def create_pr_entry(self, data: dict) -> dict:
        if not self._client:
            return {"error": "stub mode"}
        resp = self._client.table("pr_queue").insert(data).execute()
        return resp.data[0] if resp.data else {}

    def update_pr_status(self, pr_id: str, status: str) -> dict:
        if not self._client:
            return {"error": "stub mode"}
        resp = (self._client.table("pr_queue")
                .update({"status": status, "processed_at": datetime.now(timezone.utc).isoformat()})
                .eq("id", pr_id)
                .execute())
        return resp.data[0] if resp.data else {}

    # ── Audit Logs ───────────────────────────────────────────────────────────

    def log_audit(self, actor: str, action: str, payload: dict = None) -> None:
        if not self._client:
            log.info(f"AUDIT [stub]: {actor} / {action} / {payload}")
            return
        self._client.table("audit_logs").insert({
            "actor": actor,
            "action": action,
            "payload": payload or {}
        }).execute()

    # ── Index Requests ───────────────────────────────────────────────────────

    def create_index_request(self, site_id: str, path: str, status: str = "pending") -> dict:
        if not self._client:
            return {"stub": True}
        resp = self._client.table("index_requests").insert({
            "site_id": site_id,
            "path": path,
            "request_status": status
        }).execute()
        return resp.data[0] if resp.data else {}

    # ── Monitor Metrics ──────────────────────────────────────────────────────

    def upsert_metric(self, data: dict) -> dict:
        if not self._client:
            return {"stub": True}
        resp = (self._client.table("monitor_metrics")
                .upsert(data, on_conflict="site_id,owner_page_id,metric_date")
                .execute())
        return resp.data[0] if resp.data else {}

    def get_metrics(self, site_id: str, owner_page_id: str, days: int = 7) -> list[dict]:
        if not self._client:
            return []
        resp = (self._client.table("monitor_metrics")
                .select("*")
                .eq("site_id", site_id)
                .eq("owner_page_id", owner_page_id)
                .order("metric_date", desc=True)
                .limit(days)
                .execute())
        return resp.data or []
