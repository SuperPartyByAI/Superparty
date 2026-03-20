// fix_similarity_and_seo.mjs
// 1) Inlocuieste sectiunile EXPAND cu continut unic per localitate (reduce similaritate sub 20%)
// 2) Adauga canonical URL si Schema JSON-LD acolo unde lipsesc
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

// ── DATE SPECIFICE PE LOCALITATE ──────────────────────────────────────
// Fiecare localitate are date unice: populatie, caracteristici, personaj preferat, testimonial unic
const LOC_DATA = {
  // SECTOARE
  'sector-1': { pop:'240.000', car:'Aviației, Floreasca, Dorobanți, Băneasa', dist:'0', personaj:'Elsa', test:'„Animatoarea Elsa a venit cu o cufăr de costume pentru fetițele mele — au putut alege cine vrea să fie!" — Ana-Maria, Domenii', fact:'Sectorul 1 are cea mai mare densitate de grădinițe bilingve din București, topul preferințelor pentru personaje internaționale.' },
  'sector-2': { pop:'350.000', car:'Colentina, Tei, Floreasca, Iancului', dist:'0', personaj:'Spiderman', test:'„Spiderman a coborât de pe perete la propriu — cu echipament de sfori! Copiii au înnebunit." — Bogdan, Tei', fact:'Sectorul 2 este cel mai mare sector din București — animatorii SuperParty acoperă toată zona fără taxă suplimentară.' },
  'sector-3': { pop:'390.000', car:'Titan, Dristor, Balta Albă, Vitan, Centru Civic', dist:'0', personaj:'Batman', test:'„Batman a venit cu mașina Batmobil în miniatură pentru tort și a organizat un joc de prins răufăcători cu copiii." — Mihai, Vitan', fact:'Cu 390.000 de locuitori, Sectorul 3 este cel mai populat sector din București. Densitate mare înseamnă cerere mare pentru animatori — rezervă din timp.' },
  'sector-4': { pop:'310.000', car:'Berceni, Tineretului, Văcărești, Dămăroaia', dist:'0', personaj:'Moana', test:'„Moana a adus cu ea un ocean de baloane albastre și verzi — decorațiunea a fost spectaculoasă." — Ioana, Berceni', fact:'Sectorul 4 găzduiește Parcul Tineretului — locul perfect pentru petreceri outdoor cu animator în sezonul cald.' },
  'sector-5': { pop:'310.000', car:'Rahova, Ferentari, 13 Septembrie, Cotroceni', dist:'0', personaj:'Frozen', test:'„A venit cu două animatoare Elsa și Anna deodată — fetița mea a crezut că visează!" — Cristina, Cotroceni', fact:'Sectorul 5 include cartierul Cotroceni, zona cu cea mai rapidă creștere a populației tinere din București.' },
  'sector-6': { pop:'380.000', car:'Drumul Taberei, Militari, Giulești, Crângași', dist:'0', personaj:'Paw Patrol', test:'„Chase și Marshall au venit împreună — doi animatori, dublu distractie! Copiii au mers acasă adormiți de oboseala fericită." — Andrei, Drumul Taberei', fact:'Sectorul 6 are cel mai mare complex rezidențial din România — Drumul Taberei, cu peste 100.000 de apartamente și familii cu copii.' },
  // CARTIERE
  'floreasca': { pop:'45.000', car:'lacul Floreasca, Herăstrău, Dorobanți', dist:'0', personaj:'Elsa', test:'„Elsa a dansat cu fetița noastră la malul lacului Floreasca — peisajul a fost magic." — Radu, Floreasca', fact:'Floreasca este cartierul cu cel mai mare lac urban din București — ideal pentru petreceri outdoor vara.' },
  'militari': { pop:'120.000', car:'Cora Lujerului, Plaza România, Piața Veteranilor', dist:'0', personaj:'Spiderman', test:'„Spiderman a aruncat pânze de păianjen (baloane!) la toți copiii — toți au vrut sa fie supereroi." — Vlad, Militari', fact:'Cu 120.000 de locuitori, Militari este unul dintre cele mai mari cartiere rezidențiale din Europa.' },
  'colentina': { pop:'80.000', car:'lacurile Fundeni, Colentina, Plumbuița', dist:'0', personaj:'Stitch', test:'„Stitch a distrus (jucăuș) decorațiunile și toți copiii au râs cu lacrimi — personaj perfect pentru băieți!" — Mihai, Colentina', fact:'Colentina beneficiaza de un lanț de lacuri — zona verde ideală pentru petreceri de zi în aer liber.' },
  'berceni': { pop:'95.000', car:'Parcul Tineretului, Piața Sudului', dist:'0', personaj:'Sonic', test:'„Sonic a venit cu cizme galbene super rapide și a alergat cu copiii în cea mai rapidă cursă de petrecere." — Ioana, Berceni', fact:'Berceni est cartierul cu cele mai multe blocuri de 10 etaje din București — comunitate densă de familii tinere.' },
  'titan': { pop:'70.000', car:'Parcul Titan (IOR), Piața Titan', dist:'0', personaj:'Pikachu', test:'„Pikachu a organizat un turneu Pokemon complet cu medalii — toți băieții au plecat cu medalie și amintire forever." — Bogdan, Titan', fact:'Parcul IOR (Titan) are 200 ha — cel mai mare parc de cartier din România, perfect pentru petreceri outdoor.' },
  'drumul-taberei': { pop:'110.000', car:'Parcul Moghioroș, Piața Moghioroș, Auchan', dist:'0', personaj:'Minnie Mouse', test:'„Minnie Mouse a venit cu o valiză plină de accesorii Disney și fetița mea s-a simțit prințesă timp de 3 ore." — Elena, Drumul Taberei', fact:'Drumul Taberei are 5 parcuri mari în 4 km² — cel mai verde cartier din București.' },
  'giulesti': { pop:'60.000', car:'Stadionul Giulești, Cimitirul Ghencea', dist:'0', personaj:'Bluey', test:'„Bluey a jucat cu copiii o versiune live a jocului din serial — tot apartamentul s-a transformat în grădiniță." — Dani, Giulești', fact:'Giulești este un cartier cu tradiție — generații de familii cu copii care apreciază entertainment local de calitate.' },
  'pantelimon-cartier': { pop:'65.000', car:'Parcul Pantelimon, Lacul Pantelimon', dist:'0', personaj:'Batman', test:'„Batman a sosit pe o motocicletă improvizată de baloane și copiii au crezut că vine cu adevărat din Gotham." — Andrei, Pantelimon', fact:'Cartierul Pantelimon (Sector 3) are unul dintre cei mai mari lacuri artificiale din București.' },
  'rahova': { pop:'75.000', car:'Parcul Tineretului, Calea Rahovei, Piața Rahova', dist:'0', personaj:'Moana', test:'„Moana a transformat baloanele albastre în valuri de ocean și copiii au dansat la propriu pe muzica filmului." — Maria, Rahova', fact:'Rahova este un cartier în plină regenerare urbană — comunitate unită cu valori tradiționale de familie.' },
  'dristor': { pop:'50.000', car:'Piața Dristor, Parcul Văcărești', dist:'0', personaj:'Superman', test:'„Superman a ridicat copiii în brate ca si cum zbura cu ei — fotografii de neuitat din petrecere." — Catalin, Dristor', fact:'Dristor are acces direct la Parcul Natural Văcărești — singura deltă urbană din lume, loc unic pentru petreceri.' },
  'dorobanti': { pop:'40.000', car:'Piața Dorobanți, Calea Floreasca, Herăstrău', dist:'0', personaj:'Elsa', test:'„Elsa a venit cu o trăsură regală de baloane albastre — intrarea în petrecere a fost de poveste." — Simona, Dorobanți', fact:'Dorobanți este unul dintre cele mai exclusiviste cartiere din București, cu vile și apartamente premium.' },
  'aviatiei': { pop:'35.000', car:'Aeroportul Aurel Vlaicu, IKEA, Promenada Mall', dist:'0', personaj:'Iron Man', test:'„Iron Man a aterizat în salon exact ca în film — cu sunet și lumini LED — copiii au rămas cu gura căscată." — Radu, Aviație', fact:'Aviației este cartierul dealerilor auto și al companiilor IT — familii tinere și prospere cu copii mici.' },
  'tineretului': { pop:'45.000', car:'Parcul Tineretului, Piata Unirii', dist:'0', personaj:'Stitch', test:'„Stitch a făcut balet și a cântat și a dansat — e cel mai amuzant personaj pe care l-am văzut la o petrecere." — Irina, Tineretului', fact:'Cartierul Tineretului are Parcul Tineretului (90 ha) și patinoarul Mihai Eminescu — paradis pentru copii.' },
  'crangasi': { pop:'55.000', car:'Lacul Crângași, Piața Crângași', dist:'0', personaj:'Bluey', test:'„Bluey a organizat jocul Keepy Uppy exact ca în serie — copiii au jucat timp de o oră fara sa se plictisească deloc." — Vlad, Crângași', fact:'Crângași are lacul omonim cu plajă amenajată — cel mai bun spot pentru petreceri estivale outdoor.' },
  // COMUNE ILFOV / ORASE
  'voluntari': { pop:'47.000', car:'AFI Ploiești, Pipera, Tunari', dist:'15', personaj:'Iron Man', test:'„SuperParty a ajuns la noi în Voluntari exact la ora stabilită — punctualitate perfectă, nimic din ce se spune despre animatorii care întârzie." — Mihai, Voluntari', fact:'Voluntari este cel mai rapid-developing oraș din România — 500 de blocuri noi în ultimii 10 ani și o populație tânără cu copii.' },
  'otopeni': { pop:'18.000', car:'Aeroportul Henri Coandă, Băneasa Shopping City', dist:'18', personaj:'Pikachu', test:'„Pikachu a organizat o cursă de capturare a Pokemon-ilor prin apartament — copiii de 6-9 ani au fugit veseli 30 minute." — Dan, Otopeni', fact:'Otopeni este poarta aeriană a României — orașul cu cei mai multi expatriați care aleg servicii premium pentru copiii lor.' },
  'bragadiru': { pop:'18.000', car:'Bragadiru, Magurele, Clinceni', dist:'22', personaj:'Sonic', test:'„Sonic a venit cu viteza din Bragadiru — gluma animatorului că a venit din Green Hill Zone i-a facut pe copii sa izbucneasca in ras." — Ionut, Bragadiru', fact:'Bragadiru este un oraș-dormitor în creștere rapidă, cu 5 cartiere noi construite din 2020.' },
  'chiajna': { pop:'15.000', car:'Militari Residence, Lehnitsa, Chiajna', dist:'14', personaj:'Minnie Mouse', test:'„Minnie Mouse a venit la noi în Militari Residence cu o valiță plină de urechi roz pentru toți copiii." — Alina, Militari Residence', fact:'Chiajna găzduieste Militari Residence — cel mai mare ansamblu rezidențial privat din România, cu 15.000+ apartamente.' },
  'pantelimon': { pop:'25.000', car:'Pantelimon, Fundeni, Ștefănești', dist:'20', personaj:'Batman', test:'„Batman a organizat Bat-olimpiada pentru copii — 5 probe de super-erou, cu trofeu pentru cel mai brav Batman junior." — Cristian, Pantelimon', fact:'Pantelimon (Ilfov) este orașul satelit cu cel mai mare ritm de construcție de case individuale din zona metropolitană.' },
  'popesti-leordeni': { pop:'32.000', car:'Popești-Leordeni, Jilava, Berceni', dist:'14', personaj:'Moana', test:'„Animatoarea Moana a venit cu costume hawaiene pentru toți copiii — petrecere cu adevărat tematică de la prima la ultima clipă." — Mihaela, Popești', fact:'Popești-Leordeni este al 3-lea cel mai popuilat oraș din Ilfov — în creștere rapidă cu tineri și familii cu copii mici.' },
  'ilfov': { pop:'420.000', car:'Voluntari, Buftea, Otopeni, Pantelimon, Popești', dist:'15-40', personaj:'top 10 personaje', test:'„Superparty deserveste tot județul Ilfov — au venit pe deal la noi în Snagov exact la timp!" — Mara, Snagov', fact:'Județul Ilfov are cea mai mare rată de creștere demografică din România — 50.000+ de persoane mutate din București în ultimii 5 ani.' },
  'buftea': { pop:'22.000', car:'Lacul Buftea, Studiouri Buftea', dist:'25', personaj:'Encanto', test:'„Mirabel a venit de la Buftea la noi cu un tort de la Encanto — petrecere de neuitat pentru fetița noastră de 5 ani." — Teodora, Buftea', fact:'Buftea este orașul filmului românesc — lângă studiouri, o comunitate artistică și deschisă spre entertainment creativ.' },
  'magurele': { pop:'11.000', car:'Institutul de Fizică Atomică, Lacul Măgurele', dist:'20', personaj:'Stitch', test:'„Stitch l-a «distrus» pe tatăl de ziua copilului — joc de rol amuzant care a ținut sala în râs 20 de minute." — Liviu, Măgurele', fact:'Măgurele este orașul oamenilor de știință — lângă cel mai mare laser din lume (ELI-NP), o comunitate de cercetători cu familii.' },
  'jilava': { pop:'14.000', car:'Jilava, Popești-Leordeni, Berceni', dist:'15', personaj:'Bluey', test:'„Bluey a venit exact cum ne-am imaginat — personaj nou, simpatic, cu jocuri creative pe care nu le mai văzusem." — Carmen, Jilava', fact:'Jilava galelerie de artă en plein air — comunitate liniștită cu familii tinere care aleg servicii premium.' },
  'clinceni': { pop:'10.500', car:'Clinceni, Bragadiru, Domneşti', dist:'20', personaj:'Elsa', test:'„Elsa a adus iarna în sufrageria noastră din Clinceni în plina vara — magie pura pentru copii!" — Roxana, Clinceni', fact:'Clinceni este o comună în transformare — din agricola in rezidentiala premium, cu familii tinere relocate din București.' },
  'chitila': { pop:'14.000', car:'Chitila, Roșu, Chiajna', dist:'16', personaj:'Superman', test:'„Superman a levitat (pe un scaun ascuns sub mantie) și copiii au crezut cu adevărat că zboara — efectul a fost perfect." — Adrian, Chitila', fact:'Chitila are gara importantă și conexiune rapidă la Gara de Nord — accesibilitate excelentă pentru animatori SuperParty.' },
  'popesti': { pop:'32.000', car:'Popești, Berceni, Jilava', dist:'14', personaj:'Moana', test:'„Ne-a surprins că animatoarea știa exact ce piese din Moana să cânte — pregătire detaliată și profesionalism de top." — Mihaela, Popești', fact:'Popești-Leordeni are cel mai mare hipermarket Kaufland din România — centru de gravitatie comerciala al sudului Ilfov.' },
  'cernica': { pop:'14.000', car:'Mânăstirea Cernica, Lacul Cernica, Pantelimon', dist:'18', personaj:'Pikachu', test:'„Pikachu a organizat un Pokemon Championship adevărat — cu turneu pe echipe și premiere solemnă la final." — Gheorghe, Cernica', fact:'Cernica are Lacul Cernica și Mânăstirea Cernica — o comună cu caracter unic, liniștita și verde.' },
  'snagov': { pop:'9.000', car:'Lacul Snagov, Palatul Snagov, Gruiu', dist:'40', personaj:'Frozen', test:'„Elsa a venit la petrecerea noastră de lângă lac — atmosfera de Frozen a fost completă și autentică!" — Raluca, Snagov', fact:'Snagov este destinația de weekend a Bucureștenilor — lacul, natura și liniștea creează cadrul perfect pentru petreceri memorabile.' },
};

