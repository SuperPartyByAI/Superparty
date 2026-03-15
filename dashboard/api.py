"""
dashboard/api.py — FastAPI dashboard for SEO Agent operations.

Endpoints:
  GET  /api/sites         — list sites + freeze status
  GET  /api/prs           — PR queue
  GET  /api/metrics       — monitor metrics
  GET  /api/alerts        — recent alerts from audit_logs
  GET  /api/embeddings    — embedding stats
  POST /api/action/approve-pr   — approve PR (HITL)
  POST /api/action/reject-pr    — reject PR
  POST /api/action/revert-pr    — trigger rollback
  POST /api/action/freeze       — set/clear freeze on a site

Run:
  cd dashboard && uvicorn api:app --reload --port 8000
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
except ImportError:
    raise ImportError("Install FastAPI: pip install fastapi uvicorn")

log = logging.getLogger("seo_dashboard")

app = FastAPI(
    title="SEO Agent Dashboard",
    description="Operational dashboard for autonomous SEO agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Supabase helpers ──────────────────────────────────────────────────────────

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def _sb_request(path: str, method: str = "GET", body: Optional[dict] = None) -> list | dict:
    """Make a request to Supabase REST API."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(503, "SUPABASE_URL/KEY not configured")

    url = f"{SUPABASE_URL}/rest/v1/{path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    if method == "GET":
        headers["Accept"] = "application/json"

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode() if e.fp else str(e)
        raise HTTPException(e.code, detail[:500])


def _sb_insert(table: str, row: dict) -> dict:
    """Insert a row into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    data = json.dumps(row).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode()
            result = json.loads(raw) if raw else []
            return result[0] if isinstance(result, list) and result else result
    except urllib.error.HTTPError as e:
        detail = e.read().decode() if e.fp else str(e)
        raise HTTPException(e.code, detail[:500])


def _sb_update(table: str, filters: str, updates: dict) -> dict:
    """Update rows in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    data = json.dumps(updates).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode() if e.fp else str(e)
        raise HTTPException(e.code, detail[:500])


# ── Pydantic models ──────────────────────────────────────────────────────────

class PRAction(BaseModel):
    pr_id: str
    actor: str = "dashboard-user"
    reason: str = ""


class FreezeAction(BaseModel):
    domain: str
    freeze_until: Optional[str] = None  # ISO timestamp or null to clear
    actor: str = "dashboard-user"


# ── API Routes ────────────────────────────────────────────────────────────────

@app.get("/api/sites")
def list_sites():
    """List all sites with freeze status."""
    sites = _sb_request("sites?select=*&order=domain")
    now = datetime.now(timezone.utc)
    for s in sites:
        freeze = s.get("freeze_until")
        if freeze:
            try:
                ft = datetime.fromisoformat(freeze.replace("Z", "+00:00"))
                s["is_frozen"] = ft > now
                s["freeze_remaining_hours"] = max(0, round((ft - now).total_seconds() / 3600, 1))
            except Exception:
                s["is_frozen"] = False
        else:
            s["is_frozen"] = False
    return {"sites": sites, "total": len(sites)}


@app.get("/api/prs")
def list_prs(
    status: Optional[str] = Query(None, description="Filter by status: pending/approved/merged/reverted"),
    site_id: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
):
    """List PR queue entries."""
    path = f"pr_queue?select=*&order=created_at.desc&limit={limit}"
    if status:
        path += f"&status=eq.{status}"
    if site_id:
        path += f"&site_id=eq.{site_id}"
    prs = _sb_request(path)
    return {"prs": prs, "total": len(prs)}


@app.get("/api/metrics")
def get_metrics(
    site: Optional[str] = Query(None, description="Domain filter"),
    since: Optional[str] = Query(None, description="ISO date"),
    limit: int = Query(100, le=500),
):
    """Get monitor metrics."""
    path = f"monitor_metrics?select=*&order=recorded_at.desc&limit={limit}"
    if since:
        path += f"&recorded_at=gte.{since}"
    metrics = _sb_request(path)
    if site:
        metrics = [m for m in metrics if site in str(m.get("payload", {}))]
    return {"metrics": metrics, "total": len(metrics)}


@app.get("/api/alerts")
def recent_alerts(limit: int = Query(20, le=100)):
    """Recent audit log entries (alerts, rollbacks, deploys)."""
    path = f"audit_logs?select=*&order=created_at.desc&limit={limit}"
    logs = _sb_request(path)
    return {"alerts": logs, "total": len(logs)}


