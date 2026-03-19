// fix_seo_final.mjs — Fix toate problemele rămase din audit:
// 1. Regenerare sitemap cu toate cele 43 pagini indexate
// 2. Schema LocalBusiness pe paginile de servicii (10 pagini fără schema)
// 3. Scurtare titluri lungi >65 caractere (15 pagini)
// 4. Fixare meta description prea lungi >160 caractere
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

// ─────────────────────────────────────────────────────────────────
// 1. REGENERARE SITEMAP XML
// ─────────────────────────────────────────────────────────────────
// Toate paginile indexate (fara noindex) — URL finale pe superparty.ro
const INDEXED_URLS = [
  'https://www.superparty.ro/',
  'https://www.superparty.ro/animatori-petreceri-copii/',
  'https://www.superparty.ro/animatori-copii-bucuresti/',
  'https://www.superparty.ro/recenzii/',
  'https://www.superparty.ro/galerie/',
  'https://www.superparty.ro/contact/',
  'https://www.superparty.ro/piniata/',
  'https://www.superparty.ro/arcade-baloane/',
  'https://www.superparty.ro/baloane-cu-heliu/',
  'https://www.superparty.ro/decoratiuni-baloane/',
  'https://www.superparty.ro/mos-craciun-de-inchiriat/',
  'https://www.superparty.ro/vata-de-zahar-si-popcorn/',
  'https://www.superparty.ro/ursitoare-botez/',
  // Petreceri — sectoare
  'https://www.superparty.ro/petreceri/sector-1/',
  'https://www.superparty.ro/petreceri/sector-2/',
  'https://www.superparty.ro/petreceri/sector-3/',
  'https://www.superparty.ro/petreceri/sector-4/',
  'https://www.superparty.ro/petreceri/sector-5/',
  'https://www.superparty.ro/petreceri/sector-6/',
  // Petreceri — cartiere bucuresti
  'https://www.superparty.ro/petreceri/aviatiei/',
  'https://www.superparty.ro/petreceri/berceni/',
  'https://www.superparty.ro/petreceri/colentina/',
  'https://www.superparty.ro/petreceri/crangasi/',
  'https://www.superparty.ro/petreceri/dorobanti/',
  'https://www.superparty.ro/petreceri/dristor/',
  'https://www.superparty.ro/petreceri/drumul-taberei/',
  'https://www.superparty.ro/petreceri/floreasca/',
  'https://www.superparty.ro/petreceri/giulesti/',
  'https://www.superparty.ro/petreceri/militari/',
  'https://www.superparty.ro/petreceri/pantelimon-cartier/',
  'https://www.superparty.ro/petreceri/rahova/',
  'https://www.superparty.ro/petreceri/tineretului/',
  'https://www.superparty.ro/petreceri/titan/',
  // Petreceri — orase/comune
  'https://www.superparty.ro/petreceri/bucuresti/',
  'https://www.superparty.ro/petreceri/ilfov/',
  'https://www.superparty.ro/petreceri/otopeni/',
  'https://www.superparty.ro/petreceri/voluntari/',
  'https://www.superparty.ro/petreceri/bragadiru/',
  'https://www.superparty.ro/petreceri/buftea/',
  'https://www.superparty.ro/petreceri/chiajna/',
  'https://www.superparty.ro/petreceri/calarasi/',
  'https://www.superparty.ro/petreceri/giurgiu/',
  'https://www.superparty.ro/petreceri/popesti-leordeni/',
];

const today = new Date().toISOString().slice(0, 10);

// Priority și changefreq per tip pagina
function getPriority(url) {
  if (url === 'https://www.superparty.ro/') return '1.0';
  if (url.includes('animatori-petreceri-copii')) return '0.95';
  if (url.includes('animatori-copii-bucuresti')) return '0.9';
  if (url.includes('/sector-')) return '0.85';
  if (url.includes('/petreceri/')) return '0.8';
  return '0.7';
}

