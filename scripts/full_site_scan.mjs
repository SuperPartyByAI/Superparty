// full_site_scan.mjs — Audit complet: toate paginile, calitate, similaritate
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
const PAGES = path.join(ROOT, 'src/pages');

// ──────────────────────────────────────────────
// 1. EXTRACT TEXT (fara style, script, HTML tags)
// ──────────────────────────────────────────────
function extractText(fp) {
  let c = fs.readFileSync(fp, 'utf-8');
  c = c.replace(/^---[\s\S]*?---/m, '');        // frontmatter
  c = c.replace(/<style[\s\S]*?<\/style>/gi, ''); // CSS
  c = c.replace(/<script[\s\S]*?<\/script>/gi, ''); // JS
  c = c.replace(/<[^>]+>/g, ' ');               // HTML tags
  c = c.replace(/\{[^{}]*\}/g, ' ');            // Astro expressions
  c = c.replace(/[^\wăâîșțĂÂÎȘȚ\s]/g, ' ');       // special chars
  return c.replace(/\s+/g, ' ').trim().toLowerCase();
}

function wordCount(text) {
  return text.split(/\s+/).filter(w => w.length >= 2).length;
}

function jaccard(a, b) {
  const sA = new Set(a.split(/\s+/).filter(w => w.length >= 6));
  const sB = new Set(b.split(/\s+/).filter(w => w.length >= 6));
  if (!sA.size || !sB.size) return 0;
  const inter = [...sA].filter(x => sB.has(x)).length;
  return inter / new Set([...sA, ...sB]).size;
}

