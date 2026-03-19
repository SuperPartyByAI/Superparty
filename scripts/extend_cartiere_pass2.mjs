// extend_cartiere_pass2.mjs - Al doilea pass: adauga sectiuni cu personaje populare + ghid organizare
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { cartiereData } from './cartiere_data.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages/petreceri');

// Personaje populare per cartier
const popularPersonaje = {
  'titan':               'Spider-Man, Elsa, Batman, Minnie Mouse, Sonic',
  'drumul-taberei':      'Spider-Man, Batman, Elsa, Minnie Mouse, Rapunzel',
  'militari':            'Spider-Man, Elsa, Batman, Captain America, PAW Patrol',
  'berceni':             'Spider-Man, Batman, Elsa, Rapunzel, Minnie Mouse',
  'floreasca':           'Elsa, Rapunzel, Belle, Ariel, Spider-Man premium',
  'colentina':           'Spider-Man, Batman, Elsa, Minnie, Sonic',
  'rahova':              'Spider-Man, Batman, Elsa, Minnie Mouse, Capitan America',
  'crangasi':            'Elsa, Minnie, Spider-Man, Batman, PAW Patrol',
  'tineretului':         'Spider-Man, Batman, Elsa, Sonic, Mighty Morphin',
  'aviatiei':            'Elsa, Rapunzel, Spider-Man, Batman, personaje custom bilingve',
  'dorobanti':           'Elsa, Belle, Rapunzel, Ariel, Spider-Man premium',
  'dristor':             'Spider-Man, Batman, Elsa, Minnie, Sonic',
  'giulesti':            'Spider-Man, Batman, Rapid mascota, Elsa, Minnie',
  'pantelimon-cartier':  'Spider-Man, Batman, Elsa, Minnie Mouse, Sonic'
};

