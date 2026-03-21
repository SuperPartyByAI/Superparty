import os
import glob
import re

files = glob.glob('src/content/seo-articles/*.md')
fixed = 0
for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Inlocuieste pubDate: '2026-03-21' cu pubDate: 2026-03-21
    new_content = re.sub(r"pubDate: '(\d{4}-\d{2}-\d{2})'", r'pubDate: \1', content)
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        fixed += 1

print(f'Reparat pubDate in {fixed} fisiere')
