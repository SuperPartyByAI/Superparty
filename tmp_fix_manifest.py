import json
from pathlib import Path

manifest_path = Path("reports/seo/indexing_manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

NON_TARGET_COUNTIES = {
    "teleorman","calarasi","ialomita","giurgiu","dambovita","prahova",
    "arges","constanta","brasov","cluj","timis","iasi","bacau",
    "neamt","suceava","galati","valcea","olt","dolj","mehedinti",
}
FORBIDDEN_PLACE_TYPES = {"village", "hamlet", "locality"}

changed = 0
for entry in manifest:
    county = entry.get("county","").strip().lower()
    ptype = entry.get("place_type","").lower()
    if ptype in FORBIDDEN_PLACE_TYPES and entry.get("indexable"):
        entry["indexable"] = False
        changed += 1
    elif county in NON_TARGET_COUNTIES and entry.get("indexable"):
        entry["indexable"] = False
        changed += 1

manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Changed {changed} entries to indexable:false")

total = len(manifest)
indexable = sum(1 for e in manifest if e.get("indexable"))
print(f"Total: {total}, indexable: {indexable}, noindex: {total-indexable}")
for e in manifest:
    if e.get("indexable"):
        print(f"  OK indexable: {e.get('slug')} | county={e.get('county','')} | type={e.get('place_type','')}")
