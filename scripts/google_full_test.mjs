// google_full_test.mjs — Test COMPLET cum vede Google superparty.ro
// Acoperă TOATE cele 145 de pagini, tot conținutul, toți factorii de ranking
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

// ═══════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════
function collectAll(dir, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const fp = path.join(dir, e.name);
    const rp = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) out.push(...collectAll(fp, rp));
    else if (e.isFile() && e.name.endsWith('.astro') && !e.name.includes('[')) out.push({ rel: rp, fp });
  }
  return out;
}

function extractText(raw) {
  return raw
    .replace(/^---[\s\S]*?---/m, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\{[^{}]*\}/g, ' ')
    .replace(/import\s+[^;]+;/g, '')
    .replace(/const\s+\w+\s*=.*?;/g, '')
    .replace(/[^\wăâîșțĂÂÎȘȚ\-\s]/g, ' ')
    .replace(/\s+/g, ' ').trim();
}

function words(text) {
  return text.split(/\s+/).filter(w => w.length >= 3).length;
}

function getMeta(raw, key) {
  const m = raw.match(new RegExp(`${key}="([^"]+)"`, 'i'));
  if (m) return m[1];
  // Also try expression form: key={`...`} for dynamic
  const m2 = raw.match(new RegExp(`${key}=\\{['\`]([^'\`]+)['\`]\\}`, 'i'));
  return m2 ? m2[1] : null;
}

function getMetaDynamic(raw, key) {
  // Detect both static "..." and dynamic {...} values
  const staticM = raw.match(new RegExp(`${key}="([^"]+)"`, 'i'));
  if (staticM) return { val: staticM[1], isDynamic: false };
  const dynM = raw.match(new RegExp(`${key}=\\{`, 'i'));
  if (dynM) return { val: '[DINAMIC]', isDynamic: true };
  return null;
}

function getImages(raw) {
  const imgs = [];
  const re = /<img([^>]+)>/gi;
  let m;
  while ((m = re.exec(raw)) !== null) {
    const attrs = m[1];
    const src = (attrs.match(/src="([^"]+)"/) || attrs.match(/src=\{([^}]+)\}/) || [])[1] || '';
    const alt = (attrs.match(/alt="([^"]*)"/) || [])[1];
    imgs.push({ src, hasAlt: alt !== undefined, alt: alt || '' });
  }
  return imgs;
}

function getLinks(raw) {
  const links = [];
  const re = /href="([^"]+)"/gi;
  let m;
  while ((m = re.exec(raw)) !== null) {
    links.push(m[1]);
  }
  return links;
}

function getHeadings(raw) {
  const h1 = (raw.match(/<h1[^>]*>/gi) || []).length;
  const h2 = (raw.match(/<h2[^>]*>/gi) || []).length;
  const h3 = (raw.match(/<h3[^>]*>/gi) || []).length;
  return { h1, h2, h3 };
}

function getSchema(raw) {
  const types = [];
  const re = /"@type"\s*:\s*"([^"]+)"/g;
  let m;
  while ((m = re.exec(raw)) !== null) types.push(m[1]);
  return types;
}

function jaccardSim(a, b) {
  const setA = new Set(a.split(/\s+/).filter(w => w.length >= 5));
  const setB = new Set(b.split(/\s+/).filter(w => w.length >= 5));
  const inter = [...setA].filter(w => setB.has(w)).length;
  const union = new Set([...setA, ...setB]).size;
  return union === 0 ? 0 : (inter / union * 100);
}

// ═══════════════════════════════════════════════════════════════
// COLLECT ALL PAGES
// ═══════════════════════════════════════════════════════════════
const allPages = collectAll(path.join(ROOT, 'src/pages'));

