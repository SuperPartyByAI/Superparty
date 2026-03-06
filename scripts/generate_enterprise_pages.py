import os
from pathlib import Path
REPO_ROOT = str(Path(__file__).resolve().parents[1])
"""
Enterprise SEO Generator — SuperParty.ro
Generează:
1) 6 hub-uri județene (Prahova, Dâmbovița, Giurgiu, Ialomița, Călărași, Teleorman)
2) Tier 3 scoring + top 60 pagini localități mari
3) indexing_manifest.json
"""
import os, json, csv, re, unicodedata
from collections import defaultdict

PAGES_DIR = r"os.path.join(REPO_ROOT, "src", "pages", "petreceri")"
REPORTS_DIR = r"os.path.join(REPO_ROOT, "reports", "seo")"
os.makedirs(REPORTS_DIR, exist_ok=True)

CANONICAL_HOST = "https://www.superparty.ro"
TEL = "tel:+40722744377"
WA = "https://wa.me/40722744377?text=Salut%21%20Vreau%20o%20ofert%C4%83%20pentru%20animatori%20petrecere%20copii.%20Data%3A%20____%20Loca%C8%9Bie%3A%20____%20V%C3%A2rst%C4%83%3A%20____%20Nr.%20copii%3A%20____"

def slugify(text):
    text = text.lower().strip()
    for ro, en in {'ă':'a','â':'a','î':'i','ș':'s','ş':'s','ț':'t','ţ':'t'}.items():
        text = text.replace(ro, en)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii','ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

