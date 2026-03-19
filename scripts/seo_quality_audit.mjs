// seo_quality_audit.mjs — Audit complet calitate SEO pagini cartiere
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { cartiereData } from './cartiere_data.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages/petreceri');

// ─── Utilitare ───────────────────────────────────────────────────────────────
function extractText(fp) {
  let c = fs.readFileSync(fp, 'utf-8');
  // Scoate frontmatter
  c = c.replace(/^---[\s\S]*?---/m, '');
  // Scoate style blocks
  c = c.replace(/<style[\s\S]*?<\/style>/gi, ' ');
  // Scoate script blocks  
  c = c.replace(/<script[\s\S]*?<\/script>/gi, ' ');
  // Scoate expresii Astro/jsx
  c = c.replace(/\{[^{}]*\}/g, ' ');
  // Scoate taguri HTML
  c = c.replace(/<[^>]+>/g, ' ');
  // Normalizeaza
  return c.replace(/\s+/g, ' ').trim().toLowerCase();
}

function countWords(text) {
  return text.split(/\s+/).filter(w => w.length > 3).length;
}

function countKw(text, kw) {
  const words = text.split(/\s+/);
  const kwArr = kw.toLowerCase().split(/\s+/);
  let count = 0;
  for (let i = 0; i <= words.length - kwArr.length; i++) {
    if (kwArr.every((w, j) => words[i+j].includes(w))) count++;
  }
  return count;
}

function jaccard(textA, textB) {
  const setA = new Set(textA.split(/\s+/).filter(w => w.length > 5));
  const setB = new Set(textB.split(/\s+/).filter(w => w.length > 5));
  const inter = [...setA].filter(x => setB.has(x)).length;
  const union = new Set([...setA, ...setB]).size;
  return union ? inter / union : 0;
}

// Cuvinte cheie petreceri copii (TOPIC RELEVANCE)
const PARTY_KEYWORDS = [
  'petreceri copii', 'petrecere copii', 'animator', 'animatori',
  'personaj', 'personaje', 'costumat', 'costum', 'face painting',
  'baloane', 'rezerva', '490 ron', '840 ron', '1290 ron',
  'mini disco', 'jocuri', 'tor', 'sala', 'parc', 'copii'
];

// Keywords NON-PARTY (penalizare daca apar prea des)
const NON_PARTY_KEYWORDS = [
  'industrie', 'fabrica', 'muncitori', 'uzina', 'socialism',
  'comunist', 'architectural', 'monument', 'muzeu'
];

// SEO checks
function checkSEO(fp, rawContent) {
  const issues = [];
  const ok = [];

  // Schema
  if (rawContent.includes('"@type":"Service"')) ok.push('Schema Service ✓');
  else issues.push('Lipsa schema Service');

  if (rawContent.includes('"@type":"FAQPage"')) ok.push('Schema FAQPage ✓');
  else issues.push('Lipsa schema FAQPage');

  if (rawContent.includes('"@type":"BreadcrumbList"')) ok.push('Schema Breadcrumb ✓');
  else issues.push('Lipsa Breadcrumb');

  if (rawContent.includes('"@type":"LocalBusiness"')) ok.push('Schema LocalBusiness ✓');
  else issues.push('Lipsa LocalBusiness');

  // Preturi corecte
  if (rawContent.includes('490') && rawContent.includes('840') && rawContent.includes('1290')) ok.push('Preturi corecte (490/840/1290) ✓');
  else issues.push('Preturi INCORECTE sau lipsa');

  // H1
  const h1count = (rawContent.match(/<h1/gi) || []).length;
  if (h1count === 1) ok.push('H1 unic ✓');
  else if (h1count === 0) issues.push('Lipsa H1');
  else issues.push(`Prea multe H1 (${h1count})`);

  // Canonical  
  if (rawContent.includes('canonical=')) ok.push('Canonical ✓');
  else issues.push('Lipsa canonical');

  // CTA
  if (rawContent.includes('0722 744 377') || rawContent.includes('wa.me/40722744377')) ok.push('CTA telefon/WA ✓');
  else issues.push('Lipsa CTA telefon');

  // Title tag  
  if (rawContent.includes('title=') && rawContent.includes('490 RON')) ok.push('Title cu pret ✓');
  else issues.push('Title fara pret sau lipsa');

  // FAQ items
  const faqCount = (rawContent.match(/faq-item/gi) || []).length;
  if (faqCount >= 5) ok.push(`FAQ ${faqCount} intrebari ✓`);
  else issues.push(`FAQ prea putine (${faqCount} din 5+)`);

  // Internal links
  if (rawContent.includes('animatori-petreceri-copii')) ok.push('Link intern flagship ✓');
  else issues.push('Lipsa link intern flagship');

  return { ok, issues };
}

// ─── AUDIT ───────────────────────────────────────────────────────────────────
const results = [];

