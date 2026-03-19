// google_seo_audit.mjs — Audit complet cum vede Google site-ul
// Verifica: title, description, canonical, schema, robots, sitemap, continut, keyword density
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

// ─────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────
function extractMeta(raw, attr) {
  const m = raw.match(new RegExp(`${attr}="([^"]+)"`, 'i'));
  return m ? m[1] : null;
}

function extractText(raw) {
  let c = raw;
  c = c.replace(/^---[\s\S]*?---/m, '');
  c = c.replace(/<style[\s\S]*?<\/style>/gi, '');
  c = c.replace(/<script[\s\S]*?<\/script>/gi, '');
  c = c.replace(/<[^>]+>/g, ' ');
  c = c.replace(/\{[^{}]*\}/g, ' ');
  c = c.replace(/[^\wăâîșțĂÂÎȘȚ\s]/g, ' ');
  return c.replace(/\s+/g, ' ').trim();
}

function wordCount(text) {
  return text.split(/\s+/).filter(w => w.length >= 2).length;
}

function keywordDensity(text, keyword) {
  const words = text.toLowerCase().split(/\s+/);
  const kw = keyword.toLowerCase();
  const count = words.filter(w => w.includes(kw)).length;
  return ((count / words.length) * 100).toFixed(2);
}

function titleLength(title) {
  return title ? title.length : 0;
}

function descLength(desc) {
  return desc ? desc.length : 0;
}

// ─────────────────────────────────────────────────────────────────
// COLLECT PAGES
// ─────────────────────────────────────────────────────────────────
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

const allPages = collectPages(path.join(ROOT, 'src/pages'));
const TARGET_KW = 'animatori petreceri copii';

// ─────────────────────────────────────────────────────────────────
// ANALYZE EACH PAGE
// ─────────────────────────────────────────────────────────────────
const issues = { critical: [], warning: [], ok: [] };
const pageResults = [];

for (const { rel, fp } of allPages) {
  const raw = fs.readFileSync(fp, 'utf-8');
  const isNoindex = raw.includes('noindex');
  const text = extractText(raw);
  const words = wordCount(text);
  
  const title = extractMeta(raw, 'title');
  const desc = extractMeta(raw, 'description');
  const canonical = extractMeta(raw, 'canonical');
  const robots = extractMeta(raw, 'robots');
  const hasSchema = raw.includes('"@type"') || raw.includes('schema={schema}');
  const hasH1 = raw.includes('<h1') || raw.includes('<h1 ');
  const hasH2 = raw.includes('<h2') || raw.includes('<h2 ');
  const titleLen = titleLength(title);
  const descLen = descLength(desc);
  
  // Keyword density in title
  const kwInTitle = title ? title.toLowerCase().includes('animatori') || title.toLowerCase().includes('petreceri') : false;
  const kwInDesc = desc ? desc.toLowerCase().includes('animatori') || desc.toLowerCase().includes('petreceri') : false;
  
  // Score per page (0-100)
  let score = 0;
  const pageIssues = [];
  
  // Title
  if (!title) { pageIssues.push({ sev: 'CRITIC', msg: 'Lipsă titlu (<title>)' }); }
  else if (titleLen < 30) { pageIssues.push({ sev: 'AVERTISMENT', msg: `Titlu prea scurt (${titleLen} caractere, minim 40)` }); score += 10; }
  else if (titleLen > 70) { pageIssues.push({ sev: 'AVERTISMENT', msg: `Titlu prea lung (${titleLen} caractere, maxim 65)` }); score += 10; }
  else { score += 20; }
  
  // Description
  if (!desc) { pageIssues.push({ sev: 'CRITIC', msg: 'Lipsă meta description' }); }
  else if (descLen < 80) { pageIssues.push({ sev: 'AVERTISMENT', msg: `Descriere prea scurtă (${descLen} caractere, minim 120)` }); score += 8; }
  else if (descLen > 165) { pageIssues.push({ sev: 'AVERTISMENT', msg: `Descriere prea lungă (${descLen} caractere, maxim 160)` }); score += 8; }
  else { score += 20; }
  
  // Canonical
  if (!canonical) { pageIssues.push({ sev: 'AVERTISMENT', msg: 'Lipsă canonical URL' }); }
  else { score += 15; }
  
  // Schema
  if (!hasSchema) { pageIssues.push({ sev: 'AVERTISMENT', msg: 'Lipsă JSON-LD Schema markup' }); }
  else { score += 15; }
  
  // Content length
  if (words < 100) { pageIssues.push({ sev: 'CRITIC', msg: `Conținut extrem de subțire (${words} cuvinte)` }); }
  else if (words < 300) { pageIssues.push({ sev: 'AVERTISMENT', msg: `Conținut subțire (${words} cuvinte, recomandat 500+)` }); score += 10; }
  else if (words < 500) { score += 20; }
  else { score += 30; }
  
  // H1
  if (!hasH1 && !isNoindex) { pageIssues.push({ sev: 'AVERTISMENT', msg: 'Lipsă tag H1' }); }
  
  // Keyword in title (only for indexed pages)
  if (!isNoindex && title && !kwInTitle) {
    pageIssues.push({ sev: 'INFO', msg: 'Cuvântul cheie principal nu apare în titlu' });
  }
  
  const url = rel.replace('index.astro', '').replace('.astro', '').replace(/\\/g, '/');
  
  pageResults.push({
    rel, url, isNoindex, title, desc, canonical, hasSchema, hasH1, hasH2,
    titleLen, descLen, words, score: Math.min(score, 100), issues: pageIssues,
    kwInTitle, kwInDesc
  });
}