# ============================================================
# 1) HUB-URI JUDEȚENE
# ============================================================
JUDETE = {
    "prahova": {
        "judet": "Prahova",
        "h1": "Județul Prahova",
        "slug": "prahova",
        "dist": "~55–100 km",
        "intro": "Animatorii SuperParty ajung și în județul Prahova — Ploiești, Câmpina, Sinaia, Băicoi, Breaza și alte localități. Distanța de la București nu e o problemă; aducem magia la petrecerea copilului tău.",
        "desc": "Animatori profesioniști pentru petreceri copii în județul Prahova — Ploiești, Câmpina, Sinaia. Costume premium. Rezervă: 0722 744 377.",
        "localitati": ["Ploiești", "Câmpina", "Sinaia", "Băicoi", "Breaza", "Comarnic", "Bușteni", "Urlați", "Mizil", "Boldești-Scăeni"],
        "faq": [
            ("Activați în Ploiești?", "Da — Ploiești este la ~55 km de București. Contactați-ne pentru detalii despre deplasare și taxa aferentă."),
            ("Există taxă de deplasare pentru Prahova?", "Da — pentru localitățile din Prahova se aplică o taxă de deplasare calculată în funcție de distanță. Contactați-ne pentru ofertă completă."),
            ("Activați și la munte (Sinaia, Bușteni)?", "Da — acoperim și stațiunile montane prahovene. Contactați-ne pentru disponibilitate și condiții specifice."),
        ]
    },
    "dambovita": {
        "judet": "Dâmbovița",
        "h1": "Județul Dâmbovița",
        "slug": "dambovita",
        "dist": "~40–90 km",
        "intro": "SuperParty acoperă și județul Dâmbovița — Târgoviște, Titu, Răcari, Găești și alte comune. Dacă organizați o petrecere în Dâmbovița, suntem la un apel distanță.",
        "desc": "Animatori profesioniști pentru petreceri copii în județul Dâmbovița — Târgoviște, Titu, Găești. Costume premium. Rezervă: 0722 744 377.",
        "localitati": ["Târgoviște", "Titu", "Găești", "Răcari", "Moreni", "Pucioasa", "Fieni", "Doicești", "Ghimpați", "Cojasca"],
        "faq": [
            ("Activați în Târgoviște?", "Da — Târgoviște este la ~80 km de București. Contactați-ne pentru confirmare și taxa de deplasare."),
            ("Activați și în comunele din Dâmbovița?", "Da — acoperim și comunele din județul Dâmbovița aflate în raza de ~100 km de București."),
            ("Care este taxa de deplasare pentru Dâmbovița?", "Taxa variază în funcție de locație. Contactați-ne cu adresa exactă pentru o ofertă completă."),
        ]
    },
    "giurgiu": {
        "judet": "Giurgiu",
        "h1": "Județul Giurgiu",
        "slug": "giurgiu",
        "dist": "~35–70 km",
        "intro": "Animatorii SuperParty activează și în județul Giurgiu — Mihăilești, Bolintin-Vale, Giurgiu și alte localități la sud de București. Venim la petrecerea copilului tău oriunde în zonă.",
        "desc": "Animatori profesioniști pentru petreceri copii în județul Giurgiu — Giurgiu, Mihăilești, Bolintin-Vale. Costume premium. Rezervă: 0722 744 377.",
        "localitati": ["Giurgiu", "Mihăilești", "Bolintin-Vale", "Comana", "Frătești", "Crevedia Mare", "Iepurești", "Hotarele", "Stoenești"],
        "faq": [
            ("Activați în municipiul Giurgiu?", "Da — Giurgiu este la ~65 km de București. Contactați-ne pentru confirmare și condiții de deplasare."),
            ("Activați în Mihăilești sau Bolintin-Vale?", "Da — acestea sunt la 35–50 km de București și sunt în raza noastră de acoperire."),
            ("Există taxă de deplasare pentru Giurgiu?", "Da — pentru localitățile mai îndepărtate se aplică o taxă de deplasare. Contactați-ne pentru detalii."),
        ]
    },
    "ialomita": {
        "judet": "Ialomița",
        "h1": "Județul Ialomița",
        "slug": "ialomita",
        "dist": "~60–100 km",
        "intro": "SuperParty ajunge și în județul Ialomița — Urziceni, Slobozia, Fetești, Amara și alte localități la est de București. Contactați-ne pentru disponibilitate și condiții specifice.",
        "desc": "Animatori profesioniști pentru petreceri copii în județul Ialomița — Urziceni, Slobozia, Fetești. Costume premium. Rezervă: 0722 744 377.",
        "localitati": ["Urziceni", "Slobozia", "Fetești", "Amara", "Țăndărei", "Fierbinți-Târg", "Dridu", "Grindu", "Reviga", "Căzănești"],
        "faq": [
            ("Activați în Urziceni?", "Da — Urziceni este la ~65 km de București. Contactați-ne pentru confirmare și condiții."),
            ("Activați în Slobozia sau Fetești?", "Da — aceste localități sunt la limita razei noastre de ~100 km. Contactați-ne pentru disponibilitate."),
            ("Există taxă de deplasare pentru Ialomița?", "Da — pentru Ialomița se aplică o taxă de deplasare. Vă comunicăm suma exactă la rezervare."),
        ]
    },
    "calarasi": {
        "judet": "Călărași",
        "h1": "Județul Călărași",
        "slug": "calarasi",
        "dist": "~45–100 km",
        "intro": "Animatorii SuperParty acoperă și județul Călărași — Oltenița, Budești, Fundulea, Lehliu-Gară și alte localități la est și sud-est de București.",
        "desc": "Animatori profesioniști pentru petreceri copii în județul Călărași — Oltenița, Fundulea, Lehliu-Gară. Costume premium. Rezervă: 0722 744 377.",
        "localitati": ["Oltenița", "Fundulea", "Budești", "Lehliu-Gară", "Belciugatele", "Ștefan Vodă", "Căscioarele", "Frumușani", "Nana"],
        "faq": [
            ("Activați în Oltenița?", "Da — Oltenița este la ~65 km de București. Contactați-ne pentru confirmare și condiții de deplasare."),
            ("Activați în Fundulea sau Budești?", "Da — acestea sunt la 48–52 km de București, în raza noastră standard."),
            ("Există taxă de deplasare pentru Călărași?", "Da — taxa variază cu distanța. Contactați-ne cu adresa exactă pentru ofertă completă."),
        ]
    },
    "teleorman": {
        "judet": "Teleorman",
        "h1": "Județul Teleorman",
        "slug": "teleorman",
        "dist": "~55–100 km",
        "intro": "SuperParty ajunge și în judetul Teleorman — Videle, Roșiorii de Vede, Alexandria și alte localități la sud-vest de București. Pentru petreceri în Teleorman, contactați-ne în avans.",
        "desc": "Animatori profesioniști pentru petreceri copii în județul Teleorman — Videle, Alexandria, Roșiorii de Vede. Costume premium. Rezervă: 0722 744 377.",
        "localitati": ["Videle", "Alexandria", "Roșiorii de Vede", "Zimnicea", "Turnu Măgurele", "Caracal", "Draganesti-Vlasca"],
        "faq": [
            ("Activați în Videle sau Alexandria?", "Da — Videle este la ~60 km, iar Alexandria la ~95 km de București. Contactați-ne pentru detalii."),
            ("Există taxă de deplasare pentru Teleorman?", "Da — pentru Teleorman se aplică o taxă de deplasare. Contactați-ne pentru ofertă."),
            ("Activați și în comunele din Teleorman?", "Da — la cerere și cu programare în avans, acoperim și comune din județul Teleorman."),
        ]
    },
}

