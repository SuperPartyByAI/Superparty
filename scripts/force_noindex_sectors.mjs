// force_noindex_sectors.mjs — Force noindex pe animatori-copii-sector-X
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const dirs = fs.readdirSync(path.join(__dirname,'../src/pages'))
  .filter(d => d.match(/^animatori-copii-sector-\d+$/));

let n = 0;
for (const d of dirs) {
  const fp = path.join(__dirname,'../src/pages', d, 'index.astro');
  if (!fs.existsSync(fp)) continue;
  let c = fs.readFileSync(fp, 'utf-8');
  
  // Remove any existing robots meta
  c = c.replace(/\s*robots="[^"]*"/g, '');
  
  // Add noindex to Layout props — find the Layout opening tag
  c = c.replace(/<Layout\b/g, '<Layout\n  robots="noindex, follow"');
  
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
  console.log('noindex forced:', d);
}
console.log(`Done: ${n} pagini`);
