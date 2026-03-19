// quick_sim_check.mjs
import { readFileSync } from 'fs';
function getText(fp) {
  let c = readFileSync(fp,'utf-8');
  c = c.replace(/---[\s\S]*?---/,'').replace(/<style[\s\S]*?<\/style>/gi,' ').replace(/<[^>]+>/g,' ');
  return c.replace(/\s+/g,' ').trim().toLowerCase();
}
function jaccard(a,b) {
  const sA=new Set(a.split(/\s+/).filter(w=>w.length>=6));
  const sB=new Set(b.split(/\s+/).filter(w=>w.length>=6));
  if(!sA.size||!sB.size) return 0;
  return [...sA].filter(x=>sB.has(x)).length/new Set([...sA,...sB]).size;
}
const pairs=[
  ['calarasi','giurgiu'],['bucuresti','giurgiu'],['calarasi','bucuresti'],
  ['sector-1','sector-2'],['sector-1','sector-3'],['sector-2','sector-4'],
  ['otopeni','voluntari'],['aviatiei','berceni'],['titan','crangasi'],
  ['floreasca','dorobanti'],['ilfov','buftea'],['chiajna','bragadiru']
];
for(const [a,b] of pairs) {
  try {
    const tA=getText('src/pages/petreceri/'+a+'.astro');
    const tB=getText('src/pages/petreceri/'+b+'.astro');
    const s=jaccard(tA,tB);
    console.log((s>=0.2?'❌':'✅'),(s*100).toFixed(1).padStart(5)+'%  '+a+' <-> '+b);
  } catch(e){console.log('ERR '+a+'/'+b+': '+e.message);}
}
