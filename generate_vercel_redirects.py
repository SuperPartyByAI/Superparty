"""
Script pentru generarea vercel.json cu redirecturi 301 corecte.
Citeste URL-urile vechi WordPress din Wayback Machine si le mapeaza la noile URL-uri Astro.
"""
import json
import xml.etree.ElementTree as ET

# ==============================
# 1. Citeste URL-urile WordPress vechi
# ==============================
with open('old_wp_urls.txt', 'r') as f:
    raw_wp_urls = [l.strip() for l in f.readlines() if l.strip()]

# Extrage path-urile
wp_paths = []
for u in raw_wp_urls:
    path = u.replace('https://www.superparty.ro', '').replace('https://superparty.ro', '').strip()
    if not path:
        path = '/'
    wp_paths.append(path)

print(f"Total URL-uri WP brute: {len(wp_paths)}")

# Filtreaza - exclude resurse tehnice WP care NU sunt pagini de continut
EXCLUDE_PATTERNS = [
    '/wp-', '/feed', '/comments', '/xmlrpc', '/sitemap',
    '/wp-json', '?s=', '.js', '.css', '.png', '.jpg', '.gif',
    '/page/', '/author/', '/tag/', '/category/'
]

def is_page(path):
    for exc in EXCLUDE_PATTERNS:
        if exc in path:
            return False
    # Pastreaza paginile cu slug sau /?p=
    return True

page_paths = [p for p in wp_paths if is_page(p)]
print(f"URL-uri pagini de continut: {len(page_paths)}")
for p in sorted(page_paths):
    print(f"  WP: {p}")

# ==============================
# 2. Incarca URL-urile Astro noi din sitemap
# ==============================
tree = ET.parse('public/sitemap.xml')
root = tree.getroot()
ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

astro_slugs = []
for url_el in root.findall('sm:url', ns):
    loc = url_el.find('sm:loc', ns).text
    if '/petreceri/' in loc:
        slug = loc.split('/petreceri/')[-1].rstrip('/')
        astro_slugs.append(slug)

print(f"\nURL-uri Astro noi: {len(astro_slugs)}")

# ==============================
# 3. Construieste redirecturi
# ==============================
redirects = []

# A. Redirecturi directe: path WP -> pagina Astro corespunzatoare
# Mapeaza /animatori-petreceri-copii/ -> /animatori-petreceri-copii (hub)
# Mapeaza /?p=ID -> / (nu putem sti exact care articol)
# Pagini de servicii directe (ex: /arcade-baloane/) -> pagina proprie Astro

for path in page_paths:
    # Scoate slash-ul final
    clean = path.rstrip('/')
    if not clean or clean == '/':
        continue
    
    # Articole cu ID WordPress (?p=NNN) -> homepage
    if '?p=' in clean:
        redirects.append({
            'source': clean,
            'destination': '/',
            'permanent': True
        })
        continue
    
    # Pagini de servicii principale care exista ca rute Astro
    # ex: /animatori-petreceri-copii -> /animatori-petreceri-copii (ruta Astro proprie)
    # Verifica daca e o ruta directa in Astro (nu /petreceri/)
    # Acestea sunt paginile care NU sunt in /petreceri/ pe Astro
    # ci au propria ruta (index pages, hub pages)
    
    # Paginile care EXISTA ca rute directe Astro (din src/pages)
    ASTRO_DIRECT_ROUTES = [
        '/animatori-petreceri-copii',
        '/arcade-baloane', 
        '/baloane-cu-heliu',
        '/decoratiuni-baloane',
        '/mos-craciun-de-inchiriat',
        '/piniata',
        '/ursitoare-botez',
        '/vata-de-zahar-si-popcorn',
        '/contact',
        '/petreceri/bucuresti',
        '/petreceri/ilfov',
        '/petreceri/sector-1',
        '/petreceri/sector-2',
        '/petreceri/sector-3',
        '/petreceri/sector-4',
        '/petreceri/sector-5',
        '/petreceri/sector-6',
    ]
    
    # Verifica daca slug-ul se potriveste cu o ruta Astro directa
    if clean in ASTRO_DIRECT_ROUTES:
        # Redirect la aceeasi pagina (din www -> fara www, sau identic)
        # Nu e nevoie de redirect daca e acelasi path
        pass
    else:
        # Poate e un articol care acum e la /petreceri/<slug>
        # Incearca sa gaseasca slug matching
        slug_clean = clean.lstrip('/')
        if slug_clean in astro_slugs:
            redirects.append({
                'source': clean,
                'destination': f'/petreceri/{slug_clean}',
                'permanent': True
            })
        else:
            # Redirect catre homepage daca nu gasim match
            redirects.append({
                'source': clean,
                'destination': '/',
                'permanent': True
            })

# B. Redirect important: ?p=ID (WordPress article IDs) -> homepage
# Adauga un wildcard pentru orice ?p= nu prins mai sus
redirects.append({
    'source': '/',
    'has': [{'type': 'query', 'key': 'p'}],
    'destination': '/',
    'permanent': True
})

print(f"\nRedirecturi generate: {len(redirects)}")
for r in redirects:
    print(f"  {r['source']} -> {r['destination']}")

# ==============================
# 4. Scrie vercel.json
# ==============================
vercel_config = {
    'redirects': redirects
}

with open('vercel.json', 'w', encoding='utf-8') as f:
    json.dump(vercel_config, f, ensure_ascii=False, indent=2)

print(f"\nvercel.json scris cu {len(redirects)} redirecturi!")
