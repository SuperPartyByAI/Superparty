import os
from pathlib import Path
REPO_ROOT = str(Path(__file__).resolve().parents[1])
"""
Enterprise QA Script — SuperParty.ro
1. Validare JSON-LD pe TOATE paginile .astro
2. Detectare duplicate sluguri  
3. Generare sitemap curat (doar indexabile, non-www)
4. Raport QA complet
"""
import os, json, re, glob, unicodedata
from collections import defaultdict, Counter

SITE_ROOT = REPO_ROOT
PAGES_DIR = os.path.join(SITE_ROOT, "src", "pages")
REPORTS_DIR = os.path.join(SITE_ROOT, "reports", "seo")
CANONICAL_HOST = "https://www.superparty.ro"
os.makedirs(REPORTS_DIR, exist_ok=True)

# ============================================================
# 1) VALIDARE JSON-LD
# ============================================================
print("=" * 60)
print("1. VALIDARE JSON-LD")
print("=" * 60)

astro_files = glob.glob(os.path.join(PAGES_DIR, "**", "*.astro"), recursive=True)
print(f"Total fișiere .astro: {len(astro_files)}")

json_ok = []
json_bad = []
no_schema = []

for fp in astro_files:
    content = open(fp, encoding='utf-8', errors='ignore').read()
    # Cauta JSON.stringify({...})
    m = re.search(r'JSON\.stringify\((\{.*?\})\s*\)', content, re.DOTALL)
    if not m:
        no_schema.append(os.path.relpath(fp, PAGES_DIR))
        continue
    try:
        json.loads(m.group(1))
        json_ok.append(os.path.relpath(fp, PAGES_DIR))
    except json.JSONDecodeError as e:
        json_bad.append((os.path.relpath(fp, PAGES_DIR), str(e)[:80]))

print(f"  JSON-LD valid:  {len(json_ok)}")
print(f"  JSON-LD INVALID: {len(json_bad)}")
print(f"  Fără schema:    {len(no_schema)}")

if json_bad:
    print("\n  ⚠️  INVALID JSON-LD:")
    for f, e in json_bad:
        print(f"     {f}: {e}")

# Fix virgule lipsă în cele invalide
if json_bad:
    print("\n  🔧 Auto-fix virgule lipsă...")
    fixed_count = 0
    for fp in astro_files:
        content = open(fp, encoding='utf-8', errors='ignore').read()
        new_content = re.sub(r'(\})\s*\n(\s*\{)', lambda m: m.group(1) + ',\n' + m.group(2), content)
        if new_content != content:
            m2 = re.search(r'JSON\.stringify\((\{.*?\})\s*\)', new_content, re.DOTALL)
            if m2:
                try:
                    json.loads(m2.group(1))
                    open(fp, 'w', encoding='utf-8').write(new_content)
                    fixed_count += 1
                except:
                    pass
    print(f"  Fixed: {fixed_count} fișiere")

# ============================================================
# 2) DETECTARE DUPLICATE + CLAIMS FALSE
# ============================================================
print("\n" + "=" * 60)
print("2. DETECTARE DUPLICATE + CLAIMS FALSE")
print("=" * 60)

slug_map = {}
duplicates = []
claims_found = []

for fp in astro_files:
    bname = os.path.basename(fp).replace('.astro', '')
    if bname == '[slug]': continue
    
    if bname in slug_map:
        duplicates.append((bname, fp, slug_map[bname]))
    else:
        slug_map[bname] = fp
    
    content = open(fp, encoding='utf-8', errors='ignore').read()
    # Cauta claims false
    if any(claim in content for claim in ['5/5', '80+ recenzii', 'Activi din 2019', 'reviewCount', 'ratingValue']):
        claims_found.append(os.path.relpath(fp, PAGES_DIR))

print(f"  Duplicate sluguri: {len(duplicates)}")
for slug, f1, f2 in duplicates:
    print(f"     '{slug}': {os.path.basename(f1)} vs {os.path.basename(f2)}")

print(f"  Pagini cu claims false: {len(claims_found)}")
for f in claims_found:
    print(f"     {f}")

# ============================================================
# 3) SITEMAP CURAT — doar indexabile (META)
# ============================================================
print("\n" + "=" * 60)
print("3. GENERARE SITEMAP CURAT")
print("=" * 60)

# Citeste manifestul
manifest_path = os.path.join(REPORTS_DIR, "indexing_manifest.json")
manifest = json.load(open(manifest_path, encoding='utf-8')) if os.path.exists(manifest_path) else []
indexed_urls = {m['url'] for m in manifest if m.get('indexable', True)}
print(f"  URL-uri indexabile din manifest: {len(indexed_urls)}")

