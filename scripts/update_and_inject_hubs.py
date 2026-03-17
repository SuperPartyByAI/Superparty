import os
import glob
import json

db_path = r'C:\Users\ursac\Superparty\scripts\local_db.json'
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

regions = db['regions']
reviews = db['reviews']

# Add high-intent logistical data to regions
logistics_data = {
    'sector-1': {
        'top_parks': ['Parcul Herăstrău (zona Roata Mare)', 'Parcul Kiseleff (zona foișoare)', 'Parcul Regina Maria'],
        'logistics': 'Traficul din zona de nord poate fi aglomerat vineri seara, însă animatorii noștri alocă mereu 30 de minute marjă de eroare. Pentru zonele Băneasa și Aviației, găsirea parcării este inclusă în logistica noastră, fără stres pentru tine.',
        'venues': 'Colaborăm excelent cu sălile de joacă din zona Floreasca și restaurantele cu terasă din Herăstrău.'
    },
    'sector-2': {
        'top_parks': ['Parcul Tei (zona roții)', 'Parcul Plumbuita', 'Parcul Național'],
        'logistics': 'Acoperim rapid axa Ștefan cel Mare - Colentina. Nu solicităm loc de parcare asigurat la scara blocului pentru show-urile de apartament din Sectorul 2.',
        'venues': 'Avem o colaborare strânsă cu locațiile de evenimente pentru copii din zona Iancului și Vatra Luminoasă.'
    },
    'sector-3': {
        'top_parks': ['Parcul IOR (Insula Pensionarilor)', 'Parcul Titan', 'Parcul Pantelimon'],
        'logistics': 'Bulevardele largi din Titan și Dristor ne permit să ajungem la fix în 99% din cazuri. Venim cu recuzita pregătită direct din mașină, gata de show la ușa ta.',
        'venues': 'Recomandăm cu căldură spațiile de joacă indoor din mall-urile locale și sălile din zona Decebal.'
    },
    'sector-4': {
        'top_parks': ['Parcul Tineretului', 'Parcul Lumea Copiilor', 'Parcul Tudor Arghezi'],
        'logistics': 'Pentru zona Berceni și Apărătorii Patriei, logistica este simplificată. Dacă petrecerea este în Parcul Lumea Copiilor, punctele de întâlnire sunt mereu clare și stabilite în prealabil.',
        'venues': 'Dacă plouă, vă recomandăm trecerea spre locurile de joacă partenere din zona Brâncoveanu.'
    },
    'sector-5': {
        'top_parks': ['Parcul Izvor', 'Parcul Sebastian', 'Parcul Romniceanu'],
        'logistics': 'În zonele Cotroceni sau 13 Septembrie, animatorii noștri se descurcă excelent cu descărcarea recuzitei (boxă, baloane) fără a bloca traficul străduțelor înguste.',
        'venues': 'Colaborăm fluid cu grădinile de vară și restaurantele family-friendly din Rahova și panduri.'
    },
    'sector-6': {
        'top_parks': ['Parcul Drumul Taberei (Moghioroș)', 'Parcul Crângași', 'Liniei'],
        'logistics': 'Știm că Militari Residence sau Prelungirea Ghencea necesită planificare la ore de vârf. Deplasarea echipei noastre este mereu calibrată după Waze, pentru a nu întârzia tăierea tortului.',
        'venues': 'Sălile de petreceri din Drumul Taberei și mall-urile din vestul Capitalei sunt destinații noastre zilnice.'
    },
    'voluntari': {
        'top_parks': ['Pădurea Băneasa', 'Parcurile Ansamblurilor Rezidențiale', 'Grădina proprie'],
        'logistics': 'Pentru Voluntari și Pipera, deplasarea cu auto propriu a animatorilor este standard. Curțile mari permit o instalare rapidă a mașinii de baloane de săpun direct la destinație.',
        'venues': 'Dacă doriți un eveniment premium, vă putem sugera locații exclusiviste de tip mansion sau clubhouse din ansamblurile locale.'
    },
    'corbeanca': {
        'top_parks': ['Zonele împădurite', 'Parcul central Corbeanca', 'Terenurile de sport'],
        'logistics': 'Aerul curat din Corbeanca este perfect! Traseul din București spre Corbeanca este mereu calculat în avans de echipa noastră pe DN1 pentru a sosi cu 15 minute înainte de machiaj.',
        'venues': 'Cele mai multe petreceri le realizăm direct în curțile spectaculoase ale clienților noștri, dar cunoaștem și restaurantele locale.'
    },
    'otopeni': {
        'top_parks': ['Parcul Central Otopeni', 'Zonele verzi adiacente', 'Baze sportive'],
        'logistics': 'Accesul din DN1 face ca Otopeniul să fie o destinație rapidă pentru noi. Aduceți tortul, de atmosfera muzicală și energia pozitivă ne ocupăm noi.',
        'venues': 'Sălile de sport transformate și centrele educaționale din Otopeni sunt spații pe care le folosim frecvent.'
    },
    'popesti-leordeni': {
        'top_parks': ['Parcul central Popești', 'Locurile de joacă din rezidențiale', 'Zonele verzi de sud'],
        'logistics': 'Infrastructura nouă din Popești-Leordeni este provocatoare uneori, însă echipa Superparty are experiența de a naviga eficient pentru a fi prezenți la Super-Petrecerea copilului tău.',
        'venues': 'Zonele de party indoor din clădirile noi sunt perfecte iarna pentru modelajul de baloane și face painting.'
    },
    'bragadiru': {
        'top_parks': ['Parcul Bragadiru', 'Zonele Cartierului Latin', 'Spațiile noi amenajate'],
        'logistics': 'Garantăm prezența în Bragadiru fără stres. Ne organizăm transportul recuzitei astfel încât jocurile să înceapă fix la ora bătută în cuie.',
        'venues': 'Fie că e acasă în living sau la un restaurant de pe Șoseaua Alexandriei, adaptăm programul pentru distracție maximă.'
    },
    'chiajna': {
        'top_parks': ['Promenada Lacul Morii', 'Parcurile din Militari Residence', 'Spațiile publice Dudu'],
        'logistics': 'Pentru Chiajna și Dudu, aglomerația nu ne oprește. Animatorii ajung costumați (sau se schimbă rapid la locație) pentru a păstra surpriza intactă pentru cel mic.',
        'venues': 'Colaborăm excelent cu locurile de joacă mari din incinta complexelor rezidențiale din toată zona de vest.'
    },
    'pantelimon': {
        'top_parks': ['Pădurea Pustnicu', 'Zona Cernica', 'Parcul Pantelimon'],
        'logistics': 'Ieșirea spre Pantelimon/Cernica este ideală în weekend. Logistica pentru ieșiri la iarbă verde include boxă portabilă cu acumulator puternic, perfectă pentru lipsa prizelor.',
        'venues': 'Restaurantele de pe malul lacului Cernica sunt locații premium unde avem acces și experiență în organizare.'
    }
}

