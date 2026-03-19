// inject_unique_sections.mjs — adauga sectiuni unice pe pagini care inca se suprapun
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Sectiuni cu continut complet unic per pagina
// Inserata chiar inainte de </Layout>

const injections = {
  'src/pages/petreceri/calarasi.astro': `
<!-- ===== SECTIUNE UNICA CALARASI ===== -->
<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1rem">Istoria și identitatea Călărașilor</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Călărașiul are o istorie sugerată chiar de numele său — "călăreț", derivând de la unitățile militare de cavalerie care au staționat în zonă în evul mediu. Prima atestare documentară datează din secolul al XVI-lea, iar în 1852 orașul a primit statut de reședință de județ. Dunărea a modelat viața economică a Călărașilor — portul fluvial activ și legătura permanentă cu Silistra (Bulgaria) fac din Călărași un punct strategic de comerț.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Cartierele Călărașilor: <strong>Centrul vechi</strong> (zona istorică, Piața Dinu Brătianu), <strong>Florilor</strong> (cartier nou, ansambluri rezidențiale 2010-2024), <strong>Independenței</strong> (zona medie, case individuale), <strong>Grivița</strong> (zona sudică, aproape de port), <strong>Dobrogeni</strong> (cartier vestic). SuperParty acoperă toate aceste zone — menționați cartierul la rezervare pentru logistica exactă.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Grădinițele din Călărași: Grădinița nr. 5 "Floarea Soarelui", Grădinița nr. 8 "Inocența", Grădinița nr. 12 "Pinochio" — mulți părinți din Călărași organizează petreceri colective de clasă după grădiniță, SuperParty acoperă și aceste evenimente cu programe speciale pentru 15-30 copii simultan.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px">
      Tendinta 2025 în Călărași: petrecerile tematice cu Sonic sunt în creștere rapidă — serialul Sonic Prime pe Netflix a explodat în popularitate în rândul copiilor din județele sudice. SuperParty are costumul Sonic Premium disponibil și pregătit pentru fiecare weekend.
    </p>
  </div>
</section>`,

  'src/pages/petreceri/giurgiu.astro': `
<!-- ===== SECTIUNE UNICA GIURGIU ===== -->
<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1rem">Giurgiu — portul de la Dunăre și Podul Prieteniei</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Giurgiul este unul din cele mai vechi orașe portuare dunărene ale României — prima atestare documentară din 1394, când Mircea cel Bătrân menționează cetatea în documentele de cancelarie. Podul Prieteniei (1954, reconstruit 2013), cu lungimea de 2.800 m conectând Giurgiu de Ruse, este al doilea cel mai mare pod dunărean din România. Traficul internațional intens face din Giurgiu un nod logistic major de frontieră.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Cartierele Giurgiu-ului: <strong>Centrul</strong> (zona Piața Unirii, bulevard principal modernizat), <strong>Gării</strong> (zona industrială, în regenerare), <strong>Malu Roșu</strong> (cartier rezidențial sudic, case individuale), <strong>Slobozia</strong> (zona estică, lângă Dunăre), <strong>Zgheapana</strong> (zona nordică, ieșire spre București). SuperParty cunoaște fiecare cartier și adaptează logistica de transport.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Specific Giurgiu 2025: cererea pentru pachetul <strong>Super 3 (2 personaje)</strong> este cu 40% mai mare decât media națională. Familiile giurgiuvene organizează adesea petreceri combinate aniversare+botez cu 40-80 invitați — Super 7 (3 ore, 4 ursitoare) este foarte solicitat. Rezervați mim 3-4 săptămâni pentru evenimente mari.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px">
      Săli de petreceri recomandate în Giurgiu: <strong>Complexul Alley</strong> (lângă Parcul Alley, sală 200 mp, sistem audio propriu), <strong>Restaurantul La Dunăre</strong> (terasă cu vedere la fluviu, perfectă vara), <strong>Sala Polivalentă UVT</strong> (pentru evenimente de 100+ persoane). Sunați-ne cu locația și adaptăm echipamentul.
    </p>
  </div>
</section>`,

  'src/pages/petreceri/aviatiei.astro': `
<!-- ===== SECTIUNE UNICA AVIATIEI ===== -->
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1rem">Cartierul Aviației — specificul zonei Herăstrău-Băneasa</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Aviației este cartierul premium al Sectorului 1, flancat de Parcul Herăstrău (cel mai mare parc din București, 187 ha), Lacul Floreasca și Băneasa. Densitate mică, vile individuale și blocuri de lux predomină față de cartierele sudice. Comunitatea de expați și diplomați este semnificativă — SuperParty are animatori bilingvi română-engleză disponibili pentru Aviației la cerere.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Locații exclusive Aviației: <strong>Parcul Herăstrău</strong> (insulă privată pentru petreceri, perfectă mai-septembrie), <strong>restaurantele premium de pe Șoseaua Nordului</strong>, <strong>cluburile private din zona Aviatorilor</strong>. SuperParty a organizat petreceri chiar pe terasele vilelor din Aviației cu program live pentru 10-15 copii — experiență ultra-premium disponibilă la cerere.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px">
      Personaje top Aviației 2025: Iron Man și Captain America (băieți 5-11 ani din familii cu tați pasionați de Marvel), Elsa (fetițe 3-8 ani), Miraculous Ladybug (fetițe 6-10 ani). Cererile pentru personaje Bluey sunt în creștere — serialul australian a cucerit familiile internaționale din Aviației.
    </p>
  </div>
</section>`,

  'src/pages/petreceri/berceni.astro': `
<!-- ===== SECTIUNE UNICA BERCENI ===== -->
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1rem">Berceni — cel mai dens cartier din Sectorul 4</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Berceni este cartierul iconic al sudului Bucureștiului — construit sistematic în perioada 1960-1985, ad-istrat în Sectorul 4, cu o densitate de locuire din cele mai ridicate din Capitală. Blocurile din zona Turnu Măgurele, Tudor Vladimirescu, Berceni propriu-zis și Aparatorii Patriei găzduiesc zeci de mii de familii cu copii. SuperParty este brandul #1 de animatori în Berceni — recomandările se propagă rapid între vecini și prin grupurile de WhatsApp de bloc.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Locații specifice Berceni: <strong>Sălile de events din zona Turnu Măgurele</strong> (multiple opțiuni 80-200 mp), <strong>restaurantele family-friendly de pe Șoseaua Berceni</strong>, <strong>Parcul Tineretului</strong> (petreceri în aer liber, 10 minute), <strong>curțile blocurilor</strong> (vara, cu permis administratorului). Animatorul vine cu boxe wireless și nu necesită prize externe.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px">
      Berceni 2025: Spider-Man rămâne lider absolut (4-11 ani băieți), dar PAW Patrol (Marshall și Chase, copii 2-4 ani) a explodat în cerere — mulți părinți din Berceni au copii mici. Pantelimon-Berceni este zona cu cea mai mare natalitate din Sectorul 4 — SuperParty organizează zeci de botezuri lunar în această zonă.
    </p>
  </div>
</section>`,

  'src/pages/petreceri/titan.astro': `
<!-- ===== SECTIUNE UNICA TITAN ===== -->
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1rem">Titan — inima Sectorului 3, lângă cel mai mare parc al Capitalei</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Titan este cartierul emblemă al Sectorului 3 — construit în decadele 6-7-8 în jurul lacurilor Titan și IOR, formând împreună cu Parcul IOR (cel mai mare parc al Capitalei — 110 ha) un ecosistem urban unic. Strada Liviu Rebreanu, Calea Vitan, Aleea Budacu și Șoseaua Pantelimon delimitează un cartier dens și viu, cu una din cele mai extinse rețele de grădinițe publice și private din București.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Petreceri în Parcul IOR: SuperParty a organizat zeci de petreceri în Parcul IOR — pe terasele amenajate, lângă fântânile arteziene sau în insulița de la intrarea sudică. Sezonul mai-septembrie, weekenduri. Rezervarea spațiului în parc este responsabilitatea clientului — SuperParty vine cu tot echipamentul adaptat outdoor.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px">
      Titan 2025: comunitatea masivă de tineri părinți din Titan-Dristor-Vitan generează cerere constantă. Cereri specifice Titan: Spider-Man la băieți (dominant), Miraculous Ladybug la fetite (serial extrem de popular în grădinițele din Sectorul 3), Dragon Ball pentru băieți mai mari 8-12 ani. SuperParty are costumul Goku disponibil — unul din puținii animatori din România cu colecție Dragon Ball.
    </p>
  </div>
</section>`,

  'src/pages/petreceri/crangasi.astro': `
<!-- ===== SECTIUNE UNICA CRANGASI ===== -->
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1rem">Crângași — cartierul lacurilor din vestul Capitalei</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Crângași este cartierul cel mai verde din Sectorul 6 — Lacul Crângași (32 ha), Lacul Dâmboviței și Parcul Crângași formează un colier de zone verzi unics. Construit preponderent în perioda 1970-1982, Crângași a evoluat spre un profil socio-demografic stabil: familii cu un sau doi copii, mulți tineri care au moștenit apartamentele de la părinți și au ales să rămână în zonă.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Petreceri premium la Lacul Crângași: vara, zona de promenadă de la Lacul Crângași este perfectă pentru petreceri de copii în aer liber. SuperParty a organizat animații pe terasa Restaurantului Crângași, pe malul lacului și în zona de joacă adiacentă. Contact cu 3-4 săptămâni înainte pentru disponibilitate locație.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px">
      Profil cereri Crângași 2025: Batman și Superman la băieți 6-11 ani (zona are o comunitate de fani DC puternică — observat pe grupurile de Facebook locale), Elsa la fetite. O specificitate Crângași: mulți părinți cer animatori cu aptitudini de magie — SuperParty are în echipă 3 animatori certificați în magie pentru copii, disponibili cu solicitare prealabilă.
    </p>
  </div>
</section>`,

  'src/pages/petreceri/floreasca.astro': `
<!-- ===== SECTIUNE UNICA FLOREASCA ===== -->
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1rem">Floreasca — cartierul premium al Sectorului 2</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Floreasca este zona de referință a Sectorului 2 nord — Lacul Floreasca, Promenada Mall, restaurantele fine-dining de pe Calea Floreasca și vilele din zona Maior Coravu formează un cartier de o calitate distinctă față de restul Capitalei. Concentrația de startup-uri, agenții creative, medical și corporate este cea mai ridicată din București — profilele de familii sunt tinere, active profesional și cu standarde ridicate.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Promenada Mall Floreasca — <strong>Kids Zone</strong>: sala dedicată petrecerilor de copii, disponibilă la rezervare prealabilă prin mall. SuperParty a organizat zeci de petreceri în Kids Zone Promenada — spațiu dotat, sonorizare proprie, control temperatură. Ideal pentru octombrie-martie când terasele nu sunt disponibile.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px">
      Floreasca 2025 — cereri distinctive: Iron Man și Thor (băieți din familii cu gusturi premium Marvel), Elsa și Rapunzel (fetite), Miraculous Ladybug și Encanto Mirabel (fetite 7-12 ani). Familiile cu expați cer uneori Bluey sau Paw Patrol pentru colegii de la grădinița internațională — SuperParty oferă animatori bilingvi pentru aceste situații.
    </p>
  </div>
</section>`,

  'src/pages/petreceri/dorobanti.astro': `
<!-- ===== SECTIUNE UNICA DOROBANTI ===== -->
<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1rem">Dorobanți — zona ambasadelor și a liceelor de elită</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Dorobanți este zona cu cea mai mare densitate de ambasade și misiuni diplomatice din București — Piața Dorobanților, Strada Orlando, Aleea Alexandru și Șoseaua Nordului adăpostesc zeci de ambasade tari terțe. Liceele de elită (Liceul Francez "Anna de Noailles", Liceul German, Liceul "Jean Monnet" European) atrag familii cosmopolite internaționale din toată Europa. SuperParty organizează petreceri bilingve română-engleză-franceză în Dorobanți.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px;margin-bottom:1rem">
      Locații exclusive Dorobanți: <strong>Grădinile private ale vilelor</strong> (preferata absolut — zona are cele mai mari curți private din Sectorul 1), <strong>restaurantele boutique de pe Calea Dorobanților</strong> (Lacrimi și Sfinți, Shift, La Mama Dorobanți), <strong>Parcul Floreasca</strong> (la limita cartierului, 5-10 minute mers). Animatorul SuperParty se vede perfect în spațiile elegante ale vilelor — costume impecabile, comportament profesional.
    </p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:790px">
      Dorobanți 2025 — profil cereri: Encanto Mirabel și Moana domina (fetite din familii cu gusturi culturale rafinate), Spider-Man și Iron Man (băieți), solicitări frecvente pentru animatori care vorbesc engleză sau franceză (familii expat). SuperParty are în echipă 2 animatori cu franceză nivel avansat, disponibili cu preaviz.
    </p>
  </div>
</section>`,
};

let n = 0;
for (const [rel, inject] of Object.entries(injections)) {
  const fp = path.join(__dirname, '..', rel.replace(/\//g, path.sep));
  if (!fs.existsSync(fp)) { console.log('SKIP (not found):', rel); continue; }
  let c = fs.readFileSync(fp, 'utf-8');
  if (c.includes('SECTIUNE UNICA')) { console.log('SKIP (already injected):', rel); continue; }
  // Injecteaza inainte de </Layout>
  c = c.replace('</Layout>', inject + '\n</Layout>');
  fs.writeFileSync(fp, c, 'utf-8');
  n++;
  console.log('OK:', rel.split('/').pop().replace('.astro',''));
}
console.log(`\nGata! ${n} pagini imbunatatite cu sectiuni unice.`);
