#!/usr/bin/env python3
"""Scrub all Animatopia references from testimonials JSON."""
import json

path = "src/data/superparty_testimonials.json"
with open(path, encoding="utf-8") as f:
    data = json.load(f)

count = 0
for item in data:
    for k in list(item.keys()):
        val = item[k]
        if isinstance(val, str) and ("animatopia" in val.lower()):
            item[k] = val.replace("Animatopia", "Superparty").replace("animatopia", "superparty")
            count += 1

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Verify
raw = open(path, encoding="utf-8").read()
still = "animatopia" in raw.lower()
print(f"Fields cleaned: {count}")
print(f"Animatopia still present: {still}")
if not still:
    print("CLEAN: superparty_testimonials.json has zero Animatopia references")
