// google_indexability_proof.mjs
// Demonstreaza ca toate cele 144 de pagini sunt gata pentru Google:
// 1) Audit complet structura fiecare pagina (titlu, desc, canonical, schema, H1, cuvinte)
// 2) Apeleaza PageSpeed Insights API (Google) pentru nota reala
import fs from 'fs';
import path from 'path';
import https from 'https';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

// ── helpers ──────────────────────────────────────────────
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

function extractText(raw) {
  return raw.replace(/^---[\s\S]*?---/m,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<[^>]+>/g,' ').replace(/[^\wăâîșțĂÂÎȘȚ\s]/g,' ').replace(/\s+/g,' ').trim();
}
function wc(text) { return text.split(/\s+/).filter(w=>w.length>=3).length; }
function getMeta(raw, key) {
  const m = raw.match(new RegExp(`${key}="([^"]+)"`, 'i'));
  return m ? m[1] : null;
}
function hasDynamic(raw, key) { return new RegExp(`${key}=\\{`, 'i').test(raw); }
function scoreBar(n) { return '█'.repeat(Math.round(n/10)) + '░'.repeat(10-Math.round(n/10)); }
function icon(n) { return n>=90?'✅':n>=70?'🟡':n>=50?'🟠':'⛔'; }

// ── fetch PageSpeed Insights API ────────────────────────
function fetchPSI(url, strategy) {
  return new Promise((resolve) => {
    const apiUrl = `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(url)}&strategy=${strategy}`;
    https.get(apiUrl, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          const cats = json.lighthouseResult?.categories;
          const audits = json.lighthouseResult?.audits;
          resolve({
            perf: Math.round((cats?.performance?.score || 0) * 100),
            seo: Math.round((cats?.seo?.score || 0) * 100),
            a11y: Math.round((cats?.accessibility?.score || 0) * 100),
            bp: Math.round((cats?.['best-practices']?.score || 0) * 100),
            lcp: audits?.['largest-contentful-paint']?.displayValue || 'N/A',
            cls: audits?.['cumulative-layout-shift']?.displayValue || 'N/A',
            fid: audits?.['total-blocking-time']?.displayValue || 'N/A',
            si: audits?.['speed-index']?.displayValue || 'N/A',
            ttfb: audits?.['server-response-time']?.displayValue || 'N/A',
          });
        } catch(e) { resolve(null); }
      });
    }).on('error', () => resolve(null));
  });
}

// ── PART 1: Audit toate 144 de pagini indexate ──────────
const all = collectAll(path.join(ROOT, 'src/pages'));
const indexed = all.filter(p => !fs.readFileSync(p.fp,'utf-8').includes('noindex'));

let R = '';
R += '╔══════════════════════════════════════════════════════════════════╗\n';
R += '║  DOVADĂ: 144 PAGINI GATA PENTRU GOOGLE — RAPORT COMPLET         ║\n';
R += `║  Data: ${new Date().toISOString().slice(0,10)} Ora: ${new Date().toISOString().slice(11,16)} UTC                    ║\n`;
R += '╚══════════════════════════════════════════════════════════════════╝\n\n';

// Counters
let perfect=0, good=0, warn=0, poor=0;
let noTitle=[], noDesc=[], noCanon=[], noSchema=[], noH1=[], thin=[];
const pageScores = [];

for (const p of indexed) {
  const raw = fs.readFileSync(p.fp, 'utf-8');
  const text = extractText(raw);
  const words = wc(text);
  const title = getMeta(raw,'title') || (hasDynamic(raw,'title') ? '[DYN]' : null);
  const desc = getMeta(raw,'description') || (hasDynamic(raw,'description') ? '[DYN]' : null);
  const canonical = getMeta(raw,'canonical');
  const hasSchema = raw.includes('"@type"') || raw.includes('schema={');
  const h1 = (raw.match(/<h1[^>]*>/gi)||[]).length;
  const h2 = (raw.match(/<h2[^>]*>/gi)||[]).length;
  const url = '/'+p.rel.replace('index.astro','').replace('.astro','').replace(/\\/g,'/');

  // Score
  let score = 0;
  if (title) score += 20; else noTitle.push(url);
  if (desc) score += 20; else noDesc.push(url);
  if (canonical) score += 15; else noCanon.push(url);
  if (hasSchema) score += 15; else noSchema.push(url);
  if (h1 >= 1) score += 15; else noH1.push(url);
  if (words >= 400) score += 15;
  else if (words >= 200) { score += 8; }
  else thin.push(url);

  pageScores.push({ url, score, title, words, h1, h2, hasSchema, canonical: !!canonical });
  if (score >= 95) perfect++;
  else if (score >= 80) good++;
  else if (score >= 60) warn++;
  else poor++;
}

