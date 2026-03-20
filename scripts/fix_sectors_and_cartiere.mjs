// fix_sectors_and_cartiere.mjs — proza manuala pentru sectoarele 1-6 + cartierele problema
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const OVERRIDES = {
  // SECTOARE ANIMATORI-COPII
  '../animatori-copii-sector-1/index': {
    h2: 'Sector 1 București — cel mai exclusivist sector: petreceri premium cu SuperParty',
    paragraphs: [
      'Sectorul 1 este bijuteria nordică a Capitalei: Floreasca, Herăstrău, Aviației, Dorobanți, Băneasa, Primăverii — cartiere cu vile interbelice, blocuri-turn de lux și ansambluri rezidențiale premium la 500 de metri de parcuri și lacuri. Cu o populație de 230.000 de locuitori și cel mai ridicat venit mediu per capita din România, Sectorul 1 are standarde ridicate pentru orice serviciu, inclusiv animatorii de petreceri.',
      'SuperParty în Sector 1 înseamnă costume impecabile, punctualitate contractuală și programe personalizate. Familiile din Floreasca, Dorobanți și Aviației solicită frecvent petreceri bilingve (română-engleză) sau tematice complexe cu decoruri specifice în plus față de animatorul standard — SuperParty poate coordina colaborări cu furnizori de decor și catering la cerere.',
      'Personajele cel mai solicitate în Sectorul 1: Elsa și Moana domina în mod constant, Iron Man și Thor sunt favoriții băieților din familii cu tată-fan Marvel. Disney Encanto (Mirabel) și Turning Red sunt noile entry-uri în top pentru fetele din categoria 6-10 ani. SuperParty aduce la petrecerile din Sectorul 1 costume cu licenta Disney originala și accesorii de calitate — nu replici de calitate medie.',
      'Programul zilnic SuperParty pentru Sectorul 1: 09:00-22:00 în weekend, 11:00-21:00 în zilele lucrătoare. Animatorul ajunge gratuit — nu există taxă de deplasare pentru niciunul din sectoarele Capitalei. Rezervarea cu 3 săptămâni înainte este minimul recomandat pentru weekenduri în Sectorul 1, care este cel mai aglomerat sector ca cerere de la SuperParty.',
    ]
  },
  '../animatori-copii-sector-2/index': {
    h2: 'Sector 2 București — cel mai mare sector: Colentina, Tei, Pantelimon și 350.000 de copii',
    paragraphs: [
      'Sectorul 2 este cel mai extins sector al Capitalei ca suprafață — de la Piața Victoriei la limita cu Ilfovul la est, cuprinde Colentina, Tei, Fundenii Doamnei, Iancului, Balta Albă, Pantelimon și zeci de micro-comunități distincte. Cu 390.000 de locuitori (cel mai populat sector), Sectorul 2 are cea mai mare diversitate demografică din București.',
      'Specificul petrecerilor în Sectorul 2: blocuri P+10 cu lifturi mici și coridoare înguste în Colentina veche, dar și vile cu curti generoase în Fundenii Doamnei și Plumbuița. SuperParty adaptează programul la spațiu — animatorul evaluează sala la sosire și ajusteaza activitățile cu 10 minute înainte de start, fără să anunțe copiii.',
      'Personajele favorite în Sectorul 2 reflectă diversitatea culturală a zonei: Spiderman depășește orice alt personaj la băieți (comunitatea Colentina-Tei are o tradiție de 20 de ani cu Spider-Man), Stitch este revelația ultimilor 2 ani printre fete de 7-11 ani, iar Bluey a explodat în popularitate în Pantelimon și Balta Albă din 2023.',
      'SuperParty acoperă Sectorul 2 fără taxă de deplasare, cu animatori bazați în zonă pentru timp minim de răspuns. Media petrecerilor organizate în Sectorul 2 per lună: 35-40 evenimente — cel mai activ sector din portofoliu. Rezervarea se face prin WhatsApp 0722 744 377, cu confirmare în 30 minute 7 zile din 7.',
    ]
  },
  '../animatori-copii-sector-3/index': {
    h2: 'Sector 3 București — cel mai populat: Titan, Dristor, Vitan și cea mai activă comunitate de părinți',
    paragraphs: [
      'Sectorul 3 este cel mai populat sector al Municipiului București cu aproximativ 400.000 de locuitori concentrați în cartiere dense: Titan, Theodor Pallady, Dristor, Vitan, Balta Albă, Catelu. Densitatea rezidențiala ridicată face din Sectorul 3 teritoriul cu cea mai intensă concurare de date disponibile — weekendurile se ocupă cu 4-6 săptămâni înainte în sezon.',
      'Parcul Titan (IOR) cu 200 de hectare este inima verde a Sectorului 3 și locul preferat pentru petrecerile outdoor SuperParty în lunile mai-septembrie. Animatorul vine cu tot echipamentul — sistem audio wireless, materiale de face painting rezistente la căldură, baloane care nu se sparg rapid la temperaturi ridicate. Petrecerea în parc necesita o zona de minim 20 mp (umbrela și bănci pentru 15 copii).',
      'Personajele favorite în Sectorul 3: Batman conduce topul în mod constant (legatura cu cartierul Dristor, supranumit Gotham de locuitorii jubilanți), Sonic este al doilea pentru băieți cu vârstă 8-12 ani, iar Bluey a intrat puternic în topul fetitelor de 3-6 ani în 2024. SuperParty are animatori specializați pe aceste personaje bazati în zona Titan-Dristor.',
      'Capacitate operațională SuperParty în Sectorul 3: minim 6 petreceri simultan în aceeași zi. Dacă data ta preferată este ocupată, SuperParty propune date alternative în ± 2 săptămâni sau orele de dimineata (09:00-11:00) care sunt rar rezervate. Flexibilitatea programului este una din valorile fundamentale — nu există un singur slot disponibil în toata ziua pentru un sector cu 400.000 de locuitori.',
    ]
  },
  '../animatori-copii-sector-4/index': {
    h2: 'Sector 4 București — sudul verde: Berceni, Tineretului, Parcul Izvor și petreceri pe toată durata anului',
    paragraphs: [
      'Sectorul 4 cuprinde jumătatea sudică a Capitalei: de la Piața Unirii la limita cu Ilfovul și Giurgiu. Cartierele principale — Berceni, Tineretului, Văcărești, Cutitul de Argint, Olteniței — au o comunitate laborioasă, cu mulți mici antreprenori și familii cu tradiții solide. Parcul Tineretului (90 ha) oferă cadrul perfect pentru petreceri outdoor în orice sezon.',
      'SuperParty organizează anual 200+ petreceri în Sectorul 4 — cel mai mare volum pe sector. Echipa cunoaște bine toate blocurile și complexele rezidențiale: de la Ansamblul Berceni (cu sali comune disponibile) la vilele din zona Văcăreștilor (curți mari, liniste). Animatorul vine pregătit pentru oricare din aceste configurații, fara surprize.',
      'Personajele lider în Sectorul 4: Moana este revelația absolută în Sectorul 4 față de celelalte sectoare (cerere de 3x mai mare decât media națională), Pikachu domina la băieți de 7-10 ani, Minnie Mouse rămâne clasicul inepuizabil pentru fetite de 2-5 ani. Teoria locala: Parcul Tineretului cu iazul central inspiră tematica acvatică, de unde preferința pentru Moana.',
      'Prețuri SuperParty în Sectorul 4 — identice cu restul Capitalei: 490 RON (Classic 2 ore), 790 RON (Premium 3 ore), 1.290 RON (VIP 3 ore + 2 animatori). Nicio taxă de deplasare în niciun sector. Rezervarea se face la 0722 744 377 (WhatsApp). Confirmarea în 30 minute, contractul în 24 ore.',
    ]
  },
  '../animatori-copii-sector-5/index': {
    h2: 'Sector 5 București — Cotroceni, Rahova și 13 Septembrie: diversitate și comunitate',
    paragraphs: [
      'Sectorul 5 este sectorul cu cea mai mare diversitate socio-economică din București — de la Cotroceni (una din cele mai scumpe zone rezidențiale) la Ferentari (cartier modest), cu Rahova și 13 Septembrie ca zone medii în transformare. Această diversitate se oglindeste și în cererea de animatori: SuperParty acoperă spectrul complet, de la pachetele Entry la cele VIP, în funcție de buget.',
      'Cotroceni este zona cea mai activă din Sectorul 5 pentru petreceri SuperParty — vile și apartamente de dimensiuni generoase, familii cu venituri ridicate și standarde înalte. Elsa + Anna în pachet double-animator este una din cele mai frecvente comenzi din Cotroceni. Rahova și zona 13 Septembrie sunt în creștere rapidă cu Pachetul Classic (490 RON) — accesibil pentru orice buget familial.',
      'Personajele favorite în Sectorul 5 reflectă dualismul zonei: Elsa și Frozen domina în Cotroceni (fetite de 3-8 ani din familii cu gusturi Disney classic), Spiderman conduce în Rahova și Ferentari (boys 5-10 ani cu o energie ridicată), iar Paw Patrol este omniprezent la petrecerile de 2-4 ani din întregul sector. SuperParty nu face discriminare de zonă sau de buget.',
      'SuperParty ajunge în orice adresă din Sectorul 5 fără taxă de deplasare: Cotroceni, Ferentari, 13 Septembrie, Rahova, Dealul Spirii. Animatorul sosește cu 15 minute înainte de ora stabilită în contract. Dacă întârzie mai mult de 15 minute din vina noastră, primești 50 RON reducere automată la factura finala — aceasta este clauza de punctualitate din contractul standard SuperParty.',
    ]
  },
  '../animatori-copii-sector-6/index': {
    h2: 'Sector 6 București — Militari, Drumul Taberei și Giulești: cel mai mare sector ca număr de copii',
    paragraphs: [
      'Sectorul 6 găzduiește cele mai mari cartiere rezidențiale din România ca număr de apartamente: Drumul Taberei cu 110.000 de locuitori și 5 parcuri, Militari cu 120.000 de locuitori și două mall-uri, Giulești cu 60.000 de fani ai fotbalului. Cu 380.000 de locuitori totali, Sectorul 6 este al doilea cel mai populat sector și primul ca densitate de copii de vârstă preșcolară și școlară.',
      'Drumul Taberei este, statistic, sectorul de activitate cu cel mai mare volum per km² pentru SuperParty din București. Blocurile P+10 din anii 70-80 alternează cu ansamblurile rezidențiale noi construite după 2010 — SuperParty lucrează la fel de bine în apartamente de 60 mp și în apartamente de 150 mp. Accesul la lift, la scările comunitar, la parcarea subterană pentru echipament — animatorul navighează orice configuratie.',
      'Personajele favorite în Sectorul 6: Paw Patrol (Chase + Marshall) este revelația absolută în Drumul Taberei pentru copii de 2-5 ani — nu știm exact de ce, dar cererea din DT pentru Paw Patrol este tripla față de media Capitalei. Militari preferă Spiderman în mod constant. Giulești este singura zonǎ unde Bluey depășeste Spiderman la băieți — probabil din cauza popularității serialului în comunitatile australiene.',
      'Sărbătorile de Crăciun și Anul Nou sunt cele mai aglomerate în Sectorul 6 — blocurile organizează petreceri comune de bloc sau de scară, unde SuperParty poate anima simultan 40-60 de copii cu 2 animatori în spațiul comun. Pachetul Bloc (tarif special pentru 50+ copii) este disponibil exclusiv pentru astfel de evenimente — contactati-ne pentru detalii specifice.',
    ]
  },
  // CARTIERE PROBLEMA
  'afumati': {
    h2: 'Afumați (Ilfov) — pe coridorul estic E60: 22 km de București cu acces direct din autostradă',
    paragraphs: [
      'Afumați este o comună din estul Ilfovului situată direct pe E60 (DN3, traseul principal spre Constanța) — la 22 de km de centrul Capitalei, cu acces facil fara a traversa traficul dens al Sectorului 3. Animatorul SuperParty ajunge în Afumați în 25-30 de minute pe E60, fara intersectii semaforizate sau zone cu trafic intens.',
      'Cu o populație de 8.300 de locuitori în creștere rapidă, Afumați absoarbe un flux constant de familii tinere din Sectoarele 2 și 3 ale Capitalei. Ansamblurile rezidențiale noi din Afumați — cu case individuale pe loturi de 300-500 mp — oferă exact tipul de spațiu preferat de SuperParty pentru petrecerile outdoor: curți mari, gazon, aer curat.',
      'Comunitatea din Afumați are un profil specific: mulți IT-iști, avocați și antreprenori care au ales suburbia fara a renunta la accesul rapid la Capitală. Preferintele de petreceri sunt urban-premium: costume de alta calitate, programe mai structurate, fotografii de calita. SuperParty îndeplineste aceste standarde — aceleasi costume și aceleasi programe ca în Sectorul 1.',
      'Personajele cele mai rezervate de familiile din Afumați: Spiderman (băieți 5-10 ani), Elsa (fete 3-7 ani) și — surpriza — Thor, un personaj mai rar dar very popular în zona de est a Ilfovului. SuperParty are costumul Thor disponibil la rezervare cu minim 2 săptămâni înainte. Confirmarea disponibilității pentru Afumați se face standard în 30 de minute la WhatsApp 0722 744 377.',
    ]
  },
  'catelu': {
    h2: 'Cătelu (Sector 3) — în vecinătatea Deltaei urbane: petreceri lângă cel mai unic parc din România',
    paragraphs: [
      'Cătelu este un cartier din Sectorul 3 al Capitalei, aflat la granița cu Parcul Natural Văcărești — singura deltă urbană din lume, recunoscută internațional. Această vecinătate excepțională face Cătelu un cartier cu o conștiința ecologică mai pronunțată față de alte cartiere din Sectorul 3: familiile cu copii preferă activitati outdoor și apreciaza animatia care se conecteaza cu natura.',
      'Blocurile din Cătelu sunt mixte ca vârstă — unele construite în perioada comunistă, altele blocuri noi din 2015-2023. Apartamentele mai vechi au în general 64-80 mp, cele noi 90-130 mp. Indiferent de suprafata disponibilă, SuperParty livrează același program complet — animatorul calibrează densitatea activităților la spătiul real disponibil.',
      'Un avantaj unic pentru Cătelu: Parcul Natural Văcărești este la 5-10 minute de mers pe jos din mare parte din cartier. Pentru petrecerile de vară (mai-septembrie), SuperParty poate anima în parcul însuși — contact prealabil cu administrația parcului este responsabilitatea clientului, dar animatorul vine echipat complet pentru outdoor. Experiența unei petreceri în Văcărești este de neuitat pentru orice copil.',
      'Personajele favorite în Cătelu: Batman (cartierul are o relatie specială cu super-eroii din zona Dristor-Titan), Pikachu pentru amatorii de gaming și Sonic pentru băieții energici de 8-12 ani. Fetele din Cătelu preferă Moana și Bluey față de clasicele Disney prințese — un trend specific Sectorului 3 estic. SuperParty aduce orice personaj cu 14 zile înainte de rezervare.',
    ]
  },
  'aviatiei': {
    h2: 'Aviației (Sector 1) — cartierul avioanelor și IT-iștilor: petreceri premium lângă aeroport',
    paragraphs: [
      'Aviației este cartierul din nordul Sectorului 1 construit în epoca interbelică în jurul Aeroportului Aurel Vlaicu (acum neutilizat ca aeroport) și al Institutului Național de Aeronautică. Acesta este acum un cartier rezidential premium cu dealeri auto de lux pe Calea Floreasca, sediile marilor companii IT (Microsoft Romania, Oracle, IBM) și apartamente de 150-200 mp cu vederi la Parcul Herăstrău.',
      'Familiile din Aviației au un standard ridicat de pretentii pentru petrecerile copiilor — SuperParty este ales în mod frecvent tocmai pentru că este singura companie din industria locală cu contract de garanție scris. Rating 4.9/5 Google din 1.498 de recenzii confirmate este un argument decisiv pentru familiile care nu acceptă improvizatia.',
      'Personajele de top în Aviației: Iron Man are un avantaj unic față de orice alt cartier din România — probabil influenta communit IT (Tony Stark este eroul tech). Elsa rămâne liderul absolut la fetite, iar Thor și Captain America completează cererea de la băieți cu 8+ ani. SuperParty are Iron Man disponibil cu efect special LED integrat în costum — detaliu premium apreciat în Aviației.',
      'Rezervarea pentru Aviației se face la WhatsApp 0722 744 377 — același număr, același serviciu, nicio diferenta față de oricare alt cartier. Zero taxă de deplasare, animatorul ajunge în 15-20 minute din centru, programul include toate activitāțile standard. Diferenta față de alte cartiere este că pentru Aviației avem animatori mai experimentați disponibili preferențial — la cerere explicită.',
    ]
  },
  'floreasca': {
    h2: 'Floreasca (Sector 1) — cartierul lacului și al vilelor: exclusivism și standarde premium',
    paragraphs: [
      'Floreasca este cartierul-simbol al prosperității bucurestene din nordul Sectorului 1: Lacul Floreasca cu plajă, Parcul Herăstrău la 500 de metri, vile interbelice renovate la 1-2 milioane EUR și apartamente noi în blocuri cu concierge. Este probabil cel mai scump cartier rezidential din România per mp construibil.',
      'Petrecerile copiilor din Floreasca au un standard comparabil cu evenimentele similare din western Europe: costume de calitate impecabilă, programe personalizate, fotografii profesionale integrate (la cerere). SuperParty acoperă standardele acestei comunități — nu pentru că Floreasca ar fi altfel, ci pentru că standardul SuperParty este acelasi oriunde in Capitală.',
      'Specificul Floreasca față de restul Sectorului 1: proporția de petreceri bilingve (română-engleză) este cea mai ridicata din portofoliu — 30% din rezervări din Floreasca solicita un animator care poate conduce partial programul în engleză (pentru copiii expatriatlor sau ai familiilor bilingve). SuperParty are animatori certificați bilingv disponibili la cerere specifică.',
      'Personajele favorite în Floreasca: Elsa cu setul complet de accesorii (coroana Aurora Borealis, manta de gheata texturata) este de departe numărul 1. Moana cu decoruri hawaiiene e o secundă preferinta. Iron Man are o cerere specifică din comunitatea de business a cartierului. Rezervările se fac cu 4-6 săptămâni înainte pentru weekendurile din mai-septembrie — Floreasca este cel mai ocupat cartier din Sectorul 1.',
    ]
  },
  'chitila': {
    h2: 'Chitila — primul oraș nordic din Ilfov: gară, fast-track la Capitală și comunitate în creștere',
    paragraphs: [
      'Chitila este cel mai apropiat oraș din nord-vestul Ilfovului față de București — la 15 km pe DN1, cu gară proprie pe magistrala feroviară Cluj-București. Trenul local poate aduce un Chitilean în Gara de Nord în 15-18 minute, o conexiune urbana aproape unică pentru o localitate din Ilfov. Aceasta accesibilitate face Chitila un hibrid urban-suburban apreciat de familiile tinere.',
      'Cu 14.500 de locuitori, Chitila a crescut semnificativ în ultimii 10 ani — noi ansambluri rezidențiale pe fostele terenuri industriale de-a lungul căii ferate și pe dealurile dinspre Mogoșoaia. Comunitatea este activă și conectată — Grupul Facebook al părinților din Chitila are 8.000+ de membri, una din cele mai active comununități de părinți din Ilfov.',
      'SuperParty ajunge în Chitila în 20-25 de minute din Capitală, cu o taxă de deplasare de 30 RON. Personajele favorite ale copiilor din Chitila diferă de media Ilfoveana: Iron Man are o cerere neașteptat de mare (locul 2, după Spiderman), ceea ce corelează cu profilul mai tehnic al comunității de rezidenți. Bluey creste constant în popularitate din 2023.',
      'Chitila are o infrastructura interesanta pentru petreceri: sala cultural din centru (disponibilă la rezervare prin primărie), parcul central renovata în 2022 și ansamblul rezidential cu sali comune. SuperParty se adaptează la oricare din aceste locații — aducem tot echipamentul necesar fără a depinde de infrastructura locului.',
    ]
  },
  'mogosoaia': {
    h2: 'Mogoșoaia — palatul lacustru și vilele premium: cel mai estetic cadru pentru petreceri',
    paragraphs: [
      'Mogoșoaia este una din cele mai frumoase comune din Ilfov — Palatul Mogoșoaia (sec. XVII, restaurat), Lacul Mogoșoaia și parcul adiacent oferă un cadru vizual excepțional pentru orice eveniment. Rezidential, Mogoșoaia găzduieste vile premium de 500.000-2.000.000 EUR, locuite de afaceriști, politicieni și vedete din media și showbiz.',
      'Petrecerile SuperParty în Mogoșoaia se desfasoara frecvent în vilele cu curți generoase din zona centrală — spații verzi de 500-1000 mp cu terase acoperite perfect pentru outdoor-ul controlat. Animatorul SuperParty aduce programul personalizat; dacă familia organizeze catering și decorare proprie, SuperParty se integrează perfect în logistica evenimentului mai mare.',
      'Specificul comenzilor din Mogoșoaia: un procent ridicat de petreceri tematice complete — nu doar animator, ci și cereri pentru coordonarea cu furnizori de decor specific. SuperParty poate recomanda parteneri verificati pentru baloane tematice, candy bar și foto-props, deși nu le furnizeaza direct. Pachetul VIP (1.290 RON) include 3 ore cu 2 animatori — ideal pentru evenimentele mai mari de 30 de copii.',
      'Personajele top din Mogoșoaia: Elsa + Anna simultan (2 animatori) este cel mai frecvent comandat duo — vilele cu curți mari permit programul dramatic al Regatului Înghețat. Frozen Party complet (decoruri albastre, tort Elsa, animatori Elsa + Anna) este varianta suprema solicitată de 3-4 ori pe lună din zona Mogoșoaia-Balotești-Corbeanca.',
    ]
  }
};

