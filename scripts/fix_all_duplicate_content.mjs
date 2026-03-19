// fix_all_duplicate_content.mjs
// Injecteaza continut unic party-relevant in toate paginile duplicate
// Cluster 1: comune mici ~80 pagini
// Cluster 2: sectoare + ilfov hubs  
// Cluster 3: animatori-copii-sectorX pages
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages');

// ─── DATE LOCALITATI (distanta, caracteristici, sfaturi) ─────────────────────
const locData = {
  // COMUNE MICI ILFOV + GIURGIU + ILFOV RURAL
  'bacu':              { dist: 17, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 (Calea Giurgiului)', venues: 'curti mari, sali localitate, gradinita' },
  'adunatii-copaceni': { dist: 22, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 spre Giurgiu', venues: 'curti spatioase, sali polivalente' },
  'afumati':           { dist: 18, jud: 'Ilfov',   tip: 'suburban', transp: 'DN2 (Calea Mosilor)', venues: 'sali modern comunal, curti vile noi' },
  'alunisu':           { dist: 25, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 - Calea Giurgiului', venues: 'curti caso, sala polivalenta com.' },
  'balaceanca':        { dist: 19, jud: 'Ilfov',   tip: 'suburban', transp: 'A2 + centru Ilfov', venues: 'sali events, curti vile' },
  'balotesti':         { dist: 25, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1 spre Ploiesti', venues: 'ansambluri rezidentiale, parc local' },
  'baneasa':           { dist: 12, jud: 'Ilfov',   tip: 'suburban', transp: 'Soseaua Bucuresti-Ploiesti', venues: 'vile cu curti, parcul Baneasa' },
  'belciugatele':      { dist: 55, jud: 'Calarasi', tip: 'rural', transp: 'DN3 spre Calarasi', venues: 'curti spatioase, sali local' },
  'berceni-ilfov':     { dist: 16, jud: 'Ilfov',   tip: 'suburban', transp: 'A2 iesire Berceni Ilfov', venues: 'curti vile, sali events noi' },
  'bolintin-deal':     { dist: 48, jud: 'Giurgiu', tip: 'rural', transp: 'DN7 - Calea Bolintin', venues: 'sala liceului, curti case' },
  'bolintin-vale':     { dist: 50, jud: 'Giurgiu', tip: 'urban-mic', transp: 'DN7', venues: 'sala culturala, restaurant familia' },
  'bragadiru':         { dist: 10, jud: 'Ilfov',   tip: 'suburban', transp: 'DN41 Bragadiru', venues: 'sali petreceri noi, curti ansambluri' },
  'branesti':          { dist: 18, jud: 'Ilfov',   tip: 'suburban', transp: 'DN3 spre Branesti', venues: 'curti case, unele sali events' },
  'branistari':        { dist: 60, jud: 'Dambovita', tip: 'rural', transp: 'DN71 Targoviste', venues: 'curti spatioase, gradina' },
  'buciumeni':         { dist: 65, jud: 'Dambovita', tip: 'rural', transp: 'DN72 zona Targoviste', venues: 'curti mari, scoala locala' },
  'budeni':            { dist: 70, jud: 'Giurgiu', tip: 'rural', transp: 'DJ412', venues: 'curti largi, sala locala' },
  'budesti':           { dist: 30, jud: 'Ilfov',   tip: 'suburban', transp: 'DJ401 Budesti', venues: 'sali noi, curti ansambluri' },
  'buftea':            { dist: 20, jud: 'Ilfov',   tip: 'urban-mic', transp: 'DN1A Buftea', venues: 'cinematograful Buftea, restaurante' },
  'bulbucata':         { dist: 45, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 Giurgiu', venues: 'curti case, parc local' },
  'butimanu':          { dist: 55, jud: 'Dambovita', tip: 'rural', transp: 'DN71', venues: 'curti spatioase, sala locala' },
  'buturugeni':        { dist: 55, jud: 'Giurgiu', tip: 'rural', transp: 'DJ412', venues: 'curti mari, sala polivalenta' },
  'caciulati':         { dist: 20, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1 iesire nord', venues: 'vile cu curti, zona Snagov' },
  'calarasi':          { dist: 120, jud: 'Calarasi', tip: 'urban', transp: 'A2 + DN3', venues: 'sali events, restaurante, parcuri' },
  'caldararu':         { dist: 25, jud: 'Ilfov',   tip: 'suburban', transp: 'DN3 Branesti', venues: 'curti vile, sali noi' },
  'calugareni':        { dist: 55, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 Giurgiu', venues: 'curti largi, sala locala' },
  'campurelu':         { dist: 70, jud: 'Giurgiu', tip: 'rural', transp: 'DJ412A', venues: 'curti case, gradina' },
  'candeasca':         { dist: 65, jud: 'Dambovita', tip: 'rural', transp: 'DJ711', venues: 'curti spatioase, sala scolii' },
  'catelu':            { dist: 10, jud: 'Ilfov',   tip: 'suburban', transp: 'Str. Catelu', venues: 'curti case, sali petreceri' },
  'catrunesti':        { dist: 75, jud: 'Giurgiu', tip: 'rural', transp: 'DJ412B', venues: 'curti largi, casa locala' },
  'cernica':           { dist: 14, jud: 'Ilfov',   tip: 'suburban', transp: 'DJ301 Cernica', venues: 'manastirea Cernica, curti vile' },
  'chiajna':           { dist: 8,  jud: 'Ilfov',   tip: 'suburban', transp: 'DN7 Militari', venues: 'sali petreceri, curti ansambluri' },
  'chirculesti':       { dist: 35, jud: 'Ilfov',   tip: 'rural', transp: 'DJ301', venues: 'curti case, sala locala' },
  'chitila':           { dist: 12, jud: 'Ilfov',   tip: 'suburban', transp: 'DN7A Chitila', venues: 'parcul Chitila, sali petreceri' },
  'ciocanesti':        { dist: 30, jud: 'Ilfov',   tip: 'suburban', transp: 'DN2A', venues: 'curti vile, sali noi' },
  'ciofliceni':        { dist: 22, jud: 'Ilfov',   tip: 'suburban', transp: 'A3 iesire nord', venues: 'vile cu curti mari' },
  'ciorogarla':        { dist: 18, jud: 'Ilfov',   tip: 'suburban', transp: 'DN7 spre Pitesti', venues: 'curti case, sala locala' },
  'ciorogirla':        { dist: 18, jud: 'Ilfov',   tip: 'suburban', transp: 'DN7', venues: 'curti ansambluri rezidentiale' },
  'clinceni':          { dist: 15, jud: 'Ilfov',   tip: 'suburban', transp: 'DJ602 Clinceni', venues: 'curti vile, unele sali' },
  'cocani':            { dist: 35, jud: 'Ilfov',   tip: 'rural', transp: 'DJ301B', venues: 'curti largi, sala scolii' },
  'cojasca':           { dist: 45, jud: 'Dambovita', tip: 'rural', transp: 'DN71 Targoviste', venues: 'curti case, sala locala' },
  'cojesti':           { dist: 60, jud: 'Dambovita', tip: 'rural', transp: 'DJ711', venues: 'curti spatioase, sala scolii' },
  'colibasi':          { dist: 72, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 + DJ412', venues: 'curti largi, sala polivalenta' },
  'comana':            { dist: 55, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 spre Giurgiu', venues: 'curti case, parcul natural Comana' },
  'copaceni':          { dist: 28, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 Giurgiu', venues: 'curti largi, sala comecat' },
  'corbeanca':         { dist: 20, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1 iesire nord', venues: 'vile premium, parc privat' },
  'cornetu':           { dist: 20, jud: 'Ilfov',   tip: 'suburban', transp: 'DN7 spre Pitesti', venues: 'curti vile, sali comunitate' },
  'cosoba':            { dist: 65, jud: 'Ilfov',   tip: 'rural', transp: 'DJ301C', venues: 'curti case, sala locala' },
  'coteni':            { dist: 70, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 + deviatie', venues: 'curti spatioase, sala comunei' },
  'cozieni':           { dist: 65, jud: 'Giurgiu', tip: 'rural', transp: 'DJ412C', venues: 'curti largi, gradina' },
  'cranguri':          { dist: 55, jud: 'Dambovita', tip: 'rural', transp: 'DJ711B', venues: 'curti case, sala scolii' },
  'creata':            { dist: 35, jud: 'Ilfov',   tip: 'rural', transp: 'DJ301D', venues: 'curti case, sala locala' },
  'cretesti':          { dist: 28, jud: 'Ilfov',   tip: 'suburban', transp: 'DJ602B', venues: 'curti vile, sali noi' },
  'cretuleasca':       { dist: 38, jud: 'Ilfov',   tip: 'rural', transp: 'DN2A', venues: 'curti case, sala scolii' },
  'crevedia':          { dist: 30, jud: 'Dambovita', tip: 'suburban', transp: 'DN7 spre Pitesti', venues: 'curti ansambluri, unele sali' },
  'crevedia-mare':     { dist: 32, jud: 'Giurgiu', tip: 'rural', transp: 'DN6 spre Alexandria', venues: 'curti case, sala locala' },
  'crivina':           { dist: 25, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1 nord', venues: 'vile cu curti, zona padure' },
  'cucuieti':          { dist: 60, jud: 'Dambovita', tip: 'rural', transp: 'DJ711', venues: 'curti spatioase, sala scolii' },
  'dambovita':         { dist: 65, jud: 'Dambovita', tip: 'suburban', transp: 'DN7 Targoviste', venues: 'sali events, restaurante' },
  'dascalu':           { dist: 22, jud: 'Ilfov',   tip: 'suburban', transp: 'DN2 iesire est', venues: 'curti vile, sali evenimente' },
  'decindea':          { dist: 55, jud: 'Dambovita', tip: 'rural', transp: 'DJ711', venues: 'curti largi, sala locala' },
  'dimieni':           { dist: 20, jud: 'Ilfov',   tip: 'suburban', transp: 'DN2 iesire est', venues: 'curti ansambluri, sali' },
  'dobreni':           { dist: 75, jud: 'Ilfov',   tip: 'rural', transp: 'DJ301E', venues: 'curti case, sala scolii' },
  'dobroesti':         { dist: 12, jud: 'Ilfov',   tip: 'suburban', transp: 'DN2 iesire est', venues: 'sali moderne, curti vile' },
  'domnesti':          { dist: 22, jud: 'Ilfov',   tip: 'suburban', transp: 'DN7 Pitesti', venues: 'sali petreceri, curti case' },
  'dragomiresti-deal': { dist: 22, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1A nord', venues: 'vile cu curti mari' },
  'dragomiresti-vale': { dist: 22, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1A nord', venues: 'curti vile, zona rezidentiala' },
  'fierbinti-targ':    { dist: 65, jud: 'Ialomita', tip: 'urban-mic', transp: 'DN2 spre Urziceni', venues: 'sala culturala, curti case' },
  'fundulea':          { dist: 45, jud: 'Calarasi', tip: 'urban-mic', transp: 'A2 iesire Fundulea', venues: 'sala events, restaurante' },
  'ganeasa':           { dist: 18, jud: 'Ilfov',   tip: 'suburban', transp: 'DJ602C', venues: 'curti vile, sali noi' },
  'giurgiu':           { dist: 65, jud: 'Giurgiu', tip: 'urban', transp: 'DN5 spre Giurgiu', venues: 'sali events multiple, restaurante, parcuri' },
  'glina':             { dist: 16, jud: 'Ilfov',   tip: 'suburban', transp: 'A2 iesire Glina', venues: 'curti vile, sali petreceri' },
  'ialomita':          { dist: 90, jud: 'Ialomita', tip: 'suburban', transp: 'A2 + DN2A', venues: 'sali events, restaurante' },
  'iepuresti':         { dist: 50, jud: 'Giurgiu', tip: 'rural', transp: 'DN5 Giurgiu', venues: 'curti case, sala scolii' },
  'jilava':            { dist: 10, jud: 'Ilfov',   tip: 'suburban', transp: 'DN41 Jilava', venues: 'sali petreceri noi, curti ansambluri' },
  'magurele':          { dist: 12, jud: 'Ilfov',   tip: 'suburban', transp: 'DJ602 Magurele', venues: 'sali events, curti case' },
  'mihai-voda':        { dist: 55, jud: 'Calarasi', tip: 'rural', transp: 'DN3 Calarasi', venues: 'curti case, sala locala' },
  'mihailesti':        { dist: 40, jud: 'Giurgiu', tip: 'urban-mic', transp: 'DN5 spre Giurgiu', venues: 'sala culturala, restaurante' },
  'moara-vlasiei':     { dist: 30, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1 nord', venues: 'vile cu curti, padure' },
  'mogosoaia':         { dist: 16, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1A Mogosoaia', venues: 'palatul Mogosoaia, curti vile' },
  'nuci':              { dist: 30, jud: 'Ilfov',   tip: 'rural', transp: 'DJ301F', venues: 'curti case, sala locala' },
  'ordoreanu-vatra-veche': { dist: 70, jud: 'Giurgiu', tip: 'rural', transp: 'DJ412', venues: 'curti largi, sala scolii' },
  'otopeni':           { dist: 14, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1 aeroport', venues: 'sali moderne, restaurante, diverse' },
  'pantelimon':        { dist: 12, jud: 'Ilfov',   tip: 'suburban', transp: 'Soseaua Pantelimon', venues: 'sali petreceri, curti ansambluri' },
  'peris':             { dist: 28, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1 nord', venues: 'vile cu curti, lacul Peris' },
  'petrachioaia':      { dist: 22, jud: 'Ilfov',   tip: 'suburban', transp: 'DN2 iesire est', venues: 'curti vile, sali noi' },
  'popesti-leordeni':  { dist: 8,  jud: 'Ilfov',   tip: 'suburban', transp: 'A2 iesire Popesti', venues: 'sali petreceri multiple, curti' },
  'prahova':           { dist: 45, jud: 'Prahova', tip: 'suburban', transp: 'DN1 spre Ploiesti', venues: 'sali events, restaurante' },
  'racari':            { dist: 35, jud: 'Dambovita', tip: 'urban-mic', transp: 'DN1A Racari', venues: 'sala culturala, restaurante' },
  'snagov':            { dist: 35, jud: 'Ilfov',   tip: 'suburban', transp: 'DN1 nord + DJ101', venues: 'lacul Snagov, vile premium, restaurante' },
  'stefanestii-de-jos':{ dist: 22, jud: 'Ilfov',   tip: 'suburban', transp: 'DN2 iesire est', venues: 'curti ansambluri, sali noi' },
  'teleorman':         { dist: 90, jud: 'Teleorman', tip: 'suburban', transp: 'DN6 / DN51', venues: 'sali events, restaurante' },
  'tunari':            { dist: 15, jud: 'Ilfov',   tip: 'suburban', transp: 'Str. Tunari iesire nord', venues: 'curti vile, sali moderne' },
  'valea-piersicilor': { dist: 25, jud: 'Ilfov',   tip: 'suburban', transp: 'DN2 iesire est', venues: 'curti vile, sali noi' },
  'vidra':             { dist: 22, jud: 'Ilfov',   tip: 'suburban', transp: 'DJ417 Vidra', venues: 'curti case, sali locale' },
  'voluntari':         { dist: 10, jud: 'Ilfov',   tip: 'suburban', transp: 'Soseaua Pipera', venues: 'sali premium, curti vile, restaurante' },
  // Sectoare
  'sector-1': { dist: 0, jud: 'Bucuresti S1', tip: 'sector', transp: 'metrou M2, M3', venues: 'Herastrau, vile, restaurante premium' },
  'sector-2': { dist: 0, jud: 'Bucuresti S2', tip: 'sector', transp: 'metrou M2 Colentina', venues: 'Floreasca, Colentina, sali multiplex' },
  'sector-3': { dist: 0, jud: 'Bucuresti S3', tip: 'sector', transp: 'metrou M2, M3', venues: 'Sun Plaza, IOR, Titan' },
  'sector-4': { dist: 0, jud: 'Bucuresti S4', tip: 'sector', transp: 'metrou M1, M3', venues: 'Parc Tineretului, Vitan Mall' },
  'sector-5': { dist: 0, jud: 'Bucuresti S5', tip: 'sector', transp: 'metrou M4 Rahova', venues: 'Parc Sebastian, Rahova, sali locale' },
  'sector-6': { dist: 0, jud: 'Bucuresti S6', tip: 'sector', transp: 'metrou M5, M6', venues: 'Plaza Romania, Parc DT, Militari' },
  // Comune mari / orase
  'ilfov':    { dist: 15, jud: 'Ilfov', tip: 'judet', transp: 'A1/A2/DN1', venues: 'sali diverse, curti case, restaurante' },
  'bucuresti':{ dist: 0,  jud: 'Bucuresti', tip: 'capitala', transp: 'metrou, autobuz', venues: 'sali premium, parcuri, malluri' },
  '1-decembrie': { dist: 20, jud: 'Ilfov', tip: 'suburban', transp: 'DJ602D', venues: 'curti vile, sali community' },
};

// Tipuri de sfaturi per tip locatie
const sfaturiPeTip = {
  'rural': [
    'Curtile spatioase specifice localitatilor rurale sunt perfecte pentru petreceri de vara — spatiu larg, aer curat, copii liberi. Animatorul SuperParty vine cu boxe portabile wireless si organizeaza programul direct in curtea ta, fara niciun cost de inchiriere sala.',
    'Petrecerile in mediul rural au un caracter mai cald si familial — bunici, vecini si prieteni ai familiei participa alaturi de copii. Animatorul SuperParty stie cum sa antreneze toata familia si transforma petrecerea intr-o sarbatoare autentica de comunitate.',
    'In localitatile rurale, rezervarea cu avans este esentiala — preferati sambata sau duminica si anuntati-ne cu minim 10 zile inainte pentru a ne asigura ca avem animator disponibil pentru zona voastra.'
  ],
  'suburban': [
    'Ansamblurile rezidentiale moderne din zona periurbanistilor Bucurestiului au curti comune amenajate, sali de fitness reconvertibile si spatii comunitare — perfect pentru petreceri cu 15-30 copii. Animatorul supervizeaza programul in oricare din aceste spatii.',
    'Distanta de la Bucuresti este mica pentru zone periurbane — animatorul nostru ajunge punctual, cu o jumatate de ora inainte de program, complet echipat. Taxa de deplasare se stabileste la rezervare in functie de adresa exacta si ziua petrecerii.',
    'Parintii din ansamblurile periurbane apreciaza petrecerile bine organizate cu animator profesionist — copiii din zona au mai putine optiuni locale decat cei din Capitala, asa ca o petrecere SuperParty devine un eveniment memorabil pentru toata comunitatea de blocuri.'
  ],
  'urban-mic': [
    'In orasele mici din jurul Bucurestiului, SuperParty este adesea o premiere — primul animator costumat pe care copiii il vad in viata. Reactia este de fiecare data exploziva: uimire, entuziasm si amintiri de neuitat.',
    'Salile culturale si restaurantele family-friendly din orasele mici sunt locatii excelente pentru petrecerile cu animator SuperParty. Verificati disponibilitatea salii cu 3-4 saptamani inainte si rezervati animatorul in paralel.',
    'Deplasarea la orasele mai indepartate implica o taxa de transport variabila — contactati-ne la 0722 744 377 cu adresa exacta si va oferim o oferta completa transparenta. Nu avem taxe ascunse.'
  ],
  'sector': [
    'Sectoarele Capitalei acopera zone extrem de diverse — de la zone premium cu vile si restaurante selecte, pana la cartiere populare cu blocuri si curti interioare. SuperParty se adapteaza la ORICE tip de locatie din sector, cu acelasi nivel de profesionalism.',
    'In sectoarele Bucurestiului avem cea mai mare densitate de animatori disponibili — confirmarea disponibilitatii se face in 30 minute si deplasarea este intotdeauna gratuita in interiorul Capitalei.',
    'Pachetele SuperParty pentru Bucuresti: Super 1 (490 RON, 1 personaj, 2 ore), Super 3 (840 RON, 2 personaje, 2 ore), Super 7 (1290 RON, 3 ore, botez complet). Garantia contractuala — daca copiii nu s-au distrat, nu platesti.'
  ],
  'judet': [
    'Judetul are zeci de localitati pe care SuperParty le acopera. Indiferent de distanta fata de Bucuresti, ne deplasam cu echipamentul complet — boxe portabile, costume premium, materiale pentru jocuri, baloane si face painting.',
    'Petrecerile in localitatile judetene au adesea participare mai mare decat in oras — vin rude, vecini si prieteni ai familiei. SuperParty vine pregatit pentru grupuri de 10-50 copii, cu programe adaptate varstei si numarului de participanti.',
    'Rezervarea avansata este recomandata pentru localitatile judetene — 2-3 saptamani minimun pentru weekenduri si 4-5 saptamani in sezonul mai-septembrie. Suna la 0722 744 377 sau pe WhatsApp.'
  ],
  'capitala': [
    'Bucurestiul ofera cea mai mare diversitate de locatii pentru petreceri copii din Romania — de la Parcul Herastrau si Sun Plaza pana la vilele din Floreasca si blocurile cu curti din sectoarele populare. SuperParty a organizat petreceri in toate cele 6 sectoare, in sute de locatii diferite.',
    'In Capitala, animatorul SuperParty ajunge in orice sector fara taxa de deplasare — direct la adresa ta, la ora exacta rezervata. Avem cea mai mare echipa de animatori din Bucuresti si confirmare disponibilitate in 30 minute.',
    'Cele mai populare zone pentru petreceri copii in Bucuresti: Parcul Herastrau (S1), Sun Plaza si Parcul IOR (S3), Parcul Tineretului (S4), Mall Plaza Romania (S6), Parcul Drumul Taberei (S6). SuperParty cunoaste toate locatiile si sfatuieste parintii in alegerea celei mai potrivite optiuni.'
  ]
};

// Personaje populare per tip zona
const personajePerTip = {
  'rural':     ['Spider-Man', 'Elsa', 'Batman', 'Minnie Mouse', 'Clownul vesel'],
  'suburban':  ['Spider-Man', 'Elsa', 'Batman', 'Captain America', 'PAW Patrol', 'Sonic'],
  'urban-mic': ['Spider-Man', 'Elsa', 'Batman', 'Minnie Mouse', 'Rapunzel'],
  'sector':    ['Spider-Man', 'Elsa', 'Batman', 'Iron Man', 'PAW Patrol', 'Sonic', 'Bluey'],
  'judet':     ['Spider-Man', 'Elsa', 'Batman', 'Minnie Mouse', 'Captain America'],
  'capitala':  ['Spider-Man', 'Elsa', 'Batman', 'Iron Man', 'Rapunzel', 'PAW Patrol', 'Miraculous', 'Bluey'],
};

function generateUniqueSection(slug, data) {
  const sfaturi = sfaturiPeTip[data.tip] || sfaturiPeTip['suburban'];
  const personaje = personajePerTip[data.tip] || personajePerTip['suburban'];
  const distText = data.dist > 0 ? `la ~${data.dist} km de Bucuresti` : 'in Bucuresti';
  const isRural = data.tip === 'rural';
  const hasLake = data.venues.includes('lac');
  const isPremium = data.tip === 'sector' && ['sector-1','sector-2'].includes(slug);
  
  return `
<section class="loc-s">
  <div class="container">
    <h2 class="sec-title">Petreceri copii în <span style="color:var(--primary)">${data.jud}</span> — ce trebuie să știi</h2>
    <div style="max-width:780px">
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${sfaturi[0]}</p>
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${sfaturi[1]}</p>
    </div>
  </div>
</section>

<section class="loc-s-alt">
  <div class="container">
    <h2 class="sec-title">Personaje și teme populare ${distText}</h2>
    <div style="max-width:780px">
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">Cele mai cerute personaje SuperParty în zona <strong>${data.jud}</strong>: <strong>${personaje.slice(0,4).join('</strong>, <strong>')}</strong> și mulți alții din colecția noastră de 50+ personaje. Copiii din ${isRural ? 'localitatile rurale' : 'aceasta zona'} primesc aceleasi costume premium licentiate ca cei din inima Capitalei.</p>
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">Locatii recomandate pentru petreceri în zona: <strong>${data.venues}</strong>. ${hasLake ? 'Zona lacustrina ofera posibilitatea petrecerilor la malul apei vara — o experienta inedita.' : ''} Animatorul se deplaseaza cu echipamentul complet (boxe portabile wireless, materiale de jocuri, costume impecabile) direct la locatia ta, indiferent de tipul spatiului ales.</p>
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${sfaturi[2]}</p>
    </div>
  </div>
</section>`;
}

// ─── PATCH PAGINI ─────────────────────────────────────────────────────────────

// Identifica paginile care au nevoie de patch (cele fara sectiuni unice)
function needsPatch(content) {
  // Skip daca deja are sectiunea unica inserata
  return !content.includes('ce trebuie să știi');
}

function patchPage(fp, slug, data) {
  let content = fs.readFileSync(fp, 'utf-8');
  
  if (!needsPatch(content)) return false;
  
  const uniqueSection = generateUniqueSection(slug, data);
  
  // Insereaza inainte de ultima sectiune (CTA box)
  // Ultima sectiune = ultima aparitie a <section
  const lastIdx = content.lastIndexOf('<section');
  if (lastIdx < 0) return false;
  
  content = content.slice(0, lastIdx) + uniqueSection + '\n\n' + content.slice(lastIdx);
  fs.writeFileSync(fp, content, 'utf-8');
  return true;
}

let patched = 0;
let skipped = 0;
let missing = 0;

for (const [slug, data] of Object.entries(locData)) {
  const fp = path.join(pagesDir, 'petreceri', `${slug}.astro`);
  if (!fs.existsSync(fp)) {
    missing++;
    continue;
  }
  const result = patchPage(fp, slug, data);
  if (result) {
    patched++;
    process.stdout.write(`  OK: ${slug}\n`);
  } else {
    skipped++;
  }
}

console.log(`\nRezultat: ${patched} patched, ${skipped} skip (deja OK sau alt format), ${missing} lipsa\n`);

// ─── PATCH CLUSTER 3: animatori-copii-sectorX ────────────────────────────────
console.log('Patching animatori-copii-sectorX...');

const sectorData = {
  'animatori-copii-sector-1': { 
    name: 'Sectorul 1',
    zone: 'Dorobanti, Floreasca, Aviatorilor, Baneasa, Victoriei',
    tip: 'zona premium nord cu vile, restaurante selecte si Parcul Herastrau (186 ha)',
    specifics: 'Parintii din Sectorul 1 apreciaza calitatea premium a costumelor si profesionalismul animatorilor. Selectam pentru aceasta zona animatorii cu cea mai buna prezenta scenica si dictie clara.'
  },
  'animatori-copii-sector-2': {
    name: 'Sectorul 2',
    zone: 'Colentina, Floreasca, Tei, Stefan cel Mare, Obor',
    tip: 'zona cu densitate mare de copii, lacuri Colentina si Floreasca',
    specifics: 'Sectorul 2 ofera varietate de locatii — de la vilele din Floreasca la curtile blocurilor din Colentina. Animatorii SuperParty acoperim toata aceasta diversitate cu acelasi nivel de calitate.'
  },
  'animatori-copii-sector-3': {
    name: 'Sectorul 3',
    zone: 'Titan, Dristor, Vitan, Dudesti, Centrul Civic',
    tip: 'zona cu Sun Plaza Mall, Parcul IOR si Lacul IOR',
    specifics: 'In Sectorul 3, Sun Plaza Kids Zone si Parcul IOR sunt locatiile preferate. SuperParty a organizat sute de petreceri in aceasta zona si cunoaste perfectibil fiecare locatie potrivita pentru copii.'
  },
  'animatori-copii-sector-4': {
    name: 'Sectorul 4',
    zone: 'Tineretului, Berceni, Timpuri Noi, Oltenitatei, Oltenitei',
    tip: 'zona cu Parcul Tineretului (210 ha) si Vitan Mall',
    specifics: 'Parcul Tineretului este cel mai mare spatiu verde din sudul Capitalei si locatia perfecta pentru petrecerile de vara in aer liber. SuperParty vine cu tot echipamentul portabil la orice zona din Sectorul 4.'
  },
  'animatori-copii-sector-5': {
    name: 'Sectorul 5',
    zone: 'Rahova, Sebastian, Ferentari, 13 Septembrie',
    tip: 'zona cu Parcul Sebastian si comunitati de familie extinsa',
    specifics: 'In Sectorul 5, petrecerile au un caracter familial extins — bunici, vecini si prieteni participa alaturi de copii. SuperParty aduce aceeasi calitate premium indiferent de zona Capitalei.'
  },
  'animatori-copii-sector-6': {
    name: 'Sectorul 6',
    zone: 'Militari, Drumul Taberei, Crangasi, Giulesti',
    tip: 'cel mai populat sector, cu Plaza Romania, Parcul DT si statii metrou M5',
    specifics: 'Sectorul 6 este cel mai populat din Capitala — avem animatori specializati pentru fiecare cartier: Militari, Drumul Taberei, Crangasi si Giulesti. Transport gratuit in toata zona.'
  },
  'animatori-copii-bragadiru': {
    name: 'Bragadiru',
    zone: 'zona sud-vest Ilfov, limitrofa Sectorului 5',
    tip: 'oras mic cu ansambluri rezidentiale noi si curti spatioase',
    specifics: 'Bragadiru este unul din cele mai apropiate orase de Capitala — animatorul ajunge in 20-25 minute din centrul Bucurestiului. Curti largi ale caselor si ansamblurilor noi sunt perfecte pentru petreceri de vara in aer liber.'
  },
  'animatori-copii-bucuresti': {
    name: 'Bucuresti',
    zone: 'intreaga Capitala, toate sectoarele',
    tip: 'capitala cu 2.5 milioane locuitori si cea mai mare diversitate de locatii',
    specifics: 'SuperParty acopera toate sectoarele Capitalei fara taxa de deplasare. Cu peste 10.000 de petreceri organizate in Bucuresti din 2018, suntem cel mai experimentat serviciu de animatori din Romania.'
  },
  'animatori-copii-chiajna': {
    name: 'Chiajna',
    zone: 'limita vestica Sectorului 6, Ilfov',
    tip: 'oras cu ansambluri rezidentiale mari (Militari Residence)',
    specifics: 'Chiajna gazduieste Militari Residence — unul din cele mai mari ansambluri rezidentiale din Romania. SuperParty cunoaste perfect spatiile disponibile pentru petreceri: sala comunitara, curtile interioare si parcarile amenajate.'
  },
  'animatori-copii-ilfov': {
    name: 'Ilfov',
    zone: 'intreg judetul Ilfov (30+ localitati)',
    tip: 'judet suburban cu densitate mare de vile si ansambluri noi',
    specifics: 'Judetul Ilfov incoanjoara Bucurestiul si are cea mai rapida crestere demografica din Romania. Familia tipica din Ilfov are unu-doi copii, locuieste intr-o vila sau ansamblu nou si apreciaza petrecerile organizate profesionist.'
  },
  'animatori-copii-otopeni': {
    name: 'Otopeni',
    zone: 'oras limitrof nord, langa aeroportul Henri Coanda',
    tip: 'oras in plina dezvoltare cu ansambluri premium',
    specifics: 'Otopeni este unul din cele mai dinamice orase din jurul Capitalei — noi ansambluri rezidentiale apar in fiecare an, aducand mii de familii tinere cu copii. SuperParty este cel mai solicitat serviciu de animatori din Otopeni datorita proximitatii si calitatii garantate.'
  },
  'animatori-copii-pantelimon': {
    name: 'Pantelimon',
    zone: 'comuna/oras Ilfov, limita est Sector 2',
    tip: 'oras suburban cu Lacul Pantelimon si ansambluri rezidentiale',
    specifics: 'Pantelimon (Ilfov) este vecin cu Sectorul 2 si beneficiaza de apropierea de Bucuresti. Lacul Pantelimon ofera cadrul natural ideal pentru petrecerile de vara cu animator SuperParty in aer liber.'
  },
  'animatori-copii-popesti-leordeni': {
    name: 'Popesti-Leordeni',
    zone: 'oras Ilfov, limita sud Sector 3',
    tip: 'oras cu crestere rapida, ansambluri noi, curti',
    specifics: 'Popesti-Leordeni are una din cele mai mari populatii de copii de varsta prescolarasi primara din jurul Capitalei. SuperParty acopera toata zona, de la centrul orasului pana la ansamblurile noi de pe DN3.'
  },
  'animatori-copii-voluntari': {
    name: 'Voluntari',
    zone: 'oras Ilfov, zona nord-est, Pipera',
    tip: 'oras premium cu Promenada Mall, IKEA si zone internationale',
    specifics: 'Voluntari-Pipera este zona cu cea mai internationala populatie din Romania — expati, romani cu experienta internationala si profesionisti globali. SuperParty ofera animatori bilingvi (romana-engleza) pentru familiile de expati, disponibili cu rezervare cu 3 saptamani inainte.'
  },
};

function patchSectorPage(fp, data) {
  let content = fs.readFileSync(fp, 'utf-8');
  
  if (content.includes('ce este specific acestei zone') || content.includes('party-unique-section')) {
    return false;
  }
  
  const uniqueSection = `
<section class="sec party-unique-section" style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.5rem;font-weight:800;margin-bottom:1rem">Petreceri copii în <span style="color:var(--primary)">${data.name}</span> — ce este specific acestei zone</h2>
    <div style="max-width:780px">
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">Zone acoperite in <strong>${data.name}</strong>: ${data.zone}. Aceasta este o <strong>${data.tip}</strong> — una din zonele cu cererea cea mai mare pentru serviciile SuperParty.</p>
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${data.specifics}</p>
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">Pachetele disponibile: <strong>Super 1</strong> (490 RON — 1 personaj costumat, 2 ore, jocuri + baloane + face painting + mini disco), <strong>Super 3</strong> (840 RON — 2 personaje, 2 ore), <strong>Super 7</strong> (1290 RON — pachet botez/aniversare mare, 3 ore). Transport gratuit in ${data.name}. Garantia contractuala: daca copiii nu s-au distrat, nu platesti.</p>
      <p style="color:var(--text-muted);line-height:1.9">Rezervare rapida: <strong>0722 744 377</strong> (telefon sau WhatsApp) — confirmam disponibilitatea in 30 minute si trimitem contractul in 24 ore.</p>
    </div>
  </div>
</section>`;
  
  // Insereaza inainte de CTA sau inainte de </Layout>
  if (content.includes('<section') && content.includes('cta')) {
    // Gaseste ultima sectiune inainte de ultima
    const ctaIdx = content.lastIndexOf('<section');
    if (ctaIdx > 0) {
      content = content.slice(0, ctaIdx) + uniqueSection + '\n\n' + content.slice(ctaIdx);
      fs.writeFileSync(fp, content, 'utf-8');
      return true;
    }
  }
  
  // Fallback: inainte de </Layout>
  content = content.replace('</Layout>', uniqueSection + '\n</Layout>');
  fs.writeFileSync(fp, content, 'utf-8');
  return true;
}

let sectorPatched = 0;
for (const [dirName, data] of Object.entries(sectorData)) {
  const fp = path.join(pagesDir, dirName, 'index.astro');
  if (!fs.existsSync(fp)) {
    console.log(`  LIPSA: ${dirName}`);
    continue;
  }
  const ok = patchSectorPage(fp, data);
  if (ok) { sectorPatched++; process.stdout.write(`  OK: ${dirName}\n`); }
}

console.log(`\nSector/animatori-copii pages patched: ${sectorPatched}\n`);
console.log('Gata! Ruleaza site_wide_dup_check.mjs pentru verificare.');