for (const c of cartiereData) {
  const fp = path.join(pagesDir, `${c.slug}.astro`);
  if (!fs.existsSync(fp)) { 
    results.push({ slug: c.slug, error: 'FISIER LIPSA' }); 
    continue; 
  }
  
  const rawContent = fs.readFileSync(fp, 'utf-8');
  const text = extractText(fp);
  const wc = countWords(text);
  
  // Keyword counts party
  const partyHits = PARTY_KEYWORDS.reduce((acc, kw) => acc + countKw(text, kw), 0);
  const nonPartyHits = NON_PARTY_KEYWORDS.reduce((acc, kw) => acc + countKw(text, kw), 0);
  
  // Specifice per pagina
  const slugKw = countKw(text, c.name.toLowerCase().replace(/[()]/g, ''));
  const animatoriPetreceri = countKw(text, 'animatori petreceri copii');
  const petreceriCopii = countKw(text, 'petreceri copii');
  const animator = countKw(text, 'animator');
  
  // SEO checks
  const { ok: seoOk, issues: seoIssues } = checkSEO(fp, rawContent);
  
  // Calitate continut party: raport cuvinte-cheie / total cuvinte
  const partyRelevanceScore = wc > 0 ? Math.round((partyHits / wc) * 100) : 0;
  
  // Scor general 0-100
  const seoScore = Math.round((seoOk.length / (seoOk.length + seoIssues.length)) * 100);
  
  // Grade
  const wcGrade = wc >= 1500 ? 'A' : wc >= 1000 ? 'B' : wc >= 600 ? 'C' : 'D';
  const kwGrade = slugKw >= 10 ? 'A' : slugKw >= 5 ? 'B' : slugKw >= 2 ? 'C' : 'D';
  const seoGrade = seoScore >= 90 ? 'A' : seoScore >= 70 ? 'B' : seoScore >= 50 ? 'C' : 'D';
  const partGrade = partyRelevanceScore >= 5 ? 'A' : partyRelevanceScore >= 3 ? 'B' : partyRelevanceScore >= 1 ? 'C' : 'D';
  
  const overallGrade = (() => {
    const grades = [wcGrade, kwGrade, seoGrade];
    const dCount = grades.filter(g => g === 'D').length;
    const cCount = grades.filter(g => g === 'C').length;
    if (dCount >= 2) return 'D';
    if (dCount >= 1 || cCount >= 2) return 'C';
    if (grades.every(g => g === 'A')) return 'A';
    return 'B';
  })();
  
  results.push({
    slug: c.slug,
    name: c.name,
    wc, wcGrade,
    slugKw,
    animatoriPetreceri,
    petreceriCopii,
    animator,
    partyHits,
    partyRelevanceScore,
    nonPartyHits,
    seoScore,
    seoOk,
    seoIssues,
    kwGrade, seoGrade, partGrade,
    overallGrade
  });
}

// ─── OUTPUT ───────────────────────────────────────────────────────────────────
console.log('\n' + '═'.repeat(70));
console.log('  AUDIT SEO CALITATE — PAGINI CARTIERE BUCURESTI');
console.log('═'.repeat(70));

console.log('\n📊 SECTIUNEA 1: CUVINTE SI RELEVANTA KEYWORDS PARTY\n');
console.log('  ' + 'Pagina'.padEnd(22) + 'Cuvinte'.padEnd(10) + 'Nota'.padEnd(6) + 
            '"anim.petr"'.padEnd(12) + '"petr.cop"'.padEnd(11) + 'Kw-Cartier'.padEnd(12) + 'Relevanta%');
console.log('  ' + '-'.repeat(73));

results.filter(r => !r.error).forEach(r => {
  const wcIcon = { A: '🟢', B: '🟡', C: '🟠', D: '🔴' }[r.wcGrade];
  console.log(`  ${r.name.padEnd(22)}${String(r.wc).padEnd(10)}${wcIcon} ${r.wcGrade.padEnd(4)}` +
              `${String(r.animatoriPetreceri).padEnd(12)}${String(r.petreceriCopii).padEnd(11)}` +
              `${String(r.slugKw).padEnd(12)}${r.partyRelevanceScore}%`);
});

console.log('\n📊 SECTIUNEA 2: ELEMENTE SEO OBLIGATORII\n');
results.filter(r => !r.error).forEach(r => {
  const seoIcon = r.seoScore === 100 ? '✅' : r.seoScore >= 80 ? '🟡' : '❌';
  console.log(`  ${seoIcon} ${r.name.padEnd(22)} SEO: ${r.seoScore}%`);
  if (r.seoIssues.length > 0) {
    r.seoIssues.forEach(i => console.log(`       ⚠️  ${i}`));
  }
});

console.log('\n📊 SECTIUNEA 3: SIMILARITATE INTRE PAGINI (max 20% acceptat)\n');

