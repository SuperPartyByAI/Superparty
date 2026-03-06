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

    import hashlib
    plan_json_str = json.dumps(opportunities, sort_keys=True)
    plan_hash = hashlib.sha256(plan_json_str.encode('utf-8')).hexdigest()
    
    plan = {"wave": wave, "created": str(date.today()), "opportunities": opportunities, "count": len(opportunities), "hash": plan_hash}
    plan_dir = Path(f"reports/{site_id}/seo_plans")
    plan_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if a plan with the same hash already exists today
    existing_plans = sorted(plan_dir.glob(f"plan_*.json"))
    if existing_plans:
        import logging
        try:
            last_plan = json.loads(existing_plans[-1].read_text(encoding='utf-8'))
            if last_plan.get("hash") == plan_hash:
                logging.getLogger(__name__).info("SEO Plan deduplicated (same hash).")
                return {"ok": True, "opportunities": len(opportunities), "note": "deduped_hash"}
        except Exception:
            pass

    import time
    run_id = time.strftime("%H%M%S")
    plan_file = plan_dir / f"plan_{date.today()}_{run_id}_{wave}.json"
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

import json
import re
import html
import hashlib
import urllib.parse
from pathlib import Path
from datetime import date
from agent.common.git_pr import git_commit_push_pr

SEO_MARKER_START = "<!-- SEO_INJECT_START:v1 -->"
SEO_MARKER_END = "<!-- SEO_INJECT_END:v1 -->"

def resolve_astro_path(url_path):
    clean_path = urllib.parse.unquote(url_path)
    clean_path = clean_path.replace("https://www.superparty.ro", "").replace("https://superparty.ro", "")
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

