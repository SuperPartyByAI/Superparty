"""
Colecteaza toate URL-urile arhivate pentru superparty.ro din Wayback Machine.
Surse:
  1. CDX API pentru superparty.ro/* (http + https + www)
  2. Sitemap.xml arhivat din Wayback
"""
import urllib.request, urllib.error, json, os, time
from datetime import datetime

TODAY = datetime.now().strftime('%Y-%m-%d')
OUTPUT_DIR = 'reports/superparty'
OUTPUT_FILE = f'{OUTPUT_DIR}/old_urls_hosterion_{TODAY}.txt'
PREVIEW_FILE = f'{OUTPUT_DIR}/old_urls_preview.txt'

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_text(url, timeout=30, retries=2):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (research)'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(3)
    return ''

all_urls = set()

# ==========================================
# 1. CDX API - toate variantele domeniului
# ==========================================
CDX_QUERIES = [
    'https://web.archive.org/cdx/search/cdx?url=superparty.ro/*&output=text&fl=original&filter=statuscode:200&collapse=urlkey&limit=1000',
    'https://web.archive.org/cdx/search/cdx?url=www.superparty.ro/*&output=text&fl=original&filter=statuscode:200&collapse=urlkey&limit=1000',
]

for cdx_url in CDX_QUERIES:
    print(f'\nFetching CDX: {cdx_url[:80]}...')
    data = fetch_text(cdx_url, timeout=30)
    if data:
        lines = [l.strip() for l in data.strip().split('\n') if l.strip()]
        # Pastreaza doar URL-uri superparty.ro reale (nu resurse statice WordPress inutile)
        for url in lines:
            # Normalizeaza: sterge www.
            clean = url.replace('//www.superparty.ro', '//superparty.ro')
            # Sterge query strings si fragmente (pentru curatenie)
            clean = clean.split('?')[0].split('#')[0].rstrip('/')
            if 'superparty.ro' in clean:
                all_urls.add(clean)
        print(f"  Gasite: {len(lines)} URL-uri")

# ==========================================
# 2. Cauta sitemap.xml arhivat in Wayback
# ==========================================
print('\nCautam sitemap.xml arhivat...')
sitemap_cdx = fetch_text(
    'https://web.archive.org/cdx/search/cdx?url=superparty.ro/sitemap.xml&output=text&fl=timestamp,original&collapse=timestamp&limit=10',
    timeout=25
)
if sitemap_cdx:
    lines = [l.strip() for l in sitemap_cdx.strip().split('\n') if l.strip()]
    print(f"  Gasite {len(lines)} snapshot-uri pentru sitemap.xml")
    # Ia ultimul snapshot
    if lines:
        last = lines[-1].split()
        if len(last) >= 1:
            ts = last[0] if len(last) == 2 else last[0]
            archive_url = f'https://web.archive.org/web/{ts}/https://superparty.ro/sitemap.xml'
            print(f"  Descarcam sitemap din: {archive_url}")
            xml_data = fetch_text(archive_url, timeout=25)
            if xml_data and '<loc>' in xml_data:
                import re
                locs = re.findall(r'<loc>(.*?)</loc>', xml_data)
                for loc in locs:
                    clean = loc.strip().replace('//www.superparty.ro', '//superparty.ro').rstrip('/')
                    if 'superparty.ro' in clean:
                        all_urls.add(clean)
                print(f"  Extrase {len(locs)} URL-uri din sitemap Wayback")

# ==========================================
# 3. Filtrare finala
# ==========================================
# Pastreaza numai URL-uri de continut (nu resurse statice WP)
EXCLUDE = ['/wp-content/', '/wp-includes/', '/wp-admin/', '/wp-json/',
           '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.woff',
           '.woff2', '.svg', '.ico', '/feed', '/comments/feed',
           '/xmlrpc', '/?s=', '/author/', '/tag/', '/category/page/']

def is_content_url(url):
    for exc in EXCLUDE:
        if exc in url:
            return False
    return True

content_urls = sorted([u for u in all_urls if is_content_url(u)])
all_sorted = sorted(all_urls)

print(f'\nTotal URL-uri brute: {len(all_urls)}')
print(f'URL-uri de continut (fara resurse statice): {len(content_urls)}')

# ==========================================
# 4. Scrie fisierele
# ==========================================
# Fisierul principal - TOATE URL-urile (inclusiv resurse statice)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f'# Superparty.ro - URL-uri arhivate din Wayback Machine\n')
    f.write(f'# Data colectare: {TODAY}\n')
    f.write(f'# Total URL-uri: {len(all_sorted)}\n')
    f.write(f'# URL-uri de continut (fara resurse WP): {len(content_urls)}\n\n')
    f.write(f'## URL-uri de continut:\n')
    for u in content_urls:
        f.write(u + '\n')
    f.write(f'\n## Toate URL-urile (inclusiv resurse statice):\n')
    for u in all_sorted:
        f.write(u + '\n')

# Preview - primele 20 URL-uri de continut
with open(PREVIEW_FILE, 'w', encoding='utf-8') as f:
    f.write(f'# Preview primele 20 URL-uri de continut\n')
    for u in content_urls[:20]:
        f.write(u + '\n')

print(f'\nFisiere scrise:')
print(f'  {OUTPUT_FILE} ({len(all_sorted)} URL-uri totale)')
print(f'  {PREVIEW_FILE} (primele 20 URL-uri de continut)')
print(f'\nPrimele 20 URL-uri de continut:')
for u in content_urls[:20]:
    print(f'  {u}')
