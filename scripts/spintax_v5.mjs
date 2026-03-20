import fs from 'fs';
import path from 'path';

const DIR = 'src/content/seo-articles';
const files = fs.readdirSync(DIR).filter(f => f.endsWith('.mdx'));

console.log('Aplicare Spintax Fractal pe ' + files.length + ' fisiere...');

// Spintax parser: {a|b|c}
function spin(text, h) {
  let spun = text;
  const regex = /\{([^{}]+)\}/g;
  let iters = 0;
  // Parse nested spintax by repeating
  while (spun.includes('{') && iters < 5) {
    spun = spun.replace(regex, (m, c) => {
      const parts = c.split('|');
      const r = Math.abs(Math.sin(h++) * 10000);
      return parts[Math.floor(r) % parts.length];
    });
    iters++;
  }
  return spun;
}

const templates = [
  "{Echipa noastră de la|Animatorii|Actorii|Profioniștii de la} SuperParty au {călătorit|străbătut|parcurs|efectuat drumul} {spre|către|în direcția} {LOC} {de nenumărate ori|de sute de ori|frecvent|constant}. {Fiecare|Orice|Absolut fiecare} {eveniment|petrecere|aniversare} {are farmecul ei|vine cu energia ei|este unică}, iar {LOC} {bineînțeles că nu|clar nu} {face excepție|se abate de la regulă}. {Aici|În această comunitate|Pe plan local}, {părinții|familiile|oamenii} {sunt foarte calzi|organizează evenimente senzaționale|se implică total}. {Cel mai dorit|Cel mai iubit|Foarte apreciat|Cel mai cerut} personaj din {LOC} {este în aceste luni|pare a fi mereu|rămâne la mare căutare} {CHAR}. {Dar colecția|Totuși garderoba|Însă portofoliul} noastră {include|cuprinde|pune la dispoziție} {peste 50 de variante|zeci de alte tematici|multe alte opțiuni}. {Când ajungem|Odată ce sosim|Imediat ce debarcăm} în {LOC}, {aducem|despachetăm|pregătim} {un kit profesionist|un echipament premium|arsenalul de distracție}: {costumul impecabil al lui|garderoba atent curățată pentru|ținuta autentică pentru} {CHAR}, {culori|pigmenți} de face painting {certificate dermatologic|premium|aprobate standard}, {multe baloane|zeci de baloane de calitate|baloane speciale} de modelaj și {un sistem de sunet puternic|o boxă portabilă performantă}. {Rezervarea|Planificarea|Stabilirea} unui {animator|actor|profesionist} pentru {LOC} este {foarte simplă|intuitivă|lipsită de bătăi de cap}: {ne trimiți un mesaj scurt|ne scrii pe WhatsApp|ne contactezi rapid}. {Oferim|Asigurăm|Garantăm} {spectacol complet|magie|zâmbete} și ne mulțumești la final! {Dacă organizezi totul acasă|Indiferent dacă e party la curte|Chiar dacă închiriezi un colț de restaurant}, în {LOC} ne adaptăm imediat!",

  "{Părinții|Multe mămici|Oamenii} din {LOC} ne {întreabă absolut mereu|scriu adesea|chestionează des}: „{Veniți|Vă deplasați|Ajungeți} {până aici|la noi|în zona noastră}?”. {Răspunsul este da, evident|Tolerăm deplasările cu drag|Categoric da}! {Comunitatea|Spațiul|Zona} din {LOC} merită {aceeași calitate de top|același zâmbet|aceleași spectacole senzaționale} ca {oriunde altundeva|în centru|în Capitală}. {O altă|O a doua} întrebare este: „Vine {fix personajul rezervat|chiar|cu adevărat} {CHAR}?”. {Garanția|Certitudinea|Promisiunea} SuperParty este că {vom trimite|alocăm|dispunem obligatoriu} exact ceea ce ai {stabilit|ales|cerut}. {CHAR} {este extrem de popular|rupe topurile|e mereu o bucurie} în {LOC}, dar {avem și restul personajelor la dispoziție|orice alt print vrei, îl avem|există 50+ opțiuni}. {Pachetul clasic|Varianta uzuală|Configurația standard} {pentru două ore|de minim două ore|de minim 2h de show} {oferă|implică|presupune} {baloane colorate|modelaj interactiv de baloane|mici sculpturi de baloane} și {pictură pe față minuțioasă|design facial spectaculos|face painting extrem de calitativ}. {Niciun minut mort|Nu se dă greș absolut deloc|Totul curge perfect}, iar {cei mici|copiii|invitații} se {bucură din plin|distrează la maxim}. {În ceea ce privește timpul|Ca detaliu temporal}, {sfătuim clienții|vă propunem|recomandăm} să {rezerve|facă booking|asigure o dată} cu {câteva zile|suficient timp|cel puțin o săptămână} {în avans|din timp}, mai ales {pentru weekend|sâmbăta și duminica|la datele aglomerate} în {LOC}.",

  "{Din punct de vedere|Pentru o analiză a|Observând specificul} petrecerilor din {LOC}, {constatăm profilul modern|vedem o evoluție masivă|remarcăm un gust rafinat}. {Aici, părinții|Familiile de aici|Mămicile locului} pun {mare preț|foarte mult accent|baza} pe {experiențe de super calitate|o amintire autentică|un show adevărat}, nu pe improvizații. {Animatorii SuperParty|Actorii din echipa noastră|Colegii noștri animatori} care ajung în {LOC} {sunt obișnuiți să interacționeze|știu cum să capteze|au carisma setată pe} cu zeci de copii odată. {Dacă ai optat pentru|Atunci când îl chemi pe|Dacă îl aduci pe} {CHAR}, noi {creăm|instituim|fabricăm} magia absolută {direct în sufragerie|în locația voastră|oriunde ne acordați spațiul}. {Un element cheie|Un detaliu major|Un factor de încredere} este că {costumele noastre, inclusiv|ținutele noastre, precum} cel de {CHAR}, sunt {menținute la calitatea de fabrică|fără defecte|spălate și curate}. {Nimic uzat|Nu vei vedea improvizații ieftine|Fără aspect comercial}. {SuperParty acoperă tot perimetrul din|Logistica noastră permite sosirea fluentă în} {LOC} {indiferent de zi|în orice zi de weekend|pe orice vreme}. {Echipa dispune|Noi am format|Firma noastră are} o trupă de profesioniști autentici, {astfel probabilitatea unei anulări este zero absolut|garantând mereu un dublaj medical|lucru ce elimină teama de țepe}. {Sună-ne acum|Cheamă-ne cu încredere|Așteptăm cu nerăbdare un apel} pentru a seta o sosire la adresa din {LOC}!",

  "{Comparând piața locală de distracții|În rândul serviciilor de organizare evenimente|Dacă analizăm nivelul experiențelor} disponibile în {LOC}, {ofertarea SuperParty|noi de la SuperParty|propunerea agenției noastre} aduce avantaje {clare|absolute|categorice}. {În primul rând|Înainte de toate}, {recenziile extraordinare de pe Google|ratingul nostru public absolut autentic|aprecierile zecilor de clienți} ne {scot clar în evidență|detașează imens|plasează pe podiumul de onoare}. {Alegerea|Selecția} unui pachet vizual {impresionant|spectaculos} precum {CHAR} {creează certitudinea unei poze fenomenale|dă un aer magic întregului eveniment|oferă copiilor fix amintirea căutată}. {Pentru locațiile din|În perimetrul|La serbările ce se întâmplă în} {LOC}, {ajungem regulat mereu cu zâmbetul pe buze|parcurgem distanța rapid și relaxat|ne organizăm traseul impecabil}. {Costumele pe care le utilizăm|Hainele purtate de actori|Ținutele personajelor noastre}, {mai ales pe formatul lui|deosebit pentru|specific} {CHAR}, au suferit o verificare {minuțioasă|la sânge|continuă}, {înlocuindu-le pe loc când e cazul|reparând orice defect imediat|astfel încât să fie poezie curată}. {Mai mult|Pe deasupra|Iar ceva extraordinar}, {conceptul cu rezerve asigurate|sistemul strict de back-up} te scapă din {din scenariul unui coșmar|emoția că va lipsi artistul|grija unui apel de la urgență anulată}. {Cei din|Dacă ești din|Oamenii din} {LOC} au testat acest standard care i-a cucerit! {Un simplu mesaj WhatsApp|Un e-mail sau SMS|O apelare scurtă} este tot ce ai de prestat."
];

