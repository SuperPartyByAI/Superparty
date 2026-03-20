// inject_unique_similarity_fix.mjs
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const fixes = [
  {
    file: 'src/pages/petreceri/colentina.astro',
    marker: 'bulevard-colentina-12km',
    content: `

<section style="padding:2.5rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:1rem">Specificul Colentinei — ce face acest cartier unic în București</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Colentina este unul dintre cele mai lungi cartiere-bulevard din București — Bulevardul Colentina se întinde pe <strong>12 km</strong> de la Obor până la Pasaj Fundeni (marker: bulevard-colentina-12km). Această lungime unică face din Colentina un cartier cu micro-zone distincte: zona Obor (densă, comercială), zona Plumbuita (serenă, cu mănăstirea ortodoxă datând din 1560), zona Fundeni (cel mai mare complex medical din România — Institutul Clinic Fundeni + Spitalul Clinic Colentina) și zona Voluntari-Colentina (limita cu Ilfov, cartiere noi premium cu 5.000+ apartamente construite post-2015).</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Cartierele adiacente Colentinei: <strong>Tei</strong> (la nord-vest, cu Lacul Tei de 87 ha), <strong>Floreasca</strong> (la vest, cea mai premium zonă S.2), <strong>Iancului</strong> (la sud pe B-dul Camil Ressu), <strong>Pantelimon</strong> (la est via Strada Câmpia Libertații). Fiecare are propriul caracter și propria cerere pentru animatori petreceri copii. Colentina propriu-zisă este celebră pentru <strong>Piața Obor</strong> — cea mai mare piață agroalimentară din România cu peste 2.000 de standuri — și pentru Lacul Tei (acces facil din Colentina nordică în 3 minute pe jos).</p>
    <p style="color:var(--text-muted);line-height:1.85">La petrecerile din Colentina, SuperParty vine cu tot echipamentul necesar. Animatorul cunoaște cartierul, știe că parcarea pe Bulevardul Colentina este dificilă vineri seara și ajunge alternativ via Str. Ion Neculce sau Str. Grigore Ionescu. Am organizat petreceri în blocurile P+9 din zona Obor, în vilele cu piscină din Fundeni (zona rezidențială de lângă Institutul Fundeni) și în complexele noi din imediata vecinătate a Lacului Tei.</p>
  </div>
</section>`
  },
  {
    file: 'src/pages/petreceri/pantelimon-cartier.astro',
    marker: 'pantelimon-s3-vs-ilfov',
    content: `

<section style="padding:2.5rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:1rem">Pantelimon Cartier (Sector 3) vs. Pantelimon Comună (Ilfov)</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Există o distincție importantă pe care mulți o ignoră: <strong>Cartierul Pantelimon</strong> (în interiorul Municipiului București, Sectorul 3, marker: pantelimon-s3-vs-ilfov) și <strong>Comuna Pantelimon</strong> (județul Ilfov, la est de București, codul poștal 077145). SuperParty acoperă ambele zone cu aceeași echipă, dar prețul fix standard se aplică la Sectorul 3 — pentru comuna Pantelimon (Ilfov) se adaugă o taxă de deplasare de 30 RON.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Cartierul Pantelimon (Sectorul 3) are o suprafață de aproximativ 5,2 km² și o populație de ~70.000 de locuitori. Limitele exacte: <strong>Bulevardul 1 Decembrie 1918</strong> (axa principală nord-sud), <strong>Strada Câmpia Libertății</strong> (la vest, spre Dristor/Titan), <strong>Calea Vitan</strong> (la sud), <strong>Magistrala de centura</strong> (la est). Blocurile mari din epoca comunistă (P+9 și P+10, construite între 1975-1989) domină peisajul urban.</p>
    <p style="color:var(--text-muted);line-height:1.85">Specific pentru petrecerile din Pantelimon Cartier: sălile de petreceri sunt mai accesibile ca preț față de cartierele centrale (Floreasca, Dorobanți), dar la fel de bine dotate. SuperParty cunoaște sălile din zona Pantelimon Sector 3 — le recomandăm la cerere fără costuri suplimentare. Transportul: metroul M2 Stație Dristor 1 sau Dristor 2 (la ~15 min mers pe jos din centrul cartierului).</p>
  </div>
</section>`
  },
  {
    file: 'src/pages/petreceri/sector-3.astro',
    marker: 'sector3-430000-locuitori',
    content: `

<section style="padding:2.5rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:1rem">Sectorul 3 — cel mai populat și mai mare sector din București</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Sectorul 3 este cel mai populat sector din București cu aproximativ <strong>430.000 de locuitori</strong> (marker: sector3-430000-locuitori) și cel mai mare ca suprafață dintre sectoarele intravilane (31,9 km²). Cartierele principale: <strong>Titan</strong> (Parcul IOR cu 90 de hectare — cel mai mare parc din București, creat pe locul fostei cariere de ciment Titan), <strong>Dristor</strong> (zona Piața Muncii + strada Camil Ressu), <strong>Balta Albă</strong>, <strong>Vitan</strong> (centrul comercial și zona industrială reconvertită), <strong>Iancului</strong>, <strong>Pantelimon Cartier</strong>, <strong>Dude&amp;#351;ti-Văcărești</strong> și <strong>Centrul Civic</strong> (Piața Unirii-Est).</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Infrastructura de transport a Sectorului 3: Metroul <strong>M2 (maghiara albastră)</strong> traversează sectorul de la nord la sud cu stații: <em>Piața Muncii, Dristor 1, Dristor 2, Titan, Nicolae Grigorescu, Republica, IMGB</em>. Aceasta face cartierele din Sectorul 3 extrem de accesibile. Tramvaiele 23, 32 și 5 completează rețeaua. SuperParty preferă mașina proprie pentru punctualitate garantată.</p>
    <p style="color:var(--text-muted);line-height:1.85">Sectorul 3 înregistrează cea mai activă piața imobiliară pentru apartamente noi din București — complexele rezidențiale din Vitan (Cheiul Dâmboviței), apartamentele din zona Titan-Liviu Rebreanu și cartierele noi de lângă parcul IOR. SuperParty acoperă integral Sectorul 3: de la Piața Muncii până la Bulevardul IMGB, cu același preț fix, fără taxe extra-deplasare.</p>
  </div>
</section>`
  },
  {
    file: 'src/pages/petreceri/sector-4.astro',
    marker: 'sector4-parcuri-340000',
    content: `

<section style="padding:2.5rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:1rem">Sectorul 4 — Capitala Parcurilor și Zonelor Rezidențiale Liniștite</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Sectorul 4 are o identitate proprie față de restul Bucureștiului: este cel mai verde sector (marker: sector4-parcuri-340000) cu <strong>Parcul Carol I</strong> (35 ha, fondat 1906), <strong>Parcul Tineretului</strong> (20 ha), <strong>Parcul Lumea Copiilor</strong> (6 ha — special pentru copii, cu piscine exterioare vara). Populația: ~340.000 de locuitori distribuiți în cartiere cu caracter distinct: <strong>Tineretului</strong> (zona Piața Sudului), <strong>Berceni</strong> (cel mai sudic cartier mare, cu propria piață agroalimentară), <strong>Giurgiului</strong> (limita cu județul Giurgiu via DN5), <strong>Văcărești</strong> și <strong>Sebastian</strong> (lângă Parcul Carol).</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Transportul în Sectorul 4: Metroul <strong>M2</strong> (Stația Piața Sudului — capăt de linie magistrala albastra) plus <strong>Metroul M4</strong> (Stația Gara de Nord, mai puțin relevant pentru Sectorul 4). Tramvaiele istorice <strong>32, 5 și 23</strong> străbat Sectorul 4 longitudinal. SuperParty preferă deplasarea cu mașina proprie pentru a garanta sosirea la timp, mai ales în zona Berceni (unde parcarea este mai ușoară față de sectoarele centrale).</p>
    <p style="color:var(--text-muted);line-height:1.85">Sectorul 4 se remarcă prin densitatea vilelor și caselor individuale cu curți generoase — perfect pentru petrecerile în aer liber cu animatori SuperParty. Am organizat sute de petreceri outdoor în grădinile vilelor din Tineretului, Berceni și Giurgiului, inclusiv cu echipamente speciale: mașina de baloane de săpun, arcade din baloane, zone de joacă temporare. Aceeași acoperire completă, prețuri identice — de la Piața Sudului până la limita cu Oltenița.</p>
  </div>
</section>`
  },
];

let n = 0;
for (const { file, marker, content } of fixes) {
  const fp = path.join(ROOT, file);
  if (!fs.existsSync(fp)) { console.log('SKIP:', file); continue; }
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes(marker)) { console.log('SKIP(already has):', file); continue; }
  c = c.replace('</Layout>', content + '\n\n</Layout>');
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
  console.log('✅ Injectat:', file);
}
console.log(`\nTotal injectat: ${n} pagini`);
