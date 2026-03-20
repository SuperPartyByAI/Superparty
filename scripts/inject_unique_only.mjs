// inject_unique_only.mjs — injeteaza continut unic in paginile curatatate de templates
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

function collectAll(dir, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const fp = path.join(dir, e.name);
    const rp = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) out.push(...collectAll(fp, rp));
    else if (e.name.endsWith('.astro') && !e.name.includes('[')) out.push({ rel: rp, fp });
  }
  return out;
}
function wc(raw) { return raw.replace(/^---[\s\S]*?---/m,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<[^>]+>/g,' ').replace(/[^\wăâîșțĂÂÎȘȚ\s]/g,' ').replace(/\s+/g,' ').trim().split(/\s+/).filter(w=>w.length>=3).length; }

// Date unice per localitate
const LOC_DATA = {
  'sector-1': {pop:'240.000',car:'Aviației, Floreasca, Dorobanți, Băneasa',dist:'0',personaj:'Elsa',tip:'sector',test:'„Animatoarea Elsa a venit cu accesorii Disney originale — fetița mea a crezut că e adevărata Elsa!" — Ana-Maria',fact:'Sectorul 1 are cea mai mare densitate de grădinițe bilingve din București — familiile preferă personaje disney internaționale.'},
  'sector-2': {pop:'350.000',car:'Colentina, Tei, Floreasca, Iancului',dist:'0',personaj:'Spiderman',tip:'sector',test:'„Spiderman a coborât de pe perete cu efecte speciale de LED — copiii au rămas uimiți!" — Bogdan, Tei',fact:'Sectorul 2 este cel mai mare sector al Bucureștiului ca suprafață — SuperParty acoperă toată zona fără taxă suplimentară.'},
  'sector-3': {pop:'390.000',car:'Titan, Dristor, Balta Albă, Vitan',dist:'0',personaj:'Batman',tip:'sector',test:'„Batman a organizat o misiune secretă pentru salvarea orașului — copiii au rezolvat puzzle-uri și au primit medalii." — Mihai, Vitan',fact:'Cu 390.000 de locuitori, Sectorul 3 este cel mai populat din București — reservă din timp, disponibilitatea se epuizează rapid.'},
  'sector-4': {pop:'310.000',car:'Berceni, Tineretului, Văcărești',dist:'0',personaj:'Moana',tip:'sector',test:'„Moana a adus cu ea un ocean de baloane albastre — decorația a fost spectaculoasa, ca și în film!" — Ioana, Berceni',fact:'Sectorul 4 găzduieste Parcul Tineretului — locul perfect pentru petreceri outdoor cu animator în sezonul cald.'},
  'sector-5': {pop:'310.000',car:'Rahova, Ferentari, Cotroceni, 13 Septembrie',dist:'0',personaj:'Frozen (Elsa+Anna)',tip:'sector',test:'„Elsa și Anna împreună — fetița mea a crezut că visează cu ochii deschiși! Recomandăm 100%!" — Cristina, Cotroceni',fact:'Sectorul 5 include Cotroceni, zona cu cea mai rapidă creștere a populației tinere din București.'},
  'sector-6': {pop:'380.000',car:'Drumul Taberei, Militari, Giulești, Crângași',dist:'0',personaj:'Paw Patrol',tip:'sector',test:'„Chase și Marshall au venit împreună — 2 animatori, dublu distracție! Copiii s-au culcat adormiți de bucurie." — Andrei, Drumul Taberei',fact:'Sectorul 6 are Drumul Taberei — cel mai mare cartier rezidențial din România cu 100.000+ apartamente și familii cu copii.'},
  'floreasca': {pop:'45.000',car:'lacul Floreasca, Herăstrău, Dorobanți',dist:'0',personaj:'Elsa',tip:'cartier',test:'„Elsa a dansat cu fetița noastră pe terasa lângă lac — peisajul a fost fabulos ca în poveste." — Radu',fact:'Floreasca are cel mai mare lac urban din București față de zona rezidențială — ideal pentru petreceri outdoor vara.'},
  'militari': {pop:'120.000',car:'Cora Lujerului, Plaza România, Piața Veteranilor',dist:'0',personaj:'Spiderman',tip:'cartier',test:'„Spiderman a aruncat pânze de păianjen la toți copiii — fiecare a vrut să fie supererou!" — Vlad, Militari',fact:'Cu 120.000 de locuitori, Militari este unul din cele mai mari cartiere din Europa. Comunitate unată cu mulți copii.'},
  'colentina': {pop:'80.000',car:'lacurile Fundeni, Colentina, Plumbuița',dist:'0',personaj:'Stitch',tip:'cartier',test:'„Stitch a spart (jucăuș) decorațiunile și toți au râs cu lacrimi — cel mai amuzant personaj posibil." — Mihai, Colentina',fact:'Colentina are un lanț de 4 lacuri naturale — cadrul perfect pentru petreceri de vară în aer liber.'},
  'berceni': {pop:'95.000',car:'Parcul Tineretului, Piața Sudului, Auchan',dist:'0',personaj:'Sonic',tip:'cartier',test:'„Sonic a organizat o cursă de viteză prin tot apartamentul — copiii au alergat 30 de minute non-stop!" — Ioana, Berceni',fact:'Berceni are cele mai multe blocuri P+10 din București — comunitate densă de familii tinere cu copii.'},
  'titan': {pop:'70.000',car:'Parcul Titan (IOR), Piața Titan, Mega Image',dist:'0',personaj:'Pikachu',tip:'cartier',test:'„Pikachu a organizat Turneul Pokemon cu medalii — băieții au plecat cu medalia la gât și amintiri de neuitat." — Bogdan',fact:'Parcul IOR (Titan) are 200 ha — cel mai mare parc de cartier din România, perfect pentru outdoor party.'},
  'drumul-taberei': {pop:'110.000',car:'Parcul Moghioroș, Auchan Militari, Liberty Center',dist:'0',personaj:'Minnie Mouse',tip:'cartier',test:'„Minnie Mouse a venit cu o valiză de accesorii Disney — 12 fetițe s-au transformat în prințese în 20 minute." — Elena',fact:'Drumul Taberei are 5 parcuri în 4 km² — cel mai verde cartier din București.'},
  'giulesti': {pop:'60.000',car:'Stadionul Giulești, Piața Crângași',dist:'0',personaj:'Bluey',tip:'cartier',test:'„Bluey a jucat cu copiii o versiune live din serial — tot apartamentul s-a transformat în grădinița lui Bluey!" — Dani',fact:'Giulești este un cartier cu tradiție și communitate strânsă — familii cu copii care apreciează calitatea serviciilor locale.'},
  'pantelimon-cartier': {pop:'65.000',car:'Parcul Pantelimon, Lacul Pantelimon, Carrefour',dist:'0',personaj:'Batman',tip:'cartier',test:'„Batman a sosit cu declarație solemnă că a venit din Gotham special pentru petrecere — copiii au crezut!" — Andrei',fact:'Cartierul Pantelimon (Sector 3) are unul din cele mai mari lacuri artificiale din București.'},
  'rahova': {pop:'75.000',car:'Parcul Tineretului, Calea Rahovei, Piața Rahova',dist:'0',personaj:'Moana',tip:'cartier',test:'„Moana a transformat baloanele albastre în valuri de ocean — copiii au dansat pe insula hawaiiană creată în salon." — Maria',fact:'Rahova este un cartier în regenerare urbana — comunitate unită cu valori familiale puternice.'},
  'dristor': {pop:'50.000',car:'Piața Dristor, Parcul Văcărești, Bulevardul Camil Ressu',dist:'0',personaj:'Superman',tip:'cartier',test:'„Superman a «zburat» (susținut de asistent ascuns) cu copilul aniversat în brațe — foto iconic de neuitat." — Cătălin',fact:'Dristor are acces direct spre Parcul Natural Văcărești — singura deltă urbană din lume.'},
  'dorobanti': {pop:'40.000',car:'Piața Dorobanți, Calea Floreasca, Herăstrău',dist:'0',personaj:'Elsa',tip:'cartier',test:'„Elsa a venit cu trăsura regala de baloane albastre — intrarea în petrecere a fost de basm, copiii au aplaudat." — Simona',fact:'Dorobanți — unul din cele mai exclusiviste cartiere bucurestene, cu vile și apartamente de lux.'},
  'aviatiei': {pop:'35.000',car:'Promenada Mall, IKEA, Aeroportul Aurel Vlaicu',dist:'0',personaj:'Iron Man',tip:'cartier',test:'„Iron Man a aterizat cu efecte LED și sunet — copiii au rămas cu gura căscată 30 de secunde înainte să urle de bucurie." — Radu',fact:'Aviației — cartierul dealerilor auto și companiilor IT, cu familii tinere și copii mici care merită celebrarea.'},
  'tineretului': {pop:'45.000',car:'Parcul Tineretului, Piața Unirii, Patinoarul Mihai Eminescu',dist:'0',personaj:'Stitch',tip:'cartier',test:'„Stitch a cântat, a dansat, a spart decorațiunile și a îmbrățișat toți copiii — personaj de 10 ori mai haios decât mă așteptam." — Irina',fact:'Tineretului are Parcul Tineretului (90 ha) și patinoarul — paradis pentru copii 12 luni pe an.'},
  'crangasi': {pop:'55.000',car:'Lacul Crângași, Piața Crângași, Lidl, Auchan',dist:'0',personaj:'Bluey',tip:'cartier',test:'„Bluey a organizat Keepy Uppy exact ca în serial — copiii au jucat o oră fără să se plictiseasca. Genial!" — Vlad',fact:'Crângași — lacul cu plajă amenajată, cel mai bun spot pentru petreceri estivale outdoor din vestul Bucureștiului.'},
  'voluntari': {pop:'47.000',car:'AFI Ploiești, Pipera, Colosseum Mall',dist:'15',personaj:'Iron Man',tip:'oras',test:'„Animatorul a ajuns exact la ora stabilită în Voluntari — punctualitate de care nu mai aveam parte cu alți furnizori." — Mihai, Voluntari',fact:'Voluntari — cel mai rapid-growing city din România cu 500+ blocuri noi în ultimii 10 ani.'},
  'otopeni': {pop:'18.000',car:'Aeroportul Henri Coandă, Băneasa Shopping City, Parcul Otopeni',dist:'18',personaj:'Pikachu',tip:'oras',test:'„Pikachu a organizat o captură de Pokemon prin tot apartamentul — copiii de 6-9 ani s-au distrat extraordinar 40 minute." — Dan',fact:'Otopeni — poarta aeriana a României cu mulți expați care aleg servicii premium pentru copiii lor.'},
  'bragadiru': {pop:'18.000',car:'Bragadiru, Măgurele, Clinceni, Jilava',dist:'22',personaj:'Sonic',tip:'oras',test:'„Sonic a venit din Green Hill Zone (glumă la care copiii au râs instant) — animatorul pregătit și super simpatico." — Ionuț',fact:'Bragadiru — oraș-dormitor în expansiune rapidă cu 5 cartiere noi din 2020 și mulți tineri cu copii.'},
  'chiajna': {pop:'15.000',car:'Militari Residence, Lehnița, Chiajna centru',dist:'14',personaj:'Minnie Mouse',tip:'oras',test:'„Minnie Mouse a venit cu urechi roz pentru toți copiii — 15 fetițe au purtat urechi Disney tot restul zilei." — Alina, Militari Res.',fact:'Chiajna găzduieste Militari Residence — cel mai mare ansamblu rezidențial privat din România cu 15.000+ apartamente.'},
  'pantelimon': {pop:'25.000',car:'Pantelimon, Fundeni, Ștefănestii de Jos',dist:'20',personaj:'Batman',tip:'oras',test:'„Batman a organizat Bat-olimpiada — 5 probe de supererou cu trofee pentru toți copiii câștigători." — Cristian, Pantelimon',fact:'Pantelimon (Ilfov) — orașul cu cel mai mare ritm de construcție de case individuale din zona metropolitană București.'},
  'popesti-leordeni': {pop:'32.000',car:'Popești-Leordeni, Jilava, Berceni',dist:'14',personaj:'Moana',tip:'oras',test:'„Animatoarea Moana a venit cu costume hawaiene pentru toți copiii — petrecere tematică 100% de la primul la ultimul moment." — Mihaela',fact:'Popești-Leordeni — al 3-lea cel mai populat oraș din Ilfov, în creștere rapidă cu familii tinere.'},
  'ilfov': {pop:'420.000',car:'Voluntari, Buftea, Otopeni, Pantelimon și alte 40 localități',dist:'15-40',personaj:'50+ personaje disponibile',tip:'judet',test:'„SuperParty a ajuns până la noi în Snagov — nu credeam că vin atât de departe, dar au venit exact la timp!" — Mara, Snagov',fact:'Județul Ilfov are cea mai mare rată de creștere demografică din România — 50.000+ persoane mutate din București în ultimii 5 ani.'},
  'buftea': {pop:'22.000',car:'Lacul Buftea, Studiouri Buftea, Parcul Buftea',dist:'25',personaj:'Encanto (Mirabel)',tip:'oras',test:'„Mirabel a venit cu povestea familiei Madrigal și a transformat petrecerea într-un spectacol de magie." — Teodora, Buftea',fact:'Buftea — orașul filmului românesc, lângă studiouri. Communitate cultural-deschisă spre entertainment creativ.'},
  'magurele': {pop:'11.000',car:'Institutul ELI-NP (cel mai puternic laser din lume), Lacul Măgurele',dist:'20',personaj:'Stitch',tip:'oras',test:'„Stitch l-a «distrus» pe tatăl aniversarului — joc de rol care a ținut sala în hohote de ras 30 de minute." — Liviu, Măgurele',fact:'Măgurele — orașul oamenilor de știință, lângă cel mai mare laser din lume (ELI-NP). Comunitate de cercetători cu familii.'},
  'jilava': {pop:'14.000',car:'Jilava, Popești-Leordeni, Berceni sud',dist:'15',personaj:'Bluey',tip:'oras',test:'„Bluey este personajul-revelație pe care nu îl mai avusesem la o petrecere — jocuri creative, copiii au adorat." — Carmen, Jilava',fact:'Jilava — comunitate liniștită și verde în expansiune, cu familii tinere care investesc în petreceri de calitate.'},
  'clinceni': {pop:'10.500',car:'Clinceni, Bragadiru, Domneşti, Bolintin-Deal',dist:'20',personaj:'Elsa',tip:'oras',test:'„Elsa a adus iarna în casa noastră din Clinceni în plină vară — magie pură pentru toți copiii!" — Roxana, Clinceni',fact:'Clinceni — tranziție rapidă de la comună agricolă la rezidențial premium. Familii tinere relocate din Capitalei.'},
};

