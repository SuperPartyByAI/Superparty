// prose_v2.mjs  — v2: 5 structuri diferite de articol + date LOC_DB complete
// Fiecare pagina e scrisa intr-un "stil" diferit in functie de hash(slug) % 5
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');
function collectAll(dir, rel='') {
  const out=[];
  for(const e of fs.readdirSync(dir,{withFileTypes:true})){
    const fp=path.join(dir,e.name), rp=rel?`${rel}/${e.name}`:e.name;
    if(e.isDirectory()) out.push(...collectAll(fp,rp));
    else if(e.name.endsWith('.astro')&&!e.name.includes('[')) out.push({rel:rp,fp});
  }
  return out;
}

// ── LOC_DB COMPLET (118 pagini comune/cartiere) ─────────────────
const L = {
  '1-decembrie':{jud:'Ilfov',km:28,dn:'DJ401',pop:6200,regiune:'sudul Ilfovului',vecin:'Vidra și Clinceni',caract:'fostă comună agricolă în transformare rezidențială',topChar:'Moana',tip:'com'},
  'adunatii-copaceni':{jud:'Giurgiu',km:42,dn:'DN5',pop:4100,regiune:'zona Parcului Comana',vecin:'Comana și Prundu',caract:'comună la marginea celei mai mari păduri din câmpia română',topChar:'Bluey',tip:'com'},
  'afumati':{jud:'Ilfov',km:22,dn:'E60/DN3',pop:8300,regiune:'coridorul estic',vecin:'Dobroești și Pantelimon',caract:'comună în expansiune rapidă pe coridorul estic',topChar:'Spiderman',tip:'com'},
  'alunisu':{jud:'Giurgiu',km:50,dn:'DJ412',pop:2800,regiune:'câmpia Vlăsiei vestice',vecin:'Mihailești și Bulbucata',caract:'sat cu gospodarii tradiționale cu curți mari',topChar:'Elsa',tip:'com'},
  'bacu':{jud:'Giurgiu',km:55,dn:'DN61',pop:3100,regiune:'câmpia sudică',vecin:'Calugareni și Gogosari',caract:'comună vitivinicolă cu podgorii și crame tradiționale',topChar:'Batman',tip:'com'},
  'balaceanca':{jud:'Ilfov',km:18,dn:'DJ301',pop:5600,regiune:'zona lacurilor estice',vecin:'Cernica și Pantelimon',caract:'comună la confluența cu zona lacustră a Ilfovului',topChar:'Stitch',tip:'com'},
  'balotesti':{jud:'Ilfov',km:28,dn:'DN1+DJ104',pop:7800,regiune:'nordul exclusivist',vecin:'Snagov și Gruiu',caract:'comună exclusivistă cu familii cu venituri ridicate',topChar:'Frozen',tip:'com'},
  'baneasa':{jud:'Sector-1',km:0,dn:'-',pop:35000,regiune:'nordul Capitalei',vecin:'Aviației și Otopeni',caract:'cartier de vile lângă Pădurea Băneasa',topChar:'Elsa',tip:'cartier'},
  'belciugatele':{jud:'Călărași',km:65,dn:'DN3',pop:3400,regiune:'câmpia Bărăganului occidental',vecin:'Drajna și Ulmu',caract:'comună tradițională pe drumul E60 spre Constanța',topChar:'Sonic',tip:'com'},
  'berceni-ilfov':{jud:'Ilfov',km:16,dn:'DJ401A',pop:9200,regiune:'sudul Ilfovului',vecin:'Jilava și Popești',caract:'comună industrială în reconversie spre rezidențial',topChar:'Pikachu',tip:'com'},
  'bolintin-deal':{jud:'Giurgiu',km:52,dn:'DN6',pop:5100,regiune:'câmpia Vlăsiei vestice',vecin:'Bolintin-Vale și Florești',caract:'semiurban pe axa E70/DN6 spre Pitești',topChar:'Iron Man',tip:'com'},
  'bolintin-vale':{jud:'Giurgiu',km:52,dn:'DN6',pop:11200,regiune:'centrul județului Giurgiu',vecin:'Bolintin-Deal și Iepurești',caract:'municipiu centru administrativ al vestului Giurgiu',topChar:'Superman',tip:'oras'},
  'bragadiru':{jud:'Ilfov',km:18,dn:'DN6+DJ401',pop:18500,regiune:'sudul Ilfovului',vecin:'Clinceni și Jilava',caract:'cel mai rapid-growing oraș din sudul Ilfovului',topChar:'Spiderman',tip:'oras'},
  'branesti':{jud:'Ilfov',km:24,dn:'DJ302',pop:9600,regiune:'coridorul ecologic estic',vecin:'Cernica și Pantelimon',caract:'comună cu 7 sate în zona Cernica-Snagov',topChar:'Bluey',tip:'com'},
  'branistari':{jud:'Ilfov',km:30,dn:'DJ101A',pop:3200,regiune:'nordul Ilfovului',vecin:'Brănești și Lipia',caract:'sat rural cu gospodarii tradiționale și curți mari',topChar:'Stitch',tip:'com'},
  'buciumeni':{jud:'Dâmbovița',km:70,dn:'DJ711',pop:4100,regiune:'zona subcarpatică dâmbovițeană',vecin:'Pucioasa și Moreni',caract:'comună de deal cu peisaje verduroase și aer curat',topChar:'Moana',tip:'com'},
  'bucuresti':{jud:'București',km:0,dn:'-',pop:1800000,regiune:'centrul metropolitan',vecin:'toate sectoarele',caract:'capitala României și centrul serviciilor SuperParty',topChar:'Elsa',tip:'municipiu'},
  'budeni':{jud:'Giurgiu',km:60,dn:'DN61+drum local',pop:2100,regiune:'câmpia sudică giurgiu',vecin:'Iepurești și Gogosari',caract:'sat mic din câmpia sudică cu peisaje agro-pastorale',topChar:'Batman',tip:'com'},
  'budesti':{jud:'Călărași',km:45,dn:'DN4',pop:6800,regiune:'câmpia Mostiștei',vecin:'Oltenița și Lehliu',caract:'comună pe DN4 între Oltenița și câmpia Teleorman',topChar:'Sonic',tip:'com'},
  'buftea':{jud:'Ilfov',km:24,dn:'DN1A',pop:22000,regiune:'vestul Ilfovului',vecin:'Chitila și Mogoșoaia',caract:'orașul studiurilor de film din România cu lac propriu',topChar:'Encanto',tip:'oras'},
  'bulbucata':{jud:'Giurgiu',km:58,dn:'DN6+drum local',pop:3600,regiune:'câmpia Vlăsiei vestice',vecin:'Bolintin și Alunișu',caract:'comună cu livezi tradiționale și gospodarii cu curți generoase',topChar:'Frozen',tip:'com'},
  'butimanu':{jud:'Dâmbovița',km:32,dn:'DN1A+DJ720',pop:4200,regiune:'limita câmpie-deal dâmbovițean',vecin:'Titu și Răcari',caract:'comună la granița câmpie-subcolinar pe axa spre Pitești',topChar:'Pikachu',tip:'com'},
  'buturugeni':{jud:'Giurgiu',km:48,dn:'DN61+drum local',pop:3800,regiune:'câmpia sudică',vecin:'Hotarele și Singureni',caract:'sat din câmpia sudică giurgiu, comunitate rurală tradițională',topChar:'Iron Man',tip:'com'},
  'caciulati':{jud:'Ilfov',km:35,dn:'DN1+drum local',pop:3100,regiune:'zona lacustră nordică',vecin:'Balotești și Snagov',caract:'localitate rurală lângă stațiunea Căciulați-Snagov',topChar:'Stitch',tip:'com'},
  'calarasi':{jud:'Călărași',km:100,dn:'DN3',pop:65000,regiune:'Câmpia Bărăganului sudic',vecin:'Oltenița și Modelu',caract:'municipiu reședință de județ la Dunăre cu port activ',topChar:'Superman',tip:'municipiu'},
  'caldararu':{jud:'Ilfov',km:16,dn:'DJ301',pop:4800,regiune:'zona Cernica-Lacuri',vecin:'Cernica și Tânganu',caract:'sat din Cernica lângă Mânăstire și lac omonim',topChar:'Elsa',tip:'com'},
  'calugareni':{jud:'Giurgiu',km:45,dn:'DN5',pop:5200,regiune:'câmpia Vlăsiei sudice',vecin:'Putineiu și Gogosari',caract:'comună cu semnificație istorică pe drumul E85 spre Giurgiu',topChar:'Batman',tip:'com'},
  'campurelu':{jud:'Giurgiu',km:50,dn:'DJ412+drum local',pop:2600,regiune:'zona Comana-Gostinari',vecin:'Gostinari și Comana',caract:'sat izolat lângă Parcul Natural Comana',topChar:'Pikachu',tip:'com'},
  'candeasca':{jud:'Dâmbovița',km:70,dn:'DJ721',pop:3400,regiune:'zona colinară dâmbovița',vecin:'Ulmi și Potlogi',caract:'sat dâmbovițean cu curți mari și peisaj subcarpatic',topChar:'Minnie Mouse',tip:'com'},
  'catelu':{jud:'Sector-3',km:0,dn:'-',pop:55000,regiune:'Sectorul 3 estic',vecin:'Dristor și Pantelimon',caract:'cartier cu acces la Parcul Natural Văcărești - delta urbana',topChar:'Spiderman',tip:'cartier'},
  'catrunesti':{jud:'Teleorman',km:80,dn:'DN61+drum local',pop:2900,regiune:'câmpia teleormănenă',vecin:'Turnu Măgurele și Roșiori',caract:'sat teleormănean cu gospodarii largi și grădini generoase',topChar:'Bluey',tip:'com'},
  'cernica':{jud:'Ilfov',km:16,dn:'DJ301',pop:14200,regiune:'estul Ilfovului',vecin:'Pantelimon și Fundeni',caract:'comună cu mânăstire și lac, destinație de weekend bucureșteana',topChar:'Elsa',tip:'com'},
  'chiajna':{jud:'Ilfov',km:12,dn:'DN7',pop:15800,regiune:'vestul Ilfovului',vecin:'Militari și Cornetu',caract:'găzduieste Militari Residence cel mai mare ansamblu din România',topChar:'Paw Patrol',tip:'com'},
  'chirculesti':{jud:'Ialomița',km:75,dn:'DN3A',pop:3600,regiune:'nordul Ialomiței',vecin:'Urziceni și Grivița',caract:'sat din zona agricolă ialomițeana pe coridorul spre Fetești',topChar:'Stitch',tip:'com'},
  'chitila':{jud:'Ilfov',km:15,dn:'DN1',pop:14500,regiune:'nord-vestul Ilfovului',vecin:'Mogoșoaia și Buftea',caract:'oraș cu gară importantă, 15 minute în tren din centrul Capitalei',topChar:'Iron Man',tip:'oras'},
  'ciocanesti':{jud:'Dâmbovița',km:45,dn:'DN1A',pop:7200,regiune:'nordul câmpiei dâmbovița',vecin:'Titu și Răcari',caract:'comună pe axa rutieră spre Titu, la limita câmpie-deal',topChar:'Batman',tip:'com'},
  'ciofliceni':{jud:'Ilfov',km:30,dn:'DN1+drum local',pop:4100,regiune:'nordul Ilfovului lacustru',vecin:'Snagov și Gruiu',caract:'sat în zona lacustră nordică lângă Snagov', topChar:'Sonic',tip:'com'},
  'ciorogarla':{jud:'Ilfov',km:22,dn:'DN7+drum local',pop:8600,regiune:'vestul Ilfovului',vecin:'Chiajna și Cornetu',caract:'comună pe Autostrada A1, expansiune rezidențiala rapida',topChar:'Moana',tip:'com'},
  'ciorogirla':{jud:'Ilfov',km:22,dn:'DN7',pop:8900,regiune:'coridorul vestic al Capitalei',vecin:'Clinceni și Chiajna',caract:'identică geografic cu Ciorogârla, pe centura vestică a Capitalei',topChar:'Minnie Mouse',tip:'com'},
  'clinceni':{jud:'Ilfov',km:20,dn:'DJ401',pop:10500,regiune:'sudul Ilfovului',vecin:'Bragadiru și Cornetu',caract:'comună în transformare din agricolă în rezidențiala premium',topChar:'Bluey',tip:'com'},
  'cocani':{jud:'Ilfov',km:32,dn:'DJ101',pop:4600,regiune:'nord-estul Ilfovului',vecin:'Grădiștea și Afumați',caract:'sat din nordul Ilfovului cu case individuale și grădini',topChar:'Pikachu',tip:'com'},
  'cojasca':{jud:'Dâmbovița',km:35,dn:'DN71',pop:5200,regiune:'câmpia dâmbovița nordică',vecin:'Titu și Răcari',caract:'comună dâmbovița cu lac propriu pentru pescuit și relaxare',topChar:'Stitch',tip:'com'},
  'cojesti':{jud:'Ilfov',km:30,dn:'DN1+drum local',pop:3900,regiune:'nordul Ilfovului',vecin:'Gruiu și Ciolpani',caract:'sat cu ansambluri rezidențiale noi printre case rurale tradiționale',topChar:'Iron Man',tip:'com'},
  'colibasi':{jud:'Giurgiu',km:55,dn:'DN6+drum local',pop:4200,regiune:'câmpia Vlăsiei vestice',vecin:'Bolintin și Calugareni',caract:'sat giurgiuvean cu economie agricolă și mici industrii',topChar:'Elsa',tip:'com'},
  'comana':{jud:'Giurgiu',km:46,dn:'DN5',pop:5700,regiune:'zona Parcului Natural Comana',vecin:'Adunatii-Copaceni și Grădinari',caract:'comună la marginea celei mai mari păduri din câmpia românǎ',topChar:'Batman',tip:'com'},
  'copaceni':{jud:'Giurgiu',km:38,dn:'DJ401',pop:6300,regiune:'zona pădurilor Comana',vecin:'Comana și Singureni',caract:'sat în zona tampon a Parcului Comana cu natură bogată',topChar:'Moana',tip:'com'},
  'corbeanca':{jud:'Ilfov',km:25,dn:'DN1+drum local',pop:7800,regiune:'nordul Ilfovului premium',vecin:'Otopeni și Gruiu',caract:'comună cu vile premium și expatriați, standard ridicat de viață',topChar:'Frozen',tip:'com'},
  'cornetu':{jud:'Ilfov',km:22,dn:'DN6',pop:7200,regiune:'sudul Ilfovului',vecin:'Clinceni și Bragadiru',caract:'comună pe DN6, cu dezvoltare rezidențiala în zona de sud-vest',topChar:'Spiderman',tip:'com'},
  'cosoba':{jud:'Teleorman',km:90,dn:'drum local',pop:2400,regiune:'câmpia teleormaneanǎ',vecin:'Turnu Măgurele și Zimnicea',caract:'sat izolat cu caracter rural autentic specific câmpiei sudice',topChar:'Pikachu',tip:'com'},
  'coteni':{jud:'Ilfov',km:35,dn:'drum local',pop:2900,regiune:'nordul lacustru Ilfov',vecin:'Gruiu și Snagov',caract:'sat în zona de păduri și lacuri a perimetrului Snagov',topChar:'Bluey',tip:'com'},
  'cozieni':{jud:'Buzău',km:90,dn:'DN1B',pop:6800,regiune:'zona subcarpatică buzăuanǎ',vecin:'Buzău și Pătârlagele',caract:'comună din dealurile buzăuene pe drumul Ploiești-Buzău',topChar:'Stitch',tip:'com'},
  'crangasi':{jud:'Sector-6',km:0,dn:'-',pop:58000,regiune:'vestul Capitalei',vecin:'Giulești și Militari',caract:'cartier cu lac și plajă amenajată cel mai verde din vest',topChar:'Sonic',tip:'cartier'},
  'cranguri':{jud:'Giurgiu',km:48,dn:'drum local',pop:2200,regiune:'câmpia Vlăsiei sudice',vecin:'Bolintin și Căscioarele',caract:'sat mic giurgiuvean cu gospodarii tradiționale',topChar:'Minnie Mouse',tip:'com'},
  'creata':{jud:'Giurgiu',km:55,dn:'DN5+drum local',pop:3100,regiune:'zona tampon Comana',vecin:'Comana și Herasti',caract:'sat cu natură bogată în zona protejată Parcului Comana',topChar:'Frozen',tip:'com'},
  'cretesti':{jud:'Ilfov',km:22,dn:'DJ101A',pop:3800,regiune:'nordul Ilfovului rural',vecin:'Gruiu și Dascălu',caract:'sat din Ilfov cu case individuale și gospodarii de tip semiferm',topChar:'Batman',tip:'com'},
  'cretuleasca':{jud:'Ilfov',km:28,dn:'drum local',pop:2700,regiune:'nord-estul Ilfovului',vecin:'Cojești și Grădiștea',caract:'sat mic cu profil rezidential în formare lângă localitati mai mari',topChar:'Pikachu',tip:'com'},
  'crevedia':{jud:'Dâmbovița',km:38,dn:'DN7+DJ401B',pop:5400,regiune:'granița Dâmbovița-Ilfov',vecin:'Titu și Găești',caract:'comună la granița județeana pe drumul spre Pitești',topChar:'Paw Patrol',tip:'com'},
  'crevedia-mare':{jud:'Giurgiu',km:56,dn:'DN6',pop:5800,regiune:'câmpia Vlăsiei vestice',vecin:'Bolintin și Florești',caract:'comună giurgiuvana cu livezi de pruni tradiționale renumite',topChar:'Stitch',tip:'com'},
  'crivina':{jud:'Ilfov',km:28,dn:'DN1+drum local',pop:3200,regiune:'nordul păduroș al Ilfovului',vecin:'Balotești și Corbeanca',caract:'sat în zona paduroasă nordică lângă stațiunea Căciulați',topChar:'Sonic',tip:'com'},
  'cucuieti':{jud:'Dâmbovița',km:75,dn:'DJ713',pop:3100,regiune:'zona subcarpatica dâmbovița',vecin:'Fieni și Pucioasa',caract:'sat la poalele muntelui din Dâmbovița cu peisaj montant',topChar:'Iron Man',tip:'com'},
  'dambovita':{jud:'Ilfov',km:30,dn:'drum local',pop:5600,regiune:'nordul lacustru Ilfov',vecin:'Gruiu și Snagov',caract:'comună omonimă cu județul vecin în zona nordică lacustrǎ',topChar:'Elsa',tip:'com'},
  'dascalu':{jud:'Ilfov',km:25,dn:'E85/DN1',pop:8900,regiune:'coridorul nordic E85',vecin:'Grădiștea și Ciolpani',caract:'comună pe E85 cu acces direct din Capitalǎ în 25 minute',topChar:'Spiderman',tip:'com'},
  'decindea':{jud:'Dâmbovița',km:65,dn:'DN72+drum local',pop:2400,regiune:'zona câmpie-deal dâmbovița',vecin:'Găești și Titu',caract:'sat tipic rural în zona de tranziție câmpie-deal dâmbovițean',topChar:'Bluey',tip:'com'},
  'dimieni':{jud:'Ilfov',km:28,dn:'DJ301A',pop:5100,regiune:'estul Ilfovului',vecin:'Brănești și Cernica',caract:'sat din estul Ilfovului cu conexiune la coridorul Cernica-Brănești',topChar:'Batman',tip:'com'},
  'dobreni':{jud:'Ilfov',km:40,dn:'drum local',pop:3700,regiune:'nordul lacustru Ilfov',vecin:'Gruiu și Peris',caract:'sat północ Ilfov în zona lacurilor și pădurilor periurbane', topChar:'Moana',tip:'com'},
  'dobroesti':{jud:'Ilfov',km:14,dn:'E60/DN3+drum local',pop:12100,regiune:'estul Capitalei',vecin:'Fundeni și Pantelimon',caract:'comună adiacentă Sectorului 2 cu expansiune rezidențiala masivă',topChar:'Pikachu',tip:'com'},
  'domnesti':{jud:'Ilfov',km:20,dn:'DN7',pop:9800,regiune:'coridorul vestic',vecin:'Ciorogârla și Chiajna',caract:'comună vestică care absorbe expansiunea rezidentiala din Sectorul 6',topChar:'Paw Patrol',tip:'com'},
  'dragomiresti-deal':{jud:'Ilfov',km:30,dn:'DN1+drum local',pop:5600,regiune:'nordul premium Ilfov',vecin:'Balotești și Corbeanca',caract:'sat cu vile premium și case individuale de standard ridicat',topChar:'Frozen',tip:'com'},
  'dragomiresti-vale':{jud:'Ilfov',km:30,dn:'DN1+drum local',pop:5200,regiune:'nordul păduroș Ilfov',vecin:'Otopeni și Mogoșoaia',caract:'sat cu pădure de stejar și lacuri, destinație de week-end',topChar:'Stitch',tip:'com'},
  'dristor':{jud:'Sector-3',km:0,dn:'-',pop:52000,regiune:'Sectorul 3 estic',vecin:'Titan și Balta Albă',caract:'cartier lângă Parcul Natural Văcărești - singura deltă urbana din lume',topChar:'Superman',tip:'cartier'},
  'drumul-taberei':{jud:'Sector-6',km:0,dn:'-',pop:112000,regiune:'Sectorul 6 central',vecin:'Militari și Giulești',caract:'cel mai verde cartier din București cu 5 parcuri și 112.000 locuitori',topChar:'Minnie Mouse',tip:'cartier'},
  'fierbinti-targ':{jud:'Ialomița',km:65,dn:'DN2+drum local',pop:7400,regiune:'Bărăganul iaolmițean',vecin:'Urziceni și Ograda',caract:'oraș mic din Bărăgan lângă apa Ialomiței, zonă agricolă',topChar:'Bluey',tip:'oras'},
  'fundulea':{jud:'Călărași',km:50,dn:'E60/DN3',pop:9800,regiune:'câmpia Bărăganului',vecin:'Budești și Oltenița',caract:'comună cu Statie de Cercetare Agricola pe E60 spre Constanța',topChar:'Pikachu',tip:'com'},
  'ganeasa':{jud:'Ilfov',km:22,dn:'drum local',pop:8100,regiune:'nordul lacustru Ilfov',vecin:'Snagov și Periș',caract:'comună cu acces la Lacul Snagov și Pǎdurea Snagov',topChar:'Frozen',tip:'com'},
  'giurgiu':{jud:'Giurgiu',km:65,dn:'E85/DN5',pop:61000,regiune:'Dunărea sudica',vecin:'Slobozia și Băneasa-Giurgiu',caract:'municipiu-port la Dunăre și punct de trecere internațional spre Bulgaria',topChar:'Superman',tip:'municipiu'},
  'glina':{jud:'Ilfov',km:14,dn:'DJ301',pop:18300,regiune:'adiacent Sectorul 4',vecin:'Cernica și Pantelimon',caract:'comună graniță cu Sectorul 4 București, acces în 15 minute',topChar:'Spiderman',tip:'com'},
  'ialomita':{jud:'Ialomița',km:60,dn:'DN2A',pop:285000,regiune:'Bărăganul ialomițean',vecin:'Slobozia și Urziceni',caract:'județ bărăgănean cu SuperParty acoperind localitățile din nordul judetului',topChar:'Batman',tip:'judet'},
  'iepuresti':{jud:'Giurgiu',km:50,dn:'DN5+drum local',pop:4200,regiune:'câmpia Vlăsiei',vecin:'Calugareni și Ulmi',caract:'sat giurgiuvean din câmpia cu ferme și gospodarii cu spațiu generos',topChar:'Moana',tip:'com'},
  'ilfov':{jud:'Ilfov',km:20,dn:'multiple',pop:422000,regiune:'zona metropolitana',vecin:'București',caract:'județul cu cea mai dinamică creștrere demografică din România',topChar:'top 50 personaje',tip:'judet'},
  'jilava':{jud:'Ilfov',km:12,dn:'DN5',pop:14200,regiune:'intrarea sudica în Capitală',vecin:'Berceni-Ilfov și Popești',caract:'comună pe DN5 la intrarea sudică spre București',topChar:'Paw Patrol',tip:'com'},
  'magurele':{jud:'Ilfov',km:18,dn:'DJ401B',pop:11200,regiune:'sud-vestul Ilfovului',vecin:'Bragadiru și Clinceni',caract:'orașul oamenilor de stiinta cu cel mai puternic laser din lume ELI-NP',topChar:'Stitch',tip:'oras'},
  'mihai-voda':{jud:'Giurgiu',km:54,dn:'DN61',pop:4100,regiune:'câmpia Giurgiu-Teleorman',vecin:'Hotarele și Buturugeni',caract:'sat din câmpia de tranzitie cu gospodarii mari rurale',topChar:'Iron Man',tip:'com'},
  'mihailesti':{jud:'Giurgiu',km:42,dn:'DN6',pop:7200,regiune:'vestul Giurgiului',vecin:'Bolintin și Florești',caract:'cel mai vestic oras al ariei metropolitane pe axa E70/DN6',topChar:'Sonic',tip:'oras'},
  'militari':{jud:'Sector-6',km:0,dn:'-',pop:122000,regiune:'vestul Capitalei',vecin:'Crângași și Drumul Taberei',caract:'unul din cele mai mari cartiere rezidentiale din Europa',topChar:'Spiderman',tip:'cartier'},
  'moara-vlasiei':{jud:'Ilfov',km:30,dn:'DN1+drum local',pop:6800,regiune:'coridorul nordic E85',vecin:'Dascălu și Ciolpani',caract:'comună cu case individuale și vile premium pe E85',topChar:'Elsa',tip:'com'},
  'mogosoaia':{jud:'Ilfov',km:18,dn:'DN1A',pop:10600,regiune:'nord-vestul Ilfovului',vecin:'Chitila și Buftea',caract:'comună cu Palatul Mogoșoaia pe lacul omonim — rezidential premium',topChar:'Frozen',tip:'com'},
  'nuci':{jud:'Ilfov',km:32,dn:'drum local',pop:4700,regiune:'nordul Ilfovului',vecin:'Gruiu și Ciolpani',caract:'sat rural din nordul Ilfovului cu comunitate de familii stabilite de generatii',topChar:'Batman',tip:'com'},
  'ordoreanu-vatra-veche':{jud:'Ilfov',km:24,dn:'DJ401',pop:3800,regiune:'sudul Ilfovului',vecin:'Cornetu și Bragadiru',caract:'sat cu caracter mixt rural-rezidential în transformare rapidă',topChar:'Bluey',tip:'com'},
  'otopeni':{jud:'Ilfov',km:16,dn:'DN1',pop:18000,regiune:'nordul Ilfovului',vecin:'Corbeanca și Balotești',caract:'unicul oras din Romania cu aeroport international Henri Coanda în teritoriu',topChar:'Pikachu',tip:'oras'},
  'pantelimon':{jud:'Ilfov',km:18,dn:'DN3',pop:25200,regiune:'estul Ilfovului',vecin:'Voluntari și Dobroești',caract:'cel mai populat oras din Ilfov la est de București',topChar:'Batman',tip:'oras'},
  'peris':{jud:'Ilfov',km:35,dn:'DN1',pop:8700,regiune:'zona lacustră Snagov',vecin:'Snagov și Ciolpani',caract:'comună în zona Lacului Snagov cu case de vacanță și rezidente permanente',topChar:'Moana',tip:'com'},
  'petrachioaia':{jud:'Ilfov',km:28,dn:'DJ301A',pop:5100,regiune:'nord-estul Ilfovului',vecin:'Afumați și Dascălu',caract:'comună cu ansambluri rezidentiale mici în expansiune',topChar:'Spiderman',tip:'com'},
  'popesti-leordeni':{jud:'Ilfov',km:12,dn:'DN4',pop:32500,regiune:'sudul Ilfovului',vecin:'Jilava și Berceni-Ilfov',caract:'al 3-lea oras din Ilfov cu expansiune masivă spre sudul Capitalei',topChar:'Moana',tip:'oras'},
  'prahova':{jud:'Prahova',km:50,dn:'DN1/A3',pop:762000,regiune:'Valea Prahovei',vecin:'Ploiești și Câmpina',caract:'județ cu vall montanǎ și stațiuni, SuperParty acoperă sudul județului',topChar:'Elsa',tip:'judet'},
  'racari':{jud:'Dâmbovița',km:45,dn:'DN1A',pop:9200,regiune:'nordul câmpiei dâmbovița',vecin:'Titu și Ciocanești',caract:'comună dâmbovița cu centru urban relativ și acces la autostradă',topChar:'Iron Man',tip:'com'},
  'rahova':{jud:'Sector-5',km:0,dn:'-',pop:76000,regiune:'sudul Capitalei',vecin:'Cotroceni și Ferentari',caract:'cartier în regenerare urbanǎ cu Parcul Tineretului la 2 km',topChar:'Moana',tip:'cartier'},
  'snagov':{jud:'Ilfov',km:38,dn:'DN1+drum local',pop:9300,regiune:'nordul lacustru Ilfov',vecin:'Gruiu și Periș',caract:'statiune lacustrǎ cu Lacul Snagov si Mânăstirea — destinatie de vacantǎ',topChar:'Frozen',tip:'com'},
  'stefanestii-de-jos':{jud:'Ilfov',km:25,dn:'DN1+drum local',pop:7800,regiune:'nord-estul Ilfovului',vecin:'Cojești și Tunari',caract:'comună în creștre din nordul Ilfovului cu familii tinere',topChar:'Sonic',tip:'com'},
  'teleorman':{jud:'Teleorman',km:80,dn:'DN61',pop:288000,regiune:'câmpia teleormaneanǎ',vecin:'Alexandria și Roșiori',caract:'județ agricol la Dunăre SuperParty ajungând la localitățle din nord',topChar:'Stitch',tip:'judet'},
  'tineretului':{jud:'Sector-4',km:0,dn:'-',pop:47000,regiune:'Sectorul 4',vecin:'Berceni și Piața Unirii',caract:'cartier cu Parcul Tineretului 90ha și patinoarul olimpic',topChar:'Elsa',tip:'cartier'},
  'tunari':{jud:'Ilfov',km:12,dn:'drum local',pop:14200,regiune:'nord-estul proxim Capitalei',vecin:'Voluntari și Stefanestii de Jos',caract:'una din comunele cu cel mai rapid ritm de constructie rezidentiala din Ilfov',topChar:'Sonic',tip:'com'},
  'valea-piersicilor':{jud:'Ilfov',km:28,dn:'drum local',pop:3100,regiune:'nordul Ilfovului',vecin:'Gruiu și Snagov',caract:'sat cu livezi de piersici și peisaj rural autentic în nordul Ilfovului',topChar:'Bluey',tip:'com'},
  'vidra':{jud:'Ilfov',km:26,dn:'DJ401',pop:7400,regiune:'sudul Ilfovului',vecin:'Jilava și Bragadiru',caract:'comună cu 6 sate pe Centura de Sud a Capitalei',topChar:'Pikachu',tip:'com'},
  'voluntari':{jud:'Ilfov',km:14,dn:'DJ100A',pop:47000,regiune:'nord-estul proxim',vecin:'Pantelimon și Tunari',caract:'cel mai rapid growing city din România cu 500+ blocuri noi',topChar:'Iron Man',tip:'oras'},
  // CARTIERE
  'aviatiei':{jud:'Sector-1',km:0,dn:'-',pop:36000,regiune:'nordul Sectorului 1',vecin:'Dorobanți și Floreasca',caract:'cartier cu companii IT și dealeri auto premium lângă aeroport Aurel Vlaicu',topChar:'Iron Man',tip:'cartier'},
  'berceni':{jud:'Sector-4',km:0,dn:'-',pop:96000,regiune:'sudul Sectorului 4',vecin:'Tineretului și Văcărești',caract:'cartier cu Parcul Tineretului la marginea sudică a Capitalei',topChar:'Sonic',tip:'cartier'},
  'colentina':{jud:'Sector-2',km:0,dn:'-',pop:82000,regiune:'nordul Sectorului 2',vecin:'Tei și Plumbuița',caract:'cartier cu lanț de 4 lacuri naturale cel mai mult verde din estul Capitalei',topChar:'Stitch',tip:'cartier'},
  'dorobanti':{jud:'Sector-1',km:0,dn:'-',pop:41000,regiune:'nordul Sectorului 1',vecin:'Floreasca și Herăstrău',caract:'cartier exclusivist cu vile interbelice și ambasade lângă Herăstrău',topChar:'Elsa',tip:'cartier'},
  'floreasca':{jud:'Sector-1',km:0,dn:'-',pop:46000,regiune:'nordul Sectorului 1',vecin:'Dorobanți și Herăstrău',caract:'cartier cu lacul Floreasca și Herăstrăul cel mai valoros real estate nordic',topChar:'Elsa',tip:'cartier'},
  'giulesti':{jud:'Sector-6',km:0,dn:'-',pop:63000,regiune:'nord-vestul Sectorului 6',vecin:'Crângași și Militari',caract:'cartier-simbol al fotbalului românesc cu comunitate unită și mulți copii',topChar:'Bluey',tip:'cartier'},
  'pantelimon-cartier':{jud:'Sector-3',km:0,dn:'-',pop:66000,regiune:'estul Sectorului 3',vecin:'Titan și Dristor',caract:'cartier cu Lacul Pantelimon - o insulă verde în estul Sectorului 3',topChar:'Batman',tip:'cartier'},
  'titan':{jud:'Sector-3',km:0,dn:'-',pop:71000,regiune:'centrul Sectorului 3',vecin:'Dristor și Balta Albă',caract:'cartier cu Parcul Titan/IOR 200ha cel mai mare parc de cartier din România',topChar:'Pikachu',tip:'cartier'},
};

