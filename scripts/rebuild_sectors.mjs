
// rebuild_sectors.mjs — Rescrie complet paginile sector-1 prin sector-6
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const sectors = [
  {
    slug: 'sector-1',
    name: 'Sectorul 1',
    zones: 'Dorobanți, Floreasca, Aviatorilor, Victoriei, Băneasa, Herăstrău, Domenii',
    profile: 'zona premium nordică a Capitalei, cu venituri ridicate și gusturi selective',
    park: 'Parcul Herăstrău (186 ha)',
    parkDesc: 'cel mai mare parc din București, locul preferat pentru petreceri în aer liber ale familiilor din Floreasca și Aviatorilor',
    venue: 'vilele cu curți impecabile din Floreasca, restaurantele de pe Dorobanți, Băneasa Shopping City',
    metro: 'Aviatorilor (M2), Piața Victoriei (M1/M2)',
    charTrend: 'Elsa și Ana (Frozen) domină la fetițe 3-7 ani, Spider-Man și Thor la băieți. Tendință 2025: Miraculous Ladybug, Bluey pentru copii 2-5 ani și PAW Patrol.',
    communityNote: 'Animatorii noștri dedicați Sectorului 1 au pregătire specială pentru ambianță premium — costume impecabile, dictie clară, control total al grupelor mari de copii. Oferim și animatori bilingvi română-engleză pentru familii internaționale din zona Băneasa.',
    bookingTip: 'Rezervați cu 4-6 săptămâni înainte pentru weekendurile din mai-septembrie. Vilele din Floreasca și Aviatorilor sunt extrem de solicitate în sezon.',
    uniqueFact: 'Sectorul 1 găzduiește cele mai frecvente cereri pentru petreceri în grădini private — SuperParty a organizat peste 400 de petreceri de curte în Floreasca, Băneasa și Aviatorilor din 2018 până astăzi.',
  },
  {
    slug: 'sector-2',
    name: 'Sectorul 2',
    zones: 'Colentina, Floreasca S2, Tei, Ștefan cel Mare, Obor, Fundeni',
    profile: 'zona cu cea mai mare diversitate socială — de la Floreasca premium la cartierele populare Colentina și Tei',
    park: 'Lacul și Parcul Floreasca + Lacul Colentina',
    parkDesc: 'sistemul lacustric Colentina formează o cintă verde care traversează sectorul — mii de familii vin la picnic și petreceri în aer liber în weekend în aceste locuri',
    venue: 'sălile de petreceri moderne de la Obor și Colentina, restaurantele family pe Ștefan cel Mare',
    metro: 'Obor (M2), Iancului (M2), Ștefan cel Mare (M2)',
    charTrend: 'Spider-Man este liderul absolut în Sectorul 2 la băieți 4-10 ani, Elsa la fetițe. Tendință în creștere: Bluey (fetițe 2-5 ani), Sonic (băieți 5-10 ani).',
    communityNote: 'Zona Colentina are o densitate mare de copii și grupuri active de părinți pe Facebook. SuperParty este cel mai recomandat serviciu în grupurile de cartier Colentina, Tei și Obor — cu sute de recomandări directe între părinți.',
    bookingTip: 'Weekendurile din mai-septembrie se ocupă rapid în zona Colentina. Rezervați cu 3-4 săptămâni înainte pentru aceste zone. Floreasca S2 — similar Sectorului 1, minimun 3 săptămâni.',
    uniqueFact: 'Sectorul 2 este sectorul cu cel mai mare număr de petreceri SuperParty la blocuri cu curți — avem experiență vastă în organizarea programelor în spațiile interioare ale curților de bloc, unde spațiul trebuie gestionat cu grijă.',
  },
  {
    slug: 'sector-3',
    name: 'Sectorul 3',
    zones: 'Titan, Dristor, Vitan, Dudești, Centrul Civic, Balta Albă, Timpuri Noi',
    profile: 'cel mai populat sector cu 400.000 de locuitori și cea mai activă scenă de petreceri pentru copii',
    park: 'Parcul IOR (Lunca Morii — 70 ha)',
    parkDesc: 'parcul IOR este destinația favorită a familiilor din Titan și pentru picnicuri cu animatori SuperParty — spațiul larg permite programe pentru 10-60 de copii simultan, fără interferențe',
    venue: 'Sun Plaza Mall Kids Zone (etaj 2), sălile de petreceri din Titan și Balta Albă',
    metro: 'Titan (M2), Dristor (M2), Timpuri Noi (M3)',
    charTrend: 'Spider-Man și Iron Man domină la băieți 4-11 ani, Elsa și Rapunzel la fetițe. Tendință 2025: PAW Patrol pentru copii 2-4 ani. Comunitatea din Titan are gusturi clasice — personajele bine-cunoscute sunt întotdeauna câștigătoare.',
    communityNote: 'Sectorul 3 este zona noastră cu cel mai mare volum de petreceri — avem animatori dedicați pentru Titan, Dristor, Vitan și Balta Albă. Confirmăm disponibilitatea în 20 de minute pentru orice adresă din sector.',
    bookingTip: 'Zona Titan este extrem de solicitată în weekend — rezervați minimum 3 săptămâni pentru orice ocazie din mai-septembrie. Sun Plaza Kids Zone se rezervă direct cu mall-ul; SuperParty vine independent la orice locație aleasă de voi.',
    uniqueFact: 'Parcul IOR a găzduit cele mai mari petreceri SuperParty în aer liber — record: 85 de copii la o singură petrecere de ziua copilăriei. Animatorii noștri sunt pregătiți pentru volume mari de participanți.',
  },
  {
    slug: 'sector-4',
    name: 'Sectorul 4',
    zones: 'Tineretului, Berceni, Oltenița, Văcărești, Timpuri Noi S4',
    profile: 'zona sudică cu mix de cartiere vechi (Berceni) și cel mai mare parc din sudul Capitalei',
    park: 'Parcul Tineretului (210 ha)',
    parkDesc: 'cel mai mare parc din sudul Bucureștiului, cu alei largi, zone amenajate și lacuri interioare — SuperParty a organizat zeci de petreceri în aer liber în Parcul Tineretului',
    venue: 'Vitan Mall Kids Zone, sălile de petreceri din Berceni, curțile blocurilor pe Oltenița',
    metro: 'Tineretului (M2), Timpuri Noi (M3)',
    charTrend: 'Sectorul 4 preferă personajele clasice: Spider-Man și Batman la băieți, Elsa și Prințesa la fetițe. Tendință 2025: Bluey (fetițe 2-4 ani) și Sonic (băieți 5-9 ani). Berceni vechi preferă personajele recunoscute imediat.',
    communityNote: 'Berceni are două zone cu caracteristici diferite: Berceni vechi cu curți interioare de bloc mai mici și Berceni nou cu ansambluri rezidențiale și spații comune modern amenajate. SuperParty cunoaște fiecare sub-zonă și adaptează programul corespunzător.',
    bookingTip: 'Parcul Tineretului este disponibil pentru petreceri fără rezervare prealabilă — SuperParty vine cu echipament portabil wireless complet. Sălile din Berceni se rezervă cu 2-3 săptămâni înainte.',
    uniqueFact: 'Sectorul 4 are cel mai ieftin raport calitate-preț pentru închirierea sălilor de petreceri din București — SuperParty recomandă părinților să combine o sală abordabilă din Berceni cu pachetu Super 3 pentru o petrecere completă la buget optimizat.',
  },
  {
    slug: 'sector-5',
    name: 'Sectorul 5',
    zones: 'Rahova, Sebastian, Ferentari, 13 Septembrie, Cotroceni',
    profile: 'sectorul cu cea mai puternică identitate comunitară — petrecerile includ bunici, vecini și prieteni de cartier în mod tradițional',
    park: 'Parcul Sebastian (30 ha)',
    parkDesc: 'cel mai iubit parc al comunității din Sectorul 5 — SuperParty a organizat sute de petreceri în Parcul Sebastian, atât în zonele umbrite cât și în spațiile deschise cu iarbă',
    venue: 'curțile caselor din Rahova, restaurantele din Cotroceni, spațiile comunitare din Sebastian',
    metro: 'Răzoare (M4), Eroilor (M4/M3), Izvor (M3)',
    charTrend: 'Sectorul 5 preferă personajele puternice și recunoscute: Spider-Man, Batman și Clovnul vesel domină. Elsa e la fel de populară ca oriunde. Particularitate: grupurile de copii din Rahova reacționează fantastic la personajele energice care interacționează mult cu publicul.',
    communityNote: 'Petrecerile din Sectorul 5 au adesea 30-50 de copii — numere mari față de media națională. SuperParty recomandă pachetul Super 3 (2 personaje) sau Super 7 pentru aceste grupuri. Curtile caselor din Rahova cu suprafete generoase sunt perfecte pentru petreceri de vară cu mulți participanți.',
    bookingTip: 'Sectorul 5 nu este blocat în rezervări ca sectoarele nord și est — de obicei confirmăm disponibilitate și pentru weekenduri cu 7-10 zile înainte. Totuși, pentru iunie-august, recomandăm 3 săptămâni în avans.',
    uniqueFact: 'Zona Cotroceni (lângă Universitate) este diferită față de restul Sectorului 5 — familii tinere cu venituri medii-ridicate care apreciază calitatea. SuperParty are animatori dedicați atât pentru zona Cotroceni cât și pentru Rahova și Ferentari.',
  },
  {
    slug: 'sector-6',
    name: 'Sectorul 6',
    zones: 'Militari, Drumul Taberei, Crângași, Giulești, Lăcănari',
    profile: 'cel mai populat sector din București (380.000 loc.) cu cea mai activă comunitate de părinți din Capitală',
    park: 'Parcul Drumul Taberei (39 ha)',
    parkDesc: 'renovat complet în 2022 cu zone dedicate copiilor, Parcul DT este cel mai vizitat parc de cartier din vestul Capitalei — SuperParty organizează petreceri aci în fiecare weekend de vară',
    venue: 'Plaza Romania Mall (Kids Zone extinsă), sălile petreceri moderne din Militari, curțile ansamblurilor noi din DT',
    metro: 'Militari (M5), Pǎcii (M5), Gorjului (M5), Drumul Taberei (M5)',
    charTrend: 'Sectorul 6 are cel mai mare volum SuperParty din București. Spider-Man este constant #1 la băieți, Elsa și Miraculous Ladybug conduc la fetițe. Militari Residence: cerere crescută pentru Bluey și PAW Patrol Marshall.',
    communityNote: 'Militari Residence (50.000 loc.) este cea mai activă comunitate — avem animatori familiarizați cu sala comunității, curțile interioare și spațiile comune ale ansamblului. Rezervarile vin masiv prin WhatsApp Community Militari Residence unde SuperParty este recomandarea #1.',
    bookingTip: 'Sectorul 6 este zona cu CEA MAI MARE CERERE SuperParty din București — rezervați cu 3-5 săptămâni înainte pentru mai-septembrie și cu 6-8 săptămâni pentru Crăciun și Revelion. Nu lăsați rezervarea pe ultimul moment!',
    uniqueFact: 'Drumul Taberei și Militari sunt separate geografie dar unite prin stilul de viață familial activ. Un fapt interesant: cele mai mari petreceri tematice SuperParty (cu decoruri complete) sunt cerute invariabil din zona Drumul Taberei.',
  },
];