def get_deterministic_payload(clean_path, manifest_data):
    page_type = "unknown"
    location_label = ""
    
    path_segments = [s for s in clean_path.split("/") if s]
    slug = path_segments[-1] if path_segments else ""

    if clean_path == "animatori-petreceri-copii":
        page_type = "pilon"
        location_label = "București și Ilfov"
    elif slug == "ilfov":
        page_type = "hub_ilfov"
        location_label = "Ilfov"
    elif slug == "bucuresti":
        page_type = "hub_bucuresti"
        location_label = "București"
    elif "sector-" in slug:
        page_type = "sector"
        sec_num = slug.replace("sector-", "")
        location_label = f"Sector {sec_num}, București"
    elif manifest_data.get(slug, {}).get("county", "").strip().lower() == "ilfov":
        page_type = "localitate_ilfov"
        location_label = manifest_data[slug].get("name", slug.title().replace("-", " "))
    else:
        location_label = slug.title().replace("-", " ")

    payload = {
        "page_type": page_type,
        "location_label": location_label,
        "title": f"Animatori petreceri copii în {location_label} | Superparty",
        "description": f"Animatori pentru petreceri copii în {location_label}. Programe adaptate vârstei, în spații private sau săli puse la dispoziție. Rezervă o ofertă.",
        "logistic_text": "Ne deplasăm pentru petreceri de copii și adaptăm programul la vârstă, număr de participanți și spațiul disponibil (acasă, curte sau o sală pusă la dispoziție de organizator). Timpul de deplasare și montajul pot varia.",
        "hub_url": "/petreceri/ilfov",
        "hub_label": "Hub județul Ilfov"
    }

    if page_type == "pilon":
        payload["title"] = "Animatori Petreceri Copii București și Ilfov | SuperParty"
        payload["description"] = "Animatori profesioniști pentru petreceri copii în București și Ilfov. Programe adaptate vârstei, personaje, jocuri și activități. Cere ofertă."
        payload["logistic_text"] = "Ne deplasăm în București și Ilfov și adaptăm programul la vârstă, numărul de copii și spațiul disponibil. Detaliile logistice (deplasare, montaj, durată) se stabilesc la rezervare, în funcție de interval."
    elif page_type == "hub_ilfov":
        payload["description"] = "Animatori pentru petreceri copii în Ilfov (orașe și comune). Programe flexibile, adaptate spațiului și vârstei. Solicită ofertă."
        payload["logistic_text"] = "Acoperim orașe și comune din Ilfov, cu programe pentru petreceri de copii adaptate spațiului și vârstei. Detaliile logistice (deplasare, montaj, durată) se stabilesc la rezervare, în funcție de interval și locație."
        payload["hub_url"] = "/petreceri/bucuresti"
        payload["hub_label"] = "Hub București"
    elif page_type == "hub_bucuresti":
        payload["description"] = "Animatori pentru petreceri copii în București, pe sectoare. Activități adaptate vârstei și spațiului. Cere ofertă și verifică disponibilitatea."
    elif page_type == "sector":
        payload["title"] = f"Animatori petreceri copii Sector {slug.replace('sector-', '')} București | Superparty"
        payload["description"] = f"Animatori pentru petreceri copii în Sector {slug.replace('sector-', '')}, București. Activități adaptate vârstei, pentru aniversări și evenimente. Cere ofertă."
        payload["hub_url"] = "/petreceri/bucuresti"
        payload["hub_label"] = "Hub București"

    base_pool = [
        {"q": f"Ajungeți și în {location_label}?", "a": f"Da, ne putem deplasa în {location_label} și în zonele apropiate, în funcție de disponibilitate și interval."},
        {"q": "Cu cât timp înainte e bine să fac rezervarea?", "a": "Recomandăm rezervarea din timp, mai ales pentru weekend. Confirmarea depinde de program și de durata aleasă."},
        {"q": "Programul se poate adapta vârstei copiilor?", "a": "Da. Activitățile sunt ajustate în funcție de vârstă și de energia grupului, astfel încât copiii să rămână implicați."},
        {"q": "Se pot ține activitățile și în spații mai mici?", "a": "Da. Putem adapta jocurile și dinamica pentru apartament, living sau spații restrânse, fără a compromite siguranța."},
        {"q": "Ce durată are, de obicei, un program de animatori?", "a": "Durata se alege în funcție de vârstă și de tipul evenimentului. Stabilim împreună varianta potrivită."},
        {"q": "Aveți programe pentru grădinițe / afterschool?", "a": "Da, putem adapta formatul pentru grupuri organizate, cu activități potrivite și structură clară."},
        {"q": "Ce aveți nevoie la fața locului?", "a": "De regulă, un spațiu liber pentru activități și acces la detaliile evenimentului (număr copii, vârstă, durată)."},
        {"q": "Cum se stabilește costul?", "a": "Costul depinde de durata programului și de detaliile evenimentului. Îți trimitem o ofertă după ce stabilim cerințele."}
    ]

    h = hashlib.sha256((slug or "home").encode("utf-8")).hexdigest()
    nums = [int(h[i:i+2], 16) for i in range(0, 32, 2)]
    order = sorted(range(len(base_pool)), key=lambda i: nums[i] if i < len(nums) else i)
    payload["faqs"] = [base_pool[i] for i in order[:4]]

    return payload

def _find_layout_open_tag(text: str):
    m = re.search(r"<Layout\b[\s\S]*?>", text)
    if not m: return None, None
    return m.group(0), (m.start(), m.end())

def _upsert_layout_prop(layout_tag: str, prop: str, value: str):
    escaped = value.replace('"', '\\"').strip()
    if re.search(rf"\b{re.escape(prop)}\s*=\s*\"[^\"]*\"", layout_tag):
        return re.sub(rf"(\b{re.escape(prop)}\s*=\s*)\"[^\"]*\"", rf'\1"{escaped}"', layout_tag)
    if re.search(rf"\b{re.escape(prop)}\s*=\s*\{{[\s\S]*?\}}", layout_tag):
        return re.sub(rf"(\b{re.escape(prop)}\s*=\s*)\{{[\s\S]*?\}}", rf'\1"{escaped}"', layout_tag)
    return re.sub(r"<Layout\b", f'<Layout\n  {prop}="{escaped}"', layout_tag, count=1)

def patch_layout_title_description(text: str, title: str, description: str):
    layout_tag, span = _find_layout_open_tag(text)
    if not layout_tag or not span: return text
    patched = _upsert_layout_prop(layout_tag, "title", title)
    patched = _upsert_layout_prop(patched, "description", description)
    start, end = span
    return text[:start] + patched + text[end:]

