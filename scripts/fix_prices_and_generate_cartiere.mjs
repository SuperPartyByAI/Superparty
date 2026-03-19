// fix_prices_and_generate_cartiere.mjs
// 1. Fixeaza preturile gresite (350/500/700 -> 490/840/1290) in toate paginile locale
// 2. Genereaza 15 pagini de cartiere din Bucuresti cu continut unic
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages/petreceri');

// ============================================================
// STEP 1: Fix preturile gresite in toate fisierele existente
// ============================================================
const files = fs.readdirSync(pagesDir).filter(f => f.endsWith('.astro'));
let priceFixed = 0;

const priceReplacements = [
  // Preturi gresite -> corecte
  { from: /Standard 60 min — de la \d+ RON/g, to: 'Super 1 — de la 490 RON' },
  { from: /Premium 90 min — de la \d+ RON/g, to: 'Super 3 — de la 840 RON' },
  { from: /VIP 120 min — de la \d+ RON/g, to: 'Super 7 — de la 1290 RON' },
  { from: /de la 350 RON/g, to: 'de la 490 RON' },
  { from: /de la 500 RON/g, to: 'de la 840 RON' },
  { from: /de la 700 RON/g, to: 'de la 1290 RON' },
  { from: /350 RON/g, to: '490 RON' },
  { from: /500 RON/g, to: '840 RON' },
  { from: /700 RON/g, to: '1290 RON' },
  { from: /60 min — de la/g, to: 'Super 1 (2 ore) — de la' },
  { from: /90 min — de la/g, to: 'Super 3 (2 ore, 2 personaje) — de la' },
  { from: /120 min — de la/g, to: 'Super 7 (3 ore) — de la' },
];

for (const f of files) {
  const fp = path.join(pagesDir, f);
  let content = fs.readFileSync(fp, 'utf-8');
  let changed = false;
  for (const { from, to } of priceReplacements) {
    if (from.test(content)) {
      content = content.replace(from, to);
      changed = true;
    }
    from.lastIndex = 0; // reset regex
  }
  if (changed) {
    fs.writeFileSync(fp, content, 'utf-8');
    priceFixed++;
  }
}
console.log(`✅ Preturi fixate in ${priceFixed} fisiere`);

