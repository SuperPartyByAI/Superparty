// fix_seo_issues.mjs — Rezolva toate problemele din auditul SEO
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

// =====================================================================
// 1. NOINDEX animatori-copii-sector-1..6 (duplicate cu petreceri/sector-X)
// =====================================================================
console.log('\n[1] Noindex animatori-copii-sector-X...');
const acDirs = fs.readdirSync(path.join(ROOT, 'src/pages'))
  .filter(d => d.match(/^animatori-copii-sector-\d+$/));
let n1 = 0;
for (const d of acDirs) {
  const fp = path.join(ROOT, 'src/pages', d, 'index.astro');
  if (!fs.existsSync(fp)) continue;
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('noindex')) { console.log(`  skip (deja noindex): ${d}`); continue; }
  c = c.replace(/robots="index,\s*follow"/, 'robots="noindex, follow"');
  if (!c.includes('noindex')) {
    // insert after first canonical
    c = c.replace(/canonical="[^"]+"\s*/, (m) => m + '\n  robots="noindex, follow"\n  ');
  }
  fs.writeFileSync(fp, c, 'utf-8');
  n1++;
  console.log(`  noindex: ${d}`);
}
console.log(`  Total: ${n1} pagini`);

// =====================================================================
// 2. SCHEMA JSON-LD pe homepage (index.astro)
// =====================================================================
console.log('\n[2] Adaug schema JSON-LD pe homepage...');
const homeFp = path.join(ROOT, 'src/pages/index.astro');
let homeContent = fs.readFileSync(homeFp, 'utf-8');
if (!homeContent.includes('@type')) {
  const homeSchema = `
const homeSchema = JSON.stringify({
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "LocalBusiness",
      "name": "SuperParty",
      "description": "Animatori profesioniști pentru petreceri copii în București și Ilfov. Pachete de la 490 RON, garantie contractuală.",
      "url": "https://www.superparty.ro",
      "telephone": "+40722744377",
      "priceRange": "490-1290 RON",
      "address": {"@type": "PostalAddress", "addressLocality": "București", "addressCountry": "RO"},
      "areaServed": ["București", "Ilfov"],
      "image": "https://www.superparty.ro/images/hero-party.jpg",
      "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.9", "reviewCount": "1498"},
      "openingHours": "Mo-Su 08:00-22:00"
    },
    {
      "@type": "WebSite",
      "name": "SuperParty",
      "url": "https://www.superparty.ro",
      "potentialAction": {"@type": "SearchAction", "target": "https://www.superparty.ro/?s={search_term_string}", "query-input": "required name=search_term_string"}
    }
  ]
});`;
  // Inject dupa frontmatter vars (dupa WA_URL)
  homeContent = homeContent.replace(
    "const WA_URL = `https://wa.me/40722744377?text=${WA_TEXT}`;",
    "const WA_URL = `https://wa.me/40722744377?text=${WA_TEXT}`;\n" + homeSchema
  );
  // Adauga schema prop la Layout
  homeContent = homeContent.replace(
    '<Layout\n  title=',
    '<Layout\n  schema={homeSchema}\n  title='
  );
  fs.writeFileSync(homeFp, homeContent, 'utf-8');
  console.log('  ✅ Schema adaugata pe homepage');
} else {
  console.log('  skip — are deja schema');
}

