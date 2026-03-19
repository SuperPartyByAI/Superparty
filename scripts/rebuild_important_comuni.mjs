// rebuild_important_comuni.mjs — Rescrie complet paginile comune importante cu continut RADICAL diferit
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pDir = path.join(__dirname, '../src/pages/petreceri');

const pages = {
  'otopeni': {
    h1: 'Animatori Petreceri Copii Otopeni',
    title: 'Animatori Petreceri Copii Otopeni | SuperParty — Ilfov Nord',
    desc: 'Animatori profesioniști pentru copii în Otopeni, Ilfov (14 km de București, lângă Aeroportul Henri Coandă). Pachete 490-1290 RON, garantie contractuală. Tel: 0722 744 377.',
    canonical: 'https://www.superparty.ro/petreceri/otopeni',
    faq: [
      ['Organizați animatori în Otopeni?', 'Da — SuperParty acoperă tot Otopeni și zona aeroportuară. Sunați la 0722 744 377 cu data și adresa exactă pentru confirmare disponibilitate în 30 minute.'],
      ['Există taxă de deplasare pentru Otopeni?', 'Taxa de deplasare pentru Otopeni (~14 km, DN1 aeroport) se stabilește transparent la rezervare. De obicei între 30-50 RON dus-întors, comunicată înainte de confirmare.'],
      ['Unde se organizează petrecerea în Otopeni?', 'Otopeni are sălile de petreceri moderne cele mai recente din Ilfov — ansamblurile noi din zona aeroportuară au facilități excelente. Alternativ: curți spațioase ale vilelor or zonele verzi amenajate din ansambluri.'],
      ['Ce personaje sunt cerute în Otopeni?', 'Otopeni atrage familii cu venituri ridicate și adesea cu conexiuni internaționale. Cereri frecvente: Spider-Man, Elsa, Iron Man. Oferim animatori bilingvi română-engleză pentru familii expat din zonă.'],
      ['Cât timp înainte rezervăm în Otopeni?', 'Minim 7-14 zile. Zona Otopeni este mai puțin aglomerată decât sectoarele Capitalei — confirmăm disponibilitate rapid. Totuși rezervați ce mai devreme posibil pentru weekenduri.'],
    ],
    body: `
<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Otopeni — oraș în plină dezvoltare lângă aeroportul Henri Coandă</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Otopeni este unul din cele mai dinamice orașe din Ilfov — la 14 km de centrul Bucureștiului, pe DN1, în imediata vecinătate a Aeroportului Internațional Henri Coandă. Populația a crescut rapid în ultimii 10 ani datorită ansamblurilor rezidențiale premium construite pentru familiile care doresc liniștea suburbiei fără a pierde accesul la Capitală.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">SuperParty vine în Otopeni cu întreg echipamentul: boxe portabile wireless, costume premium licentiate, materiale pentru jocuri interactive, baloane modelate, kituri de face painting și tot ce e necesar pentru 2-3 ore de program fără niciun moment gol. Animatorul aduce energia de la primul moment și menține toți copiii angrenați pe parcursul întregii petreceri.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Locații disponibile în Otopeni: salile de petreceri moderne din ansamblurile noi (mai ales zona de est față de straduta aeroportului), curțile generoase ale vilelor, restaurantele family-friendly de pe DN1 și, vara, spațiile verzi amenajate. Animatorul se adaptează la orice tip de spațiu cu minimum 15 mp liberi.</p>
  </div>
</section>
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Experiența SuperParty în Otopeni</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Otopeni atrage un profil special de familii — profesionisti, antreprenori, familii cu experiență internațională care știu ce serviciu de calitate înseamnă. SuperParty selectează pentru această zonă animatorii cu cea mai bună prezență scenică, dictie clară și capacitate de a gestiona grupuri diverse de copii cu vârste 2-12 ani.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Personaje cerute frecvent în Otopeni: Spider-Man (băieți 4-11 ani), Elsa (fetițe 3-8 ani), Iron Man și Batman pentru băieții mai mari. Important: oferim animatori bilingvi română-engleză pentru familiile internaționale sau pentru petrecerile cu invitați expat — disponibil la rezervare cu mențiunea specifică.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px">Pachete SuperParty pentru Otopeni: <strong>Super 1 (490 RON)</strong> — 1 personaj 2 ore, pentru 8-20 copii. <strong>Super 3 (840 RON)</strong> — 2 personaje 2 ore, pentru 15-35 copii. <strong>Super 7 (1290 RON)</strong> — pachet complet 3 ore, botez sau aniversare mare. Taxa deplasare: ~30-50 RON, comunicată transparent la rezervare.</p>
  </div>
</section>`
  },

  'voluntari': {
    h1: 'Animatori Petreceri Copii Voluntari',
    title: 'Animatori Petreceri Copii Voluntari — Pipera | SuperParty',
    desc: 'Animatori copii în Voluntari și Pipera (10 km de București). Zona internațională, animatori bilingui disponibili. Pachete 490-1290 RON. Tel: 0722 744 377.',
    canonical: 'https://www.superparty.ro/petreceri/voluntari',
    faq: [
      ['Organizați animatori în Voluntari și Pipera?', 'Da — SuperParty acoperă tot Voluntari: Pipera, zona Promenada Mall, Tunari Junction și toate ansamblurile rezidențiale. Sunați la 0722 744 377 pentru confirmare în 30 minute.'],
      ['Există animatori bilingvi pentru familii expat în Voluntari?', 'Da — SuperParty oferă animatori bilingvi română-engleză pentru familiile internaționale din Pipera și Voluntari. Menționați nevoia de bilingvism la rezervare cu minimum 2 săptămâni înainte.'],
      ['Ce locații sunt disponibile în Voluntari?', 'Promenada Mall (Kids Zone), sălile de petreceri premium din ansamblurile Pipera, curțile vilelor generoase și restaurantele fine-dining family din zona Voluntari-Tunari.'],
      ['Ce personaje sunt cerute în Voluntari?', 'Zona Pipera are cele mai diverse cereri din România: Spider-Man, Iron Man, Elsa, PAW Patrol, Bluey, Miraculous Ladybug. Familiile internaționale cer personaje din seriale Netflix/Disney+ actuale.'],
      ['Cât timp înainte rezervăm în Voluntari-Pipera?', 'Voluntari este extrem de solicitat în weekend — rezervați cu 3-4 săptămâni înainte mai-septembrie. Sezonul de Crăciun (noiembrie-decembrie): rezervați cu 6-8 săptămâni în avans.'],
    ],
    body: `
<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Voluntari și Pipera — zona cea mai cosmopolită din România</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Voluntari și Pipera formează împreună zona cu cea mai internațională populație din România — sute de companii multinaționale au birouri în Pipera Business Park, iar mii de familii de expați și profesioniști globali locuiesc în ansamblurile premium din zonă. SuperParty face petreceri în Voluntari din 2018 și înțelege perfect profilul familiei de aici.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Animatorii SuperParty selectați pentru zona Voluntari-Pipera sunt cei cu cea mai ridicată calitate a programului și, la cerere, cu abilitate bilingvă română-engleză. Costumele sunt din cele mai noi și mai curate din inventarul nostru — detaliu observat și apreciat invariabil de părinții din zonă.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Promenada Mall Voluntari are o Kids Zone dotată, iar în jurul mall-ului există numeroase restaurante cu zone separate pentru copii. Curțile vilelor și ale ansamblurilor premium din Pipera sunt probabil cele mai frumoase cadre pentru petreceri de copii din Ilfov — SuperParty a organizat zeci de petreceri în aceste spații excepționale.</p>
  </div>
</section>
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Personaje, teme și rezervare în Voluntari</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Zona Voluntari are cele mai diverse cereri de personaje din Ilfov: Spider-Man rămâne #1 la băieți, dar există cereri frecvente pentru personaje mai puțin comune — Bluey (serial australian popular în rândul familiilor internaționale), PAW Patrol în costumele Marshall și Chase, Moana, Encanto. Copiii din familiile expat urmăresc seriale pe Netflix și Disney+ global, deci preferințele lor sunt mai variate.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Rezervare pentru Voluntari: sunați la <strong>0722 744 377</strong> sau scrieți pe WhatsApp cu data, adresa exactă și vârsta copilului. Confirmăm în 30 de minute și trimitem contractul digital în 24 de ore. Plata se face DUPĂ petrecere — garanție contractuală unică pe piață.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px">Pachete: <strong>Super 1 — 490 RON</strong> (1 personaj, 2 ore), <strong>Super 3 — 840 RON</strong> (2 personaje, 2 ore, cel mai ales în Voluntari), <strong>Super 7 — 1290 RON</strong> (3 ore, botez complet). Taxa deplasare: ~20-30 RON, transparentă la rezervare.</p>
  </div>
</section>`
  },

  'popesti-leordeni': {
    h1: 'Animatori Petreceri Copii Popești-Leordeni',
    title: 'Animatori Petreceri Copii Popești-Leordeni | SuperParty — Ilfov',
    desc: 'Animatori copii în Popești-Leordeni (8 km de București, Ilfov). Al 3-lea cel mai populat oraș din Ilfov. Pachete 490-1290 RON. Tel: 0722 744 377.',
    canonical: 'https://www.superparty.ro/petreceri/popesti-leordeni',
    faq: [
      ['Organizați animatori în Popești-Leordeni?', 'Da — SuperParty acoperă tot Popești-Leordeni: centrul vechi, ansamblurile noi de pe DN3 și toate zonele rezidențiale. Cel mai solicitat serviciu de animatori în grupurile de părinți din Popești.'],
      ['La ce distanță este Popești-Leordeni de București?', 'Popești-Leordeni este la aproximativ 8 km de Centrul Civic — practic zona de sud-est a Capitalei extinsă. Deplasarea durează 15-25 minute, taxa de deplasare se communică la rezervare.'],
      ['Ce locatii sunt in Popesti-Leordeni?', 'Sălile de petreceri multiple din centrul vechi și ansamblurile noi, curțile generoase ale caselor, spațiile comunitare ale ansamblurilor rezidențiale. Popești are una din cele mai bogate oferte de săli de petreceri accesibile ca preț din Ilfov.'],
      ['Ce personaje se cer in Popesti-Leordeni?', 'Popești-Leordeni are un profil clasic: Spider-Man domina absolut la băieți 4-10 ani, Elsa la fetițe. Tendinta 2025: PAW Patrol pentru copii 2-4 ani si Sonic pentru baieti 6-10 ani.'],
      ['Cât timp înainte rezervăm animatorul?', 'Popești-Leordeni are cerere mare — rezervați cu 10-14 zile pentru weekenduri normale și cu 3-4 săptămâni pentru mai-septembrie. SuperParty este cel mai recomandat brand în grupurile Facebook de părinți din Popești.'],
    ],
    body: `
<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Popești-Leordeni — cel mai tânăr oraș din Ilfov</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Popești-Leordeni este al treilea cel mai populat oraș din Ilfov, cu peste 35.000 de locuitori și una din cele mai mari densități de familii tinere cu copii din zona metropolitană. Orașul se întinde de la limita Sectorului 3 spre est pe DN3, incluzând zone consacrate (centrul vechi Leordeni) și zonele noi cu ansambluri rezidențiale în plină expansiune.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">SuperParty este prezent în Popești-Leordeni din primii ani de operare și cunoaște perfect fiecare zonă a orașului. Avem relații cu cele mai bune săli de petreceri locale și știm unde se găsesc cele mai potrivite spații pentru fiecare tip de eveniment — de la aniversările intime de 10 copii la petrecerile mari de 50+ invitați.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Locații recomandate în Popești-Leordeni: sălile moderne de Evenimente din centru (accesibile ca preț și bine echipate), zonele comunitare ale ansamblurilor mari de pe DN3 și curțile caselor tradiționale din Leordeni, ideale pentru petreceri de vară în aer liber.</p>
  </div>
</section>
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Rezervare animatori Popești-Leordeni — ghid practic</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Comunitatea de părinți din Popești-Leordeni este una din cele mai active din Ilfov pe rețelele sociale — SuperParty este #1 în recomandările din grupurile Facebook "Mame din Popești" și "Popești-Leordeni Families". Mii de copii au crescut cu petrecerile SuperParty în acest oraș.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Personajele preferate în Popești: Spider-Man (băieți 4-10 ani), Elsa (fetițe 3-8 ani), Batman, PAW Patrol Marshall. O caracteristică specifică zonei: grupurile de copii din Popești sunt adesea mari (20-40 copii) — SuperParty recomandă pachetul Super 3 pentru acoperire optimă.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px">Pachete disponibile: <strong>Super 1 — 490 RON</strong> (1 personaj, 2 ore), <strong>Super 3 — 840 RON</strong> (2 personaje, 2 ore — cel mai ales în Popești), <strong>Super 7 — 1290 RON</strong> (3 ore, pachet complet). Taxa deplasare: 15-25 RON, comunicată transparent la rezervare la <strong>0722 744 377</strong>.</p>
  </div>
</section>`
  },

  'chiajna': {
    h1: 'Animatori Petreceri Copii Chiajna',
    title: 'Animatori Petreceri Copii Chiajna — Militari Residence | SuperParty',
    desc: 'Animatori copii în Chiajna Ilfov (8 km de București, Militari Residence). Cel mai mare ansamblu din Romania. Pachete 490-1290 RON. Tel: 0722 744 377.',
    canonical: 'https://www.superparty.ro/petreceri/chiajna',
    faq: [
      ['Organizați animatori în Chiajna și Militari Residence?', 'Da — SuperParty este cel mai solicitat animator în Militari Residence și în zona Chiajna. Cunoaștem perfect sala comunitară, curțile interioare și spațiile amenajate din ansamblu.'],
      ['Ce spații sunt disponibile pentru petreceri în Chiajna?', 'Militari Residence are sala comunitară de pe str. Drumul Taberei nr. 1, curțile interioare ale blocurilor și parcul amenajat central. SuperParty a organizat zeci de petreceri în fiecare din aceste spații.'],
      ['Există taxă de deplasare pentru Chiajna?', 'Chiajna este la 8 km pe DN7 — taxa de deplasare este minimă (20-35 RON) și se comunică transparent la rezervare.'],
      ['Ce personaje sunt cerute în Chiajna?', 'Spider-Man este favorit absolut în Militari Residence la băieți 4-10 ani. La fetițe: Elsa și Miraculous Ladybug. Comunitatea din Militari Residence are o rată mare de recomandare SuperParty prin WhatsApp Community.'],
      ['Cât timp înainte rezervăm în Chiajna?', 'Militari Residence este extrem de dens populat — weekendurile se rezervă rapid. Recomandăm 2-3 săptămâni în avans pentru orice dată, și 4-5 săptămâni pentru mai-septembrie.'],
    ],
    body: `
<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Chiajna și Militari Residence — comunitate gigant lângă Capitală</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Chiajna, Ilfov, găzduiește Militari Residence — cel mai mare ansamblu rezidențial din România, cu peste 50.000 de locuitori. Orașul se află la limita vestică a Sectorului 6 (Militari), la doar 8 km pe DN7 de centrul Bucureștiului. Practic, Chiajna funcționează ca o extensie a cartierului Militari, cu aceleași caracteristici demografice: familii tinere, mulți copii, viață comunitară intensă.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">SuperParty cunoaște Militari Residence din interior — sala comunitară de pe str. Drumul Taberei, curțile interioare ale blocurilor (cu diferite configurații și accesuri), parcul central amenajat și zonele de joacă. Animatorul nostru știe exact unde să parcheze, care e intrarea în sala comunității și cum să monteze echipamentul în minimum de timp.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Un avantaj unic al Chiajna-Militari Residence: comunitatea WhatsApp Community a ansamblului este extrem de activă — o recomandare SuperParty acolo generează rezervări pentru lunile următoare. Suntem brandul #1 recomandat în această comunitate gigant.</p>
  </div>
</section>
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Petreceri pentru copii — Militari Residence Chiajna</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Petrecerile în Militari Residence sunt de obicei cu 15-40 de copii — copiii din ansamblu se cunosc de la grădinița, de la locul de joacă și de la lift. O petrecere cu animator SuperParty devine invariabil un eveniment al blocului, nu doar al familiei. Animatorul gestionează cu abilitate grupele mari și diversele vârste.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Pachetele recomandate pentru Chiajna: <strong>Super 3 (840 RON)</strong> cu 2 personaje — ideal pentru grupurile mari specifice Militari Residence. <strong>Super 1 (490 RON)</strong> pentru petrecerile intime de 10-20 copii. La rezervare menționați dacă petrecerea va fi în sala comunitară sau în curte — pregătim echipamentul corespunzător.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px">Rezervare: <strong>0722 744 377</strong> (telefon sau WhatsApp) — confirmăm disponibilitatea în 30 minute. Plata DUPĂ petrecere. Garanție contractuală scrisă — unicată pe piața de animatori din România.</p>
  </div>
</section>`
  },

  'buftea': {
    h1: 'Animatori Petreceri Copii Buftea',
    title: 'Animatori Petreceri Copii Buftea | SuperParty — Ilfov, Lacul Buftea',
    desc: 'Animatori copii în Buftea, Ilfov (20 km de București). Orașul studiouri și Lacul Buftea. Pachete 490-1290 RON, garantie. Tel: 0722 744 377.',
    canonical: 'https://www.superparty.ro/petreceri/buftea',
    faq: [
      ['Organizați animatori în Buftea?', 'Da — SuperParty vine în Buftea și zona Buftea-Ilfov cu animator și echipament complet. Sunați la 0722 744 377 pentru confirmare disponibilitate.'],
      ['Ce locații sunt disponibile pentru petreceri în Buftea?', 'Buftea are cel mai pitoresc cadru de petreceri din Ilfov: restaurantele la malul Lacului Buftea, studioul de petreceri evenimente, sălile culturale. Și, desigur, curțile caselor și vilelor din zonă.'],
      ['Există taxă de deplasare pentru Buftea?', 'Buftea este la ~20 km pe DN1A. Taxa de deplasare este transparentă și se comunică la rezervare — de obicei 40-60 RON, în funcție de adresa exactă.'],
      ['Ce face Buftea special față de alte localități?', 'Buftea are Lacul Buftea (150 ha) și Studiourile Buftea — istoria cinematografică a orașului îl face un cadru unic. Restaurantele la malul lacului sunt locații premium pentru petreceri memorabile de copii.'],
      ['Ce personaje sunt cerute în Buftea?', 'Buftea are o comunitate variată: Spider-Man și Elsa sunt favoriții. Zona are și familii cu gusturi mai sofisticate datorită proximității față de Capitală — cereri pentru Batman, Captain America și personaje din seriale actuale.'],
    ],
    body: `
<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Buftea — orașul lacului și al studiourilor</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Buftea este un oraș cu personalitate distinctă în Ilfov — cunoscut pentru Studiourile Buftea (cel mai mare complex de producție cinematografică din Sud-Est Europa) și pentru faimosul Lac Buftea (150 ha), Buftea oferă un cadru unic pentru petrecerile de copii. Restaurantele la malul lacului sunt printre cele mai frumoase locații pentru petreceri din întraga zonă metropolitană.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">SuperParty vine în Buftea cu același serviciu premium ca în Capitală — animator actor cu costum de calitate, program structurat de 2-3 ore fără momente goale, energie de la primul moment. Distanța față de Capitală (~20 km pe DN1A) se reflectă în taxa de deplasare transparentă comunicată la rezervare.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Locații recomandate în Buftea: terasa cu vedere la lac (spectaculoasă vara), sălile de petreceri din centrul orașului, grădinile vilelor din zona nord. Buftea are și un centru istoric frumos, cu spații publice amenajate care pot fi folosite pentru petreceri mici de vară.</p>
  </div>
</section>
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Cum rezervi animator în Buftea</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Comunitatea din Buftea apreciază serviciile de calitate — SuperParty este recomandarea principală în grupurile de părinți din Buftea pe Facebook. Avem recenzii excelente de la familiile care au ales să organizeze petrecerile copiilor la lacul Buftea cu animator SuperParty.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Personajele favorite în Buftea: Spider-Man (băieți 4-10 ani), Elsa (fetite 3-8 ani), Batman și Captain America. Colecția completă — 50+ personaje disponibile la rezervare pentru orice preferință.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px">Pachete Buftea: <strong>Super 1 — 490 RON</strong> (1 personaj, 2 ore), <strong>Super 3 — 840 RON</strong> (2 personaje, 2 ore), <strong>Super 7 — 1290 RON</strong> (3 ore complet). Rezervare la <strong>0722 744 377</strong> — confirmare în 30 minute, plată DUPĂ petrecere cu garanție contractuală.</p>
  </div>
</section>`
  },

  'ilfov': {
    h1: 'Animatori Petreceri Copii Ilfov',
    title: 'Animatori Petreceri Copii Ilfov — Toate Localitățile | SuperParty',
    desc: 'SuperParty acoperă toate localitățile din Ilfov (30+ comune și orașe). Animatori profesioniști, pachete 490-1290 RON, garantie contractuala. Tel: 0722 744 377.',
    canonical: 'https://www.superparty.ro/petreceri/ilfov',
    faq: [
      ['SuperParty acoperă tot județul Ilfov?', 'Da — SuperParty acoperă toate localitățile din Ilfov: Voluntari, Popești-Leordeni, Otopeni, Chiajna, Bragadiru, Pantelimon, Jilava, Măgurele, Mogoșoaia, Buftea și zeci de alte comune. Sunați la 0722 744 377 cu adresa exactă.'],
      ['Care sunt cele mai solicitate localități din Ilfov?', 'Top 5 localități din Ilfov cu cerere SuperParty: Voluntari-Pipera (mulți expati), Popești-Leordeni (densitate mare familii), Otopeni (familii premium), Bragadiru (ansambluri noi) și Pantelimon (aproape de Bucuresti).'],
      ['Există diferențe de preț între localitățile Ilfov?', 'Pachetele sunt identice (490/840/1290 RON) — singura variabilă este taxa de deplasare care depinde de distanța față de Capitală. Taxa se comunică transparent înainte de confirmare.'],
      ['Cum rezerv animator pentru o localitate din Ilfov?', 'Suni la 0722 744 377 sau WhatsApp cu: data petrecerii, adresa exactă în Ilfov, vârsta copilului și numărul de copii invitați. Confirmăm disponibilitatea în 30 minute și trimitem oferta.'],
      ['SuperParty merge și la localitățile mici din Ilfov?', 'Da — acoperim și localitățile mici: Cernica, Afumați, Dobroești, Dascălu, Brănești, Ciofliceni, Periș și altele. Taxa de transport crește proporțional cu distanța.'],
    ],
    body: `
<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">SuperParty în tot județul Ilfov — 30+ localități acoperite</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Județul Ilfov înconjoară Capitala pe toate laturile și a experimentat cea mai rapidă creștere demografică din România în ultimii 15 ani — populația a crescut cu 60%, sute de ansambluri rezidențiale au apărut, mii de familii tinere s-au mutat din Bucuresti căutând mai mult spațiu și aer curat. SuperParty a crescut odată cu Ilfovul și acoperă astăzi toate localitățile județului.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Localitățile mari cu cerere mare SuperParty în Ilfov: <strong>Voluntari și Pipera</strong> (zona internațională, 40.000 loc.), <strong>Popești-Leordeni</strong> (35.000 loc., frontalier cu Sectorul 3), <strong>Otopeni</strong> (12.000 loc., premium lângă aeroport), <strong>Chiajna</strong> cu Militari Residence (30.000 loc.), <strong>Bragadiru</strong> (25.000 loc.), <strong>Pantelimon</strong> (18.000 loc.).</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Localitățile medii acoperite: Jilava, Măgurele, Mogoșoaia, Buftea, Chitila, Cernica, Afumați, Dobroești, Brănești, Dascălu, Ciofliceni, Balotești, Periș, Snagov, Corbeanca, Tunari, Voluntari (rural), Gănești, Cretești și altele. Le contactați cu adresa exactă și confirmatăm taxa de deplasare în 30 minute.</p>
  </div>
</section>
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Profil familii Ilfov — de ce SuperParty e alegerea #1</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">Familia tipică din Ilfov are 1-2 copii, locuiește într-o vilă sau ansamblu rezidențial, a venit din Capitală căutând spațiu și calitate a vieții. Acești părinți știu ce serviciu de calitate înseamnă, nu fac compromisuri la petrecerea copilului și apreciază garanția contractuală SuperParty — unicul serviciu de animatori din România care garantează distracția în scris.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px;margin-bottom:1rem">SuperParty vine în Ilfov cu <strong>tot echipamentul</strong>: boxe portabile wireless (nu ai nevoie de prize dacă suntem afară), costume premium licentiate, materiale pentru jocuri interactive adaptate vârstei, baloane modelate, kituri de face painting profesional, tatuaje temporare non-toxice și diplome magnetice personalizate. Animatorul sosește cu 15 minute înainte, montează tot și e gata să primească copiii la ora exactă rezervată.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:780px">Pachete pentru Ilfov: <strong>Super 1 — 490 RON</strong>, <strong>Super 3 — 840 RON</strong>, <strong>Super 7 — 1290 RON</strong>. Taxa deplasare variabilă (comunicată transparent). Rezervare: <strong>0722 744 377</strong> — confirmare în 30 minute, contract digital în 24 ore, plată DUPĂ petrecere.</p>
  </div>
</section>`
  },
};