// ═══════════════════════════════════════════════════════════════
// ANALYZE EACH PAGE
// ═══════════════════════════════════════════════════════════════
const analyzed = [];
for (const { rel, fp } of allPages) {
  const raw = fs.readFileSync(fp, 'utf-8');
  const text = extractText(raw);
  const wc = words(text);
  const isNoindex = raw.includes('noindex');
  const isIndex = !isNoindex;

  const titleMeta = getMetaDynamic(raw, 'title');
  const descMeta = getMetaDynamic(raw, 'description');
  const canonical = getMeta(raw, 'canonical');
  const schemaTypes = getSchema(raw);
  const hasSchema = schemaTypes.length > 0 || raw.includes('schema={schema}');
  const { h1, h2, h3 } = getHeadings(raw);
  const imgs = getImages(raw);
  const imgsNoAlt = imgs.filter(i => !i.hasAlt);
  const links = getLinks(raw);
  const internalLinks = links.filter(l => l.startsWith('/') || l.includes('superparty.ro'));
  const externalLinks = links.filter(l => l.startsWith('http') && !l.includes('superparty.ro'));

  const url = '/' + rel.replace('index.astro', '').replace('.astro', '').replace(/\\/g, '/').replace(/\/$/, '');
  const slug = rel.replace('index.astro', '').replace('.astro', '').replace(/\\/g, '/');

  // Scoring (100 pt max)
  let score = 0;
  const issues = [];

  // Title (20 pts)
  if (!titleMeta) { issues.push({ sev: 3, msg: 'CRITIC: Lipsă titlu' }); }
  else if (titleMeta.isDynamic) { score += 18; }
  else {
    const tl = titleMeta.val.length;
    if (tl < 20) { issues.push({ sev: 2, msg: `Titlu prea scurt (${tl}chr)` }); score += 8; }
    else if (tl > 70) { issues.push({ sev: 1, msg: `Titlu prea lung (${tl}chr > 65)` }); score += 14; }
    else { score += 20; }
  }

  // Description (20 pts)
  if (!descMeta) { issues.push({ sev: 3, msg: 'CRITIC: Lipsă meta description' }); }
  else if (descMeta.isDynamic) { score += 18; }
  else {
    const dl = descMeta.val.length;
    if (dl < 70) { issues.push({ sev: 2, msg: `Desc prea scurtă (${dl}chr)` }); score += 8; }
    else if (dl > 165) { issues.push({ sev: 1, msg: `Desc prea lungă (${dl}chr > 160)` }); score += 14; }
    else { score += 20; }
  }

  // Canonical (10 pts)
  if (!canonical) { if (isIndex) issues.push({ sev: 2, msg: 'Lipsă canonical URL' }); }
  else { score += 10; }

  // Schema (10 pts)
  if (!hasSchema) { if (isIndex) issues.push({ sev: 2, msg: 'Lipsă Schema JSON-LD' }); }
  else { score += 10; }

  // H1 — o singură dată (10 pts)
  if (h1 === 0) { issues.push({ sev: 2, msg: 'Tag H1 lipsă' }); }
  else if (h1 > 1) { issues.push({ sev: 1, msg: `Multiple H1 (${h1}) — SEO negativ` }); score += 5; }
  else { score += 10; }

  // Content word count (20 pts)
  if (wc < 50) { issues.push({ sev: 3, msg: `Conținut extrem de subțire (${wc}w)` }); }
  else if (wc < 200) { issues.push({ sev: 2, msg: `Conținut subțire (${wc}w, ideal 500+)` }); score += 6; }
  else if (wc < 400) { issues.push({ sev: 1, msg: `Conținut mediu (${wc}w, ideal 500+)` }); score += 13; }
  else { score += 20; }

  // Images alt (5 pts)
  if (imgs.length > 0) {
    const altRatio = (imgs.length - imgsNoAlt.length) / imgs.length;
    if (altRatio < 0.5) { issues.push({ sev: 2, msg: `${imgsNoAlt.length}/${imgs.length} imagini fără alt` }); }
    else if (altRatio < 1) { issues.push({ sev: 1, msg: `${imgsNoAlt.length} imagini fără alt` }); score += 3; }
    else { score += 5; }
  } else { score += 5; } // no images = no issue

  // H2 structure (5 pts)
  if (h2 === 0 && wc > 200) { issues.push({ sev: 1, msg: 'Fără H2 — structură săracă' }); }
  else { score += 5; }

  score = Math.min(Math.max(score, 0), 100);

  analyzed.push({
    rel, url, slug, fp, isIndex, isNoindex,
    title: titleMeta?.val, titleLen: titleMeta?.val?.length || 0, titleDynamic: titleMeta?.isDynamic,
    desc: descMeta?.val, descLen: descMeta?.val?.length || 0, descDynamic: descMeta?.isDynamic,
    canonical, hasSchema, schemaTypes,
    h1, h2, h3, imgs: imgs.length, imgsNoAlt: imgsNoAlt.length,
    internalLinks: internalLinks.length, externalLinks: externalLinks.length,
    wc, text, score, issues
  });
}

