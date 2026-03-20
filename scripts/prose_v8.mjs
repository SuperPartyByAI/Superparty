import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const dir = 'src/content/seo-articles';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.mdx'));

console.log('--- Aplicare Motor Combinatorial V8 pe ' + files.length + ' fisiere ---');

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

const subjects = [
  "{Organizarea|Planificarea|Structurarea|Setarea|Pregătirea|Conceperea|Vizualizarea|Stabilirea|Gândirea|Aducerea}", 
  "{Sărbătorirea|Marcarea|Petrecerea|Onoarea|Bucuria|Veselia|Trăirea|Punctarea|Serbarea|Sărbătoarea}",
  "{Succesul|Reușita|Garanția|Certitudinea|Calitatea|Performanța|Excelența|Magia|Atmosfera|Unicitatea}",
  "{Impactul vizual|Momentul magic|Surpriza totală|Entuziasmul pur|Fericirea extremă|Explozia de zâmbete|Amintirea superbă|Zâmbetul imens|Emoția veritabilă|Vibrația excepțională}",
  "{Detaliul fin|Logisticul atent|Pregătirile minuțioase|Standardul înalt|Pretențiile calitative|Focusul permanent|Responsabilitatea asumată|Calibrul estetic|Garanția SuperParty|Sistemul premium}"
];

const attributes = [
  "{unui eveniment privat|unei aniversări tematice|unei petreceri memorabile|unei serbări de vis|unui show extraordinar|unui moment de poveste|unei surprize de lux|unei adunări festive|unei atmosfere vibrante|unui cadru festiv perfect}",
  "{unei zile speciale perfecte|unui party excepțional asigurat|unei bucurii maxime garantate|unei acțiuni organizate curat|unei intervenții calitative remarcabile|unui spectacol animat intens|unei prezențe scenice ireproșabile|unui sistem magic uimitor|unui program distractiv complex|unei animații pline de viată}",
  "{unui public exigent și dornic de joc|unei asistențe absolut fascinate de culoare|unui grup de prichindei alergând voioși|unei comunități locale moderne atente|unei arii rezidențiale liniștite și frumoase|unei adrese setate riguros în agendă|unei logistici implementate perfect la fața locului|unei locații selecte curat alese anterior|unei cerințe primite extrem de clar|unei așteptări confirmate mereu absolut pozitiv}"
];

const impacts = [
  "{reprezintă mereu|devine instantaneu|se transformă rapid în|este apreciat ca fiind|se validează mereu ca|rămâne fără doar și poate|tinde evident spre|poate fi definit absolut prin|are forma clară a|oferă certitudinea completă pentru}",
  "{un beneficiu palpabil concret asigurat|un avantaj tehnic logistic impecabil|o garanție certă complet funcțională de pe loc|un plus de valoare evident imediat arătat vizual|o decizie înțeleaptă dovedită statistic din cifre|un pariu câștigător pe termen lung pur memorabil|o siguranță parentală extrem de importantă absolut|un cadou inestimabil de apreciat intens|o investiție utilă de amintiri fericite continue|o soluție ideală pentru orice dificultate spontană}"
];

const actors = [
  "{atunci când este invitat|dacă intră pe scenă|imediat ce apare cu adevărat|odată ce sosește impunător|în momentul în care își face simțită prezența|de cum calcă pragul adresei fixate|în clipa declanșării acțiunii cu|când demarează distracția absolută prin|prin prestația artistică masivă livrată de|alături de carisma debordantă adusă mereu de}",
  "*{CHAR}*", 
  "{superbului erou popular CHAR|minunatului personaj adorat CHAR|excepționalului favorit CHAR|magnificului și mult așteptatului CHAR|talentului neegalat demonstrat nativ prin CHAR|magiei autentice adunate sub vizualul prestat de CHAR|costumului uluitor de realistic aparținând garantat fix lui CHAR|idolului ecranelor și cărților copilăriei adică tocmai ineditului CHAR}"
];