let updated = 0;
let hVar = 0;

for (let f of files) {
  const fp = path.join(DIR, f);
  let c = fs.readFileSync(fp, 'utf-8');
  
  const titleMatch = c.match(/title:\s*"([^"]+)"/);
  const title = titleMatch ? titleMatch[1] : '';
  const locMatch = title.match(/Copii (.*?) \|/i);
  let loc = locMatch ? locMatch[1].trim() : f.replace('.mdx', '');
  loc = loc.replace('București – ', '').replace('Bucuresti - ', '');
  
  const charMatch = title.match(/Animator\s(.*?)\sPetreceri/i);
  const charName = charMatch ? charMatch[1].trim() : 'Personaj Magic';
  
  const tplIdx = (f + charName).length % templates.length;
  let raw1 = templates[tplIdx];
  let raw2 = templates[(tplIdx + 1) % templates.length];
  let raw3 = templates[(tplIdx + 2) % templates.length];
  
  hVar += 1;
  let p1 = spin(raw1, hVar).replace(/\{LOC\}/g, loc).replace(/\{CHAR\}/g, charName);
  hVar += 1;
  let p2 = spin(raw2, hVar).replace(/\{LOC\}/g, loc).replace(/\{CHAR\}/g, charName);
  hVar += 1;
  let p3 = spin(raw3, hVar).replace(/\{LOC\}/g, loc).replace(/\{CHAR\}/g, charName);
  
  let p4 = spin(templates[hVar % templates.length], hVar * 7).replace(/\{LOC\}/g, loc).replace(/\{CHAR\}/g, charName);
  
  let p5 = "Detalii importante: spectacolele cu " + charName + " la " + loc + " beneficiază de o prezență 100% interactivă. Magia este vitală din punct de vedere ludic aducând micuților un mod inedit prin implicarea repetată în dinamica spectacolului. Sunați relaxați pentru programări la agenția SuperParty la numărul vizibil.";

  const finalProse = '<p>' + p1 + '</p>\n\n<p>' + p2 + '</p>\n\n<p>' + p3 + '</p>\n\n<p>' + p4 + '</p>\n\n<p>' + p5 + '</p>';

  const marker = '<section class="zona-detail"';
  const hVal = (f+charName).split('').reduce((a,c)=>a+c.charCodeAt(0),0)%5;
  const titles = [
    'Ghid complet pentru petreceri cu ' + charName + ' în ' + loc,
    'Animatori ' + loc + ' — Cum chemi personajul ' + charName,
    loc + ' și SuperParty — Rezervă-l pe ' + charName + ' la aniversare',
    'Experiențe reale de la petreceri cu ' + charName + ' în ' + loc,
    charName + ' in ' + loc + ' - De ce suntem alegerea optimă'
  ];
  
  let newHtml = "\n<!-- UNIQUE-SPINTAX -->\n" +
"<section class=\"zona-detail\" style=\"padding:2.5rem 0;background:rgba(255,255,255,0.02)\">\n" +
"  <div class=\"container\" style=\"max-width:820px\">\n" +
"    <h2 style=\"font-size:1.2rem;font-weight:800;color:var(--text-primary,#fff);margin-bottom:1rem\">" + titles[hVal] + "</h2>\n    " +
finalProse.replace(/\n\n/g, '\n    ') + "\n" +
"  </div>\n" +
"</section>\n";

  if (c.includes(marker)) {
    c = c.replace(/<!-- UNIQUE-(?:PROSE|SPINTAX).*?-->[\s\S]*?<\/section>/g, '');
  } else if (c.includes('UNIQUE-PROSE-MARKER')) {
    c = c.replace('UNIQUE-PROSE-MARKER', '');
  }
  
  c = c.trim() + '\n\n' + newHtml.trim() + '\n';
  
  fs.writeFileSync(fp, c, 'utf8');
  updated++;
  if(updated % 100 === 0) process.stdout.write(updated + '/' + files.length + '\n');
}

console.log('✅ Spintax inserat complet pe ' + updated + ' pagini!');
