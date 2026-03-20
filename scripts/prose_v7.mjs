import fs from 'fs';
import path from 'path';

const dir = 'src/content/seo-articles';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.mdx'));

console.log('--- Aplicare Motor Hiper-Dens V7 pe ' + files.length + ' fisiere ---');

function spin(text, h) {
  let spun = text;
  const regex = /\{([^{}]+)\}/g;
  let iters = 0;
  while (spun.includes('{') && iters < 8) {
    spun = spun.replace(regex, (m, c) => {
      const parts = c.split('|');
      const r = Math.abs(Math.sin(h++) * 10000);
      return parts[Math.floor(r) % parts.length];
    });
    iters++;
  }
  return spun;
}

const bp = [
  "{Organizarea|Planificarea|Structurarea|Setarea|Pregătirea} unei {petreceri pentru copii|aniversări private|serbări perfecte|zile de naștere de vis|surprize aniversare} în {LOC} {nu a fost|nu reprezintă|nu este nicicând|nu necesită|nu implică} o {provocare|bătaie de cap|problemă complicată|misiune imposibilă|grijă majoră} dacă {alegi|optezi pentru|soliciți|contractezi|rezervi} o {echipă de top|agenție de experți|trupă profesionistă|formulă experimentată|structură artistică} precum SuperParty. {Prezența lui|Apariția lui|Aducerea lui|Implicarea lui|Vizita lui} {CHAR} {va schimba totul|oferă magia supremă|stârnește entuziasm pur|transformă atmosfera|livrează zâmbete instant}. {Suntem la un clic distanță|Intervenim instant|Coordonăm totul rapid|Te deservim eficient|Acționăm prompt}.",
  "{O armată de|Sute de|Nenumărate|O mulțime de|Zeci de} {mămici|bunici|familii|părinți|adulți} din {LOC} {caută lunar|doresc constant|vizează frecvent|urmăresc mereu|solicită adesea} {servicii premium|spectacole complete|oferte imbatabile|intervenții impecabile|jocuri captivante}. {Când inviți un erou ca|Odată ce intră în scenă|Imediat ce debarcă|Dacă îl alegi clar pe|În plus, prezența masivă a lui} {CHAR}, {nivelul de entuziasm|gradul de interes|explozia de fericire|impactul emoțional|valoarea evenimentului} {sare pur și simplu în aer|atinge cote maxime|strălucește puternic|marchează sufletele micuților|stabilește recorduri locale}.",
  "{Dacă îți dorești|Când vizezi|Pentru a atinge|În ideea de a bifa|Visând curajos la} un {spectacol de excepție|show memorabil|eveniment perfect|party ca în filme|moment magic} direct în {LOC}, {tot ce ai de făcut este|singurul tău task este|pasul logic rămâne|rețeta succesului implică|secretul absolut este} să {apelezi la o trupă cu vechime|ne contactezi fără rețineri|soliciți garantat echipa|mergi pe mâna noastră|chemi profesioniștii absoluți}. {Iar surpriza absolută cu|Intervenția artistică a lui|Jocurile coordonate de|Costumația sclipitoare a lui|Prestația plină de carismă prin} {CHAR} {rămâne garanția supremă|este cireașa de pe tort|reprezintă vârful aisbergului|validează prețul plătit|salvează complet ziua festivă}.",
  "{Siguranța și educația|Buna creștere și siguranța fizică|Atenția și protecția|Zâmbetul și igiena procedurală|Standardele de lucru de elită} {sunt aspecte ne-negociabile|reprezintă factori cheie|stabilesc regulile interne|sunt garantate 100%|primează mereu obligatoriu} {când activăm în arealul privat din|oriunde suntem chemați în aria|la interacțiunile din perimetrul|pe parcursul intervențiilor din|în interiorul superbei locații din} {LOC}. {Animatorii care îl joacă pe|Talentații care îl întruchipează pe|Experții ce devin temporar|Colegii noștri instruiți să fie precis|Actorii profesioniști transformați clar în} {CHAR} {trec teste de conduită|sunt verificați atent|au pedagogia în sânge|posedă carismă antrenată pur|știu cum să capteze masele de copii constant}.",
  "{Calitatea|Acuratețea|Perfecțiunea|Autenticitatea|Superlativul obținut în realizarea} {costumelor|recuzitei|ținutelor de lux|accesoriilor scenice|echipamentelor logistice} prestate exclusiv pentru {CHAR} {este evidentă|se vede de la poștă|atrage privirile imediat|lasă audiența mută admirativ|convinge din primele secunde garantat}. {Nu admitem sfâșieri sau materiale ieftine|Menținem totul curat lacrimă de la spălătorie|Restaurăm și investim organic în hainele eroilor|Suntem impecabili mereu la aspectul curat primar|Folosim replici excepționale filmice perfect} atunci când ne instalăm voioși în {LOC}."
];

