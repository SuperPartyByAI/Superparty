"""ga4_stub.py — GA4 Measurement Protocol stub. Ready when credentials added."""
import json
import os
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path


def ga4_send_event(event_name: str, params: dict = None, client_id: str = "agent-001") -> dict:
    """Send a single event to GA4 via Measurement Protocol."""
    measurement_id = os.environ.get("GA4_MEASUREMENT_ID", "").strip()
    api_secret = os.environ.get("GA4_API_SECRET", "").strip()

    if not measurement_id or not api_secret:
        return {"ok": False, "error": "ga4_not_configured",
                "note": "Set GA4_MEASUREMENT_ID and GA4_API_SECRET in .env.agent"}

    payload = {
        "client_id": client_id,
        "events": [{
            "name": event_name,
            "params": params or {}
        }]
    }
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={measurement_id}&api_secret={api_secret}"
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return {"ok": True, "status": resp.status, "event": event_name}
    except Exception as ex:
        return {"ok": False, "error": str(ex)[:100]}


def ga4_track_agent_run(site_id: str, task_name: str, result: dict) -> dict:
    """Track an agent task run as a GA4 event (for monitoring)."""
    return ga4_send_event(
        event_name="agent_task_complete",
        params={
            "site_id": site_id,
            "task_name": task_name,
            "ok": str(result.get("ok", False)),
            "note": result.get("note", result.get("error", ""))[:80],
            "date": str(date.today()),
        }
    )


def ga4_status_task(site_id="superparty") -> dict:
    """Check GA4 configuration and write status report."""
    measurement_id = os.environ.get("GA4_MEASUREMENT_ID", "").strip()
    api_secret = os.environ.get("GA4_API_SECRET", "").strip()

    configured = bool(measurement_id and api_secret)

    status = {
        "ok": True,
        "ga4_configured": configured,
        "note": "ready" if configured else "ga4_not_configured",
        "instructions": None if configured else (
            "1. Go to GA4 → Admin → Data Streams → Web → Measurement Protocol API secrets\n"
            "2. Create secret, copy value\n"
            "3. Add to .env.agent: GA4_MEASUREMENT_ID=G-XXXXXXXX, GA4_API_SECRET=xxxx\n"
            "4. docker compose restart"
        ),
        "events_to_implement": [
            "click_to_call",
            "click_to_whatsapp",
            "form_submit",
            "lead_created",
            "page_view"
        ]
    }

    report_dir = Path(f"reports/{site_id}/ga4")
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / f"ga4_status_{date.today()}.json"
    out.write_text(json.dumps(status, indent=2))

    return status