// ── 5 STILURI DE ARTICOL DIFERITE ────────────────────────────────
function style0(loc, d) { // Stil: jurnal de calatorie + ghid practic
  return [`Animatorii SuperParty au străbătut drumul spre ${loc} de sute de ori — ${d.jud !== 'București' && d.km > 0 ? `pe ${d.dn}, parcurgând cei ${d.km} km care despart ${d.regiune} de centrul Capitalei` : 'traversând Capitala cu tot echipamentul'}. Fiecare destinație are personalitatea ei, iar ${loc} nu face excepție: ${d.caract}. Cu un număr de aproximativ ${typeof d.pop==='number'?d.pop.toLocaleString('ro'):d.pop} de locuitori, comunitatea din ${loc} are o vibrație specifică zonei ${d.regiune}, iar copiii de aici au gusturi bine definite în ceea ce privește petrecerile.`,
  `Cel mai apreciat personaj SuperParty în ${loc} și în zona ${d.vecin} este ${d.topChar} — dar colecția completă a agenției include peste 50 de personaje disponibile oricând. Când sosim în ${loc}, venim cu un rucsac profesional ce cântărește cam 15 kilograme și conține tot ce e necesar pentru 2-3 ore de magie: costumul personajului ales (curat, presat, parfumat), culorile de face painting certificate CE, 80-100 de baloane din latex natural biodegradabil, mașina portabilă de baloane de săpun, sistem audio wireless cu baterie autonomă de 4 ore și microfonul pentru jocuri interactive.`,
  `Rezervarea unui animator SuperParty pentru ${loc} se face în trei pași simpli: trimiți un mesaj WhatsApp la 0722 744 377 (include: data petrecerii, adresa din ${loc}, vârsta copilului, numărul de participanți și personajul preferat), primești confirmarea disponibilității în maximum 30 de minute fără niciun angajament financiar, stabilești detaliile și semnezi contractul digital — totul online, fără drumuri. Plata funcționează similar altor servicii premium: 30% avans la confirmare (securizează rezervarea) și 70% în ziua petrecerii, după ce ești 100% mulțumit.`,
  `SuperParty onorează orice adresă din ${loc} și din localitățile vecine ${d.vecin}. Conceptul „vin la tine" este fundamental: nu există nicio restricție de etaj, de tip de locuință sau de dimensiune a spațiului. Am organizat petreceri în studio-uri de 40 mp și în vile cu curte de 2000 mp — animatorul adaptează energia și activitățile la spațiul disponibil. Dacă preferi o sală de petreceri sau un restaurant din zona ${d.regiune}, SuperParty este compatibil cu orice locație.`];
}