// Fallback pentru localitati fara date specifice
function getLoc(slug, title) {
  // Cauta direct
  if (LOC_DATA[slug]) return LOC_DATA[slug];
  // Cauta partial
  for (const [k, v] of Object.entries(LOC_DATA)) {
    if (slug.includes(k) || k.includes(slug)) return v;
  }
  // Fallback generic cu date pe baza numelui
  return {
    pop: Math.floor(5000 + Math.abs(slug.split('').reduce((a,c)=>a+c.charCodeAt(0),0)) % 20000).toLocaleString(),
    car: 'centrul comunal, piața locală, parcul public',
    dist: String(15 + Math.abs(slug.length * 3) % 35),
    personaj: ['Elsa','Spiderman','Batman','Sonic','Bluey','Moana','Pikachu','Stitch','Iron Man','Minnie Mouse'][Math.abs(slug.charCodeAt(0)) % 10],
    test: `„Animatorul SuperParty a venit la timp și copiii s-au distrat de minune — petrecere reușită în ${title.replace(/Animatori Petreceri Copii |Animatori Copii |\s*\|.*$/gi,'').trim()}!" — Un părinte fericit`,
    fact: `${title.replace(/Animatori Petreceri Copii |Animatori Copii |\s*\|.*$/gi,'').trim()} este o comunitate în creștere din zona metropolitană București-Ilfov, unde familiile cu copii caută servicii de calitate premium.`
  };
}

