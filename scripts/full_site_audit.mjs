// full_site_audit.mjs
// Audit complet al site-ului Superparty — scanează TOATE fișierele
// Găsește erori: meta lipsă, duplicate, broken imports, noindex, conținut scurt, etc.

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const errors = [];
const warnings = [];
const info = [];

function addError(cat, file, msg) { errors.push({ cat, file: file.replace(ROOT, ''), msg }); }
function addWarn(cat, file, msg) { warnings.push({ cat, file: file.replace(ROOT, ''), msg }); }
function addInfo(cat, msg) { info.push({ cat, msg }); }

// ─── 1. SCAN ASTRO PAGES ────────────────────────────────────────────────────
function scanAstroPages() {
  const pagesDir = path.join(ROOT, 'src/pages');
  const astroFiles = [];

  function walkDir(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walkDir(full);
      else if (entry.name.endsWith('.astro')) astroFiles.push(full);
    }
  }
  walkDir(pagesDir);

  let pagesWithoutTitle = 0, pagesWithoutDesc = 0, pagesWithoutH1 = 0;

  for (const file of astroFiles) {
    const content = fs.readFileSync(file, 'utf-8');
    const rel = file.replace(ROOT, '');

    // Check for title
    if (!content.match(/title[=:{]/i) && !content.match(/title\s*=/)) {
      pagesWithoutTitle++;
      addWarn('PAGE_META', file, 'Lipsă title tag');
    }

    // Check for description
    if (!content.match(/description[=:{]/i)) {
      pagesWithoutDesc++;
      addWarn('PAGE_META', file, 'Lipsă description');
    }

    // Check for broken imports (component referenced but not imported)
    const imports = [...content.matchAll(/import\s+(\w+)\s+from\s+['"](.+?)['"]/g)].map(m => ({
      name: m[1], path: m[2]
    }));

    for (const imp of imports) {
      // Resolve relative import
      if (imp.path.startsWith('.')) {
        const resolved = path.resolve(path.dirname(file), imp.path);
        const candidates = [resolved, resolved + '.astro', resolved + '.ts', resolved + '.js', resolved + '.tsx'];
        const exists = candidates.some(c => fs.existsSync(c));
        if (!exists) {
          addError('BROKEN_IMPORT', file, `Import lipsă: ${imp.path} (${imp.name})`);
        }
      }
    }

    // Check for <h1>
    if (!content.includes('<h1') && !content.includes('{entry.data.title}') && !content.includes('h1>')) {
      pagesWithoutH1++;
      addWarn('SEO_H1', file, 'Lipsă <h1>');
    }
  }

  addInfo('PAGES', `Total pagini Astro: ${astroFiles.length}`);
  addInfo('PAGES', `Fără title: ${pagesWithoutTitle}`);
  addInfo('PAGES', `Fără description: ${pagesWithoutDesc}`);
  addInfo('PAGES', `Fără <h1>: ${pagesWithoutH1}`);
  return astroFiles.length;
}

// ─── 2. SCAN SEO ARTICLES ───────────────────────────────────────────────────
function scanSeoArticles() {
  const dir = path.join(ROOT, 'src/content/seo-articles');
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.mdx'));

  let noTitle = 0, noDesc = 0, tooShort = 0, noindex = 0, indexable = 0;
  const shortThreshold = 300; // chars body min

  // Detectă duplicate (primele 80 chars identice)
  const bodyStarts = {};
  for (const f of files) {
    const content = fs.readFileSync(path.join(dir, f), 'utf-8');
    const title = content.match(/title:\s*['"](.+?)['"]/)?.[1] || '';
    const desc = content.match(/description:\s*['"](.+?)['"]/)?.[1] || '';
    const hasNoindex = content.includes('noindex');
    const body = content.replace(/---[\s\S]*?---/, '').trim();

    if (!title) { noTitle++; addError('ARTICLE_META', path.join(dir, f), 'Lipsă title'); }
    if (!desc) { noDesc++; addWarn('ARTICLE_META', path.join(dir, f), 'Lipsă description'); }
    if (body.length < shortThreshold) { tooShort++; addWarn('ARTICLE_CONTENT', path.join(dir, f), `Conținut prea scurt: ${body.length} chars`); }
    if (hasNoindex) noindex++; else indexable++;

    const key = body.slice(0, 80).replace(/\s+/g, ' ');
    if (!bodyStarts[key]) bodyStarts[key] = [];
    bodyStarts[key].push(f);
  }

  const dupGroups = Object.values(bodyStarts).filter(g => g.length > 1);
  const dupWithoutNoindex = dupGroups.filter(g => {
    return g.some(f => {
      const c = fs.readFileSync(path.join(dir, f), 'utf-8');
      return !c.includes('noindex');
    });
  });

  addInfo('ARTICLES', `Total articole: ${files.length}`);
  addInfo('ARTICLES', `Indexabile (unice): ${indexable}`);
  addInfo('ARTICLES', `Cu noindex: ${noindex}`);
  addInfo('ARTICLES', `Grupuri duplicate NEPROTEJATE (fără noindex): ${dupWithoutNoindex.length}`);
  addInfo('ARTICLES', `Fără title: ${noTitle}`);
  addInfo('ARTICLES', `Conținut < ${shortThreshold} chars: ${tooShort}`);

  if (dupWithoutNoindex.length > 0) {
    dupWithoutNoindex.slice(0, 5).forEach(g => {
      addError('DUPLICATE_UNPROTECTED', path.join(dir, g[0]), `${g.length} articole duplicate fără noindex`);
    });
  }

  return files.length;
}

// ─── 3. SCAN COMPONENTS ─────────────────────────────────────────────────────
function scanComponents() {
  const dir = path.join(ROOT, 'src/components');
  const files = fs.readdirSync(dir, { recursive: true })
    .filter(f => typeof f === 'string' && (f.endsWith('.astro') || f.endsWith('.tsx')));

  let emptyComponents = 0;
  for (const f of files) {
    const full = path.join(dir, f);
    const stat = fs.statSync(full);
    if (stat.size < 50) {
      emptyComponents++;
      addWarn('COMPONENT', full, `Componentă goală/minimală: ${stat.size} bytes`);
    }
  }
  addInfo('COMPONENTS', `Total componente: ${files.length}`);
  addInfo('COMPONENTS', `Componente goale/minimale: ${emptyComponents}`);
}

// ─── 4. SCAN CONTENT SCHEMA ─────────────────────────────────────────────────
function scanContentSchema() {
  const configPath = path.join(ROOT, 'src/content/config.ts');
  const content = fs.readFileSync(configPath, 'utf-8');

  const hasRobots = content.includes('robots');
  const hasIndexStatus = content.includes('indexStatus');
  const hasCanonical = content.includes('canonical');

  if (!hasRobots) addError('SCHEMA', configPath, 'Câmpul `robots` lipsă din schema Zod');
  if (!hasIndexStatus) addError('SCHEMA', configPath, 'Câmpul `indexStatus` lipsă din schema Zod');
  if (!hasCanonical) addError('SCHEMA', configPath, 'Câmpul `canonical` lipsă din schema Zod');

  addInfo('SCHEMA', `robots în schema: ${hasRobots ? 'DA' : 'NU'}`);
  addInfo('SCHEMA', `indexStatus în schema: ${hasIndexStatus ? 'DA' : 'NU'}`);
  addInfo('SCHEMA', `canonical în schema: ${hasCanonical ? 'DA' : 'NU'}`);
}

// ─── 5. SCAN SCRIPTS ────────────────────────────────────────────────────────
function scanScripts() {
  const dir = path.join(ROOT, 'scripts');
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.js') || f.endsWith('.mjs') || f.endsWith('.py'));
  addInfo('SCRIPTS', `Total scripts: ${files.length}`);
}

// ─── 6. SCAN LOCAL PAGES FOR FLAGSHIPLINK ──────────────────────────────────
function scanLocalPagesLinking() {
  const localSlugs = [
    'sector-1','sector-2','sector-3','sector-4','sector-5','sector-6',
    'bucuresti','ilfov','voluntari','otopeni','pantelimon','bragadiru','chiajna','popesti-leordeni'
  ];
  let linked = 0, missing = 0;
  for (const slug of localSlugs) {
    const f = path.join(ROOT, `src/pages/animatori-copii-${slug}/index.astro`);
    if (!fs.existsSync(f)) {
      missing++;
      addError('INTERNAL_LINK', f, `Pagina locală lipsă: animatori-copii-${slug}`);
      continue;
    }
    const content = fs.readFileSync(f, 'utf-8');
    if (!content.includes('FlagshipLink')) {
      addError('INTERNAL_LINK', f, 'FlagshipLink LIPSĂ — nu trimite link juice spre flagship!');
    } else {
      linked++;
    }
  }
  addInfo('INTERNAL_LINKS', `Pagini locale cu FlagshipLink: ${linked}/${localSlugs.length}`);
  if (missing > 0) addInfo('INTERNAL_LINKS', `Pagini locale lipsă: ${missing}`);
}

// ─── 7. SCAN FLAGSHIP PAGE ──────────────────────────────────────────────────
function scanFlagshipPage() {
  const f = path.join(ROOT, 'src/pages/animatori-petreceri-copii/index.astro');
  if (!fs.existsSync(f)) {
    addError('FLAGSHIP', f, 'Pagina flagship /animatori-petreceri-copii LIPSĂ!');
    return;
  }
  const content = fs.readFileSync(f, 'utf-8');
  const body = content.replace(/---[\s\S]*?---/, '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  const wordCount = body.split(' ').filter(w => w.length > 2).length;
  const faqCount = (content.match(/<details/g) || []).length;
  const internalLinks = (content.match(/href="\/animatori-copii-/g) || []).length;

  if (wordCount < 800) addError('FLAGSHIP', f, `Flagship prea scurtă: ${wordCount} cuvinte (min 800)`);
  if (faqCount < 3) addWarn('FLAGSHIP', f, `FAQ insuficient: ${faqCount} întrebări (recomandat 5+)`);
  if (internalLinks < 5) addWarn('FLAGSHIP', f, `Linkuri interne insuficiente: ${internalLinks} (recomandat 10+)`);

  addInfo('FLAGSHIP', `Cuvinte flagship: ${wordCount}`);
  addInfo('FLAGSHIP', `FAQ entries: ${faqCount}`);
  addInfo('FLAGSHIP', `Linkuri interne spre locale: ${internalLinks}`);
}

// ─── 8. SCAN vercel.json / astro.config ─────────────────────────────────────
function scanConfig() {
  const vercelJson = path.join(ROOT, 'vercel.json');
  if (fs.existsSync(vercelJson)) {
    try {
      const data = JSON.parse(fs.readFileSync(vercelJson, 'utf-8'));
      addInfo('CONFIG', `vercel.json: OK (${Object.keys(data).join(', ')})`);
    } catch (e) {
      addError('CONFIG', vercelJson, 'vercel.json invalid JSON!');
    }
  } else {
    addWarn('CONFIG', vercelJson, 'vercel.json lipsă');
  }

  const astroConfig = path.join(ROOT, 'astro.config.mjs');
  if (fs.existsSync(astroConfig)) {
    const content = fs.readFileSync(astroConfig, 'utf-8');
    if (!content.includes('sitemap')) addWarn('CONFIG', astroConfig, 'Sitemap integration lipsă din astro.config');
    addInfo('CONFIG', `astro.config.mjs: OK`);
  }
}

// ─── RUN ALL ─────────────────────────────────────────────────────────────────
console.log('🔍 AUDIT COMPLET SUPERPARTY.RO\n');
console.log('Scanez... (poate dura 20-30 secunde)\n');

const totalPages = scanAstroPages();
const totalArticles = scanSeoArticles();
scanComponents();
scanContentSchema();
scanScripts();
scanLocalPagesLinking();
scanFlagshipPage();
scanConfig();

// ─── OUTPUT ──────────────────────────────────────────────────────────────────
console.log('╔══════════════════════════════════════════════════════════════════╗');
console.log('║                    REZULTAT AUDIT COMPLET                       ║');
console.log('╚══════════════════════════════════════════════════════════════════╝\n');

console.log(`Pagini Astro scanate:   ${totalPages}`);
console.log(`Articole MDX scanate:   ${totalArticles}`);
console.log(`ERORI CRITICE:          ${errors.length}`);
console.log(`AVERTISMENTE:           ${warnings.length}`);
console.log('');

// ERORI
if (errors.length > 0) {
  console.log('════ 🔴 ERORI CRITICE ════');
  const byCategory = {};
  errors.forEach(e => {
    if (!byCategory[e.cat]) byCategory[e.cat] = [];
    byCategory[e.cat].push(e);
  });
  Object.entries(byCategory).forEach(([cat, errs]) => {
    console.log(`\n[${cat}] — ${errs.length} erori:`);
    errs.slice(0, 8).forEach(e => console.log(`  ❌ ${path.basename(e.file)}: ${e.msg}`));
    if (errs.length > 8) console.log(`  ... +${errs.length - 8} altele`);
  });
}

// WARNINGS
if (warnings.length > 0) {
  console.log('\n════ 🟡 AVERTISMENTE ════');
  const byCategory = {};
  warnings.forEach(w => {
    if (!byCategory[w.cat]) byCategory[w.cat] = [];
    byCategory[w.cat].push(w);
  });
  Object.entries(byCategory).forEach(([cat, warns]) => {
    console.log(`\n[${cat}] — ${warns.length} warnings:`);
    warns.slice(0, 5).forEach(w => console.log(`  ⚠️  ${path.basename(w.file)}: ${w.msg}`));
    if (warns.length > 5) console.log(`  ... +${warns.length - 5} altele`);
  });
}

// INFO
console.log('\n════ ℹ️  INFO GENERAL ════');
info.forEach(i => console.log(`  [${i.cat}] ${i.msg}`));

// Salvează raportul
const reportData = { timestamp: new Date().toISOString(), errors, warnings, info };
fs.writeFileSync('scripts/audit_report.json', JSON.stringify(reportData, null, 2));
console.log(`\n✅ Raport salvat în: scripts/audit_report.json`);