@app.get("/api/head-terms")
def list_head_terms():
    """List head terms and their owners."""
    terms = _sb_request("head_terms?select=*&order=term")
    return {"terms": terms, "total": len(terms)}


@app.get("/api/owner-pages")
def list_owner_pages():
    """List owner pages."""
    pages = _sb_request("owner_pages?select=*&order=created_at.desc")
    return {"pages": pages, "total": len(pages)}


@app.get("/api/embeddings/stats")
def embedding_stats():
    """Get embedding statistics."""
    try:
        embeddings = _sb_request("page_embeddings_json?select=id,model,dim,created_at")
        models = {}
        for e in embeddings:
            m = e.get("model", "unknown")
            models[m] = models.get(m, 0) + 1
        return {"total": len(embeddings), "by_model": models}
    except Exception as e:
        return {"total": 0, "by_model": {}, "error": str(e)}


# ── HITL Actions ──────────────────────────────────────────────────────────────

@app.post("/api/action/approve-pr")
def approve_pr(action: PRAction):
    """Approve a PR in the queue."""
    _sb_update("pr_queue", f"id=eq.{action.pr_id}", {"status": "approved"})
    _sb_insert("audit_logs", {
        "actor": action.actor,
        "action": "approve_pr",
        "payload": {"pr_id": action.pr_id, "reason": action.reason},
    })
    return {"ok": True, "pr_id": action.pr_id, "new_status": "approved"}


@app.post("/api/action/reject-pr")
def reject_pr(action: PRAction):
    """Reject a PR in the queue."""
    _sb_update("pr_queue", f"id=eq.{action.pr_id}", {"status": "rejected"})
    _sb_insert("audit_logs", {
        "actor": action.actor,
        "action": "reject_pr",
        "payload": {"pr_id": action.pr_id, "reason": action.reason},
    })
    return {"ok": True, "pr_id": action.pr_id, "new_status": "rejected"}


@app.post("/api/action/revert-pr")
def revert_pr(action: PRAction):
    """Mark a PR for rollback."""
    _sb_update("pr_queue", f"id=eq.{action.pr_id}", {"status": "reverted"})
    _sb_insert("audit_logs", {
        "actor": action.actor,
        "action": "revert_pr",
        "payload": {"pr_id": action.pr_id, "reason": action.reason},
    })
    return {"ok": True, "pr_id": action.pr_id, "new_status": "reverted", "note": "Run rollback.py for full revert"}


@app.post("/api/action/freeze")
def set_freeze(action: FreezeAction):
    """Set or clear freeze on a site."""
    updates = {"freeze_until": action.freeze_until}
    _sb_update("sites", f"domain=eq.{action.domain}", updates)
    _sb_insert("audit_logs", {
        "actor": action.actor,
        "action": "set_freeze" if action.freeze_until else "clear_freeze",
        "payload": {"domain": action.domain, "freeze_until": action.freeze_until},
    })
    verb = "set" if action.freeze_until else "cleared"
    return {"ok": True, "domain": action.domain, "freeze": verb}


# ── Health / Root ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    """Health check."""
    try:
        sites = _sb_request("sites?select=domain&limit=1")
        return {"status": "ok", "db": "connected", "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        return {"status": "degraded", "db": str(e)}


@app.get("/", response_class=HTMLResponse)
def root():
    """Redirect to frontend or show status."""
    return """
    <html>
    <head><title>SEO Agent Dashboard</title></head>
    <body style="font-family:system-ui;max-width:600px;margin:40px auto;color:#e0e0e0;background:#1a1a2e;">
      <h1 style="color:#00d4ff;">🔭 SEO Agent Dashboard API</h1>
      <p>API is running. Connect the React frontend on <code>:5173</code></p>
      <ul>
        <li><a href="/api/health" style="color:#00d4ff;">/api/health</a></li>
        <li><a href="/api/sites" style="color:#00d4ff;">/api/sites</a></li>
        <li><a href="/api/prs" style="color:#00d4ff;">/api/prs</a></li>
        <li><a href="/api/metrics" style="color:#00d4ff;">/api/metrics</a></li>
        <li><a href="/api/alerts" style="color:#00d4ff;">/api/alerts</a></li>
        <li><a href="/docs" style="color:#00d4ff;">/docs</a> (Swagger UI)</li>
      </ul>
    </body>
    </html>
    """