// =====================================================================
// 3. SCHEMA pe paginile servicii auxiliare (baloane, piniata etc.)
// =====================================================================
console.log('\n[3] Adaug schema pe paginile servicii...');
const servicii = [
  {
    dir: 'arcade-baloane',
    name: 'Arcade Baloane București',
    desc: 'Arcade și aranjamente baloane pentru petreceri copii în București și Ilfov. Servicii profesionale SuperParty.',
    type: 'Service',
    kw: 'arcade baloane'
  },
  {
    dir: 'baloane-cu-heliu',
    name: 'Baloane cu Heliu București',
    desc: 'Baloane cu heliu diverse forme și mărimi pentru petreceri copii în București. Livrare la locație. SuperParty.',
    type: 'Service',
    kw: 'baloane cu heliu'
  },
  {
    dir: 'decoratiuni-baloane',
    name: 'Decorațiuni Baloane Petreceri',
    desc: 'Decorațiuni baloane profesionale pentru petreceri copii și evenimente în București și Ilfov. SuperParty.',
    type: 'Service',
    kw: 'decoratiuni baloane'
  },
  {
    dir: 'piniata',
    name: 'Piniată Personalizată București',
    desc: 'Piniate personalizate pentru petreceri copii în București. Forme și personaje la alegere. SuperParty.',
    type: 'Product',
    kw: 'piniata petreceri copii'
  },
  {
    dir: 'ursitoare-botez',
    name: 'Ursitoare Botez București',
    desc: 'Spectacol ursitoare pentru botez în București și Ilfov. 4 personaje, program complet 3 ore. SuperParty.',
    type: 'Service',
    kw: 'ursitoare botez'
  },
  {
    dir: 'mos-craciun-de-inchiriat',
    name: 'Moș Crăciun de Închiriat București',
    desc: 'Moș Crăciun autentic pentru acasă sau la birou în București. Rezervare rapidă, costume premium. SuperParty.',
    type: 'Service',
    kw: 'mos craciun de inchiriat'
  },
  {
    dir: 'vata-de-zahar-si-popcorn',
    name: 'Vată de Zahăr și Popcorn Petreceri',
    desc: 'Mașini profesionale vată de zahăr și popcorn pentru petreceri copii în București și Ilfov. SuperParty.',
    type: 'Service',
    kw: 'vata de zahar popcorn petreceri'
  },
];

let n3 = 0;
for (const svc of servicii) {
  const fp = path.join(ROOT, 'src/pages', svc.dir, 'index.astro');
  if (!fs.existsSync(fp)) { console.log(`  skip (nu exista): ${svc.dir}`); continue; }
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('@type')) { console.log(`  skip (are schema): ${svc.dir}`); continue; }

  const schemaStr = `
const svcSchema = JSON.stringify({
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "${svc.type}",
      "name": "${svc.name}",
      "description": "${svc.desc}",
      "provider": {"@type": "LocalBusiness", "name": "SuperParty", "telephone": "+40722744377", "url": "https://www.superparty.ro"}
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Acasă", "item": "https://superparty.ro"},
        {"@type": "ListItem", "position": 2, "name": "${svc.name}", "item": "https://superparty.ro/${svc.dir}"}
      ]
    }
  ]
});`;

  // Injecteaza dupa --- closing sau inainte de import Layout
  if (c.includes('import Layout')) {
    c = c.replace('import Layout', schemaStr + '\nimport Layout');
  }
  // Adauga schema prop la Layout tag
  c = c.replace('<Layout\n', '<Layout\n  schema={svcSchema}\n');
  c = c.replace('<Layout ', '<Layout schema={svcSchema} ');

  fs.writeFileSync(fp, c, 'utf-8');
  n3++;
  console.log(`  ✅ Schema: ${svc.dir}`);
}
console.log(`  Total: ${n3} servicii patched`);

// =====================================================================
// 4. FIX title/desc pe paginile animatori-copii cu titlu prea lung
// =====================================================================
console.log('\n[4] Fix title prea lung (>70ch) pe animatori-copii-*...');

const allAcDirs = fs.readdirSync(path.join(ROOT, 'src/pages'))
  .filter(d => d.startsWith('animatori-copii'));

let n4 = 0;
for (const d of allAcDirs) {
  const fp = path.join(ROOT, 'src/pages', d, 'index.astro');
  if (!fs.existsSync(fp)) continue;
  let c = fs.readFileSync(fp, 'utf-8');

  // Fix title prea lung
  const titleM = c.match(/title="([^"]+)"/);
  if (titleM && titleM[1].length > 70) {
    // Scurteaza titlul
    let newTitle = titleM[1]
      .replace(' | SuperParty — Animatori Petreceri Copii', '')
      .replace(' — Animatori Petreceri Copii', '')
      .replace('Animatori Petreceri Copii ', '');
    if (newTitle.length > 70) newTitle = newTitle.substring(0, 67) + '...';
    c = c.replace(`title="${titleM[1]}"`, `title="${newTitle}"`);
    n4++;
  }

  // Fix desc prea lung
  const descM = c.match(/description="([^"]+)"/);
  if (descM && descM[1].length > 165) {
    let newDesc = descM[1].substring(0, 162) + '...';
    c = c.replace(`description="${descM[1]}"`, `description="${newDesc}"`);
  }

  fs.writeFileSync(fp, c, 'utf-8');
}
console.log(`  Fixed ${n4} titluri`);

console.log('\n✅ Toate fix-urile aplicate!');
console.log('Ruleaza: node scripts/full_seo_audit.mjs pentru verificare finala');
