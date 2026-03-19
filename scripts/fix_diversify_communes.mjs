// fix_diversify_communes.mjs
// Inlocuieste sectiunile unice cu text VARIAT per pagina (nu acelasi per tip)
// Foloseste hash din slug pentru a alege variante diferite
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages');

// Hash simplu din slug pt selectie varianta
function hashSlug(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

function pick(arr, idx) { return arr[idx % arr.length]; }

// ─── BAZA DE DATE LOCALITATI ──────────────────────────────────────────────────
const locData = {
  'bacu':              { dist: 17, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 (Calea Giurgiului)', venues: ['curtea casei', 'sala de sport a scolii', 'gradina spatioasa'], pop: 800 },
  'adunatii-copaceni': { dist: 22, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 spre Giurgiu', venues: ['curte larga', 'sala polivalenta', 'parcul central'], pop: 1200 },
  'afumati':           { dist: 18, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN2 (Calea Mosilor)', venues: ['sala events recenta', 'curtile ansamblului Afumati', 'parcul local'], pop: 7000 },
  'alunisu':           { dist: 25, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 Calea Giurgiului', venues: ['gradina casei', 'sala scolii', 'spatiu deschis'], pop: 600 },
  'balaceanca':        { dist: 19, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'A2 Centura Sud', venues: ['curti vile Balaceanca', 'sala community Balaceanca', 'parcul local'], pop: 5000 },
  'balotesti':         { dist: 25, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1 spre Ploiesti', venues: ['ansambluri rezidentiale Balotesti', 'parcul local', 'sali events noi'], pop: 9000 },
  'baneasa':           { dist: 12, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'Soseaua Bucuresti-Ploiesti (DN1)', venues: ['vile cu curti la Baneasa', 'Padurea Baneasa', 'restaurante premium Baneasa'], pop: 5500 },
  'belciugatele':      { dist: 55, jud: 'Calarasi', tip: 'rural', county: 'Calarasi', road: 'DN3 spre Calarasi', venues: ['curti spatioase', 'sala locala Belciugatele', 'gradina casei'], pop: 3000 },
  'berceni-ilfov':     { dist: 16, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'A2 iesire Berceni', venues: ['curti vile Berceni Ilfov', 'sali events noi', 'parcul local'], pop: 8000 },
  'bolintin-deal':     { dist: 48, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN7 Calea Bolintin', venues: ['sala liceului', 'curti case', 'spatiu deschis'], pop: 2000 },
  'bolintin-vale':     { dist: 50, jud: 'Giurgiu', tip: 'urban-mic', county: 'Giurgiu', road: 'DN7', venues: ['sala culturala Bolintin', 'restaurant familia', 'piata centrala'], pop: 8000 },
  'bragadiru':         { dist: 10, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN41 Bragadiru', venues: ['sali petreceri noi Bragadiru', 'curti ansambluri', 'Parcul Bragadiru'], pop: 25000 },
  'branesti':          { dist: 18, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN3 spre Branesti', venues: ['curti case Branesti', 'sala events Branesti', 'Lacul Branesti'], pop: 6000 },
  'branistari':        { dist: 60, jud: 'Dambovita', tip: 'rural', county: 'Dambovita', road: 'DN71 Targoviste', venues: ['curti spatioase', 'gradina casei', 'sala scolii'], pop: 500 },
  'buciumeni':         { dist: 65, jud: 'Dambovita', tip: 'rural', county: 'Dambovita', road: 'DN72 zona Targoviste', venues: ['curti mari', 'scoala locala', 'spatiu verde comunal'], pop: 1000 },
  'budeni':            { dist: 70, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DJ412', venues: ['curti largi', 'sala locala'], pop: 700 },
  'budesti':           { dist: 30, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DJ401 Budesti', venues: ['sali noi Budesti', 'curti ansambluri', 'parcul orasului'], pop: 5500 },
  'buftea':            { dist: 20, jud: 'Ilfov',   tip: 'urban-mic', county: 'Ilfov', road: 'DN1A Buftea', venues: ['Studios Buftea', 'restaurante Buftea', 'Lacul Buftea'], pop: 20000 },
  'bulbucata':         { dist: 45, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 Giurgiu', venues: ['curti case', 'parc local', 'sala locala'], pop: 1100 },
  'butimanu':          { dist: 55, jud: 'Dambovita', tip: 'rural', county: 'Dambovita', road: 'DN71', venues: ['curti spatioase', 'sala locala', 'gradina'], pop: 800 },
  'buturugeni':        { dist: 55, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DJ412', venues: ['curti mari', 'sala polivalenta', 'spatiu verde'], pop: 900 },
  'caciulati':         { dist: 20, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1 nord', venues: ['vile cu curti Caciulati', 'zona Snagov', 'padure Caciulati'], pop: 3000 },
  'calarasi':          { dist: 120, jud: 'Calarasi', tip: 'urban', county: 'Calarasi', road: 'A2 + DN3', venues: ['sali events Calarasi', 'restaurante Calarasi', 'Parcul Dunarii'], pop: 60000 },
  'caldararu':         { dist: 25, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN3 spre Branesti', venues: ['curti vile', 'sali noi Caldararu', 'spatiu comunitar'], pop: 4000 },
  'calugareni':        { dist: 55, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 Giurgiu', venues: ['curti largi', 'sala locala', 'camp deschis'], pop: 1300 },
  'campurelu':         { dist: 70, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DJ412A', venues: ['curti case', 'gradina', 'sala scolii'], pop: 600 },
  'candeasca':         { dist: 65, jud: 'Dambovita', tip: 'rural', county: 'Dambovita', road: 'DJ711', venues: ['curti spatioase', 'sala scolii', 'spatiu deschis'], pop: 700 },
  'catelu':            { dist: 10, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'Str. Catelu - Sector 3', venues: ['curti case Catelu', 'sali petreceri', 'spatiu semi-urban'], pop: 6000 },
  'catrunesti':        { dist: 75, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DJ412B', venues: ['curti largi', 'casa locala', 'gradina'], pop: 500 },
  'cernica':           { dist: 14, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DJ301 Cernica', venues: ['Manastirea Cernica', 'curti vile Cernica', 'lacul Cernica'], pop: 8000 },
  'chiajna':           { dist: 8,  jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN7 Militari', venues: ['Militari Residence Chiajna', 'sali petreceri', 'curti ansambluri'], pop: 30000 },
  'chirculesti':       { dist: 35, jud: 'Ilfov',   tip: 'rural', county: 'Ilfov', road: 'DJ301', venues: ['curti case', 'sala locala', 'spatiu deschis'], pop: 1500 },
  'chitila':           { dist: 12, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN7A Chitila', venues: ['Parcul Chitila', 'sali petreceri Chitila', 'curti case noi'], pop: 12000 },
  'ciocanesti':        { dist: 30, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN2A', venues: ['curti vile Ciocanesti', 'sali noi', 'zona rezidentiala'], pop: 5000 },
  'ciofliceni':        { dist: 22, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'A3 iesire nord', venues: ['vile cu curti mari Ciofliceni', 'zona premium nord', 'lacul Snagov aproape'], pop: 4000 },
  'ciorogarla':        { dist: 18, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN7 spre Pitesti', venues: ['curti case Ciorogarla', 'sala locala', 'zona verde'], pop: 7000 },
  'ciorogirla':        { dist: 18, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN7', venues: ['curti ansambluri Ciorogirla', 'sali noi', 'zona rezidentiala'], pop: 6000 },
  'clinceni':          { dist: 15, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DJ602 Clinceni', venues: ['curti vile Clinceni', 'sala locala', 'zona verde'], pop: 5000 },
  'cocani':            { dist: 35, jud: 'Ilfov',   tip: 'rural', county: 'Ilfov', road: 'DJ301B', venues: ['curti largi', 'sala scolii', 'spatiu rural'], pop: 1800 },
  'cojasca':           { dist: 45, jud: 'Dambovita', tip: 'rural', county: 'Dambovita', road: 'DN71 Targoviste', venues: ['curti case', 'sala locala Cojasca', 'gradina'], pop: 2000 },
  'cojesti':           { dist: 60, jud: 'Dambovita', tip: 'rural', county: 'Dambovita', road: 'DJ711', venues: ['curti spatioase', 'sala scolii', 'spatiu deschis'], pop: 700 },
  'colibasi':          { dist: 72, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 + DJ412', venues: ['curti largi', 'sala polivalenta Colibasi', 'spatiu deschis'], pop: 1500 },
  'comana':            { dist: 55, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 spre Giurgiu', venues: ['curti case', 'Parcul Natural Comana', 'sala locala'], pop: 3000 },
  'copaceni':          { dist: 28, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 Giurgiu', venues: ['curti largi', 'sala comecat Copaceni', 'zona verde'], pop: 1200 },
  'corbeanca':         { dist: 20, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1 iesire nord', venues: ['vile premium Corbeanca', 'parc privat', 'zona verde exclusivista'], pop: 5000 },
  'cornetu':           { dist: 20, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN7 spre Pitesti', venues: ['curti vile Cornetu', 'sali comunitate', 'zona verde Cornetu'], pop: 8000 },
  'cosoba':            { dist: 65, jud: 'Ilfov',   tip: 'rural', county: 'Ilfov', road: 'DJ301C', venues: ['curti case', 'sala locala', 'spatiu rural'], pop: 1000 },
  'coteni':            { dist: 70, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 + deviatie', venues: ['curti spatioase', 'sala comunei Coteni', 'gradina'], pop: 800 },
  'cozieni':           { dist: 65, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DJ412C', venues: ['curti largi', 'gradina casei', 'sala locala'], pop: 900 },
  'cranguri':          { dist: 55, jud: 'Dambovita', tip: 'rural', county: 'Dambovita', road: 'DJ711B', venues: ['curti case', 'sala scolii', 'spatiu deschis'], pop: 700 },
  'creata':            { dist: 35, jud: 'Ilfov',   tip: 'rural', county: 'Ilfov', road: 'DJ301D', venues: ['curti case', 'sala locala Creata', 'zona verde'], pop: 1200 },
  'cretesti':          { dist: 28, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DJ602B', venues: ['curti vile Cretesti', 'sali noi', 'zona rezidentiala'], pop: 4000 },
  'cretuleasca':       { dist: 38, jud: 'Ilfov',   tip: 'rural', county: 'Ilfov', road: 'DN2A', venues: ['curti case', 'sala scolii Cretuleasca', 'spatiu verde'], pop: 2000 },
  'crevedia':          { dist: 30, jud: 'Dambovita', tip: 'suburban', county: 'Dambovita', road: 'DN7 spre Pitesti', venues: ['curti ansambluri Crevedia', 'sala locala', 'zona verde'], pop: 6000 },
  'crevedia-mare':     { dist: 32, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN6 spre Alexandria', venues: ['curti case', 'sala locala Crevedia Mare', 'gradina'], pop: 1500 },
  'crivina':           { dist: 25, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1 nord', venues: ['vile cu curti Crivina', 'zona padure Crivina', 'zona premium nord'], pop: 3000 },
  'cucuieti':          { dist: 60, jud: 'Dambovita', tip: 'rural', county: 'Dambovita', road: 'DJ711', venues: ['curti spatioase', 'sala scolii', 'gradina'], pop: 600 },
  'dambovita':         { dist: 65, jud: 'Dambovita', tip: 'suburban', county: 'Dambovita', road: 'DN7 Targoviste', venues: ['sali events Dambovita', 'restaurante', 'Parcul Targoviste'], pop: 12000 },
  'dascalu':           { dist: 22, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN2 iesire est', venues: ['curti vile Dascalu', 'sali evenimente Dascalu', 'zona rezidentiala'], pop: 7000 },
  'decindea':          { dist: 55, jud: 'Dambovita', tip: 'rural', county: 'Dambovita', road: 'DJ711', venues: ['curti largi', 'sala locala', 'spatiu deschis'], pop: 700 },
  'dimieni':           { dist: 20, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN2 iesire est', venues: ['curti ansambluri Dimieni', 'sali community', 'zona verde'], pop: 5000 },
  'dobreni':           { dist: 75, jud: 'Ilfov',   tip: 'rural', county: 'Ilfov', road: 'DJ301E', venues: ['curti case', 'sala scolii Dobreni', 'spatiu rural'], pop: 1000 },
  'dobroesti':         { dist: 12, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN2 iesire est', venues: ['sali moderne Dobroesti', 'curti vile Dobroesti', 'zona rezidentiala'], pop: 10000 },
  'domnesti':          { dist: 22, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN7 Pitesti', venues: ['sali petreceri Domnesti', 'curti case', 'zona verde Domnesti'], pop: 9000 },
  'dragomiresti-deal': { dist: 22, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1A nord', venues: ['vile cu curti mari Dragomiresti Deal', 'zona premium rezidentiala', 'padure aproape'], pop: 4000 },
  'dragomiresti-vale': { dist: 22, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1A nord', venues: ['curti vile Dragomiresti Vale', 'zona rezidentiala premium', 'spatii verzi'], pop: 4000 },
  'fierbinti-targ':    { dist: 65, jud: 'Ialomita', tip: 'urban-mic', county: 'Ialomita', road: 'DN2 spre Urziceni', venues: ['sala culturala Fierbinti', 'curti case', 'parcul local'], pop: 6000 },
  'fundulea':          { dist: 45, jud: 'Calarasi', tip: 'urban-mic', county: 'Calarasi', road: 'A2 iesire Fundulea', venues: ['sala events Fundulea', 'restaurante', 'parcul orasului'], pop: 8000 },
  'ganeasa':           { dist: 18, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DJ602C', venues: ['curti vile Ganeasa', 'sali noi', 'zona verde Ganeasa'], pop: 5000 },
  'giurgiu':           { dist: 65, jud: 'Giurgiu', tip: 'urban', county: 'Giurgiu', road: 'DN5 spre Giurgiu', venues: ['sali events multiple Giurgiu', 'restaurante Giurgiu', 'Parcul Alei'], pop: 55000 },
  'glina':             { dist: 16, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'A2 iesire Glina', venues: ['curti vile Glina', 'sali petreceri', 'zona rezidentiala sud'], pop: 7000 },
  'ialomita':          { dist: 90, jud: 'Ialomita', tip: 'suburban', county: 'Ialomita', road: 'A2 + DN2A', venues: ['sali events', 'restaurante', 'zona Slobozia'], pop: 40000 },
  'iepuresti':         { dist: 50, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DN5 Giurgiu', venues: ['curti case', 'sala scolii Iepuresti', 'spatiu verde'], pop: 1500 },
  'jilava':            { dist: 10, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN41 Jilava', venues: ['sali petreceri noi Jilava', 'curti ansambluri Jilava', 'zona sud bucuresteni'], pop: 12000 },
  'magurele':          { dist: 12, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DJ602 Magurele', venues: ['sali events Magurele', 'curti case', 'zona Institut Atomic'], pop: 10000 },
  'mihai-voda':        { dist: 55, jud: 'Calarasi', tip: 'rural', county: 'Calarasi', road: 'DN3 Calarasi', venues: ['curti case', 'sala locala Mihai Voda', 'gradina'], pop: 2000 },
  'mihailesti':        { dist: 40, jud: 'Giurgiu', tip: 'urban-mic', county: 'Giurgiu', road: 'DN5 spre Giurgiu', venues: ['sala culturala Mihailesti', 'restaurante', 'centrul orasului'], pop: 6000 },
  'moara-vlasiei':     { dist: 30, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1 nord', venues: ['vile cu curti Moara Vlasiei', 'padurea din zona', 'zona exclusivista nord'], pop: 3500 },
  'mogosoaia':         { dist: 16, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1A Mogosoaia', venues: ['Palatul Mogosoaia', 'curti vile premium', 'Lacul Mogosoaia'], pop: 6000 },
  'nuci':              { dist: 30, jud: 'Ilfov',   tip: 'rural', county: 'Ilfov', road: 'DJ301F', venues: ['curti case', 'sala locala Nuci', 'spatiu verde rural'], pop: 1500 },
  'ordoreanu-vatra-veche': { dist: 70, jud: 'Giurgiu', tip: 'rural', county: 'Giurgiu', road: 'DJ412', venues: ['curti largi', 'sala scolii', 'gradina'], pop: 600 },
  'otopeni':           { dist: 14, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1 aeroport', venues: ['sali moderne Otopeni', 'restaurante Otopeni', 'zona aeroportului'], pop: 12000 },
  'pantelimon':        { dist: 12, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'Soseaua Pantelimon', venues: ['sali petreceri Pantelimon Ilfov', 'curti ansambluri', 'Lacul Pantelimon'], pop: 18000 },
  'peris':             { dist: 28, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1 nord', venues: ['vile cu curti Peris', 'Lacul Peris', 'zona verde nord'], pop: 4000 },
  'petrachioaia':      { dist: 22, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN2 iesire est', venues: ['curti vile Petrachioaia', 'sali noi', 'zona rezidentiala est'], pop: 5000 },
  'popesti-leordeni':  { dist: 8,  jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'A2 iesire Popesti', venues: ['sali petreceri multiple Popesti', 'curti', 'zona sud Capitala'], pop: 35000 },
  'prahova':           { dist: 45, jud: 'Prahova', tip: 'suburban', county: 'Prahova', road: 'DN1 spre Ploiesti', venues: ['sali events Ploiesti', 'restaurante', 'Parcul Ploiesti'], pop: 50000 },
  'racari':            { dist: 35, jud: 'Dambovita', tip: 'urban-mic', county: 'Dambovita', road: 'DN1A Racari', venues: ['sala culturala Racari', 'restaurante', 'centrul Racari'], pop: 7000 },
  'snagov':            { dist: 35, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN1 nord + DJ101', venues: ['Lacul Snagov', 'vile premium Snagov', 'restaurante la malul apei'], pop: 4000 },
  'stefanestii-de-jos':{ dist: 22, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN2 iesire est', venues: ['curti ansambluri Stefanestii de Jos', 'sali noi', 'zona rezidentiala est'], pop: 8000 },
  'teleorman':         { dist: 90, jud: 'Teleorman', tip: 'suburban', county: 'Teleorman', road: 'DN6/DN51', venues: ['sali events Alexandria', 'restaurante', 'Parcul Alexandru Vlahuta'], pop: 45000 },
  'tunari':            { dist: 15, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'Str. Tunari nord', venues: ['curti vile Tunari', 'sali moderne Tunari', 'zona premium nord Bucuresti'], pop: 7000 },
  'valea-piersicilor': { dist: 25, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DN2 iesire est', venues: ['curti vile Valea Piersicilor', 'sali noi', 'zona rezidentiala est Ilfov'], pop: 4000 },
  'vidra':             { dist: 22, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'DJ417 Vidra', venues: ['curti case Vidra', 'sali locale', 'zona verde Vidra'], pop: 7000 },
  'voluntari':         { dist: 10, jud: 'Ilfov',   tip: 'suburban', county: 'Ilfov', road: 'Soseaua Pipera', venues: ['Promenada Mall Voluntari', 'curti vile Pipera', 'sali premium Voluntari'], pop: 40000 },
  'sector-1': { dist: 0, jud: 'Sector 1', tip: 'sector', county: 'Bucuresti', road: 'Calea Victoriei, DN1', venues: ['Parcul Herastrau 186ha', 'vile premium', 'restaurante nord Bucuresti'], pop: 222000 },
  'sector-2': { dist: 0, jud: 'Sector 2', tip: 'sector', county: 'Bucuresti', road: 'Calea Mosilor, DN2', venues: ['Lacul Floreasca', 'Lacul Colentina', 'sali petreceri diverse'], pop: 350000 },
  'sector-3': { dist: 0, jud: 'Sector 3', tip: 'sector', county: 'Bucuresti', road: 'Calea Vitan, A2', venues: ['Sun Plaza Mall', 'Parcul IOR', 'Lacul IOR'], pop: 400000 },
  'sector-4': { dist: 0, jud: 'Sector 4', tip: 'sector', county: 'Bucuresti', road: 'Calea Oltenitei, A2', venues: ['Parcul Tineretului 210ha', 'Vitan Mall', 'sali petreceri sud'], pop: 300000 },
  'sector-5': { dist: 0, jud: 'Sector 5', tip: 'sector', county: 'Bucuresti', road: 'Calea Rahovei, metrou M4', venues: ['Parcul Sebastian', 'curtile caselor', 'sali locale'], pop: 270000 },
  'sector-6': { dist: 0, jud: 'Sector 6', tip: 'sector', county: 'Bucuresti', road: 'Bd Timisoara, metrou M5/M6', venues: ['Plaza Romania', 'Parcul Drumul Taberei', 'sali multiple'], pop: 380000 },
  'ilfov':    { dist: 15, jud: 'Ilfov', tip: 'judet', county: 'Ilfov', road: 'A1/A2/DN1', venues: ['sali diverse Ilfov', 'curti case', 'restaurante periurbane'], pop: 500000 },
  'bucuresti':{ dist: 0,  jud: 'Bucuresti', tip: 'capitala', county: 'Bucuresti', road: 'metrou, autobuz, tram', venues: ['sali premium', 'parcuri multiple', 'malluri'], pop: 2500000 },
  '1-decembrie': { dist: 20, jud: 'Ilfov', tip: 'suburban', county: 'Ilfov', road: 'DJ602D', venues: ['curti vile 1 Decembrie', 'sali community', 'zona rezidentiala'], pop: 5000 },
};

// ─── POOL DE VARIANTE TEXT ─────────────────────────────────────────────────────
const venueIntros = [
  (d) => `Familia ta poate organiza petrecerea copilului direct la <strong>${d.venues[0]}</strong> — animatorul SuperParty vine cu tot echipamentul necesar (boxe portabile wireless, materiale jocuri, costume premium) direct la adresa ta din <strong>${d.county}</strong>.`,
  (d) => `In <strong>${d.jud}</strong>, cele mai populare locatii pentru petreceri de copii sunt: <strong>${d.venues.join('</strong>, <strong>')}</strong>. SuperParty a organizat zeci de petreceri in aceasta zona si cunoaste perfectibil fiecare tip de spatiu.`,
  (d) => `<strong>${d.venues[0]}</strong> este una din locatiile preferate de familiile din <strong>${d.jud}</strong> pentru petrecerile de copii. Animatorul SuperParty se adapteaza oricarui spatiu — interior sau exterior, sala sau gradina.`,
  (d) => `Locatiile disponibile pentru petreceri copii in <strong>${d.jud}</strong> includ: <strong>${d.venues.join('</strong>, <strong>')}</strong>. Sfatul nostru: optati pentru un spatiu cu cel putin 20 mp liberi si acces la prize electrice — animatorul face restul.`,
];

const distTexts = [
  (d) => d.dist > 0 ? `SuperParty vine la <strong>${d.jud}</strong> (la ~${d.dist} km de Bucuresti, pe ${d.road}) cu deplasare inclusa in oferta. Contactati-ne pentru taxa exacta in functie de adresa si ziua petrecerii.` : `SuperParty acopera toata zona <strong>${d.jud}</strong> fara taxa de deplasare — suntem intotdeauna in Bucuresti, confirmam si ajungem in maxim 30-45 minute.`,
  (d) => d.dist > 0 ? `Distanta de la Bucuresti: ~${d.dist} km pe ${d.road}. Animatorul pleaca din Capitala cu timp suficient si ajunge cu 10-15 minute inainte de inceperea programului. Taxa de transport se stabileste transparent la rezervare.` : `In <strong>${d.jud}</strong> nu exista taxa de deplasare — facem parte din zona de acoperire totala SuperParty. Confirmam disponibilitatea in 30 minute de la apel.`,
  (d) => d.dist > 0 ? `Ajungem la <strong>${d.jud}</strong> via ${d.road}, la ${d.dist} km de Bucuresti. Animatorul vine cu o masina proprie bine echipata si parcheaza cat mai aproape de intrarea la locul petrecerii.` : `<strong>${d.jud}</strong> este complet acoperita de reteaua SuperParty — zero taxa deplasare, zero surprize. Suntem cei mai punctuali animatori din Capitala.`,
];

const charPersonTexts = [
  (d) => `Personajele cele mai cerute in <strong>${d.jud}</strong>: Spider-Man, Elsa, Batman, Sonic, PAW Patrol si Bluey pentru micutii pana in 4 ani. SuperParty aduce aceleasi costume premium licentiate, indiferent de distanta.`,
  (d) => `In <strong>${d.jud}</strong> si zona de <strong>${d.tip}</strong>, cele mai solicitate personaje 2025 sunt Elsa, Spider-Man, Batman si Captain America. La cerere speciala, SuperParty poate aduce oricare din cele 50+ personaje disponibile in colectie.`,
  (d) => `Copiii din <strong>${d.jud}</strong> au aceleasi preferinte ca cei din Capitala — Spider-Man, Elsa, Sonic, PAW Patrol domina topul rezervarilor. Animatorul vine cu costum impecabil, machiaj de calitate si energie de la primul moment.`,
  (d) => `Top personaje cerute in <strong>${d.jud}</strong>: <strong>Elsa</strong> pentru fetite 3-8 ani, <strong>Spider-Man</strong> pentru baieti 3-10 ani, <strong>Batman</strong> si <strong>Captain America</strong> pentru baieti mai mari. Colectia completa — 50+ personaje disponibile la rezervare.`,
];

const orgTips = [
  (d) => `Rezervati animatorul cu <strong>minim 7-14 zile inainte</strong> pentru saptamani normale si <strong>3-4 saptamani inainte</strong> pentru weekendurile din mai-septembrie si decembrie. Confirmam disponibilitatea in 30 minute si trimitem contractul in 24 de ore. Plata se face DUPA petrecere.`,
  (d) => `Proces rezervare SuperParty in <strong>${d.jud}</strong>: (1) Suna la 0722 744 377 sau trimite WhatsApp cu data, ora si adresa; (2) Confirmam disponibilitatea in 30 minute; (3) Trimitem contractul digital in 24 ore; (4) Animatorul ajunge la tine in ziua petrecerii. Garantia contractuala: daca copiii nu s-au distrat, nu platesti.`,
  (d) => `Sfat SuperParty pentru petrecerile din <strong>${d.jud}</strong>: alegeti intervalul 15:00-17:00 sambata sau 11:00-13:00 duminica — acestea sunt orele cu cea mai mare energie la copii. Evitati intervalele dopo 18:00 pentru copiii sub 6 ani. Animatorul ajusteaza ritmul programului in functie de energia grupului.`,
  (d) => `Pentru petrecerile in <strong>${d.jud}</strong>, SuperParty recomanda: spatiu minim 15-20 mp, o priza electrica in apropiere pentru boxe si o zona de asteptare pentru parintii care fotografiaza. Noi aducem tot restul — de la baloane la diplome personalizate.`,
];

// ─── FUNCTIE GENERARE TEXT UNIC ──────────────────────────────────────────────
function genUniqueContent(slug, d) {
  const h = hashSlug(slug);
  const venueText = venueIntros[h % venueIntros.length](d);
  const distText = distTexts[(h + 1) % distTexts.length](d);
  const charText = charPersonTexts[(h + 2) % charPersonTexts.length](d);
  const orgText = orgTips[(h + 3) % orgTips.length](d);
  
  return `
<section class="loc-s party-unique-section">
  <div class="container">
    <h2 class="sec-title">Animatori petreceri copii în <span style="color:var(--primary)">${d.jud}</span> — locatii și sfaturi practice</h2>
    <div style="max-width:780px">
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${venueText}</p>
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${distText}</p>
    </div>
  </div>
</section>

<section class="loc-s-alt party-topics-section">
  <div class="container">
    <h2 class="sec-title">Personaje cerute și cum rezervi în <span style="color:var(--primary)">${d.jud}</span></h2>
    <div style="max-width:780px">
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${charText}</p>
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${orgText}</p>
    </div>
  </div>
</section>`;
}

// ─── APLICA PATCH ─────────────────────────────────────────────────────────────
let patched = 0;
let alreadyDone = 0;
let missing = 0;

for (const [slug, data] of Object.entries(locData)) {
  const fp = path.join(pagesDir, 'petreceri', `${slug}.astro`);
  if (!fs.existsSync(fp)) { missing++; continue; }
  
  let content = fs.readFileSync(fp, 'utf-8');
  
  // Sterge sectiunile injectate anterior (daca exista)
  content = content.replace(/<section class="loc-s party-unique-section">[\s\S]*?<\/section>/g, '');
  content = content.replace(/<section class="loc-s-alt party-topics-section">[\s\S]*?<\/section>/g, '');
  content = content.replace(/<section class="loc-s">\s*<div class="container">\s*<h2 class="sec-title">Petreceri copii în[\s\S]*?<\/section>/g, '');
  content = content.replace(/<section class="loc-s-alt">\s*<div class="container">\s*<h2 class="sec-title">Personaje și teme populare[\s\S]*?<\/section>/g, '');
  
  // Injecteaza continut nou unic
  const uniqueSection = genUniqueContent(slug, data);
  
  // Insereaza inainte de ultima sectiune
  const lastIdx = content.lastIndexOf('<section');
  if (lastIdx < 0) { missing++; continue; }
  
  content = content.slice(0, lastIdx) + uniqueSection + '\n\n' + content.slice(lastIdx);
  fs.writeFileSync(fp, content, 'utf-8');
  patched++;
}

console.log(`\nPatched: ${patched} pagini | Lipsa: ${missing}`);

// Aplica si pt animatori-copii-sectorX (Cluster 3)
console.log('\nPatching animatori-copii pages...');
const sectorAnimData = {
  'animatori-copii-sector-1': { jud: 'Sectorul 1', county: 'Bucuresti', zone: 'Dorobanti, Floreasca, Aviatorilor, Baneasa, Victoriei', dist: 0, tip: 'sector', road: 'Calea Victoriei, DN1', venues: ['Parcul Herastrau 186ha', 'vile cu curti premium', 'restaurante nord Bucuresti'], specifics: 'Sectorul 1 este zona premium a Capitalei. Animatorii SuperParty selectati pentru aceasta zona au cea mai buna prezenta scenica si dictie din echipa noastra. Costume impecabile, prezenta profesionala, program fara momente goale.' },
  'animatori-copii-sector-2': { jud: 'Sectorul 2', county: 'Bucuresti', zone: 'Colentina, Floreasca, Tei, Stefan cel Mare, Obor', dist: 0, tip: 'sector', road: 'Calea Mosilor, DN2', venues: ['Lacul Floreasca', 'Lacul Colentina', 'sali petreceri diverse'], specifics: 'Sectorul 2 combina zone premium (Floreasca) cu zone populare (Colentina, Tei). SuperParty acopera toata diversitatea cu acelasi nivel de calitate si profesionalism.' },
  'animatori-copii-sector-3': { jud: 'Sectorul 3', county: 'Bucuresti', zone: 'Titan, Dristor, Vitan, Dudesti, Centrul Civic', dist: 0, tip: 'sector', road: 'Calea Vitan, A2', venues: ['Sun Plaza Mall', 'Parcul IOR', 'Lacul IOR'], specifics: 'In Sectorul 3, Sun Plaza Kids Zone si Parcul IOR sunt destinatiile preferate familiilor. SuperParty a organizat sute de petreceri in zona Titan, Dristor si Vitan si cunoaste perfect fiecare locatie potrivita.' },
  'animatori-copii-sector-4': { jud: 'Sectorul 4', county: 'Bucuresti', zone: 'Tineretului, Berceni, Timpuri Noi, Oltenitei', dist: 0, tip: 'sector', road: 'Calea Oltenitei, A2', venues: ['Parcul Tineretului 210ha', 'Vitan Mall', 'sali petreceri sud'], specifics: 'Parcul Tineretului (210 ha) este cel mai mare spatiu verde din sudul Capitalei. SuperParty organizeaza aici petreceri in aer liber cu echipament portabil complet, fara nicio rezervare de spatiu necesara.' },
  'animatori-copii-sector-5': { jud: 'Sectorul 5', county: 'Bucuresti', zone: 'Rahova, Sebastian, Ferentari, 13 Septembrie', dist: 0, tip: 'sector', road: 'Calea Rahovei, metrou M4', venues: ['Parcul Sebastian', 'curtile caselor', 'sali locale accesibile'], specifics: 'In Sectorul 5, SuperParty aduce servicii premium la preturi standard. Petrecerile au adesea un caracter familial extins — bunici, vecini si prieteni. Animatorul stie cum sa antreneze toata familia intr-o sarbatoare autentica.' },
  'animatori-copii-sector-6': { jud: 'Sectorul 6', county: 'Bucuresti', zone: 'Militari, Drumul Taberei, Crangasi, Giulesti', dist: 0, tip: 'sector', road: 'Bd Timisoara, metrou M5/M6', venues: ['Plaza Romania', 'Parcul Drumul Taberei', 'sali multiple Militari'], specifics: 'Sectorul 6 este cel mai populat din Capitala. SuperParty are animatori dedicati per cartier: Militari, Drumul Taberei, Crangasi si Giulesti — fiecare zona are caracteristici diferite pe care le cunoastem perfect.' },
  'animatori-copii-bragadiru': { jud: 'Bragadiru', county: 'Ilfov', zone: 'zona sud-vest Ilfov, limitrofa Sectorului 5', dist: 10, tip: 'suburban', road: 'DN41 Bragadiru', venues: ['ansambluri rezidentiale noi', 'curti case spacioase', 'Parcul local Bragadiru'], specifics: 'Bragadiru este unul din orasele cu cresterea cea mai rapida din jurul Capitalei. SuperParty vine in Bragadiru cu aceleasi pachete si garantii ca in centrul Bucurestiului — fara surcharges, fara surprize.' },
  'animatori-copii-bucuresti': { jud: 'Bucuresti', county: 'Bucuresti', zone: 'toate cele 6 sectoare', dist: 0, tip: 'capitala', road: 'metrou, autobuz, tram', venues: ['6 sectoare acoperite', 'sali premium', 'parcuri si malluri'], specifics: 'SuperParty opereaza in intreaga Capitala din 2018 — peste 10.000 de petreceri organizate in Bucuresti. Cunoastem fiecare sector, fiecare cartier, fiecare locatie. Zero deplasare, confirmare in 30 minute.' },
  'animatori-copii-chiajna': { jud: 'Chiajna', county: 'Ilfov', zone: 'limita vestica Sectorului 6, Militari Residence', dist: 8, tip: 'suburban', road: 'DN7 Militari', venues: ['Militari Residence', 'sala comunitara ansamblu', 'curti ansambluri noi'], specifics: 'Chiajna gazduieste Militari Residence — unul din cele mai mari ansambluri rezidentiale din Romania. SuperParty cunoaste perfect spatiile disponibile: sala comunitara, curtile interioare si spatiile comune amenajate.' },
  'animatori-copii-ilfov': { jud: 'Ilfov', county: 'Ilfov', zone: 'intreg judetul (30+ localitati)', dist: 15, tip: 'judet', road: 'A1/A2/DN1', venues: ['30+ localitati acoperite', 'sali diverse', 'curti case periurbane'], specifics: 'Judetul Ilfov este cel mai dinamic din Romania — populatia a crescut cu 60% in ultimii 10 ani. Familiile tinere mutate din Bucuresti in Ilfov apreciaza calitatea SuperParty — acelasi serviciu premium ca in Capitala, livrat direct la usa.' },
  'animatori-copii-otopeni': { jud: 'Otopeni', county: 'Ilfov', zone: 'oras nord, langa aeroportul Henri Coanda', dist: 14, tip: 'suburban', road: 'DN1 aeroport', venues: ['ansambluri premium Otopeni', 'sali events moderne', 'restaurante zona aeroportului'], specifics: 'Otopeni atrage familii internationale si romani cu experienta globala — acestia apreciaza profesionalismul de nivel international al animatorilor SuperParty. Optam pentru costumele cele mai noi si mai curate din inventar.' },
  'animatori-copii-pantelimon': { jud: 'Pantelimon', county: 'Ilfov', zone: 'oras Ilfov, limita est Sector 2', dist: 12, tip: 'suburban', road: 'Soseaua Pantelimon, DN3', venues: ['Lacul Pantelimon', 'ansambluri rezidentiale noi', 'sali petreceri Pantelimon'], specifics: 'Pantelimon Ilfov are o populatie in continua crestere si o comunitate activa de parinti. Lacul Pantelimon este locatia preferata pentru petrecerile de vara in aer liber — SuperParty vine cu echipament portabil si program adaptat spatiului exterior.' },
  'animatori-copii-popesti-leordeni': { jud: 'Popesti-Leordeni', county: 'Ilfov', zone: 'oras sud Ilfov, limita Sector 3', dist: 8, tip: 'suburban', road: 'A2 iesire Popesti, DN3', venues: ['sali petreceri multiple Popesti', 'ansambluri noi', 'curti case Sud Ilfov'], specifics: 'Popesti-Leordeni este al treilea cel mai populat oras din Ilfov. SuperParty acopera tot orasul — de la centrul vechi pana la ansamblurile new-built de pe DN3. Cel mai recomandat serviciu de animatori in retelele de parinti din Popesti.' },
  'animatori-copii-voluntari': { jud: 'Voluntari', county: 'Ilfov', zone: 'oras Ilfov, Pipera, Tunari, zona nord-est', dist: 10, tip: 'suburban', road: 'Soseaua Pipera, Voluntari', venues: ['Promenada Mall Voluntari', 'curti vile Pipera premium', 'sali events Voluntari'], specifics: 'Voluntari-Pipera este zona cu cea mai internationala populatie din Romania. SuperParty ofera animatori bilingvi (romana-engleza) disponibili pentru familiile de expati. Costumele selectate pentru zona Voluntari sunt din cele mai noi si mai curate din inventarul nostru.' },
};

let sectorPatched = 0;
for (const [dirName, d] of Object.entries(sectorAnimData)) {
  const fp = path.join(pagesDir, dirName, 'index.astro');
  if (!fs.existsSync(fp)) { console.log(`  LIPSA: ${dirName}`); continue; }
  
  let content = fs.readFileSync(fp, 'utf-8');
  
  // Sterge sectiunile anterioare daca exista
  content = content.replace(/<section class="sec party-unique-section"[\s\S]*?<\/section>/g, '');
  
  const h = hashSlug(dirName);
  const venueText = venueIntros[h % venueIntros.length](d);
  const distText = distTexts[(h + 1) % distTexts.length](d);
  
  const injectSection = `
<section class="sec party-unique-section" style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.5rem;font-weight:800;margin-bottom:1rem">Animatori petreceri copii în <span style="color:var(--primary)">${d.jud}</span> — ce este specific acestei zone</h2>
    <div style="max-width:780px">
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">Zone acoperite: <strong>${d.zone}</strong>. ${venueText}</p>
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${d.specifics}</p>
      <p style="color:var(--text-muted);line-height:1.9;margin-bottom:1rem">${distText}</p>
    </div>
  </div>
</section>`;
  
  const lastIdx = content.lastIndexOf('<section');
  if (lastIdx < 0) continue;
  content = content.slice(0, lastIdx) + injectSection + '\n\n' + content.slice(lastIdx);
  fs.writeFileSync(fp, content, 'utf-8');
  sectorPatched++;
}

console.log(`\nSector/animatori pages patched: ${sectorPatched}`);
console.log('\nTotal patched. Rulati acum: node scripts/site_wide_dup_check.mjs');
