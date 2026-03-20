// final_full_audit.mjs — unicitate + nota Google-bot simulata pentru toate 144 pagini
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

function collectAll(dir, rel='') {
  const out=[];
  for(const e of fs.readdirSync(dir,{withFileTypes:true})){
    const fp=path.join(dir,e.name), rp=rel?`${rel}/${e.name}`:e.name;
    if(e.isDirectory()) out.push(...collectAll(fp,rp));
    else if(e.name.endsWith('.astro')&&!e.name.includes('[')) out.push({rel:rp,fp});
  }
  return out;
}

// ── EXTRAGERE TEXT VIZIBIL ──────────────────────────────────────
function extractText(raw) {
  return raw
    .replace(/^---[\s\S]*?---/m,'')
    .replace(/<!--[\s\S]*?-->/g,'')
    .replace(/<style[\s\S]*?<\/style>/gi,'')
    .replace(/<script[\s\S]*?<\/script>/gi,'')
    .replace(/style="[^"]*"/g,'').replace(/class="[^"]*"/g,'')
    .replace(/href="[^"]*"/g,'').replace(/src="[^"]*"/g,'')
    .replace(/<[^>]+>/g,' ')
    .replace(/https?:\/\/[^\s]*/g,'')
    .replace(/[^a-zA-Z\u00C0-\u024F\s]/g,' ')
    .replace(/\b\w{1,3}\b/g,' ')
    .replace(/\s+/g,' ').trim().toLowerCase();
}

// ── BIGRAM SIMILARITY ────────────────────────────────────────────
function simBi(a,b) {
  const t=s=>{const w=s.split(/\s+/).filter(x=>x.length>4);const r=new Set();for(let i=0;i<w.length-1;i++)r.add(w[i]+'_'+w[i+1]);return r;};
  const sa=t(a),sb=t(b);if(!sa.size||!sb.size)return 0;
  return Math.round([...sa].filter(x=>sb.has(x)).length/new Set([...sa,...sb]).size*100);
}