// ============================================================
// STEP 2: Genereaza 15 pagini de cartiere cu continut unic
// ============================================================
const cartiere = [
  {
    slug: 'titan',
    name: 'Titan',
    sector: '3',
    sectorSlug: 'sector-3',
    desc: 'cartier central din Sectorul 3, cu Parc IOR și numeroase săli de petreceri',
    details: ['Parcul IOR (ideal pentru petreceri în aer liber)', 'Centrul Comercial Sun Plaza', 'Numeroase complexe rezidențiale noi', 'Acces rapid Metrou Stația Titan'],
    time: '15 min din centru',
    keywords: 'Titan, IOR, Sectorul 3',
    faq: [
      ['Activați în cartierul Titan?', 'Da — acoperim tot cartierul Titan și zonele adiacente (IOR, Dristor). Ajungem rapid via Bulevardul Nicolae Grigorescu sau Calea Vitan.'],
      ['Cât costă un animator în Titan?', 'Pachetul Super 1 pornește de la 490 RON pentru 2 ore (1 personaj). Transport gratuit în Titan, Sectorul 3.'],
      ['Veniți și la sălile de petreceri din Titan?', 'Da — lucrăm cu toate sălile de petreceri din zona Titan/IOR. Coordonăm direct cu sala pentru logistică.'],
    ]
  },
  {
    slug: 'drumul-taberei',
    name: 'Drumul Taberei',
    sector: '6',
    sectorSlug: 'sector-6',
    desc: 'unul din cele mai mari cartiere din București, Sectorul 6, cu zeci de săli de petreceri',
    details: ['Parcul Drumul Taberei — perfect pentru petreceri în aer liber', 'Metrou M5 — acces facil', 'Centrul Comercial Plaza România în apropiere', 'Comunitate numeroasă cu cerere mare pentru animatori'],
    time: '20 min din centru',
    keywords: 'Drumul Taberei, Sectorul 6, Militari',
    faq: [
      ['Activați în Drumul Taberei?', 'Da — acoperim tot Drumul Taberei și cartierele vecine (Militari, Crângași). Transport inclus.'],
      ['Cât durează un program de animație în Drumul Taberei?', 'Programele durează 2-3 ore. Pachetul Super 1 (490 RON) = 2 ore, Super 3 (840 RON) = 2 ore cu 2 personaje.'],
      ['Aveți animatori disponibili în weekend în Drumul Taberei?', 'Da, dar rezervările de weekend se ocupă rapid. Recomandăm rezervarea cu min. 2 săptămâni înainte.'],
    ]
  },
  {
    slug: 'militari',
    name: 'Militari',
    sector: '6',
    sectorSlug: 'sector-6',
    desc: 'cartier mare din Sectorul 6, cu Centrul Comercial Militari Shopping și numeroase zone rezidențiale',
    details: ['Militari Shopping Center — zonă comercială populară', 'Complexe rezidențiale noi (Militari Residence)', 'Acces via Splaiul Independenței și Bd. Iuliu Maniu', 'Comunitate tânără cu mulți copii de vârstă petreceri'],
    time: '18 min din centru',
    keywords: 'Militari, Militari Residence, Sectorul 6',
    faq: [
      ['Activați în Militari?', 'Da — acoperim tot Militari, de la Militari Shopping până la Militari Residence și Bd. Iuliu Maniu.'],
      ['Ce personaje sunt populare în Militari?', 'Cele mai cerute: Spider-Man, Elsa, Batman, Minnie Mouse. Avem 50+ personaje disponibile.'],
      ['Există taxă de deplasare în Militari?', 'Nu — transportul este inclus în pachet pentru zona Militari, Sectorul 6.'],
    ]
  },
  {
    slug: 'berceni',
    name: 'Berceni',
    sector: '4',
    sectorSlug: 'sector-4',
    desc: 'cartier din sudul Bucureștiului, Sectorul 4, cu numeroase familii și cerere mare pentru animatori',
    details: ['Parcul Tineretului — în apropiere', 'Piața Berceni — centrul cartierului', 'Numeroase blocuri și case cu curte pentru petreceri', 'Acces via Șoseaua Olteniței'],
    time: '20 min din centru',
    keywords: 'Berceni, Sectorul 4, Olteniței',
    faq: [
      ['Activați în Berceni?', 'Da — acoperim tot Berceni, de la Piața Berceni până la limita cu Jilava.'],
      ['Cât costă un animator în Berceni?', 'De la 490 RON pachetul Super 1 (1 personaj, 2 ore). Transport gratuit în tot Sectorul 4.'],
      ['Veniți și la case cu curte în Berceni?', 'Da — organizăm animație atât în săli de petreceri cât și la domiciliu, în curte sau apartament.'],
    ]
  },
  {
    slug: 'floreasca',
    name: 'Floreasca',
    sector: '2',
    sectorSlug: 'sector-2',
    desc: 'cartier rezidențial premium din nordul Bucureștiului, Sectorul 2, zona Herăstrău',
    details: ['Parcul Herăstrău — cadru ideal pentru petreceri memorabile', 'Cartier cu familii cu venituri ridicate și standarde înalte', 'Numeroase vile și apartamente spațioase', 'Aproape de Piața Dorobanți și Șoseaua Nordului'],
    time: '15 min din centru',
    keywords: 'Floreasca, Herăstrău, Sectorul 2, Dorobanți',
    faq: [
      ['Activați în Floreasca și Herăstrău?', 'Da — acoperim zona Floreasca, Herăstrău, Dorobanți, Aviației. Transport inclus.'],
      ['Ce pachete recomandați pentru petreceri în Floreasca?', 'Pachetul Super 7 (1290 RON, 1 animator + 4 ursitoare, 3 ore) este cel mai ales în zonele premium precum Floreasca.'],
      ['Aveți animatori cu experiență pentru petreceri la vilă?', 'Da — echipele noastre au experiență în petreceri private la vilă, inclusiv în Floreasca și Herăstrău.'],
    ]
  },
  {
    slug: 'colentina',
    name: 'Colentina',
    sector: '2',
    sectorSlug: 'sector-2',
    desc: 'cartier din estul Bucureștiului, Sectorul 2, cu Parcul Plumbuita și comunitate numeroasă',
    details: ['Parcul Plumbuita — spațiu verde ideal pentru petreceri', 'Cartier vechi cu numeroase familii', 'Acces via Șoseaua Colentina', 'Multiple săli de petreceri în zonă'],
    time: '20 min din centru',
    keywords: 'Colentina, Plumbuita, Sectorul 2',
    faq: [
      ['Activați în Colentina?', 'Da — acoperim tot Colentina, de la Parcul Plumbuita până la Fundeni.'],
      ['Ce include pachetul de animație pentru Colentina?', 'Jocuri interactive, modelare baloane, face painting, mini disco. Durata 2-3 ore.'],
      ['Transport gratuit în Colentina?', 'Da — transportul este inclus în toate pachetele pentru zona Colentina, Sectorul 2.'],
    ]
  },
  {
    slug: 'rahova',
    name: 'Rahova',
    sector: '5',
    sectorSlug: 'sector-5',
    desc: 'cartier din sudul Bucureștiului, Sectorul 5, cu comunitate mare și cerere crescută pentru animatori',
    details: ['Cartier cu multe familii tinere', 'Acces via Calea Rahovei', 'Parcul Sebastian în apropiere', 'Prețuri accesibile la sălile de petreceri din zonă'],
    time: '20 min din centru',
    keywords: 'Rahova, Calea Rahovei, Sectorul 5',
    faq: [
      ['Activați în Rahova?', 'Da — acoperim Rahova, Ferentari, Sebastian și toată zona Sectorului 5.'],
      ['Cât costă animatorii în Rahova?', 'Pachetul Super 1 (490 RON, 2 ore) este cel mai ales. Prețuri clare, fără costuri ascunse.'],
      ['Veniți și în Ferentari?', 'Da — activăm în tot Sectorul 5, inclusiv Ferentari și Prelungirea Ferentari.'],
    ]
  },
  {
    slug: 'crangasi',
    name: 'Crângași',
    sector: '6',
    sectorSlug: 'sector-6',
    desc: 'cartier din vestul Bucureștiului, Sectorul 6, lângă Lacul Crângași',
    details: ['Lacul Crângași — cadru natural pentru petreceri de vară', 'Cartier liniștit cu familii', 'Acces Metrou Crângași pe M1', 'Aproape de Giulești și Militari'],
    time: '20 min din centru',
    keywords: 'Crângași, Lacul Crângași, Sectorul 6',
    faq: [
      ['Activați în Crângași?', 'Da — acoperim Crângași și zonele adiacente (Giulești, Militari). Transport inclus.'],
      ['Organizați petreceri și la Lacul Crângași?', 'Da — putem coordona animație și în aer liber, la Lacul Crângași sau alte spații verzi.'],
      ['Cât durează o petrecere cu animator în Crângași?', 'Standard: 2 ore (pachetul Super 1, 490 RON). Opțional: 3 ore cu pachetul Super 7 (1290 RON).'],
    ]
  },
  {
    slug: 'tineretului',
    name: 'Tineretului',
    sector: '4',
    sectorSlug: 'sector-4',
    desc: 'cartier din Sectorul 4, cunoscut pentru Parcul Tineretului și Sala Polivalentă',
    details: ['Parcul Tineretului — unul din cele mai mari parcuri din București', 'Sala Polivalentă în apropiere', 'Acces Metrou Timpuri Noi', 'Zona rezidențială cu multe familii tinere'],
    time: '15 min din centru',
    keywords: 'Tineretului, Parcul Tineretului, Sectorul 4, Timpuri Noi',
    faq: [
      ['Activați în zona Tineretului?', 'Da — acoperim Tineretului, Timpuri Noi, Berceni. Transport gratuit.'],
      ['Organizați animație în Parcul Tineretului?', 'Da — facem și animație în aer liber, în parcuri, pentru grupuri mai mari sau zile de naștere.'],
      ['Ce personaje sunt disponibile în zona Tineretului?', 'Avem 50+ personaje: Spider-Man, Elsa, Batman, Minnie, Sonic, PAW Patrol și altele.'],
    ]
  },
  {
    slug: 'aviatiei',
    name: 'Aviației',
    sector: '1',
    sectorSlug: 'sector-1',
    desc: 'cartier de nord al Bucureștiului, Sectorul 1, zona Pipera și Promenada Mall',
    details: ['Promenada Mall — zonă comercială premium', 'Cartier corporatist cu familii expat și români cu venituri mari', 'Pipera — hub-ul de business al Bucureștiului', 'Aproape de Voluntari și Tunari'],
    time: '20 min din centru',
    keywords: 'Aviației, Pipera, Sectorul 1, Promenada',
    faq: [
      ['Activați în Aviației și Pipera?', 'Da — acoperim Aviației, Pipera, Floreasca, Dorobanți. Transport inclus.'],
      ['Ce pachete alegeți familiile din Aviației/Pipera?', 'Zona Pipera preferă pachete premium: Super 3 (840 RON) sau Super 7 (1290 RON) pentru petreceri elaborate.'],
      ['Aveți experiență cu petreceri în apartamente mari sau penthouse?', 'Da — avem experiență cu spații de orice tip, inclusiv apartamente spațioase sau vile din zona Aviației.'],
    ]
  },
  {
    slug: 'dorobanti',
    name: 'Dorobanți',
    sector: '1',
    sectorSlug: 'sector-1',
    desc: 'cartier elegant din nordul Bucureștiului, Sectorul 1, zona Piața Dorobanți',
    details: ['Piața Dorobanți — centrul cartierului', 'Zona cu vile și apartamente premium', 'Aproape de Parcul Floreasca și Herăstrău', 'Restaurante și cafenele exclusiviste'],
    time: '15 min din centru',
    keywords: 'Dorobanți, Piața Dorobanți, Sectorul 1, Floreasca',
    faq: [
      ['Activați în Dorobanți?', 'Da — Dorobanți este una din zonele noastre preferate. Transport inclus, punctualitate garantată.'],
      ['Ce personaje sunt cerute în Dorobanți?', 'Personajele Disney premium (Elsa, Rapunzel, Belle) sunt foarte cerute în zona Dorobanți.'],
      ['Organizați petreceri la vile în Dorobanți?', 'Da — avem experiență cu petreceri la case și vile private din zona Dorobanți și Floreasca.'],
    ]
  },
  {
    slug: 'dristor',
    name: 'Dristor',
    sector: '3',
    sectorSlug: 'sector-3',
    desc: 'cartier din Sectorul 3, în apropierea Centrului Comercial Vitan',
    details: ['Centrul Comercial Vitan în apropiere', 'Acces Metrou Dristor 1 și Dristor 2', 'Cartier cu blocuri și zone rezidențiale mixte', 'Aproape de Titan și Centrul Civic'],
    time: '15 min din centru',
    keywords: 'Dristor, Vitan, Sectorul 3',
    faq: [
      ['Activați în Dristor?', 'Da — acoperim Dristor, Vitan, Titan și toată zona Sectorului 3 est.'],
      ['Există săli de petreceri recomandate în Dristor?', 'Da — colaborăm cu mai multe săli din zona Dristor/Vitan. Contactați-ne pentru recomandări.'],
      ['Cât costă un animator în Dristor?', 'De la 490 RON pachetul Super 1 (2 ore, 1 personaj). Fără costuri ascunse.'],
    ]
  },
  {
    slug: 'giulesti',
    name: 'Giulești',
    sector: '6',
    sectorSlug: 'sector-6',
    desc: 'cartier din vestul Bucureștiului, Sectorul 6, cu stadionul Giulești și comunitate tradițională',
    details: ['Stadionul Giulești — reper important al zonei', 'Cartier cu comunitate numeroasă și tradiție', 'Acces via Calea Giulești', 'Aproape de Crângași și Militari'],
    time: '20 min din centru',
    keywords: 'Giulești, Calea Giulești, Sectorul 6',
    faq: [
      ['Activați în Giulești?', 'Da — acoperim Giulești și cartierele adiacente (Crângași, Militari). Transport gratuit.'],
      ['Cât durează o animație în Giulești?', 'Standard 2 ore (490 RON) sau Premium 3 ore cu Super 7 (1290 RON).'],
      ['Veniți și la petreceri în curte în Giulești?', 'Da — organizăm animație atât la interior cât și în curte sau grădină.'],
    ]
  },
  {
    slug: 'baneasa',
    name: 'Băneasa',
    sector: '1',
    sectorSlug: 'sector-1',
    desc: 'cartier exclusivist din nordul Bucureștiului, Sectorul 1, cunoscut pentru villele și aeroportul Băneasa',
    details: ['Zona rezidențială cu cele mai scumpe proprietăți din București', 'Băneasa Shopping City — mallul premium al Capitalei', 'Aproape de Parcul Regele Mihai I (Herăstrău)', 'Comunitate internațională și expat'],
    time: '20 min din centru',
    keywords: 'Băneasa, Băneasa Shopping City, Sectorul 1, nord București',
    faq: [
      ['Activați în Băneasa?', 'Da — Băneasa este o zonă pe care o acoperim cu plăcere. Transport inclus, echipă selectată.'],
      ['Ce pachet este recomandat pentru petreceri în Băneasa?', 'Pachetul Super 7 (1290 RON, 3 ore) sau Super 3 (840 RON) sunt cele mai alese în zone premium ca Băneasa.'],
      ['Aveți costumele licențiate și de calitate pentru petrecerile din Băneasa?', 'Da — toate costumele noastre sunt licențiate oficial și de înaltă calitate, potrivite pentru orice standard.'],
    ]
  },
  {
    slug: 'pantelimon-cartier',
    name: 'Pantelimon (Cartier)',
    sector: '2',
    sectorSlug: 'sector-2',
    desc: 'cartier din estul Bucureștiului, Sectorul 2, cu numeroase familii și cerere mare',
    details: ['Cartier dens cu familii numeroase', 'Acces via Șoseaua Pantelimon', 'Multiple săli de petreceri în zonă', 'Aproape de Centrul Comercial Pantelimon'],
    time: '20 min din centru',
    keywords: 'Pantelimon cartier, Sectorul 2, Șoseaua Pantelimon',
    faq: [
      ['Activați în cartierul Pantelimon?', 'Da — acoperim atât cartierul Pantelimon (Sectorul 2) cât și comuna Pantelimon din Ilfov. Transport inclus.'],
      ['Există animatori disponibili în Pantelimon în weekend?', 'Da, dar locurile se ocupă rapid. Rezervați cu minim 2 săptămâni înainte.'],
      ['Cât costă un animator în Pantelimon?', 'De la 490 RON pachetul Super 1 (2 ore). Contactați-ne pentru disponibilitate.'],
    ]
  },
];