// Separate indexed vs noindex
const indexed = pageResults.filter(p => !p.isNoindex);
const noindexed = pageResults.filter(p => p.isNoindex);

// ─────────────────────────────────────────────────────────────────
// CHECK SITEMAP
// ─────────────────────────────────────────────────────────────────
const sitemapPath = path.join(ROOT, 'public/sitemap.xml');
const sitemapExists = fs.existsSync(sitemapPath);
let sitemapUrls = 0;
let sitemapMissingIndexed = [];

if (sitemapExists) {
  const sitemapContent = fs.readFileSync(sitemapPath, 'utf-8');
  const urls = sitemapContent.match(/<loc>[^<]+<\/loc>/g) || [];
  sitemapUrls = urls.length;
  
  // Check if indexed pages are in sitemap
  for (const p of indexed) {
    const slug = p.url.replace(/\/$/, '');
    const inSitemap = urls.some(u => u.includes(slug) || u.includes(slug.replace('/index', '')));
    if (!inSitemap && slug.length > 0) {
      sitemapMissingIndexed.push(p.url);
    }
  }
}

// Check robots.txt
const robotsPath = path.join(ROOT, 'public/robots.txt');
const robotsExists = fs.existsSync(robotsPath);
let robotsContent = '';
if (robotsExists) robotsContent = fs.readFileSync(robotsPath, 'utf-8');

// ─────────────────────────────────────────────────────────────────
// PRIORITY ISSUES ACROSS SITE
// ─────────────────────────────────────────────────────────────────
const noTitle = indexed.filter(p => !p.title);
const noDesc = indexed.filter(p => !p.desc);
const noCanonical = indexed.filter(p => !p.canonical);
const noSchema = indexed.filter(p => !p.hasSchema);
const thinContent = indexed.filter(p => p.words < 300);
const longTitle = indexed.filter(p => p.titleLen > 70);
const shortTitle = indexed.filter(p => p.title && p.titleLen < 30);
const longDesc = indexed.filter(p => p.descLen > 165);
const noH1 = indexed.filter(p => !p.hasH1);
const noKwTitle = indexed.filter(p => p.title && !p.kwInTitle);

// Average score
const avgScore = Math.round(indexed.reduce((a, p) => a + p.score, 0) / Math.max(indexed.length, 1));

// ─────────────────────────────────────────────────────────────────
// GENERATE REPORT
// ─────────────────────────────────────────────────────────────────
const RED = (n) => n > 0 ? `⛔ ${n}` : `✅ 0`;
const WARN = (n) => n > 0 ? `⚠️  ${n}` : `✅ 0`;
const OK = (n) => `✅ ${n}`;

let R = '';
R += '══════════════════════════════════════════════════════════════\n';
R += '   AUDIT SEO — CUM VEDE GOOGLE SUPERPARTY.RO\n';
R += `   ${new Date().toISOString().slice(0,16).replace('T',' ')} UTC\n`;
R += '══════════════════════════════════════════════════════════════\n\n';

R += `📊 SCOR GLOBAL: ${avgScore}/100  ${'█'.repeat(Math.round(avgScore/10))}${'░'.repeat(10-Math.round(avgScore/10))}\n\n`;