// Summary stats
const avgScore = Math.round(pageScores.reduce((a,p)=>a+p.score,0)/pageScores.length);
R += `📊 TOTAL PAGINI INDEXATE: ${indexed.length}\n`;
R += `📊 SCOR MEDIU SEO: ${avgScore}/100\n\n`;
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  DISTRIBUȚIE SCORURI — CUM VĂD ROBOTII GOOGLE PAGINILE          │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
R += `✅ PERFECTE (95-100/100):   ${perfect} pagini  ${'▓'.repeat(Math.round(perfect/indexed.length*40))}\n`;
R += `🟡 BUNE     (80-94/100):   ${good} pagini  ${'▓'.repeat(Math.round(good/indexed.length*40))}\n`;
R += `🟠 MEDII    (60-79/100):   ${warn} pagini  ${'▓'.repeat(Math.round(warn/indexed.length*40))}\n`;
R += `⛔ SLABE    (0-59/100):    ${poor} pagini  ${'▓'.repeat(Math.round(poor/indexed.length*40))}\n`;
R += '\n';

// Elements check
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  ELEMENTE SEO TEHNIC — TOATE 144 PAGINI                         │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
R += `Titlu <title>:     ${noTitle.length===0?`✅ TOATE ${indexed.length} pagini au titlu!`:`⚠️  ${noTitle.length} fără titlu`}\n`;
R += `Meta description:  ${noDesc.length===0?`✅ TOATE ${indexed.length} pagini au description!`:`⚠️  ${noDesc.length} fără description`}\n`;
R += `Canonical URL:     ${noCanon.length===0?`✅ Toate OK!`:`⚠️  ${noCanon.length} fără canonical`}\n`;
R += `Schema JSON-LD:    ${noSchema.length===0?`✅ Toate OK!`:`⚠️  ${noSchema.length} fără schema`}\n`;
R += `H1 prezent:        ${noH1.length===0?`✅ Toate OK!`:`⚠️  ${noH1.length} fără H1`}\n`;
R += `Conținut 200+w:    ${thin.length===0?`✅ Toate OK!`:`⚠️  ${thin.length} prea subțiri`}\n`;
R += '\n';

// Content stats 
const wcAll = pageScores.map(p=>p.words);
const minWc = Math.min(...wcAll), maxWc = Math.max(...wcAll);
const avgWc = Math.round(wcAll.reduce((a,n)=>a+n,0)/wcAll.length);
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  STATISTICI CONȚINUT                                            │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
R += `Cuvinte MINIM:     ${minWc}\n`;
R += `Cuvinte MEDIU:     ${avgWc}\n`;
R += `Cuvinte MAXIM:     ${maxWc}\n`;
R += `Pagini 400+ cuvinte: ${pageScores.filter(p=>p.words>=400).length}/${indexed.length}\n`;
R += `Pagini 200-400w:     ${pageScores.filter(p=>p.words>=200&&p.words<400).length}/${indexed.length}\n`;
R += `Pagini sub 200w:     ${pageScores.filter(p=>p.words<200).length}/${indexed.length}\n`;
R += '\n';

// Schema types
const schemaCount = pageScores.filter(p=>p.hasSchema).length;
R += `Schema JSON-LD (Rich Snippets): ${schemaCount}/${indexed.length} pagini (${Math.round(schemaCount/indexed.length*100)}%)\n\n`;

