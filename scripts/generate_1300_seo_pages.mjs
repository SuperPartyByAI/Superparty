import fs from 'fs';
import path from 'path';

const characters = [
  { name: 'Spiderman', slug: 'spiderman' },
  { name: 'Batman', slug: 'batman' },
  { name: 'Elsa Frozen', slug: 'elsa-frozen' },
  { name: 'Anna Frozen', slug: 'anna-frozen' },
  { name: 'Olaf', slug: 'olaf' },
  { name: 'Mickey Mouse', slug: 'mickey-mouse' },
  { name: 'Minnie Mouse', slug: 'minnie-mouse' },
  { name: 'Ladybug Miraculous', slug: 'miraculous-ladybug' },
  { name: 'Ariel Mica Sirenă', slug: 'ariel' },
  { name: 'Cenușăreasa', slug: 'cenusareasa' },
  { name: 'Rapunzel', slug: 'rapunzel' },
  { name: 'Alba ca Zăpada', slug: 'alba-ca-zapada' },
  { name: 'Aurora', slug: 'aurora' },
  { name: 'Belle', slug: 'belle' },
  { name: 'Sonic', slug: 'sonic' },
  { name: 'Pikachu', slug: 'pikachu' },
  { name: 'Chase Paw Patrol', slug: 'chase' },
  { name: 'Marshall Paw Patrol', slug: 'marshall' },
  { name: 'Skye Paw Patrol', slug: 'skye' },
  { name: 'Rublle Paw Patrol', slug: 'rubble' },
  { name: 'Minion', slug: 'minion' },
  { name: 'Pirat', slug: 'pirat' },
  { name: 'Zâna Măseluță', slug: 'zana-maseluta' },
  { name: 'Aladdin', slug: 'aladdin' },
  { name: 'Jasmine', slug: 'jasmine' },
  { name: 'Iron Man', slug: 'iron-man' }
];

const locations = [
  'Sector 1', 'Sector 2', 'Sector 3', 'Sector 4', 'Sector 5', 'Sector 6',
  'Voluntari', 'Otopeni', 'Buftea', 'Chitila', 'Măgurele', 'Popești-Leordeni',
  'Pantelimon', 'Bragadiru', 'Chiajna', 'Corbeanca', 'Snagov', 'Mogoșoaia',
  'Tunari', 'Ștefăneștii de Jos', 'Afumați', 'Glina', 'Cernica', 'Dobroești',
  'Berceni', 'Jilava', '1 Decembrie', 'Copăceni', 'Vidra', 'Clinceni', 'Domnești',
  'Ciorogârla', 'Dragomirești-Vale', 'Joița', 'Săbăreni', 'Tărtășești', 'Ciocănești',
  'Crevedia', 'Periș', 'Ciolpani', 'Gruiu', 'Nuci', 'Grădiștea', 'Moara Vlăsiei',
  'Dascălu', 'Petrăchioaia', 'Balotești', 'Adunații-Copăceni', 'Mihăilești', 'Tâncăbești'
];

const slugify = (str) => {
  let s = str.toLowerCase();
  const map = { 'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't' };
  s = s.replace(/[ăâîșț]/g, m => map[m]);
  return s.replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
};

const DIR = 'src/content/seo-articles';
if (!fs.existsSync(DIR)) fs.mkdirSync(DIR, { recursive: true });

let created = 0;
let existing = 0;

console.log(`Pornesc generarea a ${characters.length * locations.length} combinatii posibile...`);

for (const char of characters) {
  for (const loc of locations) {
    const locSlug = slugify(loc);
    const fileName = `animatori-petreceri-copii-${char.slug}-${locSlug}.mdx`;
    const filePath = path.join(DIR, fileName);

    if (fs.existsSync(filePath)) {
      existing++;
      continue;
    }

    const title = `Animator ${char.name} Petreceri Copii ${loc} | Superparty.ro`;
    const desc = `Animator ${char.name} la petreceri copii în ${loc} sau împrejurimi. Pachet cu jocuri, face painting profesional și baloane modelate. Rezervă la 0722744377!`;
    const keywords = `animator ${char.name}, petreceri copii ${loc}, animatori copii, baloane, face painting`;
    
    // Setăm noindex inițial până când punem proza unică, sau direct index, follow (oricum băgăm proza in minutul urmator)
    const frontmatter = `---
title: "${title}"
description: "${desc}"
indexStatus: 'ready'
pubDate: 2026-03-20
keywords: "${keywords}"
robots: 'index, follow'
---

UNIQUE-PROSE-MARKER
`;
    fs.writeFileSync(filePath, frontmatter, 'utf8');
    created++;
  }
}

console.log(`[SUCCES] Generare completa!`);
console.log(`Pagini noi adaugate: ${created}`);
console.log(`Pagini deja existente ignorate: ${existing}`);
console.log(`Total pagini in seo-articles: ${fs.readdirSync(DIR).length}`);
