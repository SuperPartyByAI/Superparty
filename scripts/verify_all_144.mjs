import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');

function collect(dir, rel='') {
  const out=[];
  for(const e of fs.readdirSync(dir,{withFileTypes:true})){
    const fp=path.join(dir,e.name), rp=rel?`${rel}/${e.name}`:e.name;
    if(e.isDirectory()) out.push(...collect(fp,rp));
    else if(e.name.endsWith('.astro')&&!e.name.includes('[')) out.push({rel:rp,fp});
  }
  return out;
}

const all = collect(path.join(ROOT,'src/pages'));
const indexed = all.filter(p=>!fs.readFileSync(p.fp,'utf-8').includes('noindex'));

let okSchema=0, noSchema=[], okCanon=0, noCanon=[], okProza=0, noProza=[];

for(const p of indexed){
  const c = fs.readFileSync(p.fp,'utf-8');
  const hasSchema = /application\/ld\+json/i.test(c) || /schema\s*=\s*JSON\.stringify/.test(c) || /"@context"\s*:/.test(c) || /const\s+combinedSchema/.test(c);
  const hasCanon = /canonical/.test(c);
  const hasProza = /UNIQUE-PROSE-MARKER/.test(c);
  
  if(hasSchema) okSchema++; else noSchema.push(p.rel);
  if(hasCanon) okCanon++; else noCanon.push(p.rel);
  if(hasProza) okProza++; else noProza.push(p.rel);
}

process.stdout.write(`\n╔══════════════════════════════════════════════════╗\n`);
process.stdout.write(`║  VERIFICARE COMPLETA TOATE ${indexed.length} PAGINI INDEXATE  ║\n`);
process.stdout.write(`╚══════════════════════════════════════════════════╝\n\n`);
process.stdout.write(`Schema JSON-LD:  ${okSchema}/${indexed.length} pagini ✅  |  Lipsa: ${noSchema.length}\n`);
process.stdout.write(`Canonical URL:   ${okCanon}/${indexed.length} pagini ✅  |  Lipsa: ${noCanon.length}\n`);
process.stdout.write(`Proza Unica:     ${okProza}/${indexed.length} pagini ✅  |  Lipsa: ${noProza.length}\n`);
process.stdout.write(`\n`);

if(noSchema.length) { process.stdout.write(`⛔ Fara schema:\n`); noSchema.forEach(r=>process.stdout.write(`  - ${r}\n`)); }
if(noCanon.length)  { process.stdout.write(`⛔ Fara canonical:\n`); noCanon.forEach(r=>process.stdout.write(`  - ${r}\n`)); }
if(noProza.length)  { process.stdout.write(`⛔ Fara proza:\n`); noProza.slice(0,10).forEach(r=>process.stdout.write(`  - ${r}\n`)); if(noProza.length>10) process.stdout.write(`  ... si ${noProza.length-10} altele\n`); }

if(!noSchema.length && !noCanon.length && !noProza.length){
  process.stdout.write(`\n🎉 PERFECT — Toate ${indexed.length} pagini au schema + canonical + proza unica!\n`);
} else {
  process.stdout.write(`\n⚠️  ${noSchema.length+noCanon.length+noProza.length} probleme detectate pe toate paginile\n`);
}
