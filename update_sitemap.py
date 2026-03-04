"""Script care adauga paginile comerciale in sitemap.xml"""
from datetime import datetime

TODAY = datetime.now().strftime('%Y-%m-%d')

commercial_urls = [
    ('https://superparty.ro/animatori-petreceri-copii', '1.0', 'weekly'),
    ('https://superparty.ro/contact', '0.9', 'monthly'),
    ('https://superparty.ro/arie-acoperire', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/bucuresti', '0.9', 'weekly'),
    ('https://superparty.ro/petreceri/sector-1', '0.9', 'monthly'),
    ('https://superparty.ro/petreceri/sector-2', '0.9', 'monthly'),
    ('https://superparty.ro/petreceri/sector-3', '0.9', 'monthly'),
    ('https://superparty.ro/petreceri/sector-4', '0.9', 'monthly'),
    ('https://superparty.ro/petreceri/sector-5', '0.9', 'monthly'),
    ('https://superparty.ro/petreceri/sector-6', '0.9', 'monthly'),
    ('https://superparty.ro/petreceri/ilfov', '0.9', 'monthly'),
    ('https://superparty.ro/petreceri/voluntari', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/popesti-leordeni', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/otopeni', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/pantelimon', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/bragadiru', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/chiajna', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/chitila', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/buftea', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/mogosoaia', '0.8', 'monthly'),
    ('https://superparty.ro/petreceri/corbeanca', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/tunari', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/snagov', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/dobroesti', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/jilava', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/magurele', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/cernica', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/afumati', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/branesti', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/domnesti', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/berceni-ilfov', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/1-decembrie', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/dragomiresti-vale', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/ganeasa', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/glina', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/peris', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/dascalu', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/moara-vlasiei', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/stefanestii-de-jos', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/ciorogirla', '0.7', 'monthly'),
    ('https://superparty.ro/petreceri/balotesti', '0.7', 'monthly'),
    ('https://superparty.ro/arcade-baloane', '0.7', 'monthly'),
    ('https://superparty.ro/baloane-cu-heliu', '0.7', 'monthly'),
    ('https://superparty.ro/decoratiuni-baloane', '0.7', 'monthly'),
    ('https://superparty.ro/mos-craciun-de-inchiriat', '0.7', 'monthly'),
    ('https://superparty.ro/piniata', '0.7', 'monthly'),
    ('https://superparty.ro/ursitoare-botez', '0.7', 'monthly'),
    ('https://superparty.ro/vata-de-zahar-si-popcorn', '0.7', 'monthly'),
]

with open('public/sitemap.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# Gaseste URL-urile existente
existing = set()
for line in content.split('\n'):
    stripped = line.strip()
    if stripped.startswith('<loc>') and stripped.endswith('</loc>'):
        url = stripped[5:-6]
        existing.add(url)

print(f'URL-uri existente in sitemap: {len(existing)}')

# Construieste blocurile noi
new_entries = []
added = 0
for url, priority, freq in commercial_urls:
    if url not in existing:
        entry = f'  <url>\n    <loc>{url}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n    <lastmod>{TODAY}</lastmod>\n  </url>'
        new_entries.append(entry)
        added += 1

print(f'URL-uri noi de adaugat: {added}')

# Insereaza dupa <urlset ...>
insert_pos = content.find('<urlset')
insert_pos = content.find('>', insert_pos) + 1
new_block = '\n' + '\n'.join(new_entries) + '\n'
new_content = content[:insert_pos] + new_block + content[insert_pos:]

# Update comment
new_content = new_content.replace('2026-03-03', TODAY, 1)

with open('public/sitemap.xml', 'w', encoding='utf-8') as f:
    f.write(new_content)

total = new_content.count('<loc>')
print(f'Total URL-uri in sitemap: {total}')
print(f'Done! Adaugate {added} pagini comerciale.')