const indexed = analyzed.filter(p => p.isIndex);
const noindexed = analyzed.filter(p => p.isNoindex);

// ═══════════════════════════════════════════════════════════════
// SIMILARITY CHECK pe paginile indexate
// ═══════════════════════════════════════════════════════════════
process.stderr.write(`Calculez similaritate pentru ${indexed.length} pagini indexate...\n`);
const simPairs = [];
for (let i = 0; i < indexed.length; i++) {
  for (let j = i + 1; j < indexed.length; j++) {
    const sim = jaccardSim(indexed[i].text, indexed[j].text);
    if (sim > 20) simPairs.push({ a: indexed[i].slug, b: indexed[j].slug, sim: sim.toFixed(1) });
  }
}
simPairs.sort((a, b) => b.sim - a.sim);
const highSim30 = simPairs.filter(p => p.sim > 30);
const highSim20 = simPairs.filter(p => p.sim > 20);

// ═══════════════════════════════════════════════════════════════
// SITEMAP CHECK
// ═══════════════════════════════════════════════════════════════
const sitemapFp = path.join(ROOT, 'public/sitemap.xml');
let sitemapUrls = [];
if (fs.existsSync(sitemapFp)) {
  const sm = fs.readFileSync(sitemapFp, 'utf-8');
  sitemapUrls = (sm.match(/<loc>([^<]+)<\/loc>/g) || []).map(l => l.replace(/<\/?loc>/g, ''));
}

// Check which indexed pages are in sitemap
const indexedNotInSitemap = indexed.filter(p => {
  const slug = p.slug.replace(/\/$/, '');
  return !sitemapUrls.some(u => u.includes(slug) || u.endsWith('/') && u.includes(slug.replace(/\/$/, '')));
});

// ═══════════════════════════════════════════════════════════════
// ROBOTS.TXT
// ═══════════════════════════════════════════════════════════════
const robotsFp = path.join(ROOT, 'public/robots.txt');
let robotsContent = '';
let robotsDisallows = [];
if (fs.existsSync(robotsFp)) {
  robotsContent = fs.readFileSync(robotsFp, 'utf-8');
  robotsDisallows = (robotsContent.match(/Disallow:\s*([^\n]+)/g) || []).map(d => d.replace('Disallow:', '').trim());
}

// ═══════════════════════════════════════════════════════════════
// GENERATE REPORT
// ═══════════════════════════════════════════════════════════════
const avgScore = Math.round(indexed.reduce((a, p) => a + p.score, 0) / Math.max(indexed.length, 1));
const avgScoreAll = Math.round(analyzed.reduce((a, p) => a + p.score, 0) / Math.max(analyzed.length, 1));