def judet_template(data):
    slug = data["slug"]
    judet = data["judet"]
    h1 = data["h1"]
    intro = data["intro"]
    desc = data["desc"]
    dist = data["dist"]
    localitati = data["localitati"]
    faq = data["faq"]

    # Build FAQ JSON (valid)
    faq_entities = []
    for q, a in faq:
        q_safe = q.replace('"', '\\"')
        a_safe = a.replace('"', '\\"')
        faq_entities.append(f'        {{"@type": "Question", "name": "{q_safe}", "acceptedAnswer": {{"@type": "Answer", "text": "{a_safe}"}}}}')
    faq_json = ',\n'.join(faq_entities)

    loc_links = "\n".join([f'              <li>📍 {loc}</li>' for loc in localitati])

    return f'''---
import Layout from '../../layouts/Layout.astro';
import {{ getCollection }} from 'astro:content';

const allArticles = await getCollection('seo-articles');
const hubArticles = allArticles.filter(a =>
  a.slug.includes('{slug}') && a.data.indexStatus !== 'hold'
).slice(0, 12);

const schema = JSON.stringify({{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Service",
      "name": "Animatori Petreceri Copii {h1}",
      "provider": {{ "@type": "LocalBusiness", "name": "SuperParty", "telephone": "+40722744377" }},
      "areaServed": "{h1}",
      "url": "{CANONICAL_HOST}/petreceri/{slug}"
    }},
    {{
      "@type": "FAQPage",
      "mainEntity": [
{faq_json}
      ]
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{ "@type": "ListItem", "position": 1, "name": "Acasă", "item": "{CANONICAL_HOST}" }},
        {{ "@type": "ListItem", "position": 2, "name": "Animatori Petreceri Copii", "item": "{CANONICAL_HOST}/animatori-petreceri-copii" }},
        {{ "@type": "ListItem", "position": 3, "name": "{h1}", "item": "{CANONICAL_HOST}/petreceri/{slug}" }}
      ]
    }}
  ]
}});
---

<Layout
  title="Animatori Petreceri Copii {h1} | SuperParty"
  description="{desc}"
  canonical="{CANONICAL_HOST}/petreceri/{slug}"
  robots="index, follow"
  schema={{schema}}
>
<style>
  .hub-hero {{ padding:4.5rem 0 3rem; background:radial-gradient(ellipse at top,rgba(255,107,53,.1) 0%,transparent 55%); }}
  .hub-hero h1 {{ font-size:clamp(1.8rem,4vw,2.8rem); font-weight:800; margin-bottom:1rem; line-height:1.2; }}
  .hub-hero p {{ color:var(--text-muted); font-size:1.05rem; max-width:620px; line-height:1.8; margin-bottom:2rem; }}
  .btn-p {{ background:linear-gradient(135deg,var(--primary),var(--primary-dark)); color:#fff; padding:.9rem 2rem; border-radius:50px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:.5rem; transition:transform .2s; }}
  .btn-p:hover {{ transform:translateY(-2px); }}
  .btn-wa {{ background:#25d366; color:#fff; padding:.9rem 1.8rem; border-radius:50px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:.5rem; }}
  .hub-s {{ padding:3.5rem 0; }} .hub-s-alt {{ padding:3.5rem 0; background:var(--dark-2); }}
  .sec-title {{ font-size:1.6rem; font-weight:800; margin-bottom:.5rem; }}
  .sec-sub {{ color:var(--text-muted); margin-bottom:2rem; }}
  .info-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:1.5rem; }}
  .info-card {{ background:var(--dark-3); border:1px solid rgba(255,107,53,.15); border-radius:14px; padding:1.5rem; }}
  .info-card h3 {{ font-weight:700; margin-bottom:.6rem; }}
  .info-card ul {{ list-style:none; padding:0; }}
  .info-card li {{ padding:.3rem 0; border-bottom:1px solid rgba(255,255,255,.05); font-size:.9rem; color:var(--text-muted); }}
  .faq-list {{ display:flex; flex-direction:column; gap:1rem; max-width:720px; }}
  .faq-item {{ background:var(--dark-3); border:1px solid rgba(255,107,53,.12); border-radius:14px; padding:1.3rem; }}
  .faq-item h3 {{ font-size:.95rem; font-weight:700; margin-bottom:.5rem; }}
  .faq-item p {{ font-size:.9rem; color:var(--text-muted); line-height:1.7; }}
  .cta-box {{ background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.05)); border:1px solid rgba(255,107,53,.25); border-radius:20px; padding:3rem 2rem; text-align:center; }}
  .cta-box h2 {{ font-size:1.7rem; font-weight:800; margin-bottom:1rem; }}
  .cta-box p {{ color:var(--text-muted); margin-bottom:2rem; }}
  .cta-btns {{ display:flex; gap:1rem; flex-wrap:wrap; justify-content:center; }}
</style>

<section class="hub-hero">
  <div class="container">
    <h1>Animatori Petreceri Copii<br><span style="color:var(--primary)">{h1}</span></h1>
    <p>{intro}</p>
    <div style="display:flex; gap:1rem; flex-wrap:wrap;">
      <a href="{TEL}" class="btn-p cta">📞 Rezervă: 0722 744 377</a>
      <a href="{WA}" class="btn-wa cta">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section class="hub-s">
  <div class="container">
    <div class="info-grid">
      <div class="info-card">
        <h3>📍 Localități principale {h1}</h3>
        <ul>
{loc_links}
        </ul>
      </div>
      <div class="info-card">
        <h3>⏱ Distanță aproximativă</h3>
        <ul>
          <li>{dist} față de București</li>
          <li>Taxă de deplasare comunicată la rezervare</li>
          <li>Rezervare cu minim 7–14 zile înainte</li>
        </ul>
      </div>
      <div class="info-card">
        <h3>🎭 Pachete disponibile</h3>
        <ul>
          <li>Super 1 — 1 personaj, 2 ore — 490 lei</li>
          <li>Super 3 — 2 personaje, 2 ore + confetti — 840 lei</li>
          <li>Super 7 — 3 ore + spectacol botez — 1290 lei</li>
        </ul>
        <p style="margin-top:.8rem; font-size:.85rem; color:var(--text-muted);">
          <a href="/animatori-petreceri-copii" style="color:var(--primary); font-weight:600;">→ Toate pachetele și prețurile</a>
        </p>
      </div>
    </div>
  </div>
</section>

<section class="hub-s-alt">
  <div class="container">
    <h2 class="sec-title">Întrebări despre {h1}</h2>
    <div class="faq-list">
      {{[
        ["{faq[0][0]}", "{faq[0][1]}"],
        ["{faq[1][0]}", "{faq[1][1]}"],
        ["{faq[2][0]}", "{faq[2][1]}"],
      ].map(([q,a]) => (
        <div class="faq-item">
          <h3>❓ {{q}}</h3>
          <p>{{a}}</p>
        </div>
      ))}}
    </div>
  </div>
</section>

<section class="hub-s">
  <div class="container">
    <div class="cta-box">
      <h2>Rezervă animator în <span style="color:var(--primary)">{h1}</span></h2>
      <p>Contactați-ne cu data și zona exactă — vă confirmăm disponibilitatea și oferta cu taxă de deplasare.</p>
      <div class="cta-btns">
        <a href="{TEL}" class="btn-p cta">📞 0722 744 377</a>
        <a href="{WA}" class="btn-wa cta">💬 WhatsApp</a>
      </div>
      <p style="margin-top:1.5rem; font-size:.9rem; color:var(--text-muted);">
        ← <a href="/animatori-petreceri-copii" style="color:var(--primary); font-weight:600;">Pagina principală Animatori Petreceri Copii</a>
        &nbsp;|&nbsp;
        <a href="/arie-acoperire" style="color:var(--primary);">Toate zonele acoperite →</a>
      </p>
    </div>
  </div>
</section>
</Layout>
'''

