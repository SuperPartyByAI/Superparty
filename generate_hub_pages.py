"""
Generează paginile hub locale pentru sectoare + Ilfov + 30 localități.
"""
import os

PAGES_DIR = r"C:\Users\ursac\Superparty\src\pages\petreceri"

# Sursa unica pentru origin — aliniata cu src/config/site.ts si astro.config.mjs
SITE_ORIGIN = 'https://www.superparty.ro'

# ==========================================
# Template comun pentru hub local
# ==========================================
def hub_template(slug, title, desc, canonical, h1, intro, locatii, timp_depl, faq_local, cartiere="", robots="noindex, follow"):
    faq_items = ",\n".join([
        f"""      {{
        "@type": "Question",
        "name": "{q}",
        "acceptedAnswer": {{ "@type": "Answer", "text": "{a}" }}
      }}""" for q, a in faq_local
    ])
    locatii_html = "\n".join([f'              <li>📍 {loc}</li>' for loc in locatii])
    return f'''---
import Layout from '../../layouts/Layout.astro';
import {{ getCollection }} from 'astro:content';

const allArticles = await getCollection('seo-articles');
const hubArticles = allArticles.filter(article =>
  article.slug.includes('{slug}') && article.data.indexStatus !== 'hold'
).slice(0, 18);

const schema = JSON.stringify({{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "Service",
      "name": "{title}",
      "provider": {{ "@type": "LocalBusiness", "name": "SuperParty", "telephone": "+40722744377" }},
      "areaServed": "{h1}",
      "url": "{SITE_ORIGIN}/petreceri/{slug}"
    }},
    {{
      "@type": "FAQPage",
      "mainEntity": [
        {faq_items}
      ]
    }},
    {{
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{ "@type": "ListItem", "position": 1, "name": "Acasă", "item": "{SITE_ORIGIN}" }},
        {{ "@type": "ListItem", "position": 2, "name": "Animatori Petreceri Copii", "item": "{SITE_ORIGIN}/animatori-petreceri-copii" }},
        {{ "@type": "ListItem", "position": 3, "name": "{h1}", "item": "{SITE_ORIGIN}/petreceri/{slug}" }}
      ]
    }}
  ]
}});
---

<Layout
  title="{title} | SuperParty"
  description="{desc}"
  canonical="{SITE_ORIGIN}/petreceri/{slug}"
  robots="{robots}"
  schema={{schema}}
>
<style>
  .hub-hero {{ padding: 4.5rem 0 3rem; background: radial-gradient(ellipse at top, rgba(255,107,53,.1) 0%, transparent 55%); }}
  .hub-hero h1 {{ font-size: clamp(1.8rem,4vw,2.8rem); font-weight:800; margin-bottom:1rem; line-height:1.2; }}
  .hub-hero p {{ color:var(--text-muted); font-size:1.05rem; max-width:620px; line-height:1.8; margin-bottom:2rem; }}
  .btn-p {{ background:linear-gradient(135deg,var(--primary),var(--primary-dark)); color:#fff; padding:.9rem 2rem; border-radius:50px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:.5rem; transition:transform .2s; }}
  .btn-p:hover {{ transform:translateY(-2px); }}
  .btn-wa {{ background:#25d366; color:#fff; padding:.9rem 1.8rem; border-radius:50px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:.5rem; }}
  .hub-section {{ padding:3.5rem 0; }}
  .hub-section-alt {{ padding:3.5rem 0; background:var(--dark-2); }}
  .sec-title {{ font-size:1.6rem; font-weight:800; margin-bottom:.5rem; }}
  .sec-sub {{ color:var(--text-muted); margin-bottom:2rem; }}
  .info-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:1.5rem; }}
  .info-card {{ background:var(--dark-3); border:1px solid rgba(255,107,53,.15); border-radius:14px; padding:1.5rem; }}
  .info-card h3 {{ font-weight:700; margin-bottom:.6rem; }}
  .info-card ul {{ list-style:none; padding:0; }}
  .info-card li {{ padding:.35rem 0; border-bottom:1px solid rgba(255,255,255,.05); font-size:.9rem; color:var(--text-muted); }}
  .art-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:1rem; }}
  .art-card {{ background:var(--dark-3); border:1px solid rgba(255,107,53,.12); border-radius:14px; padding:1.2rem; text-decoration:none; color:var(--text); transition:border-color .2s; }}
  .art-card:hover {{ border-color:var(--primary); }}
  .art-card h3 {{ font-size:.95rem; font-weight:700; color:var(--primary); margin-bottom:.4rem; }}
  .art-card p {{ font-size:.82rem; color:var(--text-muted); }}
  .faq-list {{ display:flex; flex-direction:column; gap:1rem; max-width:720px; }}
  .faq-item {{ background:var(--dark-3); border:1px solid rgba(255,107,53,.12); border-radius:14px; padding:1.3rem; }}
  .faq-item h3 {{ font-size:.95rem; font-weight:700; margin-bottom:.5rem; }}
  .faq-item p {{ font-size:.9rem; color:var(--text-muted); line-height:1.7; }}
  .cta-box {{ background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.05)); border:1px solid rgba(255,107,53,.25); border-radius:20px; padding:3rem 2rem; text-align:center; }}
  .cta-box h2 {{ font-size:1.7rem; font-weight:800; margin-bottom:1rem; }}
  .cta-box p {{ color:var(--text-muted); margin-bottom:2rem; }}
  .cta-btns {{ display:flex; gap:1rem; flex-wrap:wrap; justify-content:center; }}
  @media(max-width:600px) {{ .cta-btns {{ flex-direction:column; align-items:center; }} }}
</style>

<section class="hub-hero">
  <div class="container">
    <h1>Animatori Petreceri Copii<br><span style="color:var(--primary)">{h1}</span></h1>
    <p>{intro}</p>
    <div style="display:flex; gap:1rem; flex-wrap:wrap;">
      <a href="tel:+40722744377" class="btn-p cta">📞 Rezervă: 0722 744 377</a>
      <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section class="hub-section">
  <div class="container">
    <div class="info-grid">
      <div class="info-card">
        <h3>📍 Locații populare în {h1}</h3>
        <ul>
          {locatii_html}
        </ul>
      </div>
      <div class="info-card">
        <h3>⏱ Timp de deplasare</h3>
        <ul>
          <li>{timp_depl}</li>
          <li>Sosim cu 10 min înainte de program</li>
          <li>Fără taxă de deplasare în zona centrală</li>
        </ul>
      </div>
      <div class="info-card">
        <h3>🎭 Pachete disponibile</h3>
        <ul>
          <li>Standard 60 min — de la 350 RON</li>
          <li>Premium 90 min — de la 500 RON</li>
          <li>VIP 120 min — de la 700 RON</li>
        </ul>
        <p style="margin-top:.8rem; font-size:.85rem; color:var(--text-muted);">
          <a href="/animatori-petreceri-copii" style="color:var(--primary)">→ Vezi toate pachetele și prețurile</a>
        </p>
      </div>
    </div>
  </div>
</section>

{{hubArticles.length > 0 && (
<section class="hub-section-alt">
  <div class="container">
    <h2 class="sec-title">Animatori disponibili în <span style="color:var(--primary)">{h1}</span></h2>
    <p class="sec-sub">Personaje și servicii specifice pentru această zonă.</p>
    <div class="art-grid">
      {{hubArticles.map(article => (
        <a href={{`/petreceri/${{article.slug}}`}} class="art-card">
          <h3>{{article.data.title}}</h3>
          <p>{{article.data.description?.slice(0,100)}}...</p>
        </a>
      ))}}
    </div>
  </div>
</section>
)}}

<section class="hub-section">
  <div class="container">
    <h2 class="sec-title">Întrebări despre animatori în <span style="color:var(--primary)">{h1}</span></h2>
    <div class="faq-list">
      {{[
        ["Activați în {h1}?", "Da — acoperim toată zona {h1}. Contactați-ne pentru confirmare și detalii logistice."],
        ["Cât costă un animator în {h1}?", "Prețurile pornesc de la 350 RON pentru 60 min. Contactați-ne pentru ofertă exactă inclusiv transport."],
        ["Se poate organiza la domiciliu în {h1}?", "Da — venim la domiciliu, sală de petreceri sau grădiniță din {h1} și împrejurimi."],
      ].map(([q, a]) => (
        <div class="faq-item">
          <h3>❓ {{q}}</h3>
          <p>{{a}}</p>
        </div>
      ))}}
    </div>
  </div>
</section>

<section class="hub-section-alt">
  <div class="container">
    <div class="cta-box">
      <h2>Rezervă animator în <span style="color:var(--primary)">{h1}</span></h2>
      <p>Disponibilitate limitată în weekend. Rezervați cu avans.</p>
      <div class="cta-btns">
        <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
        <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
      </div>
      <p style="margin-top:1.5rem; font-size:.9rem; color:var(--text-muted);">
        ← <a href="/animatori-petreceri-copii" style="color:var(--primary); font-weight:600;">Înapoi la pagina principală Animatori Petreceri Copii</a>
      </p>
    </div>
  </div>
</section>

</Layout>
'''