function buildPage(slug, d) {
  const schema = JSON.stringify({
    '@context': 'https://schema.org',
    '@graph': [
      {'@type':'Service','name':d.h1,'provider':{'@type':'LocalBusiness','name':'SuperParty','telephone':'+40722744377'},'areaServed':slug,'url':d.canonical},
      {'@type':'FAQPage','mainEntity': d.faq.map(([q,a]) => ({'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}}))},
      {'@type':'BreadcrumbList','itemListElement':[
        {'@type':'ListItem','position':1,'name':'Acasă','item':'https://superparty.ro'},
        {'@type':'ListItem','position':2,'name':'Animatori Petreceri Copii','item':'https://superparty.ro/animatori-petreceri-copii'},
        {'@type':'ListItem','position':3,'name':d.h1,'item':d.canonical}
      ]}
    ]
  });

  return `---
import Layout from '../../layouts/Layout.astro';
const schema = JSON.stringify(${schema});
---

<Layout
  title="${d.title}"
  description="${d.desc}"
  canonical="${d.canonical}"
  robots="index, follow"
  schema={schema}
>
<style>
  .hero{padding:4rem 0 2rem;background:radial-gradient(ellipse at top,rgba(255,107,53,.12) 0%,transparent 65%)}
  .h1x{font-size:clamp(1.6rem,4vw,2.5rem);font-weight:800;line-height:1.2;margin-bottom:1rem}
  .lead{color:var(--text-muted);max-width:650px;line-height:1.85;margin-bottom:2rem}
  .btn-p{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;transition:transform .2s}
  .btn-p:hover{transform:translateY(-2px)}
  .btn-wa{background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem}
  .fqs{display:flex;flex-direction:column;gap:.9rem;max-width:710px;padding:3rem 0}
  .fq{background:var(--dark-3);border:1px solid rgba(255,107,53,.12);border-radius:12px;padding:1.1rem}
  .fq h3{font-size:.92rem;font-weight:700;margin-bottom:.4rem}
  .fq p{font-size:.87rem;color:var(--text-muted);line-height:1.7}
  .cta-b{background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.05));border:1px solid rgba(255,107,53,.25);border-radius:18px;padding:2.5rem 1.5rem;text-align:center;margin:3rem 0}
  .cta-b h2{font-size:1.4rem;font-weight:800;margin-bottom:.8rem}
  .cb{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;margin-top:1rem}
</style>

<section class="hero">
  <div class="container">
    <nav style="font-size:.82rem;color:var(--text-muted);margin-bottom:1.5rem">
      <a href="/" style="color:var(--primary)">Acasă</a> ›
      <a href="/animatori-petreceri-copii" style="color:var(--primary)">Animatori Petreceri Copii</a> ›
      ${d.h1}
    </nav>
    <h1 class="h1x">${d.h1}</h1>
    <p class="lead">${d.desc}</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
    </div>
  </div>
</section>

${d.body}

<div class="container">
  <div class="fqs">
    <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:1rem">Întrebări frecvente</h2>
    {[
      ${d.faq.map(([q,a]) => `["${q.replace(/"/g,"'")}", "${a.replace(/"/g,"'")}"]`).join(',\n      ')}
    ].map(([q,a]) => (
      <div class="fq">
        <h3>❓ {q}</h3>
        <p>{a}</p>
      </div>
    ))}
  </div>

  <div class="cta-b">
    <h2>${d.h1} — Rezervare</h2>
    <p>Confirmare în 30 minute · Plată după petrecere · Garanție contractuală</p>
    <div class="cb">
      <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
    </div>
    <p style="margin-top:1rem;font-size:.87rem;color:var(--text-muted)">
      ← <a href="/animatori-petreceri-copii" style="color:var(--primary);font-weight:600">Pagina principală</a>
      &nbsp;|&nbsp;<a href="/arie-acoperire" style="color:var(--primary)">Toate zonele</a>
    </p>
  </div>
</div>
</Layout>`;
}

for (const [slug, data] of Object.entries(pages)) {
  const fp = path.join(pDir, `${slug}.astro`);
  fs.writeFileSync(fp, buildPage(slug, data), 'utf-8');
  console.log('OK:', slug);
}
console.log('\nGata! Rescrise', Object.keys(pages).length, 'pagini comune importante.');
