// rebuild_comune_full.mjs — Rescrie complet paginile comune cu 600+ cuvinte unice per pagina
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pDir = path.join(__dirname, '../src/pages/petreceri');

function h(s) { let v=0; for(let i=0;i<s.length;i++) v=(v*31+s.charCodeAt(i))|0; return Math.abs(v); }
function pick(arr,idx) { return arr[idx % arr.length]; }

const communes = {
  'bacu':{'n':'Bâcu','d':17,'j':'Giurgiu','t':'rural','r':'DN5','v':'curtile caselor din Bacu, sala polivalenta, gradina mare','pop':800,'jud_info':'judetul Giurgiu este cunoscut pentru comunele agricole verzi'},
  'adunatii-copaceni':{'n':'Adunații-Copăceni','d':22,'j':'Giurgiu','t':'rural','r':'DN5','v':'curti spatioase, sala polivalenta Copaceni, parc local','pop':1200,'jud_info':'zona pitoreasca din sudul Ilfovului'},
  'afumati':{'n':'Afumați','d':18,'j':'Ilfov','t':'suburban','r':'DN2','v':'sala events Afumati, curti ansambluri noi, parcul local','pop':7000,'jud_info':'suburbie dinamica la est de Bucuresti'},
  'alunisu':{'n':'Alunișu','d':25,'j':'Giurgiu','t':'rural','r':'DN5','v':'gradina casei, sala scolii, spatiu deschis','pop':600,'jud_info':'sat mic linistit din judetul Giurgiu'},
  'balaceanca':{'n':'Bălăceanca','d':19,'j':'Ilfov','t':'suburban','r':'A2','v':'curti vile Balaceanca, sali noi, parcul local','pop':5000,'jud_info':'suburbie din sudul Ilfovului'},
  'balotesti':{'n':'Balotești','d':25,'j':'Ilfov','t':'suburban','r':'DN1','v':'ansambluri rezidentiale noi, parcul Balotesti, sali moderne','pop':9000,'jud_info':'oras in crestere pe axa nordica DN1'},
  'baneasa':{'n':'Băneasa','d':12,'j':'Ilfov','t':'suburban','r':'DN1','v':'vile cu curti, Padurea Baneasa, restaurante premium','pop':5500,'jud_info':'zona nordicagrefata de padurea Baneasa'},
  'belciugatele':{'n':'Belciugatele','d':55,'j':'Calarasi','t':'rural','r':'DN3','v':'curti spatioase, sala locala, gradina','pop':3000,'jud_info':'comuna din judetul Calarasi pe DN3'},
  'berceni-ilfov':{'n':'Berceni (Ilfov)','d':16,'j':'Ilfov','t':'suburban','r':'A2','v':'curti vile Berceni Ilfov, sali events noi, parcul local','pop':8000,'jud_info':'suburbie sudica in expansiune'},
  'bolintin-deal':{'n':'Bolintin-Deal','d':48,'j':'Giurgiu','t':'rural','r':'DN7','v':'sala liceului, curti case, spatiu deschis','pop':2000,'jud_info':'sat din zona Bolintinului, judetul Giurgiu'},
  'bolintin-vale':{'n':'Bolintin-Vale','d':50,'j':'Giurgiu','t':'urban-mic','r':'DN7','v':'sala culturala, restaurant family, piata centrala','pop':8000,'jud_info':'orasel de pe DN7, judetul Giurgiu'},
  'branesti':{'n':'Brănești','d':18,'j':'Ilfov','t':'suburban','r':'DN3','v':'curti case Branesti, sala events, Lacul Branesti','pop':6000,'jud_info':'suburbie la est de Capitala pe DN3'},
  'branistari':{'n':'Brăniștari','d':60,'j':'Dambovita','t':'rural','r':'DN71','v':'curti spatioase, gradina, sala scolii','pop':500,'jud_info':'sat din judetul Dambovita'},
  'buciumeni':{'n':'Buciumeni','d':65,'j':'Dambovita','t':'rural','r':'DN72','v':'curti mari, scoala locala, spatiu verde','pop':1000,'jud_info':'localitate rurala damboviteana'},
  'budeni':{'n':'Budeni','d':70,'j':'Giurgiu','t':'rural','r':'DJ412','v':'curti largi, sala locala','pop':700,'jud_info':'sat mic din judetul Giurgiu'},
  'budesti':{'n':'Budești','d':30,'j':'Ilfov','t':'suburban','r':'DJ401','v':'sali noi Budesti, curti ansambluri, parcul orasului','pop':5500,'jud_info':'oras suburban la sud-est'},
  'buftea':{'n':'Buftea','d':20,'j':'Ilfov','t':'urban-mic','r':'DN1A','v':'Studios Buftea, restaurante, Lacul Buftea','pop':20000,'jud_info':'oras cu studiouri de film si lac'},
  'bulbucata':{'n':'Bulbucata','d':45,'j':'Giurgiu','t':'rural','r':'DN5','v':'curti case, parc local, sala locala','pop':1100,'jud_info':'sat din sudul judetului Giurgiu'},
  'butimanu':{'n':'Butimanu','d':55,'j':'Dambovita','t':'rural','r':'DN71','v':'curti spatioase, sala locala, gradina','pop':800,'jud_info':'sat dambovitean linistit'},
  'buturugeni':{'n':'Buturugeni','d':55,'j':'Giurgiu','t':'rural','r':'DJ412','v':'curti mari, sala polivalenta, spatiu verde','pop':900,'jud_info':'sat din Giurgiu'},
  'caciulati':{'n':'Căciulați','d':20,'j':'Ilfov','t':'suburban','r':'DN1','v':'vile curti mari, zona Snagov, padure','pop':3000,'jud_info':'suburbie nordica langa Snagov'},
  'calarasi':{'n':'Călărași','d':120,'j':'Calarasi','t':'urban','r':'A2+DN3','v':'sali events multiple, restaurante, Parcul Dunarii','pop':60000,'jud_info':'resedinta de judet la Dunare'},
  'caldararu':{'n':'Căldăraru','d':25,'j':'Ilfov','t':'suburban','r':'DN3','v':'curti vile, sali noi, spatiu comunitar','pop':4000,'jud_info':'suburbie Ilfov pe DN3'},
  'calugareni':{'n':'Călugăreni','d':55,'j':'Giurgiu','t':'rural','r':'DN5','v':'curti largi, sala locala, camp deschis','pop':1300,'jud_info':'sat cu traditie istorica in Giurgiu'},
  'campurelu':{'n':'Câmpurelu','d':70,'j':'Giurgiu','t':'rural','r':'DJ412A','v':'curti case, gradina, sala scolii','pop':600,'jud_info':'sat mic din Giurgiu'},
  'candeasca':{'n':'Cândeasca','d':65,'j':'Dambovita','t':'rural','r':'DJ711','v':'curti spatioase, sala scolii, spatiu deschis','pop':700,'jud_info':'sat dambovitean'},
  'catelu':{'n':'Catelu','d':10,'j':'Ilfov','t':'suburban','r':'Str. Catelu','v':'curti case, sali petreceri, spatiu semi-urban','pop':6000,'jud_info':'zona limitrofa Sectorului 3'},
  'catrunesti':{'n':'Câtrunești','d':75,'j':'Giurgiu','t':'rural','r':'DJ412B','v':'curti largi, casa locala, gradina','pop':500,'jud_info':'sat izolat in Giurgiu'},
  'cernica':{'n':'Cernica','d':14,'j':'Ilfov','t':'suburban','r':'DJ301','v':'Manastirea Cernica, curti vile, lacul Cernica','pop':8000,'jud_info':'suburbie cu manastire si lac'},
  'chiajna':{'n':'Chiajna','d':8,'j':'Ilfov','t':'suburban','r':'DN7','v':'Militari Residence, sali petreceri, curti ansambluri','pop':30000,'jud_info':'oras cu cel mai mare ansamblu din RO'},
  'chirculesti':{'n':'Chirculești','d':35,'j':'Ilfov','t':'rural','r':'DJ301','v':'curti case, sala locala, spatiu deschis','pop':1500,'jud_info':'sat Ilfov linistit'},
  'chitila':{'n':'Chitila','d':12,'j':'Ilfov','t':'suburban','r':'DN7A','v':'Parcul Chitila, sali petreceri, curti case','pop':12000,'jud_info':'oras suburban nord-vest'},
  'ciocanesti':{'n':'Ciocanești','d':30,'j':'Ilfov','t':'suburban','r':'DN2A','v':'curti vile, sali noi, zona rezidentiala','pop':5000,'jud_info':'suburbie Ilfov pe DN2A'},
  'ciofliceni':{'n':'Ciofliceni','d':22,'j':'Ilfov','t':'suburban','r':'A3','v':'vile curti mari, zona nord premium, lac Snagov aproape','pop':4000,'jud_info':'zona premium nord Ilfov'},
  'ciorogarla':{'n':'Ciorogârla','d':18,'j':'Ilfov','t':'suburban','r':'DN7','v':'curti case, sala locala, zona verde','pop':7000,'jud_info':'suburbie vest pe DN7'},
  'ciorogirla':{'n':'Ciorogârla (sat)','d':18,'j':'Ilfov','t':'suburban','r':'DN7','v':'curti ansambluri, sali noi, zona rezidentiala','pop':6000,'jud_info':'zona rezidentiala vest Ilfov'},
  'clinceni':{'n':'Clinceni','d':15,'j':'Ilfov','t':'suburban','r':'DJ602','v':'curti vile, sala locala, zona verde','pop':5000,'jud_info':'suburbie Ilfov sud-vest'},
  'cocani':{'n':'Cocani','d':35,'j':'Ilfov','t':'rural','r':'DJ301B','v':'curti largi, sala scolii, spatiu rural','pop':1800,'jud_info':'sat Ilfov rural'},
  'cojasca':{'n':'Cojasca','d':45,'j':'Dambovita','t':'rural','r':'DN71','v':'curti case, sala locala, gradina','pop':2000,'jud_info':'sat dambovitean pe DN71'},
  'cojesti':{'n':'Cojești','d':60,'j':'Dambovita','t':'rural','r':'DJ711','v':'curti spatioase, sala scolii, spatiu deschis','pop':700,'jud_info':'sat mic dambovitean'},
  'colibasi':{'n':'Colibași','d':72,'j':'Giurgiu','t':'rural','r':'DN5+DJ412','v':'curti largi, sala polivalenta, spatiu deschis','pop':1500,'jud_info':'sat din sudul Giurgiului'},
  'comana':{'n':'Comana','d':55,'j':'Giurgiu','t':'rural','r':'DN5','v':'curti case, Parcul Natural Comana 24000ha, sala locala','pop':3000,'jud_info':'zona Parcului Natural Comana'},
  'copaceni':{'n':'Copăceni','d':28,'j':'Giurgiu','t':'rural','r':'DN5','v':'curti largi, sala comunala, zona verde','pop':1200,'jud_info':'sat Giurgiu pe DN5'},
  'corbeanca':{'n':'Corbeanca','d':20,'j':'Ilfov','t':'suburban','r':'DN1','v':'vile premium curti, parc privat, zona exclusivista nord','pop':5000,'jud_info':'zona premium nord Ilfov langa Otopeni'},
  'cornetu':{'n':'Cornetu','d':20,'j':'Ilfov','t':'suburban','r':'DN7','v':'curti vile, sali comunitate, zona verde','pop':8000,'jud_info':'suburbie Ilfov vest'},
  'cosoba':{'n':'Cosoba','d':65,'j':'Ilfov','t':'rural','r':'DJ301C','v':'curti case, sala locala, spatiu rural','pop':1000,'jud_info':'sat mic Ilfov rural'},
  'coteni':{'n':'Coneni','d':70,'j':'Giurgiu','t':'rural','r':'DN5+deviatie','v':'curti spatioase, sala comunei, gradina','pop':800,'jud_info':'sat indepartat din Giurgiu'},
  'cozieni':{'n':'Cozieni','d':65,'j':'Giurgiu','t':'rural','r':'DJ412C','v':'curti largi, gradina casei, sala locala','pop':900,'jud_info':'sat giurgiuvean'},
  'cranguri':{'n':'Cranguri','d':55,'j':'Dambovita','t':'rural','r':'DJ711B','v':'curti case, sala scolii, spatiu deschis','pop':700,'jud_info':'sat dambovitean mic'},
  'creata':{'n':'Creata','d':35,'j':'Ilfov','t':'rural','r':'DJ301D','v':'curti case, sala locala, zona verde','pop':1200,'jud_info':'sat Ilfov rural'},
  'cretesti':{'n':'Cretesti','d':28,'j':'Ilfov','t':'suburban','r':'DJ602B','v':'curti vile, sali noi, zona rezidentiala','pop':4000,'jud_info':'suburbie Ilfov'},
  'cretuleasca':{'n':'Cretuleasca','d':38,'j':'Ilfov','t':'rural','r':'DN2A','v':'curti case, sala scolii, spatiu verde','pop':2000,'jud_info':'sat Ilfov rural pe DN2A'},
  'crevedia':{'n':'Crevedia','d':30,'j':'Dambovita','t':'suburban','r':'DN7','v':'curti ansambluri, sala locala, zona verde','pop':6000,'jud_info':'suburbie damboviteana pe DN7'},
  'crevedia-mare':{'n':'Crevedia Mare','d':32,'j':'Giurgiu','t':'rural','r':'DN6','v':'curti case, sala locala, gradina','pop':1500,'jud_info':'sat Giurgiu pe DN6'},
  'crivina':{'n':'Crivina','d':25,'j':'Ilfov','t':'suburban','r':'DN1','v':'vile curti, zona padure, premium nord','pop':3000,'jud_info':'zona paduroasa nord Ilfov'},
  'cucuieti':{'n':'Cucuieti','d':60,'j':'Dambovita','t':'rural','r':'DJ711','v':'curti spatioase, sala scolii, gradina','pop':600,'jud_info':'sat dambovitean'},
  'dambovita':{'n':'Dâmbovița','d':65,'j':'Dambovita','t':'suburban','r':'DN7','v':'sali events, restaurante, Parcul Targoviste','pop':12000,'jud_info':'judetul cu orasul Targoviste'},
  'dascalu':{'n':'Dascălu','d':22,'j':'Ilfov','t':'suburban','r':'DN2','v':'curti vile Dascalu, sali evenimente, zona rezidentiala','pop':7000,'jud_info':'suburbie est Ilfov pe DN2'},
  'decindea':{'n':'Decindea','d':55,'j':'Dambovita','t':'rural','r':'DJ711','v':'curti largi, sala locala, spatiu deschis','pop':700,'jud_info':'sat dambovitean'},
  'dimieni':{'n':'Dimieni','d':20,'j':'Ilfov','t':'suburban','r':'DN2','v':'curti ansambluri, sali community, zona verde','pop':5000,'jud_info':'suburbie est pe DN2'},
  'dobreni':{'n':'Dobreni','d':75,'j':'Ilfov','t':'rural','r':'DJ301E','v':'curti case, sala scolii, spatiu rural','pop':1000,'jud_info':'sat Ilfov rural indepartat'},
  'dobroesti':{'n':'Dobroești','d':12,'j':'Ilfov','t':'suburban','r':'DN2','v':'sali moderne, curti vile, zona rezidentiala','pop':10000,'jud_info':'suburbie est dinamica'},
  'domnesti':{'n':'Domneșiii','d':22,'j':'Ilfov','t':'suburban','r':'DN7','v':'sali petreceri, curti case, zona verde','pop':9000,'jud_info':'suburbie vest Ilfov'},
  'dragomiresti-deal':{'n':'Dragomirești-Deal','d':22,'j':'Ilfov','t':'suburban','r':'DN1A','v':'vile curti mari, zona premium rezidentiala, padure aproape','pop':4000,'jud_info':'zona premium nord DN1A'},
  'dragomiresti-vale':{'n':'Dragomirești-Vale','d':22,'j':'Ilfov','t':'suburban','r':'DN1A','v':'curti vile, zona rezidentiala premium, spatii verzi','pop':4000,'jud_info':'zona rezidentiala nord Ilfov'},
  'fierbinti-targ':{'n':'Fierbinți-Târg','d':65,'j':'Ialomita','t':'urban-mic','r':'DN2','v':'sala culturala, curti case, parcul local','pop':6000,'jud_info':'orasel pe DN2 in Ialomita'},
  'fundulea':{'n':'Fundulea','d':45,'j':'Calarasi','t':'urban-mic','r':'A2','v':'sala events, restaurante, parcul orasului','pop':8000,'jud_info':'oras la iesirea din A2 spre Calarasi'},
  'ganeasa':{'n':'Găneasa','d':18,'j':'Ilfov','t':'suburban','r':'DJ602C','v':'curti vile, sali noi, zona verde','pop':5000,'jud_info':'suburbie Ilfov'},
  'giurgiu':{'n':'Giurgiu','d':65,'j':'Giurgiu','t':'urban','r':'DN5','v':'sali events multiple, restaurante, Parcul Alei, Dunarea','pop':55000,'jud_info':'oras la Dunare, poarta spre Bulgaria'},
  'glina':{'n':'Glina','d':16,'j':'Ilfov','t':'suburban','r':'A2','v':'curti vile, sali petreceri, zona rezidentiala sud','pop':7000,'jud_info':'suburbie pe A2 sud'},
  'ialomita':{'n':'Ialomița','d':90,'j':'Ialomita','t':'suburban','r':'A2+DN2A','v':'sali events Slobozia, restaurante, Parcul Slobozia','pop':40000,'jud_info':'judetul Ialomita, resedinta Slobozia'},
  'iepuresti':{'n':'Iepurești','d':50,'j':'Giurgiu','t':'rural','r':'DN5','v':'curti case, sala scolii, spatiu verde','pop':1500,'jud_info':'sat giurgiuvean pe DN5'},
  'jilava':{'n':'Jilava','d':10,'j':'Ilfov','t':'suburban','r':'DN41','v':'sali petreceri noi, curti ansambluri, zona sud','pop':12000,'jud_info':'suburbie sudica langa Capitala'},
  'magurele':{'n':'Măgurele','d':12,'j':'Ilfov','t':'suburban','r':'DJ602','v':'sali events, curti case, zona Institut Atomic','pop':10000,'jud_info':'oras cu institut nuclear, Ilfov sud'},
  'mihai-voda':{'n':'Mihai Vodă','d':55,'j':'Calarasi','t':'rural','r':'DN3','v':'curti case, sala locala, gradina','pop':2000,'jud_info':'sat calarasean pe DN3'},
  'mihailesti':{'n':'Mihailești','d':40,'j':'Giurgiu','t':'urban-mic','r':'DN5','v':'sala culturala, restaurante, centrul orasului','pop':6000,'jud_info':'orasel pe DN5 in Giurgiu'},
  'moara-vlasiei':{'n':'Moara Vlăsiei','d':30,'j':'Ilfov','t':'suburban','r':'DN1','v':'vile curti, padure Vlasiei, zona exclusivista','pop':3500,'jud_info':'zona paduroasa premium nord Ilfov'},
  'mogosoaia':{'n':'Mogoșoaia','d':16,'j':'Ilfov','t':'suburban','r':'DN1A','v':'Palatul Mogosoaia, curti vile premium, Lacul Mogosoaia','pop':6000,'jud_info':'suburbie cu palat renascentist si lac'},
  'nuci':{'n':'Nuci','d':30,'j':'Ilfov','t':'rural','r':'DJ301F','v':'curti case, sala locala, spatiu verde','pop':1500,'jud_info':'sat Ilfov rural'},
  'ordoreanu-vatra-veche':{'n':'Ordoreanu-Vatra Veche','d':70,'j':'Giurgiu','t':'rural','r':'DJ412','v':'curti largi, sala scolii, gradina','pop':600,'jud_info':'sat giurgiuvean izolat'},
  'otopeni':{'n':'Otopeni','d':14,'j':'Ilfov','t':'suburban','r':'DN1','v':'sali moderne, restaurante, zona aeroportului Henri Coanda','pop':12000,'jud_info':'oras la aeroport, nord Ilfov'},
  'pantelimon':{'n':'Pantelimon','d':12,'j':'Ilfov','t':'suburban','r':'Sos. Pantelimon','v':'sali petreceri, curti ansambluri, Lacul Pantelimon','pop':18000,'jud_info':'oras suburban est cu lac'},
  'peris':{'n':'Periș','d':28,'j':'Ilfov','t':'suburban','r':'DN1','v':'vile curti, Lacul Snagov in apropiere, zona verde','pop':4000,'jud_info':'suburbie nord cu acces la Snagov'},
  'petrachioaia':{'n':'Petrachioaia','d':22,'j':'Ilfov','t':'suburban','r':'DN2','v':'curti vile, sali noi, zona rezidentiala est','pop':5000,'jud_info':'suburbie est Ilfov'},
  'popesti-leordeni':{'n':'Popești-Leordeni','d':8,'j':'Ilfov','t':'suburban','r':'A2 iesire','v':'sali petreceri multiple, curti, zona sud Capitala','pop':35000,'jud_info':'uno din cele mai populate orase din Ilfov'},
  'prahova':{'n':'Prahova','d':45,'j':'Prahova','t':'suburban','r':'DN1','v':'sali events Ploiesti, restaurante, Parcul Ploiesti','pop':50000,'jud_info':'judetul cu Ploiesti si Sinaia'},
  'racari':{'n':'Răcari','d':35,'j':'Dambovita','t':'urban-mic','r':'DN1A','v':'sala culturala, restaurante, centrul Racari','pop':7000,'jud_info':'oras dambovitean pe DN1A'},
  'snagov':{'n':'Snagov','d':35,'j':'Ilfov','t':'suburban','r':'DN1+DJ101','v':'Lacul Snagov, vile premium, restaurante la malul apei','pop':4000,'jud_info':'zona lacustra premium nord Ilfov'},
  'stefanestii-de-jos':{'n':'Ștefăneștii de Jos','d':22,'j':'Ilfov','t':'suburban','r':'DN2','v':'curti ansambluri, sali noi, zona rezidentiala est','pop':8000,'jud_info':'suburbie est Ilfov'},
  'teleorman':{'n':'Teleorman','d':90,'j':'Teleorman','t':'suburban','r':'DN6/DN51','v':'sali events Alexandria, restaurante, Parcul Alexandru Vlahuta','pop':45000,'jud_info':'judetul Teleorman, resedinta Alexandria'},
  'tunari':{'n':'Tunari','d':15,'j':'Ilfov','t':'suburban','r':'Str. Tunari','v':'curti vile, sali moderne, zona premium nord Bucuresti','pop':7000,'jud_info':'suburbie nord premium Ilfov'},
  'valea-piersicilor':{'n':'Valea Piersicilor','d':25,'j':'Ilfov','t':'suburban','r':'DN2','v':'curti vile, sali noi, zona rezidentiala est Ilfov','pop':4000,'jud_info':'ansambluri rezidentiale est Ilfov'},
  'vidra':{'n':'Vidra','d':22,'j':'Ilfov','t':'suburban','r':'DJ417','v':'curti case, sali locale, zona verde Vidra','pop':7000,'jud_info':'suburbie Ilfov'},
  'voluntari':{'n':'Voluntari','d':10,'j':'Ilfov','t':'suburban','r':'Sos. Pipera','v':'Promenada Mall, curti vile Pipera, sali premium','pop':40000,'jud_info':'oras Ilfov cu zona internationala Pipera'},
  'sector-1':{'n':'Sectorul 1','d':0,'j':'Sectorul 1','t':'sector','r':'Calea Victoriei/DN1','v':'Parcul Herastrau, vile premium, restaurante nord','pop':222000,'jud_info':'sectorul nordic cu zona premium'},
  'sector-2':{'n':'Sectorul 2','d':0,'j':'Sectorul 2','t':'sector','r':'Calea Mosilor/DN2','v':'Lacul Floreasca, Lacul Colentina, sali petreceri','pop':350000,'jud_info':'sectorul cu lacuri si zone mixte'},
  'sector-3':{'n':'Sectorul 3','d':0,'j':'Sectorul 3','t':'sector','r':'Calea Vitan/A2','v':'Sun Plaza Mall, Parcul IOR, Lacul IOR','pop':400000,'jud_info':'cel mai populat sector, zona Titan/Vitan'},
  'sector-4':{'n':'Sectorul 4','d':0,'j':'Sectorul 4','t':'sector','r':'Calea Oltenitei/A2','v':'Parcul Tineretului 210ha, Vitan Mall, sali sud','pop':300000,'jud_info':'sectorul cu cel mai mare parc din sud'},
  'sector-5':{'n':'Sectorul 5','d':0,'j':'Sectorul 5','t':'sector','r':'Calea Rahovei/metrou M4','v':'Parcul Sebastian, curtile caselor, sali locale','pop':270000,'jud_info':'sectorul cu caracter familial extins'},
  'sector-6':{'n':'Sectorul 6','d':0,'j':'Sectorul 6','t':'sector','r':'Bd Timisoara/metrou M5','v':'Plaza Romania, Parcul DT, sali multiple','pop':380000,'jud_info':'cel mai populat sector, zona Militari'},
  'ilfov':{'n':'Ilfov','d':15,'j':'Ilfov','t':'judet','r':'A1/A2/DN1','v':'30+ localitati acoperite, sali diverse, curti case','pop':500000,'jud_info':'judetul cu cea mai rapida crestere din Romania'},
  'bucuresti':{'n':'București','d':0,'j':'Bucuresti','t':'capitala','r':'metrou/autobuz/tram','v':'6 sectoare, sali premium, parcuri, malluri','pop':2500000,'jud_info':'capitala cu 2.5 milioane locuitori'},
  '1-decembrie':{'n':'1 Decembrie','d':20,'j':'Ilfov','t':'suburban','r':'DJ602D','v':'curti vile, sali community, zona rezidentiala','pop':5000,'jud_info':'suburbie Ilfov pe DJ602D'},
};

