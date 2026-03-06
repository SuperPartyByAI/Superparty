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
    from pathlib import Path
    from datetime import date
    from agent.common.env import getenv_int

    index_file = Path(f"reports/{site_id}/gsc/index.json")
    if not index_file.exists():
        return {"ok": True, "note": "no_data_yet", "reason": "no_index_file", "next_check": "daily"}

    index = json.loads(index_file.read_text())
    if not index:
        return {"ok": True, "note": "no_data_yet", "reason": "index_empty", "next_check": "daily"}

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
        opportunities = index[:min(5, wave_size)]

    plan = {"wave": wave, "created": str(date.today()), "opportunities": opportunities, "count": len(opportunities)}
    plan_dir = Path(f"reports/{site_id}/seo_plans")
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plan_dir / f"plan_{date.today()}_{wave}.json"
    plan_file.write_text(json.dumps(plan, indent=2))
    return {"ok": True, "opportunities": len(opportunities), "file": str(plan_file)}


def seo_apply_task():
    import pathlib
    import os
    res = {}
    
    ga4_plans = sorted(pathlib.Path("reports/superparty").glob("seo_plan_ga4_*.json"), reverse=True)
    if ga4_plans:
        try:
            from agent.tasks.seo_ga4_patch import seo_apply_ga4_plan
            res["ga4"] = seo_apply_ga4_plan(site_id="superparty")
        except Exception as e:
            res["ga4_error"] = str(e)
            
    apply_mode = os.environ.get("SEO_APPLY_MODE", "report").strip()
    if apply_mode == "real" or not ga4_plans:
        res["gsc"] = _orig_seo_apply_task(apply_mode=apply_mode)
        
    if "ga4" in res and "gsc" not in res:
        return res["ga4"]
    if "gsc" in res and "ga4" not in res:
        return res["gsc"]
    return res