const noTitle = indexed.filter(p => !p.title && !p.titleDynamic);
const noDesc = indexed.filter(p => !p.desc && !p.descDynamic);
const noCanon = indexed.filter(p => !p.canonical);
const noSchema = indexed.filter(p => !p.hasSchema);
const noH1 = indexed.filter(p => p.h1 === 0);
const multiH1 = indexed.filter(p => p.h1 > 1);
const thin50 = indexed.filter(p => p.wc < 50);
const thin200 = indexed.filter(p => p.wc >= 50 && p.wc < 200);
const medium = indexed.filter(p => p.wc >= 200 && p.wc < 400);
const rich = indexed.filter(p => p.wc >= 400);
const hasImgNoAlt = indexed.filter(p => p.imgsNoAlt > 0);
const perfect = indexed.filter(p => p.issues.length === 0);

const scoreBar = n => '█'.repeat(Math.round(n/10)) + '░'.repeat(10-Math.round(n/10));
const icon = n => n >= 90 ? '✅' : n >= 70 ? '🟡' : n >= 50 ? '🟠' : '⛔';

let R = '';
R += '╔══════════════════════════════════════════════════════════════╗\n';
R += '║    TEST COMPLET SEO — CUM VEDE GOOGLE SUPERPARTY.RO         ║\n';
R += `║    Data: ${new Date().toISOString().slice(0,10)}  Ora: ${new Date().toISOString().slice(11,16)} UTC            ║\n`;
R += '╚══════════════════════════════════════════════════════════════╝\n\n';

R += `📊 SCOR PAGINI INDEXATE: ${avgScore}/100  ${scoreBar(avgScore)}\n`;
R += `📊 SCOR TOATE PAGINILE:  ${avgScoreAll}/100  ${scoreBar(avgScoreAll)}\n\n`;

// ─── INVENTAR ───────────────────────────────────────────────
R += '┌──────────────────────────────────────────────────────────────┐\n';
R += '│  INVENTAR COMPLET SITE                                       │\n';
R += '└──────────────────────────────────────────────────────────────┘\n';
R += `Total fișiere .astro (pagini):     ${analyzed.length}\n`;
R += `  ✅ Indexate de Google:           ${indexed.length}\n`;
R += `  🚫 NOINDEX (ascunse):            ${noindexed.length}\n`;
R += `Sitemap.xml:  ${fs.existsSync(sitemapFp) ? `✅ găsit — ${sitemapUrls.length} URL-uri` : '⛔ LIPSĂ!'}\n`;
R += `Robots.txt:   ${fs.existsSync(robotsFp) ? '✅ găsit' : '⛔ LIPSĂ!'}\n`;
if (robotsDisallows.some(d => d === '/' || d === '')) {
  R += `⛔ ROBOTS BLOCHEAZĂ TOATE PAGINILE! Disallow: /\n`;
} else if (robotsDisallows.length > 0) {
  R += `⚠️  Robots.txt blochează: ${robotsDisallows.join(', ')}\n`;
}
R += '\n';

// ─── CALITATE CONTINUT ──────────────────────────────────────
R += '┌──────────────────────────────────────────────────────────────┐\n';
R += '│  CALITATE CONȚINUT (pagini indexate)                         │\n';
R += '└──────────────────────────────────────────────────────────────┘\n';
R += `Conținut BOGAT (400+ cuvinte):   ✅ ${rich.length} pagini\n`;
R += `Conținut MEDIU (200-400w):       🟡 ${medium.length} pagini\n`;
R += `Conținut SUBȚIRE (50-200w):      🟠 ${thin200.length} pagini\n`;
R += `Conținut CRITIC (<50w):          ⛔ ${thin50.length} pagini\n`;
if (thin50.length > 0) thin50.forEach(p => R += `  ⛔ [${p.wc}w] ${p.url}\n`);
if (thin200.length > 0) thin200.forEach(p => R += `  🟠 [${p.wc}w] ${p.url}\n`);
R += '\n';