function getFreq(url) {
  if (url === 'https://www.superparty.ro/') return 'weekly';
  if (url.includes('recenzii')) return 'weekly';
  if (url.includes('/petreceri/')) return 'monthly';
  return 'monthly';
}

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
${INDEXED_URLS.map(url => `  <url>
    <loc>${url}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${getFreq(url)}</changefreq>
    <priority>${getPriority(url)}</priority>
  </url>`).join('\n')}
</urlset>`;

const sitemapPath = path.join(ROOT, 'public/sitemap.xml');
fs.writeFileSync(sitemapPath, sitemap, 'utf-8');
console.log(`✅ Sitemap regenerat: ${INDEXED_URLS.length} URL-uri (era 13, acum ${INDEXED_URLS.length})`);

// ─────────────────────────────────────────────────────────────────
// 2. SCHEMA LocalBusiness PE PAGINILE DE SERVICII (lipsesc schema)
// ─────────────────────────────────────────────────────────────────
const serviceSchema = JSON.stringify({
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "SuperParty",
  "description": "Animatori profesionisti pentru petreceri copii in Bucuresti si Ilfov. Peste 8.000 de petreceri organizate.",
  "url": "https://www.superparty.ro",
  "telephone": "+40722744377",
  "priceRange": "490-1290 RON",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Bucuresti",
    "addressCountry": "RO"
  },
  "areaServed": { "@type": "City", "name": "Bucuresti" },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "1498",
    "bestRating": "5"
  }
});

const servicePages = [
  'arcade-baloane/index.astro',
  'baloane-cu-heliu/index.astro',
  'decoratiuni-baloane/index.astro',
  'mos-craciun-de-inchiriat/index.astro',
  'vata-de-zahar-si-popcorn/index.astro',
  'ursitoare-botez/index.astro',
  'piniata/index.astro',
  'contact/index.astro',
  'galerie.astro',
];

let schemaAdded = 0;
for (const relFp of servicePages) {
  const fp = path.join(ROOT, 'src/pages', relFp);
  if (!fs.existsSync(fp)) continue;
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('"@type"') || c.includes('schema=')) { console.log('SKIP(has schema):', relFp); continue; }
  
  // Inject schema into frontmatter
  const schemaLine = `const schema = ${JSON.stringify(serviceSchema, null, 0)};`;
  
  // Add const schema after imports in frontmatter
  if (c.includes("import Layout from")) {
    c = c.replace(
      /^(---\nimport Layout[^\n]+\n)/m,
      `---\nimport Layout from '${relFp.includes('/') ? '../../' : '../'}layouts/Layout.astro';\nconst schema = JSON.stringify(${serviceSchema});\n`
    );
    // Add schema prop to Layout  
    c = c.replace(/<Layout\s*\n/, '<Layout\n  schema={schema}\n');
    c = c.replace(/<Layout\s+title/, '<Layout\n  schema={schema}\n  title');
    fs.writeFileSync(fp, c, 'utf-8');
    schemaAdded++;
    console.log('✅ Schema adăugat:', relFp);
  }
}
console.log(`✅ Schema adăugat pe ${schemaAdded} pagini de servicii`);

// ─────────────────────────────────────────────────────────────────
// 3. FIX TITLURI PREA LUNGI (>65 caractere)
// ─────────────────────────────────────────────────────────────────
// Titluri lungi identificate in audit — scurtate la maxim 65 caractere
const titleFixes = {
  'animatori-petreceri-copii/index.astro': {
    oldTitle: 'Animatori petreceri copii București & Ilfov | Superparty — Peste 10.00',
    newTitle: 'Animatori Petreceri Copii București | SuperParty',
    newDesc: 'Animatori pentru petreceri copii în București și Ilfov. 50+ personaje costumate. De la 490 RON. Confirmare în 30 minute. 1498+ recenzii ⭐ 4.9/5.'
  },
  'petreceri/aviatiei.astro': {
    oldTitle: 'Animatori Petreceri Copii Aviației Bucuresti | SuperParty — de la 490',
    newTitle: 'Animatori Petreceri Copii Aviației | SuperParty',
  },
  'petreceri/berceni.astro': {
    oldTitle: 'Animatori Petreceri Copii Berceni Bucuresti | SuperParty — de la 490 R',
    newTitle: 'Animatori Petreceri Copii Berceni | SuperParty',
  },
  'petreceri/colentina.astro': {
    oldTitle: 'Animatori Petreceri Copii Colentina Bucuresti | SuperParty — de la 490',
    newTitle: 'Animatori Petreceri Copii Colentina | SuperParty',
  },
  'petreceri/crangasi.astro': {
    oldTitle: 'Animatori Petreceri Copii Crangasi Bucuresti | SuperParty — de la 490',
    newTitle: 'Animatori Petreceri Copii Crângași | SuperParty',
  },
  'petreceri/dorobanti.astro': {
    oldTitle: 'Animatori Petreceri Copii Dorobanți Bucuresti | SuperParty — de la 490',
    newTitle: 'Animatori Petreceri Copii Dorobanți | SuperParty',
  },
  'petreceri/dristor.astro': {
    oldTitle: 'Animatori Petreceri Copii Dristor Bucuresti | SuperParty — de la 490 R',
    newTitle: 'Animatori Petreceri Copii Dristor | SuperParty',
  },
  'petreceri/drumul-taberei.astro': {
    oldTitle: 'Animatori Petreceri Copii Drumul Taberei Bucuresti | SuperParty — de l',
    newTitle: 'Animatori Petreceri Copii Drumul Taberei | SuperParty',
  },
  'petreceri/floreasca.astro': {
    oldTitle: 'Animatori Petreceri Copii Floreasca Bucuresti | SuperParty — de la 490',
    newTitle: 'Animatori Petreceri Copii Floreasca | SuperParty',
  },
  'petreceri/giulesti.astro': {
    oldTitle: 'Animatori Petreceri Copii Giulești Bucuresti | SuperParty — de la 490',
    newTitle: 'Animatori Petreceri Copii Giulești | SuperParty',
  },
  'petreceri/militari.astro': {
    oldTitle: 'Animatori Petreceri Copii Militari Bucuresti | SuperParty — de la 490',
    newTitle: 'Animatori Petreceri Copii Militari | SuperParty',
  },
  'petreceri/pantelimon-cartier.astro': {
    oldTitle: 'Animatori Petreceri Copii Pantelimon (Cartier) Bucuresti | SuperParty',
    newTitle: 'Animatori Petreceri Copii Pantelimon | SuperParty',
  },
  'petreceri/rahova.astro': {
    oldTitle: 'Animatori Petreceri Copii Rahova Bucuresti | SuperParty — de la 490 RO',
    newTitle: 'Animatori Petreceri Copii Rahova | SuperParty',
  },
  'petreceri/tineretului.astro': {
    oldTitle: 'Animatori Petreceri Copii Tineretului Bucuresti | SuperParty — de la 4',
    newTitle: 'Animatori Petreceri Copii Tineretului | SuperParty',
  },
  'petreceri/titan.astro': {
    oldTitle: 'Animatori Petreceri Copii Titan Bucuresti | SuperParty — de la 490 RON',
    newTitle: 'Animatori Petreceri Copii Titan | SuperParty',
  },
  'arcade-baloane/index.astro': {
    oldTitle: 'Arcade Baloane Petreceri Copii | SuperParty București — Decorațiuni Pr',
    newTitle: 'Arcade Baloane Petreceri Copii | SuperParty',
  },
};

let titleFixed = 0;
for (const [relFp, fix] of Object.entries(titleFixes)) {
  const fp = path.join(ROOT, 'src/pages', relFp);
  if (!fs.existsSync(fp)) { continue; }
  let c = fs.readFileSync(fp, 'utf-8');
  
  // Find and replace title in Layout tag or frontmatter variable
  const titleRegex = /title="([^"]+)"/;
  const titleMatch = c.match(titleRegex);
  if (!titleMatch) continue;
  
  const currentTitle = titleMatch[1];
  if (currentTitle.length <= 65) { console.log(`SKIP(${currentTitle.length}chr):`, relFp); continue; }
  
  // Replace with short title
  c = c.replace(titleRegex, `title="${fix.newTitle}"`);
  
  // Also fix desc if provided
  if (fix.newDesc) {
    c = c.replace(/description="([^"]+)"/, `description="${fix.newDesc}"`);
  }
  
  fs.writeFileSync(fp, c, 'utf-8');
  titleFixed++;
  console.log(`✅ Titlu scurtat (${currentTitle.length}→${fix.newTitle.length}chr): ${relFp}`);
}
console.log(`✅ ${titleFixed} titluri scurtate sub 65 caractere`);

// ─────────────────────────────────────────────────────────────────
// 4. FIX DESCRIERI PREA LUNGI > 160 CARACTERE
// ─────────────────────────────────────────────────────────────────
const descFixes = {
  'petreceri/otopeni.astro': 'Animatori petreceri copii în Otopeni, Ilfov (14 km de București). 50+ personaje costumate, de la 490 RON. Confirmare în 30 min.',
  'petreceri/sector-1.astro': 'SuperParty în Sectorul 1: Dorobanți, Floreasca, Aviatorilor. Animatori profesioniști de la 490 RON. Confirmare în 30 minute.',
  'petreceri/sector-6.astro': 'SuperParty în Sectorul 6: Militari, Drumul Taberei, Crângași. Animatori profesioniști de la 490 RON. Confirmare în 30 minute.',
  'animatori-petreceri-copii/index.astro': 'Animatori petreceri copii București — SuperParty: 50+ personaje costumate, jocuri interactive, face painting. De la 490 RON. ⭐ 4.9/5.',
  'piniata/index.astro': 'Piniate personalizate la comandă pentru petreceri copii în București. Forme 3D, personaje la alegere, umplute cu dulciuri. SuperParty.',
};

let descFixed = 0;
for (const [relFp, newDesc] of Object.entries(descFixes)) {
  const fp = path.join(ROOT, 'src/pages', relFp);
  if (!fs.existsSync(fp)) continue;
  let c = fs.readFileSync(fp, 'utf-8');
  const descMatch = c.match(/description="([^"]+)"/);
  if (!descMatch) continue;
  if (descMatch[1].length <= 160) { console.log(`SKIP desc(${descMatch[1].length}):`, relFp); continue; }
  c = c.replace(/description="[^"]+"/, `description="${newDesc}"`);
  fs.writeFileSync(fp, c, 'utf-8');
  descFixed++;
  console.log(`✅ Desc scurtata: ${relFp}`);
}
console.log(`✅ ${descFixed} descrieri scurtate sub 160 caractere`);

// ─────────────────────────────────────────────────────────────────
// 5. FIX ANIMATORI-COPII-BUCURESTI — lipsesc canonical + schema
// ─────────────────────────────────────────────────────────────────
const acbPath = path.join(ROOT, 'src/pages/animatori-copii-bucuresti/index.astro');
if (fs.existsSync(acbPath)) {
  let c = fs.readFileSync(acbPath, 'utf-8');
  if (!c.includes('canonical=')) {
    c = c.replace(/(<Layout\s*)/, '$1\n  canonical="https://www.superparty.ro/animatori-copii-bucuresti/"');
    console.log('✅ Canonical adăugat pe animatori-copii-bucuresti');
  }
  fs.writeFileSync(acbPath, c, 'utf-8');
}

// ─────────────────────────────────────────────────────────────────
// SUMMARY
// ─────────────────────────────────────────────────────────────────
console.log('\n════════════════════════════════════════');
console.log('  REZUMAT FIX-URI APLICATE');
console.log('════════════════════════════════════════');
console.log(`✅ Sitemap: ${INDEXED_URLS.length} URL-uri (era 13, acum ${INDEXED_URLS.length})`);
console.log(`✅ Schema LocalBusiness adăugat pe ${schemaAdded} pagini`);
console.log(`✅ ${titleFixed} titluri scurtate sub 65 caractere`);
console.log(`✅ ${descFixed} descrieri scurtate sub 160 caractere`);
console.log('════════════════════════════════════════\n');
console.log('Ruleaza din nou google_seo_audit.mjs pentru verificare!');
