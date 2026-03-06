import json, logging, os
from datetime import date, timedelta
from pathlib import Path
import requests
from agent.common.env import getenv, getenv_int
try:
    from agent.tasks.ga4_planner import load_latest_ga4_report, select_top_pages_from_ga4
    from agent.tasks.ga4_planner import resolve_pagepath_to_file, safe_apply_frontmatter, MAX_WEEKLY_WAVE
except ImportError:
    pass


log = logging.getLogger(__name__)


def _gsc_client():
    """Build GSC client using webmasters v3 (works with service account)."""
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
    """Collect GSC analytics (impressions, clicks, positions) for top queries."""
    service, err = _gsc_client()
    if err:
        return {"ok": False, "error": err}

    gsc_property = os.environ.get("GSC_PROPERTY", "https://superparty.ro/").strip()

    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=28)

    body = {
        "startDate": str(start),
        "endDate": str(end),
        "dimensions": ["query", "page"],
        "rowLimit": 500,
    }

    # Try sc-domain: (domain property) first, then url-prefix
    host = gsc_property.replace("https://", "").replace("http://", "").rstrip("/")
    candidates = [f"sc-domain:{host}", gsc_property]
    last_err = "unknown"
    for prop in candidates:
        try:
            response = service.searchanalytics().query(siteUrl=prop, body=body).execute()
            rows = response.get("rows", [])
            out_dir = Path(f"reports/{site_id}/gsc")
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"collect_{date.today()}.json"
            data = {
                "collected_at": str(date.today()),
                "property": prop,
                "date_range": f"{start} to {end}",
                "rows": rows,
                "total_rows": len(rows),
            }
            out_file.write_text(json.dumps(data, indent=2))
            return {
                "ok": True,
                "rows": len(rows),
                "property": prop,
                "file": str(out_file),
                "date_range": f"{start} to {end}",
            }
        except Exception as e:
            last_err = str(e)
            continue

    return {"ok": False, "error": f"gsc_collect_failed: {last_err}"}


def seo_index_task(site_id="superparty"):
    """Index collected GSC data. Returns ok+no_data_yet if GSC not populated."""
    import json
    from pathlib import Path
    from datetime import date

    gsc_dir = Path(f"reports/{site_id}/gsc")
    if not gsc_dir.exists():
        return {"ok": True, "note": "no_data_yet", "reason": "no_gsc_directory", "next_check": "daily"}

    files = sorted(gsc_dir.glob("collect_*.json"))
    if not files:
        return {"ok": True, "note": "no_data_yet", "reason": "no_collect_files", "next_check": "daily"}

    all_rows = []
    for f in files[-7:]:
        try:
            d = json.loads(f.read_text())
            all_rows.extend(d.get("rows", []))
        except Exception:
            pass

    if not all_rows:
        # Write a status file so operators can see what happened
        status_dir = Path(f"reports/{site_id}")
        status_dir.mkdir(parents=True, exist_ok=True)
        status_file = status_dir / "gsc_status.json"
        status_file.write_text(json.dumps({
            "gsc_status": "no_data_yet",
            "reason": "Google Search Console returned 0 impressions - site may be new or recently migrated",
            "property": "sc-domain:superparty.ro",
            "files_checked": len(files),
            "last_checked": str(date.today()),
            "next_check": "daily",
            "action": "Data will appear automatically when Google crawls and indexes the site"
        }, indent=2))
        return {
            "ok": True,
            "note": "no_data_yet",
            "reason": "0 rows from GSC - site new or recently migrated",
            "gsc_files": len(files),
            "next_check": "daily"
        }

    query_agg = {}
    for row in all_rows:
        keys = row.get("keys", [])
        if not keys:
            continue
        query = keys[0] if len(keys) > 0 else "unknown"
        page = keys[1] if len(keys) > 1 else ""
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        position = row.get("position", 0)
        if query not in query_agg:
            query_agg[query] = {"query": query, "page": page, "clicks": 0, "impressions": 0, "position_sum": 0, "count": 0}
        query_agg[query]["clicks"] += clicks
        query_agg[query]["impressions"] += impressions
        query_agg[query]["position_sum"] += position
        query_agg[query]["count"] += 1

    index = []
    for q, agg in query_agg.items():
        avg_pos = agg["position_sum"] / agg["count"] if agg["count"] > 0 else 99
        index.append({"query": q, "page": agg["page"], "clicks": agg["clicks"], "impressions": agg["impressions"], "avg_position": round(avg_pos, 1)})
    index.sort(key=lambda x: x["impressions"], reverse=True)

    out_dir = Path(f"reports/{site_id}/gsc")
    index_file = out_dir / "index.json"
    index_file.write_text(json.dumps(index, indent=2))
    return {"ok": True, "indexed_queries": len(index), "file": str(index_file)}