const pairs = [];
for (let i = 0; i < results.length; i++) {
  for (let j = i + 1; j < results.length; j++) {
    if (results[i].error || results[j].error) continue;
    const fpA = path.join(pagesDir, `${results[i].slug}.astro`);
    const fpB = path.join(pagesDir, `${results[j].slug}.astro`);
    const textA = extractText(fpA);
    const textB = extractText(fpB);
    
    // Extrage NUMAI sectiunile unice (scoate template comun)
    // Identifica textul specific de party (venues + themes + orga sections)
    const getUniqueText = (raw) => {
      const venuesMatch = raw.match(/Locatii pentru petreceri copii([\s\S]*?)Personaje si teme/);
      const themesMatch = raw.match(/Personaje si teme([\s\S]*?)Cum organizezi/);
      const orgaMatch = raw.match(/Cum organizezi([\s\S]*?)Intrebari frecvente/);
      return [
        venuesMatch ? venuesMatch[1] : '',
        themesMatch ? themesMatch[1] : '',
        orgaMatch ? orgaMatch[1] : ''
      ].join(' ').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').toLowerCase();
    };
    
    const rawA = fs.readFileSync(fpA, 'utf-8');
    const rawB = fs.readFileSync(fpB, 'utf-8');
    const uniqueA = getUniqueText(rawA);
    const uniqueB = getUniqueText(rawB);
    
    const simUnique = uniqueA.length > 100 && uniqueB.length > 100 ? jaccard(uniqueA, uniqueB) : jaccard(textA, textB);
    pairs.push({ a: results[i].name, b: results[j].name, sim: simUnique });
  }
}

const over20 = pairs.filter(p => p.sim > 0.20).length;
const sortedPairs = [...pairs].sort((x, y) => y.sim - x.sim);

console.log('  Top 10 cele mai similare perechi (continut unic party):');
sortedPairs.slice(0, 10).forEach(p => {
  const ok = p.sim <= 0.20;
  const icon = ok ? '✅' : '❌';
  console.log(`  ${icon} ${p.a.padEnd(22)} <-> ${p.b.padEnd(22)} | ${(p.sim*100).toFixed(1)}%`);
});

console.log(`\n  Total perechi > 20%: ${over20} / ${pairs.length}`);
const maxSim = Math.max(...pairs.map(p => p.sim));
const minSim = Math.min(...pairs.map(p => p.sim));
console.log(`  Similaritate max: ${(maxSim*100).toFixed(1)}% | min: ${(minSim*100).toFixed(1)}%`);

// ─── RAPORT FINAL ────────────────────────────────────────────────────────────
console.log('\n' + '═'.repeat(70));
console.log('  RAPORT FINAL — NOTE GLOBALE');
console.log('═'.repeat(70));
console.log('\n  ' + 'Pagina'.padEnd(24) + 'Cuvinte'.padEnd(8) + 'Keywords'.padEnd(10) + 'SEO%'.padEnd(8) + 'NOTA FINALA');
console.log('  ' + '-'.repeat(60));

let totalWc = 0;
let totalSEO = 0;
let allA = 0;
results.filter(r => !r.error).forEach(r => {
  const emoji = { A: '🟢 A', B: '🟡 B', C: '🟠 C', D: '🔴 D' }[r.overallGrade];
  console.log(`  ${r.name.padEnd(24)}${String(r.wc).padEnd(8)}${String(r.slugKw).padEnd(10)}${String(r.seoScore)+'%'.padEnd(8)}${emoji}`);
  totalWc += r.wc;
  totalSEO += r.seoScore;
  if (r.overallGrade === 'A') allA++;
});

const avgWc = Math.round(totalWc / results.filter(r => !r.error).length);
const avgSEO = Math.round(totalSEO / results.filter(r => !r.error).length);

console.log('\n' + '═'.repeat(70));
console.log(`  📝 Cuvinte medii per pagina: ${avgWc}`);
console.log(`  🔍 SEO score mediu: ${avgSEO}%`);
console.log(`  🎯 Pagini nota A: ${allA}/14`);
console.log(`  🔗 Perechi similare >20%: ${over20}/${pairs.length}`);

const readyForGoogle = avgWc >= 800 && avgSEO >= 80 && over20 < 20;
console.log(`\n  ${readyForGoogle ? '✅ READY FOR GOOGLE INDEX' : '⚠️  NECESITA IMBUNATATIRI'}`);
console.log('═'.repeat(70));

// Salveaza output
fs.writeFileSync(path.join(__dirname, 'seo_quality_result.txt'), 
  `SEO Quality Audit - ${new Date().toISOString()}\nAvg words: ${avgWc}\nAvg SEO: ${avgSEO}%\nSim pairs >20%: ${over20}/${pairs.length}`, 
  'utf-8');
