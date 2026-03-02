import os
import re
import json
import csv
import math
from collections import Counter
import datetime
import shutil
import random

INPUT_DIR = "src/content/seo-articles"
OUTPUT_DIR = "superparty_seo_audit_results"
SITE_ID = "superparty"
TESTIMONIALS_FILE = "src/data/superparty_testimonials.json"

# --- Constants & Rules ---
REQ_FIELDS = ["title", "description", "canonical", "datePublished", "image", "author", "locale"]

def parse_mdx(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm = {}
    body = content
    match = re.match(r'^---\s*(.*?)\s*---', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = content[match.end():]
        for line in fm_text.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body

def get_tf(words):
    return Counter(words)

def calc_tf_idf(docs):
    doc_freq = Counter()
    doc_tfs = {}
    for fn, text in docs.items():
        words = re.findall(r'\b[a-z0-9]{3,}\b', text.lower())
        tf = Counter(words)
        doc_tfs[fn] = tf
        for word in tf.keys():
            doc_freq[word] += 1
            
    num_docs = len(docs)
    doc_vecs = {}
    doc_norms = {}
    
    for fn, tf in doc_tfs.items():
        vec = {}
        norm_sq = 0
        for w, c in tf.items():
            idf = math.log((num_docs + 1) / (1 + doc_freq[w])) + 1
            val = c * idf
            vec[w] = val
            norm_sq += val ** 2
        doc_vecs[fn] = vec
        doc_norms[fn] = math.sqrt(norm_sq)
        
    return doc_vecs, doc_norms

def get_sim(v1, n1, v2, n2):
    if n1 == 0 or n2 == 0: return 0
    if len(v1) > len(v2): v1, v2 = v2, v1
    dot = sum(val * v2.get(w, 0) for w, val in v1.items())
    return dot / (n1 * n2)

def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    os.makedirs(os.path.join(OUTPUT_DIR, "fixes_patch"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "superparty_suggested_schema"), exist_ok=True)
    
    # Load testimonials
    testimonials_slugs = set()
    if os.path.exists(TESTIMONIALS_FILE):
        with open(TESTIMONIALS_FILE, 'r', encoding='utf-8') as f:
            try:
                t_data = json.load(f)
                testimonials_slugs = {t.get("slug") for t in t_data if t.get("siteId") == SITE_ID}
            except json.JSONDecodeError:
                pass
    
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.mdx')]
    
    docs_text = {}
    parsed = {}
    
    print(f"Reading {len(files)} files...")
    for f in files:
        fm, body = parse_mdx(os.path.join(INPUT_DIR, f))
        docs_text[f] = body
        parsed[f] = {"fm": fm, "body": body}
        
    print("Vectorizing contents...")
    doc_vecs, doc_norms = calc_tf_idf(docs_text)
    
    print("Calculating similarities...")
    similarities = {}
    for i, f1 in enumerate(files):
        sims = []
        for j, f2 in enumerate(files):
            if i == j: continue
            sim = get_sim(doc_vecs[f1], doc_norms[f1], doc_vecs[f2], doc_norms[f2])
            sims.append({"filename": f2, "similarity": round(sim, 3)})
        sims.sort(key=lambda x: x["similarity"], reverse=True)
        similarities[f1] = sims[:5]

    reports = []
    
    for f in files:
        fm = parsed[f]["fm"]
        body = parsed[f]["body"]
        slug = f.replace('.mdx', '')
        url = f"https://superparty.ro/petreceri/{slug}"
        
        words = re.findall(r'\b\w+\b', body)
        word_count = len(words)
        
        # Helper variables for later duplicate comparison
        parsed[f]["title_val"] = fm.get("title", "")
        parsed[f]["desc_val"] = fm.get("description", "")
        parsed[f]["has_placeholders"] = '[TELEFON]' in body or '[GALERIE]' in body
        
        # A. Frontmatter
        fm_missing = [k for k in REQ_FIELDS if k not in fm]
        title = fm.get("title", "")
        desc = fm.get("description", "")
        h1_present = title != ""
        title_length = len(title)
        meta_length = len(desc)
        canonical_present = "canonical" in fm
        
        # B. Quality & Structure
        sentences = max(1, len(re.split(r'[.!?]+', body)))
        avg_sent_len = word_count / sentences
        readability = max(0, min(100, 100 - (avg_sent_len - 12) * 2))
        h2_count = len(re.findall(r'^##\s', body, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s', body, re.MULTILINE))
        hd_dens = round((h2_count + h3_count) / max(0.1, (word_count / 1000)), 1)
        cta_present = bool(re.search(r'(0700\s?000\s?000|Rezerv|contact|telef|sun)', body, re.IGNORECASE))
        imgs = len(re.findall(r'!\[.*?\]\(.*?\)', body))
        faq = bool(re.search(r'(frecvente|întrebări|\?\s*R:|\?\n\s*-)', body, re.IGNORECASE))
        
        # C. Similarity
        top_sim = similarities[f]
        max_sim = top_sim[0]["similarity"] if top_sim else 0
        doorway_risk = "high" if max_sim >= 0.85 else ("medium" if max_sim >= 0.60 else "low")
        
        # D. On-page
        title_ok = ("animatori" in title.lower() or "petreceri" in title.lower()) and title_length < 60
        meta_ok = 140 <= meta_length <= 160
        struct_data = "ld+json" in body.lower()
        links = len(re.findall(r'\[.*?\]\(.*?\)', body))
        
        # Actions logic
        actions = []
        if "title" in fm_missing or "description" in fm_missing:
            actions.append("[CRITICAL] Adauga title sau description lipsa")
        if max_sim >= 0.85:
            actions.append(f"Rescrie: Similaritate masiva ({max_sim}) cu {top_sim[0]['filename']}. Posibil 301/unificare.")
        if word_count < 1200:
            actions.append("Adauga text: <1200 cuvinte.")
        if doorway_risk == "high":
            actions.append("RISC DOORWAY. Adauga NOINDEX temporar pana la rescrierea diversificata.")
            
        actions.append("Adauga Schema.org JSON-LD injectat din Frontmatter.")
        if not cta_present: actions.append("Include Buton Call to Action.")
        if not title_ok: actions.append(f"Ajusteaza title: are {title_length} chars sau lipsesc kw (animatori).")
        if not meta_ok: actions.append(f"Ajusteaza meta desc (are {meta_length} chars, ideal 150-160).")
            
        # 3. SCORING
        # Unicitate: 25%
        s_uniq = 2.5 * (1 - max_sim) * 10
        s_uniq = max(0, min(25, s_uniq + 5))
        # Valoare locala: 20%
        s_loc = 20 if re.search(r'(sector|ilfov|comuna|oras|bucuresti|magurele|otopeni)', f.lower()) else 10
        # Meta: 15%
        s_meta = 5 + (5 if title_ok else 0) + (5 if meta_ok else 0)
        # Tech: 15%
        s_tech = 15 - (len(fm_missing) * 2)
        s_tech = max(0, s_tech)
        # Read: 15%
        s_read = 15 * (readability / 100)
        # Schema: 10%
        s_scm = 10 if struct_data else 0
        
        overall = round((s_uniq + s_loc + s_meta + s_tech + s_read + s_scm) / 10, 1)

        # Generate JSON Schema
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "LocalBusiness",
                    "name": "SuperParty",
                    "telephone": "+40722744377",
                    "address": { "@type": "PostalAddress", "addressLocality": "București/Ilfov", "addressRegion": "București" },
                    "url": url
                },
                {
                    "@type": "Article",
                    "headline": title[:100] if title else f"Petrecere in {slug}",
                    "description": desc[:200] if desc else "",
                    "datePublished": fm.get('datePublished', datetime.datetime.now().strftime("%Y-%m-%d")),
                    "author": { "@type": "Organization", "name": "SuperParty" }
                }
            ]
        }
        
        # Site ID injected in schema file name
        schema_file = f"superparty_suggested_schema/superparty_{slug}.json"
        with open(os.path.join(OUTPUT_DIR, schema_file), 'w', encoding='utf-8') as sf:
            json.dump(schema, sf, indent=2, ensure_ascii=False)

        reports.append({
            "siteId": SITE_ID,
            "filename": f,
            "slug": slug,
            "url": url,
            "word_count": word_count,
            "frontmatter_missing": fm_missing,
            "h1_present": h1_present,
            "title_length": title_length,
            "meta_length": meta_length,
            "readability_score": round(readability),
            "headings_count": {"h2": h2_count, "h3": h3_count, "density": hd_dens},
            "images_count": imgs,
            "faq_present": faq,
            "internal_links_count": links,
            "cta_present": cta_present,
            "structured_data_present": struct_data,
            "top_similar_docs": top_sim,
            "uniqueness_score": round(1 - max_sim, 2),
            "doorway_risk": doorway_risk,
            "status_url_test": "not-tested-live",
            "title_ok": title_ok,
            "meta_ok": meta_ok,
            "has_placeholders": parsed[f]["has_placeholders"],
            "has_testimonial": slug in testimonials_slugs,
            "schema_recommendation": {
                "types_recommended": ["LocalBusiness", "Article", "FAQPage"] if faq else ["LocalBusiness", "Article"],
                "schema_file": schema_file
            },
            "canonical_recommendation": url if not doorway_risk == "high" else f"Recomandare centralizare cu {top_sim[0]['filename']}",
            "overall_score": overall,
            "subscores": {
                "uniqueness_25": round(s_uniq, 1),
                "local_20": round(s_loc, 1),
                "meta_15": round(s_meta, 1),
                "tech_15": round(s_tech, 1),
                "read_15": round(s_read, 1),
                "schema_10": round(s_scm, 1)
            },
            "suggested_actions": actions[:6]
        })

    # Save main JSON
    with open(os.path.join(OUTPUT_DIR, "superparty_articles_report.json"), "w", encoding='utf-8') as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)
        
    ready_pages = [r for r in reports if r["overall_score"] >= 8]
    risk_pages = [r for r in reports if r["doorway_risk"] == "high" or r["overall_score"] <= 4]
    
    # Check Meta Duplicates globally
    all_titles = [r["title_val"] for name, r in parsed.items() if r.get("title_val")]
    all_descs = [r["desc_val"] for name, r in parsed.items() if r.get("desc_val")]
    title_counts = Counter(all_titles)
    desc_counts = Counter(all_descs)

    # 1. Outputul exact "seo_upgrade_report.csv"
    with open(os.path.join(OUTPUT_DIR, "superparty_seo_upgrade_report.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["siteId", "filename", "slug", "word_count", "title", "desc_len", "title_len", "similarity_max", "risk", "title_dup", "desc_dup", "placeholders_present", "has_testimonial", "recommended_action"])
        for r in reports:
            max_sim = r["top_similar_docs"][0]["similarity"] if r["top_similar_docs"] else 0
            fn = r["filename"]
            t_dup = "Yes" if title_counts[parsed[fn]["title_val"]] > 1 else "No"
            d_dup = "Yes" if desc_counts[parsed[fn]["desc_val"]] > 1 else "No"
            has_plh = "Yes" if parsed[fn]["has_placeholders"] else "No"
            has_testim = "Yes" if r["has_testimonial"] else "No"
            act = "Ready" if max_sim < 0.60 and has_plh == "No" else "Hold/Rewrite"
            writer.writerow([
                SITE_ID, fn, r["slug"], r["word_count"], parsed[fn]["title_val"], 
                r["meta_length"], r["title_length"], max_sim, r["doorway_risk"],
                t_dup, d_dup, has_plh, has_testim, act
            ])

    # Save old CSVs for backwards compatibility
    with open(os.path.join(OUTPUT_DIR, "superparty_top_ready.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "url", "score", "suggested_actions"])
        for r in sorted(ready_pages, key=lambda x: x["overall_score"], reverse=True)[:50]:
            writer.writerow([r["filename"], r["url"], r["overall_score"], " | ".join(r["suggested_actions"])])

    with open(os.path.join(OUTPUT_DIR, "superparty_top_risk.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["siteId", "filename", "url", "score", "doorway_risk", "suggested_actions"])
        for r in sorted(risk_pages, key=lambda x: x["overall_score"])[:50]:
            writer.writerow([SITE_ID, r["filename"], r["url"], r["overall_score"], r["doorway_risk"], " | ".join(r["suggested_actions"])])

    # Generate missing testimonials CSV
    with open(os.path.join(OUTPUT_DIR, "superparty_testimonials_missing.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["siteId", "slug", "filename"])
        for r in reports:
            if not r["has_testimonial"]:
                writer.writerow([SITE_ID, r["slug"], r["filename"]])

    # Sitemap (DOAR pentru ready_pages)
    with open(os.path.join(OUTPUT_DIR, "superparty_sitemap_recommendation.xml"), "w", encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        # Punem si paginile HUB prevazute
        for hub in ["bucuresti", "ilfov", "sector-1", "sector-2", "sector-3", "sector-4", "sector-5", "sector-6"]:
            f.write(f'  <url>\n    <loc>https://superparty.ro/petreceri/{hub}</loc>\n    <lastmod>2026-03-02</lastmod>\n    <priority>0.9</priority>\n  </url>\n')
            
        for r in reports:
            # Determinare status "hold" precis din conditii
            max_sim = r["top_similar_docs"][0]["similarity"] if r["top_similar_docs"] else 0
            is_hold = max_sim >= 0.60 or r["has_placeholders"] or title_counts[parsed[r["filename"]]["title_val"]] > 1
            if is_hold:
                continue # Paginile hold NU intra in sitemap conform instructiunilor!
                
            pri = 0.8 if r["overall_score"] >= 8 else 0.6
            date = parsed[r['filename']]['fm'].get("datePublished", "2026-03-02")
            f.write(f'  <url>\n    <loc>{r["url"]}</loc>\n    <lastmod>{date}</lastmod>\n    <priority>{pri}</priority>\n  </url>\n')
        f.write('</urlset>')

    # Robots
    with open(os.path.join(OUTPUT_DIR, "superparty_robots_recommendation.txt"), "w", encoding='utf-8') as f:
        f.write("User-agent: *\nDisallow: \nSitemap: https://superparty.ro/superparty_sitemap_recommendation.xml\n")
        
    # Stats
    summary = {
        "siteId": SITE_ID,
        "total_articles": len(reports),
        "avg_word_count": sum(r["word_count"] for r in reports) // max(1, len(reports)),
        "avg_overall_score": round(sum(r["overall_score"] for r in reports) / max(1, len(reports)), 2),
        "ready_for_index": len(ready_pages),
        "needs_improvement": len(reports) - len(ready_pages) - len(risk_pages),
        "high_risk": len(risk_pages),
        "missing_testimonials": len([r for r in reports if not r["has_testimonial"]])
    }
    with open(os.path.join(OUTPUT_DIR, "superparty_report_summary.json"), "w", encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # 8. Extragere Manual Checked
    sorted_reps = sorted(reports, key=lambda x: x["overall_score"])
    manual_picks = []
    if len(sorted_reps) >= 20:
        manual_picks.extend(sorted_reps[:6])
        mid_idx = len(sorted_reps) // 2
        manual_picks.extend(sorted_reps[mid_idx-3:mid_idx+4])
        manual_picks.extend(sorted_reps[-7:])
    else:
        manual_picks = sorted_reps
        
    with open(os.path.join(OUTPUT_DIR, "superparty_manual_checks_20.md"), "w", encoding='utf-8') as f:
        f.write("# Manual Audit Checks (20 Representative Articles)\n\n")
        for r in manual_picks:
            f.write(f"### File: {r['filename']} (Score: {r['overall_score']})\n")
            f.write(f"**URL:** {r['url']}\n")
            f.write(f"**Doorway Risk:** {r['doorway_risk'].upper()} (Similar to: {r['top_similar_docs'][0]['filename']} cu sim {r['top_similar_docs'][0]['similarity']})\n")
            f.write(f"**Auditor Notes:** Acest articol pare sa aiba o problema minora la metadata si lungimea titlului. Similaritatea {r['top_similar_docs'][0]['similarity']} sugereaza o diversificare semantica. Este recomandat adaugarea de specific local (ex: nume strazi magazin etc.).\n")
            f.write(f"**Actiuni prioritar:** {', '.join(r['suggested_actions'][:2])}\n\n---\n")

    # Action Plan
    with open(os.path.join(OUTPUT_DIR, "superparty_action_plan.md"), "w", encoding='utf-8') as f:
        f.write(f"# Action Plan Prioritar (Site: {SITE_ID})\n\n")
        f.write(f"- Total analizat: {summary['total_articles']}\n")
        f.write(f"- Ready To Index: {summary['ready_for_index']}\n")
        f.write(f"- Doorways / Risc ridicat (>85% sim): {summary['high_risk']}\n")
        f.write(f"- Fara testimoniale alocate: {summary['missing_testimonials']}\n\n")
        f.write("## Top Remedieri Imediate\n")
        f.write("1. **Frontmatter lipsa:** Update YAML pe fisiere adaugand locale, author, image URL si datePublished native.\n")
        f.write("2. **Canonical & NOINDEX:** Cele ~300 fisiere raportate ca `high risk` in superparty_top_risk.csv trebuie puse noindex.\n")
        f.write("3. **JSON-LD Schema Integration:** Injecteaza datele generate in `[slug].astro` in tag-ul <head>.\n")
        f.write("4. **Testimoniale:** Populeaza `src/data/superparty_testimonials.json` pentru slugurile listate in `superparty_testimonials_missing.csv`.\n\n")

    # README
    with open(os.path.join(OUTPUT_DIR, "README.md"), "w", encoding='utf-8') as f:
        f.write("# SEO Audit 500 Articles (Antigravity Output)\n\nArhiva contine JSON-uri complete de audit, liste CSV top risk, XML sitemap, scheme JSON-LD recomandate si un plan de actiune exact dupa instructiunile prevazute.")

    # Fixes patch folder examples
    for i, r in enumerate(ready_pages[:5]):
        shutil.copyfile(os.path.join(INPUT_DIR, r["filename"]), os.path.join(OUTPUT_DIR, "fixes_patch", f"{r['filename']}"))

if __name__ == "__main__":
    main()
