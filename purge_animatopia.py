#!/usr/bin/env python3
"""Remove all animatopia-* MDX files and fix testimonials JSON."""
import os, json, re
from pathlib import Path

SRC = Path("src/content/seo-articles")
rename_map = {}

# Find and rename all remaining animatopia-* files
for mdx in sorted(SRC.glob("*.mdx")):
    if "animatopia" in mdx.stem.lower():
        slug_old = mdx.stem
        slug_new = slug_old.replace("animatopia", "superparty").replace("--", "-").strip("-")
        rename_map[slug_old] = slug_new

        content = mdx.read_text(encoding="utf-8")
        # Replace brand
        content = content.replace("Animatopia", "Superparty").replace("animatopia", "superparty")
        # Fix title
        loc = "București"
        for city in ["cluj-napoca", "bucuresti", "ilfov"]:
            if city in slug_new:
                loc = city.replace("-", " ").title()
        new_title = f'Animatori Petreceri Copii {loc} | Superparty.ro'
        content = re.sub(r'title: ".+?"', f'title: "{new_title}"', content)
        content = re.sub(r'description: ".+?"',
            'description: "Animatori profesionisti petreceri copii cu Superparty. Costume premium, jocuri, baloane. Rezerva: 0722744377!"',
            content)

        new_path = SRC / (slug_new + ".mdx")
        new_path.write_text(content, encoding="utf-8")
        mdx.unlink()
        print(f"Renamed: {mdx.name} -> {slug_new}.mdx")

if not rename_map:
    print("No animatopia-*.mdx files found (already clean).")

# Patch testimonials JSON
json_path = Path("src/data/superparty_testimonials.json")
data = json.loads(json_path.read_text(encoding="utf-8"))
patched = 0
for item in data:
    if item.get("slug") in rename_map:
        item["slug"] = rename_map[item["slug"]]
        patched += 1
    # Clean any remaining animatopia in testimonial text
    old_text = item.get("text", "")
    item["text"] = old_text.replace("Animatopia", "Superparty").replace("animatopia", "superparty")
json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Testimonials JSON: patched {patched} slug(s)")

# Final scan
hits = []
for root, dirs, files in os.walk("src"):
    for fn in files:
        path = os.path.join(root, fn)
        try:
            c = open(path, encoding="utf-8", errors="ignore").read()
            if "Animatopia" in c or "animatopia" in c:
                hits.append(path)
        except:
            pass

print(f"\nFinal scan - Animatopia hits in src/: {len(hits)}")
for h in hits:
    print(f"  {h}")
if len(hits) == 0:
    print("CLEAN: zero Animatopia references in src/")