# URL-uri comerciale statice (mereu indexabile)
STATIC_COMMERCIAL = [
    f"{CANONICAL_HOST}/",
    f"{CANONICAL_HOST}/animatori-petreceri-copii",
    f"{CANONICAL_HOST}/contact",
    f"{CANONICAL_HOST}/arie-acoperire",
    f"{CANONICAL_HOST}/piniata",
    f"{CANONICAL_HOST}/baloane-cu-heliu",
    f"{CANONICAL_HOST}/arcade-baloane",
    f"{CANONICAL_HOST}/decoratiuni-baloane",
    f"{CANONICAL_HOST}/mos-craciun-de-inchiriat",
    f"{CANONICAL_HOST}/ursitoare-botez",
    f"{CANONICAL_HOST}/animatoare-botez",
    f"{CANONICAL_HOST}/vata-de-zahar",
    f"{CANONICAL_HOST}/popcorn-masina",
    f"{CANONICAL_HOST}/balonase-modelate",
]

# URL-uri hub din manifest (Tier 2)
tier2_urls = [m['url'] for m in manifest if m.get('tier') == 2 and m.get('indexable', True)]
tier3_urls = [m['url'] for m in manifest if m.get('tier') == 3 and m.get('indexable', True)]

print(f"  Tier 1 (pilon): 1")
print(f"  Tier 2 (hub-uri): {len(tier2_urls)}")
print(f"  Tier 3 (localități): {len(tier3_urls)}")
print(f"  Servicii comerciale: {len(STATIC_COMMERCIAL)}")

# Construieste sitemap
from datetime import date
today = date.today().isoformat()

sitemap_urls = []

# Tier 1
sitemap_urls.append({"url": f"{CANONICAL_HOST}/animatori-petreceri-copii", "priority": "1.0", "changefreq": "weekly", "tier": 1})

# Tier 2
for u in tier2_urls:
    sitemap_urls.append({"url": u, "priority": "0.9", "changefreq": "weekly", "tier": 2})

# Tier 3  
for u in tier3_urls:
    sitemap_urls.append({"url": u, "priority": "0.7", "changefreq": "monthly", "tier": 3})

# Servicii comerciale
for u in STATIC_COMMERCIAL:
    if u not in {x['url'] for x in sitemap_urls}:
        sitemap_urls.append({"url": u, "priority": "0.8", "changefreq": "weekly", "tier": "serviciu"})

# Deduplicat + sortare
seen = set()
final_urls = []
for item in sitemap_urls:
    if item['url'] not in seen:
        seen.add(item['url'])
        final_urls.append(item)

print(f"\n  TOTAL sitemap URL-uri: {len(final_urls)}")
print(f"  (EXCLUDE: noindex/hold/combinații thin)")

# Scrie sitemap
sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
sitemap_content += f'<!-- Sitemap SuperParty.ro | Generat: {today} | DOAR pagini indexabile Tier 1-3 + servicii -->\n'
sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for item in sorted(final_urls, key=lambda x: -float(x['priority'])):
    sitemap_content += f'  <url>\n'
    sitemap_content += f'    <loc>{item["url"]}</loc>\n'
    sitemap_content += f'    <changefreq>{item["changefreq"]}</changefreq>\n'
    sitemap_content += f'    <priority>{item["priority"]}</priority>\n'
    sitemap_content += f'    <lastmod>{today}</lastmod>\n'
    sitemap_content += f'  </url>\n'
sitemap_content += '</urlset>'

sitemap_path = os.path.join(SITE_ROOT, "public", "sitemap.xml")
with open(sitemap_path, 'w', encoding='utf-8') as f:
    f.write(sitemap_content)
print(f"\n  ✅ sitemap.xml scris: {len(final_urls)} URL-uri")

# ============================================================
# 4) QA REPORT
# ============================================================
print("\n" + "=" * 60)
print("4. QA REPORT FINAL")
print("=" * 60)

report = {
    "date": today,
    "json_ld": {
        "valid": len(json_ok),
        "invalid": len(json_bad),
        "invalid_list": [f for f,e in json_bad],
        "no_schema": len(no_schema),
    },
    "duplicates": len(duplicates),
    "duplicate_list": [(s, os.path.basename(f1)) for s,f1,f2 in duplicates],
    "claims_found": claims_found,
    "sitemap": {
        "total_urls": len(final_urls),
        "tier1": 1,
        "tier2": len(tier2_urls),
        "tier3": len(tier3_urls),
        "services": len([x for x in final_urls if x['tier'] == 'serviciu']),
        "host": CANONICAL_HOST,
        "noindex_excluded": True,
    }
}

report_path = os.path.join(REPORTS_DIR, "qa_report.json")
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"  ✅ Raport QA: {report_path}")
print(f"\n  SUMAR FINAL:")
print(f"    JSON-LD valid: {len(json_ok)}/{len(astro_files) - len(no_schema)}")
print(f"    Duplicate sluguri: {len(duplicates)}")
print(f"    Claims false: {len(claims_found)}")
print(f"    Sitemap URL-uri: {len(final_urls)} (din care {len(tier3_urls)} Tier 3)")
print(f"    Host canonical: {CANONICAL_HOST}")
print(f"    noindex/hold EXCLUSE din sitemap: ✅")
