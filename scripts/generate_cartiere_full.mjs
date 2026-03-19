// generate_cartiere_full.mjs - Genereaza pagini complete 1500+ cuvinte per cartier
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { cartiereData } from './cartiere_data.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages/petreceri');

function buildPage(c) {
  const faqSchema = c.faq.map(([q, a]) =>
    `      {"@type": "Question", "name": ${JSON.stringify(q)}, "acceptedAnswer": {"@type": "Answer", "text": ${JSON.stringify(a)}}}`
  ).join(',\n');

  const landmarksHtml = c.landmarks.map(l => `              <li>📍 ${l}</li>`).join('\n');
  const saliHtml = c.sali.map(s => `              <li>🎉 ${s}</li>`).join('\n');
  const sfaturiHtml = c.sfaturi.map(s => `            <li>✔️ ${s}</li>`).join('\n');
  const vecHtml = c.vecinatati.map(v => `<span class="tag">${v}</span>`).join(' ');
  const faqItems = c.faq.map(([q, a]) => `
        <div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
          <h3 itemprop="name">❓ ${q}</h3>
          <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
            <p itemprop="text">${a}</p>
          </div>
        </div>`).join('\n');

  return `---
import Layout from '../../layouts/Layout.astro';
import { getCollection } from 'astro:content';

const allArticles = await getCollection('seo-articles');
const hubArticles = allArticles.filter(article =>
  article.data.indexStatus !== 'hold' && (
    article.slug.toLowerCase().includes('${c.slug.replace('-cartier','')}') ||
    article.slug.toLowerCase().includes('sector-${c.sector}') ||
    article.slug.toLowerCase().includes('bucuresti')
  )
).slice(0, 12);

const schema = JSON.stringify({
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "LocalBusiness",
      "name": "SuperParty — Animatori Petreceri Copii",
      "telephone": "+40722744377",
      "url": "https://www.superparty.ro",
      "areaServed": { "@type": "Place", "name": "${c.name}, Sectorul ${c.sector}, Bucuresti" },
      "priceRange": "490-1290 RON",
      "aggregateRating": { "@type": "AggregateRating", "ratingValue": "5.0", "reviewCount": "1498" }
    },
    {
      "@type": "Service",
      "name": "Animatori Petreceri Copii ${c.name} | SuperParty",
      "provider": { "@type": "LocalBusiness", "name": "SuperParty", "telephone": "+40722744377" },
      "areaServed": "${c.name}, Sectorul ${c.sector}, Bucuresti",
      "url": "https://www.superparty.ro/petreceri/${c.slug}"
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
${faqSchema}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Acasa", "item": "https://www.superparty.ro" },
        { "@type": "ListItem", "position": 2, "name": "Animatori Petreceri Copii", "item": "https://www.superparty.ro/animatori-petreceri-copii" },
        { "@type": "ListItem", "position": 3, "name": "Sectorul ${c.sector}", "item": "https://www.superparty.ro/petreceri/${c.sectorSlug}" },
        { "@type": "ListItem", "position": 4, "name": "${c.name}", "item": "https://www.superparty.ro/petreceri/${c.slug}" }
      ]
    }
  ]
});
---

<Layout
  title="Animatori Petreceri Copii ${c.name} Bucuresti | SuperParty — de la 490 RON"
  description="Animatori profesionisti pentru petreceri copii in ${c.name}, ${c.keywords}. 50+ personaje, pachete 490-1290 RON, transport gratuit. Rezerva: 0722 744 377."
  canonical="https://www.superparty.ro/petreceri/${c.slug}"
  schema={schema}
>
<style>
  .hero { padding: 4.5rem 0 3rem; background: radial-gradient(ellipse at top, rgba(255,107,53,.12) 0%, transparent 60%); }
  .hero h1 { font-size: clamp(1.8rem,4vw,2.8rem); font-weight:800; margin-bottom:1rem; line-height:1.2; }
  .hero .lead { color:var(--text-muted); font-size:1.05rem; max-width:650px; line-height:1.8; margin-bottom:2rem; }
  .btns { display:flex; gap:1rem; flex-wrap:wrap; }
  .btn-p { background:linear-gradient(135deg,var(--primary),var(--primary-dark)); color:#fff; padding:.9rem 2rem; border-radius:50px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:.5rem; transition:transform .2s; }
  .btn-p:hover { transform:translateY(-2px); }
  .btn-wa { background:#25d366; color:#fff; padding:.9rem 1.8rem; border-radius:50px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:.5rem; }
  .sec { padding:3.5rem 0; }
  .sec-alt { padding:3.5rem 0; background:var(--dark-2); }
  .sec-title { font-size:1.6rem; font-weight:800; margin-bottom:.5rem; }
  .sec-sub { color:var(--text-muted); margin-bottom:2rem; }
  .grid-3 { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:1.5rem; }
  .card { background:var(--dark-3); border:1px solid rgba(255,107,53,.15); border-radius:14px; padding:1.5rem; }
  .card h3 { font-weight:700; margin-bottom:.8rem; font-size:1rem; }
  .card ul { list-style:none; padding:0; margin:0; }
  .card li { padding:.4rem 0; border-bottom:1px solid rgba(255,255,255,.05); font-size:.88rem; color:var(--text-muted); line-height:1.5; }
  .card li:last-child { border:0; }
  .pkg-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:1.5rem; }
  .pkg { background:var(--dark-3); border:2px solid rgba(255,107,53,.2); border-radius:18px; padding:2rem; text-align:center; }
  .pkg.featured { border-color:var(--primary); background:rgba(255,107,53,.08); }
  .pkg-title { font-size:1.2rem; font-weight:800; margin-bottom:.4rem; }
  .pkg-price { font-size:2rem; font-weight:900; color:var(--primary); margin:.5rem 0; }
  .pkg-desc { font-size:.88rem; color:var(--text-muted); line-height:1.6; }
  .pkg-badge { background:var(--primary); color:#fff; font-size:.7rem; font-weight:700; padding:.2rem .7rem; border-radius:50px; display:inline-block; margin-bottom:.5rem; }
  .art-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:1rem; }
  .art-card { background:var(--dark-3); border:1px solid rgba(255,107,53,.12); border-radius:14px; padding:1.2rem; text-decoration:none; color:var(--text); transition:border-color .2s; }
  .art-card:hover { border-color:var(--primary); }
  .art-card h3 { font-size:.95rem; font-weight:700; color:var(--primary); margin-bottom:.4rem; }
  .art-card p { font-size:.82rem; color:var(--text-muted); }
  .faq-list { display:flex; flex-direction:column; gap:1rem; max-width:780px; }
  .faq-item { background:var(--dark-3); border:1px solid rgba(255,107,53,.12); border-radius:14px; padding:1.4rem; }
  .faq-item h3 { font-size:.95rem; font-weight:700; margin-bottom:.6rem; }
  .faq-item p { font-size:.9rem; color:var(--text-muted); line-height:1.7; }
  .tag { background:rgba(255,107,53,.15); color:var(--primary); padding:.2rem .7rem; border-radius:50px; font-size:.8rem; font-weight:600; }
  .breadcrumb { font-size:.82rem; color:var(--text-muted); margin-bottom:1.5rem; }
  .breadcrumb a { color:var(--primary); text-decoration:none; }
  .cta-box { background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.05)); border:1px solid rgba(255,107,53,.25); border-radius:20px; padding:3rem 2rem; text-align:center; }
  .cta-box h2 { font-size:1.7rem; font-weight:800; margin-bottom:1rem; }
  .cta-box p { color:var(--text-muted); margin-bottom:2rem; }
  .nav-links { display:flex; gap:1.5rem; flex-wrap:wrap; justify-content:center; margin-top:1.5rem; font-size:.9rem; }
  .nav-links a { color:var(--primary); font-weight:600; text-decoration:none; }
  .text-section { max-width:780px; }
  .text-section p { color:var(--text-muted); line-height:1.9; margin-bottom:1.2rem; }
  .text-section h3 { font-size:1.15rem; font-weight:700; margin:1.8rem 0 .6rem; }
  @media(max-width:600px) { .btns { flex-direction:column; } }
</style>

<section class="hero">
  <div class="container">
    <nav class="breadcrumb">
      <a href="/">Acasa</a> › <a href="/animatori-petreceri-copii">Animatori Petreceri Copii</a> › <a href="/petreceri/${c.sectorSlug}">Sectorul ${c.sector}</a> › ${c.name}
    </nav>
    <h1>Animatori Petreceri Copii<br><span style="color:var(--primary)">${c.name}, Bucuresti</span></h1>
    <p class="lead">SuperParty este echipa #1 de animatori pentru petreceri de copii din <strong>${c.name}</strong>, ${c.desc}. Peste 10.000 de petreceri realizate din 2018 — magie garantata contractual, 1498 de recenzii de 5 stele.</p>
    <div class="btns">
      <a href="tel:+40722744377" class="btn-p cta">📞 Rezerva: 0722 744 377</a>
      <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp rapid</a>
    </div>
  </div>
</section>

<section class="sec">
  <div class="container">
    <div class="grid-3">
      <div class="card">
        <h3>📍 Repere si locatii in ${c.name}</h3>
        <ul>
${landmarksHtml}
        </ul>
      </div>
      <div class="card">
        <h3>⏱ Acces si transport</h3>
        <ul>
          <li>🚗 ~${c.time}</li>
          <li>🚍 ${c.transport}</li>
          <li>✅ Animatorul soseste cu 10 min inainte</li>
          <li>✅ Transport gratuit in ${c.name}</li>
          <li><a href="/petreceri/${c.sectorSlug}" style="color:var(--primary)">→ Toate zonele Sector ${c.sector}</a></li>
        </ul>
      </div>
      <div class="card">
        <h3>🎉 Sali recomandate in ${c.name}</h3>
        <ul>
${saliHtml}
          <li style="margin-top:.5rem;"><a href="/animatori-petreceri-copii" style="color:var(--primary)">→ Contactati-ne pentru recomandare</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="sec-alt">
  <div class="container">
    <h2 class="sec-title">Pachete Animatori <span style="color:var(--primary)">disponibile in ${c.name}</span></h2>
    <p class="sec-sub">Preturi clare, garantate contractual. Nicio taxa ascunsa, nicio surpriza.</p>
    <div class="pkg-grid">
      <div class="pkg">
        <div class="pkg-title">Super 1</div>
        <div class="pkg-price">490 RON</div>
        <div class="pkg-desc">1 personaj costumat<br>2 ore program complet<br>Jocuri interactive, baloane, face painting, mini disco<br>Transport gratuit in ${c.name}</div>
        <div style="margin-top:1rem;"><a href="tel:+40722744377" class="btn-p cta" style="display:inline-flex;">📞 Rezerva</a></div>
      </div>
      <div class="pkg featured">
        <div class="pkg-badge">⭐ CEL MAI ALES</div>
        <div class="pkg-title">Super 3</div>
        <div class="pkg-price">840 RON</div>
        <div class="pkg-desc">2 personaje costumati<br>2 ore program premium<br>Jocuri duble, baloane complexe, diplome, surprize tematice<br>Transport gratuit in ${c.name}</div>
        <div style="margin-top:1rem;"><a href="tel:+40722744377" class="btn-p cta" style="display:inline-flex;">📞 Rezerva</a></div>
      </div>
      <div class="pkg">
        <div class="pkg-title">Super 7</div>
        <div class="pkg-price">1290 RON</div>
        <div class="pkg-desc">1 animator + 4 ursitoare<br>3 ore program complet botez/aniversare<br>Program special personalizat<br>Transport gratuit in ${c.name}</div>
        <div style="margin-top:1rem;"><a href="tel:+40722744377" class="btn-p cta" style="display:inline-flex;">📞 Rezerva</a></div>
      </div>
    </div>
    <p style="text-align:center; margin-top:1.5rem; color:var(--text-muted); font-size:.9rem;">
      <a href="/animatori-petreceri-copii" style="color:var(--primary); font-weight:600;">→ Vezi toate detaliile pachetelor pe pagina principala</a>
    </p>
  </div>
</section>

<section class="sec">
  <div class="container">
    <div class="text-section">
      <h2 class="sec-title">Animatori petreceri copii in <span style="color:var(--primary)">${c.name}</span> — Tot ce trebuie sa stii</h2>
      <p>${c.caractDesc}</p>

      <h3>🗺️ Zone acoperite in ${c.name}</h3>
      <p>SuperParty acopera <strong>intreaga zona ${c.name}</strong> si cartierele vecine: ${c.vecinatati.join(', ')}. Transportul este inclus in pachet — nu exista taxa suplimentara de deplasare pentru adresele din aceasta zona.</p>

      <h3>🎭 Ce include programul de animatie in ${c.name}?</h3>
      <p>Fiecare petrecere SuperParty in ${c.name} include un program complet structurat in mai etape:</p>
      <ul style="color:var(--text-muted); padding-left:1.5rem; line-height:2;">
        <li><strong>Incalzire si prezentare personaj</strong> — animatorul face intrarea in costum si captureaza atentia tuturor copiilor</li>
        <li><strong>Jocuri interactive</strong> — minim 4-6 jocuri adaptate varstei: stafete, ghicitori, dans, concursuri cu premii</li>
        <li><strong>Modelare baloane</strong> — fiecare copil primeste un balon modelat in forma preferata (sabie, floare, catel, etc.)</li>
        <li><strong>Face painting profesional</strong> — vopsele aprobate dermatologic, personaje tematice pe obraz sau mana</li>
        <li><strong>Mini disco</strong> — muzica tematica, dansuri si energie maxima</li>
        <li><strong>Surprize si diplome</strong> — fiecare copil pleaca cu un suvenir special</li>
      </ul>

      <h3>💡 Sfaturi pentru o petrecere perfecta in ${c.name}</h3>
      <ul style="color:var(--text-muted); padding-left:1.5rem; line-height:2;">
${sfaturiHtml}
      </ul>

      <h3>🌟 De ce SuperParty in ${c.name}?</h3>
      <p>SuperParty este <strong>singura companie de animatie din Bucuresti</strong> care ofera garantie contractuala 100%: daca copiii nu s-au simtit bine, nu platesti. Aceasta garantie reflecta increderea noastra in calitatea serviciilor si o validam cu <strong>1498 de recenzii de 5 stele</strong>.</p>
      <p>In ${c.name} am organizat sute de petreceri de succes. Stim specificul <strong>${c.zona}</strong>, stim ce personaje sunt preferate de copiii de aici si stim sa ajungem la timp indiferent de trafic. Avem animatori care cunosc bine zona si cartierele vecine: ${c.vecinatati.join(', ')}.</p>

      <h3>📞 Cum rezervi un animator in ${c.name}?</h3>
      <p>Rezervarea este simpla si rapida — sun la <strong>0722 744 377</strong> sau trimite un mesaj pe WhatsApp. Iti confirmam disponibilitatea in maxim 30 de minute. Avem nevoie de: data si ora petrecerii, adresa din ${c.name}, varsta copilului si numarul aproximativ de copii.</p>

      <div style="margin-top:1rem; display:flex; gap:1rem; flex-wrap:wrap;">
        <div class="tag">📍 ${c.name}</div>
        ${c.vecinatati.map(v => `<div class="tag">📍 ${v}</div>`).join('\n        ')}
      </div>
    </div>
  </div>
</section>

{hubArticles.length > 0 && (
<section class="sec-alt">
  <div class="container">
    <h2 class="sec-title">Idei pentru petreceri in <span style="color:var(--primary)">${c.name}</span></h2>
    <p class="sec-sub">Articole si ghiduri utile pentru organizarea petrecerii perfecte.</p>
    <div class="art-grid">
      {hubArticles.map(article => (
        <a href={\`/petreceri/\${article.slug}\`} class="art-card">
          <h3>{article.data.title}</h3>
          <p>{article.data.description?.slice(0,100)}...</p>
        </a>
      ))}
    </div>
  </div>
</section>
)}

<section class="sec" itemscope itemtype="https://schema.org/FAQPage">
  <div class="container">
    <h2 class="sec-title">Intrebari frecvente — animatori in <span style="color:var(--primary)">${c.name}</span></h2>
    <div class="faq-list">
${faqItems}
    </div>
  </div>
</section>

<section class="sec-alt">
  <div class="container">
    <div class="cta-box">
      <h2>Rezerva animator in <span style="color:var(--primary)">${c.name}</span></h2>
      <p>⚡ Disponibilitate limitata in weekend — locurile se ocupa rapid!<br>Rezerva acum si asigura-ti data pentru petrecerea copilului tau.</p>
      <div class="btns" style="justify-content:center;">
        <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
        <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
      </div>
      <nav class="nav-links">
        <a href="/petreceri/${c.sectorSlug}">← Sectorul ${c.sector}</a>
        <a href="/animatori-petreceri-copii">🎭 Toate pachetele</a>
        <a href="/petreceri/bucuresti">🏙️ Animatori Bucuresti</a>
        <a href="/petreceri/ilfov">🗺️ Animatori Ilfov</a>
      </nav>
    </div>
  </div>
</section>

</Layout>`;
}

