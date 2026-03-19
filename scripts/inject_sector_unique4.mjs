// inject_sector_unique4.mjs — al patrulea strat unic pe sectoare (structura sociala, transport, specific events)
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pDir = path.join(__dirname, '../src/pages/petreceri');

// Sectii complet distincte, cu cuvinte cheie diferite
const layers4 = {
  'sector-1': `<section style="padding:2rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:.9rem">Transport Sector 1 — accesibilitate si mobilitate</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Autobuzele 131, 301, 331 strabat Sectorul 1 longitudinal. Troleibuzul 70 conecteaza Piata Victoriei cu Gara Baneasa. Magistrala M2 (Berceni-Baneasa, inaugurata 1989, extinsa 2016) are 6 statii in Sectorul 1: Parc Bazilescu, Jiului, Nufarul, Aurel Vlaicu, Aviatorilor, Baneasa. SuperParty ajunge in orice colt din Sectorul 1 in sub 35 minute din baza centrala.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Zonele cu accesul cel mai dificil in Sectorul 1: vilele din spatele Parcului Herastrau (stradute infundate, fara iesire), zona Primaverii fara acces auto dublu-directionat. SuperParty cunoaste rutele alternative si evita blocarile tipice din Sectorul 1 cu ajutorul aplicatiei Waze calibrata pe experienta locala.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Parcarea in Sectorul 1: zona Floreasca are parcari cu plata incepand cu 3 lei/ora. Animatorul parcheaza pe durata evenimentului (taxele se includ in deplasare). Pentru vilele cu parcare privata — animatorul necesita acces garantat la intrarea proprietatii cu echipamentul de animatie.</p>
  </div>
</section>`,

  'sector-2': `<section style="padding:2rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:.9rem">Transport Sector 2 — rute si acces animatori</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Soseaua Colentinei este artera principala a Sectorului 2 — si una din cele mai aglomerate din Capitala pe directia E-V in orele de varf. SuperParty programeaza sosirile la petreceri din Sectorul 2 cu minim 90 minute devansa fata de ora evenimentului pentru a absorbi eventualele blocaje pe Colentina.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Magistrala M2 traverseaza Sectorul 2 pe axul Pipera-Piata Romanä. Statia Pipera (business park-urile nordice), Aurel Vlaicu (zona corporatista), Aviatorilor (nexus cu Sectorul 1) sunt active 6:00-23:30 zilnic. Familiile din Pantelimon si Colentina Est folosesc autobuzele 101, 170, 471 pentru deplasari locale.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Accesul in Sectorul 2 din centru: Soseaua Stefan cel Mare si Soseaua Pantelimon sunt artere prioritare. Bulevardul Ferdinand (Sectorul 2 central-vest) este o optiune pentru evitarea ambuteiajelor. SuperParty cunoaste toate rutele alternative si ajunge punctual garantat.</p>
  </div>
</section>`,

  'sector-3': `<section style="padding:2rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:.9rem">Transport Sector 3 — magistrale si artere</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Magistrala M3 (Anghel Saligny - Preciziei) traverseaza Sectorul 3 pe axa E-V: Dristor 1, Dristor 2, Mihai Bravu, Piata Muncii, Timpuri Noi, Piata Unirii. Magistrala M1 (Magistrala Rosie) traverseaza Sectorul 3 la Iancului si Nicolae Grigorescu. Combinatia M1+M3 asigura o conectivitate rara — Titan este la 20 minute de orice punct al Capitalei.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Calea Vitan este coloana vertebrala a Sectorului 3 dinspre centru (Piata Unirii Est) pana in Vitan-Barzesti. Vitan Mall (mall-ul local, ~200 magazine) atrage familiile din intregul sector. SuperParty a organizat animatii in incinta Vitan Mall si in restaurantele adiacente.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Accesul in Titan: Soseaua Iancului (nord), Bulevardul 1 Decembrie 1918 (sud), Strada Fizicienilor (vest) si Soseaua Pantelimon (est) formeaza un perimetru care intretine in 2025 o dezvoltare rezidentiala activa. SuperParty foloseste aplicatia Waze pentru optimizare ruta in timp real la fiecare eveniment.</p>
  </div>
</section>`,

  'sector-4': `<section style="padding:2rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:.9rem">Transport Sector 4 — conexiuni si accesibilitate</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Sectorul 4 beneficiaza de Magistrala M2 pe limita nordica (Statia Berceni) si de multiple linii de tramvai (1, 10, 32) care conecteaza Berceni cu centrul in 25-40 minute. Statia de Metrou Aparatorii Patriei (M2) este cea mai frecventata statie sudica a Capitalei — 12.000+ calatori zilnic.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Soseaua Berceni este artera principala SV a Sectorului 4 — paralela cu Calea Serban Voda (Sectorul 4 NV). Autobuzele 104, 236, 338 asigura conexiunile est-vest in sector. SuperParty cunoaste fiecare artera secundara care evita ambuteiajele de pe Soseaua Berceni in orele de varf (17:00-19:00).</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Soseaua Olteniței (Sectorul 4 sud, limita cu Ilfov) este poarta de intrare dinspre Jilava si Bragadiru. Familiile din comunele Ilfov limitrofe care aleg Super Party aleg de obicei sali din Sectorul 4 (mai aproape, mai accesibile). Transport inclus gratuit din orice punct al Sectorului 4 si comunele limitrofe la maximum 15 km.</p>
  </div>
</section>`,

  'sector-5': `<section style="padding:2rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:.9rem">Transport Sector 5 — accesibilitate din toate punctele</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Magistrala M4 (inauguration 2011, prelungita 2014) trece prin nordul Sectorului 5: Statia Eroilor (nexus M4-M3-M1), Statia Izvor (sub Parcul Izvor si Palatul Parlamentului), Statia Opereta (Bd. Unirii). Magistrala conecteaza direct Rahova cu Centrul in 15 minute fara ambuteiaje.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Calea Rahovei este artera principala N-S a Sectorului 5 — de la Piata Natiunilor Unite (nord) pana la Bragadiru (Ilfov, sud). Traseul troleibuzului 66 si autobuzului 105 acoperă Calea Rahovei. SuperParty ajunge in orice punct de pe Calea Rahovei in sub 20 minute din baza centrala.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Accesul in Cotroceni (Sectorul 5 nord premium): Bulevardul Eroilor Sanitari, Strada Vasile Conta si Intrarea Armand Calinescu au restrictii auto — animatorul cunoaste locurile de parcare permisa si accesul pedestrian cu echipament. Unele vile Cotroceni necesita acces prestabilit cu portarul — informati SuperParty la rezervare.</p>
  </div>
</section>`,

  'sector-6': `<section style="padding:2rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:.9rem">Transport Sector 6 — Militari, Drumul Taberei, Giulesti</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Magistrala M5 (Eroilor-Drumul Taberei, 2020) a transformat radical accesibilitatea Sectorului 6. Cele 12 statii noi includ Favorit (Drumul Taberei centru), Brancoveanu Eroilor (Militari-vest), Salajan, Gorjului, Politehnica, Raul Doamnei, Orizont, Petrila, Laminorului si Drumul Taberei final. Timp de la centru: 22 minute.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:.8rem">Militari Residence (Chiajna, Ilfov) este conectata la Sectorul 6 prin Autobuzul 640 (serviciu frecvent, 6 curse/ora in orele de varf). Familiile din Militari Residence ajung in Militari PROPER in 8-12 minute. SuperParty acopera Militari Residence simultan cu Sectorul 6 — fara costuri suplimentare.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Soseaua Giulesti (Sectorul 6 nord) conecteaza Giulesti de Gara de Nord in 12 minute si de Piata Victoriei in 18 minute. Autobuzele 137 si 238 asigura conexiunile locale. Strazile rezidentiale din Giulesti-Sarbi sunt accesibile auto — SuperParty parcheaza imediat in fata adresei beneficiarului pentru descarcat rapid echipamentul de animatie.</p>
  </div>
</section>`
};

let n = 0;
for (const [slug, section] of Object.entries(layers4)) {
  const fp = path.join(pDir, `${slug}.astro`);
  if (!fs.existsSync(fp)) { console.log('SKIP:', slug); continue; }
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('LAYER 3') && c.includes('Transport Sector')) { 
    // Injecteaza layer 4 daca nu e deja acolo
    if (!c.includes('magistrale si artere') && !c.includes('conexiuni si accesibilitate') &&
        !c.includes('accesibilitate si mobilitate') && !c.includes('rute si acces') &&
        !c.includes('accesibilitate din toate') && !c.includes('Militari, Drumul Taberei, Giulesti')) {
      c = c.replace('</Layout>', section + '\n</Layout>');
      fs.writeFileSync(fp, c, 'utf-8');
      n++;
      console.log('OK layer4:', slug);
    } else {
      console.log('SKIP (has transport section):', slug);
    }
    continue;
  }
  c = c.replace('</Layout>', section + '\n</Layout>');
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
  console.log('OK:', slug);
}
console.log(`\nGata! ${n} sectoare patched.`);
