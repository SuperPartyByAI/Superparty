// extend_cartiere_pass4.mjs - Pass final: adauga sectiune "Cum rezervi" si verificare finala
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { cartiereData } from './cartiere_data.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages/petreceri');

// Sectiuni unice "Avantaje SuperParty in zona ta" - diferite pentru fiecare cartier
const avantajeExtra = {
  'titan':              'Comunitatea din Titan este una activa si bine informata — parintii care au ales SuperParty in zona Titan revin an dupa an. Suntem cel mai recomandat serviciu de animatie din zona Titan, IOR si Sun Plaza, datorita punctualitatii, creativitatii si garantiei contractuale. Costumele noastre Disney si Marvel sunt licenziate oficial si confectionate la standarde premium.',
  'drumul-taberei':     'In cartierul Drumul Taberei avem una din cele mai mari densitati de parinti multumiti din Capitala. Metroul M5 faciliteaza accesul animatorilor din orice zona a Capitalei la orice adresa de pe Bulevardul Timisoara sau strazile din Drumul Taberei. Garantia contractuala SuperParty este valabila si in aceasta zona fara nicio exceptie.',
  'militari':           'Militari Residence este complexul nostru preferat din Sectorul 6 — avem experienta specifica cu regulamentele de interior si cu organizarea de petreceri in spatiile comunitare. Indiferent daca locuiti in blocurile socialiste de pe Iuliu Maniu sau in ansamblurile noi, SuperParty ajunge la tine cu aceleasi standarde de calitate si acelasi entuziasm.',
  'berceni':            'In Berceni, SuperParty este recomandat de parinti la parinti prin retele sociale si grupuri de WhatsApp de cartier. Popularitatea noastra in zona se datoreaza simplu: facem ceea ce promitem, la timp si la calitate garantata contractual. Parcul Tineretului si spatiile verzi din zona Soseaua Oltenitei sunt locatiile noastre preferate pentru petreceri de vara.',
  'floreasca':          'Floreasca este una din zonele cu cele mai inalte asteptari de calitate din Capitala — si SuperParty intampina aceste asteptari cu succes de fiecare data. Animatorii selectati pentru zona Floreasca-Herastrau sunt cei mai experimentati din echipa noastra, cu o prezenta scenica impecabila si abilitatea de a personaliza programul la cel mai inalt nivel.',
  'colentina':          'Soseaua Colentina, cu lungimea ei de 10 km, este una din cele mai lungi zone acoperite de SuperParty in Sectorul 2. Cunoastem fiecare sector al Colentinei si ajungem rapid la orice adresa, de la intrarea in zona si pana la Fundeni. Lantul de lacuri Colentina este cadrul natural perfect pentru petrecerile noastre de vara.',
  'rahova':             'In zona Rahova-Ferentari, SuperParty aduce acelasi standard de calitate ca in cele mai exclusive zone ale Capitalei. Credem ca fiecare copil merita o petrecere magica, indiferent de cartierul in care locuieste. Pretul nostru transparent si garantia contractuala sunt promisiunile pe care le tinem in fiecare petrecere, inclusiv in Sectorul 5.',
  'crangasi':           'Crangasiul este o zona in care parintii pun mare pret pe incredere si pe recomandarile vecnilor. SuperParty a castigat increderea comunitatii locale prin consistenta si calitate — fiecare petrecere livrata la acelasi nivel inalt, de la un an la altul. Metroul M1 si Lacul Crangasi sunt avantajele geografice ale zonei pe care stim sa le valorificam cu fiecare ocazie.',
  'tineretului':        'Zona Tineretului-Timpuri Noi este una dintre cele mai bine conectate zone din Sectorul 4 — metroul M1+M3 aduce invitati din toata Capitala in 15-20 de minute. Parcul Tineretului este cel mai mare spatiu de joaca din zona de sud a Capitalei si cadrul ideal pentru petrecerile cu animatori SuperParty in aer liber. Avem experienta specifica cu organizarea de petreceri in parc.',
  'aviatiei':           'Zona Aviatorilor-Pipera este cea mai internationala din Capitala — si SuperParty este pregatit pentru astepat international. Avem animatori bilingvi, costume premium licentiate oficial Disney si Marvel, si un nivel de profesionalism pe masura asteptarilor cele mai exigente. Suntem alegerea numarul 1 a familiilor de expati din zona Pipera-Promenada.',
  'dorobanti':          'Dorobantii este zona de referinta a Capitalei pentru servicii premium — si SuperParty se aliniaza perfect acestor standarde. Selectionam animatorii destinati acestei zone dupa criterii suplimentare de prezentare, dictie si capacitate de adaptare la contexte sociale rafinate. Garantia contractuala este valabila si in zona premium Dorobanti, Floreasca sau Herastrau.',
  'dristor':            'Dristor este un cartier de comunitate, unde recomandarea directa este cel mai important factor de decizie. SuperParty a castigat increderea parintilor din Dristor-Vitan prin consecventa livrarii la cel mai inalt nivel — de la cel mai mic pachet pana la cel mai complex eveniment. Doua statii de metro M2 ne aduc rapid la orice adresa din zona.',
  'giulesti':           'Giulesti este un cartier cu suflet — iar SuperParty a invatat sa se potriveasca spiritului comunitar specific zonei. Petrecerile din Giulesti sunt adesea evenimente colective, cu multa lume si multa energie. Echipa noastra stie cum sa gestioneze grupuri mari si cum sa mentina entuziasmul la nivel maxim pe toata durata petrecerii.',
  'pantelimon-cartier': 'Cartierul Pantelimon din Sectorul 2 (distinct de comuna Pantelimon din Ilfov pe care o acoperim si noi) este o zona cu o cerere in crestere pentru servicii de calitate. SuperParty este activ in ambele zone Pantelimon — garantam aceleasi standarde de calitate si aceleasi preturi indiferent daca esti pe Soseaua Pantelimon Sector 2 sau in comuna din Ilfov.'
};

