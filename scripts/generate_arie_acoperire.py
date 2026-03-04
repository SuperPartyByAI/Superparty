import csv, json, re, unicodedata, os

def slugify(text):
    text = text.lower().strip()
    for r, e in {'ă':'a','â':'a','î':'i','ș':'s','ş':'s','ț':'t','ţ':'t'}.items():
        text = text.replace(r, e)
    text = unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')

rows = []
with open('reports/locations/bucuresti_100km_places.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        rows.append(r)

manifest = json.load(open('reports/seo/indexing_manifest.json', encoding='utf-8'))
indexed_slugs = {m['slug'] for m in manifest if m.get('indexable')}

by_city_town = sorted([r for r in rows if r['place'] in ('city','town')], key=lambda x: float(x.get('dist_km',999) or 999))
by_village   = sorted([r for r in rows if r['place'] == 'village'], key=lambda x: x.get('name',''))
by_suburb    = sorted([r for r in rows if r['place'] in ('suburb','neighbourhood')], key=lambda x: x.get('name',''))

def loc_chip(name):
    slug = slugify(name)
    if slug in indexed_slugs:
        return f'<a href="/petreceri/{slug}" class="loc-chip linked">{name}</a>'
    return f'<span class="loc-chip">{name}</span>'

cities_html  = "\n      ".join(loc_chip(r.get('name','')) for r in by_city_town)
suburbs_html = "\n      ".join(loc_chip(r.get('name','')) for r in by_suburb[:150])
villages_html= "\n      ".join(loc_chip(r.get('name','')) for r in by_village[:300])
villages_extra = "\n      ".join(loc_chip(r.get('name','')) for r in by_village[300:])
hamlets_html = "\n      ".join(loc_chip(r.get('name','')) for r in rows if r['place'] in ('hamlet','locality'))

# Search data JSON (doar city+town + suburb)
search_data = []
for r in by_city_town:
    nm = r.get('name','')
    sl = slugify(nm)
    available = sl in indexed_slugs
    search_data.append({"n": nm, "t": r.get('place',''), "s": sl if available else ""})
for r in by_suburb[:80]:
    nm = r.get('name','')
    sl = slugify(nm)
    available = sl in indexed_slugs
    search_data.append({"n": nm, "t": "cartier", "s": sl if available else ""})

search_json = json.dumps(search_data, ensure_ascii=False)

# Write page using string concatenation (avoid f-string JS conflicts)
parts = []
parts.append('---')
parts.append("import Layout from '../layouts/Layout.astro';")
parts.append('')
parts.append('const searchData = ' + search_json + ';')
parts.append('')
parts.append('const schema = JSON.stringify({')
parts.append('  "@context": "https://schema.org",')
parts.append('  "@graph": [')
parts.append('    { "@type": "Service", "name": "Animatori Petreceri Copii — Arie Acoperire", "provider": { "@type": "LocalBusiness", "name": "SuperParty", "telephone": "+40722744377" }, "areaServed": "București, Ilfov și ~100 km", "url": "https://superparty.ro/arie-acoperire" },')
parts.append('    { "@type": "BreadcrumbList", "itemListElement": [')
parts.append('      { "@type": "ListItem", "position": 1, "name": "Acasă", "item": "https://superparty.ro" },')
parts.append('      { "@type": "ListItem", "position": 2, "name": "Animatori", "item": "https://superparty.ro/animatori-petreceri-copii" },')
parts.append('      { "@type": "ListItem", "position": 3, "name": "Arie Acoperire", "item": "https://superparty.ro/arie-acoperire" }')
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

# Hero
parts.append('<section class="ac-hero">')
parts.append('  <div class="container">')
parts.append('    <h1>Zone <span style="color:var(--primary)">Acoperite</span></h1>')
parts.append(f'    <p>SuperParty activează în <strong>București</strong> (toate sectoarele), <strong>Ilfov</strong> și localități până la <strong>~100 km</strong> — Prahova, Dâmbovița, Giurgiu, Ialomița, Călărași, Teleorman. Verificăm disponibilitatea la cerere.</p>')
parts.append('    <a href="tel:+40722744377" class="btn-p cta" style="margin-bottom:.8rem;">📞 Verificați: 0722 744 377</a>')
parts.append('    <div class="stat-bar">')
parts.append(f'      <span class="stat-item">🏙️ {len(by_city_town)} orașe</span>')
parts.append(f'      <span class="stat-item">🏘️ {len(by_village)} sate</span>')
parts.append(f'      <span class="stat-item">🗺️ {len(by_suburb)} cartiere</span>')
parts.append(f'      <span class="stat-item">📍 Total: {len(rows)} localități OSM</span>')
parts.append('    </div>')
parts.append('  </div>')
parts.append('</section>')
parts.append('')

# Search
parts.append('<section class="ac-s">')
parts.append('  <div class="container">')
parts.append('    <h2 class="sec-title">Caută <span style="color:var(--primary)">localitatea ta</span></h2>')
parts.append('    <p class="sec-sub">Scrie numele localității pentru a vedea dacă suntem disponibili:</p>')
parts.append('    <input type="text" id="loc-search" class="search-input" placeholder="ex: Voluntari, Ploiești, Floreasca..." aria-label="Caută localitate"/>')
parts.append('    <div id="search-results"></div>')
parts.append('  </div>')
parts.append('</section>')
parts.append('')

# Judete
parts.append('<section class="ac-s-alt">')
parts.append('  <div class="container">')
parts.append('    <h2 class="sec-title">Hub-uri pe <span style="color:var(--primary)">județe</span></h2>')
parts.append('    <p class="sec-sub">Pagini dedicate cu informații și pachete specifice zonei:</p>')
parts.append('    <div class="judet-grid">')
judete = [
    ("bucuresti","📍 București","Toate sectoarele 1–6"),
    ("ilfov","📍 Ilfov","Voluntari, Otopeni, Bragadiru…"),
    ("prahova","📍 Prahova","Ploiești, Câmpina, Sinaia…"),
    ("dambovita","📍 Dâmbovița","Târgoviște, Titu, Găești…"),
    ("giurgiu","📍 Giurgiu","Giurgiu, Mihăilești, Bolintin…"),
    ("ialomita","📍 Ialomița","Urziceni, Slobozia, Fetești…"),
    ("calarasi","📍 Călărași","Oltenița, Fundulea, Lehliu…"),
    ("teleorman","📍 Teleorman","Videle, Alexandria…"),
]
for jslug, jname, jdesc in judete:
    parts.append(f'      <a href="/petreceri/{jslug}" class="judet-card"><h3>{jname}</h3><p>{jdesc}</p></a>')
parts.append('    </div>')
parts.append('  </div>')
parts.append('</section>')
parts.append('')

# Orase
parts.append('<section class="ac-s">')
parts.append('  <div class="container">')
parts.append(f'    <h2 class="sec-title">Orașe și <span style="color:var(--primary)">municipii</span> ({len(by_city_town)})</h2>')
parts.append('    <p class="sec-sub">Cele <a href="#" style="color:var(--primary)">subliniate</a> au pagini dedicate cu detalii locale:</p>')
parts.append('    <div class="loc-cloud">')
parts.append('      ' + cities_html)
parts.append('    </div>')
parts.append('  </div>')
parts.append('</section>')
parts.append('')

# Cartiere
parts.append('<section class="ac-s-alt">')
parts.append('  <div class="container">')
parts.append(f'    <h2 class="sec-title">Cartiere <span style="color:var(--primary)">București și Ilfov</span></h2>')
parts.append(f'    <p class="sec-sub">{len(by_suburb)} cartiere/zone identificate:</p>')
parts.append('    <div class="loc-cloud">')
parts.append('      ' + suburbs_html)
parts.append('    </div>')
parts.append('  </div>')
parts.append('</section>')
parts.append('')

# Sate
extra_count = len(by_village) - 300
parts.append('<section class="ac-s">')
parts.append('  <div class="container">')
parts.append(f'    <h2 class="sec-title">Comune și <span style="color:var(--primary)">sate</span> ({len(by_village)})</h2>')
parts.append('    <p class="sec-sub">Lista completă — cele cu link au pagini dedicate cu informații locale:</p>')
parts.append('    <div class="loc-cloud" id="villages-list">')
parts.append('      ' + villages_html)
parts.append('    </div>')
if extra_count > 0:
    parts.append(f'    <button class="show-more-btn" id="show-more-btn" onclick="document.getElementById(\'extra-v\').style.display=\'flex\';this.style.display=\'none\'">+ Afișează {extra_count} mai mult</button>')
    parts.append('    <div class="loc-cloud" id="extra-v" style="display:none;margin-top:.5rem;">')
    parts.append('      ' + villages_extra)
    parts.append('    </div>')
parts.append('  </div>')
parts.append('</section>')
parts.append('')

# CTA
parts.append('<section class="ac-s-alt">')
parts.append('  <div class="container">')
parts.append('    <div class="cta-box">')
parts.append('      <h2>Nu ați găsit <span style="color:var(--primary)">localitatea voastră</span>?</h2>')
parts.append('      <p>Contactați-ne direct — dacă suntem în raza de activitate, venim!</p>')
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

# Script search
parts.append('<script>')
parts.append('  const _SD = ' + search_json + ';')
parts.append('  const inp = document.getElementById("loc-search");')
parts.append('  const res = document.getElementById("search-results");')
parts.append('  inp.addEventListener("input", function() {')
parts.append('    const q = this.value.toLowerCase().trim();')
parts.append('    res.innerHTML = "";')
parts.append('    if (q.length < 2) return;')
parts.append('    const m = _SD.filter(d => d.n.toLowerCase().includes(q)).slice(0,10);')
parts.append('    if (!m.length) { res.innerHTML = "<span style=\'color:var(--text-muted);font-size:.88rem;\'>Localitate negăsită. Contactați-ne pentru confirmare.</span>"; return; }')
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
with open('src/pages/arie-acoperire.astro', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"DONE: /arie-acoperire.astro generat ({len(content)//1024}KB)")
print(f"  {len(by_city_town)} orase, {len(by_village)} sate, {len(by_suburb)} cartiere")
print(f"  Pagini indexabile link-uite: {len(indexed_slugs)}")
