#!/usr/bin/env python3
"""
Fix all remaining placeholder strings in MDX files.
Replaces [PERSONAJ], [WHATSAPP], Zona Ta Locală, [LOCALITATE], etc.
based on the slug of each file.
"""
import os, re
from pathlib import Path

MDX_DIR = Path("src/content/seo-articles")
PHONE = "0722744377"

# City detection from slug
CITY_MAP = {
    "sector-1": "Sector 1", "sector-2": "Sector 2", "sector-3": "Sector 3",
    "sector-4": "Sector 4", "sector-5": "Sector 5", "sector-6": "Sector 6",
    "ilfov": "Ilfov", "bucuresti": "București", "magurele": "Măgurele",
    "otopeni": "Otopeni", "popesti": "Popești-Leordeni", "voluntari": "Voluntari",
    "bragadiru": "Bragadiru", "pantelimon": "Pantelimon", "chitila": "Chitila",
    "berceni": "Berceni", "branesti": "Brănești", "1-decembrie": "1 Decembrie",
    "cernica": "Cernica", "chiajna": "Chiajna", "ciorogarla": "Ciorogârla",
    "clinceni": "Clinceni", "corbeanca": "Corbeanca", "cornetu": "Cornetu",
    "dobroiesti": "Dobroiești", "domnesti": "Domnești", "dragomiresti": "Dragomirești",
    "glina": "Glina", "jilava": "Jilava", "moara-vlasiei": "Moara Vlăsiei",
    "mogosoaia": "Mogoșoaia", "snagov": "Snagov", "stefanestii-de-jos": "Ștefăneștii de Jos",
    "tunari": "Tunari", "vidra": "Vidra", "grozavesti": "Grозăvești",
    "colentina": "Colentina", "floreasca": "Floreasca", "herastrau": "Herăstrău",
    "titan": "Titan", "drumul-taberei": "Drumul Taberei", "militari": "Militari",
}

def get_location_from_slug(slug):
    for city_key, city_name in CITY_MAP.items():
        if city_key in slug:
            return city_name
    if "bucuresti" in slug:
        return "București"
    return "București"

def get_character_from_slug(slug):
    """Extract character/service name from slug."""
    # Remove common prefixes
    name = slug
    for prefix in ["animator-", "animatori-petreceri-copii-", "animatori-petreceri-", "petreceri-copii-"]:
        name = name.replace(prefix, "")
    # Remove location suffixes
    for city_key in CITY_MAP:
        name = name.replace(f"-{city_key}", "").replace(city_key + "-", "")
    name = name.replace("-bucuresti", "").replace("-ilfov", "")
    name = name.replace("-", " ").title()
    return name if name.strip() else "Animatorul Superparty"

fixed_count = 0
already_clean = 0

mdx_files = sorted(MDX_DIR.glob("*.mdx"))
print(f"Processing {len(mdx_files)} MDX files...")

for mdx_path in mdx_files:
    slug = mdx_path.stem
    content = mdx_path.read_text(encoding="utf-8")
    
    location = get_location_from_slug(slug)
    character = get_character_from_slug(slug)
    
    original = content
    
    # Replace all placeholder variants
    content = content.replace("[PERSONAJ]", character)
    content = content.replace("[WHATSAPP]", PHONE)
    content = content.replace("[TELEFON]", PHONE)
    content = content.replace("[GALERIE]", "galeria noastră de evenimente")
    content = content.replace("[PACHETE]", "pagina de Oferte")
    content = content.replace("[PRETURI]", "prețuri accesibile")
    content = content.replace("[PRET]", "prețuri accesibile")
    content = content.replace("[ADRESA]", "zona " + location)
    content = content.replace("[DATA]", "data petrecerii")
    content = content.replace("[ORA]", "ora stabilită")
    content = content.replace("[LOCALITATE]", location)
    content = content.replace("[SECTOR]", location)
    content = content.replace("Zona Ta Locală", location)
    content = content.replace("zona ta locală", location.lower())
    content = content.replace("[LOCATIE]", location)
    
    if content != original:
        mdx_path.write_text(content, encoding="utf-8")
        fixed_count += 1
    else:
        already_clean += 1

print(f"Fixed: {fixed_count} files | Already clean: {already_clean} files")
print("Done! Run audit_and_fix_ready.py again to recount ready/hold.")
