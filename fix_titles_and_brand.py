#!/usr/bin/env python3
"""
Fix remaining SEO issues:
1. Generate unique title+description per slug based on character+location extracted from slug
2. Remove any Animatopia brand leaks in non-Animatopia slugs
3. Re-run audit to confirm all 500 still READY after fixes
"""
import os, re
from pathlib import Path

MDX_DIR = Path("src/content/seo-articles")

# --- Location/Character extraction helpers ---
CITY_LABELS = {
    "sector-1": "Sector 1 București", "sector-2": "Sector 2 București",
    "sector-3": "Sector 3 București", "sector-4": "Sector 4 București",
    "sector-5": "Sector 5 București", "sector-6": "Sector 6 București",
    "ilfov": "Ilfov", "bucuresti": "București", "magurele": "Măgurele",
    "otopeni": "Otopeni", "popesti-leordeni": "Popești-Leordeni",
    "popesti": "Popești-Leordeni", "voluntari": "Voluntari",
    "bragadiru": "Bragadiru", "pantelimon": "Pantelimon",
    "chitila": "Chitila", "berceni": "Berceni", "branesti": "Brănești",
    "1-decembrie": "1 Decembrie", "cernica": "Cernica",
    "chiajna": "Chiajna", "ciorogarla": "Ciorogârla",
    "clinceni": "Clinceni", "corbeanca": "Corbeanca",
    "cornetu": "Cornetu", "dobroiesti": "Dobroiești",
    "domnesti": "Domnești", "dragomiresti": "Dragomirești",
    "glina": "Glina", "jilava": "Jilava",
    "moara-vlasiei": "Moara Vlăsiei", "mogosoaia": "Mogoșoaia",
    "snagov": "Snagov", "stefanestii-de-jos": "Ștefăneștii de Jos",
    "tunari": "Tunari", "vidra": "Vidra",
    "colentina": "Colentina", "floreasca": "Floreasca",
    "titan": "Titan", "drumul-taberei": "Drumul Taberei",
    "militari": "Militari", "alba-ca-zapada": "pe tema Albă ca Zăpada",
    "cluj-napoca": "Cluj-Napoca",
}

SERVICE_OVERRIDES = {
    "animatori-petreceri-botez": ("Animatori Petrecere Botez", "botez"),
    "animatori-petreceri-copii": ("Animatori Petreceri Copii", "petrecere"),
    "petreceri-tema": ("Petreceri cu Temă", "petrecere"),
    "petrecere-craciun": ("Petrecere Crăciun Copii", "petrecere"),
    "mos-craciun": ("Moș Crăciun la Domiciliu", "eveniment"),
}

CHARACTER_MAP = {
    "elsa": "Elsa Frozen", "frozen": "Elsa & Anna Frozen",
    "anna": "Anna Frozen", "ladybug": "Ladybug Miraculous",
    "peppa-pig": "Peppa Pig", "peppa": "Peppa Pig",
    "spiderman": "Spiderman", "spider-man": "Spiderman",
    "batman": "Batman", "superman": "Superman",
    "hulk": "Hulk Avengers", "avengers": "Avengers",
    "minnie": "Minnie Mouse", "mickey": "Mickey Mouse",
    "moana": "Moana Disney", "ariel": "Ariel Mica Sirenă",
    "rapunzel": "Rapunzel", "belle": "Belle Disney",
    "jasmine": "Jasmine Aladdin", "aladin": "Prințul Aladdin",
    "merida": "Merida Brave", "mulan": "Mulan Disney",
    "cenusareasa": "Cenușăreasa Disney", "aurora": "Aurora Frumoasa Adormită",
    "stitch": "Stitch Disney", "minion": "Minion",
    "mario": "Mario Bros", "luigi": "Luigi Bros",
    "pikachu": "Pikachu Pokemon", "pokemon": "Pokemon",
    "Cars": "Lightning McQueen Cars",
    "lightning-mcqueen": "Lightning McQueen Cars",
    "pj-masks": "PJ Masks", "catboy": "Catboy PJ Masks",
    "gekko": "Gekko PJ Masks", "owlette": "Owlette PJ Masks",
    "spongebob": "SpongeBob", "winx": "Winx Club",
    "rainbow-dash": "Rainbow Dash My Little Pony",
    "my-little-pony": "My Little Pony", "masha": "Masha și Ursul",
    "george-pig": "George Pig", "peter-pan": "Peter Pan",
    "woody": "Woody Toy Story", "buzz-lightyear": "Buzz Lightyear",
    "toy-story": "Toy Story", "bumblebee": "Bumblebee Transformers",
    "transformers": "Transformers", "hello-kitty": "Hello Kitty",
    "donald-duck": "Donald Duck Disney", "pantera-roz": "Pantera Roz",
    "princess-peach": "Princess Peach Mario",
    "dragon": "Dragon Mascotă", "pirat": "Pirat Aventurier",
    "supererou": "Supererou", "ghidul": "Ghidul Petrecerilor",
    "albastru": "Personaj Albastru", "1-decembrie": "Albă ca Zăpada",
    "alba-ca-zapada": "Albă ca Zăpada",
}

