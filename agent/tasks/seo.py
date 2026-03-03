import json, logging
from datetime import date, timedelta
from pathlib import Path
import requests
from agent.common.env import getenv, getenv_int
from agent.common.guardrails import max_weekly_wave

log = logging.getLogger("seo")


def _data_dir(s):
    return Path("data/" + s + "/seo")


def _idx_dir(s):
    return Path("data/" + s + "/seo_index")


def _rep_dir(s):
    return Path("reports/" + s)


def _gsc_client():
    """Build GSC client using webmasters v3 (more compatible with service accounts)."""
    import json, os
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    gsc_json = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    if not gsc_json or gsc_json in ("{}", ""):
        return None, "gsc_not_configured"
    
    try:
        sa_info = json.loads(gsc_json)
    except Exception as e:
        return None, f"gsc_json_parse_error: {e}"
    
    try:
        creds = service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        service = build("webmasters", "v3", credentials=creds)
        return service, None
    except Exception as e:
        return None, f"gsc_build_error: {e}"


def seo_collect_task(site_id="superparty"):
    """Collect GSC data (impressions, clicks, positions) for top queries."""
    import os, json, datetime, pathlib
    
    service, err = _gsc_client()
    if err:
        return {"ok": False, "error": err}
    
    gsc_property = os.environ.get("GSC_PROPERTY", "https://superparty.ro/").strip()
    # Normalize: Search Console supports sc-domain: or https:// prefix
    if not gsc_property.startswith("sc-domain:") and not gsc_property.startswith("http"):
        gsc_property = f"https://{gsc_property}/"
    
    try:
        # Date range: last 28 days
        end = datetime.date.today() - datetime.timedelta(days=3)  # GSC lag ~3 days
        start = end - datetime.timedelta(days=28)
        
        body = {
            "startDate": str(start),
            "endDate": str(end),
            "dimensions": ["query", "page"],
            "rowLimit": 500,
            "startRow": 0
        }
        
        # Try sc-domain: first, fallback to url prefix
        for prop in [f"sc-domain:{gsc_property.replace('https://','').replace('http://','').rstrip('/')}", gsc_property]:
            try:
                response = service.searchAnalytics().query(siteUrl=prop, body=body).execute()
                rows = response.get("rows", [])
                
                if rows:
                    # Save results
                    out_dir = pathlib.Path(f"reports/{site_id}/gsc")
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_file = out_dir / f"collect_{datetime.date.today()}.json"
                    
                    data = {
                        "collected_at": str(datetime.datetime.utcnow()),
                        "property": prop,
                        "date_range": f"{start} to {end}",
                        "rows": rows,
                        "total_rows": len(rows)
                    }
                    out_file.write_text(json.dumps(data, indent=2))
                    
                    return {
                        "ok": True,
                        "rows": len(rows),
                        "property": prop,
                        "file": str(out_file),
                        "date_range": f"{start} to {end}"
                    }
            except Exception as e:
                last_err = str(e)
                continue
        
        return {"ok": False, "error": f"No data from GSC: {last_err}"}
        
    except Exception as e:
        return {"ok": False, "error": f"gsc_collect_error: {e}"}


def seo_index_task(site="superparty"):
    _idx_dir(site).mkdir(parents=True, exist_ok=True)
    files = sorted(_data_dir(site).glob("gsc_*.json"))
    if not files:
        return {"ok": False, "error": "no_gsc_files"}
    raw = json.loads(files[-1].read_text(encoding="utf-8"))
    norm = []
    for r in raw.get("rows", []):
        keys = r.get("keys", [])
        if len(keys) < 2:
            continue
        norm.append({
            "query": keys[0],
            "page": keys[1],
            "clicks": r.get("clicks", 0),
            "impressions": r.get("impressions", 0),
            "ctr": r.get("ctr", 0),
            "position": r.get("position", 999),
        })
    out = _idx_dir(site) / "latest.json"
    out.write_text(json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "indexed": len(norm)}


def seo_plan_task(site="superparty", mode="weekly_wave"):
    idx = _idx_dir(site) / "latest.json"
    if not idx.exists():
        return {"ok": False, "error": "no_index"}
    rows = json.loads(idx.read_text(encoding="utf-8"))
    imp_min = getenv_int("SEO_IMPRESSIONS_MIN", 100)
    pos_min = getenv_int("SEO_POS_MIN", 5)
    pos_max = getenv_int("SEO_POS_MAX", 25)
    candidates = [r for r in rows if r["impressions"] >= imp_min and pos_min <= r["position"] <= pos_max]
    candidates.sort(key=lambda x: x["impressions"], reverse=True)
    wave = max_weekly_wave() if mode == "weekly_wave" else min(10, max_weekly_wave())
    plan = []
    llm_url = getenv("LLM_WORKER_URL", "http://localhost:8100") + "/generate"
    for item in candidates[:wave]:
        q = item["query"]
        p = item["page"]
        prompt = "Write SEO title max 60 chars and meta description max 155 chars for: " + q + " on page " + p + ". Reply JSON only with keys title and description."
        try:
            r = requests.post(llm_url, json={"prompt": prompt}, timeout=60)
            llm = r.json()
        except Exception as e:
            llm = {"error": str(e)}
        plan.append(dict(item, llm=llm))
    _rep_dir(site).mkdir(parents=True, exist_ok=True)
    out = _rep_dir(site) / ("seo_plan_" + mode + "_" + date.today().isoformat() + ".json")
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "count": len(plan), "plan_file": str(out)}


def seo_apply_task(site="superparty"):
    plans = sorted(_rep_dir(site).glob("seo_plan_*_*.json"))
    if not plans:
        return {"ok": False, "error": "no_plan"}
    token = getenv("GITHUB_TOKEN", "")
    if not token or "CHANGEME" in token or len(token) < 20:
        return {"ok": False, "error": "github_token_missing", "plan": str(plans[-1])}
    return {"ok": True, "note": "apply ready - call git_commit_push_pr to create PR", "plan": str(plans[-1])}