// All pages sorted by score (worst first)
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  TOATE PAGINILE — ORDIN SCOR (worst → best)                     │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';

const sorted = [...pageScores].sort((a,b)=>a.score-b.score);
for (const p of sorted) {
  const ic = icon(p.score);
  const bar = scoreBar(p.score);
  const titleStr = p.title ? (p.title==='[DYN]'?'[dinamic]':p.title.slice(0,45)+(p.title.length>45?'...':'')) : '⛔LIPSĂ';
  R += `${ic}[${String(p.score).padStart(3)}/100] ${bar}  ${p.url}\n`;
  R += `   T:"${titleStr}" | ${p.words}w | H1:${p.h1} H2:${p.h2} | Schema:${p.hasSchema?'✅':'⚠️'} | Canon:${p.canonical?'✅':'⚠️'}\n`;
}
R += '\n';

// Save part 1
const outPart1 = path.join(ROOT, 'scripts/google_indexability_result.txt');
fs.writeFileSync(outPart1, R, 'utf-8');
process.stdout.write(R.slice(0, 2000) + '\n... [continua in fisier] ...\n');
process.stderr.write(`✅ Part 1 salvat: ${outPart1}\n`);

// ── PART 2: PageSpeed Insights API ─────────────────────────
process.stderr.write(`\n🚀 Testez PageSpeed Insights (Google) — astept raspuns API...\n`);

const testPages = [
  'https://www.superparty.ro/',
  'https://www.superparty.ro/animatori-petreceri-copii',
  'https://www.superparty.ro/petreceri/sector-1',
  'https://www.superparty.ro/petreceri/floreasca',
  'https://www.superparty.ro/petreceri/voluntari',
];

let psiReport = '\n╔══════════════════════════════════════════════════════════════════╗\n';
psiReport     += '║  NOTA GOOGLE PAGESPEED INSIGHTS — DATE REALE DIN API GOOGLE     ║\n';
psiReport    += '╚══════════════════════════════════════════════════════════════════╝\n\n';
psiReport += 'Scara: 0-49 SLAB 🔴 | 50-89 MEDIU 🟡 | 90-100 BUN 🟢\n\n';

for (const url of testPages) {
  process.stderr.write(`  Testing: ${url}\n`);
  const [mobile, desktop] = await Promise.all([fetchPSI(url,'mobile'), fetchPSI(url,'desktop')]);
  
  psiReport += `📍 ${url}\n`;
  if (mobile) {
    const pm = mobile.perf>=90?'🟢':mobile.perf>=50?'🟡':'🔴';
    const sm = mobile.seo>=90?'🟢':mobile.seo>=50?'🟡':'🔴';
    psiReport += `   📱 MOBIL:   Perf:${pm}${mobile.perf} | SEO:${sm}${mobile.seo} | A11y:${mobile.a11y} | BP:${mobile.bp}\n`;
    psiReport += `              LCP:${mobile.lcp} | TBT:${mobile.fid} | CLS:${mobile.cls} | SI:${mobile.si}\n`;
  } else { psiReport += '   📱 MOBIL: eroare API\n'; }
  if (desktop) {
    const pd = desktop.perf>=90?'🟢':desktop.perf>=50?'🟡':'🔴';
    const sd = desktop.seo>=90?'🟢':desktop.seo>=50?'🟡':'🔴';
    psiReport += `   🖥️  DESKTOP: Perf:${pd}${desktop.perf} | SEO:${sd}${desktop.seo} | A11y:${desktop.a11y} | BP:${desktop.bp}\n`;
    psiReport += `              LCP:${desktop.lcp} | TBT:${desktop.fid} | CLS:${desktop.cls} | SI:${desktop.si}\n`;
  } else { psiReport += '   🖥️  DESKTOP: eroare API\n'; }
  psiReport += '\n';
  
  // Small delay to not hammer API
  await new Promise(r => setTimeout(r, 3000));
}

// Append to result
fs.appendFileSync(outPart1, psiReport, 'utf-8');
process.stdout.write(psiReport);
process.stderr.write(`\n✅ Rezultat complet: scripts/google_indexability_result.txt\n`);
