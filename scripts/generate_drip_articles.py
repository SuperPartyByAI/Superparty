import os
import json
import random
from datetime import datetime, timedelta

# Load local db for mapping
db_path = r'C:\Users\ursac\Superparty\scripts\local_db.json'
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

regions = db['regions']
# Filter only actual localities, exclude generic 'bucuresti' or 'ilfov' if we just want strict neighborhoods/areas
# Actually, the regions dictionary contains keys like 'sector-1', 'voluntari', etc.
area_keys = list(regions.keys())

# Define variables for generation
characters = [
    {"name": "Spider-Man", "type": "băieți", "slug": "spiderman"},
    {"name": "Batman", "type": "băieți", "slug": "batman"},
    {"name": "Elsa", "type": "fete", "slug": "elsa"},
    {"name": "Wednesday", "type": "fete", "slug": "wednesday"},
    {"name": "Mickey Mouse", "type": "botez", "slug": "mickey_mouse"},
    {"name": "Ariel", "type": "fete", "slug": "mica_sirena"},
    {"name": "Sonic", "type": "băieți", "slug": "sonic"},
    {"name": "Eroii în Pijama", "type": "mixt", "slug": "eroi_in_pijama"}
]

ages = ["1-3 ani", "4-6 ani", "7-10 ani"]

intros = [
    "Dacă ești în căutarea celor mai bune idei pentru o petrecere de neuitat în {location}, ai ajuns în locul potrivit.",
    "Organizarea unei zile de naștere în {location} poate fi o provocare pentru orice părinte, dar cu personajul potrivit totul devine magie.",
    "Bucuria de a vedea zâmbetul copilului tău este neprețuită. Descoperă cum poți aduce atmosfera de poveste direct în {location}.",
    "Când vine vorba de divertisment pentru copii în {location}, echipa noastră are rețeta succesului garantat.",
    "Fie că locuiești la casă sau la bloc în {location}, o petrecere bine structurată face diferența între haos și magie absolută."
]

bodies = [
    "Alegerea personajului {character} este ideală pentru grupa de vârstă {age}. Jocurile sunt perfect adaptate pentru energia lor debordantă. Pe lângă asta, știm că în {location} spațiile de joacă variază, dar animatorii noștri se adaptează oricărui living sau curte.",
    "Fiecare detaliu contează, de la decorul cu baloane până la intrarea spectaculoasă a lui {character}. Părinții din {location} ne-au transmis deja că atenția noastră la detalii face ca fiecare eveniment pentru vârsta de {age} să iasă ireproșabil.",
    "Bucură-te de energia lui {character} chiar în confortul casei tale din {location}. Copiii de {age} sunt la vârsta la care jocurile interactive, muzica antrenantă și surprizele construiesc cele mai puternice amintiri."
]

tips = [
    "Traficul din zona ta adesea nu este o problemă pentru logistica noastră: {logistics}",
    "Dacă vrei să ieși cu copiii în aer liber, îți recomandăm aceste locații: {parks}",
    "Alternativ, dacă preferi un spațiu indoor sau o curte de restaurant, știm că aceste opțiuni sunt ideale: {venues}"
]

faqs = [
    [
        {"q": "Putem organiza petrecerea cu {character} într-un apartament?", "a": "Sigur! Jocurile sunt perfect adaptabile spațiilor restrânse fără a compromite distracția."},
        {"q": "Animatorul vine echipat cu boxă pentru muzică?", "a": "Da, toți animatorii noștri aduc sisteme de sunet portabile pentru coregrafii și jocuri muzicale."},
        {"q": "Se asigură și modelaj de baloane?", "a": "Evident. La finalul programului, {character} va modela săbii, floricele sau animale pentru fiecare invitat."}
    ],
    [
        {"q": "Care este durata ideală a petrecerii pentru grupa {age}?", "a": "Pentru vârstele de {age}, un interval de 1.5 - 2 ore de animație este perfect pentru a capta atenția completă a prichindeilor."},
        {"q": "Realizați pictură pe față?", "a": "Avem truse de face painting hipoalergenice și transformăm copiii în eroii lor preferați."},
        {"q": "Ne ajutați la aducerea tortului?", "a": "Momentul tortului este condus de {character}, care adună copiii și cântă `La mulți ani`."}
    ]
]

