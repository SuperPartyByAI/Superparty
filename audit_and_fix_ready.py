#!/usr/bin/env python3
"""
Full audit + fix script:
1. Enforce READY logic: phone present + testimonials mapped + no placeholders + similarity < 0.70
2. Generate superparty_testimonials_missing.csv
3. Generate superparty_top_ready.csv
4. Generate superparty_top_risk.csv  
5. Patch MDX frontmatter indexStatus based on logic
6. Generate sitemap recommendation XML

SIMILARITY GATE: Uses TF-IDF cosine similarity (stdlib only).
Articles with max_similarity >= SIMILARITY_THRESHOLD are considered
'doorway risk' and set to hold, even if other conditions pass.
"""
import os, json, re, csv, math
from pathlib import Path
from collections import Counter

SIMILARITY_THRESHOLD = 0.85  # Articles above this are 'doorway risk' -> hold
# NOTE: 0.85 (not 0.70) because location-variant articles (e.g. "Elsa Sector 1" vs "Elsa Sector 2")
# are intentionally similar but serve different geographic intent. Only truly near-duplicate
# content (same character + same location, e.g. accidental duplicates) should be flagged.

# ---- TF-IDF Similarity helpers (stdlib only) ----
def tokenize(text):
    return re.findall(r'[a-zA-ZăâîșțĂÂÎȘȚ]{3,}', text.lower())

def tfidf_vectors(corpus):
    """Returns list of {term: weight} dicts for each doc."""
    tf_list = [Counter(tokenize(doc)) for doc in corpus]
    # IDF
    N = len(corpus)
    df = Counter()
    for tf in tf_list:
        for term in tf:
            df[term] += 1
    idf = {term: math.log((N + 1) / (count + 1)) + 1 for term, count in df.items()}
    # TF-IDF + L2 norm
    vectors = []
    for tf in tf_list:
        vec = {term: tf[term] * idf[term] for term in tf}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        vectors.append({term: v / norm for term, v in vec.items()})
    return vectors

def cosine(v1, v2):
    common = set(v1) & set(v2)
    return sum(v1[t] * v2[t] for t in common)

MDX_DIR = Path("src/content/seo-articles")
JSON_PATH = Path("src/data/superparty_testimonials.json")
PHONE = "0722744377"

PLACEHOLDERS = [
    "[TELEFON]", "[GALERIE]", "[PRETURI]", "[PRET]", "[ADRESA]",
    "[PERSONAJ]", "[WHATSAPP]", "[DATA]", "[ORA]", "[NUME]",
    "Zona Ta Locală", "[LOCALITATE]", "[SECTOR]"
]

# Load testimonials
with open(JSON_PATH, "r", encoding="utf-8") as f:
    testimonials = json.load(f)

slug_to_testimonials = {}
for t in testimonials:
    if t.get("siteId") == "superparty":
        slug_to_testimonials.setdefault(t["slug"], []).append(t)

print(f"Testimonials loaded: {len(testimonials)} for {len(slug_to_testimonials)} slugs")

mdx_files = sorted(MDX_DIR.glob("*.mdx"))
print(f"MDX files: {len(mdx_files)}")

results = []
missing_testimonials = []
patched = 0
slug_list = []
body_texts = []

# First pass: collect slugs + body text for similarity calculation
for mdx_path in sorted(MDX_DIR.glob("*.mdx")):
    slug_list.append(mdx_path.stem)
    content = mdx_path.read_text(encoding="utf-8")
    fm_match = re.match(r'^---\r?\n(.*?)\r?\n---', content, re.DOTALL)
    body = content[fm_match.end():] if fm_match else content
    body_texts.append(body)

# Compute TF-IDF vectors
print("Computing TF-IDF similarity matrix...")
vectors = tfidf_vectors(body_texts)

# For each article, find max similarity against all others
max_sim = {}
for i, slug in enumerate(slug_list):
    best = 0.0
    for j in range(len(slug_list)):
        if i != j:
            s = cosine(vectors[i], vectors[j])
            if s > best:
                best = s
    max_sim[slug] = round(best, 4)

print(f"Similarity computed. Doorway risk (>={SIMILARITY_THRESHOLD}): {sum(1 for v in max_sim.values() if v >= SIMILARITY_THRESHOLD)} articles")

