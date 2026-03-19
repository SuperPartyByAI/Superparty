// full_seo_audit.mjs — Audit SEO complet pentru superparty.ro
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

function getAllAstro(dir, list = []) {
  if (!fs.existsSync(dir)) return list;
  for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
    if (f.isDirectory()) getAllAstro(path.join(dir, f.name), list);
    else if (f.name.endsWith('.astro') && !f.name.includes('[')) {
      list.push(path.join(dir, f.name));
    }
  }
  return list;
}

function getText(raw) {
  return raw
    .replace(/^---[\s\S]*?---/m, '')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/\{[^{}]*\}/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ').trim();
}

function countWords(text) {
  return text.split(/\s+/).filter(w => w.length > 2).length;
}

function jaccard(a, b) {
  const sA = new Set(a.split(/\s+/).filter(w => w.length >= 6));
  const sB = new Set(b.split(/\s+/).filter(w => w.length >= 6));
  if (!sA.size || !sB.size) return 0;
  return [...sA].filter(x => sB.has(x)).length / new Set([...sA, ...sB]).size;
}

const pagesDir = path.join(ROOT, 'src/pages');
const files = getAllAstro(pagesDir);

const pages = [];
for (const fp of files) {
  const raw = fs.readFileSync(fp, 'utf-8');
  const rel = path.relative(pagesDir, fp).replace(/\\/g, '/');
  const text = getText(raw);
  const words = countWords(text);

  // Extract meta
  const noindex = raw.includes('noindex');
  const hasCanonical = raw.includes('canonical=');
  const hasSchema = raw.includes('@type');
  const hasTitle = raw.includes('title=');
  const hasDesc = raw.includes('description=');
  const hasCTA = raw.includes('cta') || raw.includes('tel:+40') || raw.includes('WhatsApp');
  const hasH1 = (raw.match(/<h1/gi) || []).length;
  const hasH2 = (raw.match(/<h2/gi) || []).length;
  const hasFAQ = raw.includes('FAQPage') || raw.includes('faq');
  const hasLocal = raw.includes('LocalBusiness');
  const hasService = raw.includes('"@type":"Service"') || raw.includes("'@type':'Service'");
  const hasBreadcrumb = raw.includes('BreadcrumbList');
  const hasAlt = (raw.match(/<img[^>]+alt=/gi) || []).length;
  const imgCount = (raw.match(/<img/gi) || []).length;
  const allImgHaveAlt = imgCount === 0 || hasAlt >= imgCount;

  // Title/desc length check
  const titleM = raw.match(/title="([^"]+)"/);
  const descM = raw.match(/description="([^"]+)"/);
  const titleLen = titleM ? titleM[1].length : 0;
  const descLen = descM ? descM[1].length : 0;

  // Party keyword relevance
  const partyKw = ['animatori', 'petreceri', 'copii', 'aniversar', 'botez', 'personaj', 'superparty'];
  const textLow = text.toLowerCase();
  const kwHits = partyKw.filter(k => textLow.includes(k)).length;

  // Score per page
  let score = 0;
  let issues = [];
  if (noindex) { score += 0; } else {
    if (!hasTitle) { issues.push('lipseste title'); } else score += 10;
    if (!hasDesc) { issues.push('lipseste description'); } else score += 10;
    if (titleLen > 0 && (titleLen < 30 || titleLen > 70)) issues.push(`title ${titleLen}ch (ideal 30-70)`);
    if (descLen > 0 && (descLen < 100 || descLen > 165)) issues.push(`desc ${descLen}ch (ideal 100-165)`);
    if (!hasCanonical) { issues.push('lipseste canonical'); } else score += 5;
    if (!hasSchema) { issues.push('lipseste schema'); } else score += 10;
    if (hasFAQ) score += 5;
    if (hasLocal) score += 5;
    if (hasBreadcrumb) score += 5;
    if (!hasCTA) { issues.push('lipseste CTA/tel'); } else score += 10;
    if (hasH1 === 0) { issues.push('lipseste H1'); } else if (hasH1 > 1) issues.push(`${hasH1}x H1`);
    else score += 10;
    if (hasH2 < 2) issues.push('prea putine H2');
    else score += 5;
    if (words < 300) { issues.push(`${words} cuvinte (sub 300)`); }
    else if (words >= 600) score += 15;
    else score += 8;
    if (kwHits < 3) { issues.push(`doar ${kwHits}/7 kw party`); } else score += 10;
    if (imgCount > 0 && !allImgHaveAlt) issues.push(`${imgCount - hasAlt} img fara alt`);
  }

  pages.push({ rel, noindex, words, score, issues, kwHits, hasSchema, hasFAQ, hasLocal, hasBreadcrumb });
}

// --- RESULTS ---
const indexed = pages.filter(p => !p.noindex);
const noIndexed = pages.filter(p => p.noindex);

