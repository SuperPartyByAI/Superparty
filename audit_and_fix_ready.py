#!/usr/bin/env python3
"""
Full audit + fix script:
1. Enforce READY logic: phone present + testimonials mapped + no placeholders
2. Generate superparty_testimonials_missing.csv
3. Generate superparty_top_ready.csv
4. Generate superparty_top_risk.csv  
5. Patch MDX frontmatter indexStatus based on logic
6. Generate sitemap recommendation XML
"""
import os, json, re, csv
from pathlib import Path

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
    
    # READY logic
    should_be_ready = has_phone and has_testimonial and not has_placeholders
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

# Write full audit report
with open("superparty_seo_upgrade_report.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["slug", "title", "status", "has_phone", "has_testimonial", "testimonial_count", "has_placeholders", "placeholders", "url"])
    w.writeheader()
    w.writerows(results)
print(f"superparty_seo_upgrade_report.csv: {len(results)} rows")

print("\n=== SUMMARY ===")
print(f"Total articles: {len(results)}")
print(f"READY (indexable): {len(ready)}")
print(f"HOLD (noindex):    {len(hold)}")
print(f"Missing testimonials: {len(missing_testimonials)}")
if hold:
    print(f"\nHold reasons (first 10):")
    for r in hold[:10]:
        issue = []
        if not r['has_phone']: issue.append('no_phone')
        if not r['has_testimonial']: issue.append('no_testimonial')
        if r['has_placeholders']: issue.append(f"placeholders:{r['placeholders'][:60]}")
        print(f"  {r['slug']}: {', '.join(issue)}")
