#!/usr/bin/env python3
"""
seo_premerge_checks.py — pre-merge policy gate pentru Superparty SEO enterprise.

Rulare: python scripts/seo_premerge_checks.py
Esuaza cu exit-code 1 daca oricare gate este violat.
Destinat CI (GitHub Actions) sau pre-merge manual.

Checks:
  1. Non-www URL: niciun https://superparty.ro (fara www) in sitemap/seo files
  2. Village/hamlet/locality indexable:true in manifest (interzis)
  3. URL-uri noindex in sitemap
  4. Judete non-target in sitemap (Teleorman, Calarasi, Ialomita, Giurgiu, Dambovita, Prahova)
"""

import sys, json, re
from pathlib import Path

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
errors = []


def check(name, ok, detail=""):
    status = PASS if ok else FAIL
    print(f"  [{status}] {name}" + (f": {detail}" if detail else ""))
    if not ok:
        errors.append(f"{name}: {detail}")


# ─── 1. SITEMAP: www-only ───────────────────────────────────────────────────
print("\n[1] Sitemap — host www-only")
sitemap = Path("public/sitemap.xml")
if sitemap.exists():
    sm_text = sitemap.read_text(encoding="utf-8")
    non_www = re.findall(r'<loc>https://superparty\.ro[^<]*</loc>', sm_text)
    check("No non-www <loc> in sitemap", len(non_www) == 0,
          f"{len(non_www)} non-www URLs: {non_www[:3]}")
else:
    check("sitemap.xml exists", False, "public/sitemap.xml missing")


# ─── 2. MANIFEST: policy indexable=true ────────────────────────────────────
print("\n[2] Manifest — indexable policy")
manifest_path = Path("reports/seo/indexing_manifest.json")
FORBIDDEN_PLACE_TYPES = {"village", "hamlet", "locality"}
NON_TARGET_COUNTIES = {
    "teleorman", "calarasi", "ialomita", "giurgiu",
    "dambovita", "prahova", "arges", "constanta", "brasov",
}
TARGET_COUNTIES = {"ilfov", ""}  # empty = pilon/servicii

if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    bad_village_indexable = []
    bad_county_indexable = []

    for entry in manifest:
        if not entry.get("indexable"):
            continue
        ptype = entry.get("place_type", "").lower()
        county = entry.get("county", "").strip().lower()

        if ptype in FORBIDDEN_PLACE_TYPES:
            bad_village_indexable.append(f"{entry.get('slug')} ({ptype})")

        if county in NON_TARGET_COUNTIES:
            bad_county_indexable.append(f"{entry.get('slug')} (county={county})")

    check("No village/hamlet/locality indexable:true", len(bad_village_indexable) == 0,
          f"{bad_village_indexable[:5]}")
    check("No non-target counties indexable:true", len(bad_county_indexable) == 0,
          f"{bad_county_indexable[:5]}")
else:
    print("  [SKIP] reports/seo/indexing_manifest.json not found (OK in CI without report dir)")


# ─── 3. SITEMAP: no URL-uri noindex ────────────────────────────────────────
print("\n[3] Sitemap — no noindex URLs")
if sitemap.exists() and manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    noindex_paths = set()
    for entry in manifest:
        if not entry.get("indexable"):
            slug = entry.get("slug", "")
            path = entry.get("path") or f"/petreceri/{slug}"
            noindex_paths.add(path.rstrip("/"))

    bad_in_sitemap = []
    urls_in_sitemap = re.findall(r'<loc>(https://www\.superparty\.ro[^<]*)</loc>', sm_text)
    for url in urls_in_sitemap:
        path = url.replace("https://www.superparty.ro", "").rstrip("/") or "/"
        if path in noindex_paths:
            bad_in_sitemap.append(path)

    check("No noindex paths in sitemap", len(bad_in_sitemap) == 0,
          f"{bad_in_sitemap[:5]}")


# ─── 4. SITEMAP: no judete non-target ───────────────────────────────────────
print("\n[4] Sitemap — no non-target counties")
NON_TARGET_SLUGS = [
    "teleorman", "calarasi", "ialomita", "giurgiu", "dambovita", "prahova",
    "arges", "constanta", "brasov", "cluj", "timisoara", "iasi",
]
if sitemap.exists():
    bad_counties_in_sitemap = [s for s in NON_TARGET_SLUGS if f"/{s}" in sm_text or f"-{s}" in sm_text]
    check("No non-target counties in sitemap", len(bad_counties_in_sitemap) == 0,
          f"{bad_counties_in_sitemap}")


# ─── 5. CANONICAL: www-only in Astro layouts ────────────────────────────────
print("\n[5] Canonical host in Astro pages")
non_www_in_astro = []
for astro_file in Path("src").rglob("*.astro"):
    text = astro_file.read_text(encoding="utf-8", errors="ignore")
    if re.search(r'canonical.*https://superparty\.ro[^w]', text):
        non_www_in_astro.append(str(astro_file))
check("No non-www canonical in Astro pages", len(non_www_in_astro) == 0,
      f"{non_www_in_astro[:3]}")


# ─── FINAL REPORT ───────────────────────────────────────────────────────────
print()
if errors:
    print(f"PREMERGE FAILED — {len(errors)} check(s) failed:")
    for e in errors:
        print(f"  * {e}")
    sys.exit(1)
else:
    print("PREMERGE OK — all checks passed.")
    sys.exit(0)