output_dir = r"C:\Users\ursac\Superparty\src\content\blog"
os.makedirs(output_dir, exist_ok=True)

start_date = datetime(2026, 3, 18) # Start drip feeding tomorrow
days_offset = 0
articles_generated = 0

print("Generating articles...")

for i in range(70):
    # Select random combo
    region_key = random.choice(area_keys)
    character = random.choice(characters)
    age = random.choice(ages)
    
    loc_data = regions.get(region_key, {})
    loc_title_name = region_key.replace("-", " ").title()
    
    # Calculate Date (Drip Feed 2-3 a day)
    if articles_generated % 2 == 0 and articles_generated > 0:
        days_offset += 1
    
    pub_date = start_date + timedelta(days=days_offset)
    
    slug = f"petrecere-{character['slug']}-copii-{region_key}-{i}"
    title = f"Petreceri Copii {loc_title_name}: Organizare perfectă cu {character['name']} pentru {age}"
    description = f"Descoperă cum să organizezi cea mai tare petrecere în {loc_title_name}. Află sfaturi utile, locații și de ce {character['name']} este favorit pentru copiii de {age}."
    
    intro = random.choice(intros).format(location=loc_title_name)
    body = random.choice(bodies).format(character=character['name'], age=age, location=loc_title_name)
    
    logistics = loc_data.get('logistics', 'Ne descurcăm excelent cu parcarea și venim mereu mai devreme.')
    parks = ", ".join(loc_data.get('top_parks', ['Parcul central', 'Spațiile verzi locale']))
    venues = loc_data.get('venues', 'Colaborăm cu toate sălile prietenoase cu copiii.')
    
    tip = random.choice(tips).format(logistics=logistics, parks=parks, venues=venues)
    
    selected_faq = random.choice(faqs)
    faq_formatted = "[\n"
    for item in selected_faq:
        q = item["q"].format(character=character['name'], age=age)
        a = item["a"].format(character=character['name'], age=age)
        faq_formatted += f"    {{ q: \"{q}\", a: \"{a}\" }},\n"
    faq_formatted += "  ]"

    mdx_content = f"""---
title: "{title}"
description: "{description}"
pubDate: {pub_date.strftime('%Y-%m-%d')}
heroImage: "https://www.superparty.ro/hero2.jpg"
author: "Echipa Superparty"
tags: ["{loc_title_name}", "{character['type'].title()}"]
---

import ServiceLinkCard from '../../components/blog/ServiceLinkCard.astro';
import FAQ from '../../components/blog/FAQ.astro';

{intro}

## Dinamica Petrecerii pentru {age}

{body}

### Sfaturi Locale pentru Părinții din {loc_title_name}

{tip}

O petrecere reușită înseamnă atenție la detalii. Echipa noastră cunoaște specificul zonei {loc_title_name} și te scutește de efortul organizatoric.

<ServiceLinkCard 
  title="Rezervă {character['name']} în {loc_title_name}" 
  description="Divertisment premium direct la locația ta din {loc_title_name}. Click aici pentru a vedea serviciile noastre oferite în această zonă!"
  href="/animatori-copii-{region_key}/" 
  image="https://www.superparty.ro/hero1.jpg"
/>

<ServiceLinkCard 
  title="Animatori {character['name']} - Detalii și Tarife" 
  description="Află totul despre momentele magice pe care le construim alături de personajul preferat al copilului tău."
  href="/petreceri/animatori-petreceri-copii-{character['slug']}-bucuresti/" 
  image="https://www.superparty.ro/hero2.jpg"
/>

<FAQ 
  title="Întrebări Frecvente organizare {loc_title_name}"
  items={{{faq_formatted}}}
/>
"""
    
    file_path = os.path.join(output_dir, f"{slug}.mdx")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(mdx_content)
        
    articles_generated += 1

print(f"✅ Generated {articles_generated} SEO articles with Drip-Feeding logic.")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {pub_date.strftime('%Y-%m-%d')}")