# ==========================================
# DATE DIFERENTIATE PER ZONA
# ==========================================
HUBS = {
    "sector-1": {
        "title": "Animatori Petreceri Copii Sector 1",
        "desc": "Animatori profesioniști pentru petreceri copii în Sector 1 București — Dorobanți, Floreasca, Aviatorilor. Costume premium, programe 60-120 min. Rezervă: 0722 744 377.",
        "h1": "Sector 1",
        "intro": "Organizăm petreceri de vis pentru copii în Sector 1 — Dorobanți, Floreasca, Aviatorilor, Băneasa, Pipera. Animatori actori cu experiență, costume premium și programe adaptate vârstei.",
        "locatii": ["Zona Dorobanți / Floreasca", "Cartier Aviatorilor / Herăstrău", "Băneasa / Pipera", "Calea Victoriei / Romană", "Săli de petreceri Sector 1"],
        "timp_depl": "15-30 min din centru, în funcție de trafic",
        "faq_local": [
            ("Activați în Sector 1?", "Da — acoperim tot Sectorul 1: Dorobanți, Floreasca, Aviatorilor, Băneasa, Pipera și toate cartierele."),
            ("Aveți animatori lângă Herăstrău?", "Da — zona Herăstrău și Floreasca este în raza noastră de acoperire principală.")
        ]
    },
    "sector-2": {
        "title": "Animatori Petreceri Copii Sector 2",
        "desc": "Animatori profesioniști pentru petreceri copii în Sector 2 București — Colentina, Pantelimon, Iancului. Costume premium. Rezervă: 0722 744 377.",
        "h1": "Sector 2",
        "intro": "Aducem petreceri magice în Sector 2 — Colentina, Pantelimon, Fundeni, Obor, Iancului. Animatori cu experiență, personaje premium și programe complete pentru orice vârstă.",
        "locatii": ["Colentina / Fundeni", "Pantelimon / Iancului", "Obor / 23 August", "Titan (limita sector 2/3)", "Săli de petreceri Sector 2"],
        "timp_depl": "20-35 min din centru",
        "faq_local": [
            ("Activați în Colentina?", "Da — Colentina este una din zonele principale ale Sectorului 2 unde activăm frecvent."),
            ("Mergeți și în Pantelimon?", "Da — Pantelimon și Fundeni sunt în raza noastră de acoperire.")
        ]
    },
    "sector-3": {
        "title": "Animatori Petreceri Copii Sector 3",
        "desc": "Animatori profesioniști pentru petreceri copii în Sector 3 București — Titan, Vitan, Dristor, Balta Albă. Costume premium. Rezervă: 0722 744 377.",
        "h1": "Sector 3",
        "intro": "Animatorii SuperParty aduc magie în Sector 3 — Titan, Vitan, Dristor, Balta Albă, Oltenița. Programe structurate 60-120 min, costume impecabile și amintiri de neuitat.",
        "locatii": ["Titan / Balta Albă", "Vitan / Dristor", "Oltenița / Mihai Bravu", "IOR / Lunca Bradului", "Săli de petreceri Sector 3"],
        "timp_depl": "15-30 min din centru",
        "faq_local": [
            ("Activați în zona Titan?", "Da — Titan este una din zonele cu cea mai mare cerere din Sectorul 3 unde activăm."),
            ("Mergeți și la Vitan Mall?", "Da — Sector 3 inclusiv zona Vitan este complet acoperită.")
        ]
    },
    "sector-4": {
        "title": "Animatori Petreceri Copii Sector 4",
        "desc": "Animatori profesioniști pentru petreceri copii în Sector 4 București — Berceni, Olteniței, Giurgiului. Costume premium. Rezervă: 0722 744 377.",
        "h1": "Sector 4",
        "intro": "Petreceri de vis în Sector 4 — Berceni, Olteniței, Giurgiului, Brâncoveanu. Animatori profesioniști cu costume premium și programe complete pentru zi de naștere sau alt eveniment special.",
        "locatii": ["Berceni / Brâncoveanu", "Olteniței / Giurgiului", "Piața Sudului / Tineretului", "Văcărești / Serghie Courboin", "Săli de petreceri Sector 4"],
        "timp_depl": "20-35 min din centru",
        "faq_local": [
            ("Activați în Berceni?", "Da — Berceni este principala zonă a Sectorului 4 unde deservim frecvent petreceri."),
            ("Costă mai mult deplasarea în Sector 4?", "Nu — Sectorul 4 este în raza standard, fără taxă suplimentară de deplasare.")
        ]
    },
    "sector-5": {
        "title": "Animatori Petreceri Copii Sector 5",
        "desc": "Animatori profesioniști pentru petreceri copii în Sector 5 București — Rahova, Ferentari, 13 Septembrie. Costume premium. Rezervă: 0722 744 377.",
        "h1": "Sector 5",
        "intro": "SuperParty activează în tot Sectorul 5 — Rahova, Ferentari, 13 Septembrie, Cotroceni, Panduri. Animatori actori, costume originale și programe pline de energie pentru copiii tăi.",
        "locatii": ["Rahova / Ferentari", "13 Septembrie / Panduri", "Cotroceni / Elefterie", "Uranus / Piața Constituției", "Săli de petreceri Sector 5"],
        "timp_depl": "15-30 min din centru",
        "faq_local": [
            ("Activați în Rahova?", "Da — acoperim tot Sectorul 5 inclusiv Rahova și toate cartierele adiacente."),
            ("Mergeți și în Cotroceni?", "Da — Cotroceni și zona 13 Septembrie sunt în raza noastră principală.")
        ]
    },
    "sector-6": {
        "title": "Animatori Petreceri Copii Sector 6",
        "desc": "Animatori profesioniști pentru petreceri copii în Sector 6 București — Militari, Drumul Taberei, Crângași. Costume premium. Rezervă: 0722 744 377.",
        "h1": "Sector 6",
        "intro": "Aducem distracție în Sector 6 — Militari, Drumul Taberei, Crângași, Giulești, Crangași. Animatori cu experiență și costume de înaltă calitate pentru petreceri de neuitat.",
        "locatii": ["Militari / Crângași", "Drumul Taberei / Favorit", "Giulești / Ghencea", "Lujerului / Plaza România", "Săli de petreceri Sector 6"],
        "timp_depl": "20-35 min din centru",
        "faq_local": [
            ("Activați în Militari?", "Da — Militari este una din cele mai mari zone din Sectorul 6 unde activăm regulat."),
            ("Mergeți și în Drumul Taberei?", "Da — Drumul Taberei și Favorit sunt complet acoperite.")
        ]
    },
    "ilfov": {
        "title": "Animatori Petreceri Copii Ilfov",
        "desc": "Animatori profesioniști pentru petreceri copii în județul Ilfov — Voluntari, Otopeni, Bragadiru, Chiajna. Costume premium. Rezervă: 0722 744 377.",
        "h1": "Județul Ilfov",
        "intro": "SuperParty activează în tot județul Ilfov — Voluntari, Otopeni, Pantelimon, Bragadiru, Chiajna și alte localități. Distanța nu e o problemă; aducem magia personajelor favorite direct la petrecerea copilului.",
        "locatii": ["Voluntari / Pipera", "Otopeni / Mogoșoaia", "Pantelimon / Cernica", "Bragadiru / Chiajna / Chitila", "Popești-Leordeni / Jilava"],
        "timp_depl": "25-45 min, în funcție de localitate (posibilă taxă de deplasare)",
        "faq_local": [
            ("Există taxă de deplasare în Ilfov?", "Depinde de localitate și distanță. Localitățile apropiate (Voluntari, Bragadiru) sunt adesea fără taxă. Contactați-ne pentru detalii."),
            ("Activați în Voluntari?", "Da — Voluntari este una din localitățile Ilfov cu cea mai mare cerere pentru serviciile noastre.")
        ]
    },
    "bucuresti": {
        "title": "Animatori Petreceri Copii București",
        "desc": "Animatori profesioniști pentru petreceri copii în toată Bucureștiul. Costume premium, 30+ personaje, programe 60-120 min. Rezervă: 0722 744 377.",
        "h1": "București",
        "intro": "Animatorii SuperParty acoperă toată capitala — toate cele 6 sectoare, orice cartier, orice tip de locație. Costume premium, actori cu experiență și programe complete adaptate oricărei vârste.",
        "locatii": ["Sector 1 — Dorobanți, Floreasca", "Sector 2 — Colentina, Pantelimon", "Sector 3 — Titan, Vitan", "Sector 4 — Berceni, Oltenița", "Sector 5 — Rahova, Drumul Taberei", "Sector 6 — Militari, Crângași"],
        "timp_depl": "15-35 min în funcție de sector și trafic",
        "faq_local": [
            ("Activați în toate sectoarele Bucureștiului?", "Da — acoperim toate cele 6 sectoare ale Bucureștiului, indiferent de zonă."),
            ("Există taxă de deplasare în București?", "Nu — în București nu există taxă de deplasare standard. Contactați-ne dacă locația este greu accesibilă.")
        ]
    }
}

