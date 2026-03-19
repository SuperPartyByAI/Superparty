// fix_22_unprotected.mjs
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dir = path.join(__dirname, '../src/content/seo-articles');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.mdx'));

const groups = {};
for (const f of files) {
  const raw = fs.readFileSync(path.join(dir, f), 'utf-8');
  const body = raw.replace(/---[\s\S]*?---/, '').trim().replace(/\s+/g, ' ');
  const key = body.slice(0, 80);
  if (!groups[key]) groups[key] = [];
  groups[key].push(f);
}

let fixed = 0;
for (const [key, arts] of Object.entries(groups)) {
  if (arts.length <= 1) continue;
  const sorted = [...arts].sort((a, b) => a.length - b.length);
  const rest = sorted.slice(1);
  for (const f of rest) {
    const fp = path.join(dir, f);
    const raw = fs.readFileSync(fp, 'utf-8');
    if (raw.includes('noindex')) continue;
    const fmEnd = raw.indexOf('\n---', 4);
    if (fmEnd === -1) continue;
    const patched = raw.slice(0, fmEnd) + "\nrobots: 'noindex, nofollow'" + raw.slice(fmEnd);
    fs.writeFileSync(fp, patched, 'utf-8');
    fixed++;
    console.log('  fixed:', f);
  }
}
console.log('Total fixed:', fixed);

// Verificare finala
const noix = files.filter(f => fs.readFileSync(path.join(dir, f), 'utf-8').includes('noindex')).length;
console.log('TOTAL:', files.length, '| Noindex:', noix, '| Indexabile:', files.length - noix);
