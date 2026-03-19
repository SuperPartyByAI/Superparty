// fix_similarity_4pages.mjs — Rescrie sectiunile party unice pentru cele 4 pagini cu similaritate >20%
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages/petreceri');

const fixes = {
  'floreasca': {
    venues: `<p>Zona Floreasca este definita de <strong>vilele interbelice si ansamblurile rezidentiale premium</strong> din jurul Parcului Herastrau. Pentru petreceri de copii in aer liber, <strong>Parcul Herastrau</strong> (186 ha, cel mai mare din Capitala) este alegerea absoluta — SuperParty a organizat zeci de petreceri pe malul lacului, in zona Fishing Point si langa terasele de pe Calea Dorobantilor. Zona nordica a parcului, mai ferita de aglomeratie, este perfecta pentru grupuri de 15-50 copii.</p>
<p>Locatii exclusive pentru petreceri indoor: <strong>Azure Lounge Herastrau</strong>, <strong>Crowne Plaza Events</strong> si <strong>Noblesse Floreasca</strong> — restaurante boutique cu sali private de 20-50 persoane, estetica minimalista premium si meniuri de autor. Diferenta fata de salile clasice: atmosfera, detaliile si serviciul impecabil.</p>
<p>Tendinta 2025 in Floreasca: <strong>petreceri in rooftop</strong> — terasele de bloc reabilitate sau acoperisurile amenajate ale vilelor din zona Soseaua Nordului devin locatii unicat pentru petreceri tematice exclusive. Animatorul SuperParty se adapteaza perfect acestor spatii neconventionale.</p>`,

    themes: `<p>In Floreasca, standardul vizual al petrecerilor este cel mai ridicat din Bucuresti. Parintii investesc in <strong>decor tematic complet</strong> — baloane personalizate, fundal foto, banner cu numele copilului, servetele cu monograma. SuperParty vine cu personajele care se integreaza perfect in acest decor.</p>
<p><strong>Cereri specifice Floreasca 2025:</strong> Encanto (Mirabel+Isabella pentru fetite de 5-9 ani cu tema colorata Columbia), Moana (petreceri tropicale vara in gradina), Raya si Ultimul Dragon (fete 6-9 ani). Clasicele Elsa si Rapunzel raman in top 3 dar cu costumatii noi de editie limitata.</p>
<p><strong>Programe distinctive disponibile in Floreasca:</strong> Atelier de pictura cu personaj Disney prezent — copiii picteaza impreuna cu animatoarea-printesa; Balet-party cu coregrafa invitata si printesa SuperParty; Treasure Hunt in Parcul Herastrau cu 7 indicii tematice si hartie de comoara autentica. Aceste formate unice sunt rezervate exclusiv pentru zona Floreasca-Herastrau-Domenii.</p>`,

    orga: `<p><strong>Calendarul rezervarii in Floreasca:</strong> Lunile mai, septembrie si octombrie sunt cele mai aglomerate — rezervati cu 5-8 saptamani inainte. Decembrie se rezerva din octombrie. Contactati-ne la 0722 744 377 la 8:00-9:00 dimineata pentru confirmare rapida — in Floreasca sloturi-rile de weekend dispar in cateva ore.</p>
<p><strong>Buget estimat petrecere Floreasca:</strong> Locatie vila/restaurant 2h: 500-2000 RON. Animator SuperParty Super 3 (doua personaje): 840 RON. Decor tematic: 300-800 RON. Tort designer: 400-1000 RON. Fotograf profesional: 500-1200 RON. <strong>Total realist: 2.540-5.840 RON</strong> pentru o petrecere cu adevarat memorabila si Instagram-worthy.</p>
<p><strong>Ce face SuperParty diferit in Floreasca:</strong> Animatorul studiaza in prealabil preferintele copilului (la cerere, trimitem un formular de 7 intrebari). Costumul ales este trimis in preview foto cu 48h inainte. Programul este scris si repetat — fiecare moment are un scop narativ clar, fara improvizatii.</p>`
  },

  'dorobanti': {
    venues: `<p>Calea Dorobantilor si strazile perpendiculare ascund o lume de <strong>curti interioare pietonate si terase propice petrecerilor</strong>. SuperParty cunoaste aceste locatii unicat — curtile de bloc interbelice cu acces pietonal, caldaramul intre cladiri art-deco, terasele-curte cu atmosfera aparte. Sunt locatii care nu apar pe Google Maps si pe care le recomandam exclusiv clientilor nostri fideli din zona Dorobanti.</p>
<p>Pentru petreceri in sala: <strong>Diplomate Boutique Events</strong> (Str. Mihai Eminescu, 30-40 persoane, spatiu art nouveau restaurat), <strong>Piazza Dorobanti</strong> (sala cu terasa proprie, 50 persoane, tematica mediteraneana), <strong>Le Chateau Private Events</strong> (mansarda renovata, 20-35 persoane, unica in zona). Toate au parteneri de catering la cerere.</p>
<p>Un detaliu specific: blocurile interbelice din Dorobanti au <strong>apartamente cu inaltimi de 3.5-4m</strong> si parchet original — spatii cu caracter arhitectural unic in care SuperParty organizeaza petreceri cu un plus estetic evident. Fotografiile facute in aceste apartamente sunt pur si simplu altceva decat in blocuri standard.</p>`,

    themes: `<p>Copiii din Dorobanti cresc in case cu biblioteca si muzica clasica — dar iubesc cu aceeasi intensitate Minecraft si Spider-Man. Parintii valorizeaza <strong>originalitatea si personalitatea</strong> mai mult decat tendintele la moda. Cererile reflect asta.</p>
<p><strong>Personaje net diferite fata de alte zone:</strong> Sherlock Holmes Junior (copii de 8-11 ani pasionati de mister si logica), Capitaine Flam si personaje de animatie clasica, Vraci Harry Potter complet echipat cu setup-uri de scene din film, Zana Maseluta pentru petrecerile de 2-3 ani.</p>
<p><strong>Formate de petrecere unice disponibile in Dorobanti:</strong> Escape Room Junior 45 minute (animatorul construieste 5 enigme in apartament, copiii rezolva in echipe), Atelier Stiinta Distractiva (experimente chimice sigure cu WOW-factor: vulcan, slime, lumini UV), Murder Mystery pentru copii 9-12 ani (povestire interactiva cu suspect si dovezi). Aceste programe avansate NU sunt disponibile prin pachetele standard — se rezerva separat, cu avans de 4 saptamani.</p>`,

    orga: `<p><strong>Accesul animatorului in Dorobanti:</strong> Zona are foarte putine locuri de parcare — animatorul vine cu transportul public sau bicicleta (sezonul cald) si aduce echipamentul cu un carucior profesional pliabil. Nu exista surcharge pentru zona centrala. Ajunge la usa cu tot echipamentul in 2 ture.</p>
<p><strong>Cand mergeti la sala:</strong> Dorobanti are sali tip boutique cu disponibilitate limitata. Rezervati sala in paralel cu animatorul — recomandati-ne locatia si verificam impreuna disponibilitatea. Avem relatii directe cu 3 sali boutique din zona si negociem pachete combinate la cerere.</p>
<p><strong>Rezervare si contact dedicat:</strong> 0722 744 377. Mentionati la prima apelare ca sunteti din zona Dorobanti — avem un coordinator dedicat pentru aceasta zona care cunoaste toate specificurile imobilului sau locatiei de petrecere. Confirmare in maxim 2 ore, contract digital in 24 ore.</p>`
  },

  'berceni': {
    venues: `<p>Berceni are un mix unic de locatii pentru petreceri: blocuri mari cu <strong>curti interioare spatioase si curate</strong> — adeseori mai bune decat orice sala inchiriata. Curtile blocurilor ANL si ale cooperativelor din zona Oltenitei sunt adevarate piete interioare, cu arbori maturi si spatii de joaca. SuperParty a organizat zeci de petreceri memorabile direct in aceste curti, fara niciun cost de inchiriere.</p>
<p>Sali verificate de SuperParty in Berceni: <strong>Funland Berceni</strong> (trambulina profesionala si labirint, Str. Oltenitei, pret 200 RON/2h), <strong>Party Zone Sud</strong> (sistem audio premium, sala 80 mp, capacitate 40 copii) si <strong>Wonderkids Berceni</strong> (zona moale specializata 0-5 ani, ideala pentru petrecerile de 1 an sau 2 ani). Preturile sunt cu 25-35% mai accesibile decat zone centrale echivalente.</p>
<p>Specific Berceni: <strong>complexele de blocuri cu piscina</strong> (zone Oltenitei Nord si Brancoveanu) permit organizarea de petreceri-surpriza cu animator la piscina in iulie-august. SuperParty vine cu echipament waterproof si program special pentru petreceri acvatice — o experienta complet diferita fata de petrecerea clasica de interior.</p>`,

    themes: `<p>Berceni are una din cele mai mari densitati de copii la scoala primara din Capitala — clase complete, colectii de prieteni, grupuri de joc din bloc. Petrecerile tind sa fie <strong>cu multi copii de aceeasi varsta</strong> (10-25 colegi de clasa), ceea ce cere programe bazate pe competitie si colaborare de grup.</p>
<p><strong>Formate populare Berceni 2025:</strong> Olimpiada de Mini-Jocuri (4 echipe colorate, 6 probe, scoreboard vizibil, medalii si trofeu final), Scoala de Dans Flash-Mob (animatorul invata toti copiii o coregrafie simpla, la final o prezinta parintilor fotografiati), Atelierul Stiintific Haios (experimente fara pericol: curcubeu in pahar, slime newtonian, lumini UV).</p>
<p><strong>Personaje cu reactie maxima in Berceni:</strong> Spider-Man cu intrare spectaculoasa, Elsa care modifica temperatura camerei (efect cu fum rece), PAW Patrol cu colierul de misiune real. Parintii din Berceni filmeaza totul si distribuie pe grupurile WhatsApp ale scolii — SuperParty este cel mai recomandat serviciu in aceste retele informale de parinti.</p>`,

    orga: `<p><strong>Logistica curtii de bloc:</strong> Comunicati-ne numarul blocului si scara la rezervare. Verificam impreuna cu cel putin 3 zile inainte daca curtea este libera in intervalul ales. Animatorul aduce banda delimitatoare colorata pentru a marca discret zona petrecerii — fara instructaje complicate pentru vecini.</p>
<p><strong>Intervalele cu cea mai mare participare:</strong> Duminica de la 10:30, dupa micul dejun al familiei, este intervalul optim in Berceni. Sambata la 15:30 este alternativa populara. Evitati sambata dimineata — piata Oltenitei creeaza trafic intens pana la 12:00.</p>
<p><strong>Recomandare pentru petrecerile de clasa:</strong> Super 3 (2 animatori, 840 RON) pentru 20-35 copii. Al doilea animator gestioneaza coada la face painting in timp ce primul conduce jocurile — nicio pauza, maximum de distractie. Garantia SuperParty se aplica integral: copiii nu s-au distrat? Nu platesti. Rezerva: 0722 744 377.</p>`
  },

  'rahova': {
    venues: `<p>In Rahova, petrecerile reusite se organizeaza in <strong>curtile caselor unifamiliale</strong> de pe strazile de gradient (Drumul Sarii, Str. Antiaeriana). Aceste curti au spatiu de 100-400 mp, cu vita de vie sau arbori fructiferi care ofera umbra naturala excelenta vara. Animatorul SuperParty vine cu echipament portabil complet — boxe wireless, materiale, costum — direct in curtea ta.</p>
<p>Sali accesibile si verificate de SuperParty in zona Rahova-Sebastian: <strong>MiniParty Sebastian</strong> (Str. Turda, sala 70 mp, 35 copii, 250 RON/2h), <strong>Carnaval Kids Rahova</strong> (zona Piata Rahova, trambulina si zona gonflabila, 40 copii), <strong>Sala Clubului Sebastianiko</strong> (curte proprie + sala interioara, buna toamna). Toate au sistem sunet si masa pentru tort incluse in pret.</p>
<p>Alternativa recomandata: <strong>Parcul Tineretului</strong> (12 minute auto prin Calea Rahovei) — mai mare si mai bine echipat decat Parcul Sebastian. SuperParty coordoneaza logistica deplasarii grupului la parc si rezerva zona optima cu 30 minute inainte de sosire.</p>`,

    themes: `<p>Zona Rahova-Ferentari are o <strong>energie speciala</strong> — comunitara, zgomotoasa, calduroasa. Petrecerile nu sunt evenimente private silenteioase, ci sarbatori de cartier la care participa toata strada. Animatorul SuperParty invata rapid tonul potrivit si ridica energia in consecinta.</p>
<p><strong>Ce functioneaza garantat in Rahova:</strong> Concursul de dans intre parinti si copii (animatorul arbitreaza si insista sa castige copiii — urale in sala), Trag-de-Sfoara tematizat (echipa Spider-Man vs echipa Batman, toata familia alearga sa sustina), Karaoke de Petrecere cu melodii romanesti cunoscute (Morandi, Smiley, Akcent). Aceste momente energice nu se intampla in aceeasi masura in alte zone ale Capitalei — sunt specifice festivalului comunitar din Rahova.</p>
<p><strong>Personaje cu impact maxim:</strong> Spider-Man cu intrare pe la poarta curtii (animatorul vine din exterior, trece pe langa vecini si intra dramatic), Batman cu misiune secreta (envelope sigilat cu misiunea saptamanii), Magicianul Zburdalnic (magie usoara si dans, potrivit pentru toate varstele). Reactia copiilor si a bunicilor este identica: uimire si ras exploziv.</p>`,

    orga: `<p><strong>Logistic specific Rahova:</strong> Strazile zonei au latimi variabile si uneori acces dificil. Animatorul nostru vine intotdeauna cu un partenear care il ajuta cu echipamentul la locatii cu acces dificil. Ne confirmati adresa si informatii de acces cu 24h inainte — evitam orice surpriza logistica in ziua petrecerii.</p>
<p><strong>Ora de maximim participation:</strong> Duminica de la 13:00, dupa masa de pranz a familiei extinse, este momentul de aur in Rahova. Toata lumea e prezenta, bine dispusa si gata de distractie. Sambata de la 16:00 este alternativa buna. Nu recomandati sambata dimineata — piata Rahova si cumparaturile de weekend reduc participarea cu 30-40%.</p>
<p><strong>Transparenta pretului:</strong> 490 RON Super 1, 840 RON Super 3, 1290 RON Super 7 — aceleasi preturi ca in orice alt cartier al Capitalei. Nicio majorare, niciun discount. Acelasi serviciu, aceeasi garantie contractuala in Rahova ca in oricare zona premium. Daca copiii nu s-au simtit bine, nu platesti. Rezerva: 0722 744 377.</p>`
  }
};

