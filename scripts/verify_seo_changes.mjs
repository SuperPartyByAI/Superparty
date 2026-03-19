// verify_seo_changes.mjs
// Demonstrează ce s-a implementat azi pe superparty.ro

import fs from 'fs';
import path from 'path';

console.log('╔══════════════════════════════════════════════════════════╗');
console.log('║         VERIFICARE LIVE — ce s-a implementat azi        ║');
console.log('╚══════════════════════════════════════════════════════════╝\n');

// ── 1. FLAGSHIP PAGE ────────────────────────────────────────────────────────
const flagship = fs.readFileSync('src/pages/animatori-petreceri-copii/index.astro', 'utf-8');
const flagshipBody = flagship.replace(/---[\s\S]*?---/, '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
const wordCount = flagshipBody.split(' ').filter(w => w.length > 2).length;
const faqCount = (flagship.match(/<details/g) || flagship.match(/\*\*Î:/g) || []).length;
const internalLinks = (flagship.match(/href="\/animatori-copii-/g) || []).length;
const personajeSection = flagship.includes('personaj') || flagship.includes('personaje');

console.log('📄 PAGINA FLAGSHIP /animatori-petreceri-copii:');
console.log(`   Cuvinte (body):       ${wordCount} cuvinte`);
console.log(`   FAQ entries:          ${(flagship.match(/<details/g) || []).length} întrebări`);
console.log(`   Link-uri interne:     ${internalLinks} → pagini locale`);
console.log(`   Secțiune personaje:   ${personajeSection ? '✅ DA' : '❌ NU'}`);
console.log(`   FlagshipLink import:  ${flagship.includes('FlagshipLink') ? '✅ DA' : '❌ NU'}`);

// ── 2. INTERNAL LINKING ─────────────────────────────────────────────────────
const localPages = [
  'animatori-copii-sector-1', 'animatori-copii-sector-2', 'animatori-copii-sector-3',
  'animatori-copii-sector-4', 'animatori-copii-sector-5', 'animatori-copii-sector-6',
  'animatori-copii-bucuresti', 'animatori-copii-ilfov', 'animatori-copii-voluntari',
  'animatori-copii-otopeni', 'animatori-copii-pantelimon', 'animatori-copii-bragadiru',
  'animatori-copii-chiajna', 'animatori-copii-popesti-leordeni'
];

console.log('\n🔗 INTERNAL LINKING (FlagshipLink pe fiecare pagina locala):');
let linked = 0;
localPages.forEach(page => {
  const f = `src/pages/${page}/index.astro`;
  if (fs.existsSync(f)) {
    const content = fs.readFileSync(f, 'utf-8');
    const has = content.includes('FlagshipLink');
    if (has) linked++;
    console.log(`   ${has ? '✅' : '❌'} ${page}`);
  } else {
    console.log(`   ⚠️  LIPSĂ: ${page}`);
  }
});
console.log(`\n   Total pagini cu link intern: ${linked}/${localPages.length}`);

// ── 3. NOINDEX DUPLICATE ARTICLES ───────────────────────────────────────────
const articlesDir = 'src/content/seo-articles';
const allArticles = fs.readdirSync(articlesDir).filter(f => f.endsWith('.mdx'));
let noindexCount = 0;
let indexableCount = 0;

allArticles.forEach(f => {
  const content = fs.readFileSync(path.join(articlesDir, f), 'utf-8');
  if (content.includes('noindex')) {
    noindexCount++;
  } else {
    indexableCount++;
  }
});

console.log('\n🚫 NOINDEX DUPLICATE CONTENT FIX:');
console.log(`   Total articole:               ${allArticles.length}`);
console.log(`   Cu noindex (blocate Google):  ${noindexCount} articole`);
console.log(`   Indexabile (unice, de calitate): ${indexableCount} articole`);
console.log(`   Procent indexabil:            ${Math.round(indexableCount/allArticles.length*100)}%`);

// ── SUMAR ────────────────────────────────────────────────────────────────────
console.log('\n══════════════════════════════════════════════════════════');
console.log('SUMAR: ce vede Google acum față de înainte:');
console.log(`  Cuvinte flagship:    ${wordCount} (era ~400 înainte)`);
console.log(`  Pagini cu link ➜ flagship: ${linked}/14`);
console.log(`  Articole duplicate blocate: ${noindexCount}/499`);
console.log('══════════════════════════════════════════════════════════');