// ─── ELEMENTE SEO TEHNIC ────────────────────────────────────
R += '┌──────────────────────────────────────────────────────────────┐\n';
R += '│  SEO TEHNIC — ELEMENTE FUNDAMENTALE (pagini indexate)        │\n';
R += '└──────────────────────────────────────────────────────────────┘\n';
R += `Titlu <title>:          ${noTitle.length === 0 ? '✅ Toate OK' : `⛔ LIPSĂ pe ${noTitle.length} pagini`}\n`;
R += `Meta description:       ${noDesc.length === 0 ? '✅ Toate OK' : `⛔ LIPSĂ pe ${noDesc.length} pagini`}\n`;
R += `Canonical URL:          ${noCanon.length === 0 ? '✅ Toate OK' : `⚠️  LIPSĂ pe ${noCanon.length} pagini`}\n`;
R += `Schema JSON-LD:         ${noSchema.length === 0 ? '✅ Toate OK' : `⚠️  LIPSĂ pe ${noSchema.length} pagini`}\n`;
R += `H1 unic:                ${noH1.length + multiH1.length === 0 ? '✅ Toate OK' : `⚠️  Probleme pe ${noH1.length + multiH1.length} pagini`}\n`;
R += `  - Fără H1:            ${noH1.length > 0 ? `⚠️  ${noH1.length}` : '✅ 0'}\n`;
R += `  - Multiple H1:        ${multiH1.length > 0 ? `⚠️  ${multiH1.length}` : '✅ 0'}\n`;
R += `Imagini fără alt:       ${hasImgNoAlt.length === 0 ? '✅ OK' : `⚠️  ${hasImgNoAlt.length} pagini cu alt lipsă`}\n`;
hasImgNoAlt.forEach(p => R += `  → ${p.url}: ${p.imgsNoAlt}/${p.imgs} fără alt\n`);
R += '\n';

// ─── SITEMAP CHECK ──────────────────────────────────────────
R += '┌──────────────────────────────────────────────────────────────┐\n';
R += '│  SITEMAP — ACOPERIRE INDEXATE                                │\n';
R += '└──────────────────────────────────────────────────────────────┘\n';
R += `URL-uri în sitemap:     ${sitemapUrls.length}\n`;
R += `Pagini indexate total:  ${indexed.length}\n`;
R += `În sitemap:             ${indexed.length - indexedNotInSitemap.length}/${indexed.length}\n`;
if (indexedNotInSitemap.length > 0) {
  R += `⚠️  Lipsesc din sitemap: ${indexedNotInSitemap.length} pagini\n`;
  indexedNotInSitemap.forEach(p => R += `  → ${p.url}\n`);
} else {
  R += `✅ Toate paginile indexate sunt în sitemap!\n`;
}
R += '\n';

// ─── CARE TIPURI DE SCHEMA ──────────────────────────────────
R += '┌──────────────────────────────────────────────────────────────┐\n';
R += '│  SCHEMA JSON-LD — TIPURI DETECTATE                          │\n';
R += '└──────────────────────────────────────────────────────────────┘\n';
const schemaMap = {};
for (const p of indexed.filter(q => q.hasSchema)) {
  for (const t of p.schemaTypes) {
    schemaMap[t] = (schemaMap[t] || 0) + 1;
  }
}
for (const [type, count] of Object.entries(schemaMap).sort((a,b) => b[1]-a[1])) {
  R += `  ${type.padEnd(25)} → ${count} pagini\n`;
}
R += '\n';

// ─── SIMILARITATE CONTINUT ──────────────────────────────────
R += '┌──────────────────────────────────────────────────────────────┐\n';
R += '│  CONȚINUT DUPLICAT — SIMILARITATE ÎNTRE PAGINI               │\n';
R += '└──────────────────────────────────────────────────────────────┘\n';
R += `Perechi > 30% similaritate: ${highSim30.length > 0 ? `⚠️  ${highSim30.length}` : '✅ 0 — EXCELENT!'}\n`;
R += `Perechi > 20% similaritate: ${highSim20.length} (include structură CSS/HTML)\n\n`;
if (highSim30.length > 0) {
  R += `Top perechi > 30%:\n`;
  highSim30.slice(0, 15).forEach(p => {
    const color = p.sim > 40 ? '⛔' : '🟠';
    R += `  ${color} ${p.sim}%  ${p.a} ↔ ${p.b}\n`;
  });
}
R += '\n';

