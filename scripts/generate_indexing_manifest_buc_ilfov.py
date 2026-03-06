import json
import os

LOCATIONS_PATH = r"C:\Users\ursac\Superparty\reports\locations\locations_100km.json"
MANIFEST_PATH = r"C:\Users\ursac\Superparty\reports\seo\indexing_manifest.json"
CANONICAL_HOST = "https://www.superparty.ro"

def main():
    print("Incepem generarea noului manifest de indexare...")
    with open(LOCATIONS_PATH, 'r', encoding='utf-8') as f:
        locations = json.load(f)

    manifest = []
    
    # 1. TIER 1 & TIER 2 HUB-URI
    hubs = [
        {"slug": "animatori-petreceri-copii", "tier": 1, "hub": None},
        {"slug": "bucuresti", "tier": 2, "hub": "animatori-petreceri-copii"},
        {"slug": "ilfov", "tier": 2, "hub": "animatori-petreceri-copii"},
        {"slug": "prahova", "tier": 2, "hub": "animatori-petreceri-copii"},
        {"slug": "dambovita", "tier": 2, "hub": "animatori-petreceri-copii"},
        {"slug": "giurgiu", "tier": 2, "hub": "animatori-petreceri-copii"},
        {"slug": "ialomita", "tier": 2, "hub": "animatori-petreceri-copii"},
        {"slug": "calarasi", "tier": 2, "hub": "animatori-petreceri-copii"},
        {"slug": "teleorman", "tier": 2, "hub": "animatori-petreceri-copii"},
        {"slug": "sector-1", "tier": 2, "hub": "bucuresti"},
        {"slug": "sector-2", "tier": 2, "hub": "bucuresti"},
        {"slug": "sector-3", "tier": 2, "hub": "bucuresti"},
        {"slug": "sector-4", "tier": 2, "hub": "bucuresti"},
        {"slug": "sector-5", "tier": 2, "hub": "bucuresti"},
        {"slug": "sector-6", "tier": 2, "hub": "bucuresti"},
    ]
    
    for h in hubs:
        h["indexable"] = True
        h["url"] = f"{CANONICAL_HOST}/{h['slug']}" if h["tier"] == 1 else f"{CANONICAL_HOST}/petreceri/{h['slug']}"
        manifest.append(h)

    # 2. TIER 3 LOCALITATI (Doar Ilfov, Orașe și Comune)
    target_count = 0
    target_slugs = set(h["slug"] for h in hubs)
    
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

    # 3. SET NON-TARGET (Existente) TO INDEXABLE: FALSE
    # Verificăm ce pagini există în `/petreceri/` și dacă nu sunt în target_slugs, le adăugăm ca ne-indexabile
    pages_dir = r"C:\Users\ursac\Superparty\src\pages\petreceri"
    non_target_count = 0
    if os.path.exists(pages_dir):
        for fname in os.listdir(pages_dir):
            if fname.endswith('.astro') and fname != '[slug].astro':
                slug = fname[:-6]
                if slug not in target_slugs:
                    entry = {
                        "slug": slug,
                        "url": f"{CANONICAL_HOST}/petreceri/{slug}",
                        "tier": 4, # Fallback
                        "indexable": False,
                        "note": "Scos din SEO core local"
                    }
                    manifest.append(entry)
                    non_target_count += 1

    # Trimming/Salvare
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Manifestul a fost salvat. Contine:")
    print(f" - {len(hubs)} Hub-uri (indexabile)")
    print(f" - {target_count} Localitati Ilfov Core (indexabile)")
    print(f" - {non_target_count} Pagini in src/pages marcate NoIndex/Neindexabile")

if __name__ == "__main__":
    main()
