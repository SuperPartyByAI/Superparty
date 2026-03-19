// rewrite_service_pages.mjs — rescrie paginile de servicii thin-content
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

const WA = 'https://wa.me/40722744377';
const TEL = 'tel:+40722744377';

const pages = {
  'arcade-baloane/index.astro': {
    title: 'Arcade Baloane Petreceri Copii | SuperParty București — Decorațiuni Premium',
    desc: 'Arcade din baloane personalizate pentru petreceri copii în București. Arcade tematice, colonade, arce decorative la intrare. SuperParty 0722 744 377.',
    canonical: 'https://www.superparty.ro/arcade-baloane',
    body: `<section style="padding:4rem 0 2rem">
  <div class="container">
    <h1 style="font-size:clamp(1.7rem,4vw,2.5rem);font-weight:900;margin-bottom:1rem">Arcade din Baloane <span style="color:var(--primary)">Petreceri Copii</span></h1>
    <p style="color:var(--text-muted);line-height:1.85;max-width:680px;margin-bottom:1.8rem">Un arc spectaculos din baloane la intrarea în sala de petrecere sau în curtea casei transformă instantaneu atmosfera. SuperParty confecționează arcade tematice personalizate — culorile, forma și personajele preferate ale copilului.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="${TEL}" style="background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 Comandă: 0722 744 377</a>
      <a href="${WA}" style="background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Tipuri de arcade din baloane</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem">
      ${[
        ['🌈 Arcadă organică', '350-500 RON', '150-200 baloane, culorile temei petrecerii. Efect "wow" garantat la intrare — fotografii de neuitat'],
        ['🎭 Arcadă tematică', '450-600 RON', 'Formă și culori care reflectă personajul ales (Spider-Man, Elsa etc.). Include baloane folie tematice'],
        ['🏛️ Colonadă 2 stâlpi', '280-400 RON', 'Doi stâlpi din baloane spiralate la intrare. Elegant și rapid de montat — perfectă pentru săli'],
        ['🎪 Tunnel arcadă', '600-800 RON', 'Arc de traversat de 1.8m înălțime — copiii intră literal prin arcadă. Moment wow unic și memorabil'],
      ].map(([n,p,d]) => `<div style="background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.3rem"><div style="font-size:1.5rem;margin-bottom:.4rem">${n.split(' ')[0]}</div><div style="font-weight:700;font-size:.95rem;margin-bottom:.3rem">${n.slice(2)}</div><div style="color:var(--primary);font-weight:900;font-size:1.1rem;margin-bottom:.5rem">${p}</div><div style="color:var(--text-muted);font-size:.85rem;line-height:1.6">${d}</div></div>`).join('')}
    </div>
  </div>
</section>

<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">De ce arcada din baloane face diferența</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">Prima impresie a petrecerii se formează în primele 10 secunde — înainte ca animatorul să înceapă programul, înainte de tort, înainte de orice. Un arc spectaculos din baloane la intrare transmite instant: <em>"aceasta este o petrecere specială"</em>. Fotografiile cu arcada devin automat fotografia de profil a petrecerii.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">SuperParty confecționează arcadele pe loc în 45-90 minute înainte de sosirea invitaților. Nu trebuie să transporti nimic — venim cu toate balonele, pompa electrică și structura de susținere. La final, demontăm și facem curat.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Culorile sunt personalizate exact după cerința ta: tonurile exacte ale temei Disney, culorile echipei de fotbal preferate sau culorile coordonate cu rochița/costumul copilului aniversat. Mulți părinți trimit o fotografie cu rochia copilului — și facem arcada să se potrivească perfect.</p>
  </div>
</section>

<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <div style="background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.04));border:1px solid rgba(255,107,53,.25);border-radius:18px;padding:2.5rem;text-align:center">
      <h2 style="font-size:1.4rem;font-weight:800;margin-bottom:.7rem">Comandă Arcadă din Baloane</h2>
      <p style="color:var(--text-muted);margin-bottom:1.5rem">Trimite-ne data petrecerii, culorile și tema — facem o arcadă WOW pentru copilul tău!</p>
      <div style="display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
        <a href="${TEL}" style="background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 0722 744 377</a>
        <a href="${WA}" style="background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
      </div>
    </div>
  </div>
</section>`
  },

  'baloane-cu-heliu/index.astro': {
    title: 'Baloane cu Heliu Petreceri Copii | SuperParty București',
    desc: 'Baloane cu heliu pentru petreceri copii în București — baloane latex colorate, baloane folie personaje, buchete decorative. Livrare la locație. 0722 744 377.',
    canonical: 'https://www.superparty.ro/baloane-cu-heliu',
    body: `<section style="padding:4rem 0 2rem">
  <div class="container">
    <h1 style="font-size:clamp(1.7rem,4vw,2.5rem);font-weight:900;margin-bottom:1rem">Baloane cu Heliu <span style="color:var(--primary)">Petreceri Copii</span></h1>
    <p style="color:var(--text-muted);line-height:1.85;max-width:680px;margin-bottom:1.8rem">Baloanele cu heliu transformă orice spațiu într-o lume de basm. SuperParty livreaza buchete de baloane cu heliu la locatia petrecerii — baloane latex colorate, baloane folie cu personaje, buchete tematice.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="${TEL}" style="background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 Comandă: 0722 744 377</a>
      <a href="${WA}" style="background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Pachete baloane cu heliu disponibile</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem">
      ${[
        ['🎈 Buchet Standard (10 buc)', '80 RON', '10 baloane latex colorate cu heliu, panglici colorate. Potrivit decorat o masă sau o zonă foto'],
        ['🌟 Buchet Premium (20 buc)', '150 RON', '18 latex + 2 folie personaj, panglici și greutăți decorative. Set complet pentru sala mică'],
        ['🎭 Buchet Tematic (15 buc)', '130 RON', 'Baloane în culorile temei + 3 baloane folie tematice. Coordonat perfect cu restul decorațiunilor'],
        ['🏰 Set Complet Sală (50 buc)', '350 RON', '40 latex + 10 folie diverse forme. Decorezi întreaga sală — efect wow complet pentru 25+ invitați'],
      ].map(([n,p,d]) => `<div style="background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.3rem"><div style="font-size:1.5rem;margin-bottom:.4rem">${n.split(' ')[0]}</div><div style="font-weight:700;font-size:.95rem;margin-bottom:.3rem">${n.slice(2)}</div><div style="color:var(--primary);font-weight:900;font-size:1.1rem;margin-bottom:.5rem">${p}</div><div style="color:var(--text-muted);font-size:.85rem;line-height:1.6">${d}</div></div>`).join('')}
    </div>
  </div>
</section>

<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Cum funcționează livrarea balonalelor cu heliu</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">Balonalele cu heliu se umflă la fața locului — nu le transportăm umflate, deoarece ar fi imposibil fizic. Tehnicianul SuperParty ajunge cu 60-90 minute înainte de petrecere și umflă balonalele cu un kit profesional de heliu. Durată umflare: 20-30 minute pentru un buchet standard.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">Durata de flotabilitate a balonalelor cu heliu: balonalele latex standard plutesc 8-12 ore, balonalele latex Hi-Float (tratate special) plutesc 24-72 ore, balonalele folie plutesc 5-7 zile. Recomandăm balonalele Hi-Float pentru petrecerile la care dorești să rămână umflate și a doua zi.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">SuperParty poate coordona balonalele cu heliu simultan cu animatorul de la petrecere — ajungem împreună, montăm totul și lansăm programul de animație la ora exactă convenită. Zero stress pentru organizatorul petrecerii.</p>
  </div>
</section>`
  },

  'decoratiuni-baloane/index.astro': {
    title: 'Decorațiuni Baloane Petreceri Copii | SuperParty București',
    desc: 'Decorațiuni din baloane pentru petreceri copii: coloane, arcade, centrepiese, garland wall. Montaj la locație în București. SuperParty 0722 744 377.',
    canonical: 'https://www.superparty.ro/decoratiuni-baloane',
    body: `<section style="padding:4rem 0 2rem">
  <div class="container">
    <h1 style="font-size:clamp(1.7rem,4vw,2.5rem);font-weight:900;margin-bottom:1rem">Decorațiuni Baloane <span style="color:var(--primary)">Petreceri Copii</span></h1>
    <p style="color:var(--text-muted);line-height:1.85;max-width:680px;margin-bottom:1.8rem">Decorațiunile din baloane sunt elementul vizual care transformă orice sală sau curte într-un decor de vis. SuperParty oferă decorațiuni complete — coloane, arcade, garland wall, centrepiese — toate montate la locație de echipa noastră.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="${TEL}" style="background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 Comandă: 0722 744 377</a>
      <a href="${WA}" style="background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Servicii de decorațiuni disponibile</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem">
      ${[
        ['🏛️ Coloane din baloane', '150-250 RON/buc', 'Coloane spiralate de 1.8-2.5m înălțime. Perechi la intrare sau aleea de acces. Efect consistent și elegant'],
        ['🌈 Garland Wall (Balloon Wall)', '400-700 RON', 'Perete decorativ 2x2m din baloane organice. Fundalul perfect pentru zona foto — fotografii profesionale incluse'],
        ['🎂 Centerpice masă tort', '200-300 RON', 'Aranjament central spectaculos pe masa tortului — inaltime 80-120cm, tematic cu personajul petrecerii'],
        ['🏠 Decorare completă sală', '800-1500 RON', 'Pachet complet: arcade + coloane + centerpice + baloane heliu. Transformăm orice sală în poveste'],
      ].map(([n,p,d]) => `<div style="background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.3rem"><div style="font-size:1.5rem;margin-bottom:.4rem">${n.split(' ')[0]}</div><div style="font-weight:700;font-size:.95rem;margin-bottom:.3rem">${n.slice(2)}</div><div style="color:var(--primary);font-weight:900;font-size:1.1rem;margin-bottom:.5rem">${p}</div><div style="color:var(--text-muted);font-size:.85rem;line-height:1.6">${d}</div></div>`).join('')}
    </div>
  </div>
</section>

<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Procesul de decorare — de la idee la realizare</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">Pasul 1: Consultație gratuită — ne trimiți pe WhatsApp o fotografie cu sala, culorile temei și personajul ales. Raspundem cu propunere vizuală în 24 ore. Pasul 2: Confirmare și contract — stabilim ora de montaj (de obicei cu 90-120 minute înainte de petrecere).</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">Pasul 3: Montaj profesional — echipa SuperParty vine la sală cu toate materialele. Nu ai nevoie de nimic — nici pompe, nici suporturi, nici scotch. Montăm de la zero. Pasul 4: Fotografii de prezentare — înainte de sosirea invitaților, facem fotografii cu întreaga decorare pentru albumul tău.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">SuperParty a decorat peste 3.000 de săli de petreceri în București și Ilfov din 2015. Cunoaștem cele mai bune tehnici pentru fiecare tip de sală — înaltă, joasă, cu stâlpi, fără stâlpi, în aer liber sau interior. Trimite-ne fotografiile și lăsăm noi restul.</p>
  </div>
</section>`
  },

  'mos-craciun-de-inchiriat/index.astro': {
    title: 'Moș Crăciun de Închiriat Petreceri Copii | SuperParty București',
    desc: 'Moș Crăciun autentic pentru petreceri copii și vizite acasă în București. Costum premium, geantă cu cadouri, spectacol interactiv. Rezervări 0722 744 377.',
    canonical: 'https://www.superparty.ro/mos-craciun-de-inchiriat',
    body: `<section style="padding:4rem 0 2rem">
  <div class="container">
    <h1 style="font-size:clamp(1.7rem,4vw,2.5rem);font-weight:900;margin-bottom:1rem">Moș Crăciun de Închiriat <span style="color:var(--primary)">Petreceri Copii</span></h1>
    <p style="color:var(--text-muted);line-height:1.85;max-width:680px;margin-bottom:1.8rem">Moș Crăciun SuperParty este Moșul cel mai autentic din București — barbă naturală sau de calitate premium, costum roșu impecabil, geantă mare cu cadouri și un temperament blând și răbdător perfect pentru copiii de 2-12 ani.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="${TEL}" style="background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 Rezervă: 0722 744 377</a>
      <a href="${WA}" style="background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Ce include vizita Moșului SuperParty</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem">
      ${[
        ['🎅 Vizită acasă (60 min)', '350 RON', 'Moșul bate la ușa copilului, ascultă ce și-a dorit, împarte cadourile aduse de tine, cântă colinde, fotografii'],
        ['🎪 Petrecere grup (90 min)', '500 RON', 'Program pentru 10-25 copii: intrare spectaculoasă, povestiri, cântece, distribuire cadouri, fotografii individuale'],
        ['🏢 Event corporatist (2-3 ore)', '900-1200 RON', 'Moș Crăciun + ajutoare + program complet pentru 50-150 copii. Perfect pentru petreceri de companie'],
        ['👥 Duo Moș + Crăciuniță', '700 RON', 'Moș Crăciun + asistentă (Crăciunița). Program interactiv combinat, energie dublă, mai multe activități'],
      ].map(([n,p,d]) => `<div style="background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.3rem"><div style="font-size:1.5rem;margin-bottom:.4rem">${n.split(' ')[0]}</div><div style="font-weight:700;font-size:.95rem;margin-bottom:.3rem">${n.slice(2)}</div><div style="color:var(--primary);font-weight:900;font-size:1.1rem;margin-bottom:.5rem">${p}</div><div style="color:var(--text-muted);font-size:.85rem;line-height:1.6">${d}</div></div>`).join('')}
    </div>
  </div>
</section>

<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">De ce Moș Crăciun SuperParty este altfel</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">Problema principală cu Moșii Crăciun de la diverse agenții: costume ieftine de carnaval, barbă de plastic evident artificială, text memorat mecanic fără adaptare la copil. Moșul SuperParty este ales din echipa noastră de animatori cu experiență — actori sau persoane cu abilități naturale de interacțiune cu copiii.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">Personalizarea Moșului: la rezervare, ne transmiteți 3-5 lucruri specifice despre copilul tău (ce-și dorește, cum îl cheamă pe cel mai bun prieten, ce materie îi place la grădiniță, ce a promis că va face mai bine). Moșul nostru le integrează natural în conversație — copilul va fi convins 100% că Moșul știe totul despre el.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Rezervări Moș Crăciun SuperParty: deschiderea rezervărilor pentru sezonul decembrie se face pe 1 octombrie. Weekendurile din 14-24 decembrie se epuizează în 48-72 ore. Dacă dorești data și ora exactă pentru Moș, rezervați în octombrie! Avem 12 Moși Crăciun în echipă — capacitate limitată.</p>
  </div>
</section>`
  },

  'vata-de-zahar-si-popcorn/index.astro': {
    title: 'Vată de Zahăr și Popcorn Petreceri Copii | SuperParty București',
    desc: 'Mașini de vată de zahăr și popcorn pentru petreceri copii în București. Chirie mașini, operator inclus, consumabile nelimitate. SuperParty 0722 744 377.',
    canonical: 'https://www.superparty.ro/vata-de-zahar-si-popcorn',
    body: `<section style="padding:4rem 0 2rem">
  <div class="container">
    <h1 style="font-size:clamp(1.7rem,4vw,2.5rem);font-weight:900;margin-bottom:1rem">Vată de Zahăr și Popcorn <span style="color:var(--primary)">Petreceri Copii</span></h1>
    <p style="color:var(--text-muted);line-height:1.85;max-width:680px;margin-bottom:1.8rem">Stația de vată de zahăr și popcorn este un magnet pentru copii la orice petrecere — și un deliciu pentru părinți. SuperParty oferă mașini profesionale cu operator inclus pentru durata petrecerii tale.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="${TEL}" style="background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 Comandă: 0722 744 377</a>
      <a href="${WA}" style="background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Pachete disponibile</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem">
      ${[
        ['🍭 Vată de Zahăr (2 ore)', '280 RON', 'Mașina profesională + operator + zahăr colorat nelimitat. 200+ porții posibile. Culorile la alegere'],
        ['🍿 Popcorn (2 ore)', '250 RON', 'Aparat popcorn profesional + operator + porumb și unt nelimitat. Variante: sarat, dulce, caramel'],
        ['🎪 Combo Vată + Popcorn (2 ore)', '450 RON', 'Ambele mașini + operator pentru fiecare. Stația dublă care face senzație la orice petrecere mare'],
        ['⏰ Extensie orar (1h)', '120 RON', 'Adaugă o oră extra la orice pachet. Recomandat pentru petreceri cu 40+ invitați sau programe lungi'],
      ].map(([n,p,d]) => `<div style="background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.3rem"><div style="font-size:1.5rem;margin-bottom:.4rem">${n.split(' ')[0]}</div><div style="font-weight:700;font-size:.95rem;margin-bottom:.3rem">${n.slice(2)}</div><div style="color:var(--primary);font-weight:900;font-size:1.1rem;margin-bottom:.5rem">${p}</div><div style="color:var(--text-muted);font-size:.85rem;line-height:1.6">${d}</div></div>`).join('')}
    </div>
  </div>
</section>

<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Detalii tehnice și logistice</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">Mașinile noastre de vată de zahăr și popcorn sunt utilizate în standard eveniment — nu mașini de plastic ieftine, ci aparate profesionale cu producție de 50-80 de porții/oră. Curățate și dezinfectate după fiecare utilizare. Conform normelor ANSVSA pentru alimente la evenimente.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">Vata de zahăr colorată disponibilă în: roz clasic, albastru, violet, curcubeu, roșu, galben, verde. Combinăm culorile cu tema petrecerii — vată albastră pentru Frozen, roșie pentru Spider-Man, galbenă pentru Pikachu. Popcornul se oferă în pungi personalizate cu numele copilului (opțional, 20 RON extra).</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Suprafața necesară: 1,5 x 1,5m pentru fiecare mașină + spațiu de așteptare 1m. Priza electrică standard 220V necesară (incluzând cu extensie de 5m). Functioneaza atât în interior (sală cu ventilație) cât și exterior (vreme fără ploaie). Operatorul este responsabil de curățenie în zona stației — lăsăm totul impecabil.</p>
  </div>
</section>`
  },

  'ursitoare-botez/index.astro': {
    title: 'Ursitoare Botez | SuperParty București — Program Autentic',
    desc: 'Ursitoare profesioniste pentru botez în București. Program autentic 30-45 min, 1-4 ursitoare disponibile, costum tradițional sau modern. SuperParty 0722 744 377.',
    canonical: 'https://www.superparty.ro/ursitoare-botez',
    body: `<section style="padding:4rem 0 2rem">
  <div class="container">
    <h1 style="font-size:clamp(1.7rem,4vw,2.5rem);font-weight:900;margin-bottom:1rem">Ursitoare pentru Botez <span style="color:var(--primary)">SuperParty</span></h1>
    <p style="color:var(--text-muted);line-height:1.85;max-width:680px;margin-bottom:1.8rem">Spectacolul de ursitoare este momentul cel mai emoționant al oricărui botez — când destinul copilului este "scris" cu urări de sănătate, noroc și fericire. SuperParty are 8 ursitoare profesioniste disponibile în București și Ilfov.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap">
      <a href="${TEL}" style="background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.85rem 1.8rem;border-radius:50px;font-weight:700;text-decoration:none">📞 Rezervă: 0722 744 377</a>
      <a href="${WA}" style="background:#25d366;color:#fff;padding:.85rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>

<section style="padding:3rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Pachete ursitoare disponibile</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.2rem">
      ${[
        ['✨ 1 Ursitoare (35 min)', '350 RON', 'Spectacol complet: intrare dramatică, urări personalizate, dans ritual, incantații, final emoționant'],
        ['👥 2 Ursitoare (40 min)', '550 RON', 'Dialog dramatic între două ursitoare. Spectacol mai dinamic, urări diversificate, mai multă energie scenică'],
        ['🎭 3 Ursitoare (50 min)', '750 RON', 'Spectacol complet cu 3 ursitoare deosebite: una severă, una blândă, una veselă. Cel mai popular format'],
        ['👑 4 Ursitoare Premium (60 min)', '990 RON', 'Pachet Super 7 inclus: 4 ursitoare + program complet pentru copiii invitați + animator dedicat'],
      ].map(([n,p,d]) => `<div style="background:var(--dark-3);border:1px solid rgba(255,107,53,.15);border-radius:14px;padding:1.3rem"><div style="font-size:1.5rem;margin-bottom:.4rem">${n.split(' ')[0]}</div><div style="font-weight:700;font-size:.95rem;margin-bottom:.3rem">${n.slice(2)}</div><div style="color:var(--primary);font-weight:900;font-size:1.1rem;margin-bottom:.5rem">${p}</div><div style="color:var(--text-muted);font-size:.85rem;line-height:1.6">${d}</div></div>`).join('')}
    </div>
  </div>
</section>

<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.35rem;font-weight:800;margin-bottom:1.2rem">Tradiția ursitoarele — cum funcționează spectacolul</h2>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">În tradiția românească, ursitoarele (sau Ursitele) sunt trei zeițe mitice care vin în noaptea de după nașterea unui copil pentru a-i ursi (determina) destinul. Spectacolul modern de ursitoare la botez recreează această tradiție în formă scenică — urările sunt personalizate cu numele copilului, prenumele părinților, detalii specifice familiei.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px;margin-bottom:1rem">SuperParty pregătește spectacolul cu 48 ore înainte pe baza informațiilor pe care le transmiteți: numele complet al copilului, prenumele bunicilor, o dorință specială a familiei pentru viitorul copilului. Urările includ referinze la aceste detalii — oaspeții rămân impresionați de nivelul de personalizare.</p>
    <p style="color:var(--text-muted);line-height:1.9;max-width:800px">Costumele ursitoarele SuperParty: variantă tradițională (ie românească, voal, coronița de flori — clasică și respectuoasă față de tradiție) sau variantă modernă (ținute alb-auriu-violet, dramă scenică mai pronunțată). La cerere, combinăm o ursitoare tradițională cu una modernă pentru efect vizual mai dinamic.</p>
  </div>
</section>`
  },
};