def build_seo_inject_block(heading, logistic_text, faq_items, hub_url, hub_label):
    h = html.escape(heading)
    logi = html.escape(logistic_text)
    faq_html_parts = []
    for it in faq_items:
        q = html.escape(it.get("q","").strip())
        a = html.escape(it.get("a","").strip())
        if q and a:
            faq_html_parts.append(f'      <div class="faq-item">\n        <h3>❓ {q}</h3>\n        <p>{a}</p>\n      </div>\n')
    faq_html = "".join(faq_html_parts)
    url = html.escape(hub_url)
    lbl = html.escape(hub_label)

    return (
        f"\n{SEO_MARKER_START}\n"
        f'<section id="seo-injected" class="hub-section">\n'
        f'  <div class="container">\n'
        f'    <h2 class="sec-title">{h}</h2>\n'
        f'    <p class="sec-sub">{logi}</p>\n'
        f'    <div class="faq-list">\n'
        f"{faq_html}"
        f'    </div>\n'
        f'    <div class="seo-links" style="margin-top:2rem; padding:1.5rem; background:rgba(255,107,53,0.1); border-radius:12px; font-size:0.95rem;">\n'
        f'      <strong>Vezi și:</strong>\n'
        f'      <a href="{url}" style="color:var(--primary);">{lbl}</a> |\n'
        f'      <a href="/animatori-petreceri-copii" style="color:var(--primary);">Animatori petreceri copii (pilon)</a> |\n'
        f'      <a href="/arie-acoperire" style="color:var(--primary);">Arie de acoperire</a>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>\n'
        f"{SEO_MARKER_END}\n"
    )

def replace_or_insert_seo_block(text: str, new_block: str):
    if SEO_MARKER_START in text and SEO_MARKER_END in text:
        pattern = re.compile(re.escape(SEO_MARKER_START) + r"[\s\S]*?" + re.escape(SEO_MARKER_END), re.MULTILINE)
        return pattern.sub(new_block.strip() + "\n", text, count=1)
    parts = text.rsplit("</Layout>", 1)
    if len(parts) != 2: return text
    return parts[0] + new_block + "\n</Layout>" + parts[1]

def patch_const_faq_array(text: str, faq_items):
    def js_escape(s): return s.replace("\\", "\\\\").replace("'", "\\\'").strip()
    objs = []
    for it in faq_items:
        q = js_escape(it.get("q",""))
        a = js_escape(it.get("a",""))
        if q and a: objs.append(f"  {{ q: '{q}', a: '{a}' }},")
    new_arr = "const faq = [\n" + "\n".join(objs) + "\n];"
    pattern = re.compile(r"const\s+faq\s*=\s*\[[\s\S]*?\]\s*;", re.MULTILINE)
    if pattern.search(text): return pattern.sub(new_arr, text, count=1)
    return text

