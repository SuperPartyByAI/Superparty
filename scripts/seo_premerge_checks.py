#!/usr/bin/env python3
"""
seo_premerge_checks.py — pre-merge policy gate pentru Superparty SEO enterprise.

Rulare: python scripts/seo_premerge_checks.py
Esuaza cu exit-code 1 daca oricare gate este violat.
Destinat CI (GitHub Actions) sau pre-merge manual.

Checks:
  1. Non-www URL: niciun https://superparty.ro (fara www) in sitemap
  2a. Village/hamlet/locality indexable:true in manifest (interzis)
  2b. Non-target counties indexable:true in manifest (Teleorman etc)
  2c. Town/commune/city indexable:true dar slug NOT in ILFOV_COMMUNES whitelist
  3. URL-uri noindex in sitemap
  4. Judete non-target in sitemap slugs
  5. Canonical non-www in Astro pages
"""

import sys, json, re
from pathlib import Path

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
errors = []

# Whitelist strict de comune/orase din judetul Ilfov (UAT Ilfov oficial)
ILFOV_COMMUNES = {
    "voluntari","pantelimon","popesti-leordeni","buftea","bragadiru","magurele",
    "otopeni","chitila","dudu","stefanestii-de-jos",
    "afumati","1-decembrie","balotesti","branesti","ciorogarla","clinceni",
    "corbeanca","copaceni","cornetu","dascalu","dimieni","dobroesti",
    "dragomiresti-vale","fundeni","glina","gradistea","gruiu",
    "jilava","mogosoaia","moara-vlasiei","nuci","petrachioaia","peris",
    "tunari","vidra","chiajna","cernica","caldararu","ilfov",
}
ALWAYS_OK_SLUGS = {
    "ilfov","bucuresti",
    "sector-1","sector-2","sector-3","sector-4","sector-5","sector-6",
}
FORBIDDEN_PLACE_TYPES = {"village", "hamlet", "locality"}
NON_TARGET_COUNTIES = {
    "teleorman","calarasi","ialomita","giurgiu","dambovita","prahova",
    "arges","constanta","brasov","cluj","timis","iasi",
}
NON_TARGET_SLUGS = [
    "teleorman","calarasi","ialomita","giurgiu","dambovita","prahova",
    "arges","constanta","brasov","cluj","timisoara","iasi",
    "bolintin-vale","fundulea","racari","mihailesti","budesti","mihai-voda",
]


def check(name, ok, detail=""):
    status = PASS if ok else FAIL
    print(f"  [{status}] {name}" + (f": {detail}" if detail else ""))
    if not ok:
        errors.append(f"{name}: {detail}")


# ─── 1. SITEMAP: www-only ───────────────────────────────────────────────────
print("\n[1] Sitemap — host www-only")
sitemap = Path("public/sitemap.xml")
sm_text = ""
if sitemap.exists():
    sm_text = sitemap.read_text(encoding="utf-8")
    non_www = re.findall(r'<loc>https://superparty\.ro[^<]*</loc>', sm_text)
    check("No non-www <loc> in sitemap", len(non_www) == 0,
          f"{len(non_www)} non-www URLs: {non_www[:3]}")
else:
    check("sitemap.xml exists", False, "public/sitemap.xml missing")


# ─── 2. MANIFEST: policy indexable=true ────────────────────────────────────
print("\n[2] Manifest — indexable policy (Buc/Ilfov strict)")
manifest_path = Path("reports/seo/indexing_manifest.json")

if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    bad_village = []
    bad_county = []
    bad_non_ilfov_town = []

    for entry in manifest:
        if not entry.get("indexable"):
            continue
        slug = entry.get("slug", "").lower().strip()
        ptype = entry.get("place_type", "").lower()
        county = entry.get("county", "").strip().lower()

        if slug in ALWAYS_OK_SLUGS:
            continue

        if ptype in FORBIDDEN_PLACE_TYPES:
            bad_village.append(f"{entry.get('slug')} ({ptype})")

        if county in NON_TARGET_COUNTIES:
            bad_county.append(f"{entry.get('slug')} (county={county})")

        # Non-Ilfov town: are place_type town/commune/city dar slug nu e in whitelist
        if ptype in {"town", "commune", "city", "municipality"} and slug not in ILFOV_COMMUNES:
            bad_non_ilfov_town.append(f"{entry.get('slug')} (type={ptype}, county={county!r})")

    check("No village/hamlet/locality indexable:true", len(bad_village) == 0,
          f"{bad_village[:5]}")
    check("No non-target counties indexable:true", len(bad_county) == 0,
          f"{bad_county[:5]}")
    check("No non-Ilfov town/commune/city indexable:true", len(bad_non_ilfov_town) == 0,
          f"{bad_non_ilfov_town[:5]}")
else:
    print("  [SKIP] reports/seo/indexing_manifest.json not found")


# ─── 3. SITEMAP: no URL-uri noindex ────────────────────────────────────────
print("\n[3] Sitemap — no noindex URLs")
if sm_text and manifest_path.exists():
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


# ─── 4. SITEMAP: no judete/sluguri non-target ────────────────────────────────
print("\n[4] Sitemap — no non-target county slugs")
if sm_text:
    found = [s for s in NON_TARGET_SLUGS if f"/{s}" in sm_text]
    check("No non-target slugs in sitemap", len(found) == 0, f"{found}")


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
