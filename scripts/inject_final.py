import os, glob, re

logistics_data = {
    'sector-1': {
        'parks': 'Parcul Herăstrău (zona Roata Mare), Parcul Kiseleff (zona foișoare), Parcul Regina Maria',
        'log': 'Traficul din zona de nord poate fi aglomerat vineri seara, însă animatorii noștri alocă mereu 30 de minute marjă de eroare. Pentru zonele Băneasa și Aviației, găsirea parcării este inclusă în logistica noastră, fără stres pentru tine.',
        'ven': 'Colaborăm excelent cu sălile de joacă din zona Floreasca și restaurantele cu terasă din Herăstrău.'
    },
    'sector-2': {
        'parks': 'Parcul Tei (zona roții), Parcul Plumbuita, Parcul Național',
        'log': 'Acoperim rapid axa Ștefan cel Mare - Colentina. Nu solicităm loc de parcare asigurat la scara blocului pentru show-urile de apartament din Sectorul 2.',
        'ven': 'Avem o colaborare strânsă cu locațiile de evenimente pentru copii din zona Iancului și Vatra Luminoasă.'
    },
    'sector-3': {
        'parks': 'Parcul IOR (Insula Pensionarilor), Parcul Titan, Parcul Pantelimon',
        'log': 'Bulevardele largi din Titan și Dristor ne permit să ajungem la fix în 99% din cazuri. Venim cu recuzita pregătită direct din mașină, gata de show la ușa ta.',
        'ven': 'Recomandăm cu căldură spațiile de joacă indoor din mall-urile locale și sălile din zona Decebal.'
    },
    'sector-4': {
        'parks': 'Parcul Tineretului, Parcul Lumea Copiilor, Parcul Tudor Arghezi',
        'log': 'Pentru zona Berceni și Apărătorii Patriei, logistica este simplificată. Dacă petrecerea este în Parcul Lumea Copiilor, punctele de întâlnire sunt mereu clare și stabilite în prealabil.',
        'ven': 'Dacă plouă, vă recomandăm trecerea spre locurile de joacă partenere din zona Brâncoveanu.'
    },
    'sector-5': {
        'parks': 'Parcul Izvor, Parcul Sebastian, Parcul Romniceanu',
        'log': 'În zonele Cotroceni sau 13 Septembrie, animatorii noștri se descurcă excelent cu descărcarea recuzitei (boxă, baloane) fără a bloca traficul străduțelor înguste.',
        'ven': 'Colaborăm fluid cu grădinile de vară și restaurantele family-friendly din Rahova și panduri.'
    },
    'sector-6': {
        'parks': 'Parcul Drumul Taberei (Moghioroș), Parcul Crângași, Liniei',
        'log': 'Știm că Militari Residence sau Prelungirea Ghencea necesită planificare la ore de vârf. Deplasarea echipei noastre este mereu calibrată după Waze, pentru a nu întârzia tăierea tortului.',
        'ven': 'Sălile de petreceri din Drumul Taberei și mall-urile din vestul Capitalei sunt destinații noastre zilnice.'
    },
    'voluntari': {
        'parks': 'Pădurea Băneasa, Parcurile Ansamblurilor Rezidențiale, Grădina proprie',
        'log': 'Pentru Voluntari și Pipera, deplasarea cu auto propriu a animatorilor este standard. Curțile mari permit o instalare rapidă a mașinii de baloane de săpun direct la destinație.',
        'ven': 'Dacă doriți un eveniment premium, vă putem sugera locații exclusiviste de tip mansion sau clubhouse din ansamblurile locale.'
    },
    'corbeanca': {
        'parks': 'Zonele împădurite, Parcul central Corbeanca, Terenurile de sport',
        'log': 'Aerul curat din Corbeanca este perfect! Traseul din București spre Corbeanca este mereu calculat în avans de echipa noastră pe DN1 pentru a sosi cu 15 minute înainte de machiaj.',
        'ven': 'Cele mai multe petreceri le realizăm direct în curțile spectaculoase ale clienților noștri, dar cunoaștem și restaurantele locale.'
    },
    'otopeni': {
        'parks': 'Parcul Central Otopeni, Zonele verzi adiacente, Baze sportive',
        'log': 'Accesul din DN1 face ca Otopeniul să fie o destinație rapidă pentru noi. Aduceți tortul, de atmosfera muzicală și energia pozitivă ne ocupăm noi.',
        'ven': 'Sălile de sport transformate și centrele educaționale din Otopeni sunt spații pe care le folosim frecvent.'
    },
    'popesti-leordeni': {
        'parks': 'Parcul central Popești, Locurile de joacă din rezidențiale, Zonele verzi de sud',
        'log': 'Infrastructura nouă din Popești-Leordeni este provocatoare uneori, însă echipa Superparty are experiența de a naviga eficient pentru a fi prezenți la Super-Petrecerea copilului tău.',
        'ven': 'Zonele de party indoor din clădirile noi sunt perfecte iarna pentru modelajul de baloane și face painting.'
    },
    'bragadiru': {
        'parks': 'Parcul Bragadiru, Zonele Cartierului Latin, Spațiile noi amenajate',
        'log': 'Garantăm prezența în Bragadiru fără stres. Ne organizăm transportul recuzitei astfel încât jocurile să înceapă fix la ora bătută în cuie.',
        'ven': 'Fie că e acasă în living sau la un restaurant de pe Șoseaua Alexandriei, adaptăm programul pentru distracție maximă.'
    },
    'chiajna': {
        'parks': 'Promenada Lacul Morii, Parcurile din Militari Residence, Spațiile publice Dudu',
        'log': 'Pentru Chiajna și Dudu, aglomerația nu ne oprește. Animatorii ajung costumați (sau se schimbă rapid la locație) pentru a păstra surpriza intactă pentru cel mic.',
        'ven': 'Colaborăm excelent cu locurile de joacă mari din incinta complexelor rezidențiale din toată zona de vest.'
    },
    'pantelimon': {
        'parks': 'Pădurea Pustnicu, Zona Cernica, Parcul Pantelimon',
        'log': 'Ieșirea spre Pantelimon/Cernica este ideală în weekend. Logistica pentru ieșiri la iarbă verde include boxă portabilă cu acumulator puternic, perfectă pentru lipsa prizelor.',
        'ven': 'Restaurantele de pe malul lacului Cernica sunt locații premium unde avem acces și experiență în organizare.'
    }
}

