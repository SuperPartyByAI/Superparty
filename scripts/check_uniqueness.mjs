// check_uniqueness.mjs
// Verifica daca paginile de cartiere sunt cel putin 80% diferite intre ele
// Foloseste Jaccard Similarity pe word bigrams (perechi de cuvinte)
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages/petreceri');

// Paginile de cartiere generate
const cartiere = [
  'titan', 'drumul-taberei', 'militari', 'berceni', 'floreasca',
  'colentina', 'rahova', 'crangasi', 'tineretului', 'aviatiei',
  'dorobanti', 'dristor', 'giulesti', 'pantelimon-cartier'
];

// Extrage textul vizibil din fisierul .astro (ignora CSS, JS, frontmatter)
function extractText(filepath) {
  let content = fs.readFileSync(filepath, 'utf-8');
  // Elimina frontmatter (---)
  content = content.replace(/^---[\s\S]*?---/m, '');
  // Elimina blocuri style
  content = content.replace(/<style[\s\S]*?<\/style>/gi, '');
  // Elimina blocuri script
  content = content.replace(/<script[\s\S]*?<\/script>/gi, '');
  // Elimina taguri HTML
  content = content.replace(/<[^>]+>/g, ' ');
  // Elimina expresii Astro {/* ... */} si {variabile}
  content = content.replace(/\{[^}]*\}/g, ' ');
  // Normalizare
  content = content.toLowerCase().replace(/[^a-zăâîșț\s]/gi, ' ').replace(/\s+/g, ' ').trim();
  return content;
}

// Construieste set de bigrams (perechi de cuvinte consecutive)
function getBigrams(text) {
  const words = text.split(' ').filter(w => w.length > 3);
  const bigrams = new Set();
  for (let i = 0; i < words.length - 1; i++) {
    bigrams.add(words[i] + '_' + words[i+1]);
  }
  return bigrams;
}

// Jaccard similarity intre doua seturi
function jaccard(setA, setB) {
  const intersection = new Set([...setA].filter(x => setB.has(x)));
  const union = new Set([...setA, ...setB]);
  return union.size === 0 ? 0 : intersection.size / union.size;
}

// Incarca toate paginile
const pages = [];
for (const slug of cartiere) {
  const fp = path.join(pagesDir, `${slug}.astro`);
  if (!fs.existsSync(fp)) {
    console.log(`⚠️  LIPSA: ${slug}.astro`);
    continue;
  }
  const text = extractText(fp);
  const bigrams = getBigrams(text);
  const wordCount = text.split(' ').filter(w => w.length > 3).length;
  pages.push({ slug, text, bigrams, wordCount });
}

console.log(`\n📊 ANALIZA UNICITATE CONTINUT — ${pages.length} pagini de cartiere\n`);
console.log('─'.repeat(70));

// Compare pairwise
let problemCount = 0;
const results = [];

for (let i = 0; i < pages.length; i++) {
  for (let j = i + 1; j < pages.length; j++) {
    const sim = jaccard(pages[i].bigrams, pages[j].bigrams);
    const simPct = (sim * 100).toFixed(1);
    const uniquePct = ((1 - sim) * 100).toFixed(1);
    const ok = sim < 0.20; // max 20% similar = min 80% unic
    results.push({ a: pages[i].slug, b: pages[j].slug, simPct, uniquePct, ok });
    if (!ok) {
      problemCount++;
      console.log(`❌ PROBLEMA: ${pages[i].slug} ↔ ${pages[j].slug}`);
      console.log(`   Similaritate: ${simPct}% | Unicitate: ${uniquePct}% (sub 80%!)`);
    }
  }
}

console.log('\n─'.repeat(70));
console.log(`\n📋 RAPORT FINAL:\n`);

// Afiseaza primele cu cea mai mare similaritate (potential problematice)
const sorted = [...results].sort((a, b) => parseFloat(b.simPct) - parseFloat(a.simPct));
console.log('Top 5 cele mai similare perechi:');
sorted.slice(0, 5).forEach(({ a, b, simPct, uniquePct, ok }) => {
  const icon = ok ? '✅' : '❌';
  console.log(`  ${icon} ${a} ↔ ${b}: ${simPct}% similar / ${uniquePct}% unic`);
});

console.log('\nTop 5 cele mai diferite perechi:');
sorted.slice(-5).reverse().forEach(({ a, b, simPct, uniquePct }) => {
  console.log(`  ✅ ${a} ↔ ${b}: ${simPct}% similar / ${uniquePct}% unic`);
});

// Per-pagina stats
console.log('\n📄 Statistici per pagina:');
pages.forEach(({ slug, wordCount, bigrams }) => {
  console.log(`  ${slug}: ${wordCount} cuvinte, ${bigrams.size} bigrams unici`);
});

console.log(`\n${'─'.repeat(70)}`);
if (problemCount === 0) {
  console.log(`\n✅ TOATE cele ${results.length} perechi verificate au UNICITATE >= 80%!`);
  console.log('   Paginile sunt suficient de diferite pentru Google (fara risc de duplicate).\n');
} else {
  console.log(`\n❌ ${problemCount} perechi cu similaritate > 20% — necesita imbunatatire!\n`);
}