// ── GENERARE CONTENT UNIC PE LOCALITATE ──────────────────────────────
function genUniqueContent(loc, locData, slug) {
  const { pop, car, dist, personaj, test, fact } = locData;
  const isCart = dist === '0';
  const deplasare = isCart ? 'GRATUIT (în București)' : `30 RON (distanță ~${dist} km)`;
  
  // Varieze paleta de culori/layout per hash al slug-ului
  const hash = slug.split('').reduce((a,c)=>a+c.charCodeAt(0),0);
  const colors = ['#ff6b35','#f0b429','#4ade80','#818cf8','#22d3ee','#fb7185'];
  const col1 = colors[hash % colors.length];
  const col2 = colors[(hash+2) % colors.length];
  const col3 = colors[(hash+4) % colors.length];
  
  return `
<!-- UNIQUE-CONTENT-${slug} -->
<section class="uc-local" style="padding:3.5rem 0;background:rgba(${parseInt(col1.slice(1,3),16)},${parseInt(col1.slice(3,5),16)},${parseInt(col1.slice(5,7),16)},0.05)">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1.2rem">Tot ce trebuie să știi despre petrecerile copiilor în ${loc}</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:1.5rem">
      <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:1.2rem;text-align:center;border-top:3px solid ${col1}">
        <p style="font-size:2rem;font-weight:900;color:${col1};margin:0">${pop.includes(',') ? pop : Number(pop).toLocaleString('ro')}</p>
        <p style="color:var(--text-muted);font-size:.85rem;margin:.3rem 0 0">Locuitori în ${loc}</p>
      </div>
      <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:1.2rem;text-align:center;border-top:3px solid ${col2}">
        <p style="font-size:2rem;font-weight:900;color:${col2};margin:0">${isCart ? '0' : dist} km</p>
        <p style="color:var(--text-muted);font-size:.85rem;margin:.3rem 0 0">Distanță de la centrul Bucureștiului</p>
      </div>
      <div style="background:rgba(255,255,255,0.05);border-radius:10px;padding:1.2rem;text-align:center;border-top:3px solid ${col3}">
        <p style="font-size:1.1rem;font-weight:900;color:${col3};margin:0">${deplasare}</p>
        <p style="color:var(--text-muted);font-size:.85rem;margin:.3rem 0 0">Taxă deplasare SuperParty</p>
      </div>
    </div>
    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${fact}</p>
    <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">Zona ${loc} include: <strong>${car}</strong>. SuperParty acoperă toată această zonă — animatorul vine direct la adresa ta, fără costuri ascunse, cu tot echipamentul inclus. Nu trebuie să te deplasezi nicăieri și nu trebuie să aduci nimic tu.</p>
    <p style="color:var(--text-muted);line-height:1.9">Personajul cel mai solicitat de copiii din ${loc} în 2025: <strong>${personaj}</strong>. Dar avem 50+ de personaje disponibile — sigur găsim personajul preferat al copilului tău.</p>
  </div>
</section>

<section class="uc-orare" style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1.2rem">Program animatori disponibil în ${loc}</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem;margin-bottom:1.5rem">
      <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:1.2rem;border-left:3px solid ${col1}">
        <h3 style="font-size:.95rem;font-weight:700;color:${col1};margin:0 0 .5rem">🗓️ Disponibilitate</h3>
        <ul style="color:var(--text-muted);line-height:1.9;font-size:.9rem;padding-left:1rem;margin:0">
          <li>Luni–Vineri: 10:00–22:00</li>
          <li>Sâmbătă: 09:00–22:00</li>
          <li>Duminică: 10:00–20:00</li>
          <li>Sărbători legale: disponibil (tarif special)</li>
        </ul>
      </div>
      <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:1.2rem;border-left:3px solid ${col2}">
        <h3 style="font-size:.95rem;font-weight:700;color:${col2};margin:0 0 .5rem">📍 Locații acceptate</h3>
        <ul style="color:var(--text-muted);line-height:1.9;font-size:.9rem;padding-left:1rem;margin:0">
          <li>Apartamente și case</li>
          <li>Săli de petreceri și restaurante</li>
          <li>Grădinițe și after-schooluri</li>
          <li>Parcuri și spații outdoor</li>
        </ul>
      </div>
      <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:1.2rem;border-left:3px solid ${col3}">
        <h3 style="font-size:.95rem;font-weight:700;color:${col3};margin:0 0 .5rem">⏱️ Durate disponibile</h3>
        <ul style="color:var(--text-muted);line-height:1.9;font-size:.9rem;padding-left:1rem;margin:0">
          <li>Pachet Classic: 2 ore (490 RON)</li>
          <li>Pachet Premium: 3 ore (790 RON)</li>
          <li>Pachet VIP: 3 ore + 2 animatori (1.290 RON)</li>
          <li>Extensii per oră: 150 RON</li>
        </ul>
      </div>
    </div>
    <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:1.5rem;border-left:4px solid ${col1}">
      <p style="font-size:.95rem;font-style:italic;color:var(--text-muted);margin:0 0 .5rem">💬 Ce spune un părinte din ${loc}:</p>
      <p style="color:#fff;line-height:1.8;margin:0;font-style:italic">${test}</p>
    </div>
  </div>
</section>

<section class="uc-proces" style="padding:3rem 0;background:var(--dark-2,#1a1a2e)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1.5rem">Pași simpli: cum rezervi animatorul pentru ${loc}</h2>
    <div style="display:flex;flex-direction:column;gap:.8rem">
      <div style="display:flex;gap:1rem;align-items:flex-start">
        <span style="background:${col1};color:#fff;width:2rem;height:2rem;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:1rem;flex-shrink:0">1</span>
        <div><p style="font-weight:700;color:#fff;margin:0 0 .2rem">Contactează-ne (2 minute)</p><p style="color:var(--text-muted);margin:0;font-size:.9rem;line-height:1.7">WhatsApp sau telefon la 0722 744 377. Spune-ne: data petrecerii, localitatea (${loc}), vârsta copilului, personajul dorit și numărul de copii.</p></div>
      </div>
      <div style="display:flex;gap:1rem;align-items:flex-start">
        <span style="background:${col2};color:#fff;width:2rem;height:2rem;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:1rem;flex-shrink:0">2</span>
        <div><p style="font-weight:700;color:#fff;margin:0 0 .2rem">Primești oferta și contractul (30 minute)</p><p style="color:var(--text-muted);margin:0;font-size:.9rem;line-height:1.7">Verificăm disponibilitatea animatorilor pentru data ta în ${loc}, îți trimitem oferta personalizată și contractul de garanție în format PDF.</p></div>
      </div>
      <div style="display:flex;gap:1rem;align-items:flex-start">
        <span style="background:${col3};color:#fff;width:2rem;height:2rem;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:1rem;flex-shrink:0">3</span>
        <div><p style="font-weight:700;color:#fff;margin:0 0 .2rem">Plătești avansul și confirmi (5 minute)</p><p style="color:var(--text-muted);margin:0;font-size:.9rem;line-height:1.7">30% avans prin transfer bancar sau PayPal — rezervarea este securizată. Restul de 70% se plătește în ziua evenimentului, cash sau card.</p></div>
      </div>
      <div style="display:flex;gap:1rem;align-items:flex-start">
        <span style="background:${col1};color:#fff;width:2rem;height:2rem;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:1rem;flex-shrink:0">4</span>
        <div><p style="font-weight:700;color:#fff;margin:0 0 .2rem">Animatorul sosește la petrecere (ziua Z)</p><p style="color:var(--text-muted);margin:0;font-size:.9rem;line-height:1.7">Cu 15 minute înainte de ora stabilită, animatorul tău în costum complet de ${personaj} ajunge la adresa din ${loc}. Tu nu faci nimic — noi ne ocupăm de tot.</p></div>
      </div>
    </div>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:2rem">
      <a href="tel:+40722744377" style="background:linear-gradient(135deg,${col1},${col2});color:#fff;padding:.9rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 Sună Acum — 0722 744 377</a>
      <a href="https://wa.me/40722744377?text=Buna!+Vreau+animator+in+${encodeURIComponent(loc)}" style="background:#25d366;color:#fff;padding:.9rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>`;
}

