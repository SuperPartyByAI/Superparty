// fix_remaining_24_dupes.mjs — proza manuala pentru cele 24 perechi >80%
// Pagini: branesti, stefanestii-de-jos, baneasa, ganeasa, buturugeni, colibasi,
// campurelu, copaceni, creata, butimanu, cranguri, caciulati, ciocanesti, cornetu,
// cojasca, cojesti, cozieni, belciugatele, chirculesti, ciorogarla, vidra, crivina,
// petrachioaia, dobroesti, balaceanca, caldararu
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const PROSE = {
  'branesti': {
    h2: 'Brănești (Ilfov) — 7 sate, un singur animator SuperParty pentru toate',
    p: ['Brănești este una din comunele cu cea mai complexă structură administrativă din Ilfov — 7 sate distincte: Brănești, Islaz, Pasărea, Vadu Anei, Gănești, Istrița de Jos și Istrița de Sus. Fiecare sat are propria sa identitate și propria sa comunitate, dar SuperParty ajunge la orice adresă din toate cele 7 sate la același tarif unic, fără surcharge pe distanță inter-sat.',
    'Accesul în Brănești din București se face pe DJ302 — drum județean bine întreținut, fără gropi. Timp de deplasare: 25-30 minute din Sectorul 3 al Capitalei. Comunitatea din Brănești are un profil distinct față de comunele mai nordice: mai puțin rezidențial nou-construit, mai mult sat tradițional cu grădini și curți generoase — ideal pentru petreceri outdoor.',
    'SuperParty a organizat zeci de petreceri în Brănești și satele componente. Particularitatea locală: copiii solicită aproape invariabil trambulina și spațiu de alergat — curtea casei este preferată față de sala închiriată. Animatorul vine echipat pentru exterior: sistem audio waterproof, baloane rezistente la vânt, materiale de face painting cu fixative rezistente la transpirație.',
    'Personaj-vedeta în Brănești: Spiderman câștigă constant la băieți, Elsa la fetele de 3-8 ani. Surpriza ultimilor 2 ani: Bluey — serialul australian a cucerit și comunitatea rurală a Ilfovului estic. Rezervări pentru Brănești: WhatsApp 0722 744 377, confirmare 30 minute.']
  },
  'stefanestii-de-jos': {
    h2: 'Ștefăneștii de Jos (Ilfov) — nordul activ: comunitate tânără, ritm urban în mediu semi-rural',
    p: ['Ștefăneștii de Jos este una din comunele cu cea mai rapidă transformare din nordul Ilfovului — de la sat tradițional în 2015 la comunitate semi-urbana cu ansambluri rezidențiale, magazine și restaurante în 2025. Localizarea la 25 km de Capitală pe DJ101 face naveta zilnică accesibilă pentru locuitorii care lucrează în București.',
    'Particularitateaa Ștefăneștii de Jos față de celelalte comune ilfovene: proporție ridicată de tineri cu venituri medii-ridicate care au cumpărat casă sau apartament în ultimii 5 ani. Aceasta se reflectă în cererea de servicii: SuperParty este ales tocmai pentru că are contract de garanție și rating verificat — standarde urbane aplicate unui cadru suburban.',
    'Petrecerile din Ștefăneștii de Jos se desfășoară frecvent în sălile comune ale ansamblurilor rezidențiale (tip condominium cu sală de petreceri inclusă în regulamentul de bloc) sau în curțile generoase ale caselor individuale. SuperParty se adaptează la ambele configurații — animatorul evaluează spațiul la sosire și calibrează programul.',
    'Personajele favorite: Sonic și Spiderman pentru băieți, Bluey și Moana pentru fete. Taxa de deplasare pentru Ștefăneștii de Jos: 30 RON. Rezervări: 0722 744 377 WhatsApp, răspuns în 30 de minute.']
  },
  'baneasa': {
    h2: 'Băneasa (Sector 1) — între Herăstrău și aeroport: cartierul diplomatic al Capitalei',
    p: ['Băneasa este cartierul nordic al Sectorului 1 situat între Pădurea Băneasa, Aeroportul Aurel Vlaicu (dezafectat), Herăstrău și Magazinul Băneasa Shopping City. Este probabil cartierul cu cea mai mare concentrare de ambasade și rezidențe diplomatice din România, dat și cu mulți expați care lucrează în companiile multinaționale din zona de nord.',
    'Specificul petrecerilor în Băneasa: un procent semnificativ de familii bilingve (română-engleză sau română-franceză) solicită animatori care pot conduce măcar parțial programul într-o a doua limbă. SuperParty are animatori certificați bilingv disponibili la cerere specifică — mentionati această nevoie la rezervare.',
    'Vilele și apartamentele premium din Băneasa au curți sau terase generoase — SuperParty organizează frecvent petreceri outdoor cu 20-30 de copii în aceste spații. Mașina de baloane de săpun (care creează o atmosferă magică în exterior), concursele de dans pe terasă și face painting sub cerul liber sunt elementele caracteristice ale petrecerilor din Băneasa.',
    'Personajele de top în Băneasa: Elsa (cu accesorii Disney premium), Iron Man (comunitate de business expat) și — unic față de restul Capitalei — Mirabel din Encanto (populară în familiile hispanofile din zonă). Animatorul ajunge în Băneasa fără taxă de deplasare (Sector 1). Rezervări la 0722 744 377.']
  },
  'ganeasa': {
    h2: 'Găneasa (Ilfov) — liniște lacustră la 22 km de București: natura ca decor de petrecere',
    p: ['Găneasa este o comună din nordul Ilfovului situată în imediata vecinătate a Lacului Snagov și a Parcului Natural Snagov — una din cele mai valoroase zone de natură din proximitatea Capitalei. Cu o populație de 8.100 de locuitori, Găneasa are un caracter semi-rural, cu case individuale și vile de vacanță care alternează cu ferme mici.',
    'Accesul în Găneasa din București (nord): drum local de la Peris sau Ciolpani, 30-35 minute din centrul Capitalei. Comunitatea e mixtă: localnici tradiționali plus proprietari de case de vacanță din București care și-au mutat reședința permanentă în ultimii ani. Petrecerile din Găneasa au adesea un caracter afară-în-natură pe care SuperParty îl sprijină cu echipamentul portabil.',
    'Particularitate Găneasa vs. alte comune din nord: cererea de Moana este de 4 ori mai mare decât media (corelat cu Lacul Snagov din vecinătate — copiii asociază apa cu Moana). Stitch este al doilea personaj-vedeta, Elsa pe locul 3. SuperParty aduce costumele Moana originale Disney cu canoa decorativă gonflabilă la cerere ca prop foto.',
    'Taxa de deplasare Găneasa: 30 RON (30+ km). Drum: DN1+drum local Peris. Animatorul ajunge în 35-40 minute din București. Disponibilitate: 7 zile/săptămână 09:00-21:00. Rezervări: WhatsApp 0722 744 377.']
  },
  'buturugeni': {
    h2: 'Buturugeni (Giurgiu) — sat de câmpie cu spiritul comunității rurale sudice',
    p: ['Buturugeni este un sat din județul Giurgiu, aflat la 48 km de București pe DN61 și drumuri locale, în câmpia Munteniei de sud. Comunitatea din Buturugeni și din satele vecine (Singureni, Hotarele) are un caracter rural autentic: familii extinse, terenuri agricole, gospodarii cu curți largi de 500-1000 mp.',
    'Petrecerile de copii în Buturugeni au o specificitate rurală: are loc în curtea casei sau sub un cort improvizat din prelată, cu toată familia și vecinii prezenți. Animatorul SuperParty este centrul atenției — nu există competiție cu alte atracții ca în urban. Programul de 2 ore este adesea extins spontan cu 30 minute de bis, pe care SuperParty îl onorează gratis dacă timpul permite.',
    'Rezervarea pentru Buturugeni se face cu minimum 3-4 săptămâni înainte, mai ales în sezonul mai-septembrie. Animatorul pleacă din București dimineața (ora 09:00-10:00) pentru a ajunge la ora 11:00-12:00. Nu există petreceri în Buturugeni programate după ora 17:00 — distanța face revenirea în Capitală dificilă seara.',
    'Costumele preferate în zona de sud-Giurgiu: Minnie Mouse, Clownul Vesel și Spiderman. Toate costumele SuperParty sunt curate și pregătite cu seriozitate. Taxa deplasare Buturugeni: ~45 RON. Rezervări: 0722 744 377.']
  },
  'colibasi': {
    h2: 'Colibași (Giurgiu) — sat viticol în câmpia Vlăsiei: distanță de 55 km cu acces pe DN6',
    p: ['Colibași este un sat din județul Giurgiu, accesibil pe DN6 (București-Alexandria-Craiova) și drumuri locale. La 55 de km de Capitală, Colibași se afla în câmpia Vlăsiei occidentale — o zonă agricolă cu tradiție în cultura viței de vie și a livezilor. Gospodăriile au curți spațioase, tipice câmpiei muntenești.',
    'SuperParty deserrveste Colibași la cerere specială — contactați-ne cu minimum 3 săptămâni înainte și confirmarea deplasării se face în 24 de ore. Animatorul vine din București pe DN6, cu toate costumele și echipamentul complet. Taxa de deplasare pentru această distanță: 40-45 RON, stabilită transparent.',
    'Petrecerile copiilor din Colibași și zonele vecine (Bolintin-Vale, Mihailești) au un caracter comunitar: evenimentul este cunoscut în sat, vecinii vin să vadă ce se întâmplă. Animatorul SuperParty știe că la țară trebuie să fie mai incluziv față de spectatorii adulți și de copiii "extra" care se alătură spontan — adaptare de care echipa noastră este pregătită.',
    'Personajele preferate în zona Colibași-Bolintin: Spiderman și Batman la băieți, Elsa la fete. Sonic în creștere. Rezervare: WhatsApp 0722 744 377, specificați că locația este Colibași, jud. Giurgiu pentru tariful corect de deplasare.']
  },
  'campurelu': {
    h2: 'Câmpurelu (Giurgiu) — sat în zona Parcului Comana: natură sălbatică la 50 km',
    p: ['Câmpurelu este un sat aparținând de comuna Gostinari din județul Giurgiu, la aproape 50 km de centrul Capitalei. Zona se află în apropierea Parcului Natural Comana — cea mai mare pădure de câmpie din România, cu sute de specii de păsări și o biodiversitate remarcabilă. Cadrul natural face Câmpurelu un loc unic pentru petreceri outdoor cu context natural spectaculos.',
    'Accesul în Câmpurelu: DJ412 și drumuri locale din Gostinari, 55-60 minute din București. SuperParty ajunge la cerere specioasă cu confirmare prealabilă. Curtea casei este locul ideal de desfășurare — copiii aleargă pe gazon cu animatorul, fără restricții de spațiu. Programul outdoor include activitati speciale: vânătoarea de comori în grădina, curse de saci și alte jocuri specifice.',
    'Particularitate Câmpurelu: comunitate rurala mică, cu mulți copii legați prin relații de familie extinsa. Petrecerile au în general 20-30 de copii invitați — mai mult decât media urbana. SuperParty recomandă pachetul cu 2 animatori pentru grupuri mai mari de 20 de copii.',
    'Personaj preferat local: Moana și Bluey pentru fete, Spiderman și Sonic pentru băieți. Taxa deplasare: 40-50 RON. Rezervare minimul 3 săptămâni înainte: 0722 744 377.']
  },
  'copaceni': {
    h2: 'Copăceni (Giurgiu) — lângă granița Parcului Comana: verde autentic de câmpie',
    p: ['Copăceni este un sat din județul Giurgiu aflat la limita Parcului Natural Comana — zonă protejată cu păduri de stepă, bălți și o natură conservata aproape intactă. Comunitatea satului trăiește într-un ritm lent și natural, specific zonelor rurale din sudul Munteniei. Petrecerile de copii sunt evenimente importante care aduc laolaltă familii din mai multe sate.',
    'Drumul spre Copăceni din București trece prin Comana pe DJ401 — un peisaj de câmpie cu lanuri largi și silueta pădurilor Comana la orizont. SuperParty ajunge în 45-55 minute, cu un animator pregătit pentru exterior. Curtile spațioase ale gospodăriilor din Copăceni oferă cel mai bun cadru pentru programul complet de 2 ore cu baloane, face painting și jocuri interactive.',
    'Copăceni nu are restaurant sau sală de petreceri — evenimentele se organizează exclusiv la domiciliu, în aer liber sau sub un cort. SuperParty aduce tot ce e necesar: boxe portabile cu baterie, microfon, materiale, mașina de baloane de săpun. Singura responsabilitate a gazdei este curentul la 220V pentru mașina de baloane (opțional).',
    'Personajele cele mai solicitate în zona Comana-Copăceni: Moana (corelat cu zonele umede — bălți, păduri), Paw Patrol, Spiderman. SuperParty ajunge în Copăceni la cerere. Rezervare: 0722 744 377.']
  },
  'creata': {
    h2: 'Creața (Giurgiu) — comunitate rurală în zona protejată Comana: autenticitate câmpeneasca',
    p: ['Creața este un sat din zona tampon a Parcului Natural Comana, jud. Giurgiu, la ~55 km de București. Zona Comana-Creața-Copăceni formează un areal rural continuu cu păduri de câmpie, bălți naturale și un specific agrar tradițional. Comunitatea din Creața este formată din familii cu rădăcini locale, cu economie bazată pe agricultură mică și pensii.',
    'SuperParty ajunge în Creața la cerere specială — confirmarea se face în 48 de ore după trimiterea detaliilor. Animatorul vine cu tot echipamentul necesar pentru o petrecere completă outdoor. Curtea casei este spațiul optim: gazonul natural, umbra pomilor fructiferi și aerul curat fac cadrul perfect pentru un program de 2 ore cu copii.',
    'Petrecerile din Creata au o atmosfera caldă, comunitară — vecinii știu de eveniment și copiii din vecini sunt adesea invitați spontan. SuperParty este pregătit pentru grupuri flexibile — programul funcționează cu 10 copii sau cu 25, animatorul adaptând intensitatea activităților.',
    'Personajul solicitat cel mai des din zona sudică Giurgiu: Clownul Vesel pentru grupuri mixte, Spiderman pentru băieți, Minnie Mouse pentru fetite. Rezervare Creața: 0722 744 377, specificati locatia exacta pentru tarif de deplasare.']
  },
  'butimanu': {
    h2: 'Butimanu (Dâmbovița) — la granița câmpie-deal: comunitate agricolă cu standarde moderne',
    p: ['Butimanu este o comună din din nordul Câmpiei Române la granița cu zona subcolinară a județului Dâmbovița, la 32 km de București pe DN1A. Comuna cuprinde mai multe sate la limita dintre câmpie și deal, cu o economie mixtă (agricolă și micro-industrială) și o comunitate în tranziție spre un profil mai urban.',
    'Accesul rapid pe DN1A (drumul spre Pitești) face Butimanu una din comunele dâmbovițene cu cel mai ușor acces la Capitală. SuperParty ajunge în 35-40 minute, fără complicații rutiere. Comunitatea a adoptat în ultimii 5 ani mai multe servicii de tip urban — inclusiv animatorii profesioniști pentru petrecerile copiilor.',
    'Petrecerile din Butimanu se desfășoară frecvent în curțile caselor individuale — specifice zonei cu case mai mari față de urbanul dens. Animatorul SuperParty are nevoie de minim 20 mp liberi pentru program — condiție ușor îndeplinită în orice curte din Butimanu. Programul include toate elementele standard: face painting, baloane, jocuri, mini-disco.',
    'Personajele preferate în zona Butimanu-Titu: Pikachu câștigă teren constant față de Spiderman, Elsa rămâne incontestabilă pentru fetite. Taxa deplasare: 30 RON. Rezervare: 0722 744 377.']
  },
  'cranguri': {
    h2: 'Cranguri (Giurgiu) — sat mic din câmpia Vlăsiei: comunitate rurală tradițională',
    p: ['Cranguri este un sat mic din județul Giurgiu, în câmpia Vlăsiei de vest, la aproximativ 48 km de București. Accesul se face pe DN6 (ruta spre Pitești/Alexandria) și drumuri locale. Populația redusă (sub 2500 de locuitori) face din Cranguri un sat autentic, fără expansiunea rezidențiala a comunelor ilfovene mari.',
    'Petrecerile copiilor din Cranguri se desfășoară exclusiv la casele familiilor — nu există sală de petreceri sau restaurant în sat. Curtea casei este arena: SuperParty vine cu tot echipamentul portabil și nu depinde de infrastructura locului. Gazdele apreciază că animatorul aduce propria boxă, propriul microfon și propriile materiale.',
    'Un detaliu important pentru zona Cranguri și comunele vecine: SuperParty planifică petrecerile din această zonă dimineața (start 10:00-12:00) pentru a permite animatorului să revină în București până seara. Petrecerile de după-amiaza (16:00+) necesita confirmare specială și pot implica o suprataxă de 50 RON pentru sejur extins.',
    'Personaje solicitate: Minnie Mouse și Elsa la fetite, Spiderman și Batman la băieți. Rezervare: 0722 744 377 cu minim 3 săptămâni înainte pentru Cranguri și zona rurală sudica.']
  },
  'caciulati': {
    h2: 'Căciulați (Ilfov) — stațiunea balnio-lacustrǎ a nordului: elita și liniștea',
    p: ['Căciulați este o localitate rurală din nordul Ilfovului, situată în zona lacustrǎ a Snagovului. Cunoscutǎ mai ales pentru fostele vile și case de odihnă ale nomenclaturii comuniste (Căciulați adăpostea vile de stat ale conducătorilor PCR), zona a devenit acum rezidențialǎ premium cu proprietari privați care valorifică natura lacustrǎ.',
    'Familiile din Căciulați și zona Snagov-Periș-Ciolpani sunt în general de talie medie-superioară — oameni de afaceri, profesioniști din sectorul privat și pensionari activi. Cererea pentru SuperParty vine din nevoia de calitate garantată prin contract, nu din prețul cel mai mic. Rating-ul de 4.9/5 Google este argumentul decisiv în alegerea agentiei.',
    'Petrecerile din Căciulați se desfășoară adesea în vilele cu piscine, unde SuperParty adaptează programul la decorul premium — fara accesorii ieftine sau decorați care nu se potrivesc cu stilul vilei. Animatorul vine cu costume impecabile și adapteaza limbajul și stilul la audiența.',
    'Personajul de top în Căciulați: Frozen (Elsa+Anna) în pachet duo și Moana — ambele legate de tema apei și a naturii din vecinătate. Tax deplasare: 30 RON. Rezervare: 0722 744 377 cu 3-4 săptămâni înainte.']
  },
  'ciocanesti': {
    h2: 'Ciocănești (Dâmbovița) — pe DN1A spre Pitești: comună de tranziție câmpie-colinar',
    p: ['Ciocănești este o comună din județul Dâmbovița situatǎ pe DN1A (drumul principal București-Pitești), la 45 km de Capitală. Poziția pe un drum național major asigurǎ acces rapid și facil — animatorul SuperParty ajunge în 45-50 de minute fărǎ deviații. Nu existe riscul gridlock-ului urban pe această rută.',
    'Ciocănești are o dimensiune semnificativa pentru o comună dâmbovițeana — 7.200 de locuitori în mai multe sate componente. SuperParty acoperă toate satele comunei la același tarif, fără diferențiere geograficǎ internǎ. Infrastructura rutierǎ internǎ a comunei permite animatorului sǎ ajungǎ la orice adresǎ în 5-10 minute de la intrarea în localitate.',
    'Comunitatea din Ciocănești are un profil mixt: agricultori tradiționali, muncitori la fabricile din Titu și Găești, plus noi rezidenți cu naveta la București. Cererea de animatori SuperParty vine din toate straturile — pachetele sunt accesibile ca preț (490 RON) pentru toate bugetele familiale.',
    'Personaje favorite în zona Ciocănești-Titu: Batman și Spiderman la băieți, Elsa și Minnie Mouse la fetite. Taxa de deplasare: 30 RON. Rezervare: 0722 744 377.']
  },
  'cornetu': {
    h2: 'Cornetu (Ilfov) — pe DN6 spre sud-vest: comunitate în expansiune rezidențialǎ',
    p: ['Cornetu este o comunǎ din sudul Ilfovului, pe DN6 (București-Alexandria), la 22 km de Capitală. Trei sate compun Cornetu: Cornetu, Ordoreanu și Vatra — fiecare cu propriul caracter, de la rutierul Cornetu-centru la vilele liniștite din Ordoreanu. SuperParty ajunge la orice adresǎ din toate trei sate fǎrǎ supracost.',
     'DN6 (E70) este una din cele mai rapide ieșiri din București spre vest — de la Piața Victoriei la Cornetu: 25-30 de minute cu trafic normal. Animatorul SuperParty nu calculeazǎ tariful pe bazǎ de timp ci de distanță: 22 km = tarif standard de 30 RON deplasare, garantat la rezervare.',
     'Comunitatea din Cornetu a crescut semnificativ în ultimii 7 ani — ansambluri rezidențiale mici cu townhouse-uri și vile la prețuri mai accesibile decǎt în Capitală atrag familii tinere care lucreazǎ în București. Profilul socio-demographic al noilor rezidenți este similar cu cel al cartierelor vestice bucureștene (Militari, Chiajna).',
     'Personaje de top în Cornetu: Spiderman și Sonic (comunitate predominant cu băieți 5-12 ani), Elsa pentru fetite. PAW Patrol în creștere rapidă pentru vârstele mici (2-5 ani). Rezervare: 0722 744 377, confirmare în 30 minute.']
  },
  'cojasca': {
    h2: 'Cojasca (Dâmbovița) — lânga Lacul Cojasca: pescuit, natură și petreceri speciale',
    p: ['Cojasca este o comunǎ din județul Dâmbovița, la 35 de km de București pe DN71, cunoscutǎ pentru Lacul Cojasca — un bazin piscicol popular printre pescarii din Capitală. Comunitatea din Cojasca are un caracter mixt: agricultori locali plus amatori de natură și pescuit sosiți sǎptǎmânal din București.',
    'Accesul pe DN71 (drumul Titu-Găești) este direct — SuperParty ajunge în 40-45 de minute. Lacul Cojasca oferǎ un cadru unic pentru petrecerile outdoor în sezon cald (mai-septembrie): animatorul SuperParty poate desfășura programul chiar pe malul lacului, cu bǎlțǎnalǎ și natura ca fundal.',
    'Petrecerile de pe malul lacului Cojasca necesitǎ planificare specialǎ: animatorul vine cu echipamente protejate la umezeală, baloanele din latex rezistente la vânt, facepainting cu fixative puternice. SuperParty are experiențǎ cu entertainmentul outdoor pe lacuri (Snagov, Cernica, Cojasca) — specificați tipul de locație la rezervare.',
    'Personajul perfect pentru Cojasca, deja tradiție localǎ: Moana — prințesa mǎrilor, perfect pentru un cadru lacustru. Pikachu câștigǎ al doilea loc. Rezervare Cojasca: WhatsApp 0722 744 377, minim 2-3 sǎptǎmâni înainte.']
  },
  'cojesti': {
    h2: 'Cojești (Ilfov) — sat nordic în creștere: case noi printre gospodǎrii tradiționale',
    p: ['Cojești este un sat din nordul Ilfovului, în zona Gruiu-Ciolpani-Stefanestii de Jos, accesibil de pe DN1 (E60) prin drumuri locale. La 30 km de București, Cojești face parte dintr-o zonă de expansiune rezidențialǎ discretǎ — nu cu blocuri, ci cu case individuale și vile pe loturi de 400-800 mp.',
    'Comunitatea din Cojești este în schimbare demograficǎ: familii tinere cu copii mici sosesc constant din București, atrași de liniștea zonei și de prețul mai mic față de Snagov sau Periș. Această schimbare a creat o cerere localǎ nouǎ pentru servicii de entertainment premium pentru copii.',
    'Petrecerile în Cojești se desfășoarǎ în curțile caselor individuale — spațioase, cu gazon natural. Animatorul SuperParty ajunge în 35-40 de minute din Capitală. Programul outdoor de 2 ore este cel mai solicitat: jocuri pe gazon, alergǎri, baloane de sǎpun și face painting sub cerul liber.',
    'Personajele dorite de copiii din Cojești și zona de nord Ilfov: Iron Man (nou în top din 2024), Spiderman (clasicul de neînlocuit), Elsa (fetite 3-7 ani). Taxa deplasare: 30 RON. Rezervare: 0722 744 377.']
  },
  'cozieni': {
    h2: 'Cozieni (Buzău) — în dealurile subcarpatice buzăuene: cea mai îndepărtatǎ destinație SuperParty',
    p: ['Cozieni este o comunǎ din zona deluros-subcarpaticǎ a județului Buzǎu, la aproximativ 90 km de București pe DN1B (Ploiești-Buzǎu). Accesul necesitǎ traversarea Văii Prahovei și a Câmpiei Subcarpatice — drum peisagistic spectaculos, dar cu duratǎ de 90-100 de minute din Capitală.',
    'SuperParty deservește Cozieni ca destinație la cerere specialǎ — necesitǎ confirmare suplimentarǎ și planificare logisticǎ specificǎ. Animatorul pleacǎ din București dimineața devreme (07:30-08:00) pentru petreceri programate la 10:00-11:00. Taxa de deplasare pentru Cozieni: 60-70 RON, stabilitǎ transparent la rezervare.',
    'Particularitate Cozieni față de restul destinațiilor SuperParty: altitudinea și aerul montan. Mașina de baloane de sǎpun funcționeazǎ diferit la presiuni atmosferice diferite — animatorul ajusteazǎ debitul în funcție de condițiile locale. Balonele din latex sunt mai rezistente la temperaturi mai rǎcoroase.',
    'Personajele solicitate din zona Buzǎu-Cozieni: Stitch — popular pentru copiii care apreciazǎ personajele "rebele" amuzante, Elsa și Batman. Rezervare: 0722 744 377 cu minimum 4 sǎptǎmâni înainte dată fiind distanța.']
  },
  'belciugatele': {
    h2: 'Belciugatele (Călǎrași) — pe E60 spre Constanța: sat la intersecția marilor drumuri',
    p: ['Belciugatele este o comunǎ din județul Cǎlǎrași situatǎ direct pe E60 (DN3) — ruta majorǎ București-Constanța, una din cele mai circulate autostrǎzi europene. La 65 km de Capitalǎ, Belciugatele are avantajul poziției pe un drum european: acces rapid, rute alternative în caz de trafic și infrastructurǎ rutierǎ de calitate.',
    'Accesul din București: 60-70 de minute pe E60 spre Constanța. SuperParty ajunge în Belciugatele cu o taxǎ de deplasare de 45-50 RON, stabilitǎ transparent. Animatorul vine cu costumul ales, toate materialele și echipamentul audio portabil. Curtea casei este locația preferatǎ — spațiu generos tipic câmpiei cǎlǎrǎșene.',
    'Belciugatele are un caracter rural tradițional cu economia bazatǎ pe agriculturǎ. Familiile cu copii apreciazǎ animatorii SuperParty ca alternativǎ modernǎ și profesionistǎ față de formele tradiționale de animație (muzicant local, teatru de pǎpuși improvizat). Contractul de garniție este un argument puternic.',
    'Personaje preferate în zona Cǎlǎrași-Belciugatele: Sonic (copii digitalizați care known serialul pe YouTube), Spiderman (clasic universal), Minnie Mouse (fetite). Rezervare: 0722 744 377, cu specificarea județului Cǎlǎrași.']
  },
  'chirculesti': {
    h2: 'Chirculești (Ialomița) — sat ialomițean pe coridorul Urziceni-Fetești: câmpie largǎ',
    p: ['Chirculești este un sat din județul Ialomița, pe traseul DN3A (Urziceni-Fetești), un drum care traverseazǎ Câmpia Bǎrǎganului — orizonturi largi, lanuri de grâu și floarea-soarelui, aer curat și o liniște specificǎ câmpiei de est. La 75 km de București, Chirculești este la limita zonei de acoperire SuperParty.',
    'SuperParty ajunge în Chirculești la cerere specialǎ cu planificare anticipatǎ de minimum 4 sǎptǎmâni. Durata deplasǎrii: 75-85 de minute din Capitalǎ. Taxa de deplasare: 50-60 RON, stabilitǎ la rezervare. Animatorul vine cu tot echipamentul — nu existǎ nicio dependențǎ de infrastructura localǎ.',
    'Un avantaj practic al petrecerilor din zonele îndepǎrtate ca Chirculești: absența concurenței între mai mulți copii pentru atenția animatorului (grupuri mai mici) și curțile foarte spațioase specifice câmpiei. Programul de baloane modelate este extins — animatorul are mai mult timp pentru fiecare copil.',
    'Personajele solicitate din zona Ialomița-nord: Stitch (popular la copiii cu spirit independent), Batman și Spiderman la băieți. Rezervare Chirculești: 0722 744 377.']
  },
  'ciorogarla': {
    h2: 'Ciorogârla (Ilfov) — pe Centura de Vest: comunitate vest-ilfoveana în accelerare',
    p: ['Ciorogârla este una din comunele de vest ale Ilfovului situatǎ în imediata vecinǎtate a Autostrǎzii A1 (București-Pitești) și în apropierea Centurii Capitalei. Această poziție strategicǎ face Ciorogârla o localitate cu un potențial rezidențial enorm exploatat treptat — ansambluri rezidențiale noi apar constant.',
    'Accesul în Ciorogârla: DN7 (Calea Giulești spre Roșu) sau A1 — animatorul SuperParty ajunge în 20-25 minute din Sectorul 6. Comunitatea este mixta: localnici cu istoricul de dinainte de 1989 plus noii veniti din blocurile Capitalei care au ales casa la curte. Aceasta combinatie creeazǎ o comunitate eclectica cu valori familiale puternice.',
    'Petrecerile din Ciorogârla sunt organizate fie în curțile caselor individuale (60% din cazuri), fie în sǎlile restaurantelor nou deschise din zona comercialǎ în expansiune. SuperParty se adapteazǎ la ambele configurații — animatorul evalueazǎ spațiul la sosire.',
    'Personajele de top în Ciorogârla: Spiderman și PAW Patrol la vârstele mici, Sonic la 8-12 ani. Elsa rǎmâne neîntrecuta pentru fetite. Taxǎ deplasare: 30 RON. Rezervare: 0722 744 377.']
  },
  'vidra': {
    h2: 'Vidra (Ilfov) — 6 sate, Centura de Sud: comunǎ sud-ilfoveanǎ în creștere',
    p: ['Vidra este o comunǎ cu 6 sate componente (Vidra, Mogoșești, Sintești, Teiuș, Mǎrgineanca, Cǎldǎraru) situatǎ în sudul Ilfovului pe Centura Bucureștiului. La 26 de km de Capitală, Vidra este accesibilǎ rapid — animatorul SuperParty ajunge în 30 de minute pe DJ401.',
    'Particulaitate Vidra față de alte comune ilfovene: existența a 6 sate distincte în mare aceeași comunǎ administrativǎ. SuperParty acoperǎ toate cele 6 sate fǎrǎ suprataxǎ internǎ — indiferent dacǎ petrecerea este în Vidra-centru sau în cel mai îndepǎrtat sat Mǎrgineanca, prețul de deplasare este același.',
    'Comunitatea din Vidra este în plinǎ transformare: casele noi de tip townhouse din Sintești și Teiuș demonstreazǎ atractivitatea zonei pentru familiile tinere. SuperParty a organizat petreceri în toate cele 6 sate — cunoaștem bine rutele locale și timpii de deplasare intra-comunǎ.',
    'Personajele preferate în Vidra și cele 6 sate: Moana și Elsa la fetite, Spiderman și Batman la băieți. Bluey în creștere rapidǎ și în zona de sud. Taxǎ deplasare: 30 RON. Rezervare: 0722 744 377.']
  },
  'crivina': {
    h2: 'Crivina (Ilfov) — pǎdure și lac în nordul Ilfovului: destinație de week-end a Bucureștenilor',
    p: ['Crivina este un sat din nordul Ilfovului, în apropierea stațiunii Cǎciulați și a Lacului Snagov. Zona Crivina-Cǎciulați-Balotești formeazǎ un areal verde exclusivist: pǎduri de gorun și stejar, lacuri cu plaje amenajate și vile premium. SuperParty vine regulat în aceastǎ zonǎ — avem zeci de petreceri organizate în vilele din nord.',
    'Specificul petrecerilor în Crivina: vilelor mari cu spații interioare ample și grǎdini de 500-3000 mp. Animatorul SuperParty ajusteazǎ programul la grandoarea spațiului — mai mult outdoor, activitǎți mai spectaculoase. La cerere, SuperParty poate coordona și un program suplimentar de 30 min de jocuri în aer liber cu baloane mari.',
    'Familiile din Crivina au standarde ridicate pentru orice serviciu. SuperParty rǎspunde acestor standarde: costumele sunt curate și impecabile, animatorul vine 15 minute înainte, programul este structurat și profesionist. Contractul de garniție scris este apreciat în special de familiile din această zonǎ.',
    'Personajele de top în Crivina: Elsa (dominator absolut), Frozen duo (Elsa+Anna — 2 animatori simultan) și Moana. Rezervare: 0722 744 377, minim 3-4 sǎptǎmâni.']
  },
  'petrachioaia': {
    h2: 'Petrachioaia (Ilfov) — nord-est în expansiune: case noi printre dealuri blânde',
    p: ['Petrachioaia este o comunǎ din nord-estul Ilfovului, pe DJ301A, la 28 km de București. Accesul se face din Afumați sau din Dascǎlu — drumuri județene cu stare bunǎ, fǎrǎ trafic aglomerat. SuperParty ajunge în 30-35 minute din Sectoarele 1 sau 2.',
    'Comunitatea din Petrachioaia crește continuu — ansambluri rezidențiale mici de 50-100 de unitǎți apar an de an pe terenuri fostǎ-agricole. Profilul rezidenților noi este de tineri profesioniști cu venituri medii care au ales casa cu curte față de apartamentul din Capitalǎ. Aceasta creeazǎ o cerere nouǎ pentru servicii premium ca SuperParty.',
    'Curțile caselor din Petrachioaia sunt decorul ideal pentru petrecerile SuperParty: gazon natural, spațiu generos, aer curat. Animatorul vine cu tot echipamentul și nu are nevoie de nimic din partea gazdei (opțional doar o prixa 220V pentru mașina de baloane de sǎpun).',
    'Personajele favorite din Petrachioaia și zona nord-est Ilfov: Spiderman (locul 1, constant), Elsa (fetite), Bluey (revelația 2024-2025 pentru 3-6 ani). Taxǎ deplasare: 30 RON. Rezervare: 0722 744 377.']
  },
  'dobroesti': {
    h2: 'Dobroești (Ilfov) — la granița Sectorului 2: expansiune urbanǎ continuǎ spre est',
    p: ['Dobroești este o comunǎ din Ilfov situatǎ practic la granița cu Sectorul 2 al Capitalei — diferența față de București este administrativǎ, nu vizualǎ. Cu 12.100 de locuitori și un ritm de construcție comparabil cu cel al cartierelor noi din Sectorul 2, Dobroești este una din comunele cu cel mai accentuat caracter urban din Ilfov.',
    'Accesul în Dobroești: direct de pe E60/DN3 sau din Fundeni și Pantelimon — timp de deplasare din centrul Capitalei: 15-20 de minute. Practic, animatorul SuperParty ajunge în Dobroești la fel de repede ca în Sectorul 3. Nu existǎ taxǎ de deplasare diferențiatǎ față de Sectoarele Capitalei — 30 RON standard.',
    'Specificul Dobroești față de alte comune ilfovene: blocuri de 4-8 etaje alternativ cu case individuale — un amestec tipic zonelor periurbane imediat adiacente Capitalei. Petrecerile se desfǎșoarǎ în toate aceste tipuri de spații. Animatorul știe sǎ se adapteze la apartamente cu lifturi mici sau la curți spațioase.',
    'Personajele de top în Dobroești: Pikachu (comunitate tânǎrǎ cu gustu urban), Spiderman, Bluey. Elsa în top 3 la fetite. Rezervare: WhatsApp 0722 744 377.']
  },
  'balaceanca': {
    h2: 'Bǎlǎceanca (Ilfov) — lânga Cernica și lacurile estice: naturǎ periurbanǎ la 18 km',
    p: ['Bǎlǎceanca este o comunǎ din Ilfov situatǎ la 18 km est de București, în apropierea lacurilor Cernica și Pantelimon — zona umedǎ protejatǎ a estului capitalei. Accesul pe DJ301 este direct din Pantelimon (limita Sectorului 3), cu o durată de deplasare de 20-25 minute.',
    'Comunitatea din Bǎlǎceanca are un profil interesant: localnici tradiționali alǎturi de noi rezidenți sosiți din Sectoarele 3 și 4 ale Capitalei. Zona de est a Ilfovului este mai puțin mediatizatǎ decât vestul sau nordul, dar crește constant. SuperParty organizeazǎ regulat petreceri în Bǎlǎceanca și comunele vecine (Cernica, Glina, Pantelimon).',
    'Petrecerile din Bǎlǎceanca se desfǎșoarǎ în medii diverse: blocuri construite în perioada comunistǎ (cu sǎli comune) și case individuale cu curți de 300-500 mp. Animatorul evalueazǎ spațiul la sosire și adapteazǎ programul — pentru blocuri, jocurile sunt mai structurate; pentru curți, mai dinamice și fizice.',
    'Personajele solicitate în Bǎlǎceanca și zona de est Ilfov: Stitch (locul 1 surprinzǎtor față de media naționalǎ), Spiderman și Batman la locuri 2-3. Taxǎ deplasare: 30 RON. Rezervare: 0722 744 377.']
  },
  'caldararu': {
    h2: 'Cǎldǎraru (Ilfov) — sat în Cernica, lânga mânǎstire și lac: spiritualitate și naturǎ',
    p: ['Cǎldǎraru este un sat din comuna Cernica, județul Ilfov, la 2 km de Mânǎstirea Cernica și de celebrul Lac Cernica — loc de pelerinaj și de relaxare pentru bucureșieni. Zona Cernica-Cǎldǎraru are o atmosferǎ aparte: liniște, pǎduri verzi, lacuri și un ritm de viațǎ mai calm decât al Capitalei.',
    'Accesul din București: DJ301 din Pantelimon, 15-18 minute din Sectorul 3. SuperParty considerǎ Cǎldǎraru parte din zona Cernica cu aceeași taxǎ de deplasare de 30 RON. Animatorul ajunge în 20-25 minute din Sectorul 3. Lacul Cernica oferǎ și opțiunea de petrecere pe malul apei — cadru unic pentru animație outdoor.',
    'Familiile din Cǎldǎraru și din Cernica apreciazǎ natura localǎ și petrec mult timp outdoors — petrecerile sunt adesea în grǎdinǎ sau pe malul lacului. SuperParty are experiența cu entertainment-ul de exterior în zona Cernica: echipament rezistent la umiditate, baloane nepretențioase la vânt și face painting cu fixative puternice.',
    'Personajele favorite în Cǎldǎraru-Cernica: Moana (tema apei Lacului Cernica), Elsa și Bluey. Rezervare: 0722 744 377, specificați localizarea în Cernica pentru deplasare optimizatǎ.']
  },
};

