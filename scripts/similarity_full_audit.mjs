// similarity_full_audit.mjs
// Analizeaza similaritatea intre TOATE paginile site-ului
// Extrage DOAR textul din continut (nu HTML, nu template, nu atribute)
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

function collectAll(dir, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const fp = path.join(dir, e.name);
    const rp = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) out.push(...collectAll(fp, rp));
    else if (e.name.endsWith('.astro') && !e.name.includes('[')) out.push({ rel: rp, fp });
  }
  return out;
}

// Extrage STRICT textul vizibil pentru utilizator/Google
// Ignora: frontmatter, style, script, atribute HTML, comments HTML
function extractMainText(raw) {
  return raw
    .replace(/^---[\s\S]*?---/m, '') // frontmatter
    .replace(/<!--[\s\S]*?-->/g, '') // HTML comments
    .replace(/<style[\s\S]*?<\/style>/gi, '') // style blocks
    .replace(/<script[\s\S]*?<\/script>/gi, '') // script blocks
    .replace(/style="[^"]*"/g, '') // inline style attributes
    .replace(/class="[^"]*"/g, '') // class attributes
    .replace(/href="[^"]*"/g, '') // href attributes
    .replace(/src="[^"]*"/g, '') // src attributes
    .replace(/itemtype="[^"]*"/g, '') // itemtype
    .replace(/itemprop="[^"]*"/g, '') // itemprop
    .replace(/itemscope/g, '')
    .replace(/<[^>]+>/g, ' ') // HTML tags
    .replace(/https?:\/\/[^\s]+/g, '') // URLs
    .replace(/[^a-zA-Z\u00C0-\u024F\s]/g, ' ') // keep only letters
    .replace(/\b\w{1,3}\b/g, ' ') // remove very short words
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}

// Jaccard similarity pe bigramuri de cuvinte (mai bun pentru detectare duplicate)
function jaccardBigrams(textA, textB) {
  const toBigrams = (text) => {
    const words = text.split(/\s+/).filter(w => w.length >= 4);
    const bigrams = new Set();
    for (let i = 0; i < words.length - 1; i++) {
      bigrams.add(words[i] + '_' + words[i+1]);
    }
    return bigrams;
  };
  const a = toBigrams(textA);
  const b = toBigrams(textB);
  if (a.size === 0 || b.size === 0) return 0;
  const intersection = [...a].filter(x => b.has(x)).length;
  const union = new Set([...a, ...b]).size;
  return Math.round(intersection / union * 100);
}

// ── MAIN ────────────────────────────────────────────────────────────
const all = collectAll(path.join(ROOT, 'src/pages'));
const indexed = all.filter(p => !fs.readFileSync(p.fp, 'utf-8').includes('noindex'));

process.stderr.write(`Analiz ${indexed.length} pagini indexate...\n`);

// Pre-extract content
const pages = indexed.map(p => {
  const raw = fs.readFileSync(p.fp, 'utf-8');
  const text = extractMainText(raw);
  const words = text.split(/\s+/).filter(w => w.length >= 4);
  return { rel: p.rel, text, words: words.length };
});

process.stderr.write(`Calculez ${Math.round(pages.length*(pages.length-1)/2)} perechi...\n`);

// Calculate all pairs
const pairs = [];
for (let i = 0; i < pages.length; i++) {
  for (let j = i + 1; j < pages.length; j++) {
    const sim = jaccardBigrams(pages[i].text, pages[j].text);
    if (sim > 0) pairs.push({ a: pages[i].rel, b: pages[j].rel, sim });
  }
  if (i % 30 === 0) process.stderr.write(`Progress: ${i}/${pages.length}\n`);
}

// Statistici
const totalPairs = pairs.length;
const over80 = pairs.filter(p => p.sim >= 80);
const over50 = pairs.filter(p => p.sim >= 50);
const over30 = pairs.filter(p => p.sim >= 30);
const over20 = pairs.filter(p => p.sim >= 20);
const under20 = pairs.filter(p => p.sim < 20);

// Sort worst first
pairs.sort((a, b) => b.sim - a.sim);

// Build report
let R = '';
R += '╔══════════════════════════════════════════════════════════════════╗\n';
R += '║  AUDIT COMPLET SIMILARITATE — TOATE PAGINILE SUPERPARTY.RO      ║\n';
R += `║  Data: ${new Date().toISOString().slice(0,10)}  Total pagini: ${indexed.length}  Total perechi: ${totalPairs}  ║\n`;
R += '╚══════════════════════════════════════════════════════════════════╝\n\n';