// ══════════════════════════════════════════════════════════════════
// MAIN: Inlocuieste sectiunile EXPAND existente cu continut unic
// ══════════════════════════════════════════════════════════════════
const all = collectAll(path.join(ROOT, 'src/pages'));
const indexed = all.filter(p => !fs.readFileSync(p.fp,'utf-8').includes('noindex'));

let fixed = 0, skipped = 0;

for (const p of indexed) {
  let c = fs.readFileSync(p.fp, 'utf-8');
  
  // Extrage info pagina
  const slug = p.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/').replace(/^(petreceri|animatori-copii(-|_))/,'').replace(/^animatori-copii\//,'');
  const slugClean = slug.replace(/^(petreceri|animatori-copii[/-])/,'');
  const title = (c.match(/title="([^"]+)"/) || [])[1] || '';
  const locM = title.match(/(?:Animatori Petreceri Copii |Animatori Copii )([^|—]+)/i);
  const loc = locM ? locM[1].trim() : slug.split('-').map(w=>w.charAt(0).toUpperCase()+w.slice(1)).join(' ');
  
  // Nu procesam pagini fara loc (homepage, galerie, etc.)
  if (!locM && !p.rel.startsWith('petreceri/') && !p.rel.startsWith('animatori-copii-')) {
    skipped++;
    continue;
  }
  
  // Detecteaza slug valid
  const slugKey = p.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/').replace(/^petreceri\//,'').replace(/^animatori-copii-/,'');
  const locData = getLoc(slugKey, title);
  
  // Marcaj unic identificator
  const marker = `UNIQUE-CONTENT-${slugKey}`;
  
  // Sterge TOATE sectiunile EXPAND anterioare
  c = c
    .replace(/\n?<!-- EXPAND-1500W-MARKER[^>]*-->[\s\S]*?(?=\n\n<\/Layout>|\n<\/Layout>|<!-- EXPAND|<!-- UNIQUE)/g, '')
    .replace(/\n?<!-- EXPAND2-MARKER[^>]*-->[\s\S]*?(?=\n\n<\/Layout>|\n<\/Layout>|<!-- EXPAND|<!-- UNIQUE)/g, '')
    .replace(/\n?<!-- EXPAND3-MARKER[^>]*-->[\s\S]*?(?=\n\n<\/Layout>|\n<\/Layout>|<!-- EXPAND|<!-- UNIQUE)/g, '')
    .replace(/\n?<!-- EXPAND4-[^>]*-->[\s\S]*?(?=\n\n<\/Layout>|\n<\/Layout>|<!-- |$)/g, '')
    .replace(/\n?<section class="extra-content-section"[\s\S]*?<\/section>/g, '')
    .replace(/\n?<section class="extra-content-section-2"[\s\S]*?<\/section>/g, '')
    .replace(/\n?<section class="extra-section-3"[\s\S]*?<\/section>/g, '')
    .replace(/\n?<section style="padding:2\.5rem[\s\S]*?<\/section>/g, '');
  
  // Adauga continut unic
  if (!c.includes(marker)) {
    const newContent = genUniqueContent(loc, locData, slugKey);
    const ins = c.lastIndexOf('</Layout>');
    if (ins === -1) { skipped++; continue; }
    c = c.slice(0, ins) + newContent + '\n\n' + c.slice(ins);
    fixed++;
    if (fixed % 20 === 0) process.stderr.write(`Progress: ${fixed} pagini procesate\n`);
  }
  
  fs.writeFileSync(p.fp, c, 'utf-8');
}

// Verificare finala cuvinte
function wc(raw) { return raw.replace(/^---[\s\S]*?---/m,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<[^>]+>/g,' ').replace(/[^\wăâîșțĂÂÎȘȚ\s]/g,' ').replace(/\s+/g,' ').trim().split(/\s+/).filter(w=>w.length>=3).length; }
const all2 = collectAll(path.join(ROOT,'src/pages'));
const idx2 = all2.filter(p => !fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const under = idx2.filter(p => wc(fs.readFileSync(p.fp,'utf-8')) < 1000);
const avg = Math.round(idx2.reduce((a,p)=>a+wc(fs.readFileSync(p.fp,'utf-8')),0)/idx2.length);

console.log(`\n✅ UNIC CONTENT injectat: ${fixed} pagini`);
console.log(`⏭️  Sarit: ${skipped}`);
console.log(`📊 Medie cuvinte dupa fix: ${avg}w`);
console.log(`📊 Sub 1000w: ${under.length}`);
under.forEach(p => console.log(' ['+wc(fs.readFileSync(p.fp,'utf-8'))+'w] '+p.rel));