let n = 0;
for (const [relFp, data] of Object.entries(pages)) {
  const fp = path.join(ROOT, 'src/pages', relFp);
  if (!fs.existsSync(fp)) { console.log('SKIP(not found):', relFp); continue; }
  
  const isNested = relFp.includes('/');
  const layoutPath = isNested ? `../../layouts/Layout.astro` : `../layouts/Layout.astro`;
  
  const newPage = `---
import Layout from '${layoutPath}';
---

<Layout
  title="${data.title}"
  description="${data.desc}"
  canonical="${data.canonical}"
  robots="index, follow"
>

${data.body}

<section style="padding:2.5rem 0">
  <div class="container">
    <div style="background:linear-gradient(135deg,rgba(255,107,53,.15),rgba(255,107,53,.04));border:1px solid rgba(255,107,53,.25);border-radius:18px;padding:2rem;text-align:center">
      <h2 style="font-size:1.3rem;font-weight:800;margin-bottom:.7rem">Rezervă acum — confirmare în 30 minute</h2>
      <p style="color:var(--text-muted);margin-bottom:1.2rem;font-size:.92rem">Spune-ne data și adresa — îți confirmăm disponibilitatea rapid.</p>
      <div style="display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
        <a href="${TEL}" style="background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">📞 0722 744 377</a>
        <a href="${WA}" style="background:#25d366;color:#fff;padding:.8rem 1.4rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
      </div>
      <p style="margin-top:1rem;font-size:.83rem;color:var(--text-muted)">← <a href="/animatori-petreceri-copii" style="color:var(--primary)">Animatori Petreceri Copii</a> &nbsp;|&nbsp; <a href="/" style="color:var(--primary)">Acasă</a></p>
    </div>
  </div>
</section>

</Layout>`;
  
  fs.writeFileSync(fp, newPage, 'utf-8');
  n++;
  console.log('OK rewrite:', relFp);
}
console.log(`\n✅ ${n} pagini de servicii rescrise cu continut complet!`);
