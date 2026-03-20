// third_pass_1500w.mjs — sectiune "Sfaturi practice + Locatii recomandate" pentru paginile inca sub 1500w
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
function getWords(raw) { return raw.replace(/^---[\s\S]*?---/m,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<[^>]+>/g,' ').replace(/[^\wăâîșțĂÂÎȘȚ\s]/g,' ').replace(/\s+/g,' ').trim().split(/\s+/).filter(w=>w.length>=3).length; }

function pass3Section(loc) {
  return `
<!-- EXPAND3-MARKER-${loc.replace(/\s/g,'-')} -->
<section class="extra-section-3" style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1.2rem">Sfaturi practice pentru organizarea petrecerii în ${loc}</h2>
    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">Iată cele mai importante lucruri pe care trebuie să le pregătești înainte de sosirea animatorului SuperParty la petrecerea copilului tău din ${loc}:</p>
    <ul style="color:var(--text-muted);line-height:2.1;padding-left:1.5rem;margin-bottom:1.2rem">
      <li><strong>Spațiu dedicat:</strong> Asigură un spațiu de minimum 12 mp liber (fără mobilă) pentru ca animatorul să poată desfășura jocurile. Dacă ai sală de petreceri, anunță-ne dimensiunile în avans.</li>
      <li><strong>Ora de sosire:</strong> Animatorul sosește cu 15 minute înainte de ora confirmată în contract. Asigură-te că există loc de parcare sau informează-ne cu o zi înainte dacă zona are restricții de parcare.</li>
      <li><strong>Copiii nerăbdători:</strong> Teen-ul sau copiii mai mari pot deveni neatenți după 45 min. Recomandăm să programezi momentele speciale (tort, lumânări) la jumătatea evenimentului, nu la final.</li>
      <li><strong>Aparatul foto/video:</strong> Părinții SuperParty filmează cele mai frumoase momente. Asigură-te că bateria e încărcată! Pachetele Premium și VIP includ fotografii profesionale.</li>
      <li><strong>Surpriza personajului:</strong> Nu spune copilului ce personaj vine — lasă-l să descopere! Reacția de surpriză a copilului la prima vedere a personajului este cel mai frumos moment din petrecere.</li>
      <li><strong>Alergi și restricții:</strong> Dacă vreun copil are alergie la latex (baloane de cauciuc), anunță-ne cu 24h înainte — folosim baloane alternative din folie mylar.</li>
    </ul>
    <h3 style="font-size:1.1rem;font-weight:700;color:var(--text-primary,#fff);margin-bottom:.8rem">Locații recomandate pentru petreceri în ${loc}</h3>
    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">SuperParty organizează petreceri în orice spațiu ești tu — fie că e vorba de acasă, sală de petreceri, restaurant sau parc. La cerere, putem recomanda locații partenere în zona ${loc} cu pachete speciale. Trebuie doar să ne anunți că ești din această zonă la momentul rezervării.</p>
    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">Printre tipurile de locații unde am organizat petreceri memorabile: apartamente (etajele 1-15, tot accesibil cu echipament portabil), vile cu curte (perfect pentru petreceri outdoor vara), restaurante cu sală separată pentru copii, săli de sport și de dansuri reconvertite, parcuri (cu scenă portabilă), grădinițe și after-schooluri (petreceri de final de an).</p>
    <p style="color:var(--text-muted);line-height:1.9">Indiferent de locație, SuperParty se adaptează. Singurul lucru de care avem nevoie este o priză electrică 220V standard pentru mașina de baloane de săpun și pentru echipamentul audio. Rest 100% portabil și independent.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:2rem">
      <a href="tel:+40722744377" style="background:linear-gradient(135deg,#ff6b35,#e85d24);color:#fff;padding:.9rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 Rezervă Acum</a>
      <a href="https://wa.me/40722744377" style="background:#25d366;color:#fff;padding:.9rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>`;
}

const all = collectAll(path.join(ROOT,'src/pages'));
const idx = all.filter(p=>!fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const under = idx.filter(p=>getWords(fs.readFileSync(p.fp,'utf-8'))<1500);
let n=0;
for (const p of under) {
  let c = fs.readFileSync(p.fp,'utf-8');
  if (c.includes('EXPAND3-MARKER')) continue;
  const title=(c.match(/title="([^"]+)"/) ||[])[1]||'';
  const m=title.match(/(?:Animatori Petreceri Copii |Animatori Copii )([^|—]+)/i);
  let loc=m?m[1].trim():(p.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/').replace(/^(petreceri|animatori-copii)\//,'').split('-').map(w=>w.charAt(0).toUpperCase()+w.slice(1)).join(' '));
  const extra=pass3Section(loc);
  const ins=c.lastIndexOf('</Layout>');
  if (ins===-1) continue;
  c=c.slice(0,ins)+extra+'\n\n'+c.slice(ins);
  fs.writeFileSync(p.fp,c,'utf-8');
  n++;
}

const all2=collectAll(path.join(ROOT,'src/pages'));
const idx2=all2.filter(p=>!fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const still=idx2.filter(p=>getWords(fs.readFileSync(p.fp,'utf-8'))<1500);
const over=idx2.filter(p=>getWords(fs.readFileSync(p.fp,'utf-8'))>=1500);
const avg=Math.round(idx2.reduce((a,p)=>a+getWords(fs.readFileSync(p.fp,'utf-8')),0)/idx2.length);
console.log(`Pass 3: ${n} pagini updatate`);
console.log(`✅ Peste 1500w: ${over.length}/${idx2.length}`);
console.log(`⚠️  Sub 1500w: ${still.length}`);
console.log(`📊 Medie: ${avg}w`);
still.forEach(p=>{const w=getWords(fs.readFileSync(p.fp,'utf-8'));console.log(` [${w}w] ${p.rel}`);});
