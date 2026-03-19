// check_unique_content.mjs
// Analiza unicitate REALA - extrage doar textul specific per pagina (nu template)
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dir = path.join(__dirname, '../src/pages/petreceri');

const cartiere = [
  'titan','drumul-taberei','militari','berceni','floreasca',
  'colentina','rahova','crangasi','tineretului','aviatiei',
  'dorobanti','dristor','giulesti','pantelimon-cartier'
];

// Extrage DOAR textul unic per pagina (hero desc + zone locale + FAQ)
function extractUniqueText(fp) {
  const c = fs.readFileSync(fp, 'utf-8');
  const parts = [];
  
  // 1. Paragraful hero (descrierea cartierului)
  const heroM = c.match(/SuperParty aduce magia[^<]{20,400}/);
  if (heroM) parts.push(heroM[0]);
  
  // 2. Elementele din lista de zone locale (<li> items)
  const liM = [...c.matchAll(/<li>([^<]{15,200})<\/li>/g)];
  liM.forEach(m => parts.push(m[1]));
  
  // 3. Raspunsurile FAQ din array (["intrebare", "raspuns"])  
  const faqM = [...c.matchAll(/\["[^"]+",\s*"([^"]{30,}?)"\]/g)];
  faqM.forEach(m => parts.push(m[1]));

  return parts.join(' ').toLowerCase().replace(/[^a-z\s]/gi, ' ').replace(/\s+/g, ' ').trim();
}

// Cuvinte unice (ignora stopwords si template words)
const STOP = new Set(['este','sunt','pentru','acest','aceasta','care','este','din','sau','nu','da','cu','la','de','si','in','pe','un','o','cel','a','i','ii','iii','iv','super','party','ron','ore','min','animatori']);

function getWords(text) {
  return new Set(text.split(' ').filter(w => w.length > 4 && !STOP.has(w)));
}

function jaccard(sA, sB) {
  const inter = [...sA].filter(x => sB.has(x)).length;
  const union = new Set([...sA, ...sB]).size;
  return union === 0 ? 1 : inter / union;
}

// Incarca paginile
const pages = [];
for (const slug of cartiere) {
  const fp = path.join(dir, `${slug}.astro`);
  if (!fs.existsSync(fp)) { console.log('LIPSA:', slug); continue; }
  const text = extractUniqueText(fp);
  const words = getWords(text);
  pages.push({ slug, words, wordCount: words.size });
}

console.log('\n📊 ANALIZA UNICITATE CONTINUT SPECIFIC (exclus template)\n');
console.log('Prag: max 20% similaritate = minim 80% unicitate\n');

let problems = 0;
const pairs = [];
for (let i = 0; i < pages.length; i++) {
  for (let j = i + 1; j < pages.length; j++) {
    const sim = jaccard(pages[i].words, pages[j].words);
    const ok = sim <= 0.20;
    pairs.push({ a: pages[i].slug, b: pages[j].slug, sim, ok });
    if (!ok) problems++;
  }
}

// Afis top 10 cele mai similare
const sorted = [...pairs].sort((x,y) => y.sim - x.sim);
console.log('Top 10 perechi (cele mai similare):');
sorted.slice(0, 10).forEach(({ a, b, sim, ok }) => {
  const icon = ok ? '✅' : '❌';
  const simPct = (sim * 100).toFixed(1);
  const uniPct = ((1 - sim) * 100).toFixed(1);
  console.log(`  ${icon} ${a.padEnd(25)} ↔ ${b.padEnd(25)} | similar: ${simPct}% | unic: ${uniPct}%`);
});

console.log('\nTop 5 cele mai diferite:');
sorted.slice(-5).reverse().forEach(({ a, b, sim }) => {
  const simPct = (sim * 100).toFixed(1);
  const uniPct = ((1 - sim) * 100).toFixed(1);
  console.log(`  ✅ ${a.padEnd(25)} ↔ ${b.padEnd(25)} | similar: ${simPct}% | unic: ${uniPct}%`);
});

console.log('\n📄 Cuvinte unice specifice per pagina:');
pages.forEach(({ slug, wordCount }) => {
  const icon = wordCount >= 30 ? '✅' : '⚠️ ';
  console.log(`  ${icon} ${slug.padEnd(25)}: ${wordCount} cuvinte unice`);
});

const total = pairs.length;
console.log(`\n${'─'.repeat(60)}`);
if (problems === 0) {
  console.log(`✅ TOATE ${total} perechi au unicitate >= 80%! Safe pentru SEO.`);
} else {
  console.log(`❌ ${problems}/${total} perechi cu similaritate > 20% (necesita continut mai unic)`);
}
console.log('');