const extendedBp = [];
const subjects = ["{Planificarea|Organizarea|Gândirea|Setarea|Aranjarea}", "{Eficiența extremă a prezenței|Bucuria interacțiunii totale|Valoarea certă adăugată evident creativ|Garanția deplină totală asumată real|Certitudinea fericirii debordante constant}", "{Orice eveniment modern|Fiecare zi specială|Fiecare pachet de lux tematic complet|Comanda lansată cert|Experiența atent aleasă curat}", "{Recomandările calduroase adunate clar in top|Părerile minunate exprimate deschis public curat|Vizualizările oneste distribuite amplu pe net|Feedback-urile zecilor de clienti fideli la noi|Impresiile zecilor de mărturii online clar structurate}", "{Baza logistică uriașă stabilă adusă complet live|Toată magia absolută livrată la ușă cert și sigur|O mulțime uriașă de baloane colorate evident viu|Infrastructura creată punctual organizat ferm|Toată veselia adunată și livrată fix matematic exact unde vrei}"];
const attributes = ["{ne-a consacrat clar de 10 ani neîntrerupt|reprezintă avantajul major față de oricine competitiv|te scapă complet instantaneu de tot stresul neplăcut mereu ascuns undeva evident prin preajmă masiv pur constatat|te va relaxa vizibil și concret deplin din start 100%|vine cu garanții extrem de absolute strict validate public}", "{reverberând mereu un sunet cald clar extrem de blând din amfiteatru portabil sonor calitativ impecabil super absolut adus de noi acolo clar evident mereu gratuit pe comanda voastra absolut fericita rapid executata prompt și calm fara surprize pur nedorite masiv exluse garantat total.|rezolvând absolut orice hop organizatoric local din umbra absolut discret mereu calm pe zeci de județe limitrofe Bucurestiului cel aglomerat cu success constant zilnic curat validat prompt din experiente anterioare la clienti top ce revin an de an|astfel adăugând un maxim garantat de fericire prețioasă pentru cel norocos ce devine rapid ferm centrul universului complet fascinat imediat instant asigurat masiv si protejat energetic pozitiv|oferind fix o memorie scumpă palpabilă copiilor radiind excelent magic ferm inedit surprinzător dar perfect echilibrat mereu absolut complet ferm testat|livrând un serviciu extrem de precis direct la virgulă fixă fara rateuri absolut deloc de ordin de intarziere si de minus de atentie asidua pur oferita cu o tona de efort fizic epuizant dus cu un imens entuziasm mereu.}"];
const impacts = ["{Succesul e total asigurat 100% clar ferm și garantie 150% din start fix pe ora setată inițial mereu absolut mereu garant|Invitații vor vorbi exclusiv pozitiv pur si mereu încântat absolut direct laudativ fără nici un fel de umbră falsă constant|Părinții stau complet complet liniștiți la relaxare cu bere și vin în zona secundară izolată și liniștea curge minunat spre seară curat perfect mereu la noi exclusiv testat pe teren constant fix mereu sigur permanent pur perfect fix|Nimeni din cei de față prezenți nu mai stă nervos sau stresat la ceas asteptând să oprească vreo ceartă subită ivită spontan din motive pur copilărești rezolvate mereu facil cu mult har asigurat rapid evident curat perfect pur mereu si ferm sigur absolut deloc exclusiv|Toată lumea implicată va savura magia imersiv fix adus din super ecrane masive ale copilăriei de poveste pur inedită dar real prestată live pe locația stabilă exact curentă mereu complet uimitor}."];
const characters = ["{CHAR}", "{protagonistul suprem adică desigur CHAR|cel pe care juniorii îl adoră adică CHAR|mascota magică pură identificată clar prin CHAR|sufletul viu colorat al audienței fermecătoare CHAR}"];
const locations = ["în {LOC}", "printre rezidenții moderni bucuroși localizați frumos din {LOC}", "chiar la adresa confortabilă rezervată punctual curat exact în inima din {LOC}"];

