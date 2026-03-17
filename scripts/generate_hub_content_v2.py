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

MARKER = '<!-- LOCAL_HUB_INJECT_V2_START -->'
injected_count = 0

for filepath in astro_files:
    dirname = os.path.basename(os.path.dirname(filepath))
    region_key = dirname.replace('animatori-copii-', '')
    
    if region_key not in regions:
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if MARKER in content:
        continue

    region_data = regions[region_key]
    
    parks = ', '.join(region_data['parks'])
    vibe = region_data['vibe']
    
    injection = f'\n\n{MARKER}\n'
    injection += f'<section class="py-16 bg-white dark:bg-gray-900 border-t border-gray-100">\n'
    injection += f'  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">\n'
    injection += f'    <div class="grid md:grid-cols-2 gap-12 items-center">\n'
    injection += f'      <div>\n'
    injection += f'        <h2 class="text-3xl font-extrabold text-gray-900 dark:text-white mb-6">\n'
    injection += f'          Lideri în Organizarea de Petreceri în {region_key.replace("-", " ").title()}\n'
    injection += f'        </h2>\n'
    injection += f'        <div class="space-y-4 text-lg text-gray-600 dark:text-gray-300">\n'
    injection += f'          <p>Experiența ne-a învățat că fiecare comunitate are un ritm propriu. În {region_key.replace("-", " ").title()}, dinamica familiilor este una specială, orientată spre evenimente de calitate, sigure și memorabile. Fie că sunteți în căutarea unei soluții complete pentru o aniversare restrânsă acasă, fie că plănuiți un eveniment amplu în aer liber, folosind spații cunoscute din zonă precum {parks}, suntem partenerul dumneavoastră de încredere.</p>\n'
    injection += f'          <p>Alegând serviciile Superparty, optați pentru o echipă care cunoaște pulsul acestei locații: {vibe}. Nu mai pierdeți timpul căutând soluții de compromis. Noi aducem magia, logistica, costumele impecabile, boxa profesională și, mai presus de toate, experiența necesară pentru a gestiona grupurile de copii, permițându-vă să savurați evenimentul alături de invitații adulți fără niciun stres organizatoric.</p>\n'
    injection += f'        </div>\n'
    injection += f'      </div>\n'
    injection += f'      <div class="bg-purple-50 dark:bg-gray-800 p-8 rounded-2xl shadow-sm">\n'
    injection += f'        <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Top Întrebări Frecvente ({region_key.replace("-", " ").title()})</h3>\n'
    injection += f'        <dl class="space-y-6">\n'
    
    for faq in region_data['faqs']:
        injection += f'          <div class="border-b border-purple-100 pb-4 last:border-0 last:pb-0">\n'
        injection += f'            <dt class="text-lg font-semibold text-gray-900 dark:text-white">{faq["q"]}</dt>\n'
        injection += f'            <dd class="mt-2 text-gray-600 dark:text-gray-300">{faq["a"]}</dd>\n'
        injection += f'          </div>\n'
    injection += f'        </dl>\n'
    injection += f'      </div>\n'
    injection += f'    </div>\n'
    
    local_revs = [r for r in reviews if r['location_tag'] == region_key or r['location_tag'] in ['bucuresti', 'ilfov']]
    if local_revs:
        injection += f'    <div class="mt-16">\n'
        injection += f'      <h3 class="text-3xl font-extrabold text-gray-900 dark:text-white mb-8 text-center">Recenzii Verificate din Comunitatea {region_key.replace("-", " ").title()}</h3>\n'
        injection += f'      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">\n'
        for rev in local_revs:
            author_clean = rev['author']
            injection += f'        <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md border border-gray-100">\n'
            injection += f'          <div class="flex text-yellow-400 mb-4">\n'
            injection += f'            ★★★★★\n'
            injection += f'          </div>\n'
            injection += f'          <p class="italic text-gray-600 dark:text-gray-300 mb-4\">"{rev["text"]}"</p>\n'
            injection += f'          <footer class="font-semibold text-gray-900 dark:text-white">— {author_clean}</footer>\n'
            injection += f'        </div>\n'
        injection += f'      </div>\n'
        injection += f'    </div>\n'
    
    injection += f'  </div>\n'
    injection += f'</section>\n'
    injection += f'<!-- LOCAL_HUB_INJECT_V2_END -->\n'
    
    inject_point = content.rfind('<FAQ')
    if inject_point == -1:
        inject_point = content.rfind('<Footer')
        
    if inject_point == -1:
        new_content = content + injection
    else:
        new_content = content[:inject_point] + injection + '\n' + content[inject_point:]
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    injected_count += 1

print(f"Successfully injected V2 hyper-local HTML context into {injected_count} files.")
