// inject_flagship_link.mjs
// Injectează FlagshipLink.astro în toate paginile locale animatori-copii-*
// Rulare: node scripts/inject_flagship_link.mjs

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PAGES_DIR = path.join(__dirname, '../src/pages');

// Paginile locale care trebuie să trimită link juice spre flagship
const LOCAL_PAGE_DIRS = [
  'animatori-copii-sector-1',
  'animatori-copii-sector-2',
  'animatori-copii-sector-3',
  'animatori-copii-sector-4',
  'animatori-copii-sector-5',
  'animatori-copii-sector-6',
  'animatori-copii-bucuresti',
  'animatori-copii-ilfov',
  'animatori-copii-voluntari',
  'animatori-copii-otopeni',
  'animatori-copii-pantelimon',
  'animatori-copii-bragadiru',
  'animatori-copii-chiajna',
  'animatori-copii-popesti-leordeni',
];

const IMPORT_LINE = `import FlagshipLink from '../../components/FlagshipLink.astro';`;
const COMPONENT_TAG = `<FlagshipLink />`;

// Injectăm componenta după primul </section> din <main>
const INJECT_AFTER = `</section>`;

let updated = 0;
let skipped = 0;

for (const dir of LOCAL_PAGE_DIRS) {
  const filePath = path.join(PAGES_DIR, dir, 'index.astro');
  
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  LIPSĂ: ${filePath}`);
    continue;
  }

  let content = fs.readFileSync(filePath, 'utf-8');

  // Verificăm dacă e deja injectat
  if (content.includes('FlagshipLink')) {
    console.log(`✓ DEJA EXISTĂ: ${dir}`);
    skipped++;
    continue;
  }

  // 1. Adăugăm importul în frontmatter (înainte de ---)
  // Găsim al doilea --- (closing frontmatter)
  const frontmatterEnd = content.indexOf('---', 3); // sărim primul ---
  if (frontmatterEnd === -1) {
    console.log(`⚠️  Nu am găsit frontmatter în: ${dir}`);
    continue;
  }

  // Inserăm importul înainte de ---
  const closingDashes = content.lastIndexOf('---', content.indexOf('<Layout'));
  if (closingDashes > 0) {
    content = content.slice(0, closingDashes) + 
      IMPORT_LINE + '\n' + 
      content.slice(closingDashes);
  }

  // 2. Injectăm <FlagshipLink /> după primul </section> din main
  // (după secțiunea hero)
  const heroSectionEnd = content.indexOf('</section>', content.indexOf('<main'));
  if (heroSectionEnd !== -1) {
    const insertPos = heroSectionEnd + '</section>'.length;
    content = content.slice(0, insertPos) + 
      '\n\n    ' + COMPONENT_TAG + '\n' + 
      content.slice(insertPos);
  }

  fs.writeFileSync(filePath, content, 'utf-8');
  console.log(`✅ INJECTAT: ${dir}`);
  updated++;
}

console.log(`\n📊 Rezultat: ${updated} pagini actualizate, ${skipped} deja aveau FlagshipLink.`);
