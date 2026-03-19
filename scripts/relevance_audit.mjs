// relevance_audit.mjs - Analiza relevanta SEO pentru paginile de cartiere
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { cartiereData } from './cartiere_data.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages/petreceri');

// ---- Utilitare ----
function extractVisibleText(fp) {
  let c = fs.readFileSync(fp, 'utf-8');
  c = c.replace(/^---[\s\S]*?---/m, '');
  c = c.replace(/<style[\s\S]*?<\/style>/gi, ' ');
  c = c.replace(/<script[\s\S]*?<\/script>/gi, ' ');
  c = c.replace(/<[^>]+>/g, ' ');
  c = c.replace(/\{[^}]*\}/g, ' ');
  return c.toLowerCase().replace(/[^a-zăâîșț\s]/gi, ' ').replace(/\s+/g, ' ').trim();
}

function wordCount(text) {
  return text.split(/\s+/).filter(w => w.length > 2).length;
}

function keywordDensity(text, kw) {
  const words = text.split(/\s+/);
  const kwWords = kw.toLowerCase().split(/\s+/);
  let count = 0;
  for (let i = 0; i <= words.length - kwWords.length; i++) {
    if (kwWords.every((w, j) => words[i + j] === w)) count++;
  }
  return { count, density: words.length > 0 ? ((count / words.length) * 100).toFixed(2) : '0' };
}

function jaccardSim(textA, textB) {
  const wordsA = new Set(textA.split(/\s+/).filter(w => w.length > 4));
  const wordsB = new Set(textB.split(/\s+/).filter(w => w.length > 4));
  const inter = [...wordsA].filter(x => wordsB.has(x)).length;
  const union = new Set([...wordsA, ...wordsB]).size;
  return union === 0 ? 0 : inter / union;
}

// ---- Cuvinte cheie SEO tinta ----
const TARGET_KWS = [
  'animatori petreceri copii',
  'animator petreceri copii',
  'petreceri copii',
  'animator',
  'animatori',
  'ron',
  '490',
  '840',
  '1290',
  'superparty',
];

console.log('='.repeat(65));
console.log('  AUDIT RELEVANTA CONTINUT — Pagini Cartiere Bucuresti');
console.log('='.repeat(65));

const pages = [];
for (const c of cartiereData) {
  const fp = path.join(pagesDir, `${c.slug}.astro`);
  if (!fs.existsSync(fp)) { console.log('LIPSA:', c.slug); continue; }
  const text = extractVisibleText(fp);
  const wc = wordCount(text);
  pages.push({ slug: c.slug, name: c.name, text, wc });
}

// 1. Cuvinte si densitate keywords
console.log('\n📊 1. CUVINTE + DENSITATE KEYWORDS PRINCIPALE:\n');
pages.forEach(({ slug, name, text, wc }) => {
  const main = keywordDensity(text, 'animatori petreceri copii');
  const sec  = keywordDensity(text, 'animator');
  const price = keywordDensity(text, 'ron');
  const localKw = keywordDensity(text, name.toLowerCase());
  
  const wcIcon = wc >= 1500 ? '✅' : '⚠️ ';
  const mainIcon = parseFloat(main.density) >= 0.3 && parseFloat(main.density) <= 3.0 ? '✅' : '⚠️ ';
  const localIcon = localKw.count >= 5 ? '✅' : '⚠️ ';
  
  console.log(`  ${name.padEnd(22)}`);
  console.log(`    ${wcIcon} Cuvinte: ${wc}`);
  console.log(`    ${mainIcon} "animatori petreceri copii": ${main.count}x (${main.density}%)`);
  console.log(`    ${localIcon} "${name.toLowerCase()}": ${localKw.count}x`);
  console.log(`    💰 "RON": ${price.count}x  |  "animator": ${sec.count}x`);
  console.log('');
});

// 2. Similaritate intre pagini
console.log('\n📊 2. SIMILARITATE INTRE PAGINI (Jaccard - TREBUIE < 20%):\n');
let maxSim = 0, maxPair = '', problemCount = 0;
const pairs = [];
for (let i = 0; i < pages.length; i++) {
  for (let j = i + 1; j < pages.length; j++) {
    const sim = jaccardSim(pages[i].text, pages[j].text);
    pairs.push({ a: pages[i].name, b: pages[j].name, sim });
    if (sim > maxSim) { maxSim = sim; maxPair = `${pages[i].name} <-> ${pages[j].name}`; }
    if (sim > 0.20) problemCount++;
  }
}