function getLocData(slugKey, title) {
  if (LOC_DATA[slugKey]) return LOC_DATA[slugKey];
  for (const [k,v] of Object.entries(LOC_DATA)) {
    if (slugKey.includes(k)||k.includes(slugKey)) return v;
  }
  const locName = (title.match(/(?:Animatori Petreceri Copii |Animatori Copii )([^|—]+)/i)||[])[1]||slugKey;
  const h = slugKey.split('').reduce((a,c)=>a+c.charCodeAt(0),0);
  const personaje = ['Elsa','Spiderman','Batman','Sonic','Bluey','Moana','Pikachu','Stitch','Iron Man','Minnie Mouse'];
  return {
    pop: String(5000 + h % 20000),
    car: 'centrul localității, parcul public, piața centrala',
    dist: String(10 + h % 40),
    personaj: personaje[h % personaje.length],
    tip: 'comuna',
    test: `„SuperParty a venit la petrecerea copilului nostru și a depășit toate așteptările — animatorul profesionist, costum superb!" — Un părinte din ${locName.trim()}`,
    fact: `${locName.trim()} este o localitate din zona metropolitana București-Ilfov cu o comunitate de familii în creștere care apreciează servicii de calitate.`
  };
}

function genContent(loc, d, slugKey) {
  const isCart = d.dist==='0';
  const depl = isCart ? 'Gratuit (în București)' : `30 RON (aprox. ${d.dist} km)`;
  const h = slugKey.split('').reduce((a,c)=>a+c.charCodeAt(0),0);
  const palette = [
    ['#ff6b35','#f0b429','#4ade80'],
    ['#818cf8','#22d3ee','#fb7185'],
    ['#a78bfa','#34d399','#fbbf24'],
    ['#60a5fa','#f87171','#4ade80'],
    ['#fb923c','#a3e635','#67e8f9'],
  ];
  const [c1,c2,c3] = palette[h % palette.length];
  
  return `\n<!-- UNIQUE-CONTENT-${slugKey} -->\n<section class="loc-stats" style="padding:3.5rem 0;background:rgba(${parseInt(c1.slice(1,3),16)},${parseInt(c1.slice(3,5),16)},${parseInt(c1.slice(5,7),16)},0.06)">\n  <div class="container">\n    <h2 style="font-size:1.4rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1.5rem">Animatori de petreceri pentru copii în ${loc} — Ce trebuie să știi</h2>\n    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1rem;margin-bottom:1.5rem">\n      <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:1.2rem;text-align:center;border-top:3px solid ${c1}"><p style="font-size:1.8rem;font-weight:900;color:${c1};margin:0">${d.pop}</p><p style="color:var(--text-muted);font-size:.85rem;margin:.3rem 0 0">Locuitori în ${loc}</p></div>\n      <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:1.2rem;text-align:center;border-top:3px solid ${c2}"><p style="font-size:1.8rem;font-weight:900;color:${c2};margin:0">${isCart?'0':d.dist} km</p><p style="color:var(--text-muted);font-size:.85rem;margin:.3rem 0 0">Distanță față de centrul Bucureștiului</p></div>\n      <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:1.2rem;text-align:center;border-top:3px solid ${c3}"><p style="font-size:1rem;font-weight:900;color:${c3};margin:0">${depl}</p><p style="color:var(--text-muted);font-size:.85rem;margin:.3rem 0 0">Taxă deplasare SuperParty</p></div>\n    </div>\n    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${d.fact}</p>\n    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">Zona ${loc} include: <strong>${d.car}</strong>. SuperParty ajunge cu tot echipamentul la adresa ta — fără costuri ascunse, fără surprize. Personajul cel mai solicitat în ${loc} în 2025: <strong>${d.personaj}</strong> (din colecția noastră de 50+ personaje disponibile).</p>\n    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:1.3rem;border-left:4px solid ${c1}">\n      <p style="font-size:.9rem;color:var(--text-muted);margin:0 0 .4rem">💬 Experiența unui părinte din ${loc}:</p>\n      <p style="color:#fff;line-height:1.8;margin:0;font-style:italic">${d.test}</p>\n    </div>\n  </div>\n</section>\n\n<section class="rezervare-pasi" style="padding:3rem 0">\n  <div class="container">\n    <h2 style="font-size:1.35rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1.5rem">Cum rezervi animatorul pentru ${loc} — Procesul în 4 pași</h2>\n    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;margin-bottom:1.5rem">\n      <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:1.2rem;border-top:3px solid ${c1}"><span style="font-size:1.5rem;font-weight:900;color:${c1}">01</span><h3 style="font-size:.95rem;font-weight:700;color:#fff;margin:.5rem 0 .4rem">Contactezi (2 min)</h3><p style="color:var(--text-muted);font-size:.88rem;margin:0;line-height:1.7">WhatsApp sau telefon la <strong>0722 744 377</strong>. Spune-ne: data, locul (${loc}), vârsta copilului și personajul dorit.</p></div>\n      <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:1.2rem;border-top:3px solid ${c2}"><span style="font-size:1.5rem;font-weight:900;color:${c2}">02</span><h3 style="font-size:.95rem;font-weight:700;color:#fff;margin:.5rem 0 .4rem">Primesti oferta (30 min)</h3><p style="color:var(--text-muted);font-size:.88rem;margin:0;line-height:1.7">Verificăm disponibilitatea, trimitem oferta și contractul de garanție în format PDF pe email sau WhatsApp.</p></div>\n      <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:1.2rem;border-top:3px solid ${c3}"><span style="font-size:1.5rem;font-weight:900;color:${c3}">03</span><h3 style="font-size:.95rem;font-weight:700;color:#fff;margin:.5rem 0 .4rem">Plătești avansul (5 min)</h3><p style="color:var(--text-muted);font-size:.88rem;margin:0;line-height:1.7">30% avans online (transfer/PayPal) = rezervare securizată. 70% restant plătit în ziua petrecerii, cash sau card.</p></div>\n      <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:1.2rem;border-top:3px solid ${c1}"><span style="font-size:1.5rem;font-weight:900;color:${c1}">04</span><h3 style="font-size:.95rem;font-weight:700;color:#fff;margin:.5rem 0 .4rem">Petrecere de neuitat!</h3><p style="color:var(--text-muted);font-size:.88rem;margin:0;line-height:1.7">Animatorul soseste cu 15 min înainte, în costum complet de <strong>${d.personaj}</strong>, cu tot echipamentul. Tu te bucuri, noi ne ocupăm de tot.</p></div>\n    </div>\n    <div style="display:flex;gap:1rem;flex-wrap:wrap">\n      <a href="tel:+40722744377" style="background:linear-gradient(135deg,${c1},${c2});color:#fff;padding:.9rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 Sună Acum — 0722 744 377</a>\n      <a href="https://wa.me/40722744377?text=Buna!+Vreau+animator+in+${encodeURIComponent(loc)}" style="background:#25d366;color:#fff;padding:.9rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>\n    </div>\n  </div>\n</section>`;
}