for k, v in logistics_data.items():
    if k in regions:
        regions[k].update(v)

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

    # Prevent double injection
    if MARKER in content:
        continue

    region_data = regions[region_key]
    
    # Check if we successfully added logistics data to this region
    if 'logistics' not in region_data:
        continue

    parks_html = "".join([f"<li class=\"flex items-start\"><span class=\"text-purple-500 mr-2\">✓</span><span>{p}</span></li>" for p in region_data['top_parks']])
    
    injection = f'\n\n{MARKER}\n'
    injection += f'<section class="py-12 bg-gray-50 dark:bg-gray-800/50">\n'
    injection += f'  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">\n'
    injection += f'    <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">Ghid Utilitar: Petreceri în {region_key.replace("-", " ").title()}</h3>\n'
    injection += f'    <div class="grid md:grid-cols-3 gap-8">\n'
    
    # Box 1: Logistics
    injection += f'      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n'
    injection += f'        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center"><svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg> Logistică & Deplasare</div>\n'
    injection += f'        <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{region_data["logistics"]}</p>\n'
    injection += f'      </div>\n'
    
    # Box 2: Parks
    injection += f'      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n'
    injection += f'        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center"><svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path></svg> Top 3 Parcuri Recomandate</div>\n'
    injection += f'        <ul class="text-sm text-gray-600 dark:text-gray-300 space-y-2">\n{parks_html}\n        </ul>\n'
    injection += f'      </div>\n'
    
    # Box 3: Venues
    injection += f'      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n'
    injection += f'        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center"><svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg> Săli & Restaurante</div>\n'
    injection += f'        <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{region_data["venues"]}</p>\n'
    injection += f'      </div>\n'
    
    injection += f'    </div>\n'
    injection += f'  </div>\n'
    injection += f'</section>\n'
    
    # Inject after the previous injection or before footer
    inject_point = content.rfind('<!-- LOCAL_HUB_INJECT_V2_END -->')
    if inject_point != -1:
        # Insert right after the previous local block
        inject_point += len('<!-- LOCAL_HUB_INJECT_V2_END -->')
        new_content = content[:inject_point] + injection + content[inject_point:]
    else:
        # Fallback to before footer
        inject_point = content.rfind('<Footer')
        if inject_point == -1:
            new_content = content + injection
        else:
            new_content = content[:inject_point] + injection + '\n' + content[inject_point:]
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    injected_count += 1

print(f"Successfully injected utility and logistics data into {injected_count} Hub pages.")