const sorted = [...pairs].sort((x, y) => y.sim - x.sim);
console.log('  Top 10 cele mai similare perechi:');
sorted.slice(0, 10).forEach(({ a, b, sim }) => {
  const ok = sim <= 0.20;
  const icon = ok ? '✅' : '❌';
  console.log(`  ${icon} ${a.padEnd(20)} <-> ${b.padEnd(20)} | ${(sim*100).toFixed(1)}%`);
});

console.log('\n  Top 5 cele mai DIFERITE:');
sorted.slice(-5).reverse().forEach(({ a, b, sim }) => {
  console.log(`  ✅ ${a.padEnd(20)} <-> ${b.padEnd(20)} | ${(sim*100).toFixed(1)}%`);
});

// 3. Unicitatea fata de flagship
console.log('\n📊 3. UNICITATE FATA DE PAGINA FLAGSHIP (animatori-petreceri-copii):\n');
const flagshipPath = path.join(__dirname, '../src/pages/animatori-petreceri-copii/index.astro');
let flagshipSim = 'N/A';
if (fs.existsSync(flagshipPath)) {
  const flagText = extractVisibleText(flagshipPath);
  pages.forEach(({ name, text }) => {
    const sim = jaccardSim(text, flagText);
    const ok = sim <= 0.20;
    const icon = ok ? '✅' : '❌';
    console.log(`  ${icon} ${name.padEnd(22)} vs flagship: ${(sim*100).toFixed(1)}% similar`);
  });
} else {
  console.log('  (flagship nu gasit)');
}

// 4. Prezenta elementelor SEO obligatorii
console.log('\n📊 4. ELEMENTE SEO OBLIGATORII PER PAGINA:\n');
for (const c of cartiereData) {
  const fp = path.join(pagesDir, `${c.slug}.astro`);
  if (!fs.existsSync(fp)) continue;
  const raw = fs.readFileSync(fp, 'utf-8');
  
  const hasSchema   = raw.includes('@type') && raw.includes('Service');
  const hasFaq      = raw.includes('FAQPage') || raw.includes('faq-item');
  const hasBreadcrumb = raw.includes('BreadcrumbList');
  const hasPrice    = raw.includes('490') && raw.includes('840') && raw.includes('1290');
  const hasCanonical = raw.includes('canonical');
  const hasH1       = (raw.match(/<h1/gi) || []).length > 0;
  const hasCTA      = raw.includes('0722 744 377') || raw.includes('wa.me');
  const hasInternalLink = raw.includes('animatori-petreceri-copii') || raw.includes('sector-');
  
  const allOk = hasSchema && hasFaq && hasBreadcrumb && hasPrice && hasCanonical && hasH1 && hasCTA && hasInternalLink;
  const icon = allOk ? '✅' : '⚠️ ';
  
  const missing = [];
  if (!hasSchema) missing.push('Schema');
  if (!hasFaq) missing.push('FAQ');
  if (!hasBreadcrumb) missing.push('Breadcrumb');
  if (!hasPrice) missing.push('Preturi 490/840/1290');
  if (!hasCanonical) missing.push('Canonical');
  if (!hasH1) missing.push('H1');
  if (!hasCTA) missing.push('CTA telefon');
  if (!hasInternalLink) missing.push('Link intern');
  
  console.log(`  ${icon} ${c.name.padEnd(22)}: ${allOk ? 'OK complet' : 'LIPSA: ' + missing.join(', ')}`);
}

// ---- SUMAR FINAL ----
console.log('\n' + '='.repeat(65));
console.log('  SUMAR FINAL');
console.log('='.repeat(65));
console.log(`  📄 Pagini analizate: ${pages.length}`);
console.log(`  📝 Cuvinte medii: ${Math.round(pages.reduce((s,p) => s + p.wc, 0) / pages.length)}`);
console.log(`  🔗 Perechi analizate: ${pairs.length}`);
console.log(`  ❌ Perechi similare (>20%): ${problemCount}/${pairs.length}`);
console.log(`  📈 Max similaritate: ${(maxSim*100).toFixed(1)}% (${maxPair})`);
if (problemCount === 0) {
  console.log('\n  ✅ TOATE paginile sunt sub 20% similaritate!');
} else {
  console.log(`\n  ❌ ${problemCount} perechi necesita imbunatatire!`);
}
console.log('='.repeat(65));