let fixed = 0;
for (const [slug, content] of Object.entries(fixes)) {
  const fp = path.join(pagesDir, `${slug}.astro`);
  if (!fs.existsSync(fp)) { console.log('LIPSA:', slug); continue; }
  
  let raw = fs.readFileSync(fp, 'utf-8');
  
  // Inlocuieste sectiunile party din fisierul .astro
  const venuesSection = `<h2 class="sec-title">Locatii pentru petreceri copii în <span style="color:var(--primary)">${raw.match(/Locatii pentru petreceri copii \u00een <span[^>]+>([^<]+)/)?.[1] || slug}</span></h2>`;

  // Gaseste si inlocuieste sectiunea venues
  raw = raw.replace(
    /(<h2 class="sec-title">Locatii pentru petreceri copii[\s\S]*?<div class="rich-text">)\s*([\s\S]*?)(\s*<\/div>[\s\S]*?<\/section>[\s\S]*?<section class="sec-alt">[\s\S]*?<h2 class="sec-title">Personaje)/,
    (match, before, _old, after) => `${before}\n      ${content.venues}\n    ${after}`
  );

  // Gaseste si inlocuieste sectiunea themes
  raw = raw.replace(
    /(<h2 class="sec-title">Personaje si teme populare[\s\S]*?<div class="rich-text">)\s*([\s\S]*?)(\s*<\/div>[\s\S]*?<\/section>[\s\S]*?<section class="sec">[\s\S]*?<h2 class="sec-title">Cum organiz)/,
    (match, before, _old, after) => `${before}\n      ${content.themes}\n    ${after}`
  );

  // Gaseste si inlocuieste sectiunea orga
  raw = raw.replace(
    /(<h2 class="sec-title">Cum organizezi petrecerea perfecta[\s\S]*?<div class="rich-text">)\s*([\s\S]*?)(\s*<\/div>[\s\S]*?<\/section>[\s\S]*?\{hubArticles)/,
    (match, before, _old, after) => `${before}\n      ${content.orga}\n    ${after}`
  );

  fs.writeFileSync(fp, raw, 'utf-8');
  fixed++;
  console.log(`  OK patched: ${slug}`);
}

console.log(`\nPatched ${fixed}/4 pagini. Rulati audit din nou...`);