def _orig_seo_apply_task(site_id="superparty", apply_mode="report"):
    import os
    from pathlib import Path
    from datetime import date
    import json
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
        result = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}-report",
            commit_msg=f"feat(seo): gsc apply report {date.today()}",
            files=[str(report_file)],
            pr_title=f"SEO: {len(opportunities)} opportunities ({latest.get('wave')}) {date.today()}",
            pr_body=f"Automated SEO opportunity report.\n\nTop: {opportunities[0].get('query') if opportunities else 'none'}"
        )
        return {"ok": True, "pr_url": result}


    def _load_apply_state(state_path: Path) -> dict:
        today = str(date.today())
        if state_path.exists():
            try:
                st = json.loads(state_path.read_text(encoding="utf-8"))
            except Exception:
                st = {}
        else:
            st = {}

        if st.get("date") != today:
            st = {
                "date": today,
                "files_applied_today": 0,
                "prs_created_today": 0,
                "page_last_applied": st.get("page_last_applied", {}),
            }

        st.setdefault("page_last_applied", {})
        st.setdefault("files_applied_today", 0)
        st.setdefault("prs_created_today", 0)
        return st

    def _save_apply_state(state_path: Path, st: dict) -> None:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")

    # Load Manifest for Source of Truth
    manifest_data = {}
    manifest_path = Path("reports/seo/indexing_manifest.json")
    if manifest_path.exists():
        try:
            m_list = json.loads(manifest_path.read_text(encoding="utf-8"))
            for m in m_list:
                manifest_data[m.get("slug")] = m
        except Exception:
            pass

    audit_log = {"applied": [], "skipped": [], "unmapped": [], "date": str(date.today())}
    applied_files = []
    
    succes_count = 0
    import agent.common.env
    max_files = agent.common.env.getenv_int("SEO_REAL_MAX_FILES", 5)

    from datetime import datetime
    for opp in opportunities:
        url_path = opp.get("page", "")
        fpath = resolve_astro_path(url_path)
        if not fpath:
            audit_log["unmapped"].append({"page": url_path, "reason": "not_resolved"})
            continue
            
        # COOLDOWN Check
        last_applied_str = state["page_last_applied"].get(url_path)
        if last_applied_str:
            last_applied_date = datetime.strptime(last_applied_str, "%Y-%m-%d").date()
            if (date.today() - last_applied_date).days < cooldown_days:
                audit_log["skipped"].append({"page": url_path, "reason": "cooldown"})
                continue
            
        clean_path = urllib.parse.unquote(url_path).replace("https://www.superparty.ro", "").replace("https://superparty.ro", "").split("?")[0].strip("/")
        text = fpath.read_text(encoding="utf-8", errors="ignore")

        payload = get_deterministic_payload(clean_path, manifest_data)
        new_text = patch_layout_title_description(text, payload["title"], payload["description"])

        if payload["page_type"] == "pilon" and "const faq =" in new_text:
            new_text = patch_const_faq_array(new_text, payload["faqs"])
        else:
            block = build_seo_inject_block(
                heading=f"Informații Utile despre {payload['location_label']}",
                logistic_text=payload["logistic_text"],
                faq_items=payload["faqs"],
                hub_url=payload["hub_url"],
                hub_label=payload["hub_label"]
            )
            new_text = replace_or_insert_seo_block(new_text, block)

        text_delta = len(new_text) - len(text)
        faq_count = new_text.count("faq-item") or new_text.count("{ q: '")
        links_count = new_text.count('href="/')

        min_chars = agent.common.env.getenv_int("SEO_REAL_MIN_TEXT_CHARS", 2500)
        
        required_links_present = (
            'href="/animatori-petreceri-copii"' in new_text and
            'href="/arie-acoperire"' in new_text and
            f'href="{payload["hub_url"]}"' in new_text
        )
        gate_passed = text_delta > min_chars and faq_count >= 4 and required_links_present
        
        if gate_passed:
            fpath.write_text(new_text, encoding="utf-8")
            applied_files.append(str(fpath))
            audit_log["applied"].append({"page": url_path, "file": str(fpath), "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})
            succes_count += 1
            state["files_applied_today"] += 1
            state["page_last_applied"][url_path] = str(date.today())
        else:
            audit_log["skipped"].append({"page": url_path, "reason": "failed_gate", "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})

        if succes_count >= max_files_per_run or state["files_applied_today"] >= max_files_per_day:
            break

    report_dir.mkdir(parents=True, exist_ok=True)
    audit_file = report_dir / f"seo_apply_gsc_{date.today()}.json"
    audit_file.write_text(json.dumps(audit_log, indent=2, ensure_ascii=False), encoding="utf-8")
    applied_files.append(str(audit_file))

    if not succes_count:
        return {"ok": True, "note": "no_pages_passed_gate", "audit": str(audit_file)}

    try:
        import time
        run_id = time.strftime("%H%M%S")
        pr_url = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}T{run_id}Z",
            commit_msg=f"feat(seo): gsc apply real {date.today()}T{run_id}Z",
            files=applied_files,
            pr_title=f"SEO Apply Real: {succes_count} pagini optimizate on-page ({date.today()})",
            pr_body=f"S-a folosit funcția llm deterministica de apply safe pentru modificari pe text.\n\nPagini îmbunătățite:\n" + "\n".join([f"- `{k}`" for k in applied_files])
        )
        return {"ok": True, "pr_url": pr_url}
    except Exception as e:
        return {"ok": False, "error": str(e), "files": applied_files}