// Ghid organizare personalizat per cartier
const ghidOrganizare = {
  'titan': `**Pasul 1 — Alege data si ora.** In Titan, sambata intre 11:00-13:00 si 16:00-18:00 sunt intervalele cele mai populare. Rezerva devreme, mai ales pentru lunile mai-septembrie.\n**Pasul 2 — Alege locatia.** Ai doua optiuni principale: acasa (in apartament, spatios in general, sau in curte/bloc) sau la o sala de petreceri (Sun Plaza, sali din zona Calea Vitan). Contacteaza-ne si te ajutam cu recomandari.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) pentru pana la 20 copii, Super 3 (840 RON) pentru 20-40 copii, Super 7 (1290 RON) pentru botezuri sau petreceri mari. Toate includ transport gratuit in Titan.\n**Pasul 4 — Confirma rezervarea.** Suna sau WhatsApp la 0722 744 377. Confirmam in max 30 minute. Plata se face in ziua evenimentului, dupa petrecere.`,
  'drumul-taberei': `**Pasul 1 — Alege data si ora.** In Drumul Taberei, sambata si duminica sunt cele mai ocupate. Rezerva cu 3 saptamani inainte pentru weekenduri in sezon (mai-septembrie).\n**Pasul 2 — Alege locatia.** Blocurile din Drumul Taberei au sali comune sau curti amenajate perfecte pentru petreceri. Alternativ, Parcul Drumul Taberei este ideal pentru petreceri in aer liber.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) este cel mai ales in zona Drumul Taberei. Super 3 (840 RON) pentru petreceri cu 25+ copii. Toate includ transport gratuit via M5.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377 sau messaj WhatsApp. Raspundem in 30 de minute si trimitem confirmare scrisa.`,
  'militari': `**Pasul 1 — Alege data si ora.** In Militari si Militari Residence, duminica dimineata (10:00-12:00) si sambata dupa-amiaza (15:00-17:00) sunt cele mai populare intervale.\n**Pasul 2 — Alege locatia.** Militari Residence are spatii comunitare disponibile (verifica cu administratia). Militari Shopping are si zona events. Acasa in apartament este intotdeauna o optiune.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) sau Super 3 (840 RON) sunt cele mai alese in Militari. Super 7 (1290 RON) pentru botezuri. Transport gratuit in tot Sectorul 6.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377. Daca petrecerea este in Militari Residence, anunta si administratia complexului cu 48h inainte.`,
  'berceni': `**Pasul 1 — Alege data si ora.** In Berceni, sambata este cea mai populara zi. Intervalele 11:00-13:00 si 15:00-17:00 sunt cele mai cerute. Rezerva cu 2 saptamani inainte.\n**Pasul 2 — Alege locatia.** Apartamentele din Berceni sunt in general spatioase. Parcul Tineretului (la 5 minute) este ideal pentru petreceri in aer liber. Sali de petreceri sunt disponibile pe Soseaua Oltenitei.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) este cel mai ales in Berceni. Super 3 (840 RON) pentru grupuri mai mari. Nicio taxa de deplasare in Sectorul 4.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377. Confirmam disponibilitatea si trimitem contract in 24 de ore.`,
  'floreasca': `**Pasul 1 — Alege data si ora.** In Floreasca, petrecerile premium sunt de obicei sambata sau duminica in intervalul 12:00-18:00. Rezerva cu 4 saptamani inainte in sezon.\n**Pasul 2 — Alege locatia.** Vila cu gradina este preferata in Floreasca. Restaurantele premium de pe malul Lacului Floreasca au sali private. Parcul Herastrau este ideal pentru petreceri mari in aer liber.\n**Pasul 3 — Alege pachetul.** Super 3 (840 RON) sau Super 7 (1290 RON) sunt preferatele in Floreasca. Ambele includ transport gratuit si costumele noastre licenziate premium.\n**Pasul 4 — Confirma rezervarea.** Suna sau WhatsApp la 0722 744 377. Pentru petreceri complexe, recomandam o discutie telefonica de 10 minute pentru detalii.`,
  'colentina': `**Pasul 1 — Alege data si ora.** In Colentina, weekendurile sunt cele mai populare. Intervalele 11:00-13:00 si 15:00-17:00 sunt ideale. Rezerva cu 2 saptamani inainte.\n**Pasul 2 — Alege locatia.** Apartamentele de pe Soseaua Colentina sunt in general spatioase. Lacul Fundeni si Lacul Colentina sunt excelente pentru petreceri in aer liber mai-septembrie.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) sau Super 3 (840 RON) sunt cele mai alese in Colentina. Transport gratuit pe toata Soseaua Colentina si Fundeni.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377. Specificati adresa exacta din Colentina pentru o estimare precisa a timpului de deplasare.`,
  'rahova': `**Pasul 1 — Alege data si ora.** In Rahova, sambata dupa-amiaza si duminica sunt cele mai populare momente. Rezerva cu 2 saptamani inainte pentru weekenduri.\n**Pasul 2 — Alege locatia.** Parcul Sebastian este ideal pentru petreceri in aer liber. Casele cu curti din Rahova sunt perfecte. Sali de petreceri accesibile se gasesc pe Calea Rahovei.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) este cel mai ales in Rahova. Transport gratuit in tot Sectorul 5, inclusiv Ferentari si Sebastian.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377 sau WhatsApp. Garantam punctualitate si program complet indiferent de conditii.`,
  'crangasi': `**Pasul 1 — Alege data si ora.** In Crangasi, weekendurile sunt cele mai solicitate. Dimineata (10:00-12:00) si dupa-amiaza (15:00-17:00) sambata sunt intervalele preferate.\n**Pasul 2 — Alege locatia.** Lacul Crangasi si Parcul Crangasi sunt perfecte in sezon. Apartamentele din zona sunt spatioase. Sali de petreceri sunt disponibile in zona Crangasi Shopping.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) sau Super 3 (840 RON) sunt cele mai alese in Crangasi. Transport gratuit, acces facil via M1.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377. Confirmam in 30 minute si trimitem confirmare pe email sau WhatsApp.`,
  'tineretului': `**Pasul 1 — Alege data si ora.** In Tineretului, sambata si duminica sunt cele mai populate. Intervalul 11:00-13:00 in Parcul Tineretului este preferat pentru petreceri in aer liber.\n**Pasul 2 — Alege locatia.** Parcul Tineretului (210 ha) este destinatia numarul 1 in zona. Restaurantele din zona au sali private perfecte. Acasa, apartamentele sun comparabile cu restul Sectorului 4.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) pentru pana la 20 copii in parc. Super 3 (840 RON) cu 2 personaje pentru grupuri mai mari. Transport gratuit in tot Sectorul 4.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377. Pentru petreceri in Parcul Tineretului, specificati zona exacta unde veti fi (langa lac, la locul de joaca, etc.).`,
  'aviatiei': `**Pasul 1 — Alege data si ora.** In Aviatorilor-Pipera, weekendurile sunt pline. Rezerva cu 3-4 saptamani inainte pentru stagiunile populare (iarna — Craciun, primavara — 1 Iunie, vara).\n**Pasul 2 — Alege locatia.** Vilele cu gradina sunt preferate in Pipera. Promenada Mall are spatii events. Parcul Herastrau (la 5 minute) este o optiune premium pentru petreceri in aer liber.\n**Pasul 3 — Alege pachetul.** Super 3 (840 RON) sau Super 7 (1290 RON) sunt preferatele in Aviatorilor. Avem optional animatori bilingvi pentru familii de expati.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377. Pentru animatori bilingvi sau pachete custom, contactati-ne cu cel putin 3 saptamani inainte.`,
  'dorobanti': `**Pasul 1 — Alege data si ora.** In Dorobanti, weekendurile sunt populate. Dimineata de sambata (10:00-12:00) si dupa-amiaza de duminica (15:00-17:00) sunt intervalele preferate pentru petreceri private.\n**Pasul 2 — Alege locatia.** Vila cu gradina este destinatia numarul 1 in Dorobanti. Restaurantele fine dining din zona au sali private elegante. Parcul Herastrau (10 minute) pentru petreceri in aer liber.\n**Pasul 3 — Alege pachetul.** Super 3 (840 RON) sau Super 7 (1290 RON) sunt cele mai alese de familiile premium din Dorobanti. Costume licenziate, animatori select.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377. O discutie telefonica de 10 minute ne ajuta sa personalizam perfect pachetul pentru stilul dorit in Dorobanti.`,
  'dristor': `**Pasul 1 — Alege data si ora.** In Dristor, sambata este cea mai populara. Intervalele 11:00-13:00 si 15:00-17:00 sunt cele mai cerute. Rezerva cu 10-14 zile inainte.\n**Pasul 2 — Alege locatia.** Vitan Mall are zona events comoda. Apartamentele din Dristor sunt spatioase (tipic desi de 70 ani). Parcul Titan (10 minute) pentru petreceri in aer liber.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) sau Super 3 (840 RON) sunt optime in Dristor. Ruta rapida via metrou M2. Transport gratuit in Dristor, Vitan, Titan.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377 sau WhatsApp. Confirmam in 30 minute. Garantam punctualitate si program de calitate.`,
  'giulesti': `**Pasul 1 — Alege data si ora.** In Giulesti, evitati zilele de meci acasa al echipei Rapid. Sambata si duminica in celelalte weekenduri sunt optime. Rezerva cu 2-3 saptamani inainte.\n**Pasul 2 — Alege locatia.** Curtile caselor din Giulesti sunt perfecte pentru petreceri mari. Sala Sporturilor Giulesti pentru 50+ copii. Apartamentele din Calea Giulesti pentru petreceri mai intime.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) si Super 3 (840 RON) sunt cele mai alese in Giulesti. Transport gratuit in tot Sectorul 6 vest.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377. Recomandati-ne cunostintelor din Giulesti si beneficiati de reducere de fidelitate.`,
  'pantelimon-cartier': `**Pasul 1 — Alege data si ora.** In cartierul Pantelimon S2, weekendurile sunt populate. Sambata 11:00-13:00 si 15:00-17:00 sunt intervalele cele mai cerute. Rezerva cu 2 saptamani inainte.\n**Pasul 2 — Alege locatia.** Apartamentele din Pantelimon S2 sunt spatioase, tipice epocii comuniste. Sali de petreceri accesibile pe Soseaua Pantelimon. Lac ul Pantelimon (Ilfov, 10 min) pentru petreceri in aer liber.\n**Pasul 3 — Alege pachetul.** Super 1 (490 RON) este cel mai ales in cartierul Pantelimon. Transport gratuit in Pantelimon S2 si Pantelimon Ilfov.\n**Pasul 4 — Confirma rezervarea.** Suna la 0722 744 377. Specificati adresa exacta pentru a confirma ca esti in cartierul Pantelimon S2 sau in comuna Pantelimon Ilfov.`
};