base_pages = r'C:\Users\ursac\Superparty\src\pages'
astro_files = glob.glob(os.path.join(base_pages, 'animatori-copii-*', 'index.astro'))
count = 0

for f in astro_files:
    reg = os.path.basename(os.path.dirname(f)).replace('animatori-copii-', '')
    if reg not in logistics_data: continue

    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    # strip old injection if it exists
    content = re.sub(r'<!--\s*LOCAL_HUB_UTIL_INJECT\s*-->.*?(?=(</Layout>|\Z))', '', content, flags=re.DOTALL)
    
    d = logistics_data[reg]
    parks = "".join([f'<li class="flex items-start"><span class="text-purple-500 mr-2">✓</span><span>{p.strip()}</span></li>' for p in d['parks'].split(',')])
    
    inj = f'\n<!-- LOCAL_HUB_UTIL_INJECT -->\n<section class="py-12 bg-gray-50 dark:bg-gray-800/50">\n  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">\n    <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">Ghid Utilitar: Petreceri în {reg.replace("-", " ").title()}</h3>\n    <div class="grid md:grid-cols-3 gap-8">\n      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">Logistică & Deplasare</div>\n        <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{d["log"]}</p>\n      </div>\n      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">Top Parcuri Recomandate</div>\n        <ul class="text-sm text-gray-600 dark:text-gray-300 space-y-2">\n{parks}        </ul>\n      </div>\n      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">\n        <div class="text-purple-600 dark:text-purple-400 font-semibold mb-3 flex items-center">Săli & Restaurante</div>\n        <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{d["ven"]}</p>\n      </div>\n    </div>\n  </div>\n</section>\n'
    
    idx = content.rfind('</Layout>')
    if idx != -1:
        content = content[:idx] + inj + content[idx:]
    else:
        content += inj
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
    count += 1
print(f'Done: {count}')
