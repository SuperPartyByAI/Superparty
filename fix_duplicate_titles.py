#!/usr/bin/env python3
"""
Final pass: make any remaining duplicate titles unique 
by appending the slug-specific suffix (last meaningful word).
"""
import re
from pathlib import Path
from collections import Counter

MDX_DIR = Path("src/content/seo-articles")

# Build title -> [slug] map
title_to_slugs = {}
slug_to_path = {}

for mdx_path in sorted(MDX_DIR.glob("*.mdx")):
    slug = mdx_path.stem
    content = mdx_path.read_text(encoding="utf-8")
    slug_to_path[slug] = mdx_path
    m = re.search(r'^title: "(.+?)"', content, re.MULTILINE)
    if m:
        title = m.group(1)
        title_to_slugs.setdefault(title, []).append(slug)

duplicates = {t: slugs for t, slugs in title_to_slugs.items() if len(slugs) > 1}
print(f"Duplicate title groups: {len(duplicates)}")

fixed = 0
for title, slugs in duplicates.items():
    for slug in slugs:
        mdx_path = slug_to_path[slug]
        content = mdx_path.read_text(encoding="utf-8")
        
        # Extract a unique distinguisher from the slug
        # Remove common prefixes/suffixes and take a specific part
        parts = slug.replace("animatori-petreceri-copii-", "").replace("animator-", "").split("-")
        # Find the most unique part (typically character variant or location sub-part)
        # Just append the last 2 non-city parts that differ
        
        # Simple approach: append the full slug keyword hint in parens
        # e.g. "disney" vs plain, "marvel" vs plain, sector number
        slug_hint = ""
        if "disney" in slug: slug_hint = " – Disney"
        elif "marvel" in slug: slug_hint = " – Marvel"
        elif "dc-" in slug: slug_hint = " – DC"
        elif "sector-1" in slug: slug_hint = " – Sector 1"
        elif "sector-2" in slug: slug_hint = " – Sector 2"
        elif "sector-3" in slug: slug_hint = " – Sector 3"
        elif "sector-4" in slug: slug_hint = " – Sector 4"
        elif "sector-5" in slug: slug_hint = " – Sector 5"
        elif "sector-6" in slug: slug_hint = " – Sector 6"
        elif "ilfov" in slug: slug_hint = " – Ilfov"
        elif "bragadiru" in slug: slug_hint = " – Bragadiru"
        elif "voluntari" in slug: slug_hint = " – Voluntari"
        elif "otopeni" in slug: slug_hint = " – Otopeni"
        elif "pantelimon" in slug: slug_hint = " – Pantelimon"
        elif "botez" in slug: slug_hint = " – Botez"
        elif "ghid" in slug: slug_hint = " – Ghid Complet"
        elif "animatopia" in slug: slug_hint = " – Animatopia"
        elif "impreuna" in slug: slug_hint = " – Împreună"
        elif "petreceri-copii" in slug and "care-e" in slug: slug_hint = " – Comparație"
        else:
            # Use last meaningful slug segment
            meaningful = [p for p in parts if len(p) > 3 and p not in ["petreceri","copii","bucuresti","animatori"]]
            if meaningful:
                slug_hint = f" – {meaningful[-1].title()}"
        
        if not slug_hint:
            continue
            
        new_title = title.replace(" | Superparty.ro", "") + slug_hint + " | Superparty.ro"
        # Remove double | Superparty.ro if it already has it
        new_title = new_title.replace(" | Superparty.ro | Superparty.ro", " | Superparty.ro")
        
        new_content = re.sub(
            r'^title: ".+?"',
            f'title: "{new_title}"',
            content,
            flags=re.MULTILINE
        )
        
        if new_content != content:
            mdx_path.write_text(new_content, encoding="utf-8")
            fixed += 1

# Final check
title_counts = Counter()
for mdx_path in sorted(MDX_DIR.glob("*.mdx")):
    content = mdx_path.read_text(encoding="utf-8")
    m = re.search(r'^title: "(.+?)"', content, re.MULTILINE)
    if m:
        title_counts[m.group(1)] += 1

dupes_remaining = sum(1 for c in title_counts.values() if c > 1)
print(f"Fixed: {fixed} | Duplicate titles remaining: {dupes_remaining}")