# ==========================================
# LOCALITATI ILFOV (30)
# ==========================================
ILFOV_LOCALITATI = [
    {
        "slug": "voluntari",
        "oras": "Voluntari",
        "intro": "Organizăm petreceri cu animatori în Voluntari — una din cele mai populate localități din Ilfov, cu o cerere mare pentru servicii de animație copii. Activăm în tot orașul și împrejurimile.",
        "locatii": ["Pipera / Tunari (zonă Voluntari)", "Centrul vechi Voluntari", "Complexe rezidențiale Voluntari", "Săli de petreceri Voluntari"],
        "timp": "~20 min din centrul Bucureștiului"
    },
    {
        "slug": "popesti-leordeni",
        "oras": "Popești-Leordeni",
        "intro": "Animatori pentru petreceri copii în Popești-Leordeni. Localitate cu creștere rapidă la sud de București, acoperită integral de echipa SuperParty.",
        "locatii": ["Centrul Popești-Leordeni", "Zona rezidențială sud", "Leordeni / Bașcov", "Săli de petreceri disponibile"],
        "timp": "~25 min din centrul Bucureștiului"
    },
    {
        "slug": "otopeni",
        "oras": "Otopeni",
        "intro": "Animatori petreceri copii în Otopeni și împrejurimi. La câțiva km de aeroportul Henri Coandă, Otopeni este o localitate activă unde organizăm petreceri de zi de naștere.",
        "locatii": ["Centrul Otopeni", "Zona aeroportului (rezidențial)", "Mogoșoaia (localitate adiacentă)", "Săli de petreceri Otopeni"],
        "timp": "~25-30 min din centrul Bucureștiului"
    },
    {
        "slug": "pantelimon",
        "oras": "Pantelimon",
        "intro": "Petreceri cu animatori în Pantelimon — localitate la est de București, la granița cu Sectorul 2 și 3. Acoperim toată zona.",
        "locatii": ["Centrul Pantelimon", "Zona Cernica / Brănești (adiacent)", "Cartiere rezidențiale Pantelimon", "Săli de petreceri disponibile"],
        "timp": "~20-25 min din centrul Bucureștiului"
    },
    {
        "slug": "bragadiru",
        "oras": "Bragadiru",
        "intro": "Animatori pentru petrecerile copiilor din Bragadiru. Localitate la sud-vest de București, cu acces facil și o comunitate în creștere.",
        "locatii": ["Centrul Bragadiru", "Cartiere rezidențiale noi", "Zona industrială adaptată events", "Săli de petreceri Bragadiru"],
        "timp": "~25-35 min din centrul Bucureștiului"
    },
    {
        "slug": "chiajna",
        "oras": "Chiajna",
        "intro": "Animatori petreceri copii în Chiajna — localitate la vest de București, pe DN1, acoperită integral de SuperParty.",
        "locatii": ["Chiajna centru", "Roșu (localitate componentă)", "Dudu / Vărăști (zone adiacente)", "Săli de petreceri Chiajna"],
        "timp": "~20-30 min din centrul Bucureștiului"
    },
    {
        "slug": "chitila",
        "oras": "Chitila",
        "intro": "Animatori copii în Chitila — localitate situată la nord-vest de București, cu acces rapid din Sectorul 1.",
        "locatii": ["Chitila centru", "Ilfov (sat component)", "Rudeni / Dârvari", "Săli de petreceri Chitila"],
        "timp": "~20-25 min din centrul Bucureștiului"
    },
    {
        "slug": "buftea",
        "oras": "Buftea",
        "intro": "Organizăm petreceri cu animatori în Buftea — unul dintre cele mai cunoscute orașe din Ilfov, cu infrastructură bună pentru events.",
        "locatii": ["Centrul Buftea (lângă lac)", "Zona studiouri Buftea", "Cartiere rezidențiale", "Săli de petreceri Buftea"],
        "timp": "~30-40 min din centrul Bucureștiului"
    },
    {
        "slug": "mogosoaia",
        "oras": "Mogoșoaia",
        "intro": "Animatori petreceri copii în Mogoșoaia — comună elegantă la nord de București, cu vile și palatul Mogoșoaia, acoperită de SuperParty.",
        "locatii": ["Mogoșoaia centru", "Zona Palatul Mogoșoaia", "Dărăști-Ilfov (adiacent)", "Vile și palate de nuntă disponibile"],
        "timp": "~25-35 min din centrul Bucureștiului"
    },
    {
        "slug": "corbeanca",
        "oras": "Corbeanca",
        "intro": "Animatori copii în Corbeanca — comună rezidențială de lux la nord de București, în apropierea Snagov-ului.",
        "locatii": ["Corbeanca centru", "Tamași (sat component)", "Zona rezidențială premium", "Vile/grădini disponibile pentru events"],
        "timp": "~35-45 min din centrul Bucureștiului"
    },
    {
        "slug": "tunari",
        "oras": "Tunari",
        "intro": "Animatori petreceri copii în Tunari — comună la nord-est de București, în vecinătatea Voluntariului.",
        "locatii": ["Tunari centru", "Zona Afumați (adiacent)", "Cartiere rezidențiale noi", "Săli de petreceri disponibile"],
        "timp": "~25-35 min din centrul Bucureștiului"
    },
    {
        "slug": "snagov",
        "oras": "Snagov",
        "intro": "Animatori copii în Snagov — comună cu lac, case de vacanță și pensiuni, ideală pentru petreceri în aer liber.",
        "locatii": ["Snagov centru / lac", "Ciofliceni (sat component)", "Vlad Țepeș / Izvorani", "Pensiuni și vile disponibile"],
        "timp": "~40-50 min din centrul Bucureștiului"
    },
    {
        "slug": "dobroesti",
        "oras": "Dobroești",
        "intro": "Animatori petreceri copii în Dobroești — comună la marginea estică a Bucureștiului, lângă Pantelimon.",
        "locatii": ["Dobroești centru", "Fundeni (sat component)", "Zona Pantelimon (adiacent)", "Săli de petreceri disponibile"],
        "timp": "~20-30 min din centrul Bucureștiului"
    },
    {
        "slug": "jilava",
        "oras": "Jilava",
        "intro": "Animatori copii în Jilava — comună la sud de București, acoperită de SuperParty.",
        "locatii": ["Jilava centru", "Zona industrială reconvertită", "Berceni (Sector 4, adiacent)", "Săli de petreceri Jilava"],
        "timp": "~25-35 min din centrul Bucureștiului"
    },
    {
        "slug": "magurele",
        "oras": "Măgurele",
        "intro": "Animatori petreceri copii în Măgurele — comună universitară la sud-vest de București, cu comunitate activă.",
        "locatii": ["Măgurele centru", "Campus universitar", "Alunișu (sat component)", "Săli de petreceri disponibile"],
        "timp": "~30-40 min din centrul Bucureștiului"
    },
    {
        "slug": "cernica",
        "oras": "Cernica",
        "intro": "Animatori copii în Cernica — comună la est de București, cunoscută pentru mânăstire și lac.",
        "locatii": ["Cernica centru", "Balotești Ilfov (adiacent)", "Târgul Cernica", "Pensiuni și vile disponibile"],
        "timp": "~25-35 min din centrul Bucureștiului"
    },
    {
        "slug": "afumati",
        "oras": "Afumați",
        "intro": "Animatori petreceri copii în Afumați — comună la nord-est de București, în apropierea autostrăzii A3.",
        "locatii": ["Afumați centru", "Zona logistică reconvertită", "Tunari (adiacent)", "Locații disponibile pentru events"],
        "timp": "~25-35 min din centrul Bucureștiului"
    },
    {
        "slug": "branesti",
        "oras": "Brănești",
        "intro": "Animatori copii în Brănești — comună la est de București, accesibilă prin DN3.",
        "locatii": ["Brănești centru", "Islaz (sat component)", "Zona Pantelimon (adiacent)", "Săli de petreceri disponibile"],
        "timp": "~30-40 min din centrul București"
    },
    {
        "slug": "domnesti",
        "oras": "Domnești",
        "intro": "Animatori petreceri copii în Domnești — comună la vest de București, lângă Bragadiru.",
        "locatii": ["Domnești centru", "Dragomirești-Vale (adiacent)", "Zone rezidențiale noi", "Locații pentru events disponibile"],
        "timp": "~30-40 min din centrul Bucureștiului"
    },
    {
        "slug": "berceni-ilfov",
        "oras": "Berceni Ilfov",
        "intro": "Animatori copii în Berceni (comuna Ilfov) — nu confundați cu Sectorul 4; această comună se află la sudul județului Ilfov.",
        "locatii": ["Berceni centru (comuna)", "Vecinii: Jilava, Măgurele", "Zone rezidențiale", "Locații disponibile"],
        "timp": "~30-40 min din centrul Bucureștiului"
    },
    {
        "slug": "1-decembrie",
        "oras": "1 Decembrie",
        "intro": "Animatori petreceri copii în 1 Decembrie (Ilfov) — comună la sud de București, pe DN4.",
        "locatii": ["1 Decembrie centru", "Zona DN4", "Comunitate locală activă", "Locații pentru events"],
        "timp": "~30-40 min din centrul Bucureștiului"
    },
    {
        "slug": "dragomiresti-vale",
        "oras": "Dragomirești-Vale",
        "intro": "Animatori copii în Dragomirești-Vale — comună la vest de București, în imediata apropiere a Domeniului Sticlari.",
        "locatii": ["Dragomirești-Vale centru", "Stâlpeni / Bacu (adiacent)", "Zone rezidențiale", "Vile disponibile"],
        "timp": "~35-45 min din centrul Bucureștiului"
    },
    {
        "slug": "ganeasa",
        "oras": "Găneasa",
        "intro": "Animatori petreceri copii în Găneasa — comună la est de București, cu acces rapid din Sector 2.",
        "locatii": ["Găneasa centru", "Mănăstirea (sat component)", "Zone rezidențiale", "Locații disponibile"],
        "timp": "~30-40 min din centrul Bucureștiului"
    },
    {
        "slug": "glina",
        "oras": "Glina",
        "intro": "Animatori copii în Glina — comună la est de București, acoperită de echipa SuperParty.",
        "locatii": ["Glina centru", "Sintești (sat component)", "Zona est București (adiacent)", "Locații disponibile"],
        "timp": "~25-35 min din centrul Bucureștiului"
    },
    {
        "slug": "peris",
        "oras": "Periș",
        "intro": "Animatori petreceri copii în Periș — comună la nord de Ilfov, pe drumul spre Snagov.",
        "locatii": ["Periș centru", "Merii Petchii (sat component)", "Zona Snagov (adiacent)", "Pensiuni disponibile"],
        "timp": "~40-50 min din centrul Bucureștiului"
    },
    {
        "slug": "dascalu",
        "oras": "Dascălu",
        "intro": "Animatori copii în Dascălu — comună la nord-est de București, acoperită de SuperParty.",
        "locatii": ["Dascălu centru", "Gagu / Creața (sate componente)", "Zone rezidențiale", "Locații pentru events"],
        "timp": "~35-45 min din centrul Bucureștiului"
    },
    {
        "slug": "moara-vlasiei",
        "oras": "Moara Vlăsiei",
        "intro": "Animatori petreceri copii în Moara Vlăsiei — comună la nord de Ilfov, cu vile și case de vacanță.",
        "locatii": ["Moara Vlăsiei centru", "Mătăsaru (sat component)", "Zone rezidențiale premium", "Vile disponibile"],
        "timp": "~40-50 min din centrul Bucureștiului"
    },
    {
        "slug": "stefanestii-de-jos",
        "oras": "Ștefăneștii de Jos",
        "intro": "Animatori copii în Ștefăneștii de Jos — comună la nord de București, cu comunitate rezidențială în creștere.",
        "locatii": ["Ștefăneștii de Jos centru", "Ștefăneștii de Sus (adiacent)", "Zone rezidențiale noi", "Locații disponibile"],
        "timp": "~30-40 min din centrul Bucureștiului"
    },
    {
        "slug": "ciorogirla",
        "oras": "Ciorogârla",
        "intro": "Animatori petreceri copii în Ciorogârla — comună la vest de București, pe DN7.",
        "locatii": ["Ciorogârla centru", "Vărăști (sat component)", "Zona Chiajna (adiacent)", "Locații disponibile"],
        "timp": "~30-40 min din centrul Bucureștiului"
    },
    {
        "slug": "balotesti",
        "oras": "Balotești",
        "intro": "Animatori copii în Balotești — comună la nord de Ilfov, cu vile și stațiuni termale.",
        "locatii": ["Balotești centru (termal)", "Corbeanca (adiacent)", "Zone rezidențiale premium", "Vile și pensiuni disponibile"],
        "timp": "~35-45 min din centrul Bucureștiului"
    },
]