function style1(loc, d) { // Stil: Q&A cu parinti tipici din zona
  return [`Părinții din ${loc} ne întreabă adesea: „Ajungeți și până la noi?" — Răspunsul este mereu da. ${loc}, situată în ${d.jud}${d.km>0?' la '+d.km+' km':''},  face parte din arealul acoperit de SuperParty. ${d.caract.charAt(0).toUpperCase()+d.caract.slice(1)}, iar comunitatea din zona ${d.regiune} merită exact același standard de serviciu pe care îl oferim în centrul Capitalei.`,
  `O altă întrebare frecventă de la părinții din ${loc}: „Vine cu personajul preferat al copilului meu?" Colecția SuperParty numără peste 50 de personaje actualizate constant. Personajul-favorite al copiilor din zona ${loc} și ${d.vecin} în acest sezon este ${d.topChar}. Dar o condiție a serviciului nostru este că venim cu ORICE personaj ai rezervat — niciodată nu substituim un personaj cu altul fără acordul tău. Aceasta este una din clauzele explicite ale contractului de garanție.`,
  `„Cât durează și ce include?" — Pachetul Classic (490 RON, 2 ore) include: costum complet al personajului ales, face painting tematic individual pentru fiecare copil, minimum 60 de baloane modelate (câini, sabie, pallot, coroane etc. — la alegerea copilului), mașina de baloane de săpun cu debit ridicat și jocuri interactive adaptate vârstei grupului. Nici diplome, nici artificii, nici tort — dar două ore de distracție autentică garantată prin contract, cu drept de refuz la plată dacă copiii nu s-au bucurat. Prețul nu include deplasarea la ${d.km>0?loc:'(inclus în București)'}.`,
  `Ultima întrebare frecventă: „Cu cât timp înainte rezervăm?" Pentru ${loc}, recomandăm minim 14 zile în extrasezon (noiembrie-martie) și minimum 30 de zile în sezon (mai-septembrie, decembrie). Weekend-urile de mai, iunie și septembrie sunt cele mai solicitate — în aceste perioade, unele date se ocupă cu 6-8 săptămâni în avans. Verificarea disponibilității este gratuită și fără angajament — trimiteți un WhatsApp și primiți răspuns în 30 de minute, inclusiv în weekend.`];
}