// Distributie globala
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  DISTRIBUȚIE SIMILARITATE — TOATE PAGINILE                       │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
R += `⛔ Identice/Duplicate (80-100%):  ${over80.length} perechi   = ${Math.round(over80.length/totalPairs*100)}% din total\n`;
R += `⚠️  Foarte similare (50-79%):     ${over50.filter(p=>p.sim<80).length} perechi   = ${Math.round(over50.filter(p=>p.sim<80).length/totalPairs*100)}%\n`;
R += `🟡 Similare (30-49%):            ${over30.filter(p=>p.sim<50).length} perechi   = ${Math.round(over30.filter(p=>p.sim<50).length/totalPairs*100)}%\n`;
R += `🟢 Parțial similare (20-29%):    ${over20.filter(p=>p.sim<30).length} perechi   = ${Math.round(over20.filter(p=>p.sim<30).length/totalPairs*100)}%\n`;
R += `✅ Unice (sub 20%):              ${under20.length} perechi   = ${Math.round(under20.length/totalPairs*100)}%\n\n`;

// Cat la suta din pagini au VREUN duplicat
const pagesWithDups = new Set();
over80.forEach(p => { pagesWithDups.add(p.a); pagesWithDups.add(p.b); });
const pagesOver50 = new Set();
over50.forEach(p => { pagesOver50.add(p.a); pagesOver50.add(p.b); });

R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  IMPACT PE PAGINI INDIVIDUALE                                     │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
R += `Pagini cu duplicate >80%: ${pagesWithDups.size}/${indexed.length} (${Math.round(pagesWithDups.size/indexed.length*100)}%)\n`;
R += `Pagini cu similare >50%:  ${pagesOver50.size}/${indexed.length} (${Math.round(pagesOver50.size/indexed.length*100)}%)\n`;
R += `Pagini cu continut UNIC: ${indexed.length - pagesOver50.size}/${indexed.length} (${Math.round((indexed.length-pagesOver50.size)/indexed.length*100)}%)\n\n`;

// Top 30 perechi duplicate
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  TOP 30 DUPLICATE — PERECHI CEL MAI SIMILARE                    │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
const top30 = pairs.slice(0, 30);
for (const p of top30) {
  const ic = p.sim >= 80 ? '⛔' : p.sim >= 50 ? '⚠️ ' : p.sim >= 30 ? '🟡' : '🟢';
  const a = p.a.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/');
  const b = p.b.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/');
  R += `${ic} ${p.sim}%  ${a.padEnd(45)}↔ ${b}\n`;
}
R += '\n';

// Analiza pe categorii
const categorize = (rel) => {
  if (rel.startsWith('petreceri/')) return 'petreceri/comune';
  if (rel.startsWith('animatori-copii-')) return 'animatori-copii-*';
  return 'alte pagini (servicii, homepage etc.)';
};

const catStats = {};
for (const p of pairs) {
  const catA = categorize(p.a), catB = categorize(p.b);
  const catKey = catA === catB ? catA : `${catA} ↔ ${catB}`;
  if (!catStats[catKey]) catStats[catKey] = { total: 0, over80: 0, over50: 0 };
  catStats[catKey].total++;
  if (p.sim >= 80) catStats[catKey].over80++;
  if (p.sim >= 50) catStats[catKey].over50++;
}

R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  SIMILARITATE PE CATEGORII DE PAGINI                            │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
for (const [cat, stat] of Object.entries(catStats).sort((a,b)=>b[1].over80-a[1].over80)) {
  const pct80 = Math.round(stat.over80/stat.total*100);
  const pct50 = Math.round(stat.over50/stat.total*100);
  R += `${cat}:\n`;
  R += `  Total perechi: ${stat.total} | Duplicate (>80%): ${stat.over80} (${pct80}%) | Similare (>50%): ${stat.over50} (${pct50}%)\n`;
}
R += '\n';

// Media de similaritate per categorie
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  CONCLUZIE SI RECOMANDARI                                        │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
const avgSim = Math.round(pairs.reduce((a,p)=>a+p.sim,0)/pairs.length);
R += `Similaritate medie globala: ${avgSim}%\n`;
R += `Perechi identice (>80%): ${over80.length} din ${totalPairs} (${Math.round(over80.length/totalPairs*100)}%)\n\n`;
if (over80.length === 0) {
  R += '✅ Nu exista pagini cu continut identic (>80% similar)!\n';
  R += '✅ Site-ul are continut suficient de unic pentru a evita penalizarile Google.\n';
} else {
  R += `⚠️  ${over80.length} perechi de pagini au continut >80% identic.\n`;
  R += `    Recomandare: rescrie sectiunile identice cu text specific per localitate.\n`;
}

// Save
const outPath = path.join(ROOT, 'scripts/similarity_full_report.txt');
fs.writeFileSync(outPath, R, 'utf-8');
process.stdout.write(R);
process.stderr.write(`\n✅ Raport salvat: scripts/similarity_full_report.txt\n`);