# ==========================================
# Generare fisiere hub
# ==========================================
generated = []

for slug, data in HUBS.items():
    content = hub_template(
        slug=slug,
        title=data["title"],
        desc=data["desc"],
        canonical=f"{SITE_ORIGIN}/petreceri/{slug}",
        h1=data["h1"],
        intro=data["intro"],
        locatii=data["locatii"],
        timp_depl=data["timp_depl"],
        faq_local=data["faq_local"]
    )
    filepath = os.path.join(PAGES_DIR, f"{slug}.astro")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    generated.append(filepath)
    print(f"✓ Generat: {slug}.astro")

# ==========================================
# Generare pagini localitati Ilfov
# ==========================================
for loc in ILFOV_LOCALITATI:
    slug = loc["slug"]
    oras = loc["oras"]
    title = f"Animatori Petreceri Copii {oras} | SuperParty"
    desc = f"Animatori profesioniști pentru petreceri copii în {oras}, Ilfov. Costume premium, programe 60-120 min. Rezervă: 0722 744 377."
    
    faq_local = [
        (f"Activați în {oras}?", f"Da — activăm în {oras} și localitățile adiacente. Contactați-ne pentru confirmare și detalii privind deplasarea."),
        (f"Există taxă de deplasare pentru {oras}?", f"Depinde de distanță — contactați-ne cu adresa exactă din {oras} pentru o ofertă completă inclusiv transport.")
    ]
    
    content = hub_template(
        slug=slug,
        title=title,
        desc=desc,
        canonical=f"{SITE_ORIGIN}/petreceri/{slug}",
        h1=oras,
        intro=loc["intro"],
        locatii=loc["locatii"],
        timp_depl=loc["timp"],
        faq_local=faq_local
    )
    
    filepath = os.path.join(PAGES_DIR, f"{slug}.astro")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    generated.append(filepath)
    print(f"✓ Generat: {slug}.astro ({oras})")

print(f"\n{'='*50}")
print(f"Total pagini generate: {len(generated)}")
print(f"  - Hub-uri locale (sectoare + Ilfov): {len(HUBS)}")
print(f"  - Pagini localități Ilfov: {len(ILFOV_LOCALITATI)}")