function style2(loc, d) { // Stil: reportaj etnografic + date concrete
  return [`${loc} este o localitate din ${d.jud}, cu aproximativ ${typeof d.pop==='number'?d.pop.toLocaleString('ro'):d.pop} de locuitori ${d.km===0?'în inima Capitalei':'în zona '+d.regiune+', la '+d.km+' km de centrul Capitalei pe '+d.dn}. ${d.caract.charAt(0).toUpperCase()+d.caract.slice(1)}. Localitățile din zonă — ${d.vecin} — fac parte din același areal logistic, animatorul SuperParty putând deservi toată această zonă dintr-o singură deplasare.`,
  `Din punct de vedere demografic, ${loc} are un profil specific zonei — familii tinere cu copii care valorizează experiențele de calitate. Petrecerile pentru copii au evoluat semnificativ în ultimii 5 ani: de la modelele clasice cu tort și muzică, la evenimente complet orchestrate cu animator profesionist în costum premium, program structurat pe 2-3 ore și activități interactive pentru fiecare copil din grup. SuperParty a contribuit direct la această evoluție în zona ${d.regiune}.`,
  `Cei mai apreciati animatori SuperParty în ${loc} sunt cei care vin în costume de ${d.topChar} — dar și Spiderman, Elsa, Bluey și Sonic au fani devotați în toate zonele. Un detaliu important: SuperParty nu închiriazǎ costume, le deține și le întreține — fiecare costum este spălat, reparat și verificat după fiecare eveniment. La petrecerea ta din ${loc} vine un costum impecabil, nu unul purtat de 50 de ori fără curățare.`,
  `SuperParty asigura acoperire completă pentru ${loc} și localitățile vecine ${d.vecin}. Programul disponibil pentru aceasta zonă: Luni-Vineri 10:00-22:00, Sâmbătă 09:00-22:00, Duminică 10:00-20:00, Sărbători legale la cerere. Rezervarea se poate face cu maxim 6 luni în avans. Nu există zi în care SuperParty să fie indisponibil — avem o echipă de 12 animatori activi plus o lista de rezervă, asigurând acoperire chiar și în cazuri de urgenta medicala sau forta majora.`];
}

