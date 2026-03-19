import fs from 'fs';
import path from 'path';

const dir = 'src/content/seo-articles';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.mdx'));

const articles = files.map(f => {
  const raw = fs.readFileSync(path.join(dir, f), 'utf-8');
  const title = (raw.match(/title:\s*['"](.+?)['"]/)?.[1] || '').trim();
  const body = raw.replace(/---[\s\S]*?---/, '').trim();
  return { file: f, title, bodyLen: body.length, bodyStart: body.slice(0, 120).replace(/\s+/g, ' ') };
});

// Grupează după primele 80 chars de body (detectează template-uri identice)
const grouped = {};
articles.forEach(a => {
  const key = a.bodyStart.slice(0, 80);
  if (!grouped[key]) grouped[key] = [];
  grouped[key].push(a.file);
});

console.log('=== ANALIZA UNICITATE ===');
console.log('Total articole:', articles.length);

const dupeGroups = Object.entries(grouped).filter(([k, v]) => v.length > 1);
console.log('Grupuri cu continut IDENTIC (primele 80 chars):', dupeGroups.length);
dupeGroups.forEach(([key, fs2], i) => {
  console.log('\nTemplate #' + (i+1) + ' (' + fs2.length + ' articole identice):');
  console.log('  Start:', JSON.stringify(key.slice(0, 70)));
  fs2.slice(0, 5).forEach(f => console.log('  -', f));
  if (fs2.length > 5) console.log('  ... +', fs2.length - 5, 'altele');
});

const lens = articles.map(a => a.bodyLen);
console.log('\nLungime medie:', Math.round(lens.reduce((s, x) => s+x, 0)/lens.length), 'chars');
console.log('Min:', Math.min(...lens), '/ Max:', Math.max(...lens), 'chars');

// Articole unice vs duplicate
const uniqueCount = Object.values(grouped).filter(v => v.length === 1).length;
console.log('\nArticole cu continut UNIC:', uniqueCount, '/', articles.length);
console.log('Articole cu continut DUPLICAT:', articles.length - uniqueCount, '/', articles.length);
