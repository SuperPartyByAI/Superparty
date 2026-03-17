import os
import glob
import json

db_path = r'C:\Users\ursac\Superparty\scripts\local_db.json'
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

regions = db['regions']
base_pages = r'C:\Users\ursac\Superparty\src\pages'
astro_files = glob.glob(os.path.join(base_pages, 'animatori-copii-*', 'index.astro'))

MARKER = '<!-- LOCAL_HUB_UTIL_INJECT -->'
injected_count = 0

for filepath in astro_files:
    dirname = os.path.basename(os.path.dirname(filepath))
    region_key = dirname.replace('animatori-copii-', '')
    
    if region_key not in regions:
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    region_data = regions[region_key]
    if 'logistics' not in region_data:
        continue

    # Prevent double injection
    if MARKER in content:
        content = content.replace(MARKER, '')

    parks_html = ""
    for p in region_data['top_parks']:
        parks_html += f'<li class="flex items-start"><span class="text-purple-500 mr-2">✓</span><span>{p}</span></li>\n'
    
    injection = f'\n\n{MARKER}\n'
    injection += f'<section class="py-12 bg-gray-50 dark:bg-gray-800/50">\n'
    injection += f'  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">\n'
    injection += f'    <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">Ghid Utilitar: Petreceri în {region_key.replace("-", " ").title()}</h3>\n'
    injection += f'    <div class="grid md:grid-cols-3 gap-8">\n'
    injection += f'      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n'
    injection += f'        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">Logistică & Deplasare</div>\n'
    injection += f'        <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{region_data["logistics"]}</p>\n'
    injection += f'      </div>\n'
    injection += f'      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n'
    injection += f'        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">Top 3 Parcuri Recomandate</div>\n'
    injection += f'        <ul class="text-sm text-gray-600 dark:text-gray-300 space-y-2">\n{parks_html}        </ul>\n'
    injection += f'      </div>\n'
    injection += f'      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n'
    injection += f'        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">Săli & Restaurante</div>\n'
    injection += f'        <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{region_data["venues"]}</p>\n'
    injection += f'      </div>\n'
    injection += f'    </div>\n'
    injection += f'  </div>\n'
    injection += f'</section>\n'
    
    # We will inject right at the end of the file contents to ensure it renders inside the layout.
    # We find if there is a closing </Layout> tag.
    inject_point = content.rfind('</Layout>')
    if inject_point != -1:
        new_content = content[:inject_point] + injection + '\n' + content[inject_point:]
    else:
        new_content = content + injection
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    injected_count += 1

print(f"Successfully force-injected V2 utilitarian local data into {injected_count} Hub pages.")