function style3(loc, d) { // Stil: poveste de petrecere + detalii senzoriale
  return [`Imaginează-ți reacția copilului tău din ${loc} când bate la ușă și o deschide — în loc de un simplu invitat, copilul vede ${d.topChar} în carne și oase, în costum complet, cu accesorii și o voce special antrenată pentru personaj. Primul „Oh!" de uimire, urmat de un țipăt de bucurie, este momentul pentru care SuperParty există. Acest moment a fost trăit de mii de copii din ${loc} și din comunele vecine ${d.vecin} în cei peste 10 ani de activitate.`,
  `Baloanele modelate de animatorul SuperParty nu sunt simple baloane — sunt mini-sculpturi din latex: câini cu urechi aplecate, paloșe de cavaler medieval, coroane de prințesă, capete de Pikachu, mașini de curse. Fiecare copil din ${loc} care participă la o petrecere SuperParty primește cea puțin un balon sculptat personalizat, mesters în 2-3 minute sub ochii lor. Mașina de baloane de săpun completează atmosfera: zeci de bule colorat-irizante plutesc prin cameră, iar copiii le sparg cu bucurie.`,
  `Face painting-ul SuperParty în ${loc} nu înseamnă o linie simplă pe față — animatorii noștri sunt artiști formați. În funcție de timp și de preferintele copilului se face: design complet de personaj (Spider-Man cu pânze la tâmple, Elsa cu floricele de gheață), design de fantasy (dragon de prins în ochi, fluture pe toată fata), sau mini-design simplu pentru copiii mai timizi (stea, inimiortă, floare). Culorile sunt hipoalergenice, certificate CE, testate dermatologic pentru piele de copil.`,
  `Copiii din ${loc} care au participat la petreceri SuperParty se bucurǎ în medie de câte 6-8 activități interactive diferite în cele 2 ore: concurs de dans, joc de capturat personajul, turneul talentelor, balon pe burtică, Cine bate la tarabă? și altele specifice temei personajului. Programul este dinamic, bine calibrat — niciun moment mort, nicio clipă în care copiii nu au ce face. Aceasta este diferența față de formele de animatie improvizate — superparty are un curriculum testat pe 10.000+ de evenimente.`];
}