console.log('='.repeat(65));
console.log('  AUDIT SEO COMPLET — SUPERPARTY.RO');
console.log('='.repeat(65));
console.log(`\nTotal pagini .astro scanate:  ${pages.length}`);
console.log(`Pagini indexate (index):      ${indexed.length}`);
console.log(`Pagini noindex:               ${noIndexed.length}`);

// Score distribution
const avg = indexed.reduce((s, p) => s + p.score, 0) / (indexed.length || 1);
const perfect = indexed.filter(p => p.score >= 85).length;
const good = indexed.filter(p => p.score >= 65 && p.score < 85).length;
const medium = indexed.filter(p => p.score >= 40 && p.score < 65).length;
const poor = indexed.filter(p => p.score < 40).length;

console.log(`\n--- SCOR SEO PAGINI INDEXATE ---`);
console.log(`Scor mediu:         ${avg.toFixed(0)}/100`);
console.log(`Excelent (85+):     ${perfect} pagini`);
console.log(`Bun (65-84):        ${good} pagini`);
console.log(`Mediu (40-64):      ${medium} pagini`);
console.log(`Slab (<40):         ${poor} pagini`);

// Schema stats
console.log('\n--- SCHEMA MARKUP ---');
console.log(`Schema JSON-LD:     ${indexed.filter(p => p.hasSchema).length}/${indexed.length} pagini indexate`);
console.log(`FAQ schema:         ${indexed.filter(p => p.hasFAQ).length}/${indexed.length}`);
console.log(`LocalBusiness:      ${indexed.filter(p => p.hasLocal).length}/${indexed.length}`);
console.log(`BreadcrumbList:     ${indexed.filter(p => p.hasBreadcrumb).length}/${indexed.length}`);

// Word count
console.log('\n--- CUVINTE CONTINUT VIZIBIL ---');
const wc = indexed.map(p => p.words).sort((a,b)=>a-b);
console.log(`Min: ${wc[0]}  Median: ${wc[Math.floor(wc.length/2)]}  Max: ${wc[wc.length-1]}`);
console.log(`Sub 300 cuvinte:  ${indexed.filter(p => p.words < 300).map(p => p.rel).join(', ') || 'niciuna'}`);
console.log(`300-599 cuvinte:  ${indexed.filter(p => p.words >= 300 && p.words < 600).length} pagini`);
console.log(`600+ cuvinte:     ${indexed.filter(p => p.words >= 600).length} pagini`);

// Duplicate check on indexed
console.log('\n--- SIMILARITATE CONTINUT (pagini indexate) ---');
let dupPairs = 0, topDup = [];
for (let i = 0; i < indexed.length; i++) {
  const tA = getText(fs.readFileSync(path.join(pagesDir, indexed[i].rel), 'utf-8'));
  for (let j = i+1; j < indexed.length; j++) {
    const tB = getText(fs.readFileSync(path.join(pagesDir, indexed[j].rel), 'utf-8'));
    const s = jaccard(tA, tB);
    if (s >= 0.2) { dupPairs++; topDup.push({ a: indexed[i].rel, b: indexed[j].rel, s }); }
  }
}
topDup.sort((a,b) => b.s - a.s);
console.log(`Perechi >20% similaritate:  ${dupPairs}`);
if (topDup.length > 0) {
  console.log('Top 5 similare:');
  topDup.slice(0, 5).forEach(x => console.log(`  ${(x.s*100).toFixed(1)}%  ${x.a}  <->  ${x.b}`));
} else {
  console.log('  ✅ Zero perechi duplicate!');
}

// Pages with issues
console.log('\n--- PAGINI CU PROBLEME (indexate) ---');
const withIssues = indexed.filter(p => p.issues.length > 0).sort((a,b) => a.score - b.score);
if (withIssues.length === 0) {
  console.log('  ✅ Nicio problemă detectată!');
} else {
  for (const p of withIssues.slice(0, 20)) {
    console.log(`  [${p.score.toString().padStart(3)}] ${p.rel}`);
    console.log(`        → ${p.issues.join(' | ')}`);
  }
  if (withIssues.length > 20) console.log(`  ... si inca ${withIssues.length - 20} pagini cu probleme`);
}

// Top pages
console.log('\n--- TOP 10 PAGINI (scor SEO) ---');
[...indexed].sort((a,b) => b.score - a.score).slice(0, 10).forEach(p => {
  console.log(`  [${p.score.toString().padStart(3)}] ${p.rel} (${p.words}w)`);
});

// Overall verdict
console.log('\n' + '='.repeat(65));
const grade = avg >= 80 ? 'A — EXCELENT' : avg >= 65 ? 'B — BUN' : avg >= 50 ? 'C — MEDIU' : 'D — NECESITA IMBUNATATIRI';
console.log(`  VERDICT FINAL: ${grade} (${avg.toFixed(0)}/100 medie)`);
console.log('='.repeat(65));
