import re

with open(r'c:\Users\ursac\Superparty\wp_posts.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

matches = re.finditer(r"(?i)(.{0,200}Prima pagina.{0,1000})", text)
count = 0
for m in matches:
    print(f"Match {count}: {m.group(1)}")
    count += 1
    if count > 5: break

if count == 0:
    print("Nu am gasit 'Prima pagina', caut 'wowparty' langa 'publish' si 'page'...")
    matches = re.finditer(r"(?i)(.{0,200}wowparty.{0,1000})", text)
    for m in matches:
        if "'page'" in m.group(1):
            print(f"Match {count}: {m.group(1)[:500]}")
            count += 1
            if count > 5: break