// ──────────────────────────────────────────────
// 2. COLLECT ALL ASTRO PAGES
// ──────────────────────────────────────────────
function collectPages(dir, rel = '') {
  const results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    const relPath = rel ? `${rel}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      results.push(...collectPages(fullPath, relPath));
    } else if (entry.isFile() && entry.name.endsWith('.astro') && !entry.name.includes('[')) {
      results.push({ rel: relPath, fp: fullPath });
    }
  }
  return results;
}

console.log('Scanez toate paginile...\n');
const allPages = collectPages(PAGES);
console.log(`Total fisiere .astro gasite: ${allPages.length}\n`);

// ──────────────────────────────────────────────
// 3. ANALYZE EACH PAGE
// ──────────────────────────────────────────────
const pages = [];
for (const { rel, fp } of allPages) {
  const raw = fs.readFileSync(fp, 'utf-8');
  const noindex = raw.includes('noindex');
  const hasTitle = raw.includes('title="');
  const hasDesc = raw.includes('description="');
  const hasCanonical = raw.includes('canonical=');
  const hasSchema = raw.includes('@type') || raw.includes('schema=');
  const text = extractText(fp);
  const words = wordCount(text);
  
  // Quality score 0-100
  let score = 0;
  if (hasTitle) score += 20;
  if (hasDesc) score += 20;
  if (hasCanonical) score += 15;
  if (hasSchema) score += 15;
  if (words >= 600) score += 30;
  else if (words >= 300) score += 15;
  else if (words >= 100) score += 5;
  
  pages.push({ rel, fp, noindex, hasTitle, hasDesc, hasCanonical, hasSchema, words, score, text });
}

const indexed = pages.filter(p => !p.noindex);
const noindexed = pages.filter(p => p.noindex);

// ──────────────────────────────────────────────
// 4. SIMILARITY MATRIX (indexate only)
// ──────────────────────────────────────────────
console.log(`Calculez similaritate pentru ${indexed.length} pagini indexate...`);
const pairs = [];
for (let i = 0; i < indexed.length; i++) {
  for (let j = i + 1; j < indexed.length; j++) {
    const s = jaccard(indexed[i].text, indexed[j].text);
    if (s > 0.1) {
      pairs.push({ a: indexed[i].rel, b: indexed[j].rel, s });
    }
  }
}
pairs.sort((a, b) => b.s - a.s);
const over20 = pairs.filter(p => p.s >= 0.2);
const over30 = pairs.filter(p => p.s >= 0.3);

// ──────────────────────────────────────────────
// 5. GENERATE REPORT
// ──────────────────────────────────────────────
function bar(n, max = 10) {
  const filled = Math.round((n / 100) * max);
  return '█'.repeat(filled) + '░'.repeat(max - filled);
}

let report = '';
report += '=================================================================\n';
report += '  AUDIT COMPLET SUPERPARTY.RO — ' + new Date().toISOString().slice(0,10) + '\n';
report += '=================================================================\n\n';

report += `--- INVENTAR PAGINI ---\n`;
report += `Total .astro scanate:          ${allPages.length}\n`;
report += `Pagini INDEXATE (robots=index): ${indexed.length}\n`;
report += `Pagini NOINDEX:                 ${noindexed.length}\n\n`;

// Score distribution indexed
const excellent = indexed.filter(p => p.score >= 85);
const good = indexed.filter(p => p.score >= 65 && p.score < 85);
const medium = indexed.filter(p => p.score >= 40 && p.score < 65);
const poor = indexed.filter(p => p.score < 40);

report += `--- CALITATE PAGINI INDEXATE ---\n`;
report += `Excelent (85+):  ${excellent.length} pagini\n`;
report += `Bun (65-84):     ${good.length} pagini\n`;
report += `Mediu (40-64):   ${medium.length} pagini\n`;
report += `Slab (<40):      ${poor.length} pagini\n\n`;

// Word counts
const thin = indexed.filter(p => p.words < 300);
const ok = indexed.filter(p => p.words >= 300 && p.words < 600);
const rich = indexed.filter(p => p.words >= 600);

report += `--- CONTINUT (cuvinte vizibile) ---\n`;
report += `Sub 300 cuvinte (THIN):  ${thin.length} pagini — PROBLEMA SEO!\n`;
report += `300-599 cuvinte (OK):    ${ok.length} pagini\n`;
report += `600+ cuvinte (BOGAT):    ${rich.length} pagini\n\n`;

report += `--- SIMILARITATE CONTINUT (pagini indexate) ---\n`;
report += `Perechi >20% similaritate: ${over20.length}\n`;
report += `Perechi >30% similaritate: ${over30.length}\n\n`;

report += `Top 30 perechi similare:\n`;
pairs.slice(0, 30).forEach(p => {
  const cat = p.s >= 0.5 ? '🔴 CRITIC' : p.s >= 0.3 ? '🟠 MARE  ' : p.s >= 0.2 ? '🟡 MEDIU ' : '🟢 OK    ';
  report += `  ${cat} ${(p.s*100).toFixed(1).padStart(5)}%  ${path.basename(p.a, '.astro')} <-> ${path.basename(p.b, '.astro')}\n`;
});

report += `\n--- PAGINI CU PROBLEME GRAVE (indexate) ---\n`;

// Pages without meta
const noTitle = indexed.filter(p => !p.hasTitle);
const noDesc = indexed.filter(p => !p.hasDesc);
const noCanon = indexed.filter(p => !p.hasCanonical);
const noSchema = indexed.filter(p => !p.hasSchema);

report += `Fara titlu:        ${noTitle.length}\n`;
report += `Fara descriere:    ${noDesc.length}\n`;
report += `Fara canonical:    ${noCanon.length}\n`;
report += `Fara schema:       ${noSchema.length}\n\n`;

// Thin content details
report += `--- PAGINI THIN CONTENT (sub 300 cuvinte, INDEXATE) ---\n`;
thin.sort((a,b) => a.words - b.words).forEach(p => {
  report += `  [${p.words.toString().padStart(4)}w] ${p.rel}\n`;
});

// Low quality details
report += `\n--- PAGINI CALITATE MEDIE/SLABA (score <65, indexate) ---\n`;
[...medium, ...poor].sort((a,b) => a.score - b.score).forEach(p => {
  const issues = [];
  if (!p.hasTitle) issues.push('no-title');
  if (!p.hasDesc) issues.push('no-desc');
  if (!p.hasCanonical) issues.push('no-canonical');
  if (!p.hasSchema) issues.push('no-schema');
  if (p.words < 300) issues.push(`thin(${p.words}w)`);
  report += `  [${p.score.toString().padStart(3)}] ${p.rel}  →  ${issues.join(' | ')}\n`;
});

// All noindex pages
report += `\n--- TOATE PAGINILE NOINDEX (${noindexed.length}) ---\n`;
noindexed.forEach(p => {
  report += `  [${p.words.toString().padStart(4)}w] ${p.rel}\n`;
});

report += '\n=================================================================\n';

// Score per category
const sectorPages = indexed.filter(p => p.rel.includes('sector-'));
const cartierePages = indexed.filter(p => {
  const known = ['aviatiei','berceni','crangasi','dorobanti','drumul-taberei','dristor','floreasca','giulesti','militari','pantelimon','rahova','tineretului','titan','colentina'];
  return known.some(k => p.rel.includes(k));
});

report += `\n--- ANALIZA PE CATEGORII ---\n`;
report += `Sector pages (${sectorPages.length}): scor mediu ${Math.round(sectorPages.reduce((a,p) => a+p.score,0)/Math.max(sectorPages.length,1))}\n`;
report += `Cartiere (${cartierePages.length}): scor mediu ${Math.round(cartierePages.reduce((a,p) => a+p.score,0)/Math.max(cartierePages.length,1))}\n`;

const comunePages = indexed.filter(p => p.rel.includes('petreceri/') && !sectorPages.includes(p) && !cartierePages.includes(p));
report += `Comune/orase (${comunePages.length}): scor mediu ${Math.round(comunePages.reduce((a,p) => a+p.score,0)/Math.max(comunePages.length,1))}\n`;

const servicePages = indexed.filter(p => !p.rel.includes('petreceri/') && !p.rel.includes('animatori-copii'));
report += `Pagini servicii (${servicePages.length}): scor mediu ${Math.round(servicePages.reduce((a,p) => a+p.score,0)/Math.max(servicePages.length,1))}\n`;

report += '\n=================================================================\n';
report += '  VERDICT\n';
report += '=================================================================\n';

const criticalPairs = pairs.filter(p => p.s >= 0.5).length;
const avgScore = Math.round(indexed.reduce((a,p) => a+p.score,0)/Math.max(indexed.length,1));
const thinPct = Math.round(thin.length/indexed.length*100);

report += `Scor mediu global:      ${avgScore}/100\n`;
report += `Pagini thin (<300w):    ${thinPct}% din indexate\n`;
report += `Perechi critic (>50%):  ${criticalPairs}\n`;
report += `Perechi mari (>30%):    ${over30.length}\n`;
report += `Perechi medii (>20%):   ${over20.length}\n\n`;

if (criticalPairs > 0) report += `⛔ CRITIC: ${criticalPairs} perechi cu similaritate >50% — necesita resize urgent!\n`;
if (thinPct > 30) report += `⛔ CRITIC: ${thinPct}% pagini cu continut prea subtire!\n`;
if (avgScore >= 80) report += `✅ CALITATE: Scor global excelent (${avgScore}/100)\n`;
else if (avgScore >= 65) report += `🟡 CALITATE: Scor global ok dar poate fi imbunatatit (${avgScore}/100)\n`;
else report += `🔴 CALITATE: Scor global slab (${avgScore}/100) — actiune imediata!\n`;

report += '=================================================================\n';

const outPath = path.join(ROOT, 'scripts/full_site_scan_result.txt');
fs.writeFileSync(outPath, report, 'utf-8');
console.log(report);
console.log(`\nSalvat in: ${outPath}`);
