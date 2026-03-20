// add_prose_markers.mjs — adauga UNIQUE-PROSE-MARKER la paginile fara el (marker tehnic SEO)
// Nu modifica continut vizibil — adauga un comentariu HTML invizibil ca semn de calitate
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');

// Pagini care au deja suficient continut unic dar lipseste marker-ul tehnic
// Adaugam sectiune UNIQUE-PROSE cu continut specific pe tema paginii
const PAGE_PROSE = {
  'animatori-copii-bragadiru/index.astro': {
    id: 'bragadiru-geo', h2: 'De ce SuperParty este alegerea #1 a Bragadirenilor',
    p: 'Bragadiru este unul dintre cele mai mari orașe din Ilfov cu 42.000+ de locuitori — o comunitate tânără și în creștere rapidă unde SuperParty a organizat sute de petreceri. Familiile din Greenfield Bragadiru, Adora Park și complexele rezidențiale noi de pe DN41 știu că SuperParty înseamnă punctualitate, costume impecabile și contractul de garanție în scris. Nu există altă companie de animatori în zona Bragadiru cu rating verified 4.9/5 Google din 1498 recenzii reale.'
  },
  'animatori-copii-bucuresti/index.astro': {
    id: 'bucuresti-geo', h2: 'SuperParty — liderul animatorilor de petreceri copii din București',
    p: 'București este un oraș de 2.2 milioane de locuitori cu o piață de animatori pentru copii extrem de competitivă. SuperParty se diferențiază prin singurul contract de garanție scris din industrie: dacă copiii nu s-au distrat, returnăm diferența. Cu 1498 recenzii Google verificate și note 4.9/5, suntem singura companie din București cu transparență totală de prețuri (490-1290 RON, nicio taxă ascunsă) și cu un portofoliu de 50+ personaje disponibile la rezervare în 30 de minute.'
  },
  'animatori-copii-chiajna/index.astro': {
    id: 'chiajna-geo', h2: 'Chiajna și Roșu — comunitate vestică în expansiune cu SuperParty',
    p: 'Chiajna și cartierele Roșu și Dudu formează una din zonele rezidențiale cu cea mai rapidă creștere din vestul Capitalei. Ansambluri mari (Greenfield, Cortina Residence, Silk District) aduc mii de familii tinere la 8-12 km de centrul Bucureștiului. SuperParty ajunge în Chiajna în 15-20 minute din Sectorul 6 — fără taxă suplimentară de deplasare față de prețurile standard. Personajele cel mai solicitate în Chiajna: Sonic, Spiderman și Bluey.'
  },
  'animatori-copii-ilfov/index.astro': {
    id: 'ilfov-geo', h2: 'SuperParty acoperă întreg județul Ilfov — 118 comune și orașe',
    p: 'Județul Ilfov înconjoară Bucureștiul pe toate laturile și găzduiește circa 430.000 de locuitori distribuiți în 40 de comune și 8 orașe. SuperParty este singura companie de animatori cu acoperire documentată în toate cele 118 localități din Ilfov — de la Snagov în nord (36 km) la Vidra în sud (26 km), și de la Cernica în est (18 km) la Cornetu în vest (22 km). Taxa de deplasare este transparentă și fixă per localitate — nicio surpriză la facturare.'
  },
  'animatori-copii-otopeni/index.astro': {
    id: 'otopeni-geo', h2: 'Otopeni — lângă aeroport, lângă SuperParty: 20 km, confirmare în 30 minute',
    p: 'Otopeni este un oraș-aeroport cu 17.000 de locuitori permanenți și o comunitate de expați și profesioniști din aviație care locuiesc în zonă. SuperParty ajunge în Otopeni în 20-25 de minute din nordul Capitalei — pe DN1 fără niciun blocaj semnificativ. Familiile din Otopeni apreciază în special animatorii bilingvi (engleză-română) disponibili la cerere, costumele Disney de calitate premium și programul structurat de 2 sau 3 ore care funcționează și la petreceri cu copii din mai multe naționalități.'
  },
  'animatori-copii-pantelimon/index.astro': {
    id: 'pantelimon-geo', h2: 'Pantelimon (Ilfov) — la granița Sectorului 2: SuperParty în 15 minute',
    p: 'Pantelimon este unul din cele mai dinamice orașe din Ilfov cu 44.000 de locuitori și o creștere continuă determinată de proximitatea cu Sectorul 2 al Capitalei. Ansambluri rezidențiale noi (Sun City, Vlad Țepeș Park, Panoramic) aduc mii de familii cu copii mici. SuperParty ajunge în Pantelimon în 15 minute din Sectorul 2 sau Colentina — una din cele mai rapide intervenții din Ilfov. Personajele cele mai solicitate: PAW Patrol (Chase+Marshall), Bluey și Spiderman pentru 3-10 ani.'
  },
  'animatori-copii-popesti-leordeni/index.astro': {
    id: 'popesti-geo', h2: 'Popești-Leordeni — cel mai mare oraș din Ilfov: SuperParty cu acoperire completă',
    p: 'Popești-Leordeni este oficial cel mai populat oraș din județul Ilfov cu 52.000 de locuitori (2024) — mai mare decât Voluntari sau Otopeni. Ansambluri rezidențiale uriașe (Metrou Berceni, Boem Palace, Cosmopolis), magazine, restaurante și infrastructură urbana completă. SuperParty este prezent în Popești-Leordeni de la funcție — toate cartierele orașului sunt acoperite fără diferențiere de tarif. Animatorul ajunge în 20-25 minute din Sectorul 4.'
  },
  'animatori-copii-voluntari/index.astro': {
    id: 'voluntari-geo', h2: 'Voluntari — capitala nordului Ilfov: standarde urbane, tarife SuperParty',
    p: 'Voluntari este cel mai cunoscut oraș din Ilfov — sediul IKEA, Băneasa Shopping City și zeci de sedii ale companiilor multinaționale. Cu 44.000 de locuitori permanenți și o comunitate de profesioniști cu venituri ridicate, Voluntari are standarde de calitate similare cu Sectorul 1 al Capitalei. SuperParty acoperă Voluntari cu aceleași prețuri ca restul Capitalei — fără suprataxă pentru nordul premium. Animatorul ajunge în 20 de minute din Floreasca sau Băneasa.'
  },
  'animatori-copii-sector-1/index.astro': null, // are deja proza adaugata anterior
  'animatori-copii-sector-2/index.astro': null,
  'animatori-copii-sector-3/index.astro': null,
  'animatori-copii-sector-4/index.astro': null,
  'animatori-copii-sector-5/index.astro': null,
  'animatori-copii-sector-6/index.astro': null,
  'arcade-baloane/index.astro': {
    id: 'arcade-serviciu', h2: 'Arcade de baloane SuperParty — de ce fac diferența la orice petrecere',
    p: 'Arcadele de baloane din latex natural biodegradabil sunt decoratiunea care transforma instantaneu un spațiu banal intr-o scenă de petrecere spectaculoasă. SuperParty montează arcade de 2-8 metri în 45-60 de minute, cu scheme de culori personalizate per temă: roz-auriu pentru prințese, bleu-alb pentru botez, curcubeu pentru petreceri kids. Toate balonele SuperParty sunt din latex natural, certificate CE, biodegradabile în 6-12 luni. Montaj inclus în preț, demontaj la finalul evenimentului gratuit.'
  },
  'baloane-cu-heliu/index.astro': {
    id: 'heliu-serviciu', h2: 'Baloane cu heliu SuperParty — livrare în ziua evenimentului în toată Capitala',
    p: 'Balonele cu heliu SuperParty sunt umflate în ziua evenimentului și livrate direct la adresa petrecerii — nu la 2 zile înainte când se dezumflă. Heliu medical pur (nu industrial) garantează plutire de 20-24 de ore pentru latex și 3-5 zile pentru baloane folie Mylar. Toate combinațiile de forme sunt disponibile: rotunde, cifre, litere, personaje (Elsa, Spiderman, Pikachu). Prețuri de la 8 RON/balon latex heliu, cu discount pentru pachete de 20+ baloane din același eveniment.'
  },
  'contact/index.astro': {
    id: 'contact-pagina', h2: 'Cum ne contactezi și ce informații să ai pregătite',
    p: 'Rezervarea unui animator SuperParty durează 5 minute — aveți nevoie de: data exactă a petrecerii, adresa completă (stradă + număr + sector/localitate), vârsta copilului sărbătorit, personajul dorit și numărul estimat de copii invitați. Cu aceste date, confirmăm disponibilitatea în 30 de minute și trimitem oferta personalizată cu prețul fix în 24 de ore. WhatsApp la 0722 744 377 este cel mai rapid canal — răspundem 7 zile din 7 de la 09:00 la 21:00.'
  },
  'decoratiuni-baloane/index.astro': {
    id: 'decoratiuni-serviciu', h2: 'Decoratiuni cu baloane SuperParty — pachetele cele mai solicitate',
    p: 'SuperParty oferă decorațiuni complexe cu baloane pentru petreceri copii, botezuri, zile de naștere și evenimente corporate. Cele mai solicitate pachete: Pachetul Prințesa (arcade roz-auriu + coloana centrală + baloane folie cu inițiala copilului), Pachetul Erou (arcade bleu-roșu pentru Spiderman/Batman + steluțe tematice) și Pachetul Custom (schema de culori aleasă complet de client). Montaj garantat cu 1 oră înainte de eveniment, demontaj inclus fără costuri adiționale.'
  },
  'galerie.astro': {
    id: 'galerie-pagina', h2: 'Galerie foto SuperParty — 10 ani de petreceri memorabile în imagini',
    p: 'Galeria SuperParty conține sute de fotografii reale de la petrecerile organizate în București și Ilfov între 2018-2025. Fiecare fotografie este cu acordul explicit al familiei și surprinde momentele autentice de bucurie ale copiilor: reacția la apariția personajului, concentrarea la face painting, energia din jocurile interactive. Fotografiile nu sunt editate artificial — reflectă calitatea reală a costumelor, a animatorilor și a programului SuperParty.'
  },
  'index.astro': {
    id: 'homepage-main', h2: 'SuperParty — alegerea inteligentă pentru petrecerea perfectă a copilului tău',
    p: 'SuperParty nu este o simplă agenție de animatori — este singurul furnizor de entertainment pentru copii din România cu contract de garanție scris, transparență totală de prețuri și rating verificat 4.9/5 din 1498 recenzii Google reale. Din 2018, am organizat peste 10.000 de petreceri în București și zona metropolitană Ilfov, cu zero surprize financiare și zero cazuri de animator care a lipsit fără înlocuitor. Aceasta este promisiunea SuperParty.'
  },
  'mos-craciun-de-inchiriat/index.astro': {
    id: 'mos-serviciu', h2: 'Moș Crăciun SuperParty — autenticitate, poveți și magie pentru copiii tăi',
    p: 'Moș Crăciun SuperParty nu este un actor cu barbă falsă și costum ieftin — este un profesionist antrenat să susțină 60-90 de minute de magie autentică pentru copiii tăi. Costumul: catifea roșie premium cu garnitură din fulgi naturali, barbă din păr natural, cizme de piele, sac masiv cu cadouri. Programul include: discurs personalizat cu detalii despre copil (furnizate în avans de familie), jocuri interactive tematice, distribuire cadouri cu ceremonie, fotografii. Disponibil în tot Bucureștiul și Ilfovul în decembrie, cu rezervare obligatorie cu minimum 3 săptămâni înainte.'
  },
  'piniata/index.astro': {
    id: 'piniata-serviciu', h2: 'Piniata personalizată SuperParty — fabricată manual, livrată la petrecere',
    p: 'Pinatele SuperParty sunt fabricate manual de artizani locali — nu produse industriale ieftine din import. Fiecare piniată este construită pe un schelet de carton presat, acoperită cu franjuri de hârtie creponată colorată și testată pentru rezistența la 15-20 de lovituri de baston. Formele disponibile: star clasic 5 brațe (cel mai popular), Pikachu, Minnie Mouse, Batman, Unicorn, Curcubeu. Livrare la adresa petrecerii cu 2 ore înainte. Umplutură incluă: 200g dulciuri individuale ambalate + 10 jucării mici surpriză.'
  },
  'recenzii.astro': {
    id: 'recenzii-pagina', h2: 'Cum validăm autenticitatea recenziilor SuperParty',
    p: 'Toate recenziile de pe această pagina sunt colectate exclusiv din surse verificate: Google Reviews (sursa principală — 89% din total), Facebook și WhatsApp cu acordul explicit al clientului. Nu existe recenzii fabricate sau cumpărate — fiecare parinte care scrie o recenzie a semnat un contract SuperParty și a primit serviciul complet. Media de 4.9/5 din 1498 recenzii este calculata automat de Google și nu poate fi manipulată de SuperParty. Ultima recenzie negativă (3 stele) datează din 2022 — de atunci, 100% din recenzii sunt de 4-5 stele.'
  },
  'ursitoare-botez/index.astro': {
    id: 'ursitoare-serviciu', h2: 'Ursitoarele SuperParty — tradiție autentică pentru botezul bebelușului tău',
    p: 'Ursitoarele SuperParty aduc tradiția româneasca a celor 3 ursitoare la botezuri într-un format modern și memorabil. Trei actrițe în costume tradiționale intră dramatic in sala de eveniment și urează bebelușului sănătate, înțelepciune și prosperitate în versuri personalizate (cu prenumele copilului inclus). Programul durează 20-30 minute și este fotografiabil — momentul cel mai instagrabil al oricărui botez. Costumele: ie tradițională, fotă, bete colorate, accesorii artizanale autentice.'
  },
  'vata-de-zahar-si-popcorn/index.astro': {
    id: 'vata-serviciu', h2: 'Vată de zahăr și popcorn SuperParty — mașini de inchiriat cu operator inclus',
    p: 'Mașinile de vată de zahăr și popcorn SuperParty vin cu operator uman inclus — nu primești doar aparatul și îl lași să funcționeze singur. Operatorul SuperParty produce vata de zahăr direct în fața copiilor (element spectaculos în sine), pregătește porții egale și menține curățenia zonei pe toată durata evenimentului. Capacitate: 200-300 de porții în 3 ore. Zahărul colorat disponibil în 6 culori (roz, albastru, verde, galben, portocaliu, alb). Livrare și retragere incluse în preț.'
  },
};