def _orig_seo_apply_task(site_id="superparty", apply_mode="report"):
    """Apply SEO plan. If apply_mode='real', safely inject content into Astro files."""
    import json
    import re
    import os
    from pathlib import Path
    from datetime import date
    from agent.common.git_pr import create_pr

    apply_mode = os.environ.get("SEO_APPLY_MODE", apply_mode).strip()

    plan_dir = Path(f"reports/{site_id}/seo_plans")
    if not plan_dir.exists():
        return {"ok": True, "note": "no_plan", "reason": "plan_dir_missing"}

    plans = sorted(plan_dir.glob("plan_*.json"))
    if not plans:
        return {"ok": True, "note": "no_plan", "reason": "no_plan_files"}

    latest = json.loads(plans[-1].read_text(encoding='utf-8'))
    opportunities = latest.get("opportunities", [])
    if not opportunities:
        return {"ok": True, "note": "no_opportunities", "reason": "plan_is_empty"}

    report_dir = Path(f"reports/{site_id}")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"seo_report_{date.today()}.md"

    # Clasicul generare report
    if apply_mode != "real":
        lines = [
            f"# SEO Opportunity Report — {date.today()}",
            "",
            f"Wave: {latest.get('wave')} | Opportunities: {len(opportunities)}",
            "",
            "| Query | Page | Impressions | Score |",
            "|-------|------|-------------|-------|",
        ]
        for opp in opportunities[:20]:
            page = opp.get("page", "").replace("|", "/")
            lines.append(f"| {opp.get('query','')} | {page} | {opp.get('impressions')} | {opp.get('local_intent_score', '')} |")

        report_file.write_text("\n".join(lines), encoding="utf-8")
        result = create_pr(
            site_id=site_id,
            title=f"SEO: {len(opportunities)} opportunities ({latest.get('wave')}) {date.today()}",
            body=f"Automated SEO opportunity report.\n\nTop: {opportunities[0].get('query') if opportunities else 'none'}",
            files={str(report_file): "\n".join(lines)},
        )
        return result

    # --- APPLY MODE REAL (Astro Injector) ---
    def resolve_astro_path(url_path):
        """Resolves GSC path to physical Astro file (ex: /petreceri/ilfov -> src/pages/petreceri/ilfov.astro)."""
        clean_path = url_path.replace("https://www.superparty.ro", "").replace("https://superparty.ro", "")
        clean_path = clean_path.split("?")[0].strip("/")
        
        candidates = [
            Path(f"src/pages/{clean_path}.astro"),
            Path(f"src/pages/{clean_path}/index.astro"),
            Path(f"src/pages/{clean_path}.mdx")
        ]
        if not clean_path:
            candidates.insert(0, Path("src/pages/index.astro"))

        for c in candidates:
            if c.exists():
                return c
        return None

    def call_ollama(prompt):
        import urllib.request as ureq
        url = os.environ.get("OLLAMA_URL", "http://sp_ollama:11434")
        model = os.environ.get("LLM_MODEL", "llama3.1:8b")
        payload = json.dumps({
            "model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.4}
        }).encode()
        try:
            req = ureq.Request(f"{url}/api/generate", data=payload, headers={"Content-Type": "application/json"})
            resp = ureq.urlopen(req, timeout=40)
            raw = json.loads(resp.read()).get("response", "")
            return raw
        except Exception:
            return ""

    applied_files = {}
    succes_count = 0

    import logging
    log = logging.getLogger(__name__)

    for opp in opportunities:
        url_path = opp.get("page", "")
        fpath = resolve_astro_path(url_path)
        if not fpath:
            continue

        query = opp.get("query", "")
        text = fpath.read_text(encoding="utf-8", errors="ignore")

        # GATE: If file already has FAQ injected by us (prevent duplication)
        if "id=\"seo-injected-faq\"" in text:
            continue

        prompt = (
            f"You are a local SEO expert for an animation events company in Romania.\n"
            f"Generate an EXACT JSON object containing 'faq' list and a 'logistic_text'.\n"
            f"Target Search Query: '{query}'. Context: they perform kids parties.\n\n"
            f"Rules:\n"
            f"1. Generate 4 Q/A pairs relevant to the query location. Real, generic answers.\n"
            f"2. Generate 1 short paragraph 'logistic_text' explaining we adapt to spaces and travel time may vary.\n"
            f"3. No fake prices, no fake venues, no guarantees. Use Romanian language.\n\n"
            f"Output template:\n"
            f"{{\n  \"faq\": [{{\"q\": \"...\", \"a\": \"...\"}}, ...],\n  \"logistic_text\": \"...\"\n}}"
        )

        llm_response = call_ollama(prompt)
        json_match = re.search(r"\{[^{}]+\}", llm_response, re.DOTALL)
        if not json_match:
            continue

        try:
            content = json.loads(json_match.group(0))
            faqs = content.get("faq", [])
            logistic = content.get("logistic_text", "")
            if len(faqs) < 4 or len(logistic) < 20:
                continue
        except Exception:
            continue

        # Construct safe ASTRO HTML block
        inject_html = "\\n\\n<section id=\"seo-injected-faq\" class=\"hub-section\">\\n  <div class=\"container\">\\n"
        inject_html += f"    <h2 class=\"sec-title\">Informații Utile: <span style=\"color:var(--primary)\">{query.title()}</span></h2>\\n"
        inject_html += f"    <p class=\"sec-sub\">{logistic}</p>\\n"
        inject_html += "    <div class=\"faq-list\">\\n"
        for item in faqs:
            inject_html += f"      <div class=\"faq-item\">\\n        <h3>❓ {item.get('q')}</h3>\\n        <p>{item.get('a')}</p>\\n      </div>\\n"
        
        inject_html += "    </div>\\n"
        
        # QUALITY GATE 3 internal links requirements
        hub_links = "    <div style=\"margin-top:2rem; padding:1.5rem; background:rgba(255,107,53,0.1); border-radius:12px; font-size:0.9rem;\">\\n"
        hub_links += "      <strong>Vezi și:</strong> <a href=\"/animatori-petreceri-copii\" style=\"color:var(--primary);\">🔗 Animatori Petreceri Copii (Pilon)</a> | "
        hub_links += "<a href=\"/arie-acoperire\" style=\"color:var(--primary);\">🔗 Arie Acoperire Completă</a> | "
        hub_links += "<a href=\"/petreceri/ilfov\" style=\"color:var(--primary);\">🔗 Hub județul Ilfov</a>\\n    </div>\\n"
        
        inject_html += hub_links
        inject_html += "  </div>\\n</section>\\n\\n"

        # Replace just before </Layout>
        if "</Layout>" in text:
            new_text = text.replace("</Layout>", inject_html + "</Layout>")
            
            # QUALITY GATE Validation (min length modification)
            if len(new_text) - len(text) > 1000:
                fpath.write_text(new_text, encoding="utf-8")
                applied_files[str(fpath)] = new_text
                succes_count += 1

        # Stop applying when wave size is completed
        if succes_count >= 5:
            break

    if not applied_files:
        return {"ok": True, "note": "no_pages_passed_gate"}

    pr_result = create_pr(
        site_id=site_id,
        title=f"SEO Apply Real: {succes_count} pagini optimizate on-page ({date.today()})",
        body=f"S-a folosit funcția llm de apply safe pentru modificari pe text.\n\nPagini îmbunătățite cu FAQ și link-uri:\n" + "\n".join([f"- `{k}`" for k in applied_files.keys()]),
        files=applied_files,
    )
    return pr_result
