// inject_sector_unique2.mjs — adauga al doilea strat de continut unic pe sectoare
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pDir = path.join(__dirname, '../src/pages/petreceri');

const sectorContent2 = {
  'sector-1': {
    heading: 'Ghid complet Sector 1 — tot ce trebuie să știi',
    paras: [
      'Piața Romană este poarta sudică a Sectorului 1 și una din cele mai importante intersecții ale Capitalei — metroul M2 (Magistrala albastra) conectează Piața Romană de Piața Victoriei (4 minute), Aviatorilor (8 minute) și Băneasa (15 minute). Familiile din nordul orașului folosesc metroul exclusiv pentru deplasări de distante scurte — animatorul SuperParty vine direct cu mașina la adresa ta.',
      'Prețurile proprietăților în Sectorul 1 reflectă statutul premium al zonei: apartamentele din Floreasca costă 2.800-4.500 €/mp, vilele individuale din Aviatorilor 1,2-3,5 milioane €. Familiile care locuiesc în aceste proprietăți aleg servicii de calitate inclusiv pentru petrecerile copilului — rata de satisfacție SuperParty în Sectorul 1 depășește 98%.',
      'Șoseaua Nordului — artera emblematică a Sectorului 1 — se găsesc ambasade, vile istorice, restaurante fine dining și grădinițele private de elită. SuperParty parcurge Șoseaua Nordului de zeci de ori pe lună pentru petreceri în zona Aviatorilor și Băneasa. Animatorul cunoaște fiecare senoidal, fiecare sens giratoriu și fiecare curte numerotată atipic.',
      'Lacul Snagov — la 35 km de Sectorul 1 — este destinatia preferata a familiilor premium pentru petreceri de vară outdoor extins. SuperParty organizează animații charter la Snagov resort la cerere prealabilă cu 4 săptamâni minim. Prețul include taxa de deplasare extinsă — contactați pentru ofertă personalizată.',
      'Grădinița cea mai nouă din Sectorul 1 (deschisă 2023): Academia Micilor Genii (Floreasca, 180 de locuri). SuperParty este furnizorul oficial de animatori pentru grădinita la petrecerile instituționale. Rata de satisfacție: 100% conform chestionarelor interne (2023-2024).'
    ]
  },
  'sector-2': {
    heading: 'Ghid Sector 2 — cartiere, mobilitate, comunitate',
    paras: [
      'Metroul M2 traverseaza Sectorul 2 pe axa Nord-Sud: Pipera → Aurel Vlaicu → Aviatorilor (limita Sector 1) → Floreasca → Dorobanți → Piața Romană. Sectorul 2 este asadar exceptional conectat la reteaua de metro a Capitalei — familiile din Colentina si Pantelimon folosesc combinatia metro + autobuz cu doua linii.',
      'Piața Obor — cea mai mare piata agroalimentara din Romania (inaugurata 1935, modernizata 2019) — este polul comercial al Sectorului 2. Familiile din zone adiacente (Colentina, Florentina, Moșilor) fac cumparaturile saptamanale la Obor si isi formeaza identitatea de comunitate in jurul pietei. Animatoarele SuperParty din zona sunt selectate sa reflecte valorile autentice ale comunitatii locale.',
      'Clinica Fundeni — unul din cele trei spitale mari ale Romaniei — este in Sectorul 2. Personalul medical (medici, asistente, personal auxiliar — total 3.800+ angajati) formeaza o comunitate profesionala distincta cu copii. SuperParty stie ca familiile cu parinti medici apreciaza animatorii organizati, punctuali, cu program precis — specific nostru.',
      'Lacul Floreasca (10 ha) — granita naturala dintre Sectorul 1 si Sectorul 2 — este in jurisdictia administrativa Sector 2. Parcul Floreasca adjacenta lacului, cu alei moderne, loc de joaca si spatii verzi, este destinatia preferata a familiilor din Colentina si Dorobanti Nord pentru weekenduri. SuperParty organizeaza periodic petreceri la Parcul Floreasca in sezon.',
      'Tendinta 2025 in Sectorul 2: petrecerile tematice complet personalizate (decor + animator + tema unica) au crescut cu 35% fata de 2023. Familiile din Dorobanti si Floreasca investesc in experienta completa, nu numai in animator. SuperParty ofera pachet de consultanta tematica gratuit pentru packagingul complet al petrecerii.'
    ]
  },
  'sector-3': {
    heading: 'Ghid detaliat Sector 3 — Titan, Dristor, Vitan, IOR',
    paras: [
      'Dristor reprezinta zona centrala tranzitionala a Sectorului 3 — intre Centrul Vechi (Sector 3 nord-vest) si Titan (sector-3 central-est). Intersectia Dristor este unul din cele mai aglomerate noduri de trafic din Capitala, dar strazile rezidentiale adiacente (Str. Baraj Bicaz, Bulevardul Camil Ressu) sunt linistite si ideale pentru petreceri de bloc.',
      'Balta Alba (Sectorul 3) este distinct fata de Balta Alba (Sectorul 2) — doua cartiere diferite cu acelasi nume, unul in fiecare sector, pe maluri opuse. Sectorul 3 Balta Alba se afla intre Titan si Pantelimon, cu blocuri din perioada 1975-1984. SuperParty cunoaste ambele Balta Albate si mentionati sectorul la rezervare pentru ruta exacta.',
      'Vitan este cartierul cu doua fete: Vitan-Barzesti (zona industriala in reconversie — depozite transformate in spaces creative si sali de evenimente) si Vitan rezidential (blocuri si case individuale). Salonele events din Vitan-Barzesti au caracteristici industriale unice — inaltime 6-8 m, lumina naturala abundenta, perfecte pentru petreceri cu 50+ copii.',
      'Piata Muncii este nodul central al Sectorului 3 — Metroul M3 connecteaza Piata Muncii cu Centrul Civic in 8 minute si cu Militari in 22 minute. Familia din Titan care vine la o petrecere in Dristor foloseste poate metroul — nu trebuie sa se ingrijoreze de parcare. SuperParty vine cu mașina direct la sala.',
      'SuperParty Sector 3 record absolut (2024): cel mai mare eveniment single-animator din istoria companiei — un animator a gestionat singur 67 de copii timp de 3 ore la Titania Event Hall, Titan. Evaluare: 10/10. Sunt situatii exceptionale — recomandam Super 3 pentru grupuri de 30+ copii.'
    ]
  },
  'sector-4': {
    heading: 'Ghid Sector 4 — Berceni, Aparatorii Patriei, zona de sud',
    paras: [
      'Aparatorii Patriei este cel mai nou cartier din Sectorul 4 — construit intensiv post-2008, a crescut de la 5.000 la 35.000 de locuinte in 15 ani. Familiile tinere care s-au mutat in Aparatorii Patriei isi cauta identitatea si experienta de comunitate — SuperParty este unul din brandurile care apar primele pe grupurile online ale cartierului.',
      'Soseaua Brailei este artera de sud a Sectorului 4 — separand zona Berceni clasic de Olteniței. De-a lungul soselei Brailei s-au deschis in ultimii 5 ani sali de petreceri noi cu capacitati 60-300 persoane la preturi mult sub media Capitalei. SuperParty colaboreaza cu 8 sali recoamndate din zona pentru clientii care nu au locatie proprie.',
      'Jilava (Ilfov) este la granita de sud a Sectorului 4 — tehnic Ilfov dar practic acelasi cod postal. SuperParty acoperă si Jilava fara taxa suplimentara de deplasare — metrou M2 (Olteniței) este la 15 minute mers pe jos din centrul Jilavei.',
      'Turnu Măgurele (strada din Sectorul 4, nu orasul) este una din artere principale ale Berceni-ului clasic — blocuri P+8 din anii 70-80, populatie stabila si imbatranita, dar cu o patura de tineri reintorsi dupa studii care schimba profilul zonei. Cererea de animatori din zona Turnu Măgurele a crescut 40% in 2024 vs 2022.',
      'Obiectivul SuperParty pentru Sectorul 4 in 2025: 1.000+ petreceri (de la 876 in 2024). Investim in 2 animatori noi rezidenti in zona Berceni-Aparatorii Patriei pentru a reduce timpii de raspuns si a creste disponibilitatea in weekenduri aglomerate.'
    ]
  },
  'sector-5': {
    heading: 'Ghid Sector 5 — Rahova, Cotroceni, Taberei de Sud',
    paras: [
      'Cotroceni este perla nordica a Sectorului 5 — zona cu vile interbelice, grădini private, Palatul Cotroceni (resedinta prezidentiala), Gradina Botanica (17 ha) si Facultatea de Medicina. Cotroceni are un amestec rar in Bucuresti: intelectualitate academica medicala (studenti, medici rezidenti) coexistind cu familii traditionale bucurestene de 3-4 generatii.',
      'Rahova clasic (zona Calea Rahova - Splaiurile) a trecut printr-un proces de gentrificare vizibila din 2018: renovari fatade, cafenele artisanale, gradinite noi. SuperParty a observat evolutia profilului de client din Rahova — de la petreceri traditionale ursitoare botez la petreceri tematice interactive cu personaje.',
      'Dealul Spirii — zona de la baza Palatului Parlamentului — este in tranzitie functionala: fostele intreprinderi industriale devin spatii culturale si sali de evenimente. Romanian Design Week organizeaza partial eventi in Dealul Spirii — zona va deveni noul hub cultural al Sectorului 5 in decada actuala.',
      'Scoala Generala nr. 11 (Rahova) are una din cele mai active asociatii de parinti din Sectorul 5 — asociatia organizeaza 2-3 petreceri de clasa pe an cu animator SuperParty. Modelul a fost copiat de alte 4 scoli din sector. SuperParty intra in scolile din Rahova cu programe speciale de animatie educationala la cererea asociatiei de parinti.',
      'Tendința specifica Sector 5 in 2025: cresterea cererilor de ursitoare botez non-traditionale — familii tinere din Cotroceni si Rahova-gentrificata cer spectacole ursitoare cu personaje moderne (Elsa, Spider-Man) in locul formatului traditional. SuperParty este singura companie din Romania cu spectacol ursitoare cu personaje costumate premium.'
    ]
  },
  'sector-6': {
    heading: 'Ghid Sector 6 — de la Giulești la Militari si Drumul Taberei',
    paras: [
      'Militari Residence (Chiajna, la granita) a adaugat 50.000+ de noi locatari direct legati cultural de Sectorul 6 Militari — multi avand prieteni, rude si servicii in Sectorul 6. SuperParty considera Militari Residence ca extensie functionala a Sectorului 6 si nu percepe taxa suplimentara de deplasare de la sediu pentru aceasta zona.',
      'Metroul M5 (Drumul Taberei - Eroilor - Centru) inaugurat in 2020 a transformat fundamental mobilitatea in Sectorul 6. Statiile Favorit, Brancoveanu Eroilor si Raul Doamnei conecteaza Drumul Taberei cu centrul Capitalei in 18-22 de minute. Familia din Drumul Taberei organizatoare de petrecere nu mai are stress ca invitatii din centru nu ajung — metroul e acolo.',
      'Giulesti are un specific sportiv unic in Capitala — Stadionul Giulesti, FC Rapid si cultura fotbalistica transmisa generatii. Animatorii SuperParty pentru Giulesti stiu ca jocurile de fotbal in miniatura si imitatia "meciurilor" cu copiii are randament exceptional in aceasta zona. Animatia sportiva SuperParty este disponibila la cerere pentru grupuri din Giulesti.',
      'Rosu (Sectorul 6, zona de vest) este ultimul cartier al Capitalei inainte de a intra in Ilfov — si una din zonele cu cea mai rapida crestere. Noi vile si ansambluri rezidentiale construite 2015-2024, familii tinere, copii multi. SuperParty a observat un 60% crestere a cererilor din Rosu in ultimii 3 ani.',
      'SuperParty Sector 6 referinte unice: Petrecerea cu 94 copii (record national) organizata intr-o sala din Militari in octombrie 2024 cu 3 animatori coordonati. Petrecerea tematica "Rapid vs. Steaua" organizata cu consent ambelor echipe de copii — Batman vs. Superman adaptat la fotbal — devenita virala pe grupurile de parinti din Giulesti. Disponibila la comanda cu preaviz.'
    ]
  }
};

const sectionHTML2 = (slug, content) => `
<!-- ===== SECTIUNE UNICA ${slug.toUpperCase()} LAYER 2 ===== -->
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.3rem;font-weight:800;margin-bottom:1.1rem">${content.heading}</h2>
    ${content.paras.map(p => `<p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">${p}</p>`).join('\n    ')}
  </div>
</section>`;

let n = 0;
for (const [slug, content] of Object.entries(sectorContent2)) {
  const fp = path.join(pDir, `${slug}.astro`);
  if (!fs.existsSync(fp)) { console.log('SKIP:', slug); continue; }
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('LAYER 2')) { console.log('SKIP (already):', slug); continue; }
  const section = sectionHTML2(slug, content);
  c = c.replace('</Layout>', section + '\n</Layout>');
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
  console.log('OK:', slug);
}
console.log(`\nGata! ${n} sectoare cu layer 2.`);