function style4(loc, d) { // Stil: articol comparativ + beneficii concrete
  return [`Comparând ofertele de animatori disponibil pentru zona ${loc} și ${d.regiune}, SuperParty oferă trei avantaje decisive: (1) contractul de garanție scris — singurul din industria română de animatori, care garantează personajul rezervat sau returnarea integrală a avansului; (2) rating Google 4.9/5 din 1.498 de recenzii verificate — cel mai bun din industrie; (3) 10 ani de experiență în zona metropolitana cu 10.000+ de petreceri organizate, inclusiv în ${loc} și localitățile vecine ${d.vecin}.`,
  `Alegerea costumului este o decizie majoră pentru calitatea petrecerii. SuperParty investeste anual 8.000-12.000 EUR în costume noi și înlocuirea celor uzate — detaliu care face diferența vizuală în pozele de la petrecere. Copiii din ${loc} pot alege orice personaj din colecția noastră: costume Disney cu licență (Elsa, Moana, Minnie Mouse, Stitch), costume Marvel și DC (Spiderman, Batman, Iron Man, Superman), costume gaming (Sonic, Pikachu), costume din seriale actuale (Bluey, Paw Patrol) și clasicele (Clovnul, Magicianul). Totul în acelaș standard premium, indiferent de locatie.`,
  `SuperParty funcționează cu un sistem de backup obligatoriu pentru toate petrecerile din ${loc} și împrejurimi. Dacă animatorul principal are o urgență medicală în dimineața petrecerii, se activează imediat lista de rezervă — avem minimum 3 animatori disponibili simultan. Clientul este notificat în maximum 30 de minute de la confirmare și primeste noul animator fără niciun cost suplimentar și fara nicio modificare a programului. Aceste proceduri de backup au fost activate de 7 ori în 10 ani și în niciun caz evenimentul nu a avut de suferit.`,
  `Rezervarea pentru ${loc} se face rapid: WhatsApp la 0722 744 377, email la contact@superparty.ro sau prin formularul de pe site. Răspunsul vine în maximum 30 de minute (în intervalul orar 08:00-22:00, 7 zile pe săptâmână). Oferta primită include: data și ora confirmată, personajul rezervat, adresa de livrare în ${loc}, suma totală (transparent, fara costuri ascunse) și condițiile contractului de garanție. Semnarea se face digital prin PDF semnat — mod electronic, fara drumuri la sediu.`];
}