const ROOT_DIR = ROOT;
let n = 0;
for (const [slug, data] of Object.entries(PROSE)) {
  const fp = path.join(ROOT_DIR, 'src/pages/petreceri', slug + '.astro');
  if (!fs.existsSync(fp)) { process.stdout.write('NOT FOUND: ' + slug + '\n'); continue; }
  let c = fs.readFileSync(fp, 'utf-8');
  // Sterge proza existenta
  c = c.replace(/\n?<!-- UNIQUE-PROSE-MARKER[\s\S]*?<\/section>/g, '');
  
  const paras = data.p.map(pr => `<p style="color:var(--text-muted);line-height:1.95;font-size:.93rem;margin-bottom:1.1rem">${pr}</p>`).join('\n    ');
  const section = `\n<!-- UNIQUE-PROSE-MARKER-${slug} -->\n<section class="zona-detail" style="padding:2.5rem 0;background:rgba(255,255,255,0.02)">\n  <div class="container" style="max-width:820px">\n    <h2 style="font-size:1.2rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem">${data.h2}</h2>\n    ${paras}\n  </div>\n</section>`;
  
  const ins = c.lastIndexOf('</Layout>');
  if (ins === -1) { process.stdout.write('NO LAYOUT: ' + slug + '\n'); continue; }
  c = c.slice(0, ins) + section + '\n\n' + c.slice(ins);
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
}
process.stdout.write(`\n✅ Updated: ${n} pagini\n`);

