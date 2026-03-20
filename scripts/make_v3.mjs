import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

let code = fs.readFileSync(path.join(__dirname, 'prose_v2.mjs'), 'utf-8');

const mainLogic = `// ── MAIN ─────────────────────────────────────────────────────────
const dir = path.join(ROOT, 'src/content/seo-articles');
const files = fs.readdirSync(dir).filter(f => f.endsWith('.mdx'));

let updated = 0;
for(const f of files) {
  const fp = path.join(dir, f);
  let c = fs.readFileSync(fp, 'utf-8');
  
  if (!c.includes('UNIQUE-PROSE-MARKER')) continue;
  
  const titleMatch = c.match(/title:\\s*"([^"]+)"/);
  const title = titleMatch ? titleMatch[1] : '';
  const locMatch = title.match(/Copii (.*?) \\|/i);
  let loc = locMatch ? locMatch[1].trim() : f.replace('.mdx', '');
  loc = loc.replace('București – ', '').replace('Bucuresti - ', '');
  
  let slugKey = loc.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  if ((slugKey === 'bucuresti' || slugKey === 'sector') && f.includes('sector-')) {
     const sm = f.match(/(sector-[1-6])/);
     if (sm) slugKey = sm[1];
  }
  
  const d = L[slugKey] || {jud:'Ilfov',km:25,dn:'drum local',pop:5000,regiune:'zona metropolitana',vecin:'localitati ilfovene',caract:'comunitate din aria metropolitana Bucuresti',topChar:'Spiderman',tip:'com'};
  
  const prose = genProse(f, loc, d);
  const finalProse = prose.split('\\n\\n').map(pr => pr.trim() + '\\n\\n').join('');
  
  c = c.replace('UNIQUE-PROSE-MARKER', finalProse.trim());
  fs.writeFileSync(fp, c, 'utf-8');
  updated++;
  if(updated % 100 === 0) process.stdout.write(updated + '/' + files.length + '\\n');
}
process.stdout.write('✅ Updatat: ' + updated + ' pagini MDX cu 5 stiluri unice\\n');
`;

code = code.replace(/\/\/ ── MAIN ─────────────────────────────────────────────────────────[\s\S]*/, mainLogic);

fs.writeFileSync(path.join(__dirname, 'prose_v3.mjs'), code, 'utf-8');
console.log('Successfully created prose_v3.mjs');