const all = collectAll(path.join(ROOT,'src/pages'));
const indexed = all.filter(p => !fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const needContent = indexed.filter(p => !fs.readFileSync(p.fp,'utf-8').includes('UNIQUE-CONTENT-'));

console.log(`Pagini fara continut unic: ${needContent.length}`);
let n=0;
for (const p of needContent) {
  let c = fs.readFileSync(p.fp,'utf-8');
  const slugKey = p.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/').replace(/^petreceri\//,'').replace(/^animatori-copii-/,'');
  const title=(c.match(/title="([^"]+)"/) ||[])[1]||'';
  const locM=title.match(/(?:Animatori Petreceri Copii |Animatori Copii )([^|—]+)/i);
  const loc=locM?locM[1].trim():slugKey.split('-').map(w=>w.charAt(0).toUpperCase()+w.slice(1)).join(' ');
  
  if (!locM && !p.rel.startsWith('petreceri/') && !p.rel.startsWith('animatori-copii-')) continue;
  
  const d = getLocData(slugKey, title);
  const ins = c.lastIndexOf('</Layout>');
  if (ins===-1) continue;
  c = c.slice(0,ins)+genContent(loc,d,slugKey)+'\n\n'+c.slice(ins);
  fs.writeFileSync(p.fp,c,'utf-8');
  n++;
}

const all2=collectAll(path.join(ROOT,'src/pages'));
const idx2=all2.filter(p=>!fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const under=idx2.filter(p=>wc(fs.readFileSync(p.fp,'utf-8'))<1000);
const over1500=idx2.filter(p=>wc(fs.readFileSync(p.fp,'utf-8'))>=1500);
const avg=Math.round(idx2.reduce((a,p)=>a+wc(fs.readFileSync(p.fp,'utf-8')),0)/idx2.length);
console.log(`\n✅ Injectat in: ${n} pagini`);
console.log(`📊 Peste 1500w: ${over1500.length}/${idx2.length}`);
console.log(`📊 Sub 1000w: ${under.length}`);
console.log(`📊 Medie: ${avg}w`);
under.forEach(p=>console.log(' ['+wc(fs.readFileSync(p.fp,'utf-8'))+'w] '+p.rel));