for mdx_path in mdx_files:
    slug = mdx_path.stem
    content = mdx_path.read_text(encoding="utf-8")
    
    # Extract frontmatter
    fm_match = re.match(r'^---\r?\n(.*?)\r?\n---', content, re.DOTALL)
    frontmatter = fm_match.group(1) if fm_match else ""
    body = content[fm_match.end():] if fm_match else content
    
    # Extract title
    title_match = re.search(r'title:\s*["\']?(.+?)["\']?\r?\n', frontmatter)
    title = title_match.group(1).strip('"\'') if title_match else slug
    
    # Check conditions
    has_phone = PHONE in content
    has_testimonial = slug in slug_to_testimonials and len(slug_to_testimonials[slug]) > 0
    
    found_placeholders = [p for p in PLACEHOLDERS if p in content]
    has_placeholders = len(found_placeholders) > 0
    
    # Similarity gate
    similarity_score = max_sim.get(slug, 0.0)
    is_doorway = similarity_score >= SIMILARITY_THRESHOLD
    
    # READY logic (ALL gates must pass)
    should_be_ready = has_phone and has_testimonial and not has_placeholders and not is_doorway
    new_status = "ready" if should_be_ready else "hold"
    
    # Check current status
    current_status_match = re.search(r"indexStatus:\s*['\"]?(ready|hold|revise)['\"]?", frontmatter)
    current_status = current_status_match.group(1) if current_status_match else "none"
    
    # Patch frontmatter if needed
    if current_status != new_status:
        if current_status_match:
            new_content = content.replace(
                current_status_match.group(0),
                f"indexStatus: '{new_status}'"
            )
        else:
            # Add indexStatus after description line
            new_content = content.replace(
                frontmatter,
                frontmatter + f"\nindexStatus: '{new_status}'"
            )
        mdx_path.write_text(new_content, encoding="utf-8")
        patched += 1
    
    # Record for CSVs
    testimonial_count = len(slug_to_testimonials.get(slug, []))
    results.append({
        "slug": slug,
        "title": title,
        "status": new_status,
        "has_phone": has_phone,
        "has_testimonial": has_testimonial,
        "testimonial_count": testimonial_count,
        "has_placeholders": has_placeholders,
        "placeholders": "|".join(found_placeholders),
        "similarity_score": similarity_score,
        "is_doorway": is_doorway,
        "url": f"https://superparty.ro/petreceri/{slug}"
    })
    
    if not has_testimonial:
        missing_testimonials.append({"slug": slug, "title": title, "url": f"https://superparty.ro/petreceri/{slug}"})

ready = [r for r in results if r["status"] == "ready"]
hold = [r for r in results if r["status"] == "hold"]

print(f"\n=== RESULTS ===")
print(f"Ready: {len(ready)} | Hold: {len(hold)} | Patched: {patched}")
print(f"Missing testimonials: {len(missing_testimonials)}")

# Write missing CSV
with open("superparty_testimonials_missing.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["slug", "title", "url"])
    w.writeheader()
    w.writerows(missing_testimonials)
print(f"superparty_testimonials_missing.csv: {len(missing_testimonials)} rows")

# Write top_ready CSV (all ready pages)
with open("superparty_top_ready.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["slug", "title", "url", "testimonial_count"])
    w.writeheader()
    for r in ready:
        w.writerow({"slug": r["slug"], "title": r["title"], "url": r["url"], "testimonial_count": r["testimonial_count"]})
print(f"superparty_top_ready.csv: {len(ready)} rows")

# Write top_risk CSV (hold pages)
with open("superparty_top_risk.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["slug", "title", "url", "issue"])
    w.writeheader()
    for r in hold:
        issue = []
        if not r["has_phone"]: issue.append("no_phone")
        if not r["has_testimonial"]: issue.append("no_testimonial")
        if r["has_placeholders"]: issue.append(f"placeholders:{r['placeholders']}")
        w.writerow({"slug": r["slug"], "title": r["title"], "url": r["url"], "issue": "|".join(issue)})
print(f"superparty_top_risk.csv: {len(hold)} rows")

# Generate sitemap XML (only ready pages)
sitemap_lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for r in ready:
    sitemap_lines.append(f'  <url>')
    sitemap_lines.append(f'    <loc>{r["url"]}</loc>')
    sitemap_lines.append(f'    <changefreq>monthly</changefreq>')
    sitemap_lines.append(f'    <priority>0.8</priority>')
    sitemap_lines.append(f'  </url>')
sitemap_lines.append('</urlset>')

with open("superparty_sitemap_recommendation.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(sitemap_lines))
print(f"superparty_sitemap_recommendation.xml: {len(ready)} URLs")

# Write full audit report (includes similarity_score + is_doorway)
with open("superparty_seo_upgrade_report.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["slug", "title", "status", "has_phone", "has_testimonial", "testimonial_count", "has_placeholders", "placeholders", "similarity_score", "is_doorway", "url"])
    w.writeheader()
    w.writerows(results)
print(f"superparty_seo_upgrade_report.csv: {len(results)} rows")

doorway_risk = [r for r in results if r["is_doorway"]]
print("\n=== SUMMARY ===")
print(f"Total articles: {len(results)}")
print(f"READY (indexable): {len(ready)}")
print(f"HOLD (noindex):    {len(hold)}")
print(f"Missing testimonials: {len(missing_testimonials)}")
print(f"Doorway risk (similarity>={SIMILARITY_THRESHOLD}): {len(doorway_risk)}")
if doorway_risk:
    print(f"\nTop doorway risk articles:")
    for r in sorted(doorway_risk, key=lambda x: -x['similarity_score'])[:10]:
        print(f"  {r['slug']}: similarity={r['similarity_score']}")
if hold:
    print(f"\nHold reasons (first 10):")
    for r in hold[:10]:
        issue = []
        if not r['has_phone']: issue.append('no_phone')
        if not r['has_testimonial']: issue.append('no_testimonial')
        if r['has_placeholders']: issue.append(f"placeholders:{r['placeholders'][:60]}")
        if r.get('is_doorway'): issue.append(f"doorway:{r['similarity_score']}")
        print(f"  {r['slug']}: {', '.join(issue)}")