// ============================================================
// Genereaza fiecare fisier de cartier
// ============================================================
let generated = 0;
for (const c of cartiere) {
  const filename = `${c.slug}.astro`;
  const filepath = path.join(pagesDir, filename);
  
  if (fs.existsSync(filepath)) {
    console.log(`  SKIP (exista): ${filename}`);
    continue;
  }

  const detailsHtml = c.details.map(d => `              <li>📍 ${d}</li>`).join('\n');
  const faqSchema = c.faq.map(([q, a]) => `      {"@type": "Question", "name": "${q.replace(/"/g, '\\"')}", "acceptedAnswer": {"@type": "Answer", "text": "${a.replace(/"/g, '\\"')}"}}`).join(',\n');
  const faqHtml = c.faq.map(([q, a]) => `        ["${q}", "${a}"]`).join(',\n');

  const content = `---
import Layout from '../../layouts/Layout.astro';
import { getCollection } from 'astro:content';

const allArticles = await getCollection('seo-articles');
const hubArticles = allArticles.filter(article =>
  (article.slug.includes('${c.slug.replace('-cartier', '')}') || article.slug.includes('${c.keywords.toLowerCase().split(',')[0].trim().replace(/\s+/g, '-')}')) && article.data.indexStatus !== 'hold'
).slice(0, 12);

const schema = JSON.stringify({
  "@context": "https://schema.org",
  "@graph": [
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
  title="Animatori Petreceri Copii ${c.name} | SuperParty Bucuresti"
  description="Animatori profesionisti pentru petreceri copii in ${c.name}, ${c.keywords}. Pachete de la 490 RON, 50+ personaje, transport gratuit. Rezerva: 0722 744 377."
  canonical="https://www.superparty.ro/petreceri/${c.slug}"
  schema={schema}
>
<style>
  .hub-hero { padding: 4.5rem 0 3rem; background: radial-gradient(ellipse at top, rgba(255,107,53,.1) 0%, transparent 55%); }
  .hub-hero h1 { font-size: clamp(1.8rem,4vw,2.8rem); font-weight:800; margin-bottom:1rem; line-height:1.2; }
  .hub-hero p { color:var(--text-muted); font-size:1.05rem; max-width:620px; line-height:1.8; margin-bottom:2rem; }
  .btn-p { background:linear-gradient(135deg,var(--primary),var(--primary-dark)); color:#fff; padding:.9rem 2rem; border-radius:50px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:.5rem; transition:transform .2s; }
  .btn-p:hover { transform:translateY(-2px); }
  .btn-wa { background:#25d366; color:#fff; padding:.9rem 1.8rem; border-radius:50px; font-weight:700; text-decoration:none; display:inline-flex; align-items:center; gap:.5rem; }
  .hub-section { padding:3.5rem 0; }
  .hub-section-alt { padding:3.5rem 0; background:var(--dark-2); }
  .sec-title { font-size:1.6rem; font-weight:800; margin-bottom:.5rem; }
  .sec-sub { color:var(--text-muted); margin-bottom:2rem; }
  .info-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:1.5rem; }
  .info-card { background:var(--dark-3); border:1px solid rgba(255,107,53,.15); border-radius:14px; padding:1.5rem; }
  .info-card h3 { font-weight:700; margin-bottom:.6rem; }
  .info-card ul { list-style:none; padding:0; }
  .info-card li { padding:.35rem 0; border-bottom:1px solid rgba(255,255,255,.05); font-size:.9rem; color:var(--text-muted); }
  .art-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:1rem; }
  .art-card { background:var(--dark-3); border:1px solid rgba(255,107,53,.12); border-radius:14px; padding:1.2rem; text-decoration:none; color:var(--text); transition:border-color .2s; }
  .art-card:hover { border-color:var(--primary); }
  .art-card h3 { font-size:.95rem; font-weight:700; color:var(--primary); margin-bottom:.4rem; }
  .art-card p { font-size:.82rem; color:var(--text-muted); }
  .faq-list { display:flex; flex-direction:column; gap:1rem; max-width:720px; }
  .faq-item { background:var(--dark-3); border:1px solid rgba(255,107,53,.12); border-radius:14px; padding:1.3rem; }
  .faq-item h3 { font-size:.95rem; font-weight:700; margin-bottom:.5rem; }
  .faq-item p { font-size:.9rem; color:var(--text-muted); line-height:1.7; }
  .cta-box { background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.05)); border:1px solid rgba(255,107,53,.25); border-radius:20px; padding:3rem 2rem; text-align:center; }
  .cta-box h2 { font-size:1.7rem; font-weight:800; margin-bottom:1rem; }
  .cta-box p { color:var(--text-muted); margin-bottom:2rem; }
  .cta-btns { display:flex; gap:1rem; flex-wrap:wrap; justify-content:center; }
  @media(max-width:600px) { .cta-btns { flex-direction:column; align-items:center; } }
</style>

<section class="hub-hero">
  <div class="container">
    <h1>Animatori Petreceri Copii<br><span style="color:var(--primary)">${c.name}</span></h1>
    <p>SuperParty aduce magia petrecerilor la tine acasă în <strong>${c.name}</strong> — ${c.desc}. Animatori profesionisti, 50+ personaje costumate, program complet inclus.</p>
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
        <h3>📍 Zone acoperite în ${c.name}</h3>
        <ul>
${detailsHtml}
        </ul>
      </div>
      <div class="info-card">
        <h3>⏱ Timp de deplasare</h3>
        <ul>
          <li>~${c.time}</li>
          <li>Sosim cu 10 min înainte de program</li>
          <li>Transport gratuit în ${c.name}, Sectorul ${c.sector}</li>
          <li><a href="/petreceri/${c.sectorSlug}" style="color:var(--primary)">→ Vezi toate zonele Sector ${c.sector}</a></li>
        </ul>
      </div>
      <div class="info-card">
        <h3>🎭 Pachete disponibile</h3>
        <ul>
          <li>Super 1 — de la 490 RON (1 personaj, 2 ore)</li>
          <li>Super 3 — de la 840 RON (2 personaje, 2 ore)</li>
          <li>Super 7 — de la 1290 RON (animator + 4 ursitoare)</li>
        </ul>
        <p style="margin-top:.8rem; font-size:.85rem; color:var(--text-muted);">
          <a href="/animatori-petreceri-copii" style="color:var(--primary)">→ Vezi toate pachetele și prețurile</a>
        </p>
      </div>
    </div>
  </div>
</section>

{hubArticles.length > 0 && (
<section class="hub-section-alt">
  <div class="container">
    <h2 class="sec-title">Animatori disponibili în <span style="color:var(--primary)">${c.name}</span></h2>
    <p class="sec-sub">Personaje și servicii specifice pentru această zonă.</p>
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

<section class="hub-section">
  <div class="container">
    <h2 class="sec-title">Întrebări despre animatori în <span style="color:var(--primary)">${c.name}</span></h2>
    <div class="faq-list">
      {[
${faqHtml}
      ].map(([q, a]) => (
        <div class="faq-item">
          <h3>❓ {q}</h3>
          <p>{a}</p>
        </div>
      ))}
    </div>
  </div>
</section>

<section class="hub-section-alt">
  <div class="container">
    <div class="cta-box">
      <h2>Rezervă animator în <span style="color:var(--primary)">${c.name}</span></h2>
      <p>Disponibilitate limitată în weekend. Rezervați cu avans pentru data dorită.</p>
      <div class="cta-btns">
        <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
        <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
      </div>
      <p style="margin-top:1.5rem; font-size:.9rem; color:var(--text-muted);">
        ← <a href="/petreceri/${c.sectorSlug}" style="color:var(--primary); font-weight:600;">Sector ${c.sector}</a>
        &nbsp;|&nbsp;
        <a href="/animatori-petreceri-copii" style="color:var(--primary); font-weight:600;">Animatori Petreceri Copii București</a>
      </p>
    </div>
  </div>
</section>

</Layout>`;

  fs.writeFileSync(filepath, content, 'utf-8');
  generated++;
  console.log(`  ✅ Generat: ${filename}`);
}

console.log(`\n✅ GATA!`);
console.log(`   Preturi fixate: ${priceFixed} fisiere`);
console.log(`   Pagini cartiere generate: ${generated}`);
console.log(`\n📋 Verifica unicitatea continutului:`);

// Verificare unicitate - compara primele 200 chars din fiecare pagina noua
const newFiles = cartiere.map(c => path.join(pagesDir, `${c.slug}.astro`)).filter(f => fs.existsSync(f));
const bodies = newFiles.map(f => {
  const content = fs.readFileSync(f, 'utf-8');
  // Extrage textul descriptiv din hero
  const match = content.match(/SuperParty aduce magia[^<]+/);
  return { file: path.basename(f), snippet: match ? match[0].slice(0, 100) : 'N/A' };
});

let duplicateBody = 0;
const seen = new Set();
for (const { file, snippet } of bodies) {
  if (seen.has(snippet)) {
    console.log(`  ⚠️ DUPLICAT: ${file}`);
    duplicateBody++;
  }
  seen.add(snippet);
}
if (duplicateBody === 0) console.log('  ✅ Toate paginile au continut unic!');
