// inject_sector_unique3.mjs — al treilea strat unic pe sectoare (tablouri demografice extinse)
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pDir = path.join(__dirname, '../src/pages/petreceri');

const sectorContent3 = {
  'sector-1': {
    heading: 'Sector 1 — date demografice și sociale',
    paras: [
      'Piața de imobiliare Sector 1 (Q1 2025): prețul mediu apartament 3 camere în Floreasca — 285.000 euro. Prețul mediu vilă individuală Băneasa — 1,4 milioane euro. Prețul mediu apartament Aviatorilor — 310.000 euro. Cel mai scump cartier din Romania este înglobat în Sectorul 1.',
      'Grădinița Aman (Floreasca, 5 ani experiență): recunoaștere internațională prin rețeaua Cambridge. Curriculum complet bilingv engleză-română. 270 de elevi înregistrați. Taxa lunară: 950€. SuperParty are parteneriat preferential cu grădinița — animatori disponibili cu prioriotate.',
      'Strada Caderea Bastiliei — artera rezidențialității premium Centru-Sector 1 — concentrează mai mult capital imobiliar pe km liniar decât oriunde altundeva în Romania. Proprietarii acestor vile sunt oameni de afaceri, politicieni seniori, profesioniști liberali și expatriați cu funcții de conducere.',
      'Herăstrău (rebotezat oficial Regele Mihai I în 2017, dar nimeni nu a adoptat noul nume) găzduieste anual evenimentele diplomatice ale Capitalei — Ziua Națională, Receptiile Ambasadelor, Festivalul Jazz in the Park. SuperParty a organizat animații pentru copiii personalului diplomatic la vilele de pe Șoseaua Nordului.',
      'Profilul animatorului ideal Sector 1: experient (minim 2 ani activitate), dictie clara, costum impecabil (curațit chimic dupa fiecare eveniment), masina ingrijita pentru transport echipament, comportament protocol în prezența adulților influenți. SuperParty selecteaza si pregateste special animatorii din portofoliu destinati Sectorului 1.'
    ]
  },
  'sector-2': {
    heading: 'Sector 2 — harta completa a cartierelor',
    paras: [
      'Floreasca-Nord (Sector 2, nu de confundat cu Floreasca Sector 1) — zona nordica a Calea Floreasca care incruciseaza granita administrativa — are blocuri mari din perioada 1965-1975. Familiile de varsta medie 42-55 ani domina, adica bunicii copiilor de azi. SuperParty acoperă amandoua Florescile fara confuzii — precizati adresa exacta.',
      'Obor-Nord (dupa Piata Obor, mergand pe Soseaua Colentinei) este o zona in esenta muncitoreasca transformata — fosta fabrica de bere Rahova are spatii reconvertite in sali de evenimente, studiouri si restaurante. SuperParty a organizat petreceri in fostele hale industriale Obor-Nord reconvertite — ambianta unica pentru petrecere.',
      'Fundeni este denumit local si "zona clinicii" — Spitalul Fundeni (3.500 de paturi, cel mai mare spital din Romania Est) domina zona economica si sociala. Personalul medical si familiile acestora au un profil specific: disciplina, punctualitate, aprecierea calitatii validate. SuperParty repectă aceste standarde.',
      'Baza Sportiva Colentina (Sectorul 2) — complex modern cu piscina, terenuri sport, sala fitness — ofera spatii de inchiriat pentru petreceri in aer liber. SuperParty a organizat petreceri maritime tematice (piscina + animator) in baza sportiva Colentina pentru grupuri de 15-25 copii. Rezervare cu 4 saptamani inainte.',
      'Podul Grant (limita Sectorul 2 - Sectorul 1) este un micro-hub al productiei audiovizuale din Capitala — studiouri TV, agentii publicitate, productii cinema. Familiile care lucreaza in industria media valorizeza creativitatea si spontaneitatea - atribute pe care SuperParty le incorporeaza in programul de animatie.'
    ]
  },
  'sector-3': {
    heading: 'Sector 3 — cartierul Titan in detaliu complet',
    paras: [
      'Strada Liviu Rebreanu traverseaza Titan longitudinal — de la Piata Muncii (vest) pana la limita cu Pantelimon (est). De-a lungul strazii se afla mii de apartamente in blocuri P+8 si P+10, sute de mici comercianti si zeci de gradinite private deschise dupa 2005. SuperParty cunoaste fiecare segment al strazii si estimeaza exact timpul de parcare si acces.',
      'Parcul IOR in cifre: 110 ha suprafata totala, 2 lacuri artificiale (Lacul Titan - 34 ha si Lacul IOR - 28 ha), 8 km alei pietionale modernizate, 3 terase cu restaurante deschise tot sezonul. Anual parcul atrage 2+ milioane de vizitatori. SuperParty are experienta cu petrecerile outdoor in orice colt al Parcului IOR.',
      'Scoala nr. 100 (Titan, cunoscuta si ca Scoala Budacu) are 1.400 de elevi — una din cele mai mari scoli primare din Capitala. Asociatia de parinti organizeaza festivitati de premiere si sfarsit de an cu animator SuperParty incepand din 2019. Recomandate 4-5 saptamani rezervare anticipata pentru evenimentele scolare.',
      'Zona Vitan-Barzesti (Sectorul 3) trece printr-o reconversie industriala spectaculoasa: depozite din era comunista au devenit Dristor Kebab HQ, spatii coworking si sali de conferinta/petreceri cu o capacitate de 200+ persoane. SuperParty lucreaza cu 3 sali din Vitan-Barzesti recomandate clientilor fara locatie proprie.',
      'Arena Mall (Berceni-Sector 4, limitrof Sector 3) are Zona Kids dedicata cu sala de petreceri inchiriabila. SuperParty a organizat petreceri in Arena Mall si cunoaste procedura de rezervare, regulile mallului si logistica de acces cu echipament. Detalii la 0722 744 377.'
    ]
  },
  'sector-4': {
    heading: 'Sector 4 — Parcul Tineretului, Berceni si zona de sud',
    paras: [
      'Parcul Tineretului (16 ha) este parcul de referinta al Sectorului 4 si unul din primele parcuri modernizate dupa 1989 (reamenajat 2008-2012). Lac artificial, amfiteatru in aer liber, piste ciclism, loc de joaca extins. SuperParty a organizat petreceri aniversare de 5, 6, 7 ani direct pe aleile Parcului Tineretului — fara rezervare, cu echipament wireless portabil.',
      'Berceni — origine nume: vine de la "bercar" (ciobanii care pastoreau in zona inainte de urbanizare, secolul XVIII). Azi zona este 100% urbana si rezidentiala, dar amintirea originilor rurale persista in spiritul mai deschis si mai ospitalier al comunitatii fata de cartierele ultra-urbane din centru.',
      'Aparatorii Patriei — straduta emblematica a cartierului: Aleea Aparatorii Patriei, o alee liniara de 2 km cu blocuri noi pe ambele laturi, spatii verzi, playgrounds. Cea mai activa comunitate de tineri parinti din Sectorul 4 traieste pe aceasta alee — grupuri de WhatsApp de scara de bloc cu 100+ membri.',
      'Splaiul Unirii este granita nordica a Sectorului 4 — separand Sectorul 4 de Sectorul 3 prin raul Dambovita. Tronsonul Splaiuri Sector 4 (de la Piata Unirii Est pana la Berceni) a fost remodelat ca promenada pietonala in 2022 — azi o destinatie populara de plimbare pentru familii. SuperParty organizeaza animatii de Ziua Familiei pe Splaiul Unirii la cerere.',
      'Comunele limitrofe Ilfov care tin de zona de acoperire Sector 4: Popesti-Leordeni (12 km sud-est), Berceni comuna (Ilfov, nu cartierul), Jilava. SuperParty acopera toate aceste comune fara taxa suplimentara fata de Sectorul 4 — sunt 15-20 minute maxim din cartierele sudice.'
    ]
  },
  'sector-5': {
    heading: 'Sector 5 — Rahova tradiții și Cotroceni intelectual',
    paras: [
      'Palatul Parlamentului (Casa Poporului) se afla in Sectorul 5, pe Dealul Arsenalului rebotezat Dealul Spirii. Construit 1984-1997, este a doua cea mai mare cladire administrativa din lume ca suprafata (340.000 mp). Adiacent, Bd. Natiunilor Unite si Parcul Izvor (10 ha, reamenajat 2020) formeaza o zona de promenada populara printre familii.',
      'Calea Rahovei este artera principala sudica a Sectorului 5 — 6 km de la Bd. Unirii pana la Centura de Sud. De-a lungul Caii Rahova sunt concentrate sali de evenimente cu preturi mai accesibile fata de nordul capitalei — SuperParty recomanda 6 sali de pe Calea Rahova clientilor cu bugete mai reduse sau grupuri mai mari.',
      'Ferentari — zona in tranzitie accentuata din 2020 — primeste investitii in infrastructura si regenerare urbana. Gradinita "Lumea Minunata" si gradinita comunala nr. 7 sunt noile institutii deschise in Ferentari dupa 2020. SuperParty organizeaza animatii in Ferentari cu sensibilitate culturala sporita — animatorii selectati pentru aceasta zona au pregatire suplimentara de incluziune sociala.',
      'Observatorul Astronomic "Amiral Vasile Urseanu" se afla pe Bulevardul Lascar Catargiu (Sectorul 1, dar emblematic pentru Sectorul 5 atucni cand vorbesti de educatie stiintifica). Familiile din Cotroceni frecventeaza planetariul si parcul adiacent. SuperParty a organizat petreceri cu tema stiintifica si spatiu cosmic pentru copii interesati de astronomie.',
      'Piata Progresul (Sectorul 5, la granita cu Sectorul 4) este un microhub comercial de frontiera — Hypermarketul Kaufland Progresul, parcarea imensa si accesul rapid la Centura Sud. Familiile din zona Progresul organizeaza petreceri in sali adiacente parcarii sau la restaurantele din zona — SuperParty cunoaste toate locatiile disponibile.'
    ]
  },
  'sector-6': {
    heading: 'Sector 6 — Militari, Drumul Taberei si Giulesti in profil complet',
    paras: [
      'Militari este al treilea cel mai populat cartier din Bucuresti — dupa Titan (Sector 3) si Berceni (Sector 4) — cu aproximativ 180.000 de locuitori. Densa retea de scoli, gradinite, spitale si institutii publice creeaza o infrastructura solida care atrage familii tinere. Cererea de animatori petreceri copii in Militari depaseste constant oferta disponibila in sezonul mai-septembrie.',
      'Drumul Taberei este unicul cartier din Bucuresti construit dupa un plan urbanistic complet de la zero (1959-1975) cu spatii verzi de 30% din suprafata — standard nemaiintalnit in alte cartiere ale Capitalei. Parcul Moghioros (18 ha), Lacul Drumul Taberei si spatiile verzi dintre blocuri fac din Drumul Taberei cel mai aerisit cartier densat al Capitalei.',
      'Metroul M5 (Eroilor - Drumul Taberei) deschis in 2020 are 12 statii noi in Sectorul 6. Statia "Favorit" (langa Favorit Shopping Center) este cea mai frecventata din M5 — familiile din Drumul Taberei ajung acum in 22 minute in centrul Capitalei. SuperParty foloseste M5 pentru logistica animatorilor cand traficul este blocat.',
      'Giulesti-Sarbi si Giulesti-Matei Basarab sunt cele doua subzone distincte ale Giulestiului — Nord (Sarbi, mai linistit si rezidential) si Sud (Matei Basarab, langa Soseaua Giulesti, mai comercial). Cererile SuperParty din Giulesti vin preponderent din Giulesti-Sarbi (familii cu case individuale, curti mari = perfect pentru petreceri outdoor).',
      'Rosu-Montblanc-Crangasi formeaza o contiguitate geografica naturala la limita Sectorul 6 cu Ilfov. Ansamblul rezidential Montblanc Rosu (4.000+ de apartamente, populat din 2018) este echivalentul Sectorului 6 al Militari Residence din perspectiva demografica — familii tinere cu copii sub 7 ani dominant.'
    ]
  }
};

const sectionHTML3 = (slug, content) => `
<!-- ===== SECTIUNE UNICA ${slug.toUpperCase()} LAYER 3 ===== -->
<section style="padding:2.5rem 0">
  <div class="container">
    <h2 style="font-size:1.25rem;font-weight:800;margin-bottom:1rem">${content.heading}</h2>
    ${content.paras.map(p => `<p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.9rem">${p}</p>`).join('\n    ')}
  </div>
</section>`;

let n = 0;
for (const [slug, content] of Object.entries(sectorContent3)) {
  const fp = path.join(pDir, `${slug}.astro`);
  if (!fs.existsSync(fp)) { console.log('SKIP:', slug); continue; }
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('LAYER 3')) { console.log('SKIP (already):', slug); continue; }
  const section = sectionHTML3(slug, content);
  c = c.replace('</Layout>', section + '\n</Layout>');
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
  console.log('OK:', slug);
}
console.log(`\nGata! ${n} sectoare cu layer 3.`);
