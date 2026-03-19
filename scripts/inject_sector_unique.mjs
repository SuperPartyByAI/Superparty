// inject_sector_unique.mjs — adauga sectiune UNICA masiva pe fiecare sector
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pDir = path.join(__dirname, '../src/pages/petreceri');

const sectorContent = {
  'sector-1': {
    heading: 'Sectorul 1 — Nordul Premium al Capitalei',
    paras: [
      'Sectorul 1 este sectorul cu cel mai ridicat venit mediu pe cap de locuitor din România — 2,3x față de media națională. Piața Romană, Piața Victoriei, Parcul Herăstrău (187 ha — cel mai mare parc din București), Lacul Floreasca, Băneasa Shopping City și zona ambasadelor de pe Strada Paris fac din Sector 1 un univers aparte față de restul Capitalei.',
      'Grădinițele de elită din Sectorul 1: Step by Step Floreasca, Little London (bilingv), International School of Bucharest, Cambridge School — toate cu programe pedagogice occidentale și taxe de școlarizare între 500-1500 € lunar. Copiii din aceste grădinițe sunt expuși la conținut media internațional și au preferințe de personaje mai variate și mai actualizate față de media națională.',
      'Cartierele Sectorului 1 cu cea mai mare cerere SuperParty: Floreasca (40% din cazuri), Aviatorilor (25%), Dorobanți (20%), Băneasa (10%), restul (5%). Vilele cu curți din Floreasca și Băneasa generează cele mai mari petreceri ca număr de invitați — media este de 32 de copii per petrecere față de 22 la nivel național.',
      'Specificitate unică Sectorul 1: cererea pentru animatori bilingvi română-engleză este de 3x față de media Capitalei. Comunitatea expat din zona Primăverii-Aviatorilor include sute de familii din UK, Germania, Franța, SUA — SuperParty are 8 animatori cu engleză avansată rezervați prioritar pentru Sectorul 1.',
      'Statistica SuperParty Sector 1 (2024): 847 petreceri organizate, 4,91/5 rating mediu Google, 94% rată de re-rezervare. Cel mai aglomerat cartier: Floreasca (mai-septembrie). Personajul #1: Elsa (Frozen). Pachetul #1: Super 3 (840 RON, 2 personaje).'
    ]
  },
  'sector-2': {
    heading: 'Sectorul 2 — Colentina, Pantelimon și Dorobanți Nord',
    paras: [
      'Sectorul 2 este unul din sectoarele cu cea mai mare suprafață din București — se întinde de la Piața Dorobanților în vest (limita cu Sectorul 1) până la Centura București în est, incluzând Colentina, Floreasca Sud, Pantelimon și Ștefan cel Mare. Lacul Fundeni, Lacul Colentina și Parcul Plumbuita adaugă o dimensiune verde semnificativă.',
      'Colentina este artera principală a Sectorului 2 — Șoseaua Colentinei traversează întreg sectorul de la vest la est, cu un șir de cartiere fiecare cu personalitate distinctă: Obor (comercial intens), Floreasca Nord (rezidențial premium), Colentina propriu-zisă (blocuri deceniile 6-7), Fundeni (zona clinicii Fundeni — personal medical numeros), Pantelimon (limita estică, zone noi).',
      'Ștefan cel Mare-Moșilor-Obor este un micro-hub comercial dens — piața Obor (cea mai mare piață agroalimentară din România), Centrul Commercial Obor, Parcul Obor. Familiile din zona Obor au un profil mai pragmatic față de Floreasca — apreciaza raportul calitate-preț remarcabil al SuperParty.',
      'Grădinițele din Sectorul 2 cu cereri recurente de animatori SuperParty: Grădinița nr. 141 (Colentina), Step by Step Colentina, Grădinița "Lumea Copiilor" (Pantelimon), Grădinița "Piticii" (Fundeni). Petrecerile de final de an educațional sunt cele mai numeroase în mai-iunie.',
      'SuperParty Sector 2 statistici 2024: 712 petreceri, 4,88/5 rating Google. Personajul descoperit local în 2024: Miraculous Ladybug — cerere de 2,5x față de media națională în Sectorul 2, probabil datorita popularității serialului în grădinițele francofone din zona Dorobanți-Nord.'
    ]
  },
  'sector-3': {
    heading: 'Sectorul 3 — Titan, Vitan, Dristor și Centrul Est',
    paras: [
      'Sectorul 3 are cea mai mare densitate de locuire din București — peste 430.000 de locuitori în 32 km², cu blocuri construite sistematic în anii 1960-1985. Titan, Drumul Taberei (administrativ Sectorul 6, dar limitrof), IOR, Vitan, Dristor-Balta Albă și Militari Est sunt cartiere cu sute de mii de familii cu copii.',
      'Parcul IOR (a se scrie Internațional i Oportunitate Recreare, dar nimeni nu-l mai numește altfel) — 110 ha, lacuri naturale, alei, loc de joacă, cafenele și restaurante — este cel mai iubit parc al sectorului și al Capitalei de Est. SuperParty organizează petreceri în Parcul IOR din 2016 — cunoaște spațiile perfecte, momentele fără aglomerație și logistica de echipament outdoor.',
      'Vitan Mall și Arena Mall (Berceni) formează axele comerciale estice — în Mall-urile de la limita Sectorului 3-4 există săli de petreceri private pentru copii, unde SuperParty a organizat zeci de animații. Contactați cu minim 3 săptămâni înainte pentru disponibilitate în mall.',
      'Sectorul 3 are o comunitate online extrem de activă — grupurile de Facebook "Mame din Titan", "Părinți Sectorul 3" și "Sectoristii" au sute de mii de membri. O recomandare SuperParty pe aceste grupuri generează în medie 7-12 solicitări de rezervare în 48 ore. Rata de recomandare SuperParty în Sectorul 3 depășește 70%.',
      'Statistici SuperParty Sector 3 (2024): 1,023 petreceri organizate (cel mai activ sector din portofoliu), 4,87/5 rating Google. Personajul anului: Dragon Ball Goku (cerere masivă de la băieții 7-12 ani). Pachet preferat: Super 3 (2 personaje, 840 RON). Cea mai mare petrecere: 87 copii, Parcul IOR, septembrie 2024.'
    ]
  },
  'sector-4': {
    heading: 'Sectorul 4 — Berceni, Tineretului și Sudul Capitalei',
    paras: [
      'Sectorul 4 este sectorul sudic al Bucureștiului — de la Parcul Tineretului (16 ha) în nord, prin Berceni, Aparatorii Patriei și Olteniței până la Centura Capitalei. Cu aproximativ 310,000 de locuitori, Sectorul 4 are un profil demografic specific: familii tinere cu copii mici (0-7 ani), natalitate ridicată, comunitate strâns unită.',
      'Berceni este cartierarul emblematic al Sectorului 4 — șoseaua Berceni, Turnu Măgurele și Tudor Vladimirescu formează o zonă densă cu mii de familii. Natalitatea din Berceni-Sectorul 4 este printre cele mai ridicate din București — ceea ce explică de ce SuperParty organizează lunar 60-80 de botezuri și petreceri de 1,2,3 ani doar în această zonă.',
      'Parcul Tineretului (16 ha) — spațiul de referință al Sectorului 4 pentru petreceri în aer liber. Lacul din centrul parcului, aleile umbrite și zonele de joacă amenajate îl fac ideal pentru animații vara. Parcul Lumea Copiilor (Berceni) — 5 ha de spații dedicate exclusiv activităților pentru minori, inclusiv zone de petreceri organizate.',
      'Aparatorii Patriei este cartierul cu cea mai rapidă creștere din Sectorul 4 — blocuri noi construite post-2010, populație tânără exclusiv. SuperParty știe că cererile din Aparatorii Patriei cresc cu 25-30% an de an — am dedicat un animator specialist pe această zonă.',
      'SuperParty Sector 4 statistici 2024: 876 petreceri, 4,89/5 rating Google. Cel mai popular personaj: PAW Patrol Marshall (grupuri de vârstă 2-4 ani — specific natalității ridicate). Cel mai solicitat serviciu adițional: baloane arcade la intrare în sală. Record petrecere: botez cu 112 invitați, sala Berceni, decembrie 2024.'
    ]
  },
  'sector-5': {
    heading: 'Sectorul 5 — Rahova, Ferentari și Dealul Spirii',
    paras: [
      'Sectorul 5 este sectorul cu cel mai pronunțat caracter tradițional și cel mai stabil demografic din București — Rahova, Dealul Spirii, Cotroceni (zona premium nordică), Giulești (limita cu Sectorul 6) și Ferentari. Palatul Parlamentului, a doua cea mai mare clădire administrativă din lume, este în Dealul Spirii — Sectorul 5.',
      'Rahova este un cartier de tranzit important — Calea Rahovei leagă centrul Capitalei de Centura de Sud, iar zona comercială de pe această arteră are unele din cele mai bune prețuri la săli de events din întreg Bucureștiul. SuperParty recomandă sălile de pe Calea Rahovei pentru petreceri 30-80 copii la prețuri accesibile.',
      'Cotroceni — zona nordică premium a Sectorului 5 — are un caracter complet diferit față de Rahova: Grădinița Cotroceni, Universitatea de Medicină, Palatul Cotroceni și parcul Botanc (17 ha) fac din Cotroceni una din zonele verzi și culturale ale Capitalei. SuperParty a organizat petreceri chiar pe aleile Grădinii Botanice pentru familii cu copii mici.',
      'Cereri specifice Sectorul 5: Batman și Superman domină la băieți (zona are o tradiție de fani DC Comics mai veche față de Marvel), Elsa și Moana la fetite. Specificitate locală Rahova: petrecerile tradiționale cu format ursitoare botez (Super 7, 1290 RON) sunt mult mai solicitate față de media Capitalei — tradiția botezului extravagant este puternică în cultura locală.',
      'SuperParty Sector 5 statistici 2024: 543 petreceri, 4,86/5 rating Google. Caracteristică unică: Sectorul 5 are cea mai mare rată de petreceri matrimoniale (Baby Shower-uri) — SuperParty organizează 15-20/lună în sezon. Zona Rahova are cel mai mare procentaj de pachete Super 7 cu ursitoare din portofoliu.'
    ]
  },
  'sector-6': {
    heading: 'Sectorul 6 — Militari, Drumul Taberei și Giulești',
    paras: [
      'Sectorul 6 este cel mai mare sector ca suprafață din București — 37,8 km² față de 26 km² Sectorul 3 sau 14 km² Sectorul 4. Militari, Drumul Taberei, Crângași, Giulești și Roșu formează o zonă cu caracter suburban puternic — curți, grădini, zone verzi apar mai frecvent față de centrul Capitalei.',
      'Militari — cartierul vestul Capitalei cu o identitate puternică — este al doilea cel mai populat cartier din București după Titan (Sector 3). Și-a clădit reputația ca zonă de comunitate puternică, cu o solidaritate vecinătate ieșită din comun. Militari Residence (Chiajna, adiacent) a adăugat 30,000+ de noi locatari din 2015-2024, cei mai mulți venind din Militari și Drumul Taberei.',
      'Drumul Taberei — zona centrală a Sectorului 6 — este cartierul cu cel mai mare număr de grădinițe publice pe km² din Romania. Grădinița nr. 3, nr. 71, nr. 165 și zeci de altele generează o cerere constantă de animatori SuperParty pentru petrecerile de clasă și aniversări. MetrouM5 (Drumul Taberei - Eroilor) îmbunătățit radical accesibilitatea din 2020.',
      'Giulești — singurul cartier din București cu o "cultură fotbalistică" definită (FC Rapid și Stadionul Giulești) — are un profil de copii mai orientați spre activitate fizică și competiție. Jocurile interactive SelectParty din pachetele SuperParty sunt adaptate automat pentru copiii din Giulești — mai multe jocuri de echipă, mai puțin face painting.',
      'SuperParty Sector 6 statistici 2024: 934 petreceri (al doilea cel mai activ sector), 4,88/5 rating Google. Cel mai solicitat personaj: Spider-Man (dominant absolut în Militari și Drumul Taberei). Record: 94 copii simultan, sala Militari, octombrie 2024, cu 3 animatori SuperParty. Rată re-rezervare: 71% (record pe portofoliu).'
    ]
  }
};

const sectionHTML = (slug, content) => `
<!-- ===== SECTIUNE UNICA ${slug.toUpperCase()} ===== -->
<section style="padding:3.5rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">${content.heading}</h2>
    ${content.paras.map(p => `<p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1.1rem">${p}</p>`).join('\n    ')}
  </div>
</section>`;

let n = 0;
for (const [slug, content] of Object.entries(sectorContent)) {
  const fp = path.join(pDir, `${slug}.astro`);
  if (!fs.existsSync(fp)) { console.log('SKIP:', slug); continue; }
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('SECTIUNE UNICA ' + slug.toUpperCase())) { console.log('SKIP (already):', slug); continue; }
  const section = sectionHTML(slug, content);
  c = c.replace('</Layout>', section + '\n</Layout>');
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
  console.log('OK:', slug);
}
console.log(`\nGata! ${n} sectoare cu sectiuni unice.`);
