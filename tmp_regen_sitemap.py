"""
Regen sitemap.xml — www-only, doar URL-uri indexable din manifest + pagini pilon/servicii hardcodate.
"""
import json, re
from pathlib import Path
from datetime import date

BASE = "https://www.superparty.ro"
TODAY = str(date.today())

# ---- Static pages always in sitemap ----
STATIC_PAGES = [
    "/",
    "/animatori-petreceri-copii",
    "/arie-acoperire",
    "/petreceri/ilfov",
    "/petreceri/bucuresti",
    "/petreceri/sector-1",
    "/petreceri/sector-2",
    "/petreceri/sector-3",
    "/petreceri/sector-4",
    "/petreceri/sector-5",
    "/petreceri/sector-6",
]

# ---- Manifest indexable paths ----
manifest_path = Path("reports/seo/indexing_manifest.json")
manifest_paths = []
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest:
        if entry.get("indexable"):
            slug = entry.get("slug", "")
            path = entry.get("path") or (f"/petreceri/{slug}" if slug else None)
            if path:
                manifest_paths.append(path.rstrip("/"))

# Deduplicate
all_paths = list(dict.fromkeys(STATIC_PAGES + manifest_paths))

# ---- Write sitemap ----
lines = ['<?xml version="1.0" encoding="UTF-8"?>']
lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
for path in all_paths:
    url = f"{BASE}{path}"
    lines.append(f"  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>")
lines.append("</urlset>")

sitemap_text = "\n".join(lines) + "\n"
Path("public/sitemap.xml").write_text(sitemap_text, encoding="utf-8")

# Verify
non_www = re.findall(r'<loc>https://superparty\.ro[^<]*</loc>', sitemap_text)
total_urls = sitemap_text.count("<url>")
print(f"Sitemap regenerated: {total_urls} URLs, {len(non_www)} non-www (should be 0)")
print("Done!")
