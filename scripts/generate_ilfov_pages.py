import os
from pathlib import Path
REPO_ROOT = str(Path(__file__).resolve().parents[1])
import json
import os

LOCATIONS_PATH = r"os.path.join(REPO_ROOT, "reports", "locations", "locations_100km.json")"
PAGES_DIR = r"os.path.join(REPO_ROOT, "src", "pages", "petreceri")"
CANONICAL_HOST = "https://www.superparty.ro"

def tier3_template(name, slug, place_type, dist_km):
    place_ro = "oraș" if place_type == "town" else "comună" if place_type == "commune" else "localitate"
    dist_str = f"~{int(dist_km)} km" if dist_km else "~50 km"

    faq_items = [
        (f"Activați animatori în {name}?", f"Da — acoperim {name} ({place_ro}) și localitățile învecinate. Contactați-ne cu data și adresa exactă pentru a confirma disponibilitatea."),
        (f"Există taxă de deplasare pentru {name}?", f"Depinde de distanță ({dist_str} de la București). Contactați-ne pentru o ofertă completă inclusiv transport pentru animatori."),
        (f"Unde se poate organiza petrecerea în {name}?", f"La domiciliu, la o sală de petreceri, grădiniță sau alt spațiu din {name}. Avem nevoie de minim 15–20 mp de spațiu de joacă."),
    ]
    
    faq_entities = ',\n'.join([
        f'        {{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}' 
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
  description="Animatori profesioniști pentru petreceri copii în {name} ({place_ro}, {dist_str} de București). Costume premium, pachete interactive și jocuri. Rezervă: 0722 744 377."
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
    <p>Organizezi o petrecere pentru copii în {name}? SuperParty aduce animatori actori cu costume premium direct la tine, indiferent dacă e o zi de naștere sau un alt eveniment special. Suntem la {dist_str} de centrul capitalei și ajungem cu plăcere în acest {place_ro} din județul Ilfov.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;">
      <a href="tel:+40722744377" class="btn-p cta">📞 Rezervă: 0722 744 377</a>
      <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section class="loc-s">
  <div class="container">
    <h2 class="sec-title">Informații despre <span style="color:var(--primary)">{name}</span></h2>
    <div class="info-grid">
      <div class="info-card">
        <h3>📍 Locație și acces {place_ro}</h3>
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
      <div class="tip-card">🏠 La domiciliu<br><span style="font-size:.78rem;">curte (recomandat) sau sufragerie</span></div>
      <div class="tip-card">🎂 Sală de petreceri<br><span style="font-size:.78rem;">locale special amenajate</span></div>
      <div class="tip-card">🍽️ Restaurant family<br><span style="font-size:.78rem;">cu spațiu dedicat pentru copii</span></div>
      <div class="tip-card">🌳 Grădină<br><span style="font-size:.78rem;">petrecere în aer liber</span></div>
      <div class="tip-card">🏫 Grădiniță/Școală<br><span style="font-size:.78rem;">la cerere specială</span></div>
      <div class="tip-card">🏢 Club/Centru<br><span style="font-size:.78rem;">centre recreative locale</span></div>
    </div>
    <p style="margin-top:1.2rem;font-size:.88rem;color:var(--text-muted);">Spațiu minim necesar: 15–20 mp. Noi aducem recuzita și magia!</p>
  </div>
</section>

<section class="loc-s">
  <div class="container">
    <h2 class="sec-title">Întrebări despre animatori în <span style="color:var(--primary)">{name}</span></h2>
    <div class="faq-list">
      {{[
        ["Activați animatori în {name}?", "Da — acoperim {name} ({place_ro}) și localitățile învecinate. Contactați-ne cu data și adresa exactă pentru a confirma disponibilitatea."],
        ["Există taxă de deplasare pentru {name}?", "Depinde de distanță ({dist_str} de la București). Contactați-ne pentru o ofertă completă inclusiv transport pentru animatori."],
        ["Unde se poate organiza petrecerea în {name}?", "La domiciliu, la o sală de petreceri, grădiniță sau alt spațiu din {name}. Avem nevoie de minim 15–20 mp de spațiu de joacă."],
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
        <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
        <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
      </div>
      <p style="margin-top:1.2rem;font-size:.88rem;color:var(--text-muted);">
        ← <a href="/animatori-petreceri-copii" style="color:var(--primary);font-weight:600;">Pagina principală Animatori</a>
        &nbsp;|&nbsp;
        <a href="/petreceri/ilfov" style="color:var(--primary);">Hub Ilfov</a>
        &nbsp;|&nbsp;
        <a href="/arie-acoperire" style="color:var(--primary);">Toate zonele</a>
      </p>
    </div>
  </div>
</section>
</Layout>
'''

def main():
    print("Regeneram paginile pentru Orase/Comune Ilfov...")
    with open(LOCATIONS_PATH, 'r', encoding='utf-8') as f:
        locations = json.load(f)

    generated_count = 0
    for loc in locations:
        if loc.get("county") == "Ilfov" and loc.get("type") in ["town", "commune"]:
            slug = loc["slug"]
            name = loc["name"]
            place_type = loc["type"]
            dist_km = loc.get("dist_km", 20)
            
            content = tier3_template(name, slug, place_type, dist_km)
            
            fpath = os.path.join(PAGES_DIR, f"{slug}.astro")
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, 'w', encoding='utf-8') as fout:
                fout.write(content)
                
            generated_count += 1
            
    print(f"✅ Gata! Au fost generate/suprascrise {generated_count} pagini indexabile pentru Ilfov.")

if __name__ == "__main__":
    main()
