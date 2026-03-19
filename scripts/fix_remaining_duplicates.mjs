// fix_remaining_duplicates.mjs
// Găsește și noindex-ează articolele duplicate rămase neprotejate

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dir = path.join(__dirname, '../src/content/seo-articles');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.mdx'));

// Grupează după primele 80 chars body (identice = duplicate)
const groups = {};
for (const f of files) {
  const raw = fs.readFileSync(path.join(dir, f), 'utf-8');
  const body = raw.replace(/---[\s\S]*?---/, '').trim().replace(/\s+/g, ' ');
  const key = body.slice(0, 80);
  if (!groups[key]) groups[key] = [];
  groups[key].push({ file: f, raw });
}

let fixed = 0;
let alreadyOk = 0;

for (const [key, articles] of Object.entries(groups)) {
  if (articles.length <= 1) continue;

  // Sortăm: primul e "keeper" (cel mai lung sau primul alfabetic)
  const sorted = [...articles].sort((a, b) => b.raw.length - a.raw.length);
  const keeper = sorted[0];
  const rest = sorted.slice(1);

  for (const { file, raw } of rest) {
    const hasNoindex = raw.includes('noindex');
    if (hasNoindex) { alreadyOk++; continue; }

    // Adaugă noindex în frontmatter
    const fmEnd = raw.indexOf('\n---', 4);
    if (fmEnd === -1) continue;

    const fixed_content = raw.slice(0, fmEnd) + "\nrobots: 'noindex, nofollow'" + raw.slice(fmEnd);
    fs.writeFileSync(path.join(dir, file), fixed_content, 'utf-8');
    fixed++;
    console.log(`  noindex → ${file}`);
  }
}

console.log(`\n✅ DONE:`);
console.log(`   Acum noindex-uite: ${fixed}`);
console.log(`   Deja protejate:    ${alreadyOk}`);