// ── GOOGLE BOT SEO SCORE ─────────────────────────────────────────
function seoScore(raw, rel) {
  const issues=[], ok=[];
  let score=100;

  // 1. Title — detecteaza atat title="..." cat si title={`...`} (Astro expressions)
  const title=(raw.match(/title=["']([^"']{10,120})["']/)||[])[1]||
               (raw.match(/title=\{[`'"]([^`'"]{10,120})[`'"]/)||[])[1]||
               (raw.match(/<title[^>]*>([^<]{5,120})<\/title>/i)||[])[1]||'';
  if(!title){issues.push('⛔ Lipseste title'); score-=15;}
  else if(title.length<30){issues.push(`🟡 Title scurt (${title.length} chars)`);score-=5;}
  else ok.push(`✅ Title OK (${title.length} ch): "${title.slice(0,50)}"`);

  // 2. Meta description — detecteaza string si Astro expressions
  const desc=(raw.match(/description=["']([^"']{20,200})["']/)||[])[1]||
              (raw.match(/description=\{[^}]{15,}/)||[])[0]||
              (raw.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']+)["']/i)||[])[1]||'';
  if(!desc){issues.push('⛔ Lipseste meta description');score-=15;}
  else if(desc.length<80){issues.push(`🟡 Description scurta (${desc.length} ch)`);score-=5;}
  else ok.push(`✅ Description OK (${desc.length} ch)`);

  // 3. Canonical — detecteaza canonical="..." si canonical={VAR} (Astro)
  const hasCanonical=/<link[^>]+rel=["']canonical["']/i.test(raw)||/canonical=["'][^"']+["']/i.test(raw)||/canonical=\{/.test(raw)||/const CANONICAL/.test(raw);
  if(!hasCanonical){issues.push('⛔ Lipseste canonical URL');score-=10;}
  else ok.push('✅ Canonical prezent');

  // 4. H1
  const h1s=raw.match(/<h1[^>]*>[\s\S]*?<\/h1>/gi)||[];
  if(h1s.length===0){issues.push('⛔ Lipseste H1');score-=10;}
  else if(h1s.length>1){issues.push(`🟡 ${h1s.length} H1-uri (trebuie 1)`);score-=5;}
  else ok.push('✅ H1 unic prezent');

  // 5. Schema JSON-LD — detecteaza <script type=ld+json>, itemtype= si schema=JSON.stringify in frontmatter
  const hasSchema=/<script[^>]+type=["']application\/ld\+json["']/i.test(raw)||/itemtype=/i.test(raw)||/schema\s*=\s*JSON\.stringify/.test(raw)||/schema=\{schema\}/.test(raw)||/\"@context\"\s*:\s*\"https:\/\/schema\.org/.test(raw);
  if(!hasSchema){issues.push('⛔ Lipseste Schema markup');score-=10;}
  else ok.push('✅ Schema markup prezent');

  // 6. Word count - cuvinte VIZIBILE
  const visibleText = raw
    .replace(/^---[\s\S]*?---/m,'')
    .replace(/<!--[\s\S]*?-->/g,'')
    .replace(/<style[\s\S]*?<\/style>/gi,'')
    .replace(/<script[\s\S]*?<\/script>/gi,'')
    .replace(/<[^>]+>/g,' ')
    .replace(/\s+/g,' ').trim();
  const wordCount=visibleText.split(/\s+/).filter(w=>w.length>2).length;
  if(wordCount<300){issues.push(`⛔ Continut slab (${wordCount} cuvinte)`);score-=15;}
  else if(wordCount<600){issues.push(`🟡 Continut mediu (${wordCount} cuvinte)`);score-=5;}
  else ok.push(`✅ Continut OK (${wordCount} cuvinte)`);

  // 7. Imagini fara alt
  const imgs=raw.match(/<img[^>]+>/gi)||[];
  const noAlt=imgs.filter(img=>!img.includes('alt=')||/alt=["']["']/.test(img));
  if(noAlt.length>0){issues.push(`🟡 ${noAlt.length} imagini fara alt`);score-=3*Math.min(noAlt.length,3);}
  else if(imgs.length>0) ok.push(`✅ Toate ${imgs.length} imagini au alt`);

  // 8. Noindex check
  const noindex=/noindex/.test(raw);
  if(noindex){issues.push('⚠️  Pagina are noindex — nu e indexata de Google');score=0;}

  // 9. Continut unic (proza specifica)
  const hasUniqueProse=/UNIQUE-PROSE-MARKER/.test(raw);
  if(!hasUniqueProse){issues.push('🟡 Fara sectiune proza unica injectata'); score-=5;}
  else ok.push('✅ Proza unica per localitate injectata');

  return {score:Math.max(0,score), issues, ok, wordCount, title, noindex};
}

// ── MAIN ─────────────────────────────────────────────────────────
const all = collectAll(path.join(ROOT,'src/pages'));
const total = all.filter(p=>!p.rel.includes('['));
const indexed = total.filter(p=>!fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const noindexPages = total.filter(p=>fs.readFileSync(p.fp,'utf-8').includes('noindex'));

process.stderr.write(`Total pagini: ${total.length} | Indexate: ${indexed.length} | Noindex: ${noindexPages.length}\n`);
process.stderr.write(`Calculez ${Math.round(indexed.length*(indexed.length-1)/2)} perechi similaritate...\n`);

// Pre-extrage texte
const texts = indexed.map(p=>({rel:p.rel, raw:fs.readFileSync(p.fp,'utf-8'), text:''}));
texts.forEach(p => { p.text = extractText(p.raw); });

// Similaritate
const pairs=[];
for(let i=0;i<texts.length;i++){
  for(let j=i+1;j<texts.length;j++){
    const s=simBi(texts[i].text,texts[j].text);
    if(s>0) pairs.push({a:texts[i].rel,b:texts[j].rel,sim:s});
  }
  if(i%30===0) process.stderr.write(`  ${i}/${texts.length}\n`);
}
pairs.sort((a,b)=>b.sim-a.sim);

const over80=pairs.filter(p=>p.sim>=80);
const over50=pairs.filter(p=>p.sim>=50);
const over30=pairs.filter(p=>p.sim>=30);
const under20=pairs.filter(p=>p.sim<20);
const totalP=pairs.length;

// SEO scoruri
const scores = texts.map(p=>({rel:p.rel, ...seoScore(p.raw,p.rel)}));
scores.sort((a,b)=>a.score-b.score);
const avgScore=Math.round(scores.reduce((a,s)=>a+s.score,0)/scores.length);
const perfect=scores.filter(s=>s.score>=95);
const good=scores.filter(s=>s.score>=80&&s.score<95);
const mid=scores.filter(s=>s.score>=60&&s.score<80);
const bad=scores.filter(s=>s.score<60);

// ── RAPORT ──────────────────────────────────────────────────────
let R='';
R+=`╔══════════════════════════════════════════════════════════════════╗\n`;
R+=`║   AUDIT FINAL COMPLET SUPERPARTY.RO — ${new Date().toISOString().slice(0,10)}              ║\n`;
R+=`║   ${total.length} pagini total | ${indexed.length} indexate | ${noindexPages.length} noindex               ║\n`;
R+=`╚══════════════════════════════════════════════════════════════════╝\n\n`;

// === SECTIUNEA 1: UNICITATE ===
R+=`╔══════════════════════════════════════════════════════════════════╗\n`;
R+=`║   A. AUDIT UNICITATE CONTINUT                                    ║\n`;
R+=`╚══════════════════════════════════════════════════════════════════╝\n`;
R+=`Total perechi analizate: ${totalP}\n\n`;

const bar=(n,t,w=25)=>'█'.repeat(Math.max(0,Math.round(n/t*w))).padEnd(w);
R+=`⛔ DUPLICATE ≥80%:    ${String(over80.length).padStart(5)} [${bar(over80.length,totalP)}] ${Math.round(over80.length/totalP*100)}%\n`;
R+=`🔴 Similare 50-79%:  ${String(over50.length-over80.length).padStart(5)} [${bar(over50.length-over80.length,totalP)}] ${Math.round((over50.length-over80.length)/totalP*100)}%\n`;
R+=`🟡 Partial 30-49%:   ${String(over30.length-over50.length).padStart(5)} [${bar(over30.length-over50.length,totalP)}] ${Math.round((over30.length-over50.length)/totalP*100)}%\n`;
R+=`✅ UNICE <20%:        ${String(under20.length).padStart(5)} [${bar(under20.length,totalP)}] ${Math.round(under20.length/totalP*100)}%\n\n`;

if(over80.length===0){
  R+=`🎉 ZERO perechi cu continut duplicat (>80%)! Toate paginile au continut unic.\n\n`;
} else {
  R+=`⚠️  Top perechi duplicate:\n`;
  for(const p of over80.slice(0,15)){
    const a=p.a.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/');
    const b=p.b.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/');
    R+=`  ⛔ ${p.sim}%  ${a.substring(0,38).padEnd(38)} ↔ ${b}\n`;
  }
  R+=`\n`;
}

const affectedUniq=new Set(); over50.forEach(p=>{affectedUniq.add(p.a);affectedUniq.add(p.b);});
const uniquePages=indexed.length-affectedUniq.size;
R+=`Pagini cu continut UNIC (fara pereche >50%): ${uniquePages}/${indexed.length} (${Math.round(uniquePages/indexed.length*100)}%)\n`;
R+=`Pagini afectate de similaritate >50%: ${affectedUniq.size}/${indexed.length}\n`;
R+=`Similaritate medie globala: ${Math.round(pairs.reduce((a,p)=>a+p.sim,0)/pairs.length)}%\n\n`;

// === SECTIUNEA 2: NOTA GOOGLE BOT ===
R+=`╔══════════════════════════════════════════════════════════════════╗\n`;
R+=`║   B. NOTA SIMULATA GOOGLE-BOT SEO                               ║\n`;
R+=`╚══════════════════════════════════════════════════════════════════╝\n`;
R+=`Nota medie: ${avgScore}/100\n\n`;
R+=`✅ Excelent (95-100): ${perfect.length} pagini (${Math.round(perfect.length/scores.length*100)}%)\n`;
R+=`🟢 Bun (80-94):       ${good.length} pagini (${Math.round(good.length/scores.length*100)}%)\n`;
R+=`🟡 Mediu (60-79):     ${mid.length} pagini (${Math.round(mid.length/scores.length*100)}%)\n`;
R+=`⛔ Slab (<60):        ${bad.length} pagini (${Math.round(bad.length/scores.length*100)}%)\n\n`;

// Top 15 pagini cu scor mic
if(bad.length>0||mid.length>0){
  R+=`┌─ PAGINI CU SCOR MIC (necesita atentie) ──────────────────────────┐\n`;
  const needsWork=[...bad,...mid.slice(0,5)].slice(0,20);
  for(const s of needsWork){
    const slug=s.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/');
    R+=`${s.score>=80?'🟢':s.score>=60?'🟡':'⛔'} ${String(s.score).padStart(3)}/100  ${slug.substring(0,45).padEnd(45)} (${s.wordCount}w)\n`;
    for(const issue of s.issues.slice(0,3)) R+=`         ${issue}\n`;
  }
  R+=`\n`;
}

// Top 10 pagini bune
R+=`┌─ TOP 10 PAGINI CU SCOR MAXIM ─────────────────────────────────┐\n`;
for(const s of [...scores].sort((a,b)=>b.score-a.score).slice(0,10)){
  const slug=s.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/');
  R+=`✅ ${s.score}/100  ${slug.substring(0,45).padEnd(45)} (${s.wordCount}w)\n`;
}
R+=`\n`;

// Probleme sistemice
const allIssues={};
scores.forEach(s=>s.issues.forEach(i=>{const k=i.slice(0,35);allIssues[k]=(allIssues[k]||0)+1;}));
R+=`┌─ PROBLEME SISTEMICE (frecventa pe site) ──────────────────────────┐\n`;
Object.entries(allIssues).sort((a,b)=>b[1]-a[1]).forEach(([k,v])=>{
  R+=`  ${String(v).padStart(3)}x  ${k}\n`;
});
R+=`\n`;

// === CONCLUZIE ===
R+=`╔══════════════════════════════════════════════════════════════════╗\n`;
R+=`║   CONCLUZIE FINALA                                               ║\n`;
R+=`╚══════════════════════════════════════════════════════════════════╝\n`;
R+=`Nota SEO medie simulata (Google-bot): ${avgScore}/100\n`;
R+=`Perechi duplicate (>80%):             ${over80.length}\n`;
R+=`% pagini cu continut unic:            ${Math.round(uniquePages/indexed.length*100)}%\n`;
R+=over80.length===0?`✅ SITE OK — Zero continut duplicat detectat!\n`:`⚠️  ${over80.length} perechi duplicate necesita rezolvare.\n`;
R+=avgScore>=90?`✅ NOTA SEO BUNA — Site-ul este bine optimizat pentru Google.\n`:
   avgScore>=80?`🟡 NOTA SEO MEDIE — Imbunatatiri recomandate.\n`:`⛔ NOTA SEO SLABA — Necesita interventie urgenta.\n`;

const outPath=path.join(ROOT,'scripts/final_full_audit_report.txt');
fs.writeFileSync(outPath,R,'utf-8');
process.stdout.write(R);
process.stderr.write(`\n✅ Raport salvat: scripts/final_full_audit_report.txt\n`);