# Generează hub-uri județene
generated_judete = []
for slug, data in JUDETE.items():
    content = judet_template(data)
    fpath = os.path.join(PAGES_DIR, f"{slug}.astro")
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    generated_judete.append(slug)
    print(f"✓ Hub județean: {slug}.astro")

# ============================================================
# 2) TIER 3 SCORING — top 60 localități
# ============================================================
print("\n📊 Calculez scoring Tier 3...")

# Citesc CSV OSM
osm_path = r"os.path.join(REPO_ROOT, "reports", "locations", "bucuresti_100km_places.csv")"
osm_data = []
with open(osm_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        osm_data.append(row)

# Citesc lista curată
clean_path = r"os.path.join(REPO_ROOT, "reports", "locations", "locations_100km.json")"
with open(clean_path, 'r', encoding='utf-8') as f:
    clean_list = json.load(f)
clean_slugs = {loc.get("slug","") for loc in clean_list}
clean_names = {loc.get("name","").lower() for loc in clean_list}

# Deja existente în /petreceri/
existing_slugs = set()
for fname in os.listdir(PAGES_DIR):
    if fname.endswith('.astro'):
        existing_slugs.add(fname.replace('.astro',''))

# Zone de prioritate
PRIORITY_COUNTIES   = {"Ilfov", "București"}
PRIORITY_TYPES      = {"city", "town"}
STANDARD_TYPES      = {"village", "hamlet", "locality"}
SKIP_TYPES          = {"neighbourhood", "suburb", "city_block", "quarter"}

scored = []
for row in osm_data:
    place = row.get("place","")
    name  = row.get("name","").strip()
    dist  = float(row.get("dist_km", 999) or 999)
    
    if not name or place in SKIP_TYPES:
        continue
    
    slug = slugify(name)
    if slug in existing_slugs:
        continue  # deja există
    
    # Scoring
    score = 1.0
    
    # County guess from name or proximity
    county_guess = ""
    if dist < 45: county_guess = "Ilfov"  # aproape de Buc = probabil Ilfov
    if dist < 20: county_guess = "Ilfov"
    
    if county_guess in PRIORITY_COUNTIES:
        score *= 5
    if place in PRIORITY_TYPES:
        score *= 2
    if slug in clean_slugs or name.lower() in clean_names:
        score *= 1.5
    if dist < 30:
        score *= 1.5
    elif dist > 80:
        score *= 0.7
    
    # Penalizare dacă slug prea scurt sau problematic
    if len(slug) < 3:
        continue
    
    scored.append({
        "name": name,
        "slug": slug,
        "place": place,
        "dist_km": dist,
        "score": round(score, 2),
        "county_guess": county_guess,
    })

# Sortează descrescător
scored.sort(key=lambda x: -x["score"])

# Top 60 (deduplicat pe slug)
seen_slugs = set()
tier3_candidates = []
for item in scored:
    if item["slug"] not in seen_slugs and len(tier3_candidates) < 60:
        seen_slugs.add(item["slug"])
        tier3_candidates.append(item)

print(f"Tier 3 candidați: {len(tier3_candidates)}")

# ============================================================
# 3) GENERARE PAGINI TIER 3
# ============================================================
def tier3_template(name, slug, place, dist_km, judet_hub="ilfov"):
    place_ro = {"city": "municipiu", "town": "oraș", "village": "comună/sat", "hamlet": "sat"}.get(place, "localitate")
    dist_str = f"~{int(dist_km)} km" if dist_km else "~50 km"

    # FAQ specific
    faq_items = [
        (f"Activați animatori în {name}?", f"Da — acoperim {name} și localitățile învecinate. Contactați-ne cu data și adresa exactă pentru a confirma disponibilitatea."),
        (f"Există taxă de deplasare pentru {name}?", f"Depinde de distanță ({dist_str} de la București). Contactați-ne pentru o ofertă completă inclusiv transport."),
        (f"Unde se poate organiza petrecerea în {name}?", f"La domiciliu, la o sală de petreceri sau alt spațiu din {name} — local, grădiniță, restaurant family-friendly. Avem nevoie de minim 15–20 mp."),
    ]
    faq_entities = ',\n'.join([
        f'        {{"@type":"Question","name":"{q.replace(chr(34), chr(39))}","acceptedAnswer":{{"@type":"Answer","text":"{a.replace(chr(34), chr(39))}"}}}}' 
        for q,a in faq_items
    ])

    return f'''---
import Layout from '../../layouts/Layout.astro';

const schema = JSON.stringify({{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Service",
      "name": "Animatori Petreceri Copii {name}",
      "provider": {{"@type": "LocalBusiness", "name": "SuperParty", "telephone": "+40722744377"}},
      "areaServed": "{name}",
      "url": "{CANONICAL_HOST}/petreceri/{slug}"
    }},
    {{
      "@type": "FAQPage",
      "mainEntity": [
{faq_entities}
      ]
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type":"ListItem","position":1,"name":"Acasă","item":"{CANONICAL_HOST}"}},
        {{"@type":"ListItem","position":2,"name":"Animatori Petreceri Copii","item":"{CANONICAL_HOST}/animatori-petreceri-copii"}},
        {{"@type":"ListItem","position":3,"name":"{name}","item":"{CANONICAL_HOST}/petreceri/{slug}"}}
      ]
    }}
  ]
}});
---

<Layout
  title="Animatori Petreceri Copii {name} | SuperParty"
  description="Animatori profesioniști pentru petreceri copii în {name} ({place_ro}, {dist_str} de București). Costume premium, pachete de la 490 lei. Rezervă: 0722 744 377."
  canonical="{CANONICAL_HOST}/petreceri/{slug}"
  robots="index, follow"
  schema={{schema}}
>
<style>
  .loc-hero {{padding:4rem 0 2.5rem; background:radial-gradient(ellipse at top,rgba(255,107,53,.1) 0%,transparent 55%);}}
  .loc-hero h1 {{font-size:clamp(1.7rem,4vw,2.6rem);font-weight:800;margin-bottom:1rem;line-height:1.2;}}
  .loc-hero p {{color:var(--text-muted);font-size:1rem;max-width:600px;line-height:1.8;margin-bottom:1.8rem;}}
  .btn-p {{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;transition:transform .2s;}}
  .btn-p:hover {{transform:translateY(-2px);}}
  .btn-wa {{background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;}}
  .loc-s {{padding:3rem 0;}} .loc-s-alt {{padding:3rem 0; background:var(--dark-2);}}
  .sec-title {{font-size:1.5rem;font-weight:800;margin-bottom:.5rem;}}
  .info-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem;}}
  .info-card {{background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.3rem;}}
  .info-card h3 {{font-weight:700;margin-bottom:.5rem;font-size:.95rem;}}
  .info-card ul {{list-style:none;padding:0;}}
  .info-card li {{padding:.3rem 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:.88rem;color:var(--text-muted);}}
  .tip-grid {{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:.8rem;margin-top:1rem;}}
  .tip-card {{background:var(--dark-3);border:1px solid rgba(255,107,53,.1);border-radius:10px;padding:.9rem;text-align:center;font-size:.88rem;color:var(--text-muted);}}
  .faq-list {{display:flex;flex-direction:column;gap:.9rem;max-width:700px;}}
  .faq-item {{background:var(--dark-3);border:1px solid rgba(255,107,53,.12);border-radius:12px;padding:1.2rem;}}
  .faq-item h3 {{font-size:.93rem;font-weight:700;margin-bottom:.4rem;}}
  .faq-item p {{font-size:.88rem;color:var(--text-muted);line-height:1.7;}}
  .cta-box {{background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.05));border:1px solid rgba(255,107,53,.25);border-radius:18px;padding:2.5rem 1.5rem;text-align:center;}}
  .cta-box h2 {{font-size:1.5rem;font-weight:800;margin-bottom:.8rem;}}
  .cta-box p {{color:var(--text-muted);margin-bottom:1.5rem;font-size:.95rem;}}
  .cta-btns {{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;}}
</style>

<section class="loc-hero">
  <div class="container">
    <h1>Animatori Petreceri Copii<br><span style="color:var(--primary)">{name}</span></h1>
    <p>Organizezi o petrecere pentru copii în {name}? SuperParty aduce animatori actori cu costume premium direct la tine, indiferent dacă e o zi de naștere sau un alt eveniment special. Suntem la {dist_str} de București și ajungem cu plăcere.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;">
      <a href="{TEL}" class="btn-p cta">📞 Rezervă: 0722 744 377</a>
      <a href="{WA}" class="btn-wa cta">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section class="loc-s">
  <div class="container">
    <h2 class="sec-title">Informații despre <span style="color:var(--primary)">{name}</span></h2>
    <div class="info-grid">
      <div class="info-card">
        <h3>📍 Locație și acces</h3>
        <ul>
          <li>Distanță: {dist_str} de la București</li>
          <li>Timp estimat: confirmat la rezervare</li>
          <li>Taxă deplasare: comunicată la ofertă</li>
        </ul>
      </div>
      <div class="info-card">
        <h3>🎭 Ce includem</h3>
        <ul>
          <li>Animator actor în costum premium</li>
          <li>Jocuri, dansuri, baloane modelate</li>
          <li>Pictură pe față + tatuaje temporare</li>
          <li>Diplome magnetice pentru toți copiii</li>
        </ul>
      </div>
      <div class="info-card">
        <h3>💰 Pachete de la 490 lei</h3>
        <ul>
          <li>Super 1 — 1 personaj, 2 ore — 490 lei</li>
          <li>Super 3 — 2 personaje + confetti — 840 lei</li>
          <li>+170 lei/oră sau personaj extra</li>
        </ul>
        <a href="/animatori-petreceri-copii" style="color:var(--primary);font-size:.85rem;display:block;margin-top:.6rem;font-weight:600;">→ Toate pachetele</a>
      </div>
    </div>
  </div>
</section>

<section class="loc-s-alt">
  <div class="container">
    <h2 class="sec-title">Unde organizăm petrecerea în <span style="color:var(--primary)">{name}</span>?</h2>
    <p style="color:var(--text-muted);margin-bottom:1.5rem;">Venim oriunde aveți spațiu — nu inventăm locații, ci ne adaptăm la ale voastre:</p>
    <div class="tip-grid">
      <div class="tip-card">🏠 La domiciliu<br><span style="font-size:.78rem;">curte sau sufragerie</span></div>
      <div class="tip-card">🎂 Sală de petreceri<br><span style="font-size:.78rem;">locale, sală copii</span></div>
      <div class="tip-card">🍽️ Restaurant family<br><span style="font-size:.78rem;">cu spațiu dedicat</span></div>
      <div class="tip-card">🌳 Grădină<br><span style="font-size:.78rem;">petrecere în aer liber</span></div>
      <div class="tip-card">🏫 Grădiniță/Școală<br><span style="font-size:.78rem;">la cerere specială</span></div>
      <div class="tip-card">🏢 Club/Centru<br><span style="font-size:.78rem;">centre recreative</span></div>
    </div>
    <p style="margin-top:1.2rem;font-size:.88rem;color:var(--text-muted);">Spațiu minim necesar: 15–20 mp. Noi aducem tot echipamentul.</p>
  </div>
</section>

<section class="loc-s">
  <div class="container">
    <h2 class="sec-title">Întrebări despre animatori în <span style="color:var(--primary)">{name}</span></h2>
    <div class="faq-list">
      {{[
        ["Activați animatori în {name}?", "Da — acoperim {name} și localitățile învecinate. Contactați-ne cu data și adresa exactă pentru a confirma disponibilitatea."],
        ["Există taxă de deplasare pentru {name}?", "Depinde de distanță ({dist_str} de la București). Contactați-ne pentru o ofertă completă inclusiv transport."],
        ["Unde se poate organiza petrecerea în {name}?", "La domiciliu, la o sală de petreceri sau alt spațiu din {name}. Avem nevoie de minim 15–20 mp."],
        ["Cu cât timp înainte rezervăm?", "Minim 7–14 zile, mai ales în weekend și sezon (mai–septembrie)."],
      ].map(([q,a]) => (
        <div class="faq-item">
          <h3>❓ {{q}}</h3>
          <p>{{a}}</p>
        </div>
      ))}}
    </div>
  </div>
</section>

<section class="loc-s-alt">
  <div class="container">
    <div class="cta-box">
      <h2>Rezervă animator în <span style="color:var(--primary)">{name}</span></h2>
      <p>Spune-ne data, adresa și vârsta copiilor — îți confirmăm disponibilitatea și oferta în cel mult 24 ore.</p>
      <div class="cta-btns">
        <a href="{TEL}" class="btn-p cta">📞 0722 744 377</a>
        <a href="{WA}" class="btn-wa cta">💬 WhatsApp</a>
      </div>
      <p style="margin-top:1.2rem;font-size:.88rem;color:var(--text-muted);">
        ← <a href="/animatori-petreceri-copii" style="color:var(--primary);font-weight:600;">Pagina principală Animatori</a>
        &nbsp;|&nbsp;
        <a href="/petreceri/{judet_hub}" style="color:var(--primary);">Hub județ</a>
        &nbsp;|&nbsp;
        <a href="/arie-acoperire" style="color:var(--primary);">Toate zonele</a>
      </p>
    </div>
  </div>
</section>
</Layout>
'''

# Mapping Judet Hub
JUDET_HUB_MAP = {
    "prahova": "prahova", "dambovita": "dambovita", "giurgiu": "giurgiu",
    "ialomita": "ialomita", "calarasi": "calarasi", "teleorman": "teleorman",
}

generated_tier3 = []
manifest = []

for item in tier3_candidates:
    slug = item["slug"]
    if slug in existing_slugs or slug in generated_judete:
        continue
    # guess judet hub
    judet_hub = "ilfov" if item["dist_km"] < 45 else "prahova"
    
    content = tier3_template(item["name"], slug, item["place"], item["dist_km"], judet_hub)
    fpath = os.path.join(PAGES_DIR, f"{slug}.astro")
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    generated_tier3.append(slug)
    manifest.append({
        "slug": slug,
        "name": item["name"],
        "tier": 3,
        "indexable": True,
        "place_type": item["place"],
        "dist_km": item["dist_km"],
        "score": item["score"],
        "hub": judet_hub,
        "url": f"{CANONICAL_HOST}/petreceri/{slug}",
    })

print(f"\n✓ Tier 3 generate: {len(generated_tier3)} pagini")

# Adaugă hub-urile județene în manifest
for slug in generated_judete:
    manifest.insert(0, {
        "slug": slug,
        "tier": 2,
        "indexable": True,
        "place_type": "county_hub",
        "hub": "animatori-petreceri-copii",
        "url": f"{CANONICAL_HOST}/petreceri/{slug}",
    })

# Adaugă și Tier 1 + hub-uri existente
TIER1_TIER2_EXISTING = [
    {"slug": "animatori-petreceri-copii", "tier": 1, "hub": None},
    {"slug": "bucuresti", "tier": 2, "hub": "animatori-petreceri-copii"},
    {"slug": "sector-1", "tier": 2, "hub": "bucuresti"},
    {"slug": "sector-2", "tier": 2, "hub": "bucuresti"},
    {"slug": "sector-3", "tier": 2, "hub": "bucuresti"},
    {"slug": "sector-4", "tier": 2, "hub": "bucuresti"},
    {"slug": "sector-5", "tier": 2, "hub": "bucuresti"},
    {"slug": "sector-6", "tier": 2, "hub": "bucuresti"},
    {"slug": "ilfov", "tier": 2, "hub": "animatori-petreceri-copii"},
]
for item in TIER1_TIER2_EXISTING:
    item["indexable"] = True
    item["url"] = f"{CANONICAL_HOST}/petreceri/{item['slug']}" if item["tier"] == 2 else f"{CANONICAL_HOST}/{item['slug']}"
    manifest.insert(0, item)

# Salvare manifest
manifest_path = os.path.join(REPORTS_DIR, "indexing_manifest.json")
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"\n📊 SUMAR FINAL:")
print(f"  Hub-uri județene noi: {len(generated_judete)}")
print(f"  Tier 3 localități:    {len(generated_tier3)}")
print(f"  Manifest total:       {len(manifest)} intrări")
print(f"\n✅ Done! Fișiere salvate.")
