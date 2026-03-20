// dup_content_audit.mjs — test complet continut duplicat pe tot site-ul
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

function collectAll(dir, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const fp = path.join(dir, e.name), rp = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) out.push(...collectAll(fp, rp));
    else if (e.name.endsWith('.astro') && !e.name.includes('[')) out.push({ rel: rp, fp });
  }
  return out;
}

// Extrage STRICT textul vizibil — ignora HTML, CSS, JS, URL-uri, atribute
function extractText(raw) {
  return raw
    .replace(/^---[\s\S]*?---/m, '')       // frontmatter
    .replace(/<!--[\s\S]*?-->/g, '')        // HTML comments
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/style="[^"]*"/g, '')
    .replace(/class="[^"]*"/g, '')
    .replace(/href="[^"]*"/g, '')
    .replace(/src="[^"]*"/g, '')
    .replace(/<[^>]+>/g, ' ')              // HTML tags
    .replace(/https?:\/\/[^\s]*/g, '')     // URLs
    .replace(/[^a-zA-Z\u00C0-\u024F\s]/g, ' ')  // keep only letters
    .replace(/\b\w{1,3}\b/g, ' ')          // remove very short words
    .replace(/\s+/g, ' ').trim().toLowerCase();
}

// Bigram Jaccard similarity
function simBigram(a, b) {
  const toBi = t => {
    const w = t.split(/\s+/).filter(x => x.length > 4);
    const s = new Set();
    for (let i = 0; i < w.length - 1; i++) s.add(w[i] + '_' + w[i + 1]);
    return s;
  };
  const sa = toBi(a), sb = toBi(b);
  if (!sa.size || !sb.size) return 0;
  const inter = [...sa].filter(x => sb.has(x)).length;
  return Math.round(inter / new Set([...sa, ...sb]).size * 100);
}

// ── MAIN ────────────────────────────────────────────────────────
const all = collectAll(path.join(ROOT, 'src/pages'));
const indexed = all.filter(p => !fs.readFileSync(p.fp, 'utf-8').includes('noindex'));

process.stderr.write(`Indexate: ${indexed.length} pagini\n`);

// Pre-extrage textul
const pages = indexed.map(p => {
  const raw = fs.readFileSync(p.fp, 'utf-8');
  return { rel: p.rel, text: extractText(raw) };
});

process.stderr.write(`Calculez ${Math.round(pages.length * (pages.length - 1) / 2)} perechi...\n`);

// Calculeaza toate perechile
const pairs = [];
for (let i = 0; i < pages.length; i++) {
  for (let j = i + 1; j < pages.length; j++) {
    const sim = simBigram(pages[i].text, pages[j].text);
    if (sim > 0) pairs.push({ a: pages[i].rel, b: pages[j].rel, sim });
  }
  if (i % 20 === 0) process.stderr.write(`  ${i}/${pages.length}\n`);
}

pairs.sort((a, b) => b.sim - a.sim);

const total = pairs.length;
const over80 = pairs.filter(p => p.sim >= 80);
const f50_80 = pairs.filter(p => p.sim >= 50 && p.sim < 80);
const f30_50 = pairs.filter(p => p.sim >= 30 && p.sim < 50);
const f20_30 = pairs.filter(p => p.sim >= 20 && p.sim < 30);
const under20 = pairs.filter(p => p.sim < 20);

// Pagini afectate
const affected80 = new Set(); over80.forEach(p => { affected80.add(p.a); affected80.add(p.b); });
const affected50 = new Set(); pairs.filter(p=>p.sim>=50).forEach(p => { affected50.add(p.a); affected50.add(p.b); });

// ── RAPORT ──────────────────────────────────────────────────────
let R = '';
R += '╔══════════════════════════════════════════════════════════════════╗\n';
R += '║   AUDIT COMPLET CONTINUT DUPLICAT — SUPERPARTY.RO               ║\n';
R += `║   ${new Date().toISOString().slice(0,10)}  |  ${indexed.length} pagini indexate  |  ${total} perechi analizate         ║\n`;
R += '╚══════════════════════════════════════════════════════════════════╝\n\n';