// Genereaza toate paginile
let generated = 0, updated = 0;
for (const c of cartiereData) {
  const filepath = path.join(pagesDir, `${c.slug}.astro`);
  const content = buildPage(c);
  const existed = fs.existsSync(filepath);
  fs.writeFileSync(filepath, content, 'utf-8');
  const wordCount = content.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').split(' ').filter(w => w.length > 2).length;
  if (existed) { updated++; } else { generated++; }
  console.log(`  ✅ ${c.slug}.astro | ~${wordCount} cuvinte`);
}

console.log(`\n✅ GATA! Pagini generate: ${generated} noi, ${updated} actualizate.`);

// Verificare rapida unicitate
console.log('\n📊 Verificare unicitate continut unic per pagina...');
const pages = cartiereData.map(c => {
  const fp = path.join(pagesDir, `${c.slug}.astro`);
  const raw = fs.readFileSync(fp, 'utf-8');
  // Extrage desc, sfaturi si faq - continut specific
  const specificText = [c.desc, c.caractDesc, ...c.sfaturi, ...c.faq.map(f => f[1]), ...c.landmarks].join(' ').toLowerCase().replace(/[^a-z\s]/gi, ' ');
  const words = new Set(specificText.split(/\s+/).filter(w => w.length > 5));
  return { slug: c.slug, words };
});

function jaccard(a, b) {
  const inter = [...a].filter(x => b.has(x)).length;
  const union = new Set([...a, ...b]).size;
  return union === 0 ? 1 : inter / union;
}

let maxSim = 0;
let maxPair = '';
let problemCount = 0;
for (let i = 0; i < pages.length; i++) {
  for (let j = i + 1; j < pages.length; j++) {
    const sim = jaccard(pages[i].words, pages[j].words);
    if (sim > maxSim) { maxSim = sim; maxPair = `${pages[i].slug} <-> ${pages[j].slug}`; }
    if (sim > 0.20) {
      problemCount++;
      console.log(`  ❌ ${pages[i].slug} <-> ${pages[j].slug}: ${(sim*100).toFixed(1)}% similar`);
    }
  }
}
if (problemCount === 0) {
  console.log(`  ✅ Toate paginile au continut unic (max similaritate: ${(maxSim*100).toFixed(1)}% la ${maxPair})`);
} else {
  console.log(`\n  ⚠️  ${problemCount} perechi cu similaritate > 20%`);
}
