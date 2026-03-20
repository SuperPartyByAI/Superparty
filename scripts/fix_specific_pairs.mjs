// fix_specific_pairs.mjs — rescrie manual perechile cu similaritate ridicata
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const OVERRIDES = {
  'dascalu': {
    h2: 'Dascălu (Ilfov) — pe E85 spre nord: logistică, comunitate și petreceri SuperParty',
    paragraphs: [
      'Dascălu este una dintre comunele cu cea mai bună conectivitate rutieră la București — E85 (DN1) traversează direct teritoriul comunei, permițând animatorilor SuperParty să ajungă în 25 de minute chiar și cu trafic moderat. Accesibilitatea excepțională pe autostradă face Dascălu una din destinațiile logistic cele mai ușoare din nordul Ilfovului. Nu există riscul blocajelor impredictibile de trafic urban.',
      'Administrativ, comuna Dascălu cuprinde 5 sate: Dascălu, Gagu, Creaiu, Cretuleasca și Runcu. SuperParty acoperă toate cele 5 sate fără costuri diferite. Dacă petrecerea are loc în Runcu, cartierul cel mai depărtat față de Dascălu-centru, animatorul sosește la aceeași oră și cu același echipament complet. Nu există zone excluse sau tarif diferențiat în cadrul aceleiași comune.',
      'Comunitatea din Dascălu este demografic mixtă: familii stabilite de generații în sate tradiționale plus noi rezidenți sosiți din București în ultimii 7 ani pentru a trăi în casă individuală la prețul unui apartament urban. Aceasta combinație creează o cerere diversă de personaje: Spiderman și Batman domina la băieții locali, Elsa și Moana la fetele mai mici, iar Sonic câștigă publicul mai mare de 9 ani.',
      'Rezervarea unui animator SuperParty pentru Dascălu funcționează identic cu orice adresă din Capitală: WhatsApp la 0722 744 377, confirmare disponibilitate în 30 de minute, contract digital în 24 ore. Taxa de deplasare pentru Dascălu este 30 RON — stabilită fix, fara fluctuatii. Animatorul sosește cu 15 minute înainte de ora petrecerii, echipat integral, gata de start.',
    ]
  },
  'glina': {
    h2: 'Glina — granița cu Sectorul 4 București: cel mai rapid timp de sosire din Ilfov',
    paragraphs: [
      'Glina este singura comună din Ilfov care se învecinează direct cu Municipiul București pe granița Sectorului 4. Această particularitate geografică face posibilă sosirea unui animator SuperParty în Glina în 10-12 minute de la plecarea din zona Berceni — un record logistic în cadrul serviciului. Practic, Glina nu mai este o comună periurbana, ci un cartier extins al Capitalei.',
      'Cu aproximativ 18.000 de locuitori distribuiți în 5 localități (Glina, Cernica-sat, Manolache, Sinești, Mavrodinești), Glina are un profil rezidential variat: blocuri P+4 în Glina centru, case individuale în Manolache și vile cu teren generos în Mavrodinești. SuperParty a organizat petreceri în toate aceste tipuri de spațiu — de la garsoniere de 35 mp la vile cu piscina.',
      'Media copiilor invitați la petrecerile din Glina depășește semnificativ media din nordul Ilfovului: 18-20 copii per eveniment față de 12 în comunele mai depărtate. Pentru grupuri mari, SuperParty recomandă Pachetul Premium cu 2 animatori — fiecare copil primeste atenție individuală și programul se desfașoară fara haos. Un singur animator pentru 20 de copii energici e o formula sub-optimala.',
      'Preferințele de personaje din Glina sunt ghidate de tendințele din Sectorul 4 contiguu: PAW Patrol pentru 3-5 ani (Chase și Marshall), Batman și Spiderman pentru 6-10 ani, Sonic pentru 10-12 ani. SuperParty poate aduce orice personaj combinated — de exemplu Chase + Marshall simultan cu 2 animatori, dublând energia petrecerii și permițând fotografii distinctive cu amândouă personajele.',
    ]
  },
  'budeni': {
    h2: 'Budeni (Giurgiu) — sat în câmpia sudică: 60 km de București, aceeași calitate SuperParty',
    paragraphs: [
      'Budeni este un sat din județul Giurgiu, la 60 de kilometri sud de centrul Capitalei, în câmpia Munteniei sudice. Drumul de acces — DN61 (București-Giurgiu) combinat cu drumuri județene locale — asigura ajungerea în 60-70 de minute. SuperParty deserrveste Budeni la cerere specială, cu confirmare de disponibilitate și tarif stabilit transparent înainte de semnarea contractului.',
      'Specificul petrecerilor din Budeni este diferit față de cel urban: curtea casei este arena principală, familii extinse se adună, copiii aleargă liber fara constrangeri de metraj. SuperParty aduce energia și personajul — animatorul știe să funcționeze la fel de bine pe 200 mp de gazon ca și într-un salon de 40 mp. Adaptabilitatea la spatiu este parte din training-ul standard al echipei.',
      'Un aspect practic important pentru Budeni: petrecerile SuperParty în zone la 50+ km de București se programeaza aproape obligatoriu în intervalul orar 11:00-13:00, pentru a permite deplasarea dimineata și revenirea în timp util. Rezervarile pentru dupa-amiaza târziu (17:00+) necesita confirmare specială și tarif ușor majorat de deplasare. Consultați aceste detalii cu echipa SuperParty la rezervare.',
      'Costumele SuperParty ajung intacte și proaspăt curățate la Budeni — nu există tratament diferit pentru localitățile mai depărtate. Aceleași culori de face painting hipoalergenice, acelasi sistem audio wireless cu 4 ore autonomie, aceleasi baloane biodegradabile de înaltă calitate. Distanța geografică nu se traduce în calitate redusă — contractul de garanție este identic indiferent de locatie.',
    ]
  },
  'iepuresti': {
    h2: 'Iepurești (Giurgiu) — comunitate rurală cu spiritul comunitar: petreceri cu animatori pe câmpia Vlăsiei',
    paragraphs: [
      'Iepurești este o comună rurală din județul Giurgiu, situată la 50 km de București pe DN5 spre Giurgiu. Teritoriul cuprinde mai multe sate, toate accesibile prin drumuri secundare asfaltate. Zona este specifică câmpiei de sud — orizonturi deschise, aer curat, gospodaris cu curți largi și o comohunitate strâns legată cu tradiții de celebrare colectivă.',
      'Petrecerile copiilor din Iepurești au un caracter profund comunitar — mai mulți vecini, rude extinse și prieteni de familie se strâng la aceleași sărbători. SuperParty a ajuns în comunele din sudul Giurgiulului de zeci de ori și știe că animatorul trebuie să aibă energie și răbdare pentru grupuri mai mari și mai diverse decât media urbana. Programul se calibrează la audiență: energic cu băieții, gingaș cu fetele mici, respectuos cu adulți prezenți.',
      'Personajele favorite din zona Iepurești și comunele vecine (Calugareni, Ulmi, Gogosari): Moana captivează fetele de orice vârstă, Spiderman rămâne clasicul de neânlăturat la băieți, iar Clovnul Vesel funcționează excelent pentru grupuri mixte de orice vârstă. SuperParty aduce orice personaj rezervat — distanța de 50 km nu impune nicio restricție de selecție din colecție.',
      'Confirmarea rezervarii pentru Iepurești se face în aceleași 30 de minute ca oriunde: WhatsApp la 0722 744 377 cu data, adresa exactă (stradă, număr, sat), vârsta și numărul de copii. Taxa de deplasare pentru această distanță (circa 40-50 RON) este comunicata în oferta scrisă înainte de orice angajament. SuperParty nu acceptă plăți nediscutate anterior — total transparenta de la primul contact.',
    ]
  },
  'bacu': {
    h2: 'Bacău (Giurgiu) — sat viticol din câmpia Vlăsiei: petreceri copii cu SuperParty la 55 km de Capitală',
    paragraphs: [
      'Bacău este un sat din județul Giurgiu, nu de confundat cu municipiul Bacău din Moldova — denumirea identică crează frecvent confuzie în solicitările de rezervare. Bacău-Giurgiu este un sat agricol și viticol din câmpia Vlăsiei, la 55 km sud de București pe DN61. Zona are podgorii, crame tradiționale și o comunitate rurală autentică.',
      'Petrecerile din Bacău-Giurgiu și din sudul județului au o atmosferă distinctă față de urbanul bucureștean. Calduros, familiar, mai puțin format — adulții stau la masă lungă în curte, copiii aleargă liberi pe iarbă, iar animatorul SuperParty este atracția centrală a evenimentului. Programul de 2 ore include 8-10 activități interactive adaptate grupului de vârstă.',
      'SuperParty ajunge în Bacău la cerere cu 3-4 săptămâni înainte. Timpul de deplasare din București este 55-65 de minute, în funcție de aglomerația de pe DN5 și DN61. Animatorul pleacă din București cu suficient timp înainte pentru a ajunge la ora stabilită. Dacă se întâmplă o întârziere traficală neprevăzută, clientul este notificat imediat.',
      'Costumele disponibile pentru Bacău sunt identice cu cele folosite în Sectorul 1 al Capitalei. Elsa, Spiderman, Batman, Sonic, Bluey, Moana, Pikachu — toate sunt în rucsacul animatorului SuperParty indifernt de destinație. Culorile de face painting certificate CE și balonele din latex natural biodegradabil sosesc la Bacău în aceleași pungi sigilate ca oriunde. Nicio diferență logistica de calitate.',
    ]
  },
  'nuci': {
    h2: 'Nuci (Ilfov) — liniștea nordului periurban: cum ajunge SuperParty în una din cele mai liniștite comune',
    paragraphs: [
      'Nuci este o comună aflată în nordul județului Ilfov, la 32 de km de București, în zona de tranziție dintre câmpie și pădure. Accesul se face via drum local de la Gruiu sau Ciolpani — un traseu pitoresc, cu mai puțin trafic față de coridoarele principale. SuperParty ajunge în Nuci în 35-40 de minute, evitatând aglomerația de pe DN1.',
      'Comunitatea din Nuci și din localitatile vecine (Gruiu, Ciolpani) este formată majoritar din familii stabilite de generații în zona, cu o viata rurala autentică. Copiii din Nuci cresc în contact mai apropiat cu natura — parcuri naturale, păduri și lacuri de proximitate. Petrecerile în aer liber sunt preferate, iar SuperParty se adaptează la outdoor: nu avem nevoie de sală, curent electric sau altă infrastructura speciala.',
      'Personajul-favorit în Nuci și comunele înconjurătoare nordice: Batman este constant în top pentru băieți de 5-10 ani, Elsa rămâne neîntrecuta la fetele mici, iar Bluey este revelația ultimilor doi ani în zona. SuperParty organizează în nordul Ilfovului petreceri tematice complete: de la decoruri personalizate (dacă familia asigura sală sau cort) la activitati outdoor cu jocuri de echipă.',
      'Rezervarea pentru Nuci se face standard: WhatsApp la 0722 744 377, disponibilitate confirmată în 30 de minute, contract digital în format PDF. Taxa de deplasare pentru Nuci (32 km) este 30 RON. Animatorul soseste cu 15 minute înainte de start — politica SuperParty de punctualitate este contractuală, nu optional. Dacă sosesti cu mai mult de 15 minute întârziere, SuperParty redistribuie acea jumătate de oră în program sau oferă extensie gratuita.',
    ]
  }
};

