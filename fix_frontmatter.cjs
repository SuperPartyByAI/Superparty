const fs = require('fs');
const path = require('path');

const dir = 'src/content/seo-articles';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));

let fixed = 0;
for (const f of files) {
  const p = path.join(dir, f);
  let c = fs.readFileSync(p, 'utf8');

  // Prevent double injection if run twice
  if (c.startsWith('---')) continue;

  const slug = f.replace(/\.md$/, '');
  const rawTitle = slug.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  const finalTitle = rawTitle.includes('Animatori') ? rawTitle : 'Animatori Petreceri Copii ' + rawTitle;

  const fm = `---
title: "${finalTitle}"
description: "Organizam super petreceri pentru copii in locatia ${rawTitle}. Alege experienta SuperParty, cu personaje de poveste, jocuri fantastice si amintiri de neuitat!"
indexStatus: "ready"
robots: "index, follow"
---

`;

  fs.writeFileSync(p, fm + c, 'utf8');
  fixed++;
}

console.log('Fixed ' + fixed + ' files.');