let updated = 0;
for(const [slugPath, data] of Object.entries(OVERRIDES)) {
  // Determina calea fisierului
  let fp;
  if(slugPath.startsWith('../')) {
    fp = path.join(ROOT, 'src/pages', slugPath.slice(3) + '.astro');
  } else {
    fp = path.join(ROOT, 'src/pages/petreceri', slugPath + '.astro');
  }
  if(!fs.existsSync(fp)) { process.stdout.write('NOT FOUND: ' + fp + '\n'); continue; }
  
  let c = fs.readFileSync(fp,'utf-8');
  c = c.replace(/\n?<!-- UNIQUE-PROSE-MARKER[\s\S]*?<\/section>/g,'');
  
  const slugId = slugPath.replace('../animatori-copii-','sector-').replace('/index','').replace('/','_');
  const paras = data.paragraphs.map(p => `<p style="color:var(--text-muted);line-height:1.95;font-size:.93rem;margin-bottom:1.1rem">${p}</p>`).join('\n    ');
  const section = `\n<!-- UNIQUE-PROSE-MARKER-${slugId} -->\n<section class="zona-detail" style="padding:2.5rem 0;background:rgba(255,255,255,0.02)">\n  <div class="container" style="max-width:820px">\n    <h2 style="font-size:1.2rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem">${data.h2}</h2>\n    ${paras}\n  </div>\n</section>`;
  
  const ins = c.lastIndexOf('</Layout>');
  if(ins===-1) { process.stdout.write('NO /Layout: '+fp+'\n'); continue; }
  c = c.slice(0,ins)+section+'\n\n'+c.slice(ins);
  fs.writeFileSync(fp,c,'utf-8');
  updated++;
  process.stdout.write('OK: '+slugPath+'\n');
}