// ─── ANALIZA DETALIATA PE CATEGORII ─────────────────────────
R += '┌──────────────────────────────────────────────────────────────┐\n';
R += '│  ANALIZA DETALIATA — PAGINI INDEXATE (ordine scor, worst first)│\n';
R += '└──────────────────────────────────────────────────────────────┘\n';

const sortedIndexed = [...indexed].sort((a, b) => a.score - b.score);
for (const p of sortedIndexed) {
  const ic = icon(p.score);
  const bar = scoreBar(p.score);
  R += `\n${ic} [${String(p.score).padStart(3)}/100] ${bar}  ${p.url || '/'}\n`;
  R += `   Titlu (${p.titleLen}chr): ${p.title ? `"${p.title.slice(0,60)}${p.title.length>60?'...':''}"` : p.titleDynamic ? '[DINAMIC ✅]' : '⛔ LIPSĂ'}\n`;
  R += `   Desc  (${p.descLen}chr): ${p.desc ? `"${p.desc.slice(0,70)}..."` : p.descDynamic ? '[DINAMIC ✅]' : '⛔ LIPSĂ'}\n`;
  R += `   Canonical: ${p.canonical || '⚠️  LIPSĂ'}  |  Schema: ${p.hasSchema ? p.schemaTypes.slice(0,3).join(', ') || '✅' : '⚠️  LIPSĂ'}\n`;
  R += `   H1:${p.h1} H2:${p.h2} H3:${p.h3}  |  Cuvinte: ${p.wc}  |  Img: ${p.imgs}(${p.imgsNoAlt} fără alt)  |  LinkInt: ${p.internalLinks}\n`;
  if (p.issues.length > 0) {
    p.issues.forEach(i => {
      const pref = i.sev === 3 ? '     ⛔' : i.sev === 2 ? '     ⚠️ ' : '     ℹ️ ';
      R += `${pref} ${i.msg}\n`;
    });
  } else {
    R += `   ✅ Toate verificările OK!\n`;
  }
}

// ─── PAGINI NOINDEX ──────────────────────────────────────────
R += '\n┌──────────────────────────────────────────────────────────────┐\n';
R += '│  PAGINI NOINDEX — ASCUNSE DE GOOGLE (102 total)              │\n';
R += '└──────────────────────────────────────────────────────────────┘\n';
const noindexThin = noindexed.filter(p => p.wc < 200);
const noindexOk = noindexed.filter(p => p.wc >= 200);
R += `Pagini NOINDEX cu conținut OK (200+w):  ${noindexOk.length}\n`;
R += `Pagini NOINDEX cu conținut subțire:     ${noindexThin.length}\n`;
const noindexSorted = [...noindexed].sort((a,b) => a.wc - b.wc).slice(0, 20);
R += `\nPrimele 20 noindex (cele mai puțin conținut):\n`;
noindexSorted.forEach(p => {
  const flag = p.wc < 100 ? '⛔' : p.wc < 200 ? '🟠' : '🟡';
  R += `  ${flag} [${p.wc}w] ${p.url}\n`;
});

// ─── SUMARUL GENERAL ─────────────────────────────────────────
R += '\n╔══════════════════════════════════════════════════════════════╗\n';
R += '║  PRIORITĂȚI DE ACȚIUNE                                      ║\n';
R += '╚══════════════════════════════════════════════════════════════╝\n\n';

