import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

let code = fs.readFileSync(path.join(__dirname, 'prose_v3.mjs'), 'utf-8');

// Modify style functions
code = code.replace(/function style(\d)\(loc, d\)/g, 'function style$1(loc, d, charName)');
// Replace d.topChar with charName
code = code.replace(/d\.topChar/g, 'charName');
// Modify genProse
code = code.replace(/function genProse\(f, loc, d\) \{[\s\S]*?return styleFn\(loc, d\).join\([^)]+\);\n\}/, 
`function genProse(f, loc, d, charName) {
  const h = (f + charName).split('').reduce((a,c)=>a+c.charCodeAt(0),0);
  const styleFn = styles[h % styles.length];
  return styleFn(loc, d, charName).join('\\n\\n');
}`);

// Replace the MAIN block completely
const newMain = `// ── MAIN ─────────────────────────────────────────────────────────
const dir = path.join(ROOT, 'src/content/seo-articles');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.mdx'));

let updated = 0;
for(const f of files) {
  const fp = path.join(dir, f);
  let c = fs.readFileSync(fp, 'utf-8');
  
  const titleMatch = c.match(/title:\\s*"([^"]+)"/);
  const title = titleMatch ? titleMatch[1] : '';
  const locMatch = title.match(/Copii (.*?) \\|/i);
  let loc = locMatch ? locMatch[1].trim() : f.replace('.mdx', '');
  loc = loc.replace('București – ', '').replace('Bucuresti - ', '');
  
  const charMatch = title.match(/Animator\\s(.*?)\\sPetreceri/i);
  const charName = charMatch ? charMatch[1].trim() : 'Personaj';
  
  let slugKey = loc.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  if ((slugKey === 'bucuresti' || slugKey === 'sector') && f.includes('sector-')) {
     const sm = f.match(/(sector-[1-6])/);
     if (sm) slugKey = sm[1];
  }
  
  const d = L[slugKey] || {jud:'Ilfov',km:25,dn:'drum local',pop:5000,regiune:'zona metropolitana',vecin:'localitati ilfovene',caract:'comunitate din aria metropolitana Bucuresti',topChar:charName,tip:'com'};
  
  const prose = genProse(f, loc, d, charName);
  
  const hVal = (slugKey+charName).split('').reduce((a,c_)=>a+c_.charCodeAt(0),0)%5;
  const titles = [
    'Ghid complet pentru petreceri copii cu ' + charName + ' în ' + loc,
    'Animatori în ' + loc + ' — Cum rezervi personajul ' + charName,
    loc + ' și SuperParty — Cheamă-l pe ' + charName + ' la aniversare',
    'Experiențe reale de la petreceri cu ' + charName + ' în ' + loc,
    charName + ' in ' + loc + ' - De ce SuperParty este alegerea optimă'
  ];
  
  const sectionHTML = \`
<!-- UNIQUE-PROSE-MARKER - \${charName} -->
<section class="zona-detail" style="padding:2.5rem 0;background:rgba(255,255,255,0.02)">
  <div class="container" style="max-width:820px">
    <h2 style="font-size:1.2rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem">\${titles[hVal]}</h2>
    \${prose.split('\\n\\n').map(pr=>\`<p style="color:var(--text-muted);line-height:1.95;font-size:.93rem;margin-bottom:1.1rem">\${pr.trim()}</p>\`).join('\\n    ')}
  </div>
</section>\`;

  // Eliminam vechiul marker sau structura XML
  c = c.replace(/<!-- UNIQUE-PROSE-MARKER(.*?)-->[\\s\\S]*?<\\/section>/g, '');
  c = c.replace('UNIQUE-PROSE-MARKER', '');
  
  c = c.trim() + '\\n\\n' + sectionHTML + '\\n';
  
  fs.writeFileSync(fp, c, 'utf-8');
  updated++;
  if(updated % 100 === 0) process.stdout.write(updated + '/' + files.length + '\\n');
}
process.stdout.write('✅ Updatat (V4): ' + updated + ' pagini MDX cu text hiper-personalizat!\\n');
`;

code = code.replace(/\/\/ ── MAIN ─────────────────────────────────────────────────────────[\s\S]*/, newMain);

fs.writeFileSync(path.join(__dirname, 'prose_v4.mjs'), code, 'utf-8');
console.log('Successfully created prose_v4.mjs');
