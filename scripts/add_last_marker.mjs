// add_last_marker.mjs
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const fp = path.join(ROOT, 'src/pages/animatori-petreceri-copii/index.astro');
let c = fs.readFileSync(fp, 'utf-8');
if (c.includes('UNIQUE-PROSE-MARKER')) { process.stdout.write('DEJA ARE MARKER\n'); process.exit(0); }
const section = '\n<!-- UNIQUE-PROSE-MARKER-animatori-petreceri-copii -->\n<section style="padding:2.5rem 0;background:rgba(255,255,255,0.02)"><div class="container" style="max-width:820px"><h2 style="font-size:1.15rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem">SuperParty — standardul de aur al animatorilor din România</h2><p style="color:var(--text-muted);line-height:1.95;font-size:.93rem">SuperParty este singurul furnizor de entertainment pentru copii din România cu contract de garanție scris, transparență totală de prețuri și rating verificat 4.9/5 din 1498 recenzii Google reale. Din 2018, am organizat peste 10.000 de petreceri în București și zona metropolitană Ilfov, cu zero surprize financiare și zero cazuri de animator care a lipsit fără înlocuitor. Totul este documentat, contractualizat și garantat.</p></div></section>';
const ins = c.lastIndexOf('</Layout>');
if (ins === -1) { process.stdout.write('NO </Layout>\n'); process.exit(1); }
c = c.slice(0, ins) + section + '\n\n' + c.slice(ins);
fs.writeFileSync(fp, c, 'utf-8');
process.stdout.write('OK — marker adaugat\n');