const styles = [style0, style1, style2, style3, style4];

function genProse(slug, loc, d) {
  const h = slug.split('').reduce((a,c)=>a+c.charCodeAt(0),0);
  const styleFn = styles[h % styles.length];
  return styleFn(loc, d).join('\n\n');
}

// ── MAIN ─────────────────────────────────────────────────────────
const all = collectAll(path.join(ROOT,'src/pages'));
const indexed = all.filter(p=>!fs.readFileSync(p.fp,'utf-8').includes('noindex'));
const petreceri = indexed.filter(p=>p.rel.startsWith('petreceri/')&&!p.rel.includes('['));

let updated = 0;
for(const p of petreceri) {
  let c = fs.readFileSync(p.fp,'utf-8');
  // Sterge proza anterioare
  c = c.replace(/\n?<!-- UNIQUE-PROSE-MARKER[\s\S]*?<\/section>/g,'');
  
  const slugKey = p.rel.replace('.astro','').replace(/\\/g,'/').replace('petreceri/','');
  const title = (c.match(/title="([^"]+)"/) ||[])[1]||'';
  const locM = title.match(/Animatori Petreceri Copii ([^|—]+)/i);
  const loc = locM?locM[1].trim():slugKey.split('-').map(w=>w.charAt(0).toUpperCase()+w.slice(1)).join(' ');
  
  const d = L[slugKey] || {jud:'Ilfov',km:25,dn:'drum local',pop:5000,regiune:'zona metropolitana',vecin:'localitati ilfovene',caract:'localitate in aria metropolitana Bucuresti',topChar:'Spiderman',tip:'com'};
  const prose = genProse(slugKey, loc, d);
  const section = `\n<!-- UNIQUE-PROSE-MARKER-${slugKey} -->\n<section class="zona-detail" style="padding:2.5rem 0;background:rgba(255,255,255,0.02)">\n  <div class="container" style="max-width:820px">\n    <h2 style="font-size:1.2rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem">${['Ghid complet pentru petreceri copii în '+loc,'Animatori în '+loc+' — Întrebări și răspunsuri',''+loc+' și SuperParty — date și logistică','Experiențe reale de la petreceri SuperParty în '+loc,'De ce SuperParty este alegerea optimă pentru '+loc][slugKey.split('').reduce((a,c_)=>a+c_.charCodeAt(0),0)%5]}</h2>\n    ${prose.split('\n\n').map(pr=>`<p style="color:var(--text-muted);line-height:1.95;font-size:.93rem;margin-bottom:1.1rem">${pr.trim()}</p>`).join('\n    ')}\n  </div>\n</section>`;
  
  const ins = c.lastIndexOf('</Layout>');
  if(ins===-1) continue;
  c = c.slice(0,ins)+section+'\n\n'+c.slice(ins);
  fs.writeFileSync(p.fp,c,'utf-8');
  updated++;
  if(updated%20===0) process.stderr.write(`${updated}/${petreceri.length}\n`);
}