R += '──────────────────────────────────────────────────────────────\n';
R += ' INVENTAR PAGINI\n';
R += '──────────────────────────────────────────────────────────────\n';
R += `Total pagini .astro:        ${allPages.length}\n`;
R += `Pagini INDEXATE de Google:  ${indexed.length}\n`;
R += `Pagini NOINDEX (ascunse):   ${noindexed.length}\n`;
R += `Sitemap.xml:               ${sitemapExists ? `✅ găsit (${sitemapUrls} URLs)` : '⛔ LIPSĂ!'}\n`;
R += `Robots.txt:                ${robotsExists ? '✅ găsit' : '⛔ LIPSĂ!'}\n`;
if (robotsExists) {
  const hasDisallow = robotsContent.includes('Disallow: /');
  R += `Robots blochează ceva:     ${hasDisallow ? '⚠️  DA — verifică!' : '✅ Nu blochează paginile importante'}\n`;
}
R += '\n';

R += '──────────────────────────────────────────────────────────────\n';
R += ' PROBLEME CRITICE (⛔ = Google nu poate indexa corect)\n';
R += '──────────────────────────────────────────────────────────────\n';
R += `Pagini fără <title>:              ${RED(noTitle.length)}\n`;
R += `Pagini fără meta description:     ${RED(noDesc.length)}\n`;
R += `Pagini cu conținut <100 cuvinte:  ${RED(indexed.filter(p=>p.words<100).length)}\n`;
if (noTitle.length > 0) { R += `  → Fără titlu: ${noTitle.map(p=>p.url).join(', ')}\n`; }
if (noDesc.length > 0) { R += `  → Fără desc:  ${noDesc.map(p=>p.url).join(', ')}\n`; }
R += '\n';

R += '──────────────────────────────────────────────────────────────\n';
R += ' PROBLEME IMPORTANTE (⚠️  = afectează rankingul)\n';
R += '──────────────────────────────────────────────────────────────\n';
R += `Pagini fără canonical URL:         ${WARN(noCanonical.length)}\n`;
R += `Pagini fără Schema JSON-LD:        ${WARN(noSchema.length)}\n`;
R += `Conținut subțire (300-500w):       ${WARN(thinContent.length)}\n`;
R += `Titlu prea lung (>70 caractere):   ${WARN(longTitle.length)}\n`;
R += `Titlu prea scurt (<30 caractere):  ${WARN(shortTitle.length)}\n`;
R += `Descriere prea lungă (>165 chr):   ${WARN(longDesc.length)}\n`;
R += `Pagini fără tag H1:                ${WARN(noH1.length)}\n`;
R += `Titlu fără cuvânt cheie principal: ${WARN(noKwTitle.length)}\n`;
if (sitemapMissingIndexed.length > 0) {
  R += `Pagini indexate LIPSĂ din sitemap: ${WARN(sitemapMissingIndexed.length)}\n`;
  sitemapMissingIndexed.forEach(u => R += `  → ${u}\n`);
}
R += '\n';

R += '──────────────────────────────────────────────────────────────\n';
R += ' ANALIZA DETALIATA PE FIECARE PAGINA INDEXATA\n';
R += '──────────────────────────────────────────────────────────────\n';

// Sort by score ascending (worst first)
const sorted = [...indexed].sort((a,b) => a.score - b.score);

for (const p of sorted) {
  const scoreBar = '█'.repeat(Math.round(p.score/10)) + '░'.repeat(10-Math.round(p.score/10));
  const icon = p.score >= 85 ? '✅' : p.score >= 65 ? '🟡' : p.score >= 40 ? '🟠' : '⛔';
  R += `\n${icon} [${p.score}/100] ${scoreBar}  ${p.url || 'homepage'}\n`;
  R += `   Titlu:      ${p.title ? `"${p.title.slice(0,70)}${p.title.length>70?'...':''}" (${p.titleLen}chr)` : '⛔ LIPSĂ'}\n`;
  R += `   Descriere:  ${p.desc ? `"${p.desc.slice(0,80)}..." (${p.descLen}chr)` : '⛔ LIPSĂ'}\n`;
  R += `   Canonical:  ${p.canonical || '⚠️  LIPSĂ'}\n`;
  R += `   Schema:     ${p.hasSchema ? '✅ DA' : '⚠️  LIPSĂ'} | H1: ${p.hasH1?'✅':'⚠️  LIPSĂ'} | Cuvinte: ${p.words}\n`;
  if (p.issues.length > 0) {
    R += `   Probleme:\n`;
    p.issues.forEach(i => {
      const prefix = i.sev === 'CRITIC' ? '     ⛔' : i.sev === 'AVERTISMENT' ? '     ⚠️ ' : '     ℹ️ ';
      R += `${prefix} ${i.msg}\n`;
    });
  } else {
    R += `   ✅ Toate verificările OK!\n`;
  }
}

