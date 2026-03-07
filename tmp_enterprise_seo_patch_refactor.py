import os

os.chdir(r"C:\Users\ursac\Superparty")

with open('agent/tasks/seo.py', 'r', encoding='utf-8') as f:
    text = f.read()

# I will just write a new version of the enterprise code directly with the global helpers
start_idx = text.find('def seo_apply_task():')
text_before = text[:start_idx]

ent_code = """
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
        "title": f"Animatori copii în {location_label} | Superparty",
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
        payload["hub_url"] = "/animatori-petreceri-copii"
        payload["hub_label"] = "Animatori petreceri copii (pilon)"
    elif page_type == "hub_bucuresti":
        payload["description"] = "Animatori pentru petreceri copii în București, pe sectoare. Activități adaptate vârstei și spațiului. Cere ofertă și verifică disponibilitatea."
    elif page_type == "sector":
        payload["title"] = f"Animatori copii Sector {slug.replace('sector-', '')} București | Superparty"
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
    m = re.search(r"<Layout\\b[\\s\\S]*?>", text)
    if not m: return None, None
    return m.group(0), (m.start(), m.end())

def _upsert_layout_prop(layout_tag: str, prop: str, value: str):
    escaped = value.replace('"', '\\\\"').strip()
    if re.search(rf"\\b{re.escape(prop)}\\s*=\\s*\\\"[^\\\"]*\\\"", layout_tag):
        return re.sub(rf"(\\b{re.escape(prop)}\\s*=\\s*)\\\"[^\\\"]*\\\"", rf'\\1"{escaped}"', layout_tag)
    if re.search(rf"\\b{re.escape(prop)}\\s*=\\s*\\{{[\\s\\S]*?\\}}", layout_tag):
        return re.sub(rf"(\\b{re.escape(prop)}\\s*=\\s*)\\{{[\\s\\S]*?\\}}", rf'\\1"{escaped}"', layout_tag)
    return re.sub(r"<Layout\\b", f'<Layout\\n  {prop}="{escaped}"', layout_tag, count=1)

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
            faq_html_parts.append(f'      <div class="faq-item">\\n        <h3>❓ {q}</h3>\\n        <p>{a}</p>\\n      </div>\\n')
    faq_html = "".join(faq_html_parts)
    url = html.escape(hub_url)
    lbl = html.escape(hub_label)

    return (
        f"\\n{SEO_MARKER_START}\\n"
        f'<section id="seo-injected" class="hub-section">\\n'
        f'  <div class="container">\\n'
        f'    <h2 class="sec-title">{h}</h2>\\n'
        f'    <p class="sec-sub">{logi}</p>\\n'
        f'    <div class="faq-list">\\n'
        f"{faq_html}"
        f'    </div>\\n'
        f'    <div class="seo-links" style="margin-top:2rem; padding:1.5rem; background:rgba(255,107,53,0.1); border-radius:12px; font-size:0.95rem;">\\n'
        f'      <strong>Vezi și:</strong>\\n'
        f'      <a href="{url}" style="color:var(--primary);">{lbl}</a> |\\n'
        f'      <a href="/animatori-petreceri-copii" style="color:var(--primary);">Animatori petreceri copii (pilon)</a> |\\n'
        f'      <a href="/arie-acoperire" style="color:var(--primary);">Arie de acoperire</a>\\n'
        f'    </div>\\n'
        f'  </div>\\n'
        f'</section>\\n'
        f"{SEO_MARKER_END}\\n"
    )

def replace_or_insert_seo_block(text: str, new_block: str):
    if SEO_MARKER_START in text and SEO_MARKER_END in text:
        pattern = re.compile(re.escape(SEO_MARKER_START) + r"[\\s\\S]*?" + re.escape(SEO_MARKER_END), re.MULTILINE)
        return pattern.sub(new_block.strip() + "\\n", text, count=1)
    parts = text.rsplit("</Layout>", 1)
    if len(parts) != 2: return text
    return parts[0] + new_block + "\\n</Layout>" + parts[1]

def patch_const_faq_array(text: str, faq_items):
    def js_escape(s): return s.replace("\\\\", "\\\\\\\\").replace("'", "\\\\\\'").strip()
    objs = []
    for it in faq_items:
        q = js_escape(it.get("q",""))
        a = js_escape(it.get("a",""))
        if q and a: objs.append(f"  {{ q: '{q}', a: '{a}' }},")
    new_arr = "const faq = [\\n" + "\\n".join(objs) + "\\n];"
    pattern = re.compile(r"const\\s+faq\\s*=\\s*\\[[\\s\\S]*?\\]\\s*;", re.MULTILINE)
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

        report_file.write_text("\\n".join(lines), encoding="utf-8")
        result = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}-report",
            commit_msg=f"feat(seo): gsc apply report {date.today()}",
            files=[str(report_file)],
            pr_title=f"SEO: {len(opportunities)} opportunities ({latest.get('wave')}) {date.today()}",
            pr_body=f"Automated SEO opportunity report.\\n\\nTop: {opportunities[0].get('query') if opportunities else 'none'}"
        )
        return {"ok": True, "pr_url": result}

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

    for opp in opportunities:
        url_path = opp.get("page", "")
        fpath = resolve_astro_path(url_path)
        if not fpath:
            audit_log["unmapped"].append({"page": url_path, "reason": "not_resolved"})
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

        min_chars = agent.common.env.getenv_int("SEO_REAL_MIN_TEXT_CHARS", 1000)
        
        gate_passed = text_delta > min_chars and faq_count >= 4 and links_count >= 3
        
        if gate_passed:
            fpath.write_text(new_text, encoding="utf-8")
            applied_files.append(str(fpath))
            audit_log["applied"].append({"page": url_path, "file": str(fpath), "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})
            succes_count += 1
        else:
            audit_log["skipped"].append({"page": url_path, "reason": "failed_gate", "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})

        if succes_count >= max_files:
            break

    report_dir.mkdir(parents=True, exist_ok=True)
    audit_file = report_dir / f"seo_apply_gsc_{date.today()}.json"
    audit_file.write_text(json.dumps(audit_log, indent=2, ensure_ascii=False), encoding="utf-8")
    applied_files.append(str(audit_file))

    if not succes_count:
        return {"ok": True, "note": "no_pages_passed_gate", "audit": str(audit_file)}

    try:
        pr_url = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}",
            commit_msg=f"feat(seo): gsc apply real {date.today()}",
            files=applied_files,
            pr_title=f"SEO Apply Real: {succes_count} pagini optimizate on-page ({date.today()})",
            pr_body=f"S-a folosit funcția llm deterministica de apply safe pentru modificari pe text.\\n\\nPagini îmbunătățite:\\n" + "\\n".join([f"- `{k}`" for k in applied_files])
        )
        return {"ok": True, "pr_url": pr_url}
    except Exception as e:
        return {"ok": False, "error": str(e), "files": applied_files}
"""

with open('agent/tasks/seo.py', 'w', encoding='utf-8') as f:
    f.write(text_before + "\n" + ent_code)