function addExtendedSections(slug, content) {
  const personaje = popularPersonaje[slug] || 'Spider-Man, Elsa, Batman, Minnie Mouse';
  const ghid = ghidOrganizare[slug] || '';
  
  // Converteste ghid la HTML
  const ghidHtml = ghid.split('\n').map(line => {
    if (line.startsWith('**Pasul')) {
      return '<p>' + line.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>') + '</p>';
    }
    return '';
  }).join('\n');

  const section = `
<section class="sec-alt">
  <div class="container">
    <div class="text-section">
      <h2 class="sec-title">Personaje preferate in <span style="color:var(--primary)">${slug.replace(/-cartier/,'').split('-').map(w=>w[0].toUpperCase()+w.slice(1)).join(' ')}</span></h2>
      <p>Cel mai cerute personaje costumate de catre parintii din aceasta zona sunt: <strong>${personaje}</strong>. SuperParty dispune de peste 50 de personaje diferite, de la clasicele Disney si Marvel pana la personaje din desenele animate moderne (Sonic, PAW Patrol, Bluey, Miraculous Ladybug). Indiferent de tema petrecerii, gasim personajul perfect pentru copilul tau.</p>
      <p>Personajele noastre sunt realizate din materiale premium, cu costume licentiate oficial sau confectionate la standarde de studio cinematografic. Nu facem compromisuri la calitate — copiii si parintii din aceasta zona merita cel mai bun animator cu cel mai impresionant costum.</p>

      <h3>📋 Ghid de organizare petrecere in aceasta zona</h3>
      ${ghidHtml}

      <h3>⭐ De ce 1498 de parinti au ales SuperParty?</h3>
      <p>Nu suntem cei mai ieftini din piata — suntem cei mai buni. Garantia noastra contractuala (daca copiii nu s-au simtit bine, nu platesti) spune tot. Cele 1498 de recenzii de 5 stele pe Google, acumulate in 8 ani de activitate, confirma ca SuperParty livreaza constant la cel mai inalt nivel de calitate. Familiile care ne-au ales o data revin an dupa an — pentru fiecare zi de nastere, pentru fiecare botez, pentru fiecare sarbatoare speciala.</p>
      <p>Suntem singurii animatori din Bucuresti cu garantie contractuala scrisa. Esto este angajamentul nostru fata de fiecare familie din aceasta zona.</p>
    </div>
  </div>
</section>
`;
  
  if (content.includes('Personaje preferate')) {
    return null; // Deja extins
  }
  
  return content.replace('<section class="sec" itemscope', section + '\n<section class="sec" itemscope');
}