R += '\n══════════════════════════════════════════════════════════════\n';
R += ' PRIORITATI DE ACTIUNE\n';
R += '══════════════════════════════════════════════════════════════\n\n';

const actions = [];

if (noTitle.length > 0) actions.push({ prio: 1, action: `⛔ URGENT: Adaugă titlu pe ${noTitle.length} pagini: ${noTitle.map(p=>p.url).join(', ')}` });
if (noDesc.length > 0) actions.push({ prio: 1, action: `⛔ URGENT: Adaugă meta description pe ${noDesc.length} pagini: ${noDesc.map(p=>p.url).join(', ')}` });
if (indexed.filter(p=>p.words<100).length > 0) actions.push({ prio: 1, action: `⛔ URGENT: Rescrie ${indexed.filter(p=>p.words<100).length} pagini cu <100 cuvinte — Google le consideră "thin content"` });
if (!sitemapExists) actions.push({ prio: 1, action: '⛔ URGENT: Creează sitemap.xml — Google nu știe ce pagini există!' });
if (noCanonical.length > 0) actions.push({ prio: 2, action: `⚠️  IMPORTANT: Adaugă canonical pe ${noCanonical.length} pagini pentru a preveni duplicate` });
if (noSchema.length > 0) actions.push({ prio: 2, action: `⚠️  IMPORTANT: Adaugă Schema JSON-LD pe ${noSchema.length} pagini pentru Rich Snippets în Google` });
if (thinContent.length > 0) actions.push({ prio: 2, action: `⚠️  IMPORTANT: Extinde conținutul pe ${thinContent.length} pagini cu sub 300 cuvinte` });
if (longTitle.length > 0) actions.push({ prio: 3, action: `ℹ️  Scurtează titlul pe ${longTitle.length} pagini (Google truncheaza la ~65 caractere)` });
if (noKwTitle.length > 0) actions.push({ prio: 3, action: `ℹ️  Adaugă cuvântul cheie "animatori petreceri copii" în titlul la ${noKwTitle.length} pagini` });
if (noH1.length > 0) actions.push({ prio: 3, action: `ℹ️  Adaugă tag H1 pe ${noH1.length} pagini indexate` });

actions.sort((a,b) => a.prio - b.prio);
actions.forEach((a,i) => R += `${i+1}. ${a.action}\n`);

if (actions.length === 0) {
  R += '🎉 Nicio problemă majoră identificată! Site-ul este bine optimizat pentru Google.\n';
}

R += '\n══════════════════════════════════════════════════════════════\n';
R += ' CONCLUZIE FINALA\n';
R += '══════════════════════════════════════════════════════════════\n\n';

const criticalCount = noTitle.length + noDesc.length + indexed.filter(p=>p.words<100).length + (sitemapExists ? 0 : 1);
const warningCount = noCanonical.length + noSchema.length + thinContent.length + longTitle.length + noH1.length;

R += `Scor mediu:     ${avgScore}/100\n`;
R += `Probleme CRITICE (Google nu poate indexa bine): ${criticalCount}\n`;
R += `Probleme IMPORTANTE (afectează rankingul):       ${warningCount}\n`;
R += `Pagini perfect optimizate:                       ${indexed.filter(p=>p.issues.length===0).length}/${indexed.length}\n\n`;

if (criticalCount === 0 && warningCount <= 3) {
  R += '✅ EXCELLENT: Site-ul este bine pregătit pentru Google. Continuați cu creearea de conținut nou.\n';
} else if (criticalCount === 0 && warningCount <= 8) {
  R += '🟡 BUN: Fără probleme critice, câteva avertismente de rezolvat pentru ranking maxim.\n';
} else if (criticalCount <= 2) {
  R += '🟠 MEDIU: Câteva probleme critice de rezolvat urgent, altfel Google indexează incorect.\n';
} else {
  R += '⛔ SLAB: Probleme critice multiple — ranking slab garantat până la rezolvare!\n';
}

R += '\n══════════════════════════════════════════════════════════════\n';

// Save to file
const outPath = path.join(ROOT, 'scripts/google_seo_audit_result.txt');
fs.writeFileSync(outPath, R, 'utf-8');
console.log(R);
console.log(`\n✅ Salvat: scripts/google_seo_audit_result.txt`);
