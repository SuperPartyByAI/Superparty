import fs from 'fs';
import path from 'path';

const dir = 'src/content/seo-articles';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.mdx')).sort();

// Extrage frontmatter + body pentru fiecare articol
const articles = files.map(f => {
  const raw = fs.readFileSync(path.join(dir, f), 'utf-8');
  const title = (raw.match(/title:\s*['"](.+?)['"]/)?.[1] || f).trim();
  const slug = (raw.match(/slug:\s*['"](.+?)['"]/)?.[1] || '').trim();
  const body = raw.replace(/---[\s\S]*?---/, '').trim();
  // Normalizat: elimina spatii extra, newlines
  const bodyNorm = body.replace(/\s+/g, ' ').trim();
  return { file: f, title, slug, bodyLen: body.length, bodyNorm, body80: bodyNorm.slice(0, 80) };
});

// Grupează după primele 80 chars — detectează template-uri identice
const groups = {};
articles.forEach(a => {
  if (!groups[a.body80]) groups[a.body80] = [];
  groups[a.body80].push(a);
});

// Separă unique vs duplicate
const uniqueArticles = [];
const duplicateGroups = [];

Object.entries(groups).forEach(([key, arts]) => {
  if (arts.length === 1) {
    uniqueArticles.push(arts[0]);
  } else {
    duplicateGroups.push({ key, articles: arts });
  }
});

const totalDupes = duplicateGroups.reduce((s, g) => s + g.articles.length, 0);

// Output raport
console.log('╔══════════════════════════════════════════════════════╗');
console.log('║        RAPORT DUPLICATE CONTENT — SUPERPARTY.RO     ║');
console.log('╚══════════════════════════════════════════════════════╝');
console.log('');
console.log(`Total articole scanate:     ${articles.length}`);
console.log(`Articole UNICE:             ${uniqueArticles.length} (${Math.round(uniqueArticles.length/articles.length*100)}%)`);
console.log(`Articole DUPLICATE:         ${totalDupes} (${Math.round(totalDupes/articles.length*100)}%)`);
console.log(`Grupuri/template-uri:       ${duplicateGroups.length}`);
console.log('');
console.log('─── TOP 10 GRUPURI DUPLICATE (cele mai mari) ───');
duplicateGroups
  .sort((a, b) => b.articles.length - a.articles.length)
  .slice(0, 10)
  .forEach((g, i) => {
    console.log(`\n#${i+1} — ${g.articles.length} articole cu conținut identic:`);
    console.log(`   Template: "${g.key.slice(0, 70)}..."`);
    g.articles.slice(0, 4).forEach(a => console.log(`   • ${a.file}`));
    if (g.articles.length > 4) console.log(`   ... +${g.articles.length - 4} altele`);
  });

console.log('\n─── ARTICOLE UNICE (primele 20) ───');
uniqueArticles.slice(0, 20).forEach(a => {
  console.log(`  ✓ ${a.file} (${a.bodyLen} chars)`);
});
if (uniqueArticles.length > 20) console.log(`  ... +${uniqueArticles.length - 20} altele unice`);

// Salvăm lista duplicatelor pentru noindex action
const noindexList = duplicateGroups.flatMap(g => 
  // Păstrăm primul articol din grup, marcăm restul ca noindex
  g.articles.slice(1).map(a => a.file)
);

fs.writeFileSync('scripts/noindex_candidates.txt', noindexList.join('\n'), 'utf-8');
console.log(`\n✅ Lista ${noindexList.length} articole candidate pentru noindex → scripts/noindex_candidates.txt`);

console.log('\n─── RECOMANDARE ───');
console.log(`Adaugă "noindex" la ${noindexList.length} articole duplicate.`);
console.log('Păstrează cele', uniqueArticles.length, 'articole unice + 1 per grup template.');
console.log('Efectul estimat: eliminare penalizare duplicate content → urcare ranking.');