R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  DISTRIBUȚIE GLOBALĂ SIMILARITATE                                │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
const bar = (n, t, w=30) => '█'.repeat(Math.round(n/t*w)).padEnd(w);
R += `⛔ DUPLICATE (80-100%):  ${String(over80.length).padStart(5)} perechi [${bar(over80.length,total)}] ${Math.round(over80.length/total*100)}%\n`;
R += `🔴 Foarte similare(50-79%): ${String(f50_80.length).padStart(5)} perechi [${bar(f50_80.length,total)}] ${Math.round(f50_80.length/total*100)}%\n`;
R += `🟡 Similare (30-49%):    ${String(f30_50.length).padStart(5)} perechi [${bar(f30_50.length,total)}] ${Math.round(f30_50.length/total*100)}%\n`;
R += `🟢 Parțial (20-29%):     ${String(f20_30.length).padStart(5)} perechi [${bar(f20_30.length,total)}] ${Math.round(f20_30.length/total*100)}%\n`;
R += `✅ UNICE (0-19%):        ${String(under20.length).padStart(5)} perechi [${bar(under20.length,total)}] ${Math.round(under20.length/total*100)}%\n\n`;

R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  IMPACT PE PAGINI INDIVIDUALE                                     │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
R += `Pagini cu duplicate >80%:  ${affected80.size}/${indexed.length} (${Math.round(affected80.size/indexed.length*100)}%)\n`;
R += `Pagini cu similare >50%:   ${affected50.size}/${indexed.length} (${Math.round(affected50.size/indexed.length*100)}%)\n`;
R += `Pagini cu conținut UNIC:   ${indexed.length - affected50.size}/${indexed.length} (${Math.round((indexed.length-affected50.size)/indexed.length*100)}%)\n\n`;

R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  TOP 25 DUPLICATE (cele mai similare perechi)                    │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
for (const p of pairs.slice(0, 25)) {
  const ic = p.sim >= 80 ? '⛔' : p.sim >= 50 ? '🔴' : p.sim >= 30 ? '🟡' : '🟢';
  const a = p.a.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/');
  const b = p.b.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/');
  R += `${ic} ${String(p.sim)+'%'}  ${a.substring(0,42).padEnd(42)} ↔ ${b}\n`;
}
R += '\n';

// Per categorie
const cat = rel => {
  if (rel.startsWith('petreceri/')) return 'petreceri/comune';
  if (rel.includes('animatori-copii')) return 'animatori-copii';
  return 'alte pagini';
};
const catS = {};
for (const p of pairs) {
  const k = `${cat(p.a)} ↔ ${cat(p.b)}`.replace('petreceri/comune ↔ petreceri/comune','petreceri/comune (intern)').replace('animatori-copii ↔ animatori-copii','animatori-copii (intern)');
  if (!catS[k]) catS[k] = { t:0, o80:0, o50:0 };
  catS[k].t++; if(p.sim>=80) catS[k].o80++; if(p.sim>=50) catS[k].o50++;
}
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  STATISTICI PE CATEGORII                                         │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
for (const [k,v] of Object.entries(catS).sort((a,b)=>b[1].o80-a[1].o80)) {
  R += `${k}:\n  Total: ${v.t} | Duplicate >80%: ${v.o80} (${Math.round(v.o80/v.t*100)}%) | Similare >50%: ${v.o50} (${Math.round(v.o50/v.t*100)}%)\n`;
}
R += '\n';

R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  CONCLUZIE                                                       │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
const avgSim = Math.round(pairs.reduce((a,p)=>a+p.sim,0)/pairs.length);
R += `Similaritate medie globală:  ${avgSim}%\n`;
if (over80.length === 0) {
  R += '✅ Nu există pagini cu conținut identic (>80%)!\n';
  R += '✅ Site-ul respectă criteriile Google pentru conținut unic.\n';
} else {
  R += `⚠️  ${over80.length} perechi au conținut >80% similar — necesită intervenție.\n`;
}

const out = path.join(ROOT, 'scripts/dup_content_report.txt');
fs.writeFileSync(out, R, 'utf-8');
process.stdout.write(R);
process.stderr.write(`\n✅ Raport: scripts/dup_content_report.txt\n`);