// Pool paragrafe unice per tip
const pools={
  rural:[
    ['curtea spatioasa a casei este locatia perfecta pentru petrecerile de copii in mediul rural',
     'animatorul vine cu boxe portabile wireless si organizeaza programul direct in curtea ta',
     'familia si vecinii se aduna — petrecerile rurale au un caracter comunitar cald',
     'spatiul verde larg permite jocuri de exterior cu toata energia'],
    ['Parcul sau spatiul verde al localitatii este cadrul natural pentru petreceri de vara',
     'grila de locatii: gradina casei, sala scolii, parcul comunal sau curtea gradinitei',
     'fara zgomotul orasului si fara lipsa de spatiu — avantajul esential al zonelor rurale',
     'copiii alerga liberi, parintii stau relaxati — animatorul coordoneaza totul profesional'],
    ['Bunicii, vecinii si prietenii de la scoala vin toti la petrecere — asa e in sat',
     'SuperParty a organizat zeci de petreceri in comune rurale si stie exact cum sa antreneze toata lumea',
     'Jocurile de grup cu echipe (rosii vs albastri) functioneaza perfect in spatii deschise',
     'nu e nevoie de sala inchiriata scumpa — o curte mare e mai buna'],
  ],
  suburban:[
    ['Ansamblurile rezidentiale noi au curti interioare amenajate, perfecte pentru petreceri cu 15-30 copii',
     'animatorul supravegheaza programul in oricare spatiu disponibil — interior sau exterior',
     'distanta mica de la Bucuresti inseamna punctualitate garantata si costuri de deplasare minime',
     'blocurile noi au si sali comunitare disponibile la cerere'],
    ['Zona periurbana ofera avantajul spatiului mai larg fata de centrul Capitalei',
     'curtile generoase ale vilelor sunt perfecte pentru petrecerile de vara',
     'sali de evenimente moderne au aparut in toate suburbiile importante ale Ilfovului',
     'transportul animatorului este rapid pe autostrada sau DN'],
    ['Familiile mutate din Bucuresti in suburb apreciaza calitatea SuperParty',
     'acelasi serviciu premium ca in Capitala, livrare directa la usa',
     'confirmam disponibilitatea in 30 minute si ajungem intotdeauna punctual',
     'costul deplasarii se stabileste transparent la rezervare'],
  ],
  'urban-mic':[
    ['Orasele mici din jurul Capitalei au sali culturale si restaurante family-friendly adecvate',
     'SuperParty este adesea o premiera in orasele mai mici — reactia copiilor este exploziva',
     'sala culturala sau restaurantul local pot fi rezervate cu 3-4 saptamani inainte',
     'animatorul vine complet echipat, fara niciun cost ascuns'],
    ['In orasele mici, o petrecere cu animator SuperParty devine evenimentul anului',
     'parintii recomanda serviciul la toata scoala — suntem cel mai word-of-mouth brand',
     'deplasarea la orase mai departe implica taxa de transport — transparenta totala la rezervare',
     'confirmam oferta in 30 minute de la primul contact'],
  ],
  sector:[
    ['Sectoarele Capitalei acopera zone extrem de diverse — de la vile premium la curti de bloc',
     'SuperParty acopera orice adresa din sector fara taxa de deplasare',
     'confirmarea disponibilitatii se face in 30 minute dupa primul apel',
     'cel mai mare numar de animatori disponibili in weekend in toata Romania'],
    ['Zero taxa deplasare in orice sector al Capitalei — este inclusa in pretul pachetului',
     'avem animatori dedicati pentru fiecare zona a sectorului',
     'pakete de la 490 RON cu garantie contractuala unica pe piata',
     'confirmare rapida si contract digital in 24 ore'],
  ],
  judet:[
    ['Acoperim intregul judet — orasul resedinta si toate comunele',
     'animatorul vine cu tot echipamentul direct la adresa ta',
     'rezervare cu 2-3 saptamani inainte pentru weekenduri',
     'taxa de deplasare transparenta la rezervare'],
    ['Familiile din judet merita acelasi serviciu premium ca in Capitala',
     'SuperParty vine la orice adresa din judet cu echipament complet',
     'confirmare disponibilitate in 30 minute, contract in 24 ore',
     'garantie contractuala — daca nu v-ati distrat, nu platiti'],
  ],
  capitala:[
    ['Capitala cu 2.5 milioane locuitor — cea mai mare diversitate de locatii din Romania',
     'sali premium, parcuri, malluri, curti de bloc — acoperim orice tip de locatie',
     'zero taxa deplasare in Bucuresti pentru orice sector',
     'echipa cea mai numeroasa si mai experimentata din tara'],
    ['SuperParty opereaza in toata Capitala din 2018 — peste 10.000 de petreceri',
     'cunoastem fiecare sector, fiecare cartier, fiecare locatie potrivita',
     'pachete de la 490 la 1290 RON cu garantie contractuala',
     'rezervare online sau telefonica, confirmare in 30 minute'],
  ],
};

