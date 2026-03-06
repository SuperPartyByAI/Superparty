from pathlib import Path
import json
import os

REPO_ROOT = Path(__file__).resolve().parents[1]
import unicodedata
import re

def slugify(text):
    text = text.lower().strip()
    for r, e in {'ă':'a','â':'a','î':'i','ș':'s','ş':'s','ț':'t','ţ':'t'}.items():
        text = text.replace(r, e)
    text = unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

MANIFEST_PATH = REPO_ROOT / "reports" / "seo" / "indexing_manifest.json"
LOCATIONS_PATH = REPO_ROOT / "reports" / "locations" / "locations_100km.json"
OUT_PAGE = REPO_ROOT / "src" / "pages" / "arie-acoperire.astro"
CANONICAL_HOST = "https://www.superparty.ro"

def main():
    if not MANIFEST_PATH.exists() or not LOCATIONS_PATH.exists():
        print("Missing reports. Rulati generate manifest / colectare locatii.")
        return

    manifest = json.load(open(MANIFEST_PATH, encoding='utf-8'))
    locations = json.load(open(LOCATIONS_PATH, encoding='utf-8'))

    # Indexed slugs din manifest ptr link-uri valide
    indexed_slugs = {m['slug'] for m in manifest if m.get('indexable')}

    # Ne interesaza: orase+comune (pentru listarea locala Ilfov/Bucuresti) 
    # si cartiere (numai Bucuresti default sau tot ce e marcat suburb)
    by_city_town = []
    by_suburb = []

    for loc in locations:
        if loc.get('type') in ('town', 'commune') and loc.get('county') == 'Ilfov':
            by_city_town.append(loc)
        elif loc.get('type') in ('suburb', 'neighbourhood') and loc.get('county') in ('București', 'Bucuresti', 'Ilfov'):
            by_suburb.append(loc)

    by_city_town = sorted(by_city_town, key=lambda x: x.get('name', ''))
    by_suburb = sorted(by_suburb, key=lambda x: x.get('name', ''))

    def loc_chip(name, linked_slug=None):
        if linked_slug and linked_slug in indexed_slugs:
            return f'<a href="/petreceri/{linked_slug}" class="loc-chip linked">{name}</a>'
        return f'<span class="loc-chip">{name}</span>'

    # Filtered cities/towns HTML (doar cele care chiar sunt in target + eventual altele fara link)
    cities_html = "\n      ".join(loc_chip(r.get('name',''), r.get('slug')) for r in by_city_town)
    
    # Suburbs
    suburbs_html = "\n      ".join(loc_chip(r.get('name',''), r.get('slug')) for r in by_suburb[:150])

    # Search Data: oras, cartier, orice are slug
    search_data = []
    for r in by_city_town:
        slug = r.get('slug')
        available = bool(slug and slug in indexed_slugs)
        search_data.append({"n": r.get('name',''), "t": "oraș/comună", "s": slug if available else ""})
        
    for r in by_suburb:
        slug = r.get('slug')
        available = bool(slug and slug in indexed_slugs)
        search_data.append({"n": r.get('name',''), "t": "cartier", "s": slug if available else ""})

    search_json = json.dumps(search_data, ensure_ascii=False)

    # PAGE GENERATION (ASTRO)
    parts = []
    parts.append('---')
    parts.append("import Layout from '../layouts/Layout.astro';")
    parts.append('')
    parts.append('const searchData = ' + search_json + ';')
    parts.append('const schema = JSON.stringify({')
    parts.append('  "@context": "https://schema.org",')
    parts.append('  "@graph": [')
    parts.append(f'    {{ "@type": "Service", "name": "Animatori Petreceri Copii — Arie Acoperire", "provider": {{ "@type": "LocalBusiness", "name": "SuperParty", "telephone": "+40722744377" }}, "areaServed": "București și Ilfov", "url": "{CANONICAL_HOST}/arie-acoperire" }},')
    parts.append('    { "@type": "BreadcrumbList", "itemListElement": [')
    parts.append(f'      {{ "@type": "ListItem", "position": 1, "name": "Acasă", "item": "{CANONICAL_HOST}" }},')
    parts.append(f'      {{ "@type": "ListItem", "position": 2, "name": "Animatori", "item": "{CANONICAL_HOST}/animatori-petreceri-copii" }},')
    parts.append(f'      {{ "@type": "ListItem", "position": 3, "name": "Arie Acoperire", "item": "{CANONICAL_HOST}/arie-acoperire" }}')
    parts.append('    ]}')
    parts.append('  ]')
    parts.append('});')
    parts.append('---')
    parts.append('')

    css = """<style>
  .ac-hero {padding:4rem 0 2.5rem; background:radial-gradient(ellipse at top,rgba(255,107,53,.1) 0%,transparent 55%);}
  .ac-hero h1 {font-size:clamp(1.8rem,4vw,2.8rem);font-weight:800;margin-bottom:1rem;}
  .ac-hero p {color:var(--text-muted);font-size:1.05rem;max-width:640px;line-height:1.8;margin-bottom:1.8rem;}
  .btn-p {background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;}
  .btn-wa {background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;}
  .ac-s {padding:3rem 0;} .ac-s-alt {padding:3rem 0;background:var(--dark-2);}
  .sec-title {font-size:1.5rem;font-weight:800;margin-bottom:.5rem;}
  .sec-sub {color:var(--text-muted);margin-bottom:1.5rem;font-size:.95rem;}
  .search-input {width:100%;max-width:500px;background:var(--dark-3);border:1px solid rgba(255,107,53,.3);color:var(--text);padding:.8rem 1.2rem;border-radius:10px;font-size:.95rem;outline:none;display:block;}
  .search-input:focus {border-color:var(--primary);}
  #search-results {margin-top:.8rem;display:flex;flex-wrap:wrap;gap:.5rem;min-height:1.5rem;}
  .judet-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:2rem;}
  .judet-card {background:var(--dark-3);border:1px solid rgba(255,107,53,.2);border-radius:14px;padding:1.2rem;text-decoration:none;color:var(--text);transition:border-color .2s;}
  .judet-card:hover {border-color:var(--primary);}
  .judet-card h3 {font-weight:700;margin-bottom:.3rem;color:var(--primary);font-size:.95rem;}
  .judet-card p {font-size:.82rem;color:var(--text-muted);}
  .loc-cloud {display:flex;flex-wrap:wrap;gap:.4rem;}
  .loc-chip {background:var(--dark-3);border:1px solid rgba(255,255,255,.07);border-radius:7px;padding:.3rem .7rem;font-size:.84rem;color:var(--text-muted);}
  .loc-chip.linked {border-color:rgba(255,107,53,.25);color:var(--text);text-decoration:none;transition:border-color .2s;}
  .loc-chip.linked:hover {border-color:var(--primary);}
  .show-more-btn {background:transparent;border:1px solid rgba(255,107,53,.3);color:var(--primary);padding:.4rem 1rem;border-radius:8px;cursor:pointer;font-size:.85rem;margin-top:.8rem;}
  .cta-box {background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.05));border:1px solid rgba(255,107,53,.25);border-radius:20px;padding:3rem 2rem;text-align:center;}
  .cta-box h2 {font-size:1.7rem;font-weight:800;margin-bottom:1rem;}
  .cta-box p {color:var(--text-muted);margin-bottom:2rem;}
  .cta-btns {display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;}
  .stat-bar {display:flex;gap:2rem;flex-wrap:wrap;margin-top:1.5rem;}
  .stat-item {font-size:.9rem;color:var(--text-muted);font-weight:600;}
</style>"""

    parts.append(css)
    parts.append('')

    parts.append('<section class="ac-hero">')
    parts.append('  <div class="container">')
    parts.append('    <h1>Zone <span style="color:var(--primary)">Acoperite</span></h1>')
    parts.append('    <p>SuperParty activează prioritar în <strong>București</strong> (toate sectoarele) și <strong>Ilfov</strong> (comune și orașe). La cerere, verificăm disponibilitatea și pentru zone limitrofe.</p>')
    parts.append('    <a href="tel:+40722744377" class="btn-p cta" style="margin-bottom:.8rem;">📞 Verificați: 0722 744 377</a>')
    parts.append('  </div>')
    parts.append('</section>')
    parts.append('')

    parts.append('<section class="ac-s">')
    parts.append('  <div class="container">')
    parts.append('    <h2 class="sec-title">Caută <span style="color:var(--primary)">localitatea ta</span></h2>')
    parts.append('    <p class="sec-sub">Scrie numele localității sau cartierului (ex: Voluntari, Floreasca, Chiajna):</p>')
    parts.append('    <input type="text" id="loc-search" class="search-input" placeholder="..." aria-label="Caută localitate"/>')
    parts.append('    <div id="search-results"></div>')
    parts.append('  </div>')
    parts.append('</section>')
    parts.append('')

    parts.append('<section class="ac-s-alt">')
    parts.append('  <div class="container">')
    parts.append('    <h2 class="sec-title">Hub-uri pe <span style="color:var(--primary)">județe</span></h2>')
    parts.append('    <p class="sec-sub">Zone prioritare și județe unde grupele noastre se deplasează cel mai frecvent:</p>')
    parts.append('    <div class="judet-grid">')
    judete = [
        ("bucuresti","📍 București","Toate sectoarele 1–6"),
        ("ilfov","📍 Ilfov","Voluntari, Otopeni, Bragadiru, Chiajna…"),
    ]
    for jslug, jname, jdesc in judete:
        parts.append(f'      <a href="/petreceri/{jslug}" class="judet-card"><h3>{jname}</h3><p>{jdesc}</p></a>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</section>')
    parts.append('')

    parts.append('<section class="ac-s">')
    parts.append('  <div class="container">')
    parts.append(f'    <h2 class="sec-title">Orașe și <span style="color:var(--primary)">Comune</span> ({len(by_city_town)})</h2>')
    parts.append('    <p class="sec-sub">Localități unde ajungem frecvent (cele cu <a href="#" style="color:var(--primary)">link</a> au oferte dedicate):</p>')
    parts.append('    <div class="loc-cloud">')
    parts.append('      ' + cities_html)
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</section>')
    parts.append('')

    parts.append('<section class="ac-s-alt">')
    parts.append('  <div class="container">')
    parts.append(f'    <h2 class="sec-title">Cartiere <span style="color:var(--primary)">București și Ilfov</span></h2>')
    parts.append(f'    <p class="sec-sub">Cartiere acoperite complet de echipa noastră:</p>')
    parts.append('    <div class="loc-cloud">')
    parts.append('      ' + suburbs_html)
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</section>')
    parts.append('')

    parts.append('<section class="ac-s">')
    parts.append('  <div class="container">')
    parts.append('    <div class="cta-box">')
    parts.append('      <h2>Nu ați găsit <span style="color:var(--primary)">zona dorită</span>?</h2>')
    parts.append('      <p>Adevărul este că ajungem oriunde ne chemați, la cerere! Sunați pentru detalii de deplasare.</p>')
    parts.append('      <div class="cta-btns">')
    parts.append('        <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>')
    parts.append('        <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>')
    parts.append('      </div>')
    parts.append('      <p style="margin-top:1rem;font-size:.9rem;color:var(--text-muted);">')
    parts.append('        ← <a href="/animatori-petreceri-copii" style="color:var(--primary);font-weight:600;">Pagina principală Animatori</a>')
    parts.append('      </p>')
    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</section>')
    parts.append('')

    parts.append('<script>')
    parts.append('  const _SD = ' + search_json + ';')
    parts.append('  const inp = document.getElementById("loc-search");')
    parts.append('  const res = document.getElementById("search-results");')
    parts.append('  inp.addEventListener("input", function() {')
    parts.append('    const q = this.value.toLowerCase().trim();')
    parts.append('    res.innerHTML = "";')
    parts.append('    if (q.length < 2) return;')
    parts.append('    const m = _SD.filter(d => d.n.toLowerCase().includes(q)).slice(0,10);')
    parts.append('    if (!m.length) { res.innerHTML = "<span style=\'color:var(--text-muted);font-size:.88rem;\'>Căutare extinsă... Mai bine sunați-ne.</span>"; return; }')
    parts.append('    m.forEach(d => {')
    parts.append('      const el = d.s ? document.createElement("a") : document.createElement("span");')
    parts.append('      el.textContent = d.n + (d.t ? " (" + d.t + ")" : "");')
    parts.append('      el.className = "loc-chip" + (d.s ? " linked" : "");')
    parts.append('      if (d.s) el.href = "/petreceri/" + d.s;')
    parts.append('      res.appendChild(el);')
    parts.append('    });')
    parts.append('  });')
    parts.append('</script>')
    
    content = "\n".join(parts)
    with open(OUT_PAGE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"DONE: UI curățat generat pt arie-acoperire.astro")

if __name__ == "__main__":
    main()
