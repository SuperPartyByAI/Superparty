"""
fix_manifest_ilfov_strict.py — Whitelist STRICT de comune/orase Ilfov.
Orice localitate care NU e in ILFOV_COMMUNES va fi indexable:false.
"""
import json
from pathlib import Path

MANIFEST = Path("reports/seo/indexing_manifest.json")

# Whitelist STRICT: comune/orase/municipii reale din judetul Ilfov
# Sursa: https://ro.wikipedia.org/wiki/Jude%C8%9Bul_Ilfov
ILFOV_COMMUNES = {
    # municipii/orase
    "voluntari","pantelimon","popesti-leordeni","buftea","bragadiru","magurele",
    "otopeni","chitila","dudu","bolintin","stefanestii-de-jos",
    # comune Ilfov
    "afumati","1-decembrie","balotesti","branesti","ciorogarla","clinceni",
    "coridoarele","corbeanca","copaceni","cornetu","cozieni","dascalu",
    "dimieni","dobroesti","dragomiresti-vale","fundeni","glina","gradistea",
    "gruiu","ilfov","jilava","mogosoaia","moara-vlasiei","nuci","petrachioaia",
    "peris","tunari","targsoru-vechi","vidra","dragomiresti-de-vale",
    "chiajna","cernica","caldararu",
    # asiguram ca ilfov hub e mereu inclus
    "ilfov",
}

# Slugs speciale mereu indexabile
ALWAYS_INDEXABLE = {
    "ilfov", "bucuresti",
    "sector-1","sector-2","sector-3","sector-4","sector-5","sector-6",
}
ALWAYS_INDEXABLE_PATHS = {
    "/animatori-petreceri-copii",
    "/petreceri/ilfov", "/petreceri/bucuresti",
    "/petreceri/sector-1", "/petreceri/sector-2", "/petreceri/sector-3",
    "/petreceri/sector-4", "/petreceri/sector-5", "/petreceri/sector-6",
}

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
changed = 0

for entry in manifest:
    if not entry.get("indexable"):
        continue

    slug = entry.get("slug", "").lower().strip()
    path = entry.get("path", "")

    # Keep always-indexable
    if path in ALWAYS_INDEXABLE_PATHS or slug in ALWAYS_INDEXABLE:
        continue

    # For local pages: must be in ILFOV_COMMUNES whitelist
    if slug and slug not in ILFOV_COMMUNES:
        entry["indexable"] = False
        changed += 1

MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

total = len(manifest)
indexable_count = sum(1 for e in manifest if e.get("indexable"))
print(f"Changed {changed} additional entries to indexable:false")
print(f"Total: {total} | indexable: {indexable_count} | noindex: {total - indexable_count}")
print("\nFinal indexable list:")
for e in manifest:
    if e.get("indexable"):
        print(f"  {e.get('slug','?')} | path={e.get('path','')} | county={e.get('county','')} | type={e.get('place_type','')}")
