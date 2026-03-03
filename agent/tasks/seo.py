import json, logging, os
from datetime import date, timedelta
from pathlib import Path
import requests
from agent.common.env import getenv, getenv_int

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
    """Index collected GSC data for planning."""
    gsc_dir = Path(f"reports/{site_id}/gsc")
    if not gsc_dir.exists():
        return {"ok": False, "error": "no_gsc_files"}

    files = sorted(gsc_dir.glob("collect_*.json"))
    if not files:
        return {"ok": False, "error": "no_gsc_files"}

    # Aggregate all rows from all files
    all_rows = []
    for f in files[-7:]:  # last 7 days
        try:
            d = json.loads(f.read_text())
            all_rows.extend(d.get("rows", []))
        except Exception:
            pass

    if not all_rows:
        return {"ok": False, "error": "no_rows_in_gsc_files"}

    # Aggregate by query
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
        ctr = row.get("ctr", 0)

        if query not in query_agg:
            query_agg[query] = {"query": query, "page": page,
                                "clicks": 0, "impressions": 0,
                                "position_sum": 0, "count": 0, "ctr": 0}
        query_agg[query]["clicks"] += clicks
        query_agg[query]["impressions"] += impressions
        query_agg[query]["position_sum"] += position
        query_agg[query]["count"] += 1

    # Compute avg position and sort by impressions
    index = []
    for q, agg in query_agg.items():
        avg_pos = agg["position_sum"] / agg["count"] if agg["count"] > 0 else 99
        index.append({
            "query": q,
            "page": agg["page"],
            "clicks": agg["clicks"],
            "impressions": agg["impressions"],
            "avg_position": round(avg_pos, 1),
        })
    index.sort(key=lambda x: x["impressions"], reverse=True)

    out_dir = Path(f"reports/{site_id}/gsc")
    index_file = out_dir / "index.json"
    index_file.write_text(json.dumps(index, indent=2))

    return {"ok": True, "indexed_queries": len(index), "file": str(index_file)}


def seo_plan_task(site_id="superparty", wave="daily_small"):
    """Generate SEO improvement plan from indexed data."""
    index_file = Path(f"reports/{site_id}/gsc/index.json")
    if not index_file.exists():
        return {"ok": False, "error": "no_index"}

    index = json.loads(index_file.read_text())

    # Filter: impressions > 50, position between 5 and 25 (opportunity zone)
    min_impressions = getenv_int("SEO_IMPRESSIONS_MIN", 50)
    pos_min = getenv_int("SEO_POS_MIN", 5)
    pos_max = getenv_int("SEO_POS_MAX", 25)
    wave_size = getenv_int("MAX_WEEKLY_WAVE", 10) if wave == "daily_small" else getenv_int("MAX_WEEKLY_WAVE", 30)

    opportunities = [
        row for row in index
        if row.get("impressions", 0) >= min_impressions
        and pos_min <= row.get("avg_position", 99) <= pos_max
    ][:wave_size]

    if not opportunities:
        # Fall back: top queries regardless of position
        opportunities = index[:min(5, wave_size)]

    plan = {
        "wave": wave,
        "created": str(date.today()),
        "opportunities": opportunities,
        "count": len(opportunities),
    }

    plan_dir = Path(f"reports/{site_id}/seo_plans")
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plan_dir / f"plan_{date.today()}_{wave}.json"
    plan_file.write_text(json.dumps(plan, indent=2))

    return {"ok": True, "opportunities": len(opportunities), "file": str(plan_file)}


def seo_apply_task(site_id="superparty"):
    """Apply latest SEO plan by creating a GitHub PR."""
    from agent.common.git_pr import create_pr

    plan_dir = Path(f"reports/{site_id}/seo_plans")
    if not plan_dir.exists():
        return {"ok": False, "error": "no_plan"}

    plans = sorted(plan_dir.glob("plan_*.json"))
    if not plans:
        return {"ok": False, "error": "no_plan"}

    latest = json.loads(plans[-1].read_text())
    opportunities = latest.get("opportunities", [])
    if not opportunities:
        return {"ok": False, "error": "no_opportunities_in_plan"}

    # Create a report file to commit
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
        body=f"Automated SEO opportunity report.\n\nTop opportunity: {opportunities[0].get('query') if opportunities else 'none'}",
        files={str(report_file): "\n".join(lines)},
    )
    return result