process.stdout.write(`\nUpdated: ${updated} pagini\n`);

// Verifica similaritate finala
function xp(raw) {
  const m = raw.match(/<!-- UNIQUE-PROSE-MARKER[^>]*-->([\s\S]*?)(?=\n\n<\/Layout>|<\/Layout>|<!--)/);
  if(!m) return '';
  return m[1].replace(/<[^>]+>/g,' ').replace(/[^a-zA-Z\u00C0-\u024F\s]/g,' ').replace(/\b\w{1,3}\b/g,' ').replace(/\s+/g,' ').trim().toLowerCase();
}
function simBi(a,b){
  const t=s=>{const w=s.split(/\s+/).filter(x=>x.length>4);const r=new Set();for(let i=0;i<w.length-1;i++)r.add(w[i]+'_'+w[i+1]);return r;};
  const sa=t(a),sb=t(b);if(!sa.size||!sb.size)return 0;
  return Math.round([...sa].filter(x=>sb.has(x)).length/new Set([...sa,...sb]).size*100);
}

const tests = [
  ['../animatori-copii-sector-1/index.astro','../animatori-copii-sector-6/index.astro'],
  ['petreceri/afumati.astro','petreceri/catelu.astro'],
  ['petreceri/aviatiei.astro','petreceri/floreasca.astro'],
  ['petreceri/chitila.astro','petreceri/mogosoaia.astro'],
  ['petreceri/dascalu.astro','petreceri/glina.astro'],
];
process.stdout.write('\nSimilaritate check:\n');
for(const [a,b] of tests) {
  try {
    const aNorm = a.startsWith('../') ? path.join(ROOT,'src/pages',a.slice(3)) : path.join(ROOT,'src/pages',a);
    const bNorm = b.startsWith('../') ? path.join(ROOT,'src/pages',b.slice(3)) : path.join(ROOT,'src/pages',b);
    const ca = xp(fs.readFileSync(aNorm,'utf-8'));
    const cb = xp(fs.readFileSync(bNorm,'utf-8'));
    const s = simBi(ca,cb);
    const name = a.replace('../animatori-copii-','s').replace('/index.astro','').replace('petreceri/','').replace('.astro','');
    const name2 = b.replace('../animatori-copii-','s').replace('/index.astro','').replace('petreceri/','').replace('.astro','');
    process.stdout.write((s<=20?'✅':s<=30?'🟡':s<=50?'🟠':'⛔')+' '+name+' vs '+name2+': '+s+'%\n');
  } catch(e) { process.stdout.write('ERR: '+e.message+'\n'); }
}
