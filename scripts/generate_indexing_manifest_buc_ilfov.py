import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCATIONS_PATH = REPO_ROOT / "reports" / "locations" / "locations_100km.json"
MANIFEST_PATH = REPO_ROOT / "reports" / "seo" / "indexing_manifest.json"
PAGES_DIR = REPO_ROOT / "src" / "pages" / "petreceri"
CANONICAL_HOST = "https://www.superparty.ro"

def main():
    print("Incepem generarea noului manifest de indexare...")
    with open(LOCATIONS_PATH, 'r', encoding='utf-8') as f:
        locations = json.load(f)

    manifest = []
    
    # Doar București / Ilfov pentru Indexare Core! 
    # Județele extra se omit (sau se setează indexable: False) ca să nu mai apară în sitemap
    hubs = [
        {"slug": "animatori-petreceri-copii", "tier": 1, "hub": None, "indexable": True},
        {"slug": "bucuresti", "tier": 2, "hub": "animatori-petreceri-copii", "indexable": True},
        {"slug": "ilfov", "tier": 2, "hub": "animatori-petreceri-copii", "indexable": True},
        {"slug": "sector-1", "tier": 2, "hub": "bucuresti", "indexable": True},
        {"slug": "sector-2", "tier": 2, "hub": "bucuresti", "indexable": True},
        {"slug": "sector-3", "tier": 2, "hub": "bucuresti", "indexable": True},
        {"slug": "sector-4", "tier": 2, "hub": "bucuresti", "indexable": True},
        {"slug": "sector-5", "tier": 2, "hub": "bucuresti", "indexable": True},
        {"slug": "sector-6", "tier": 2, "hub": "bucuresti", "indexable": True},
        
        # Județele extra (au pagina fizică, dar momentan le marcăm indexable: False pentru Strict Scope)
        {"slug": "prahova", "tier": 2, "hub": "animatori-petreceri-copii", "indexable": False},
        {"slug": "dambovita", "tier": 2, "hub": "animatori-petreceri-copii", "indexable": False},
        {"slug": "giurgiu", "tier": 2, "hub": "animatori-petreceri-copii", "indexable": False},
        {"slug": "ialomita", "tier": 2, "hub": "animatori-petreceri-copii", "indexable": False},
        {"slug": "calarasi", "tier": 2, "hub": "animatori-petreceri-copii", "indexable": False},
        {"slug": "teleorman", "tier": 2, "hub": "animatori-petreceri-copii", "indexable": False},
    ]
    
    for h in hubs:
        h["url"] = f"{CANONICAL_HOST}/{h['slug']}" if h["tier"] == 1 else f"{CANONICAL_HOST}/petreceri/{h['slug']}"
        manifest.append(h)

    # TIER 3 LOCALITATI (Doar Ilfov, Orașe și Comune)
    target_count = 0
    target_slugs = set(h["slug"] for h in hubs if h["indexable"])
    
    for loc in locations:
        if loc.get("county") == "Ilfov" and loc.get("type") in ["town", "commune"]:
            slug = loc["slug"]
            if slug not in target_slugs:
                entry = {
                    "slug": slug,
                    "url": f"{CANONICAL_HOST}/petreceri/{slug}",
                    "tier": 3,
                    "indexable": True,
                    "county": "Ilfov",
                    "place_type": loc["type"],
                    "hub": "ilfov"
                }
                if "name" in loc:
                    entry["name"] = loc["name"]
                
                manifest.append(entry)
                target_slugs.add(slug)
                target_count += 1

    # SET NON-TARGET (Existente) TO INDEXABLE: FALSE
    non_target_count = 0
    if os.path.exists(PAGES_DIR):
        for fname in os.listdir(PAGES_DIR):
            if fname.endswith('.astro') and fname != '[slug].astro':
                slug = fname[:-6]
                # If it's not in the indexable list AND not already added in hubs:
                if slug not in target_slugs and not any(h['slug'] == slug for h in hubs):
                    entry = {
                        "slug": slug,
                        "url": f"{CANONICAL_HOST}/petreceri/{slug}",
                        "tier": 4, 
                        "indexable": False,
                        "note": "Scos din SEO core local"
                    }
                    manifest.append(entry)
                    non_target_count += 1

    # Salvare
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Manifestul a fost salvat.")
    print(f" - Hub-uri/Sectoare Indexabile: {len([h for h in hubs if h['indexable']])}")
    print(f" - Extra Județe NoIndex: {len([h for h in hubs if not h['indexable']])}")
    print(f" - Localitati Ilfov Core (indexabile): {target_count}")
    print(f" - Alte Sate/Localitati NoIndex: {non_target_count}")

if __name__ == "__main__":
    main()
