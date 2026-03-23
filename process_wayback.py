import os
import re
from bs4 import BeautifulSoup

html_path = r'c:\Users\ursac\Superparty\wowparty_original.html'
out_path = r'c:\Users\ursac\WowParty\src\pages\index.astro'

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

for s in soup.find_all('script'):
    src = s.get('src', '')
    if 'archive.org' in src or 'wayback' in src:
        s.decompose()
    elif '__wm' in s.text:
        s.decompose()

for d in soup.find_all(id=re.compile(r'wm-ipp.*')):
    d.decompose()

def fix_url(url):
    if not url: return url
    url = re.sub(r'https?://web\.archive\.org/web/\d+(?:im_|js_|cs_)?/', '', url)
    url = url.replace('https://www.wowparty.ro', '')
    url = url.replace('http://www.wowparty.ro', '')
    return url

for tag in soup.find_all(True):
    if tag.has_attr('href'): tag['href'] = fix_url(tag['href'])
    if tag.has_attr('src'): tag['src'] = fix_url(tag['src'])
    if tag.has_attr('srcset'):
        srcs = tag['srcset'].split(',')
        tag['srcset'] = ', '.join([' '.join([fix_url(p) if i==0 else p for i, p in enumerate(s.strip().split())]) for s in srcs])
    if tag.has_attr('style'):
        tag['style'] = re.sub(r'url\([\'"]?https?://web\.archive\.org/web/\d+(?:im_)?/(https?://www\.wowparty\.ro)?([^\)\'"]+)[\'"]?\)', r'url(\2)', tag['style'])

# ESCAPE JSX and ASTRO PARSING: Add is:inline to all scripts and styles
for tag in soup.find_all(['script', 'style']):
    tag['is:inline'] = ""

astro_code = f"""---
// Migrat 1:1 din WordPress original via Wayback Machine
---
{soup.prettify()}
"""

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(astro_code)

print("✅ process_wayback corectat cu is:inline")
