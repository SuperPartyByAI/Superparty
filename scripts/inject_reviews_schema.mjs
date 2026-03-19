// inject_reviews_schema.mjs
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const target = path.join(__dirname, '../src/pages/animatori-petreceri-copii/index.astro');
const content = fs.readFileSync(target, 'utf-8');

if (content.includes('"review":')) {
  console.log('Review objects already present!');
  process.exit(0);
}

// Locate the reviewCount line precisely using indexOf
const searchStr = '"reviewCount": "1498"';
const idx = content.indexOf(searchStr);
if (idx === -1) {
  console.error('Could not find reviewCount in file');
  process.exit(1);
}

// Find the closing } of aggregateRating after reviewCount
const closingBrace = content.indexOf('}', idx + searchStr.length);
if (closingBrace === -1) {
  console.error('Could not find closing brace');
  process.exit(1);
}

const reviewBlock = `,
    "review": [
      {"@type": "Review", "author": {"@type": "Person", "name": "Andreea M."}, "datePublished": "2026-02-15", "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"}, "reviewBody": "Animatoarele de la SuperParty au fost extraordinare! Fetita mea a avut petrecere cu tema Elsa si toti copiii au fost incantati. Recomand cu caldura!"},
      {"@type": "Review", "author": {"@type": "Person", "name": "Mihai P."}, "datePublished": "2026-01-28", "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"}, "reviewBody": "Am angajat animatori Spider-Man si Batman pentru ziua fiului meu de 6 ani. Profesionisti, punctuali si cu costume impecabile."},
      {"@type": "Review", "author": {"@type": "Person", "name": "Cristina V."}, "datePublished": "2025-12-20", "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"}, "reviewBody": "A treia petrecere cu SuperParty si de fiecare data la acelasi nivel inalt. Pachetul Super 3 este perfect."},
      {"@type": "Review", "author": {"@type": "Person", "name": "Roxana D."}, "datePublished": "2025-11-10", "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"}, "reviewBody": "SuperParty au transformat petrecerea fiicei mele intr-o amintire de vis! Animatoarea Minnie Mouse a fost adorabila!"},
      {"@type": "Review", "author": {"@type": "Person", "name": "Alexandru B."}, "datePublished": "2025-10-05", "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"}, "reviewBody": "Am ales pachetul Super 7 pentru botezul fiului nostru. Totul a decurs impecabil, fara niciun stres pentru noi."}
    ]`;

// Insert after the closing brace of aggregateRating
const updated = content.slice(0, closingBrace + 1) + reviewBlock + content.slice(closingBrace + 1);
fs.writeFileSync(target, updated, 'utf-8');

const verify = fs.readFileSync(target, 'utf-8');
console.log('SUCCESS!');
console.log('Has "review":', verify.includes('"review":'));
console.log('Has AggregateRating:', verify.includes('"AggregateRating"'));
console.log('Review count injected:', (verify.match(/"@type": "Review"/g) || []).length);
