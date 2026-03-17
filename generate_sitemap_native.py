import os
import glob
from datetime import datetime

base_url = "https://www.superparty.ro"
xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
xml_footer = '</urlset>'

# Hardcoded main pages
main_pages = [
    "",
    "/animatori-petreceri-copii",
    "/ursitoare-botez",
    "/decoratiuni-baloane",
    "/arcade-baloane",
    "/baloane-cu-heliu",
    "/vata-de-zahar-si-popcorn",
    "/mos-craciun-de-inchiriat",
    "/piniata",
    "/contact",
    "/arie-acoperire"
]

now = datetime.utcnow().strftime("%Y-%m-%dT%H:M:%SZ")
urls = []

# Adaugam paginile principale (prioritate maxima)
for p in main_pages:
    urls.append(f"""  <url>
    <loc>{base_url}{p}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>{'daily' if p == '' else 'weekly'}</changefreq>
    <priority>{'1.0' if p == '' else '0.9'}</priority>
  </url>""")

# Preluam cele ~500 articole SEO
articles_path = r"C:\Users\ursac\Superparty\src\content\seo-articles\*.mdx"
for file in glob.glob(articles_path):
    filename = os.path.basename(file)
    slug = filename.replace(".mdx", "")
    urls.append(f"""  <url>
    <loc>{base_url}/petreceri/{slug}</loc>
    <lastmod>{now}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>""")

# Salvam sitemap.xml in folderul public unde Astro il muta la build direct in root
output_path = r"C:\Users\ursac\Superparty\public\sitemap.xml"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(xml_header + "\n".join(urls) + "\n" + xml_footer)

print(f"✅ SITEMAP GENERAT CU SUCCES! {len(urls)} link-uri scrise in {output_path}")