for (let s of subjects) {
  for (let a of attributes) {
    for (let i of impacts) {
      for (let c of characters) {
        for (let l of locations) {
           extendedBp.push(s + ' unui cadru festiv memorabil absolut minunat ' + l + ' ' + a + ' prin participarea formidabilă prestrată pur intens emoțional cu carismă magică constant oferită cu iubire de către ' + c + '. Copiii plini de veselie sunt prinși fascinat fix într-un vârtej narativ miniatural perfect controlat clar. ' + i + ' Și totul rămâne în general captat clar curat pur fixat ferm în fotografii luminoase și curate permanent amintiri super frumoase garantat livrate sigur la domiciliu curat. Acesta este in final elementul secret si esential care ne ridica standardul de organizare de-a ungul anilor atat de frumosi pentru noi echipa noastra de excelenta absoluti ferm mereu prezenți la datorie cu multa gratie.');
        }
      }
    }
  }
}

bp.push(...extendedBp);

let updated = 0;
let hVar = 0;

for (let f of files) {
  const fp = path.join(dir, f);
  let c = fs.readFileSync(fp, 'utf-8');
  
  const titleMatch = c.match(/title:\s*"([^"]+)"/);
  const title = titleMatch ? titleMatch[1] : '';
  const locMatch = title.match(/Copii (.*?) \|/i);
  let loc = locMatch ? locMatch[1].trim() : f.replace('.mdx', '');
  loc = loc.replace('București – ', '').replace('Bucuresti - ', '');
  
  const charMatch = title.match(/Animator\s(.*?)\sPetreceri/i);
  const charName = charMatch ? charMatch[1].trim() : 'Zâne Bune';
  
  let paragraphsPool = [];
  
  let baseH = 0;
  for(let i=0; i<f.length; i++) baseH += f.charCodeAt(i);
  
  for (let i = 0; i < 40; i++) {
    hVar += 7;
    const bpidx = (baseH + i * 17) % bp.length;
    const rawForm = bp[bpidx];
    const spun = spin(rawForm, hVar + baseH).replace(/\{LOC\}/g, loc).replace(/\{CHAR\}/g, charName);
    paragraphsPool.push('<p>' + spun + '</p>');
  }

  const finalProse = paragraphsPool.join('\n\n');

  const titles = [
    'Informații vitale pentru serbări cu ' + charName + ' excepțional planificate local modern în zona ' + loc,
    'Detalii de preț și pachet fixate ferm calitativ absolut pentru prestația personajului uimitor adus din basme ' + charName + ' în ' + loc,
    'Logistică impecabilă - rezervă-l imediat la curte relaxat pe ' + charName + ' în inima liniștită primitoare din super arealul ' + loc,
    'Distracție fără margini calitativ garantate 100% alături fericit clar de magnificul tău îndrăgit perfect anume personaj ' + charName + ' în ' + loc
  ];
  const secTitle = titles[baseH % titles.length];
  
  let newHtml = "\n<!-- UNIQUE-TEXT-V7 -->\n" +
"<section class='zona-detail' style='padding:2.5rem 0;background:rgba(255,255,255,0.02)'>\n" +
"  <div class='container' style='max-width:820px'>\n" +
"    <h2 style='font-size:1.2rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem'>" + secTitle + "</h2>\n    " +
finalProse.replace(/\n\n/g, '\n    ') + "\n" +
"  </div>\n" +
"</section>\n";

  if (c.includes('<section class="zona-detail"')) {
    c = c.replace(/<!-- UNIQUE-(?:PROSE|SPINTAX|TEXT).*?-->[\s\S]*?<\/section>/g, '');
  } else if (c.includes("<section class='zona-detail'")) {
    c = c.replace(/<!-- UNIQUE-(?:PROSE|SPINTAX|TEXT).*?-->[\s\S]*?<\/section>/g, '');
  } else if (c.includes('UNIQUE-PROSE-MARKER')) {
    c = c.replace('UNIQUE-PROSE-MARKER', '');
  }
  
  c = c.replace(/<!-- UNIQUE-TEXT-V6 -->[\s\S]*?<\/section>/g, '');
  c = c.replace(/<!-- UNIQUE-TEXT-V7 -->[\s\S]*?<\/section>/g, '');
  c = c.replace(/<!-- UNIQUE-SPINTAX -->[\s\S]*?<\/section>/g, '');
  
  c = c.trim() + '\n\n' + newHtml.trim() + '\n';
  
  fs.writeFileSync(fp, c, 'utf8');
  updated++;
  if(updated % 100 === 0) process.stdout.write(updated + '/' + files.length + '\n');
}

console.log('✅ Hiper-Densitatea V7 aplicata pe ' + files.length + ' pagini!');
