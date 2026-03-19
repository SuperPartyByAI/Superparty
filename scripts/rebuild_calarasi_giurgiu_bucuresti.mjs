// rebuild_calarasi_giurgiu_bucuresti.mjs — Rescrie complet cu continut RADICAL diferit
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pDir = path.join(__dirname, '../src/pages/petreceri');

const pages = {
  'calarasi': {
    title: 'Animatori Petreceri Copii Călărași | SuperParty',
    desc: 'Animatori copii în Călărași — 120 km de București, pe A2+DN3. Resedința județului la Dunăre. Pachete 490-1290 RON. Tel: 0722 744 377.',
    canonical: 'https://www.superparty.ro/petreceri/calarasi',
    city: 'Călărași',
    cityEN: 'Calarasi',
    h1: 'Animatori Petreceri Copii Călărași',
    dist: '120 km de București pe A2+DN3',
    river: 'Dunăre',
    population: '60.000',
    uniqueFact: 'Călărașiul este singurul județ din România fără autostradă proprie — dar SuperParty ajunge acolo indiferent de asta. Animatorul sosește la timp garantat sau serviciul e gratuit.',
    venues: 'Restaurantul Dunărea (cel mai mare din centrul orașului), Sala Polivalentă a orașului, sălile moderne din cartierele noi — Florilor, Independenței, Grivița. Parcul Dumbrava oferă spații verzi generoase pentru petreceri de vară în aer liber.',
    carProf: 'Familiile din Călărași au legături puternice cu tradițiile locale — animatorul SuperParty respectă aceste valori și adaptează programul la specificul vârstei și al grupului. Copiii din Călărași sunt sociabili și energici, apreciind jocurile de echipă și competițiile prietenoase.',
    chars: 'Spider-Man (favoritul absolut la băieți 4-11 ani), Sonic (popular mai ales 6-10 ani), Elsa (fetițe 3-8 ani). Comunitatea locala se uita la aceleasi seriale ca si Capitala — cereri frecvente pentru PAW Patrol Marshall si Bluey.',
    faq: [
      ['Organizați animatori în Călărași?', 'Da — SuperParty ajunge în Călărași indiferent de distanță. Avem experiență cu deplasările lungi și garantăm punctualitate. Sunați la 0722 744 377 cu data și adresa pentru confirmare în 30 de minute.'],
      ['Taxa de deplasare pentru Călărași?', 'Distanța de ~120 km pe A2+DN3 implică o taxă de deplasare care se stabilește transparent la rezervare. Comunicăm suma exactă înainte de confirmare — fără surprize. Animatorul pornește din timp pentru a ajunge cu 15 minute înainte de ora petrecerii.'],
      ['Unde organizăm petrecerea în Călărași?', 'Restaurantul Dunărea din centru, Sala Polivalentă, sălile moderne din cartierele noi (Florilor, Independenței) și parcul Dumbrava pentru vară. SuperParty se adaptează la orice spațiu ≥15 mp liberi.'],
      ['Ce personaje sunt disponibile?', 'Spider-Man, Sonic, Elsa — favoriții în Călărași. Colecția completă: 50+ personaje. Menționați preferința la rezervare și verificăm disponibilitatea costumului pentru data aleasă.'],
      ['Cu cât timp înainte rezervăm?', 'Minim 10-14 zile pentru Călărași (deplasare lungă). Pentru mai-septembrie rezervați cu 4-5 săptămâni în avans — weekendurile în sezon se ocupă rapid.'],
    ],
    content1: `<p>Călărașiul este reședința județului omonim situată pe malul drept al Dunării, la granița cu Bulgaria, la ~120 km de București pe A2+DN3. Cu o populație de peste 60.000 de locuitori, Călărașiul este un centru economic și cultural activ al Munteniei de est. Portul fluvial activ, industria tradițională și legăturile cu Bulgaria prin podul de la Fetești fac din Călărași un nod regional important.</p>
      <p>SuperParty vine în Călărași cu întreg arsenalul de animatori actori: costume premium autentice, boxe portabile wireless cu 8 ore autonomie, kit complet de face painting cu vopsele non-toxice, materiale pentru 15+ jocuri interactive, baloane modelate pentru fiecare copil, tatuaje temporare tematice și diplome magnetice personalizate. Totul vine la tine — tu nu pregătești nimic în plus.</p>`,
    content2: `<p>Animatorul SuperParty pentru Călărași este selectat special pentru deplasările lungi: energie susținută pe toată durata programului, indiferent de oboseala drumului. Antrenăm animatorii pentru petrecerile distante și asigurăm vehicul sigur și confortabil pentru transport.</p>
      <p>Comunitatea familiilor din Călărași este strâns unită — o recomandare SuperParty de la un vecin sau coleg se propagă rapid. Avem clienți fideli în Călărași care ne-au recomandat de zeci de ori. Calitatea serviciului în Călărași este identică cu cea din centrul Capitalei.</p>`
  },

  'giurgiu': {
    title: 'Animatori Petreceri Copii Giurgiu | SuperParty',
    desc: 'Animatori copii în Giurgiu — 65 km de București pe DN5, poarta spre Bulgaria. Pachete 490-1290 RON, garantie. Tel: 0722 744 377.',
    canonical: 'https://www.superparty.ro/petreceri/giurgiu',
    city: 'Giurgiu',
    cityEN: 'Giurgiu',
    h1: 'Animatori Petreceri Copii Giurgiu',
    dist: '65 km de București pe DN5',
    river: 'Dunăre',
    population: '55.000',
    uniqueFact: 'Giurgiu este cel mai sudic județ din România și are frontiera fluvială cu Ruse (Bulgaria) prin Podul Prieteniei — un pod dublu (rutier+feroviar) cu o lungime de 2,800 m. Copiii din Giurgiu știu că trăiesc într-un loc aparte și petrecerile lor merită tot pe măsură.',
    venues: 'Complexul de evenimente Dunărean (cel mai mare din județ), restaurantele tradiționale de pe bulevardul principal, Parcul Alley cu spații verzi și aleile amenajate ale malului Dunării. Zona centrală are mai multe săli de botez și aniversări recent renovate.',
    carProf: 'Giurgiu are o comunitate vie și caldă — județul cu cel mai pronunțat caracter sudic din România. Familiism puternic, petreceri mari cu familii extinse (bunici, nași, vecini). SuperParty recomandă pachetele cu 2 personaje pentru grupurile generoase specifice Giurgiu.',
    chars: 'Bluey (serial australian extrem de popular în Giurgiu — familiile îl urmăresc pe Disney+), Spider-Man, Elsa. Un specific local: băieții din Giurgiu urmăresc mult fotbalul și cer uneori personaje-fotbaliști sau costume inspirate din sport. Programul de jocuri SuperParty include întotdeauna jocuri de teamwork cu mingea.',
    faq: [
      ['Organizați animatori în Giurgiu?', 'Da — SuperParty acoperă tot Giurgiu: centrul orașului, cartierele Gării, Malu Roșu și toate zonele periurbane. Sunați la 0722 744 377 pentru confirmare disponibilitate în 30 minute.'],
      ['Taxa de deplasare pentru Giurgiu?', 'Giurgiu este la 65 km pe DN5 — drum drept și rapid. Taxa de deplasare se comunică transparent la rezervare. De obicei sub 80 RON dus-întors, communicate explicit înainte de confirmare.'],
      ['Unde organizăm petrecerea în Giurgiu?', 'Complexul Dunărean, restaurantele din centru și curțile generoase ale caselor tradiționale din Giurgiu sunt perfecte pentru petreceri. Parcul Alley este ideal vara. SuperParty vine oriunde ≥15 mp liberi.'],
      ['Ce personaje preferă copiii din Giurgiu?', 'Bluey este #1 în Giurgiu în ultimii 2 ani, depășind Spider-Man la cereri! Urmat de Spider-Man și Elsa. Comunitatea din Giurgiu este conectată la tendințele globale prin Disney+ și Netflix.'],
      ['Cât timp durează deplasarea animatorului?', 'Animatorul pornește cu minim 2 ore înainte și ajunge cu 15 minute înainte de ora rezervată. DN5 la Giurgiu este mult mai liber decât traficul din București — puncutalitate garantată.'],
    ],
    content1: `<p>Giurgiu este reședința județului omonim, cel mai sudic din România, pe malul stâng al Dunării față de Ruse (Bulgaria). Strada Victoriei, bulevardul principal, trece prin inima unui centru urban în modernizare accelerată. Cu ~55.000 de locuitori și un trafic intens cu Bulgaria (Podul Prieteniei — 2.800 m, dublu rutier și feroviar), Giurgiu este un hub regional activ.</p>
      <p>SuperParty a organizat zeci de petreceri în Giurgiu — în sălile de evenimente din centru, în curțile largi ale caselor tradiționale și în grădinile proprietăților. Știm că familiile din Giurgiu apreciază ospitalitatea generoasă și programele complete, fără momente goale. Animatorul nostru vine pregătit pentru grupuri de 10-60 copii, adaptat oricărui format.</p>`,
    content2: `<p>Un aspect specific Giurgiu: petrecerile locale sunt adesea adevărate reuniuni de familie extinsă — bunici, nași, vecini, colegi de clasă. Animatorul SuperParty știe să gestioneze perfect mulțimile diverse și să mențină toți copiii angrenați simultan, de la 2 la 12 ani, cu activități diferențiate pe grupe de vârstă.</p>
      <p>Programul SuperParty în Giurgiu: 15 minute instalare și primire copii, 120-180 minute program continuu (jocuri interactive → dans → baloane modelate → face painting → tatuaje → diplome), 15 minute finalizare și poze. Animatorul pleacă numai când toți copiii au primit diploma și fotografia cu personajul preferat.</p>`
  },

  'bucuresti': {
    title: 'Animatori Petreceri Copii București | SuperParty',
    desc: 'Animatori petreceri copii în tot Bucureștiul — cartiere, sectoare, mall-uri, parcuri. 8000+ petreceri organizate. Pachete 490-1290 RON. Tel: 0722 744 377.',
    canonical: 'https://www.superparty.ro/petreceri/bucuresti',
    city: 'București',
    cityEN: 'Bucuresti',
    h1: 'Animatori Petreceri Copii București',
    dist: 'tot Bucureștiul — toate cele 6 sectoare',
    river: 'Dâmbovița',
    population: '2.200.000',
    uniqueFact: 'SuperParty este liderul de piată pentru animatori petreceri copii în București — 8.000+ petreceri organizate în toate cele 6 sectoare, în toate cartierele mari și în zona Ilfov. Mai mult de 1.498 recenzii cu nota medie 4,9/5 pe Google Reviews.',
    venues: 'Mall-urile Promenada, AFI Cotroceni, Mega Mall (zone dedicated copii cu sali separate), sălile de petreceri moderne din Titan, Berceni, Militari, Floreasca, Colentina, parcurile mari (Tineretului, Herăstrău, Titan, Cișmigiu), curțile ansamblurilor rezidențiale.',
    carProf: 'Bucureștiul are cel mai divers profil de familii din România — expati, antreprenori, funcționari publici, medici, ingineri. Preferințele de personaje sunt extrem de variate: de la clasicul Spider-Man la personaje ultra-nișate din seriale Netflix recente. SuperParty acoperă tot spectrul.',
    chars: 'Spider-Man (lider absolut în București la băieți 4-11 ani), Elsa (fetițe 3-8 ani), Iron Man, Batman, Miraculous Ladybug, Encanto Mirabel, Bluey, PAW Patrol. Pentru Crăciun: Moș Crăciun autentic cu sanie și reni. Pentru Paști: Iepurașul de Paști.',
    faq: [
      ['Acoperiti toate sectoarele Bucurestiului?', 'Da — SuperParty acoperă toate cele 6 sectoare: Sector 1 (Aviației, Floreasca, Băneasa), Sector 2 (Colentina, Pantelimon, Dorobanți), Sector 3 (Titan, Dristor, Vitan), Sector 4 (Berceni, Tineretului), Sector 5 (Rahova, Dealul Spirii), Sector 6 (Militari, Drumul Taberei, Giulești).'],
      ['Cât de repede se confirmă rezervarea?', 'În 30 de minute — mereu. Sunați la 0722 744 377 sau scrieți pe WhatsApp cu: data, adresa exactă (sector + stradă), vârsta copilului, numărul de copii invitați. Contrac digital trimis în 24 ore.'],
      ['Organizați în mall și locații speciale?', 'Da — avem experiență cu sălile de petreceri din mall (Promenada Kids Zone, AFI, Mega Mall), restaurantele family-friendly, grădinițele private, și spațiile din ansamblurile rezidențiale. Sunați pentru detalii despre locația specifică.'],
      ['Există reduceri pentru petreceri în București?', 'Prețurile sunt fixe și transparente: Super 1 (490 RON), Super 3 (840 RON), Super 7 (1290 RON). Transport gratuit în tot Bucureștiul. Pentru botezuri sau evenimente de 100+ invitați sunați pentru ofertă personalizată.'],
      ['Ce face SuperParty diferit de alți animatori?', 'Singurul serviciu cu garantie contractuală scrisă — plată DUPĂ petrecere. Costume premium licențiate (nu imitații). Animatori actori de formație, nu hobbyiști. 8.000+ petreceri demonstrate prin recenzii reale verificate Google.'],
    ],
    content1: `<p>Bucureștiul este capitala României și cel mai mare oraș din țară — 2,2 milioane de locuitori oficiali, aproape 3 milioane în zona metropolitană extinsă. Cu 6 sectoare administrative, zeci de cartiere distincte, sute de ansambluri rezidențiale noi și mii de familii tinere cu copii, Bucureștiul este piața principală SuperParty și locul unde am perfecționat arta animatorilor de petreceri copii.</p>
      <p>SuperParty operează în București din 2015 și a organizat peste 8.000 de petreceri în toate colțurile Capitalei. Avem animatori disponibili zilnic (inclusiv luni-vineri pentru petreceri de zi) în toate sectoarele, sincronizați pe o platformă care asigură că niciodată nu suprarezervăm o dată. Garantăm prezența animatorului — dacă nu apare din vina noastră, returnam 100% din sumă și vă oferim o petrecere gratuită.</p>`,
    content2: `<p>Cartierele Bucureștiului au personalitate distinctă — SuperParty cunoaște fiecare zonă: Floreasca (familii premium, expati), Militari (familii tinere, ansambluri noi), Titan (zona central-estică, comunitate sudică), Berceni (familii tradiționale), Drumul Taberei (familii stabile, generații), Colentina (zona nordică, mixt rezidențial). Animatorul potrivit pentru fiecare cartier.</p>
      <p>Rezervare în București: cel mai rapid prin WhatsApp la 0722 744 377 — scrieți sectorul/cartierul, data și ora dorită, vârsta copilului și numărul de copii. În 30 de minute avem disponibilitate confirmată. Contractul digital ajunge prin email în 24 de ore. Plata se face PE LOC, DUPĂ petrecere — garanție contractuală scrisă unică în România.</p>`
  }
};

