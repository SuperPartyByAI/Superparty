import os, glob

base_pages = r'C:\Users\ursac\Superparty\src\pages'
astro_files = glob.glob(os.path.join(base_pages, 'animatori-copii-*', 'index.astro'))

count = 0
for f in astro_files:
    reg = os.path.basename(os.path.dirname(f)).replace('animatori-copii-', '')
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'Experiență Locală Verificată' in content:
        continue
        
    extra_box = f'\n      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">Experiență Locală Verificată</div>\n        <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">Echipa Superparty a susținut nenumărate evenimente în zona {reg.replace("-", " ").title()}. Cunoaștem specificul grădinițelor și afterschool-urilor locale, iar animatorii noștri își adaptează mereu spectacolul în funcție de suprafața disponibilă (fie că e apartament, cort sau curte deschisă).</p>\n      </div>\n'
    
    idx = content.find('    </div>\n  </div>\n</section>')
    if idx != -1:
        content = content[:idx] + extra_box + content[idx:]
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        count += 1

print(f'Added 4th util box to {count} files.')