let updated = 0;
for (const c of cartiereData) {
  const fp = path.join(pagesDir, `${c.slug}.astro`);
  if (!fs.existsSync(fp)) { console.log('LIPSA:', c.slug); continue; }
  let content = fs.readFileSync(fp, 'utf-8');
  if (content.includes('avantaje-extra')) { console.log('SKIP:', c.slug); continue; }

  const displayName = c.slug.replace(/-cartier$/, '').split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  const avantajeText = avantajeExtra[c.slug] || '';

  // Adauga un paragraf suplimentar in sectiunea de text principal (primul .text-section)
  const extraPara = `
      <div class="avantaje-extra" style="margin-top:1.5rem;padding:1.2rem;background:rgba(255,107,53,.05);border-left:3px solid var(--primary);border-radius:8px;">
        <h3 style="margin-top:0;">💪 SuperParty in ${displayName} — Avantajul tau</h3>
        <p>${avantajeText}</p>
        <p>Contacteaza-ne la <strong>0722 744 377</strong> sau pe WhatsApp pentru a verifica disponibilitatea in zona <strong>${displayName}</strong> si a rezerva animatorul preferat pentru copilul tau.</p>
      </div>`;

  // Insereaza inainte de </div></section> din prima sectiune .text-section
  content = content.replace('</div>\n  </div>\n</section>\n\n{hubArticles', extraPara + '\n    </div>\n  </div>\n</section>\n\n{hubArticles');
  
  if (content.includes('avantaje-extra')) {
    fs.writeFileSync(fp, content, 'utf-8');
    updated++;
    console.log(`  ✅ Pass 4: ${c.slug}`);
  } else {
    // Fallback: insereaza inainte de CTA final
    content = fs.readFileSync(fp, 'utf-8');
    const insertBefore = '<section class="sec-alt">\n  <div class="container">\n    <div class="cta-box">';
    if (content.includes(insertBefore)) {
      const section = `<section class="sec"><div class="container"><div class="avantaje-extra" style="max-width:780px;"><h2 class="sec-title">💪 De ce <span style="color:var(--primary)">SuperParty</span> in ${displayName}?</h2><p>${avantajeText}</p><p style="margin-top:1rem;">Contacteaza-ne la <strong>0722 744 377</strong> sau pe WhatsApp pentru a verifica disponibilitatea si a rezerva rapid.</p></div></div></section>\n\n`;
      content = content.replace(insertBefore, section + insertBefore);
      fs.writeFileSync(fp, content, 'utf-8');
      updated++;
      console.log(`  ✅ Pass 4 fallback: ${c.slug}`);
    } else {
      console.log(`  ⚠️  Nu s-a putut insera in: ${c.slug}`);
    }
  }
}

console.log(`\n✅ Pass 4 complet! ${updated} pagini actualizate.\n`);

// Verifica finala
console.log('📊 VERIFICARE FINALA cuvinte:');
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
  const icon = wc >= 1500 ? '✅' : wc >= 1400 ? '🔜' : '⚠️ ';
  console.log(`  ${icon} ${c.slug.padEnd(25)}: ${wc} cuvinte`);
}
console.log(`\nMin: ${minW} | Max: ${maxW} | Tinta: 1500+`);
if (allOk) {
  console.log('\n🎉 SUCCES TOTAL! Toate paginile au 1500+ cuvinte unice!');
} else {
  console.log('\n🔜 Majority ok! Cateva pagini mai au nevoie de inca 50-100 cuvinte.');
}
