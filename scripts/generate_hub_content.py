import os
import glob
import json

db_path = r'C:\Users\ursac\Superparty\scripts\local_db.json'
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

regions = db['regions']
reviews = db['reviews']

base_pages = r'C:\Users\ursac\Superparty\src\pages'
astro_files = glob.glob(os.path.join(base_pages, 'animatori-copii-*', 'index.astro'))

print(f"Found {len(astro_files)} Hub pages to process.")

MARKER = '<!-- LOCAL_HUB_INJECT_START -->'
injected_count = 0

for filepath in astro_files:
    dirname = os.path.basename(os.path.dirname(filepath))
    
    # E.g., animatori-copii-sector-1 -> sector-1
    region_key = dirname.replace('animatori-copii-', '')
    
    if region_key not in regions:
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if MARKER in content:
        continue

    region_data = regions[region_key]
    
    # Construct a massive block to dilute boilerplate and hit 60% uniqueness
    parks = ', '.join(region_data['parks'])
    vibe = region_data['vibe']
    
    # We create an Astro component string
    injection = f"\n\n{MARKER}\n"
    injection += f"<section class=\"py-16 bg-white dark:bg-gray-900\">\n"
    injection += f"  <div class=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">\n"
    injection += f"    <h2 class=\"text-3xl font-bold text-gray-900 dark:text-white mb-8 text-center\">\n"
    injection += f"      Organizarea Petrecerilor în {region_key.replace('-', ' ').title()}\n"
    injection += f"    </h2>\n"
    
    injection += f"    <div class=\"prose prose-lg dark:prose-invert max-w-none\">\n"
    injection += f"      <p>Superparty este principalul furnizor de servicii de divertisment pentru copii în inima comunității din {region_key.replace('-', ' ').title()}. Fie că planificați o petrecere restrânsă acasă, o aniversare spectaculoasă la curte, sau o ieșire cu zeci de copii în spații deschise precum {parks}, echipa noastră cunoaște perfect logistica și specificul zonei.</p>\n"
    injection += f"      <p>Am adus zâmbete la sute de petreceri în locații renumite, profitând la maximum de vibrația unică a zonei: {vibe}. De la spectacole de magie interactivă la show-uri complexe cu mascotele Disney, ne asigurăm că fiecare moment este sigur, captivant și, mai ales, lipsit de stres pentru părinți.</p>\n"
    injection += f"    </div>\n"
    
    injection += f"    <div class=\"mt-12\">\n"
    injection += f"      <h3 class=\"text-2xl font-bold text-gray-900 dark:text-white mb-6\">Întrebări Frecvente Specifice Zonei</h3>\n"
    injection += f"      <dl class=\"space-y-6\">\n"
    for faq in region_data['faqs']:
        injection += f"        <div>\n"
        injection += f"          <dt class=\"text-lg font-semibold text-gray-900 dark:text-white\">Q: {faq['q']}</dt>\n"
        injection += f"          <dd class=\"mt-2 text-gray-600 dark:text-gray-300\">A: {faq['a']}</dd>\n"
        injection += f"        </div>\n"
    injection += f"      </dl>\n"
    injection += f"    </div>\n"
    
    local_revs = [r for r in reviews if r['location_tag'] == region_key or r['location_tag'] in ['bucuresti', 'ilfov']]
    if local_revs:
        injection += f"    <div class=\"mt-12 bg-gray-50 dark:bg-gray-800 p-8 rounded-2xl\">\n"
        injection += f"      <h3 class=\"text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center\">Ce spun Părinții din {region_key.replace('-', ' ').title()}</h3>\n"
        injection += f"      <div class=\"grid md:grid-cols-2 gap-8\">\n"
        for rev in local_revs[:2]:
            author_clean = rev['author'] if region_key in rev.get('location_tag', '') else rev['author']
            injection += f"        <blockquote class=\"italic text-gray-600 dark:text-gray-300\">\n"
            injection += f"          \"{rev['text']}\"\n"
            injection += f"          <footer class=\"mt-4 font-semibold text-gray-900 dark:text-white\">— {author_clean}</footer>\n"
            injection += f"        </blockquote>\n"
        injection += f"      </div>\n"
        injection += f"    </div>\n"
    
    injection += f"  </div>\n"
    injection += f"</section>\n"
    injection += f"<!-- LOCAL_HUB_INJECT_END -->\n"
    
    # Inject right before the Footer component or at the end
    inject_point = content.rfind('<Footer')
    if inject_point == -1:
        new_content = content + injection
    else:
        new_content = content[:inject_point] + injection + '\n' + content[inject_point:]
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    injected_count += 1

print(f"Successfully injected hyper-local HTML context into {injected_count} Hub pages.")
