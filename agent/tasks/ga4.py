"""ga4.py — GA4 Data API collector task."""
import os, json
from datetime import date, timedelta
from pathlib import Path


def ga4_collect_task(site_id="superparty", lookback_days=7):
    """Collect GA4 analytics data for top pages and events."""
    from agent.tasks.ga4_client import run_report, parse_report
    
    prop_id = os.environ.get("GA4_PROPERTY_ID", "").strip()
    if not prop_id:
        return {"ok": False, "error": "missing_GA4_PROPERTY_ID"}
    
    gsc_json = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    if not gsc_json:
        return {"ok": False, "error": "missing_GSC_SERVICE_ACCOUNT_JSON"}
    
    end = date.today()
    start = end - timedelta(days=lookback_days)
    
    out_dir = Path(f"reports/{site_id}/ga4")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # 1. Top pages by sessions
    try:
        resp_pages = run_report(
            prop_id, str(start), str(end),
            dimensions=["pagePath"],
            metrics=["sessions", "screenPageViews", "bounceRate", "averageSessionDuration"],
            limit=200
        )
        pages = parse_report(resp_pages)
        results["top_pages"] = sorted(pages, key=lambda x: x.get("sessions", 0), reverse=True)[:50]
    except Exception as e:
        results["top_pages_error"] = str(e)[:200]
    
    # 2. Events (click_to_call, whatsapp, cta_click, form_submit)
    try:
        resp_events = run_report(
            prop_id, str(start), str(end),
            dimensions=["eventName", "pagePath"],
            metrics=["eventCount"],
            limit=500
        )
        events = parse_report(resp_events)
        results["events"] = events
        
        # Count key conversion events
        conversions = {}
        for ev in events:
            name = ev.get("eventName", "")
            if name in ("click_to_call", "click_to_whatsapp", "cta_click", "form_submit", "lead_created"):
                conversions[name] = conversions.get(name, 0) + int(ev.get("eventCount", 0))
        results["conversions"] = conversions
    except Exception as e:
        results["events_error"] = str(e)[:200]
    
    # 3. Traffic sources
    try:
        resp_src = run_report(
            prop_id, str(start), str(end),
            dimensions=["sessionDefaultChannelGroup"],
            metrics=["sessions", "newUsers"],
            limit=20
        )
        results["traffic_sources"] = parse_report(resp_src)
    except Exception as e:
        results["traffic_sources_error"] = str(e)[:200]
    
    # Save report
    report = {
        "date": str(date.today()),
        "property_id": prop_id,
        "period": f"{start} to {end}",
        **results
    }
    out_file = out_dir / f"collect_{start}_{end}.json"
    out_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    top_pages_count = len(results.get("top_pages", []))
    events_count = len(results.get("events", []))
    has_errors = any(k for k in results if k.endswith("_error"))
    
    return {
        "ok": not has_errors,
        "property_id": prop_id,
        "period": f"{start} to {end}",
        "top_pages": top_pages_count,
        "events": events_count,
        "conversions": results.get("conversions", {}),
        "file": str(out_file),
        "errors": [v for k, v in results.items() if k.endswith("_error")],
    }


def ga4_status_task(site_id="superparty"):
    """Check GA4 Data API connection status."""
    prop_id = os.environ.get("GA4_PROPERTY_ID", "").strip()
    gsc_json = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    
    ga4_mid = os.environ.get("GA4_MEASUREMENT_ID", "").strip()
    ga4_secret = os.environ.get("GA4_API_SECRET", "").strip()
    
    configured = bool(prop_id and gsc_json)
    
    details = {
        "GA4_PROPERTY_ID": "set" if prop_id else "missing",
        "GSC_SERVICE_ACCOUNT_JSON": f"set (len={len(gsc_json)})" if gsc_json else "missing",
        "GA4_MEASUREMENT_ID": ga4_mid if ga4_mid else "missing",
        "GA4_API_SECRET": "set" if ga4_secret else "missing",
    }
    
    from pathlib import Path
    out_dir = Path(f"reports/{site_id}/ga4")
    out_dir.mkdir(parents=True, exist_ok=True)
    import json
    from datetime import date
    out_file = out_dir / f"ga4_status_{date.today()}.json"
    out_file.write_text(json.dumps({"ok": configured, "details": details}, indent=2))
    
    return {
        "ok": configured,
        "ga4_configured": configured,
        "details": details,
        "note": "ready" if configured else "configure GA4_PROPERTY_ID in .env.agent",
    }
