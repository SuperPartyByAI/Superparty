import re
import os

with open(r'c:\Users\ursac\Superparty\wp_posts.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

rows = text.split('),(')
count = 0
for i, r in enumerate(rows):
    if "'page'" in r and "'publish'" in r:
        if 'wp:generateblocks' in r or '<div' in r or 'wowparty' in r.lower() or 'acas' in r.lower():
            parts = r.split("','")
            if len(parts) > 5:
                # Titlul este de obicei pe o poziție specifică după content
                title = parts[5].replace("\\'", "'")
                content = parts[4].replace("\\n", "\n").replace("\\r", "\r")
                
                # Curățare nume fișier
                safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).strip().replace(" ", "_")
                if not safe_title:
                    safe_title = f"page_{i}"
                
                out_path = rf'c:\Users\ursac\Superparty\wowparty_{safe_title}.html'
                with open(out_path, 'w', encoding='utf-8') as out:
                    out.write(content)
                print(f"Saved: wowparty_{safe_title}.html")
                count += 1

print(f"Done. Extracted {count} pages.")