def seo_plan_task(mode="default"):
    if mode.startswith("ga4"):
        try:
            from agent.tasks.seo_ga4_patch import seo_plan_ga4_wave
            return seo_plan_ga4_wave(site_id="superparty", mode=mode)
        except Exception as e:
            return {"ok": True, "note": f"ga4_error:{e}"}
    return _orig_seo_plan_task()

def _orig_seo_plan_task(site_id="superparty", wave="daily_small"):
    """Generate SEO plan. Returns ok+no_data_yet if no index available."""
    import json
    import re
    import unicodedata
    from pathlib import Path
    from datetime import date
    from agent.common.env import getenv_int

    index_file = Path(f"reports/{site_id}/gsc/index.json")
    if not index_file.exists():
        return {"ok": True, "note": "no_data_yet", "reason": "no_index_file", "next_check": "daily"}

    index = json.loads(index_file.read_text())
    if not index:
        return {"ok": True, "note": "no_data_yet", "reason": "index_empty", "next_check": "daily"}

    # Incarcare Whitelist pentru Local Intent Score (Ilfov)
    manifest_path = Path("reports/seo/indexing_manifest.json")
    whitelist_slugs = set()
    if manifest_path.exists():
        try:
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            for m in manifest_data:
                # Doar comune si orase din Ilfov care sunt indexable
                if m.get("county") == "Ilfov" and m.get("indexable") and m.get("place_type") in ("town", "commune"):
                    whitelist_slugs.add(m.get("slug", "").lower())
        except Exception:
            pass

    def normalize_text(text):
        if not text: return ""
        text = str(text).lower().strip()
        for r, e in {'ă':'a','â':'a','î':'i','ș':'s','ş':'s','ț':'t','ţ':'t'}.items():
            text = text.replace(r, e)
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        return re.sub(r'[^a-z0-9]+', ' ', text).strip()

    def compute_local_intent(query, whitelist):
        q_norm = normalize_text(query)
        score = 0
        matched = []

        if "bucuresti" in q_norm:
            score += 8
            matched.append("bucuresti")
        if "ilfov" in q_norm:
            score += 8
            matched.append("ilfov")
        
        # Sectoare
        sec_match = re.search(r'sector\s*(ul)?\s*([1-6])', q_norm)
        if sec_match:
            score += 10
            matched.append(f"sector {sec_match.group(2)}")
        elif "sector" in q_norm:
            score += 6
            matched.append("sector")

        # Cuvinte cheie comerciale
        if "animatori" in q_norm or "animator" in q_norm:
            score += 6 if "animatori" in q_norm else 5
            matched.append("animator/i")
        if "petreceri copii" in q_norm:
            score += 6
            matched.append("petreceri copii")
        elif "petreceri pentru copii" in q_norm:
            score += 5
            matched.append("petreceri pentru copii")

        # Whitelist Ilfov
        for w_slug in whitelist:
            w_norm = w_slug.replace('-', ' ')
            if w_norm and w_norm in q_norm:
                score += 9
                matched.append(f"localitate {w_norm}")

        return score, matched

    min_impressions = getenv_int("SEO_IMPRESSIONS_MIN", 50)
    pos_min = getenv_int("SEO_POS_MIN", 5)
    pos_max = getenv_int("SEO_POS_MAX", 25)
    wave_size = getenv_int("MAX_WEEKLY_WAVE", 10) if wave == "daily_small" else getenv_int("MAX_WEEKLY_WAVE", 30)

    # 1. Filtrare bazata pe praguri si adaugare Score/Matched
    filtered_opps = []
    for row in index:
        imp = row.get("impressions", 0)
        pos = row.get("avg_position", 99)
        if imp >= min_impressions and pos_min <= pos <= pos_max:
            intent_score, matched_terms = compute_local_intent(row.get("query", ""), whitelist_slugs)
            row["local_intent_score"] = intent_score
            row["matched_terms"] = matched_terms
            filtered_opps.append(row)

    # 2. Sortare Multi-Criteriu
    filtered_opps.sort(key=lambda x: (x.get("local_intent_score", 0), x.get("impressions", 0), -x.get("avg_position", 99)), reverse=True)
    
    # 3. Wave cutoff
    opportunities = filtered_opps[:wave_size]

    if not opportunities:
        index_with_score = []
        for row in index[:min(5, wave_size)]:
            score, matched = compute_local_intent(row.get("query", ""), whitelist_slugs)
            row["local_intent_score"] = score
            row["matched_terms"] = matched
            index_with_score.append(row)
        opportunities = index_with_score

    plan = {"wave": wave, "created": str(date.today()), "opportunities": opportunities, "count": len(opportunities)}
    plan_dir = Path(f"reports/{site_id}/seo_plans")
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plan_dir / f"plan_{date.today()}_{wave}.json"
    plan_file.write_text(json.dumps(plan, indent=2, ensure_ascii=False))
    return {"ok": True, "opportunities": len(opportunities), "file": str(plan_file)}