const tipMap={'rural':'rural','suburban':'suburban','urban-mic':'urban-mic','sector':'sector','judet':'judet','capitala':'capitala'};

function getPool(tip) { return pools[tipMap[tip]] || pools.suburban; }

const charsByType = {
  rural:['Spider-Man','Elsa','Batman si Robin','Minnie Mouse','Clownul vesel','Captain America'],
  suburban:['Spider-Man','Elsa','Batman','Captain America','PAW Patrol','Sonic','Bluey'],
  'urban-mic':['Spider-Man','Elsa','Batman','Minnie Mouse','Rapunzel','Iron Man'],
  sector:['Spider-Man','Elsa','Batman','Iron Man','PAW Patrol','Sonic','Bluey','Miraculous Ladybug'],
  judet:['Spider-Man','Elsa','Batman','Minnie Mouse','Captain America','PAW Patrol'],
  capitala:['Spider-Man','Elsa','Batman','Iron Man','Rapunzel','PAW Patrol','Miraculous','Bluey','Sonic'],
};

function buildPage(slug, c) {
  const hv = h(slug);
  const pool = getPool(c.t);
  const variant = pool[hv % pool.length];
  const chars = charsByType[c.t] || charsByType.suburban;
  const c1 = chars[(hv+0) % chars.length];
  const c2 = chars[(hv+1) % chars.length];
  const c3 = chars[(hv+2) % chars.length];
  const distStr = c.d > 0 ? `~${c.d} km de Bucuresti (${c.r})` : 'in Bucuresti (zero taxa deplasare)';
  const popStr = c.pop > 10000 ? `cu peste ${(c.pop/1000).toFixed(0)}.000 de locuitori` : `cu aproximativ ${c.pop} locuitori`;
  const isRural = c.t === 'rural';
  const venues = c.v.split(', ');

  return `---
import Layout from '../../layouts/Layout.astro';

const schema = JSON.stringify({
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Service",
      "name": "Animatori Petreceri Copii ${c.n}",
      "provider": {"@type": "LocalBusiness", "name": "SuperParty", "telephone": "+40722744377"},
      "areaServed": "${c.n}",
      "url": "https://superparty.ro/petreceri/${slug}"
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {"@type":"Question","name":"Organizati animatori in ${c.n}?","acceptedAnswer":{"@type":"Answer","text":"Da — SuperParty acopera ${c.n} si zona ${c.j}. Sunati la 0722 744 377 cu data si adresa pentru confirmare disponibilitate."}},
        {"@type":"Question","name":"Este taxa de deplasare pentru ${c.n}?","acceptedAnswer":{"@type":"Answer","text":"${c.d > 0 ? `Distanta este ~${c.d} km pe ${c.r} — taxa de deplasare se stabileste transparent la rezervare in functie de adresa exacta.` : 'Nu exista taxa de deplasare in ' + c.n + ' — este inclusa in pretul pachetului.'}"}},
        {"@type":"Question","name":"Unde se organizeaza petrecerea in ${c.n}?","acceptedAnswer":{"@type":"Answer","text":"In ${c.n} recomandam: ${venues.slice(0,2).join(' sau ')}. Animatorul vine cu echipament portabil complet — boxe wireless, materiale jocuri, costume premium."}},
        {"@type":"Question","name":"Ce personaje sunt disponibile in ${c.n}?","acceptedAnswer":{"@type":"Answer","text":"Cele mai cerute in zona ${c.j}: ${c1}, ${c2} si ${c3}. SuperParty are peste 50 de personaje disponibile la rezervare."}},
        {"@type":"Question","name":"Cat timp inainte rezervam animatorul?","acceptedAnswer":{"@type":"Answer","text":"Minim 7-14 zile pentru saptamani normale, 3-4 saptamani pentru weekendurile de mai-septembrie. Suna la 0722 744 377."}}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type":"ListItem","position":1,"name":"Acasa","item":"https://superparty.ro"},
        {"@type":"ListItem","position":2,"name":"Animatori Petreceri Copii","item":"https://superparty.ro/animatori-petreceri-copii"},
        {"@type":"ListItem","position":3,"name":"${c.n}","item":"https://superparty.ro/petreceri/${slug}"}
      ]
    }
  ]
});
---

<Layout
  title="Animatori Petreceri Copii ${c.n} | SuperParty — de la 490 RON"
  description="Animatori profesionisti pentru petreceri copii in ${c.n} (${c.j}), ${distStr}. Peste 50 personaje, pachete 490-1290 RON, garantie contractuala. Tel: 0722 744 377."
  canonical="https://www.superparty.ro/petreceri/${slug}"
  robots="index, follow"
  schema={schema}
>
<style>
  .loc-hero{padding:4rem 0 2.5rem;background:radial-gradient(ellipse at top,rgba(255,107,53,.1) 0%,transparent 55%)}
  .loc-hero h1{font-size:clamp(1.7rem,4vw,2.6rem);font-weight:800;margin-bottom:1rem;line-height:1.2}
  .loc-hero p{color:var(--text-muted);font-size:1rem;max-width:600px;line-height:1.8;margin-bottom:1.8rem}
  .btn-p{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;transition:transform .2s}
  .btn-p:hover{transform:translateY(-2px)}
  .btn-wa{background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem}
  .loc-s{padding:3rem 0}.loc-s-alt{padding:3rem 0;background:var(--dark-2)}
  .sec-title{font-size:1.5rem;font-weight:800;margin-bottom:.5rem}
  .info-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem}
  .info-card{background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.3rem}
  .info-card h3{font-weight:700;margin-bottom:.5rem;font-size:.95rem}
  .info-card ul{list-style:none;padding:0}
  .info-card li{padding:.3rem 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:.88rem;color:var(--text-muted)}
  .rich-text p{color:var(--text-muted);line-height:1.9;margin-bottom:1rem;max-width:780px}
  .rich-text strong{color:var(--text)}
  .faq-list{display:flex;flex-direction:column;gap:.9rem;max-width:700px}
  .faq-item{background:var(--dark-3);border:1px solid rgba(255,107,53,.12);border-radius:12px;padding:1.2rem}
  .faq-item h3{font-size:.93rem;font-weight:700;margin-bottom:.4rem}
  .faq-item p{font-size:.88rem;color:var(--text-muted);line-height:1.7}
  .cta-box{background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.05));border:1px solid rgba(255,107,53,.25);border-radius:18px;padding:2.5rem 1.5rem;text-align:center}
  .cta-box h2{font-size:1.5rem;font-weight:800;margin-bottom:.8rem}
  .cta-box p{color:var(--text-muted);margin-bottom:1.5rem;font-size:.95rem}
  .cta-btns{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center}
</style>

<section class="loc-hero">
  <div class="container">
    <nav style="font-size:.82rem;color:var(--text-muted);margin-bottom:1.5rem">
      <a href="/" style="color:var(--primary)">Acasa</a> ›
      <a href="/animatori-petreceri-copii" style="color:var(--primary)">Animatori Petreceri Copii</a> ›
      ${c.n}
    </nav>
    <h1>Animatori Petreceri Copii <span style="color:var(--primary)">${c.n}</span></h1>
    <p>SuperParty organizeaza petreceri de copii in <strong>${c.n}</strong>, ${c.jud_info} ${popStr}. Animatori actori cu costume premium, jocuri interactive, face painting si mini disco — direct la adresa ta, ${distStr}. Garantie contractuala: daca copiii nu s-au distrat, nu platesti.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="tel:+40722744377" class="btn-p cta">📞 Rezerva: 0722 744 377</a>
      <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section class="loc-s">
  <div class="container">
    <h2 class="sec-title">Pachete animatori in <span style="color:var(--primary)">${c.n}</span></h2>
    <div class="info-grid">
      <div class="info-card">
        <h3>📦 Super 1 — 490 RON</h3>
        <ul>
          <li>1 personaj costumat premium</li>
          <li>Durata: 2 ore program complet</li>
          <li>Jocuri interactive + baloane modelate</li>
          <li>Face painting + tatuaje temporare</li>
          <li>Mini disco + diplome magnetic</li>
          <li>Transport inclus in ${c.n}</li>
        </ul>
      </div>
      <div class="info-card">
        <h3>⭐ Super 3 — 840 RON (cel mai ales)</h3>
        <ul>
          <li>2 personaje costumati premium</li>
          <li>Durata: 2 ore program dublu</li>
          <li>Jocuri duble + confetti + baloane</li>
          <li>Atentie individuala per copil</li>
          <li>Recomandat pentru 15-35 copii</li>
          <li>Transport inclus in ${c.n}</li>
        </ul>
      </div>
      <div class="info-card">
        <h3>👑 Super 7 — 1290 RON</h3>
        <ul>
          <li>1 animator + 4 ursitoare, 3 ore</li>
          <li>Pachet botez sau aniversare mare</li>
          <li>Program complet extins</li>
          <li>Ideal 50-100 invitati</li>
          <li>Transport inclus in ${c.n}</li>
          <li><a href="/animatori-petreceri-copii" style="color:var(--primary)">→ Toate pachetele</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="loc-s-alt">
  <div class="container">
    <h2 class="sec-title">Locatii si petreceri in <span style="color:var(--primary)">${c.n}</span></h2>
    <div class="rich-text">
      <p><strong>${variant[0]}.</strong> In <strong>${c.n}</strong> (${c.j}), locatiile disponibile includ: <strong>${venues[0]}</strong>${venues[1] ? ', <strong>' + venues[1] + '</strong>' : ''}${venues[2] ? ' si <strong>' + venues[2] + '</strong>' : ''}. ${variant[1]}.</p>
      <p>${c.jud_info.charAt(0).toUpperCase() + c.jud_info.slice(1)} — SuperParty acopera zona completa, ${distStr}. ${variant[2]}. Animatorul vine cu boxe portabile wireless, costume premium licentiate, materiale pentru jocuri interactive, baloane si tot ce e necesar pentru un program de 2-3 ore fara momente goale.</p>
      <p>${variant[3]}. Spatiul minim necesar este de 15-20 mp — in rest, animatorul se adapteaza la orice configuratie de spatiu. ${isRural ? 'In curtile spatioase specifice zonei rurale, programul se desfasoara perfect in aer liber, cu toata energia si miscare libera pentru copii.' : 'Fie ca este o sala dedicata sau o curte de bloc, rezultatul este acelasi: copii fericiti si parinti relaxati.'}</p>
    </div>
  </div>
</section>

<section class="loc-s">
  <div class="container">
    <h2 class="sec-title">Personaje disponibile in <span style="color:var(--primary)">${c.n}</span></h2>
    <div class="rich-text">
      <p>Cele mai cerute personaje SuperParty in zona <strong>${c.j}</strong>: <strong>${c1}</strong>, <strong>${c2}</strong> si <strong>${c3}</strong>. SuperParty aduce aceleasi costume premium licentiate in ${c.n} ca si in inima Capitalei — zero compromis la calitate indiferent de distanta.</p>
      <p>Colectia completa SuperParty include peste <strong>50 de personaje</strong> disponibile la rezervare: super-eroi (Spider-Man, Batman, Captain America, Iron Man, Thor), printese Disney (Elsa, Rapunzel, Belle, Ariel, Aurora, Moana), personaje moderne (PAW Patrol, Sonic, Bluey, Miraculous Ladybug, Encanto), clasice (Clovnul vesel, Magicianul, Zanele). La doua saptamani dupa lansarea unui nou film sau serial, personajul apare in colectia noastra.</p>
      <p>Programul inclus in orice pachet: <strong>jocuri interactive</strong> adaptate varstei (3-12 ani), <strong>baloane modelate</strong> pentru fiecare copil (animale, sabii, coroane), <strong>face painting</strong> tematic cu personajul ales, <strong>tatuaje temporare</strong> profesionale, <strong>mini disco</strong> cu muzica pentru copii si dans, <strong>diplome magnetice</strong> personalizate cu numele copilului aniversat.</p>
    </div>
  </div>
</section>

<section class="loc-s-alt">
  <div class="container">
    <h2 class="sec-title">Cum rezervi animatori in <span style="color:var(--primary)">${c.n}</span></h2>
    <div class="rich-text">
      <p><strong>Pas 1 — Contacteaza:</strong> Suna la <strong>0722 744 377</strong> sau trimite un mesaj WhatsApp cu: data petrecerii, adresa exacta in ${c.n}, varsta copilului aniversat si numarul aproximativ de copii invitati. Confirmare disponibilitate garantata in 30 minute.</p>
      <p><strong>Pas 2 — Alege pachetul:</strong> Super 1 (490 RON, 1 personaj, 2 ore) pentru petreceri intime de 10-20 copii. Super 3 (840 RON, 2 personaje, 2 ore) pentru petreceri medii de 15-35 copii. Super 7 (1290 RON, 3 ore botez complet) pentru evenimente mari cu 50-100 invitati.</p>
      <p><strong>Pas 3 — Contract si confirmare:</strong> Trimitem contractul digital in 24 ore. Plata se face DUPA petrecere, nu inainte. <strong>Garantia SuperParty</strong>: daca copiii nu s-au distrat si nu au ramas cu zambet pe fata, nu platesti — singurul serviciu de animatori din Romania cu garantie contractuala scrisa.</p>
      <p><strong>Avans rezervare recomandat:</strong> ${c.d > 40 ? '3-4 saptamani pentru localitatile mai indepartate, mai ales in sezonul mai-septembrie.' : '7-14 zile pentru saptamani normale, 2-3 saptamani pentru weekenduri si sezon mai-septembrie.'} Locurile pentru weekend se ocupa rapid — nu amanati rezervarea!</p>
    </div>
  </div>
</section>

<section class="loc-s">
  <div class="container">
    <h2 class="sec-title">Intrebari despre animatori in <span style="color:var(--primary)">${c.n}</span></h2>
    <div class="faq-list">
      {[
        ["Organizati animatori in ${c.n}?", "Da — SuperParty acopera ${c.n} si zona ${c.j}. Sunati la 0722 744 377 cu data si adresa pentru confirmare disponibilitate in 30 minute."],
        ["Este taxa de deplasare pentru ${c.n}?", "${c.d > 0 ? `Distanta este ~${c.d} km de la Bucuresti pe ${c.r}. Taxa de deplasare se stabileste transparent la rezervare in functie de adresa exacta si ziua petrecerii.` : 'Nu exista taxa de deplasare in ' + c.n + ' — este inclusa in pretul pachetului selectat.'}"],
        ["Unde se organizeaza petrecerea in ${c.n}?", "Recomandam: ${venues[0]}${venues[1] ? ' sau ' + venues[1] : ''}. SuperParty se adapteaza oricarui spatiu cu minim 15-20 mp liberi. Aducem tot echipamentul necesar."],
        ["Ce personaje pot alege pentru petrecerea din ${c.n}?", "Colectia cuprinde 50+ personaje: ${c1}, ${c2}, ${c3} si multi altii. Mentionati preferinta la rezervare — verificam disponibilitatea costumului specific in acel weekend."],
        ["Cu cat timp inainte rezervam animatorul in ${c.n}?", "Minim 7-14 zile pentru saptamani normale. Pentru weekenduri de mai-septembrie si Craciun rezervati cu 3-4 saptamani inainte. Suna la 0722 744 377."],
      ].map(([q,a]) => (
        <div class="faq-item">
          <h3>❓ {q}</h3>
          <p>{a}</p>
        </div>
      ))}
    </div>
  </div>
</section>

<section class="loc-s-alt">
  <div class="container">
    <div class="cta-box">
      <h2>Rezerva animator in <span style="color:var(--primary)">${c.n}</span></h2>
      <p>Confirmare disponibilitate in 30 minute. Plata dupa petrecere. Garantie contractuala scrisa.</p>
      <div class="cta-btns">
        <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
        <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
      </div>
      <p style="margin-top:1.2rem;font-size:.88rem;color:var(--text-muted)">
        ← <a href="/animatori-petreceri-copii" style="color:var(--primary);font-weight:600">Pagina principala Animatori</a>
        &nbsp;|&nbsp;
        <a href="/arie-acoperire" style="color:var(--primary)">Toate zonele</a>
      </p>
    </div>
  </div>
</section>
</Layout>`;
}

let done = 0;
for (const [slug, c] of Object.entries(communes)) {
  const fp = path.join(pDir, `${slug}.astro`);
  if (!fs.existsSync(fp)) continue;
  fs.writeFileSync(fp, buildPage(slug, c), 'utf-8');
  done++;
}
console.log(`\nRescrise complet: ${done} pagini comune/sectoare\n`);

// Verificare rapida cuvinte
let minW = 9999, maxW = 0;
for (const [slug] of Object.entries(communes)) {
  const fp = path.join(pDir, `${slug}.astro`);
  if (!fs.existsSync(fp)) continue;
  let raw = fs.readFileSync(fp, 'utf-8');
  raw = raw.replace(/^---[\s\S]*?---/m,'').replace(/<style[\s\S]*?<\/style>/gi,' ').replace(/\{[^{}]*\}/g,' ').replace(/<[^>]+>/g,' ');
  const wc = raw.split(/\s+/).filter(w=>w.length>3).length;
  if(wc<minW) minW=wc;
  if(wc>maxW) maxW=wc;
}
console.log(`Cuvinte text vizibil: min=${minW} max=${maxW}`);
