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


def seo_collect_task(site="superparty"):
    _data_dir(site).mkdir(parents=True, exist_ok=True)
    sa = getenv("GSC_SERVICE_ACCOUNT_JSON")
    prop = getenv("GSC_PROPERTY")
    if not sa or sa.strip() in ("{}", "") or not prop:
        return {"ok": False, "error": "gsc_not_configured"}
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        creds = service_account.Credentials.from_service_account_info(json.loads(sa))
        svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
        end = date.today()
        start = end - timedelta(days=28)
        resp = svc.searchanalytics().query(siteUrl=prop, body={
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["query", "page"],
            "rowLimit": 25000,
        }).execute()
        out = _data_dir(site) / ("gsc_" + start.isoformat() + "_" + end.isoformat() + ".json")
        out.write_text(json.dumps(resp, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "rows": len(resp.get("rows", []))}
    except Exception as e:
        log.exception("GSC error: %s", e)
        return {"ok": False, "error": str(e)}


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