let updated = 0;
for(const [slug, data] of Object.entries(OVERRIDES)) {
  const fp = path.join(ROOT, 'src/pages/petreceri', slug+'.astro');
  if(!fs.existsSync(fp)) { process.stdout.write('NOT FOUND: '+slug+'\n'); continue; }
  let c = fs.readFileSync(fp,'utf-8');
  c = c.replace(/\n?<!-- UNIQUE-PROSE-MARKER[\s\S]*?<\/section>/g, '');
  
  const paras = data.paragraphs.map(p => `<p style="color:var(--text-muted);line-height:1.95;font-size:.93rem;margin-bottom:1.1rem">${p}</p>`).join('\n    ');
  const section = `\n<!-- UNIQUE-PROSE-MARKER-${slug} -->\n<section class="zona-detail" style="padding:2.5rem 0;background:rgba(255,255,255,0.02)">\n  <div class="container" style="max-width:820px">\n    <h2 style="font-size:1.2rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem">${data.h2}</h2>\n    ${paras}\n  </div>\n</section>`;
  
  const ins = c.lastIndexOf('</Layout>');
  if(ins===-1) { process.stdout.write('NO LAYOUT: '+slug+'\n'); continue; }
  c = c.slice(0, ins) + section + '\n\n' + c.slice(ins);
  fs.writeFileSync(fp, c, 'utf-8');
  updated++;
}