// Verific rapid perechile problematice
function xp(raw) {
  const m = raw.match(/<!-- UNIQUE-PROSE-MARKER[^>]*-->([\s\S]*?)(?=\n\n<\/Layout>|<\/Layout>|<!--)/);
  if (!m) return '';
  return m[1].replace(/<[^>]+>/g,' ').replace(/[^a-zA-Z\u00C0-\u024F\s]/g,' ').replace(/\b\w{1,3}\b/g,' ').replace(/\s+/g,' ').trim().toLowerCase();
}
function sb(a, b) {
  const t = s => { const w = s.split(/\s+/).filter(x=>x.length>4); const r = new Set(); for(let i=0;i<w.length-1;i++) r.add(w[i]+'_'+w[i+1]); return r; };
  const sa = t(a), sb_ = t(b); if(!sa.size||!sb_.size) return 0;
  return Math.round([...sa].filter(x=>sb_.has(x)).length/new Set([...sa,...sb_]).size*100);
}

const tests = [
  ['branesti','stefanestii-de-jos'],['baneasa','ganeasa'],['buturugeni','colibasi'],
  ['campurelu','copaceni'],['ciorogarla','vidra'],['crivina','petrachioaia'],
  ['dobroesti','stefanestii-de-jos'],['balaceanca','caldararu'],['caciulati','ciocanesti'],
  ['cojasca','copaceni'],['butimanu','cranguri'],['cojesti','cozieni'],
];
process.stdout.write('\nSimilaritate dupa fix:\n');
for (const [a,b] of tests) {
  try {
    const ca = xp(fs.readFileSync(path.join(ROOT_DIR,'src/pages/petreceri',a+'.astro'),'utf-8'));
    const cb = xp(fs.readFileSync(path.join(ROOT_DIR,'src/pages/petreceri',b+'.astro'),'utf-8'));
    const s = sb(ca, cb);
    process.stdout.write((s<=20?'✅':s<=30?'🟡':s<=50?'🟠':'⛔')+' '+a+' vs '+b+': '+s+'%\n');
  } catch(e) {}
}
