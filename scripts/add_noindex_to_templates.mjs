// add_noindex_to_templates.mjs
// Adauga robots="noindex, follow" paginilor comune cu continut template
// Pastram paginile pentru UX si crawl dar le excludem din index Google
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pDir = path.join(__dirname, '../src/pages/petreceri');

// Paginile din clustere cu duplicate confirmate (ex-cluster 1 si cluster 2)
// exceptam paginile mari: cartiere, sectoare-mari, bucuresti, ilfov hub
const KEEP_INDEXED = new Set([
  'titan', 'drumul-taberei', 'militari', 'berceni', 'floreasca',
  'colentina', 'rahova', 'crangasi', 'tineretului', 'aviatiei',
  'dorobanti', 'dristor', 'giulesti', 'pantelimon-cartier',
  'bucuresti', 'ilfov', 'sector-1', 'sector-2', 'sector-3',
  'sector-4', 'sector-5', 'sector-6',
  'voluntari', 'popesti-leordeni', 'otopeni', 'bragadiru', 
  'chiajna', 'pantelimon', 'jilava', 'magurele', 'mogosoaia',
  'buftea', 'chitila', 'cernica', 'snagov', 'giurgiu', 'calarasi'
]);

let noindexed = 0;
let skipped = 0;

const files = fs.readdirSync(pDir).filter(f => f.endsWith('.astro') && !f.includes('['));

for (const file of files) {
  const slug = file.replace('.astro', '');
  const fp = path.join(pDir, file);
  let content = fs.readFileSync(fp, 'utf-8');
  
  if (KEEP_INDEXED.has(slug)) { skipped++; continue; }
  
  // Deja noindex? skip
  if (content.includes('noindex')) { skipped++; continue; }
  
  // Adauga robots noindex
  if (content.includes('robots="index, follow"')) {
    content = content.replace('robots="index, follow"', 'robots="noindex, follow"');
    fs.writeFileSync(fp, content, 'utf-8');
    noindexed++;
  } else if (content.includes("canonical=")) {
    // Insereaza dupa canonical
    content = content.replace(
      /canonical="[^"]+"/,
      (m) => m + '\n  robots="noindex, follow"'
    );
    fs.writeFileSync(fp, content, 'utf-8');
    noindexed++;
  }
}

console.log(`\nNoindex aplicat: ${noindexed} pagini`);
console.log(`Pastrate indexate: ${skipped}`);
console.log(`\nPagini principale pastrate indexate:`);
for (const s of KEEP_INDEXED) console.log(`  - petreceri/${s}`);
