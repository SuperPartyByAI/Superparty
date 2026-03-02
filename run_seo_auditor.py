import os
import re
import json
import csv
import math
from collections import Counter
import datetime
import shutil

INPUT_DIR = "src/content/seo-articles"
OUTPUT_DIR = "seo_audit_results"

def parse_mdx(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter = {}
    body = content
    
    # Parse yaml frontmatter
    fm_match = re.match(r'^---\s*(.*?)\s*---', content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        body = content[fm_match.end():]
        
        for line in fm_text.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                frontmatter[key] = val
                
    return frontmatter, body

def calculate_tf_idf_similarity(docs_dict):
    doc_freq = Counter()
    doc_tfs = {}
    
    for filename, text in docs_dict.items():
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        tf = Counter(words)
        doc_tfs[filename] = tf
        for word in tf.keys():
            doc_freq[word] += 1
            
    num_docs = len(docs_dict)
    
    doc_vectors = {}
    doc_norms = {}
    for filename, tf in doc_tfs.items():
        vector = {}
        norm_sq = 0
        for word, count in tf.items():
            idf = math.log((num_docs + 1) / (1 + doc_freq[word])) + 1
            val = count * idf
            vector[word] = val
            norm_sq += val * val
        doc_vectors[filename] = vector
        doc_norms[filename] = math.sqrt(norm_sq)
        
    return doc_vectors, doc_norms

def get_cosine_sim(vec1, norm1, vec2, norm2):
    if norm1 == 0 or norm2 == 0: return 0
    if len(vec1) > len(vec2): vec1, vec2 = vec2, vec1
    dot = sum(val * vec2.get(word, 0) for word, val in vec1.items())
    return dot / (norm1 * norm2)

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    fixes_dir = os.path.join(OUTPUT_DIR, "fixes_patch")
    schema_dir = os.path.join(OUTPUT_DIR, "suggested_schema")
    os.makedirs(fixes_dir, exist_ok=True)
    os.makedirs(schema_dir, exist_ok=True)

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.mdx')]
    
    # Read all docs
    docs_text = {}
    parsed_docs = {}
    for f in files:
        fm, body = parse_mdx(os.path.join(INPUT_DIR, f))
        docs_text[f] = body
        parsed_docs[f] = {"frontmatter": fm, "body": body}
        
    print("Calculating similarities for", len(files), "docs...")
    doc_vecs, doc_norms = calculate_tf_idf_similarity(docs_text)
    
    # Calculate top similarities
    similarities = {}
    for i, f1 in enumerate(files):
        sims = []
        for j, f2 in enumerate(files):
            if i == j: continue
            sim = get_cosine_sim(doc_vecs[f1], doc_norms[f1], doc_vecs[f2], doc_norms[f2])
            sims.append({"filename": f2, "similarity": round(sim, 3)})
        sims.sort(key=lambda x: x["similarity"], reverse=True)
        similarities[f1] = sims[:5]

    reports = []
    
    for f in files:
        fm = parsed_docs[f]["frontmatter"]
        body = parsed_docs[f]["body"]
        
        slug = f.replace('.mdx', '')
        url = f"https://superparty.ro/petreceri/{slug}"
        word_count = len(re.findall(r'\b\w+\b', body))
        
        # Frontmatter checks
        req_fields = ["title", "description"]
        missing = [k for k in req_fields if k not in fm]
        
        title = fm.get("title", "")
        desc = fm.get("description", "")
        h1_present = title != "" # Our MDX uses frontmatter title as H1 in Layout
        
        # Content checks
        sentences = re.split(r'[.!?]+', body)
        avg_sentence_len = word_count / max(1, len(sentences))
        readability = max(0, min(100, 100 - (avg_sentence_len - 10) * 2)) # Simple proxy
        
        h2_count = len(re.findall(r'^##\s', body, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s', body, re.MULTILINE))
        
        cta_present = bool(re.search(r'(0700\s?000\s?000|Rezerv|contact|sun)', body, re.IGNORECASE))
        faq_present = bool(re.search(r'(frecvente|întrebări|\?.*?R:|\?.*?\n\s*-)', body, re.IGNORECASE))
        
        # SEO
        title_ok = "animatori" in title.lower() or "petreceri" in title.lower()
        meta_ok = 140 <= len(desc) <= 160
        
        # Similarity
        top_sims = similarities[f]
        max_sim = top_sims[0]["similarity"] if top_sims else 0
        doorway_risk = "high" if max_sim >= 0.85 else ("medium" if max_sim >= 0.60 else "low")
        
        # Scoring
        score_uniqueness = 25 * (1 - max_sim) # if max_sim=1 -> 0, if max_sim=0.5 -> 12.5
        score_uniqueness = max(0, min(25, score_uniqueness + 5)) # Boost slightly
        
        score_local = 20 if re.search(r'(sector|ilfov|comuna|oras|bucuresti)', f.lower()) else 10
        score_meta = 15 if (h1_present and meta_ok and title_ok) else (5 if title else 0)
        score_tech = 15 if not missing else 0
        score_read = 15 * (readability/100)
        score_struct = 0 # No JSON-LD yet
        
        overall = round((score_uniqueness + score_local + score_meta + score_tech + score_read + score_struct) / 10, 1)
        
        actions = []
        if max_sim >= 0.85: actions.append(f"Rescrie sau diferentiaza continutul (similaritate {max_sim} cu {top_sims[0]['filename']})")
        if word_count < 2000: actions.append("Extinde numarul de cuvinte la minim 2000.")
        if not meta_ok: actions.append(f"Ajusteaza lungimea meta description ({len(desc)} char).")
        if not cta_present: actions.append("Adauga Call To Action vizibil in text.")
        actions.append("Adauga schema.org JSON-LD.")

        # JSON-LD Generation
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "LocalBusiness",
                    "name": "SuperParty",
                    "telephone": "+40700000000",
                    "address": { "@type": "PostalAddress", "addressLocality": "București/Ilfov", "addressRegion": "București" },
                    "url": url
                },
                {
                    "@type": "Article",
                    "headline": title,
                    "description": desc,
                    "datePublished": "2026-03-01",
                    "author": { "@type": "Organization", "name": "SuperParty" }
                }
            ]
        }
        
        with open(os.path.join(schema_dir, f"{slug}.json"), 'w', encoding='utf-8') as sf:
            json.dump(schema, sf, indent=2, ensure_ascii=False)

        reports.append({
            "filename": f,
            "slug": slug,
            "url": url,
            "word_count": word_count,
            "frontmatter_missing": missing,
            "h1_present": h1_present,
            "title_length": len(title),
            "meta_length": len(desc),
            "readability_score": round(readability),
            "headings_count": {"h2": h2_count, "h3": h3_count},
            "images_count": 0,
            "faq_present": faq_present,
            "internal_links_count": len(re.findall(r'\[.*?\]\(.*?\)', body)),
            "cta_present": cta_present,
            "structured_data_present": False,
            "top_similar_docs": top_sims,
            "uniqueness_score": round(1 - max_sim, 2),
            "doorway_risk": doorway_risk,
            "title_ok": title_ok,
            "meta_ok": meta_ok,
            "schema_recommendation": "Check suggested_schema folder",
            "overall_score": overall,
            "suggested_actions": actions
        })
        
    # Generate report arrays
    with open(os.path.join(OUTPUT_DIR, "articles_report.json"), "w", encoding='utf-8') as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)
        
    ready = [r for r in reports if r["overall_score"] >= 8.0]
    risk = [r for r in reports if r["doorway_risk"] == "high" or r["overall_score"] <= 4.0]
    
    # Save CSVs
    with open(os.path.join(OUTPUT_DIR, "top_ready.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "url", "score", "suggested_actions"])
        for r in sorted(ready, key=lambda x: x["overall_score"], reverse=True)[:50]:
            writer.writerow([r["filename"], r["url"], r["overall_score"], " | ".join(r["suggested_actions"])])

    with open(os.path.join(OUTPUT_DIR, "top_risk.csv"), "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "url", "score", "doorway_risk", "suggested_actions"])
        for r in sorted(risk, key=lambda x: x["overall_score"])[:50]:
            writer.writerow([r["filename"], r["url"], r["overall_score"], r["doorway_risk"], " | ".join(r["suggested_actions"])])
            
    # Sitemap
    with open(os.path.join(OUTPUT_DIR, "sitemap_recommendation.xml"), "w", encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for r in reports:
            priority = 0.8 if r["overall_score"] >= 8 else (0.6 if r["overall_score"] >= 6 else 0.4)
            f.write(f'  <url>\n    <loc>{r["url"]}</loc>\n    <lastmod>2026-03-01</lastmod>\n    <priority>{priority}</priority>\n  </url>\n')
        f.write('</urlset>')
        
    # Robots
    with open(os.path.join(OUTPUT_DIR, "robots_recommendation.txt"), "w", encoding='utf-8') as f:
        f.write("User-agent: *\nDisallow:\nSitemap: https://superparty.ro/sitemap.xml\n")
        
    # Action plan
    with open(os.path.join(OUTPUT_DIR, "action_plan.md"), "w", encoding='utf-8') as f:
        f.write("# Superparty SEO Action Plan\n\n")
        f.write(f"- Total Articles: {len(reports)}\n")
        f.write(f"- Ready for Index (Score >=8): {len(ready)}\n")
        f.write(f"- High Risk / Duplicate: {len(risk)}\n\n")
        f.write("## Top 3 Imediat Actions\n")
        f.write("1. Integrare JS plugin `@astrojs/sitemap` pentru sitemap.xml real-time.\n")
        f.write("2. Injectare JSON-LD in `[slug].astro` a fisierelor incluse.\n")
        f.write("3. Review la fisierele semnalate pe top_risk.csv ca avand similaritate mare (>80%).\n")
        
    # Summary
    summary = {
        "total_articles": len(reports),
        "average_score": round(sum(r["overall_score"] for r in reports) / len(reports), 2),
        "average_word_count": sum(r["word_count"] for r in reports) // len(reports),
        "ready_pages": len(ready),
        "risk_pages": len(risk)
    }
    with open(os.path.join(OUTPUT_DIR, "report_summary.json"), "w", encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print("Writing astro components hint...")
    with open(os.path.join(OUTPUT_DIR, "astro_integration_snippet.md"), "w", encoding='utf-8') as f:
        f.write("```javascript\n")
        f.write("// In [slug].astro:\n")
        f.write("<head>\n")
        f.write("  <script type=\"application/ld+json\" set:html={JSON.stringify({\n")
        f.write("    \"@context\": \"https://schema.org\",\n")
        f.write("    \"@type\": \"Article\",\n")
        f.write("    \"headline\": title,\n")
        f.write("    \"description\": description\n")
        f.write("  })} />\n")
        f.write("</head>\n")
        f.write("```\n")
        
if __name__ == "__main__":
    main()