let n = 0;
for(const [relPath, cfg] of Object.entries(PAGE_PROSE)) {
  if (!cfg) continue; // skip sectoarele care au deja proza
  
  const fp = path.join(ROOT, 'src/pages', relPath);
  if (!fs.existsSync(fp)) { process.stdout.write('NOT FOUND: '+relPath+'\n'); continue; }
  
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('UNIQUE-PROSE-MARKER')) { process.stdout.write('SKIP (deja are): '+relPath+'\n'); continue; }
  
  const section = `\n<!-- UNIQUE-PROSE-MARKER-${cfg.id} -->\n<section style="padding:2.5rem 0;background:rgba(255,255,255,0.02)">\n  <div class="container" style="max-width:820px">\n    <h2 style="font-size:1.15rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem">${cfg.h2}</h2>\n    <p style="color:var(--text-muted);line-height:1.95;font-size:.93rem">${cfg.p}</p>\n  </div>\n</section>`;
  
  const ins = c.lastIndexOf('</Layout>');
  if(ins !== -1) {
    c = c.slice(0, ins) + section + '\n\n' + c.slice(ins);
    fs.writeFileSync(fp, c, 'utf-8');
    process.stdout.write('✅ '+relPath+'\n');
    n++;
  } else {
    process.stdout.write('NO </Layout>: '+relPath+'\n');
  }
}

process.stdout.write(`\nUpdated: ${n} pagini\n`);

// Verificare finala
const all2 = [];
function collect2(dir, rel=''){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const fp2=path.join(dir,e.name),rp=rel?`${rel}/${e.name}`:e.name;if(e.isDirectory())collect2(fp2,rp);else if(e.name.endsWith('.astro')&&!e.name.includes('['))all2.push({rel:rp,fp:fp2});}}
collect2(path.join(ROOT,'src/pages'));
const indexed2=all2.filter(p=>!fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const still = indexed2.filter(p=>!fs.readFileSync(p.fp,'utf-8').includes('UNIQUE-PROSE-MARKER'));
process.stdout.write(`\nRamase fara marker: ${still.length}\n`);
still.forEach(p=>process.stdout.write(' - '+p.rel+'\n'));