const actions = [];
if (noTitle.length > 0) actions.push({ p: 1, msg: `⛔ URGENT: Titlu lipsă pe ${noTitle.length} pagini: ${noTitle.map(p=>p.url).join(', ')}` });
if (noDesc.length > 0) actions.push({ p: 1, msg: `⛔ URGENT: Description lipsă pe ${noDesc.length} pagini: ${noDesc.map(p=>p.url).join(', ')}` });
if (thin50.length > 0) actions.push({ p: 1, msg: `⛔ URGENT: ${thin50.length} pagini cu sub 50 cuvinte — Google le penalizează dur` });
if (robotsDisallows.some(d => d === '/')) actions.push({ p: 1, msg: `⛔ URGENT: robots.txt blochează TOATE paginile!` });
if (highSim30.length > 0) actions.push({ p: 2, msg: `⚠️  IMPORTANT: ${highSim30.length} perechi de pagini cu >30% conținut similar` });
if (noCanon.length > 0) actions.push({ p: 2, msg: `⚠️  IMPORTANT: Canonical lipsă pe ${noCanon.length} pagini` });
if (noSchema.length > 0) actions.push({ p: 2, msg: `⚠️  IMPORTANT: Schema JSON-LD lipsă pe ${noSchema.length} pagini (pierd Rich Snippets)` });
if (thin200.length > 0) actions.push({ p: 2, msg: `⚠️  IMPORTANT: ${thin200.length} pagini cu conținut 50-200w — extinde` });
if (indexedNotInSitemap.length > 0) actions.push({ p: 2, msg: `⚠️  IMPORTANT: ${indexedNotInSitemap.length} pagini indexate lipsesc din sitemap` });
if (hasImgNoAlt.length > 0) actions.push({ p: 3, msg: `ℹ️  ${hasImgNoAlt.length} pagini cu imagini fără alt text` });
if (noH1.length > 0) actions.push({ p: 3, msg: `ℹ️  ${noH1.length} pagini fără H1` });
if (multiH1.length > 0) actions.push({ p: 3, msg: `ℹ️  ${multiH1.length} pagini cu multiple H1 (negativ SEO)` });

actions.sort((a,b) => a.p - b.p);
actions.forEach((a, i) => R += `${i+1}. ${a.msg}\n`);

if (actions.length === 0) R += '🎉 Nu există probleme! Site-ul este perfect optimizat pentru Google!\n';

// ─── CONCLUZIE ───────────────────────────────────────────────
R += '\n╔══════════════════════════════════════════════════════════════╗\n';
R += '║  CONCLUZIE FINALĂ                                           ║\n';
R += '╚══════════════════════════════════════════════════════════════╝\n\n';
R += `Total pagini scanate:              ${analyzed.length}\n`;
R += `Pagini indexate (văzute de Google): ${indexed.length}\n`;
R += `Scor mediu pagini indexate:        ${avgScore}/100\n`;
R += `Pagini perfect optimizate:         ${perfect.length}/${indexed.length}\n`;
R += `Perechi conținut duplicat >30%:   ${highSim30.length}\n`;
R += `Probleme critice totale:           ${actions.filter(a=>a.p===1).length}\n`;
R += `Probleme importante totale:        ${actions.filter(a=>a.p===2).length}\n\n`;

const critCount = actions.filter(a=>a.p===1).length;
if (critCount === 0 && actions.filter(a=>a.p===2).length <= 2) {
  R += `🏆 EXCELLENT: Site-ul este excelent optimizat pentru Google!\n`;
} else if (critCount === 0) {
  R += `✅ BUN: Fără probleme critice. Câteva avertismente de rezolvat.\n`;
} else if (critCount <= 2) {
  R += `🟠 MEDIU: ${critCount} problemă critică de rezolvat urgent.\n`;
} else {
  R += `⛔ SLAB: ${critCount} probleme critice — ranking afectat!\n`;
}

R += '\n╔══════════════════════════════════════════════════════════════╝\n';

// Save & print
const outFp = path.join(ROOT, 'scripts/google_full_test_result.txt');
fs.writeFileSync(outFp, R, 'utf-8');
process.stdout.write(R);
process.stderr.write(`\n✅ Salvat: scripts/google_full_test_result.txt\n`);