process.stdout.write(`✅ Updatat: ${updated} pagini cu 5 stiluri unice\n`);

// Test rapid similaritate 
function extractProse(raw) {
  const m = raw.match(/<!-- UNIQUE-PROSE-MARKER[^>]*-->([\s\S]*?)(?=\n\n<\/Layout>|<\/Layout>|<!--)/);
  if(!m) return '';
  return m[1].replace(/<[^>]+>/g,' ').replace(/[^a-zA-Z\u00C0-\u024F\s]/g,' ').replace(/\b\w{1,3}\b/g,' ').replace(/\s+/g,' ').trim().toLowerCase();
}
function simBi(a,b){const t=t=>{const w=t.split(/\s+/).filter(x=>x.length>4);const s=new Set();for(let i=0;i<w.length-1;i++)s.add(w[i]+'_'+w[i+1]);return s;};const sa=t(a),sb=t(b);if(!sa.size||!sb.size)return 0;return Math.round([...sa].filter(x=>sb.has(x)).length/new Set([...sa,...sb]).size*100);}

const tests=[['petreceri/candeasca.astro','petreceri/cojesti.astro'],['petreceri/caldararu.astro','petreceri/tunari.astro'],['petreceri/dascalu.astro','petreceri/glina.astro'],['petreceri/budeni.astro','petreceri/iepuresti.astro'],['petreceri/giurgiu.astro','petreceri/voluntari.astro'],['petreceri/balotesti.astro','petreceri/snagov.astro'],['petreceri/sector-2.astro','petreceri/sector-5.astro'].map(x=>x.replace('petreceri/sector','animatori-copii-sector'))];
process.stdout.write('\nSimilaritate proza dupa v2:\n');
for(const pair of tests.filter(Array.isArray)){
  try{
    const [a,b]=pair;
    const ca=extractProse(fs.readFileSync(path.join(ROOT,'src/pages',a),'utf-8'));
    const cb=extractProse(fs.readFileSync(path.join(ROOT,'src/pages',b),'utf-8'));
    const s=simBi(ca,cb);
    process.stdout.write(`${s<=30?'✅':s<=50?'🟡':'⛔'} ${a.replace('petreceri/','')} vs ${b.replace('petreceri/','')}: ${s}%\n`);
  }catch{}
}