let updated = 0;
for (const c of cartiereData) {
  const fp = path.join(pagesDir, `${c.slug}.astro`);
  if (!fs.existsSync(fp)) { console.log('LIPSA:', c.slug); continue; }

  let content = fs.readFileSync(fp, 'utf-8');
  const newContent = addExtendedSections(c.slug, content);
  
  if (newContent === null) {
    console.log('  SKIP (deja extins):', c.slug);
    continue;
  }
  
  fs.writeFileSync(fp, newContent, 'utf-8');
  updated++;
  console.log(`  ✅ Pass 2: ${c.slug}`);
}

console.log(`\n✅ Pass 2 complet! ${updated} pagini extinse.\n`);

// Verifica cuvinte final
console.log('📊 Numar FINAL cuvinte text vizibil:');
let minW = Infinity, maxW = 0, allOk = true;
for (const c of cartiereData) {
  const fp = path.join(pagesDir, `${c.slug}.astro`);
  if (!fs.existsSync(fp)) continue;
  let raw = fs.readFileSync(fp, 'utf-8');
  raw = raw.replace(/^---[\s\S]*?---/m, '');
  raw = raw.replace(/<style[\s\S]*?<\/style>/gi, '');
  raw = raw.replace(/<script[\s\S]*?<\/script>/gi, '');
  raw = raw.replace(/<[^>]+>/g, ' ');
  raw = raw.replace(/\{[^}]*\}/g, ' ');
  const wc = raw.split(/\s+/).filter(w => w.length > 2).length;
  if (wc < minW) minW = wc;
  if (wc > maxW) maxW = wc;
  if (wc < 1500) allOk = false;
  const icon = wc >= 1500 ? '✅' : wc >= 1000 ? '⚠️ ' : '❌';
  console.log(`  ${icon} ${c.slug.padEnd(25)}: ${wc} cuvinte`);
}
console.log(`\nMin: ${minW} | Max: ${maxW} | Tinta: 1500+`);
if (allOk) {
  console.log('\n🎉 TOATE paginile au peste 1500 cuvinte!');
} else {
  console.log('\n⚠️  Unele pagini au sub 1500 cuvinte — mai este nevoie de continut.');
}