def seo_apply_task():
    import pathlib
    ga4_plans = sorted(pathlib.Path("reports/superparty").glob("seo_plan_ga4_*.json"), reverse=True)
    if ga4_plans:
        try:
            from agent.tasks.seo_ga4_patch import seo_apply_ga4_plan
            return seo_apply_ga4_plan(site_id="superparty")
        except Exception as e:
            pass
    return _orig_seo_apply_task()

def _orig_seo_apply_task(site_id="superparty"):
    """Apply SEO plan as PR. Returns ok+no_plan gracefully if no plan exists."""
    import json
    from pathlib import Path
    from datetime import date
    from agent.common.git_pr import create_pr

    plan_dir = Path(f"reports/{site_id}/seo_plans")
    if not plan_dir.exists():
        return {"ok": True, "note": "no_plan", "reason": "plan_dir_missing"}

    plans = sorted(plan_dir.glob("plan_*.json"))
    if not plans:
        return {"ok": True, "note": "no_plan", "reason": "no_plan_files"}

    latest = json.loads(plans[-1].read_text())
    opportunities = latest.get("opportunities", [])
    if not opportunities:
        return {"ok": True, "note": "no_opportunities", "reason": "plan_is_empty"}

    report_dir = Path(f"reports/{site_id}")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"seo_report_{date.today()}.md"
    lines = [
        f"# SEO Opportunity Report — {date.today()}",
        "",
        f"Wave: {latest.get('wave')} | Opportunities: {len(opportunities)}",
        "",
        "| Query | Page | Impressions | Avg Position |",
        "|-------|------|-------------|--------------|",
    ]
    for opp in opportunities[:20]:
        page = opp.get("page", "").replace("|", "/")
        lines.append(f"| {opp.get('query','')} | {page} | {opp.get('impressions')} | {opp.get('avg_position')} |")

    report_file.write_text("\n".join(lines))
    result = create_pr(
        site_id=site_id,
        title=f"SEO: {len(opportunities)} opportunities ({latest.get('wave')}) {date.today()}",
        body=f"Automated SEO opportunity report.\n\nTop: {opportunities[0].get('query') if opportunities else 'none'}",
        files={str(report_file): "\n".join(lines)},
    )
    return result
