import os
import glob
import json
import re

db_path = r'C:\Users\ursac\Superparty\scripts\local_db.json'
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

regions = db['regions']
base_pages = r'C:\Users\ursac\Superparty\src\pages'
astro_files = glob.glob(os.path.join(base_pages, 'animatori-copii-*', 'index.astro'))

injected_count = 0

for filepath in astro_files:
    dirname = os.path.basename(os.path.dirname(filepath))
    region_key = dirname.replace('animatori-copii-', '')
    
    if region_key not in regions or 'logistics' not in regions[region_key]:
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    region_data = regions[region_key]

    # Strip ALL previously injected blocks (V1, V2, Util) completely
    content = re.sub(r'<!--\s*LOCAL_HUB_INJECT_START\s*-->.*?<!--\s*LOCAL_HUB_INJECT_END\s*-->', '', content, flags=re.DOTALL)
    content = re.sub(r'<!--\s*LOCAL_HUB_INJECT_V2_START\s*-->.*?<!--\s*LOCAL_HUB_INJECT_V2_END\s*-->', '', content, flags=re.DOTALL)
    content = re.sub(r'<!--\s*LOCAL_HUB_UTIL_INJECT\s*-->.*?(?=(</Layout>|\Z))', '', content, flags=re.DOTALL)

    parks_html = ""
    for p in region_data['top_parks']:
        parks_html += f'<li class="flex items-start"><span class="text-purple-500 mr-2">✓</span><span>{p}</span></li>\n'
    
    injection = f'\n<!-- LOCAL_HUB_UTIL_INJECT -->\n'
    injection += f'<section class="py-12 bg-gray-50 dark:bg-gray-800/50">\n'
    injection += f'  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">\n'
    injection += f'    <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">Ghid Utilitar: Petreceri în {region_key.replace("-", " ").title()}</h3>\n'
    injection += f'    <div class="grid md:grid-cols-3 gap-8">\n'
    
    # 1. Logistics
    injection += f'      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n'
    injection += f'        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">\n'
    injection += f'          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>\n'
    injection += f'          Logistică & Deplasare\n'
    injection += f'        </div>\n'
    injection += f'        <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{region_data["logistics"]}</p>\n'
    injection += f'      </div>\n'
    
    # 2. Parks
    injection += f'      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n'
    injection += f'        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">\n'
    injection += f'          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path></svg>\n'
    injection += f'          Top Parcuri Recomandate\n'
    injection += f'        </div>\n'
    injection += f'        <ul class="text-sm text-gray-600 dark:text-gray-300 space-y-2">\n{parks_html}        </ul>\n'
    injection += f'      </div>\n'
    
    # 3. Venues
    injection += f'      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n'
    injection += f'        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">\n'
    injection += f'          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>\n'
    injection += f'          Săli & Restaurante\n'
    injection += f'        </div>\n'
    injection += f'        <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{region_data["venues"]}</p>\n'
    injection += f'      </div>\n'
    
    injection += f'    </div>\n  </div>\n</section>\n'
    
    # Inject directly before the closing Layout tag
    layout_idx = content.rfind('</Layout>')
    if layout_idx != -1:
        new_content = content[:layout_idx] + injection + content[layout_idx:]
    else:
        new_content = content + injection
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    injected_count += 1

print(f"Force injected V4 utilized grids securely into {injected_count} Hub pages.")
