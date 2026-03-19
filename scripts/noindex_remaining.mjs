// noindex_remaining.mjs — aplica noindex pe paginile comune ramase
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pDir = path.join(__dirname, '../src/pages/petreceri');

const KEEP = new Set([
  'titan','drumul-taberei','militari','berceni','floreasca',
  'colentina','rahova','crangasi','tineretului','aviatiei',
  'dorobanti','dristor','giulesti','pantelimon-cartier',
  'bucuresti','ilfov',
  'sector-1','sector-2','sector-3','sector-4','sector-5','sector-6',
  'giurgiu','calarasi','voluntari','popesti-leordeni','bragadiru',
  'otopeni','chiajna','buftea'
]);

let n = 0;
for (const f of fs.readdirSync(pDir)) {
  if (!f.endsWith('.astro') || f.includes('[')) continue;
  const slug = f.replace('.astro', '');
  if (KEEP.has(slug)) continue;
  const fp = path.join(pDir, f);
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('noindex')) continue;
  c = c.replace('robots="index, follow"', 'robots="noindex, follow"');
  if (!c.includes('noindex')) {
    c = c.replace(/canonical="[^"]+"/, (m) => m + '\n  robots="noindex, follow"');
  }
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
  console.log('noindex:', slug);
}
console.log(`\nNoindex aplicat pe inca ${n} pagini. Total pastrate indexate: ${KEEP.size}`);
