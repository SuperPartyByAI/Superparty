// find_remaining_issues.mjs
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

const noProse=[], shortWC=[], shortDesc=[];

for(const p of indexed) {
  const c = fs.readFileSync(p.fp,'utf-8');
  const wc = c.replace(/<[^>]+>/g,' ').replace(/^---[\s\S]*?---/m,'').split(/\s+/).filter(w=>w.length>2).length;
  
  // description length
  const dm = c.match(/description="([^"]{1,300})"/) || c.match(/description='([^']{1,300})'/) || [];
  const descLen = (dm[1]||'').length;
  
  if(!c.includes('UNIQUE-PROSE-MARKER')) noProse.push({rel:p.rel, wc});
  if(wc < 600) shortWC.push({rel:p.rel, wc});
  if(descLen > 0 && descLen < 80) shortDesc.push({rel:p.rel, desc:(dm[1]||'').slice(0,60), len:descLen});
}

process.stdout.write(`FARA PROZA UNICA (${noProse.length}):\n`);
noProse.forEach(p=>process.stdout.write(` - ${p.rel} (${p.wc}w)\n`));
process.stdout.write(`\nCONTINUT SUB 600 (${shortWC.length}):\n`);
shortWC.forEach(p=>process.stdout.write(` - ${p.rel} -> ${p.wc}w\n`));
process.stdout.write(`\nDESCRIPTION SCURTA (${shortDesc.length}):\n`);
shortDesc.forEach(p=>process.stdout.write(` - ${p.rel} len:${p.len} => ${p.desc}\n`));
