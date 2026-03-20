// quality_unique_audit.mjs
// Masoara: (1) continut unic per pagina vs template comun, (2) relevanta pt "animatori petreceri copii"
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

// Extrage DOAR textul vizibil (fara HTML, fara atribute, fara CSS)
function extractText(raw) {
  return raw
    .replace(/^---[\s\S]*?---/m, '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/style="[^"]*"/g, '')
    .replace(/class="[^"]*"/g, '')
    .replace(/href="[^"]*"/g, '')
    .replace(/src="[^"]*"/g, '')
    .replace(/itemtype="[^"]*"/g, '')
    .replace(/itemprop="[^"]*"/g, '')
    .replace(/itemscope/g, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/https?:\/\/[^\s]*/g, '')
    .replace(/[^a-zA-Z\u00C0-\u024F\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}

// Cuvinte relevante pentru "animatori petreceri copii"
const RELEVANT_WORDS = new Set([
  'animator','animatori','animatoare','petrecere','petreceri','copii','copil','copilului','copiilor',
  'personaj','personaje','costume','costum','elsa','spiderman','batman','sonic','bluey','moana',
  'pikachu','stitch','frozen','paw','patrol','minnie','mickey','superman','ironman','encanto',
  'face','painting','baloane','balon','sapun','modelare','jocuri','joc','interactiv','interactive',
  'aniversare','aniversara','aniversari','ziua','nastere','botez','ursitoare','mos','craciun',
  'rezervare','rezerva','pachet','pachete','ron','pret','preturi','tarif','contract','garantie',
  'profesionist','profesionisti','calitate','premium','licentiata','licentiate','licenta',
  'bucuresti','ilfov','sector','cartier','localitate','zona','deplasare','km','distanta',
  'program','ore','durata','echipament','materiale','diplome','trofee','premii','diplome',
]);

// Cuvinte IRELEVANTE / template generic
const TEMPLATE_WORDS = new Set([
  'acasa','contact','despre','servicii','galerie','recenzii','sitemap','gdpr','cookies',
  'privacy','termeni','conditii','utilizare','newsletter','abonare','social','media',
  'copyright','toate','drepturile','rezervate','design','dezvoltat','powered',
]);

function analyzeContent(text) {
  const words = text.split(/\s+/).filter(w => w.length >= 4);
  if (words.length === 0) return { total: 0, relevant: 0, template: 0, relevPct: 0, wordCount: 0 };
  
  let relevant = 0, template = 0;
  for (const w of words) {
    if (RELEVANT_WORDS.has(w)) relevant++;
    if (TEMPLATE_WORDS.has(w)) template++;
  }
  
  return {
    wordCount: words.length,
    relevant,
    template,
    relevPct: Math.round(relevant / words.length * 100),
  };
}

// ── Calculeaza continut UNIC vs COMUN intre toate paginile ──────────
// Genereaza vocabularul comun (cuvinte care apar pe >80% din pagini)
const all = collectAll(path.join(ROOT, 'src/pages'));
const indexed = all.filter(p => !fs.readFileSync(p.fp, 'utf-8').includes('noindex'));

// Extrage texte
const pageTexts = indexed.map(p => {
  const raw = fs.readFileSync(p.fp, 'utf-8');
  const text = extractText(raw);
  return { rel: p.rel, text, words: text.split(/\s+/).filter(w => w.length >= 4) };
});

// Frecventa cuvintelor pe site (pentru a detecta cuvintele comune/template)
const wordFreq = {};
for (const p of pageTexts) {
  const uniqueWords = new Set(p.words);
  for (const w of uniqueWords) {
    wordFreq[w] = (wordFreq[w] || 0) + 1;
  }
}

const totalPages = pageTexts.length;
// Cuvinte care apar pe mai mult de 60% din pagini = template/boilerplate
const COMMON_THRESHOLD = 0.6;
const commonWords = new Set(
  Object.entries(wordFreq)
    .filter(([, freq]) => freq / totalPages >= COMMON_THRESHOLD)
    .map(([w]) => w)
);

process.stderr.write(`Cuvinte template comune (>60% pagini): ${commonWords.size}\n`);

// Analizeaza fiecare pagina
const results = [];
for (const p of pageTexts) {
  const allW = p.words;
  const uniqueW = allW.filter(w => !commonWords.has(w));
  const relevantW = allW.filter(w => RELEVANT_WORDS.has(w));
  const relevantUniqueW = uniqueW.filter(w => RELEVANT_WORDS.has(w));
  
  const uniquePct = allW.length > 0 ? Math.round(uniqueW.length / allW.length * 100) : 0;
  const relevPct = allW.length > 0 ? Math.round(relevantW.length / allW.length * 100) : 0;
  const qualityScore = Math.round((uniquePct * 0.5) + (relevPct * 2));
  
  results.push({
    rel: p.rel,
    totalW: allW.length,
    uniqueW: uniqueW.length,
    uniquePct,
    relevantW: relevantW.length,
    relevPct,
    qualityScore: Math.min(qualityScore, 100),
  });
}

results.sort((a, b) => a.qualityScore - b.qualityScore);

// ── RAPORT ──────────────────────────────────────────────────────────
let R = '';
R += '╔══════════════════════════════════════════════════════════════════╗\n';
R += '║  AUDIT CALITATE CONTINUT — SUPERPARTY.RO                        ║\n';
R += '║  Masurare: % continut UNIC + % relevanta "animatori copii"       ║\n';
R += '╚══════════════════════════════════════════════════════════════════╝\n\n';

// Globale
const avgUnique = Math.round(results.reduce((a, r) => a + r.uniquePct, 0) / results.length);
const avgRelev = Math.round(results.reduce((a, r) => a + r.relevPct, 0) / results.length);
const avgQuality = Math.round(results.reduce((a, r) => a + r.qualityScore, 0) / results.length);
const highQuality = results.filter(r => r.qualityScore >= 60).length;
const midQuality = results.filter(r => r.qualityScore >= 30 && r.qualityScore < 60).length;
const lowQuality = results.filter(r => r.qualityScore < 30).length;

R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  STATISTICI GLOBALE                                              │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
R += `Total pagini analizate:          ${results.length}\n`;
R += `Cuvinte template comun (>60%):   ${commonWords.size} cuvinte ignorate\n`;
R += `\n`;
R += `Medie % continut UNIC:           ${avgUnique}%\n`;
R += `Medie % relevanta tematica:      ${avgRelev}%\n`;
R += `Scor calitate mediu:             ${avgQuality}/100\n`;
R += `\n`;
R += `✅ Calitate BUNA (60-100):       ${highQuality} pagini (${Math.round(highQuality/results.length*100)}%)\n`;
R += `🟡 Calitate MEDIE (30-59):       ${midQuality} pagini (${Math.round(midQuality/results.length*100)}%)\n`;
R += `⛔ Calitate SLABA (0-29):        ${lowQuality} pagini (${Math.round(lowQuality/results.length*100)}%)\n\n`;

// Top 20 pagini slabe
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  PAGINI CU CEA MAI SLABA CALITATE (cel mai putin continut unic)  │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
R += `${'Pagina'.padEnd(50)} ${'Unic%'.padEnd(7)} ${'Relev%'.padEnd(8)} ${'Scor'.padEnd(6)} Cuvinte\n`;
R += '-'.repeat(80) + '\n';
for (const r of results.slice(0, 25)) {
  const slug = r.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/').substring(0,48);
  const icon = r.qualityScore >= 60 ? '✅' : r.qualityScore >= 30 ? '🟡' : '⛔';
  R += `${icon} ${slug.padEnd(48)} ${String(r.uniquePct+'%').padEnd(7)} ${String(r.relevPct+'%').padEnd(8)} ${String(r.qualityScore).padEnd(6)} ${r.totalW}w\n`;
}
R += '\n';

// Top 20 pagini bune
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  PAGINI CU CEA MAI BUNA CALITATE                                │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
R += `${'Pagina'.padEnd(50)} ${'Unic%'.padEnd(7)} ${'Relev%'.padEnd(8)} ${'Scor'.padEnd(6)} Cuvinte\n`;
R += '-'.repeat(80) + '\n';
const best = [...results].sort((a, b) => b.qualityScore - a.qualityScore).slice(0, 20);
for (const r of best) {
  const slug = r.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/').substring(0,48);
  const icon = r.qualityScore >= 60 ? '✅' : r.qualityScore >= 30 ? '🟡' : '⛔';
  R += `${icon} ${slug.padEnd(48)} ${String(r.uniquePct+'%').padEnd(7)} ${String(r.relevPct+'%').padEnd(8)} ${String(r.qualityScore).padEnd(6)} ${r.totalW}w\n`;
}
R += '\n';

// Cuvintele template comune detectate (primele 30)
R += '┌──────────────────────────────────────────────────────────────────┐\n';
R += '│  CUVINTE TEMPLATE COMUN DETECTED (apar pe >60% din pagini)      │\n';
R += '└──────────────────────────────────────────────────────────────────┘\n';
const topCommon = Object.entries(wordFreq)
  .filter(([w]) => commonWords.has(w))
  .sort((a,b) => b[1]-a[1])
  .slice(0,40);
R += topCommon.map(([w,f]) => `${w}(${f})`).join(', ') + '\n\n';

// Salveaza
const outPath = path.join(ROOT, 'scripts/quality_unique_report.txt');
fs.writeFileSync(outPath, R, 'utf-8');
process.stdout.write(R);
process.stderr.write(`\nSalvat: scripts/quality_unique_report.txt\n`);