def get_location(slug):
    for key in sorted(CITY_LABELS.keys(), key=len, reverse=True):
        if key in slug:
            return CITY_LABELS[key]
    return "București"

def get_character(slug):
    for key in sorted(CHARACTER_MAP.keys(), key=len, reverse=True):
        if key in slug:
            return CHARACTER_MAP[key]
    # fallback: clean up slug
    name = slug
    for prefix in ["animator-", "animatori-petreceri-copii-", "animatori-petreceri-"]:
        name = name.replace(prefix, "")
    for city_key in CITY_LABELS:
        name = name.replace(f"-{city_key}", "").replace(f"{city_key}-", "")
    name = name.replace("-", " ").title()
    return name if len(name) > 2 else "Animator Superparty"

def make_title(slug, character, location):
    # Avoid generic "Personaj Surpriză" - use actual character + location
    if "botez" in slug:
        return f"Animator Botez {location} | Personaj {character} | Superparty.ro"
    if "craciun" in slug or "revelion" in slug:
        return f"Petrecere Crăciun Copii {location} | {character} | Superparty.ro"
    if "animatopia" in slug:
        return f"Animatorii Superparty în {location} | {character} – Rezervă Acum"
    return f"Animator {character} Petreceri Copii {location} | Superparty.ro"

def make_description(slug, character, location):
    if "botez" in slug:
        return f"Animatori botez copii în {location}. {character} vine la evenimentul tău cu jocuri, baloane și pictură pe față. Sună 0722744377!"
    if "craciun" in slug:
        return f"Petrecere de Crăciun pentru copii în {location} cu {character}. Program complet, costume profesionale. Rezervare: 0722744377."
    return f"Animator {character} la petreceri copii în {location}. Jocuri, baloane modelate, pictură pe față. Rezervă acum: 0722744377!"

# Animatopia brand contamination patterns to remove/replace from non-Animatopia slugs
ANIMATOPIA_PATTERNS = [
    (r'Animatopia Despre Noi Echipa Animatori', 'Animatorul Superparty'),
    (r'animatopia\.ro', 'superparty.ro'),
    (r'\bAnimatopia\b', 'Superparty'),
    (r'\banimatopia\b', 'superparty'),
]

fixed_titles = 0
fixed_animatopia = 0
skipped = 0

mdx_files = sorted(MDX_DIR.glob("*.mdx"))
print(f"Processing {len(mdx_files)} MDX files...")

for mdx_path in mdx_files:
    slug = mdx_path.stem
    content = mdx_path.read_text(encoding="utf-8")
    original = content

    # --- Fix Animatopia brand leaks (only in non-Animatopia slugs) ---
    if "animatopia" not in slug:
        for pattern, replacement in ANIMATOPIA_PATTERNS:
            content = re.sub(pattern, replacement, content)

    # --- Fix duplicate titles/descriptions ---
    fm_match = re.match(r'^(---\r?\n)(.*?)(\r?\n---)', content, re.DOTALL)
    if fm_match:
        before = fm_match.group(1)
        fm_body = fm_match.group(2)
        after = content[fm_match.end():]

        character = get_character(slug)
        location = get_location(slug)
        new_title = make_title(slug, character, location)
        new_desc = make_description(slug, character, location)

        # Replace title
        fm_body = re.sub(
            r'^title:.*$',
            f'title: "{new_title}"',
            fm_body, flags=re.MULTILINE
        )
        # Replace description
        fm_body = re.sub(
            r'^description:.*$',
            f'description: "{new_desc}"',
            fm_body, flags=re.MULTILINE
        )

        content = before + fm_body + fm_match.group(3) + after
        fixed_titles += 1

    if content != original:
        mdx_path.write_text(content, encoding="utf-8")
        if "animatopia" not in slug and any(
            re.search(p, original) for p, _ in ANIMATOPIA_PATTERNS
        ):
            fixed_animatopia += 1
    else:
        skipped += 1

print(f"\nDone!")
print(f"  Titles/descriptions updated: {fixed_titles}")
print(f"  Animatopia brand fixes: {fixed_animatopia}")
print(f"  Unchanged files: {skipped}")
print(f"\nRe-run audit_and_fix_ready.py to confirm all still READY.")
