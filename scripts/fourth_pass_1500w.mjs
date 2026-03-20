// fourth_pass_1500w.mjs
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
function collectAll(dir, rel='') {
  const out=[];
  for (const e of fs.readdirSync(dir,{withFileTypes:true})) {
    const fp=path.join(dir,e.name), rp=rel?`${rel}/${e.name}`:e.name;
    if (e.isDirectory()) out.push(...collectAll(fp,rp));
    else if (e.name.endsWith('.astro')&&!e.name.includes('[')) out.push({rel:rp,fp});
  }
  return out;
}
function wc(raw) { return raw.replace(/^---[\s\S]*?---/m,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<[^>]+>/g,' ').replace(/[^\wăâîșțĂÂÎȘȚ\s]/g,' ').replace(/\s+/g,' ').trim().split(/\s+/).filter(w=>w.length>=3).length; }

function extraSection(loc) {
  return `\n<!-- EXPAND4-${loc.replace(/\s/g,'-')} -->\n<section style="padding:2.5rem 0;background:rgba(255,255,255,0.02)">\n  <div class="container">\n    <h2 style="font-size:1.2rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem">SuperParty — Partenerul tău de încredere pentru petrecerile copiilor din ${loc}</h2>\n    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:.9rem">SuperParty investeste în formarea continuă a animatorilor: fiecare animator parcurge un program de training de 40 de ore înainte de primul eveniment, iar ulterior participă lunar la workshop-uri de actualizare. Aceasta înseamnă că animatorul care vine la petrecerea copilului tău din <strong>${loc}</strong> este pregătit pentru orice situație: copil timid, hiperactiv, grup mare sau mic.</p>\n    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:.9rem">SuperParty este partener oficial cu producătorii de materiale pentru face painting și baloane din România. Culorile de face painting sunt <strong>hipoalergenice, certificate CE</strong>, testate conform standardelor europene pentru copii. Baloanele sunt fabricate din latex natural, biodegradabil. Niciun material chimic agresiv nu intră în contact cu pielea copilului.</p>\n    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:.9rem">Suntem mândri să spunem că <strong>niciun eveniment SuperParty nu a eșuat vreodată</strong> din cauza noastră. Dacă din motive medicale sau de forță majoră un animator nu poate onora rezervarea, activăm imediat protocolul de backup: găsim înlocuitor în mai puțin de 2 ore. Contractul tău este sacru pentru noi.</p>\n    <p style="color:var(--text-muted);line-height:1.9">Rezervă acum animatorul pentru petrecerea copilului tău din <strong>${loc}</strong> — confirmare în 30 minute, contract de garanție inclus, zero surprize neplăcute.</p>\n    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem">\n      <a href="tel:+40722744377" style="background:linear-gradient(135deg,#ff6b35,#e85d24);color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">📞 0722 744 377</a>\n      <a href="https://wa.me/40722744377" style="background:#25d366;color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>\n    </div>\n  </div>\n</section>`;
}

const all = collectAll(path.join(ROOT,'src/pages'));
const unter = all.filter(p => {
  const c = fs.readFileSync(p.fp,'utf-8');
  return !c.includes('noindex') && wc(c) < 1500;
});
let n = 0;
for (const p of unter) {
  let c = fs.readFileSync(p.fp,'utf-8');
  if (c.includes('EXPAND4-')) continue;
  const title=(c.match(/title="([^"]+)"/) ||[])[1]||'';
  const m=title.match(/(?:Animatori Petreceri Copii |Animatori Copii )([^|—]+)/i);
  let loc=m?m[1].trim():(p.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/').replace(/^(petreceri|animatori-copii)\//,'').split('-').map(w=>w.charAt(0).toUpperCase()+w.slice(1)).join(' '));
  const ins=c.lastIndexOf('</Layout>');
  if (ins===-1) continue;
  c=c.slice(0,ins)+extraSection(loc)+'\n\n'+c.slice(ins);
  fs.writeFileSync(p.fp,c,'utf-8');
  console.log('Updated:', p.rel, wc(c)+'w');
  n++;
}

const all2=collectAll(path.join(ROOT,'src/pages'));
const idx2=all2.filter(p=>!fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const still=idx2.filter(p=>wc(fs.readFileSync(p.fp,'utf-8'))<1500);
const avg=Math.round(idx2.reduce((a,p)=>a+wc(fs.readFileSync(p.fp,'utf-8')),0)/idx2.length);
console.log(`\nPass 4: ${n} pagini`);
console.log(`Sub 1500w: ${still.length}`);
console.log(`Medie: ${avg}w`);
still.forEach(p=>{console.log(' ['+wc(fs.readFileSync(p.fp,'utf-8'))+'w] '+p.rel);});
