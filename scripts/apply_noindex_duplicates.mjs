// apply_noindex_duplicates.mjs
// Adaugă robots: noindex în frontmatter-ul articolelor duplicate
// Rulare: node scripts/apply_noindex_duplicates.mjs

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Citim lista de candidate (generată de audit_duplicates.mjs)
const candidatesFile = path.join(__dirname, 'noindex_candidates.txt');
if (!fs.existsSync(candidatesFile)) {
  console.error('❌ Nu găsesc noindex_candidates.txt. Rulează mai întâi audit_duplicates.mjs');
  process.exit(1);
}

const candidates = fs.readFileSync(candidatesFile, 'utf-8')
  .split('\n')
  .map(f => f.trim())
  .filter(Boolean);

const ARTICLES_DIR = path.join(__dirname, '../src/content/seo-articles');

let updated = 0;
let alreadyNoindex = 0;
let missing = 0;

for (const filename of candidates) {
  // Suportă cu și fără extensie
  const fullName = filename.endsWith('.mdx') ? filename : filename + '.mdx';
  const filePath = path.join(ARTICLES_DIR, fullName);

  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  Lipsă: ${fullName}`);
    missing++;
    continue;
  }

  let content = fs.readFileSync(filePath, 'utf-8');

  // Verificăm dacă deja are noindex
  if (content.includes("robots: 'noindex'") || content.includes('robots: noindex') || content.includes('robots: "noindex"')) {
    alreadyNoindex++;
    continue;
  }

  // Inserăm robots: noindex după prima linie (---)
  // Frontmatter: --- \n ...\n ---
  const frontmatterEnd = content.indexOf('\n---', 4); // al doilea ---
  if (frontmatterEnd === -1) {
    console.log(`⚠️  Nu am găsit frontmatter valid: ${fullName}`);
    continue;
  }

  // Adăugăm robots field înainte de closing ---
  content = content.slice(0, frontmatterEnd) + 
    "\nrobots: 'noindex, nofollow'" + 
    content.slice(frontmatterEnd);

  fs.writeFileSync(filePath, content, 'utf-8');
  updated++;
}

console.log('\n✅ REZULTAT:');
console.log(`  Articole actualizate (noindex adăugat): ${updated}`);
console.log(`  Deja aveau noindex:                     ${alreadyNoindex}`);
console.log(`  Fișiere lipsă:                          ${missing}`);
console.log('\n💡 Acum deployează și Google va opri indexarea duplicatelor.');