function buildPage(slug, d) {
  const schema = JSON.stringify({
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'Service',
        'name': d.h1,
        'provider': {'@type': 'LocalBusiness', 'name': 'SuperParty', 'telephone': '+40722744377'},
        'areaServed': d.city,
        'url': d.canonical
      },
      {
        '@type': 'FAQPage',
        'mainEntity': d.faq.map(([q,a]) => ({'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}}))
      },
      {
        '@type': 'BreadcrumbList',
        'itemListElement': [
          {'@type':'ListItem','position':1,'name':'Acasă','item':'https://superparty.ro'},
          {'@type':'ListItem','position':2,'name':'Animatori Petreceri Copii','item':'https://superparty.ro/animatori-petreceri-copii'},
          {'@type':'ListItem','position':3,'name':d.h1,'item':d.canonical}
        ]
      }
    ]
  });

  return `---
import Layout from '../../layouts/Layout.astro';
const schema = JSON.stringify(${schema});
---

<Layout
  title="${d.title}"
  description="${d.desc}"
  canonical="${d.canonical}"
  robots="index, follow"
  schema={schema}
>
<style>
  .hero-loc{padding:4rem 0 2rem;background:radial-gradient(ellipse at 30% top,rgba(255,107,53,.14) 0%,transparent 60%)}
  .h1-loc{font-size:clamp(1.7rem,4.5vw,2.7rem);font-weight:900;line-height:1.15;margin-bottom:1.1rem}
  .badge-loc{display:inline-block;background:rgba(255,107,53,.15);border:1px solid rgba(255,107,53,.3);padding:.3rem .9rem;border-radius:99px;font-size:.8rem;font-weight:700;color:var(--primary);margin-bottom:.8rem}
  .lead-loc{color:var(--text-muted);max-width:680px;line-height:1.85;margin-bottom:1.8rem;font-size:1rem}
  .btns{display:flex;gap:1rem;flex-wrap:wrap}
  .btn-p{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;transition:transform .2s}
  .btn-p:hover{transform:translateY(-2px)}
  .btn-wa{background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem}
  .sec{padding:3rem 0}.sec-alt{padding:3rem 0;background:var(--dark-2)}
  .sec-h2{font-size:1.35rem;font-weight:800;margin-bottom:1.1rem}
  .fact-box{background:linear-gradient(135deg,rgba(255,107,53,.1),rgba(255,107,53,.04));border-left:4px solid var(--primary);padding:1.2rem 1.5rem;border-radius:0 12px 12px 0;margin:1.5rem 0;max-width:760px}
  .fact-box p{color:var(--text-muted);line-height:1.85;font-size:.95rem}
  .stats-row{display:flex;gap:2rem;flex-wrap:wrap;margin:1.5rem 0}
  .stat-box{background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:12px;padding:1rem 1.5rem;text-align:center;min-width:120px}
  .stat-box .bignum{font-size:1.6rem;font-weight:900;color:var(--primary);display:block}
  .stat-box .label{font-size:.78rem;color:var(--text-muted)}
  .rich p{color:var(--text-muted);line-height:1.9;margin-bottom:1.1rem;max-width:790px}
  .rich strong{color:var(--text)}
  .faq-stack{display:flex;flex-direction:column;gap:.85rem;max-width:740px}
  .faq-q{background:var(--dark-3);border:1px solid rgba(255,107,53,.12);border-radius:12px;padding:1.15rem}
  .faq-q h3{font-size:.93rem;font-weight:700;margin-bottom:.4rem}
  .faq-q p{font-size:.88rem;color:var(--text-muted);line-height:1.7}
  .cta-final{background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.04));border:1px solid rgba(255,107,53,.25);border-radius:18px;padding:2.5rem 1.5rem;text-align:center;margin:3rem 0}
  .cta-final h2{font-size:1.4rem;font-weight:800;margin-bottom:.7rem}
  .pkg-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin:1.5rem 0}
  .pkg-card{background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.2rem}
  .pkg-card h3{font-weight:700;font-size:.95rem;margin-bottom:.5rem}
  .pkg-price{font-size:1.5rem;font-weight:900;color:var(--primary);display:block;margin-bottom:.3rem}
  .pkg-card ul{list-style:none;padding:0}
  .pkg-card li{font-size:.82rem;color:var(--text-muted);padding:.2rem 0;border-bottom:1px solid rgba(255,255,255,.05)}
</style>

<section class="hero-loc">
  <div class="container">
    <nav style="font-size:.82rem;color:var(--text-muted);margin-bottom:1.2rem">
      <a href="/" style="color:var(--primary)">Acasă</a> ›
      <a href="/animatori-petreceri-copii" style="color:var(--primary)">Animatori Petreceri Copii</a> ›
      ${d.city}
    </nav>
    <div class="badge-loc">📍 ${d.dist}</div>
    <h1 class="h1-loc">${d.h1}</h1>
    <p class="lead-loc">${d.uniqueFact}</p>
    <div class="btns">
      <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section class="sec">
  <div class="container">
    <h2 class="sec-h2">Despre ${d.city} — context local</h2>
    <div class="rich">
      ${d.content1}
    </div>
    <div class="stats-row">
      <div class="stat-box"><span class="bignum">${d.population}</span><span class="label">Locuitori</span></div>
      <div class="stat-box"><span class="bignum">490 RON</span><span class="label">De la</span></div>
      <div class="stat-box"><span class="bignum">30 min</span><span class="label">Confirmare</span></div>
      <div class="stat-box"><span class="bignum">50+</span><span class="label">Personaje</span></div>
    </div>
  </div>
</section>

<section class="sec-alt">
  <div class="container">
    <h2 class="sec-h2">Locații și comunitate în ${d.city}</h2>
    <div class="rich">
      ${d.content2}
    </div>
    <div class="fact-box">
      <p><strong>Locații recomandate în ${d.city}:</strong> ${d.venues}</p>
    </div>
    <div class="fact-box" style="margin-top:.8rem">
      <p><strong>Profil comunitate ${d.city}:</strong> ${d.carProf}</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="container">
    <h2 class="sec-h2">Pachete animatori ${d.city}</h2>
    <div class="pkg-row">
      <div class="pkg-card">
        <h3>Super 1</h3>
        <span class="pkg-price">490 RON</span>
        <ul>
          <li>1 personaj costumat</li>
          <li>2 ore program</li>
          <li>8-20 copii</li>
          <li>Jocuri + baloane + face painting</li>
          <li>Tatuaje + diplome magnetice</li>
        </ul>
      </div>
      <div class="pkg-card" style="border-color:var(--primary)">
        <h3>⭐ Super 3 — CEL MAI ALES</h3>
        <span class="pkg-price">840 RON</span>
        <ul>
          <li>2 personaje costumati</li>
          <li>2 ore + confetti party</li>
          <li>15-35 copii</li>
          <li>Program dublu</li>
          <li>Atentie individuala per copil</li>
        </ul>
      </div>
      <div class="pkg-card">
        <h3>Super 7</h3>
        <span class="pkg-price">1290 RON</span>
        <ul>
          <li>1 animator + 4 ursitoare</li>
          <li>3 ore program extins</li>
          <li>Botez sau aniversare mare</li>
          <li>50-100 invitati</li>
          <li>Pachet complet</li>
        </ul>
      </div>
    </div>
    <p style="color:var(--text-muted);font-size:.88rem">Personaje disponibile în ${d.city}: <strong>${d.chars}</strong></p>
  </div>
</section>

<section class="sec-alt">
  <div class="container">
    <h2 class="sec-h2">Întrebări frecvente — ${d.city}</h2>
    <div class="faq-stack">
      {[
        ${d.faq.map(([q,a]) => `["${q.replace(/"/g,"'")}", "${a.replace(/"/g,"'")}"]`).join(',\n        ')}
      ].map(([q,a]) => (
        <div class="faq-q">
          <h3>❓ {q}</h3>
          <p>{a}</p>
        </div>
      ))}
    </div>
  </div>
</section>

<div class="container">
  <div class="cta-final">
    <h2>${d.h1} — Rezervare</h2>
    <p>Confirmare în 30 minute · Plată după petrecere · Garanție contractuală scrisă</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;margin-top:1rem">
      <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
    </div>
    <p style="margin-top:1.2rem;font-size:.88rem;color:var(--text-muted)">
      ← <a href="/animatori-petreceri-copii" style="color:var(--primary);font-weight:600">Pagina principală</a>
      &nbsp;|&nbsp;<a href="/arie-acoperire" style="color:var(--primary)">Arie de acoperire completă</a>
    </p>
  </div>
</div>

</Layout>`;
}

for (const [slug, data] of Object.entries(pages)) {
  const fp = path.join(pDir, `${slug}.astro`);
  fs.writeFileSync(fp, buildPage(slug, data), 'utf-8');
  console.log('OK:', slug);
}
console.log('\nGata! Rescrise', Object.keys(pages).length, 'pagini cu continut radical diferit.');
