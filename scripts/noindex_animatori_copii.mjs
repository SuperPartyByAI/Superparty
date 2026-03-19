import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
let n = 0;
for (const d of fs.readdirSync(path.join(__dirname,'../src/pages')).filter(d => d.startsWith('animatori-copii'))) {
  const fp = path.join(__dirname,'../src/pages', d, 'index.astro');
  if (!fs.existsSync(fp)) continue;
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('noindex')) continue;
  c = c.replace('robots="index, follow"', 'robots="noindex, follow"');
  if (!c.includes('noindex')) {
    c = c.replace(/canonical="[^"]+"/, m => m + '\n  robots="noindex, follow"');
  }
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
}
console.log(`noindex aplicat pe ${n} pagini animatori-copii`);