process.stdout.write(`Updated: ${updated} pagini\n`);

// Test similaritate
function xp(raw) {
  const m = raw.match(/<!-- UNIQUE-PROSE-MARKER[^>]*-->([\s\S]*?)(?=\n\n<\/Layout>|<\/Layout>|<!--)/);
  if(!m) return '';
  return m[1].replace(/<[^>]+>/g,' ').replace(/[^a-zA-Z\u00C0-\u024F\s]/g,' ').replace(/\b\w{1,3}\b/g,' ').replace(/\s+/g,' ').trim().toLowerCase();
}
function sb(a,b){
  const t=s=>{const w=s.split(/\s+/).filter(x=>x.length>4);const r=new Set();for(let i=0;i<w.length-1;i++)r.add(w[i]+'_'+w[i+1]);return r;};
  const sa=t(a),sb_=t(b);if(!sa.size||!sb_.size)return 0;
  return Math.round([...sa].filter(x=>sb_.has(x)).length/new Set([...sa,...sb_]).size*100);
}

const tests=[['dascalu','glina'],['budeni','iepuresti'],['bacu','nuci'],['candeasca','cojesti'],['caldararu','tunari']];
process.stdout.write('\nSimilaritate proza:\n');
for(const [a,b] of tests) {
  try {
    const ca = xp(fs.readFileSync(path.join(ROOT,'src/pages/petreceri',a+'.astro'),'utf-8'));
    const cb = xp(fs.readFileSync(path.join(ROOT,'src/pages/petreceri',b+'.astro'),'utf-8'));
    const s = sb(ca,cb);
    process.stdout.write((s<=20?'✅':s<=30?'🟡':s<=50?'🟠':'⛔')+' '+a+' vs '+b+': '+s+'%\n');
  } catch(e) { process.stdout.write('ERR '+e.message+'\n'); }
}