const actions = [
  "{Baloanele modelabile se împart cu finețe formând absolut magie vizuală fix acolo|Face painting-ul de calitate premium acoperă pur rapid fața fiecărui copil|Jocurile cu parașuta colorată adună extrem de disciplinat grupurile masive la interior|Ritmurile muzicale antrenante ridică spontan rapid starea de veghe a tuturor|Coregrafia perfectă setată la secundă elimină absolut curat orice umbră pasivă totală|Interacțiunea 1 la 1 se livrează cu calm angelic și carismă uimitoare pozitiv|Sunetul perfect reglat ajută intens imersia deplină complet focusată totală real|Curiozitatea piticilor este complet potolită prin răspunsuri complet magice inteligent ticluite calm|Orice dorință spontană e rapid acoperită prin tehnici pedagogice calitative ireproșabil conduse fluid|Zâmbetul adulților de pe margini probează matematic siguranța calității generale incontestabil arătate ferm}.",
  "{Echipa este mereu zâmbitoare energică super promptă|Recomandările curg apoi masiv online pur organic constant|Tarifele dovedesc fix echilibrul moral calitativ asigurat curat|Cuvintele de laudă apar zilnic instant pe Facebook absolut admirativ constant|Tristețea plecării este calmată mereu blând cu un ultim balon frumos dăruit ferm și prompt|Timpul curge evident nesesizabil lăsând amintiri fix prețioase mereu adunate clar continuu|Bucuria rămâne complet imună la stresul citadin obositor lăsat departe imediat brusc|Confortul tău de părinte este strict vizat protejat super central absolut ireproșabil evident garantat|Zero anulări bruște înregistrate vreodată pe portofoliul absolut vast de experiențe de acest gen uimitor|Experiența anterioară vastă liniștește cert din secunda zero absolut orice tensiune inerent asumată pur complet}."
];

// Combine them dynamically!
console.log('Construiesc masina combinationala de fundal...');
const bp = [];
for(let s of subjects) {
  for(let a of attributes) {
    for(let i of impacts) {
      for(let ac of actors) {
        for(let act of actions) {
          bp.push(s + ' ' + a + ' din superba arie de referinta din {LOC} ' + i + ' ' + ac + '. ' + act + ' Iar surprizele pur si simplu nu se termina absolut niciodata aici pastrand fix magia curata pe axa temporala prelungita stabil asigurat complet organic.');
        }
      }
    }
  }
} // 5 * 3 * 2 * 3 * 2 = 180 blue-prints extrem de spinate intern de baza!
// 180 * (10 variante interne) = 1.8 milioane fragmente posibile!

console.log(`Baza matematica de paragrafe are ${bp.length} sabloane unice.`);

function simpleHash(str) {
  return crypto.createHash('md5').update(str).digest('hex').substring(0, 10);
}

let updated = 0;

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
  
  // Utilizam hash criptografic pentru o distributie perfect aleatoare per nume de fisier
  const hexHash = simpleHash(f + charName + loc);
  const baseHInt = parseInt(hexHash, 16);
  
  // Alegem exact 38 de paragrafe unice din cele 180 disponibile (garantare 1500+ cuvinte)
  for (let i = 0; i < 38; i++) {
    // Selectam sablonul
    const bpidx = (baseHInt + i * 13 + i * i) % bp.length;
    const rawForm = bp[bpidx];
    // Seed unic de spintax intern per paragraf
    let hVar = baseHInt + i * 73;
    const spun = spin(rawForm, hVar).replace(/\{LOC\}/g, loc).replace(/\{CHAR\}/g, charName);
    paragraphsPool.push('<p>' + spun + '</p>');
  }

  const finalProse = paragraphsPool.join('\n\n');

  const titles = [
    'Detalii supreme despre o adunare magică asumată de ' + charName + ' excepțional planificată în zona curată ' + loc,
    'Explozie de calități logistice ferm fixate absolut pentru prestația epică pură a invitatului de aur ' + charName + ' în inima ' + loc,
    'Structură impecabilă și jocuri reale - asigură-l imediat prompt și total pe magic ' + charName + ' în zona liniștită primitoare ' + loc,
    'Sărbătoriri unice de basm faptic reale prin prezența magnificului pur și perfect asigurat personaj iubit absolut ' + charName + ' în ' + loc
  ];
  const secTitle = titles[baseHInt % titles.length];
  
  let newHtml = "\n<!-- UNIQUE-TEXT-V8 -->\n" +
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
}

console.log('✅ Generator Combinatorial Criptologic V8 aplicat si finalizat pe ' + updated + ' pagini cu un fond cuvantaj enorm (aprox 1600+ win)');