function buildSectorPage(d) {
  const schema = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'Service',
        'name': `Animatori Petreceri Copii ${d.name}`,
        'provider': {'@type': 'LocalBusiness', 'name': 'SuperParty', 'telephone': '+40722744377'},
        'areaServed': d.name,
        'url': `https://superparty.ro/petreceri/${d.slug}`
      },
      {
        '@type': 'FAQPage',
        'mainEntity': [
          {'@type':'Question','name':`Ce zone din ${d.name} acoperiți?`,'acceptedAnswer':{'@type':'Answer','text':`Acoperim integral ${d.name}: ${d.zones}. Zero taxă deplasare în întreg sectorul.`}},
          {'@type':'Question','name':`Unde se poate organiza petrecerea în ${d.name}?`,'acceptedAnswer':{'@type':'Answer','text':`${d.parkDesc}. De asemenea: ${d.venue}.`}},
          {'@type':'Question','name':`Ce personaje sunt cerute în ${d.name}?`,'acceptedAnswer':{'@type':'Answer','text':d.charTrend}},
          {'@type':'Question','name':`Cât timp înainte rezervăm în ${d.name}?`,'acceptedAnswer':{'@type':'Answer','text':d.bookingTip}},
          {'@type':'Question','name':`Ce face unic ${d.name} față de alte sectoare?`,'acceptedAnswer':{'@type':'Answer','text':d.uniqueFact}},
        ]
      },
      {
        '@type': 'BreadcrumbList',
        'itemListElement': [
          {'@type':'ListItem','position':1,'name':'Acasă','item':'https://superparty.ro'},
          {'@type':'ListItem','position':2,'name':'Animatori Petreceri Copii','item':'https://superparty.ro/animatori-petreceri-copii'},
          {'@type':'ListItem','position':3,'name':d.name,'item':`https://superparty.ro/petreceri/${d.slug}`}
        ]
      }
    ]
  };

  return `---
import Layout from '../../layouts/Layout.astro';
const schema = JSON.stringify(${JSON.stringify(schema)});
---

<Layout
  title="Animatori Petreceri Copii ${d.name} | SuperParty — 490 RON, garantie"
  description="SuperParty acoperă ${d.name}: ${d.zones.split(',').slice(0,3).join(', ')}. Animatori profesionisti, pachete 490-840-1290 RON, garantie contractuala scrisa. Tel: 0722 744 377."
  canonical="https://www.superparty.ro/petreceri/${d.slug}"
  robots="index, follow"
  schema={schema}
>
<style>
  .hero{padding:4rem 0 2rem;background:radial-gradient(ellipse at top,rgba(255,107,53,.12) 0%,transparent 65%)}
  .h1c{font-size:clamp(1.6rem,4vw,2.5rem);font-weight:800;line-height:1.2;margin-bottom:1rem}
  .lead{color:var(--text-muted);max-width:650px;line-height:1.85;margin-bottom:2rem}
  .btn-p{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem;transition:transform .2s}
  .btn-p:hover{transform:translateY(-2px)}
  .btn-wa{background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none;display:inline-flex;align-items:center;gap:.5rem}
  .s{padding:3rem 0}.s-alt{padding:3rem 0;background:var(--dark-2)}
  .h2c{font-size:1.4rem;font-weight:800;margin-bottom:1rem}
  .g3{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.2rem}
  .card{background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.3rem}
  .card h3{font-weight:700;margin-bottom:.6rem;font-size:.95rem}
  .card ul{list-style:none;padding:0;margin:0}
  .card li{padding:.27rem 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:.87rem;color:var(--text-muted)}
  .rt p{color:var(--text-muted);line-height:1.9;margin-bottom:1rem;max-width:780px}
  .rt strong{color:var(--text)}
  .fqs{display:flex;flex-direction:column;gap:.9rem;max-width:710px}
  .fq{background:var(--dark-3);border:1px solid rgba(255,107,53,.12);border-radius:12px;padding:1.1rem}
  .fq h3{font-size:.92rem;font-weight:700;margin-bottom:.4rem}
  .fq p{font-size:.87rem;color:var(--text-muted);line-height:1.7}
  .cta-b{background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.05));border:1px solid rgba(255,107,53,.25);border-radius:18px;padding:2.5rem 1.5rem;text-align:center}
  .cta-b h2{font-size:1.4rem;font-weight:800;margin-bottom:.8rem}
  .cta-b p{color:var(--text-muted);margin-bottom:1.5rem;font-size:.93rem}
  .cb{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center}
  .fact{background:rgba(255,107,53,.08);border-left:3px solid var(--primary);padding:1rem 1.2rem;border-radius:0 10px 10px 0;margin-bottom:1rem;max-width:780px}
  .fact p{color:var(--text-muted);font-size:.9rem;line-height:1.7;margin:0}
</style>

<section class="hero">
  <div class="container">
    <nav style="font-size:.82rem;color:var(--text-muted);margin-bottom:1.5rem">
      <a href="/" style="color:var(--primary)">Acasă</a> ›
      <a href="/animatori-petreceri-copii" style="color:var(--primary)">Animatori Petreceri Copii</a> ›
      ${d.name}
    </nav>
    <h1 class="h1c">Animatori Petreceri Copii <span style="color:var(--primary)">${d.name}</span></h1>
    <p class="lead">${d.profile.charAt(0).toUpperCase() + d.profile.slice(1)}. SuperParty vine direct la adresa ta din <strong>${d.name}</strong> — zero taxă deplasare, confirmare în 30 min., garantie contractuală scrisa.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section class="s">
  <div class="container">
    <h2 class="h2c">Zone acoperite în <span style="color:var(--primary)">${d.name}</span></h2>
    <div class="rt">
      <p>SuperParty acoperă <strong>tot ${d.name}</strong>: <strong>${d.zones}</strong>. Metrou în zonă: <strong>${d.metro}</strong>. Zero taxă de deplasare pentru orice adresă din sector.</p>
      <p>${d.communityNote}</p>
    </div>
    <div class="g3" style="margin-top:1.5rem">
      <div class="card">
        <h3>🌿 ${d.park}</h3>
        <ul>
          <li>${d.parkDesc.substring(0, 60)}...</li>
          <li>Petreceri aer liber fără rezervare spațiu</li>
          <li>Echipament portabil wireless inclus</li>
          <li>10-100 de copii — adaptare completă</li>
        </ul>
      </div>
      <div class="card">
        <h3>🏢 Locații indoor</h3>
        <ul>
          <li>${d.venue.split(',')[0].trim()}</li>
          ${d.venue.split(',')[1] ? `<li>${d.venue.split(',')[1].trim()}</li>` : ''}
          <li>Spațiu minim 15-20 mp</li>
          <li>Animatorul vine cu tot echipamentul</li>
        </ul>
      </div>
      <div class="card">
        <h3>✅ Garantie SuperParty</h3>
        <ul>
          <li>Zero taxă deplasare în ${d.name}</li>
          <li>Confirmare în 30 minute</li>
          <li>Contract digital în 24 ore</li>
          <li>Plată DUPĂ petrecere</li>
          <li>Nerambursabil dacă nu v-ați distrat</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="s-alt">
  <div class="container">
    <h2 class="h2c">Personaje și tendințe în <span style="color:var(--primary)">${d.name}</span></h2>
    <div class="rt">
      <p>${d.charTrend}</p>
      <p>Colecția completă SuperParty: <strong>50+ personaje</strong> — super-eroi (Spider-Man, Batman, Captain America, Iron Man, Thor, Hulk), prințese Disney (Elsa, Ana, Rapunzel, Belle, Moana, Ariel, Aurora), personaje moderne (PAW Patrol, Sonic, Bluey, Miraculous Ladybug), clasice (Clovnul vesel, Magicianul, Zânele). Menționați preferința copilului la rezervare — verificăm disponibilitatea costumului specific.</p>
    </div>
    <div class="fact">
      <p>📌 <strong>Fapt interesant despre ${d.name}:</strong> ${d.uniqueFact}</p>
    </div>
  </div>
</section>

<section class="s">
  <div class="container">
    <h2 class="h2c">Pachete animatori — <span style="color:var(--primary)">${d.name}</span></h2>
    <div class="rt">
      <p><strong>Super 1 (490 RON):</strong> 1 personaj costumat, 2 ore program complet — jocuri interactive adaptate vârstei, baloane modelate (1 per copil), face painting tematic, tatuaje temporare profesionale, mini disco cu muzică pentru copii și diplome magnetice personalizate. Recomandat pentru 8-20 de copii.</p>
      <p><strong>Super 3 (840 RON):</strong> 2 personaje costumați, 2 ore program dublu. Atenție individuală crescută per copil, energia se dublează, recomandat pentru 15-35 de copii. Cel mai ales pachet în ${d.name}.</p>
      <p><strong>Super 7 (1290 RON):</strong> 1 animator + 4 ursitoare, 3 ore, pachet botez sau aniversare mare. Recomandat pentru 50-100 de invitați. <a href="/animatori-petreceri-copii" style="color:var(--primary)">→ Detalii complete</a></p>
      <p>${d.bookingTip}</p>
    </div>
  </div>
</section>

<section class="s-alt">
  <div class="container">
    <h2 class="h2c">Întrebări frecvente — animatori în <span style="color:var(--primary)">${d.name}</span></h2>
    <div class="fqs">
      {[
        ["Ce zone din ${d.name} acoperiți?", "Acoperim integral ${d.name}: ${d.zones}. Zero taxă deplasare în întreg sectorul — inclusa în prețul pachetului ales."],
        ["Unde se poate organiza petrecerea în ${d.name}?", "${d.parkDesc}. De asemenea recomandăm: ${d.venue}."],
        ["Ce personaje cerute în ${d.name}?", "${d.charTrend}"],
        ["Cât timp înainte rezervăm animatorul în ${d.name}?", "${d.bookingTip}"],
        ["Ce face ${d.name} unic față de alte sectoare?", "${d.uniqueFact}"],
      ].map(([q,a]) => (
        <div class="fq">
          <h3>❓ {q}</h3>
          <p>{a}</p>
        </div>
      ))}
    </div>
  </div>
</section>

<section class="s">
  <div class="container">
    <div class="cta-b">
      <h2>Rezervă animator în <span style="color:var(--primary)">${d.name}</span></h2>
      <p>Spune-ne data, adresa și vârsta copilului — confirmăm disponibilitatea în 30 minute.</p>
      <div class="cb">
        <a href="tel:+40722744377" class="btn-p cta">📞 0722 744 377</a>
        <a href="https://wa.me/40722744377" class="btn-wa cta">💬 WhatsApp</a>
      </div>
      <p style="margin-top:1rem;font-size:.87rem;color:var(--text-muted)">
        ← <a href="/animatori-petreceri-copii" style="color:var(--primary);font-weight:600">Pagina principală Animatori</a>
        &nbsp;|&nbsp;
        <a href="/arie-acoperire" style="color:var(--primary)">Toate zonele acoperite</a>
      </p>
    </div>
  </div>
</section>
</Layout>`;
}

const pDir = path.join(__dirname, '../src/pages/petreceri');
for (const d of sectors) {
  const fp = path.join(pDir, `${d.slug}.astro`);
  fs.writeFileSync(fp, buildSectorPage(d), 'utf-8');
  console.log(`OK: ${d.slug}`);
}
console.log('\nGata! Sectoare rescrise.');
