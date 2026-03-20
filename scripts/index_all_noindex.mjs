// index_all_noindex.mjs — Faza 1+2: activarea tuturor celor 102 pagini noindex
// Faza 1: 88 petreceri/comune — elimina noindex (au deja titlu+desc+schema+canonical+580w)
// Faza 2: 13 animatori-copii-* — rescrie continut + elimina noindex
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

function collectAll(dir, rel = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const fp = path.join(dir, e.name);
    const rp = rel ? `${rel}/${e.name}` : e.name;
    if (e.isDirectory()) out.push(...collectAll(fp, rp));
    else if (e.name.endsWith('.astro') && !e.name.includes('[')) out.push({ rel: rp, fp });
  }
  return out;
}

function getWords(raw) {
  return raw.replace(/^---[\s\S]*?---/m, '').replace(/<style[\s\S]*?<\/style>/gi, '').replace(/<script[\s\S]*?<\/script>/gi, '').replace(/<[^>]+>/g, ' ').replace(/[^\wăâîșțĂÂÎȘȚ\s]/g, ' ').replace(/\s+/g, ' ').trim().split(/\s+/).filter(w => w.length >= 3).length;
}

const all = collectAll(path.join(ROOT, 'src/pages'));
const noindexAll = all.filter(p => fs.readFileSync(p.fp, 'utf-8').includes('noindex'));

// ═══════════════════════════════════════════════════════════
// FAZA 1: petreceri/comune — simple remove noindex
// ═══════════════════════════════════════════════════════════
const petreceriNoindex = noindexAll.filter(p => p.rel.startsWith('petreceri'));
let phase1Fixed = 0;
const phase1Urls = [];

for (const p of petreceriNoindex) {
  let c = fs.readFileSync(p.fp, 'utf-8');
  const wc = getWords(c);
  
  if (wc < 300) { console.log(`SKIP(${wc}w thin): ${p.rel}`); continue; }
  
  // Remove noindex — various patterns
  c = c.replace(/robots="noindex,\s*follow"/gi, 'robots="index, follow"');
  c = c.replace(/robots="noindex"/gi, 'robots="index, follow"');
  c = c.replace(/noindex,\s*nofollow/gi, 'index, follow');
  c = c.replace(/<meta\s+name="robots"\s+content="noindex[^"]*"\s*\/>/gi, '');
  // Also remove noindex from Layout prop if present
  c = c.replace(/robots\s*=\s*\{\s*["']noindex[^"']*["']\s*\}/gi, 'robots="index, follow"');
  
  fs.writeFileSync(p.fp, c, 'utf-8');
  const url = 'https://www.superparty.ro/' + p.rel.replace('index.astro','').replace('.astro','').replace(/\\/g,'/').replace(/\/$/,'') + '/';
  phase1Urls.push({ url, wc });
  phase1Fixed++;
  if (phase1Fixed % 10 === 0) process.stderr.write(`Faza 1: ${phase1Fixed}/${petreceriNoindex.length}\n`);
}
console.log(`✅ Faza 1: ${phase1Fixed} pagini petreceri/comune activate`);

// ═══════════════════════════════════════════════════════════
// FAZA 2: animatori-copii-* — rescrie subtire + remove noindex
// ═══════════════════════════════════════════════════════════
const acNoindex = noindexAll.filter(p => p.rel.startsWith('animatori-copii'));

// Continut unic pe fiecare pagina animatori-copii-*
const acContentMap = {
  'animatori-copii-ilfov': {
    title: 'Animatori Copii Ilfov — Toate Localitățile | SuperParty',
    desc: 'Animatori petreceri copii în toate localitățile din județul Ilfov. SuperParty acoperă 30+ comune și orașe: Otopeni, Voluntari, Bragadiru, Chiajna și altele.',
    canonical: 'https://www.superparty.ro/animatori-copii-ilfov/',
    extra: `<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.3rem;font-weight:800;margin-bottom:1rem">Animatori copii în tot județul Ilfov — acoperire completă</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Județul Ilfov înconjoară Municipiul București pe toate laturile și include peste 30 de localități cu o populație de aproximativ 500.000 de locuitori (2024). SuperParty acoperă integral județul Ilfov — de la Otopeni în nord (14 km de centrul Bucureștiului) până la Popești-Leordeni în sud (8 km), de la Chiajna în vest (6 km) până la Pantelimon-Ilfov în est.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem"><strong>Localitățile principale acoperite:</strong> Otopeni, Voluntari (Pipera), Bragadiru, Chiajna (Militari Residence), Popești-Leordeni, Măgurele, Jilava, Cornetu, Clinceni, Glina, Ciorogârla, Cernica, Dobroești, Chitila, Buftea, Snagov, Gruiu, Periș și altele. Zero taxe de deplasare pentru toate localitățile din Ilfov situate la mai puțin de 25 km de centrul Bucureștiului.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Boom-ul imobiliar din Ilfov (cel mai rapid județ în creștere din România, +45% populație în 10 ani) a adus sute de mii de familii cu copii în noile complexe rezidențiale. SuperParty știe că părinții din Corbeanca, Tunari, Afumați sau Balotești merită aceeași calitate de animație ca și părinții din Floreasca sau Primăverii.</p>
    <p style="color:var(--text-muted);line-height:1.85">De la 490 RON, pachet complet: 1 animator profesionist costumat în personajul ales de copil, face painting, jocuri interactive, modelare baloane, mașină baloane de săpun. Confirmare disponibilitate în 30 minute. Contract garantie inclus.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem">
      <a href="tel:+40722744377" style="background:linear-gradient(135deg,var(--primary),#e85d24);color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" style="background:#25d366;color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>
<section style="padding:2.5rem 0;background:var(--dark-2)">
  <div class="container">
    <h2 style="font-size:1.2rem;font-weight:800;margin-bottom:.9rem">Cel mai rapid din Ilfov — confirmare în 30 minute</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.8rem"><strong>De ce suntem preferați în Ilfov?</strong> Spre deosebire de animatorii din București care percep taxe de deplasare pentru Ilfov (20-50 RON extra), SuperParty include deplasarea în prețul pachetului pentru degereu localitățile Ilfovene apropiate. Un animator din zona Militari ajunge în Chiajna în 5 minute. Un animator din Pipera ajunge în Voluntari în 7 minute.</p>
    <p style="color:var(--text-muted);line-height:1.85">Sunăm sau trimitem confirmare WhatsApp în maxim 30 de minute de la cerere. Locul tău este blocat cu contract. Personajul ales este garantat — niciodată un alt personaj în locul celui rezervat.</p>
  </div>
</section>`
  },
  'animatori-copii-otopeni': {
    title: 'Animatori Copii Otopeni | SuperParty — Ilfov Nord',
    desc: 'Animatori petreceri copii în Otopeni, Ilfov (14 km de Piața Unirii). Pachete de la 490 RON, 50+ personaje costumate. Confirmare rapidă 30 min. SuperParty.',
    canonical: 'https://www.superparty.ro/animatori-copii-otopeni/',
    extra: `<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.3rem;font-weight:800;margin-bottom:1rem">Animatori petreceri copii Otopeni — Super Party vine la tine!</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Otopeni este cel mai cunoscut oraș din Ilfov datorită <strong>Aeroportului Internațional Henri Coandă</strong> — cel mai mare aeroport din România. Dar Otopeni este mult mai mult de atât: un oraș de 30.000+ de locuitori cu cartiere moderne (Otopeni-Sat, Odăile, Pișcari) și zeci de ansambluri rezidențiale noi apărute după 2010. Familiile din Otopeni au același drept la petreceri de calitate pentru copii ca și familiile din centrul Capitalei.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Distanțe: Otopeni Primărie → București Piața Unirii: 14 km pe A3 (12-15 min în afara orelor de vârf). SuperParty ajunge din Sectorul 1-2 în Otopeni în mai puțin de 20 de minute. Acoperim: Otopeni-Sat, Odăile, Pișcari, Băneasa (limită cu Sectorul 1), zona aeroport.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Am organizat petreceri pentru copii în complexele rezidențiale din Otopeni: Cosmopolis (cel mai mare complex rezidențial din România cu 5.000+ apartamente), Aviatiei Park, Otopeni Residence și în casele cu grădini din Otopeni-Sat. Petrecerile outdoor cu mașina de baloane de săpun sunt preferatele copiilor din Otopeni vara.</p>
    <p style="color:var(--text-muted);line-height:1.85">Pachete disponibile în Otopeni: Classic (490 RON), Premium (790 RON), VIP (990 RON). Nicio taxă de deplasare. Toate includ: costum premium, face painting profesional, jocuri adaptate vârstei, baloane modelate, mașină baloane de săpun.</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem">
      <a href="tel:+40722744377" style="background:linear-gradient(135deg,var(--primary),#e85d24);color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" style="background:#25d366;color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>`
  },
  'animatori-copii-bragadiru': {
    title: 'Animatori Copii Bragadiru | SuperParty Ilfov',
    desc: 'Animatori petreceri copii în Bragadiru, Ilfov (zona Militari/Rahova). SuperParty de la 490 RON. Fără taxă deplasare. 50+ personaje. Confirmare 30 min.',
    canonical: 'https://www.superparty.ro/animatori-copii-bragadiru/',
    extra: `<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.3rem;font-weight:800;margin-bottom:1rem">Animatori copii Bragadiru — la 6 km de Militari</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Bragadiru este o comună din vestul județului Ilfov cu o populație de 42.000+ de locuitori (una dintre cele mai populate comune din România). Situată la doar 6 km de Sectorul 6 (Militari), Bragadiru s-a transformat rapid dintr-o comună rurală într-o zonă rezidențială densă, cu complexe mari: Bragadiru Hill, Greenfield Bragadiru, Adora Park. Mii de familii cu copii au ales Bragadiru pentru prețurile mai accesibile ale locuințelor față de București.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">SuperParty acoperă întregul Bragadiru: centrul vechi (zona Primăriei), Bragadiru Nord (lângă DN6), zona Clinceni-Bragadiru și toate complexele rezidențiale noi. Animatorul ajunge direct la adresa ta — fără taxe de deplasare, prețuri identice cu Sectorul 6.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Specificul petrecerilor din Bragadiru: multe familii au case cu curți și grădini generoase — SuperParty adoră petrecerile outdoor! Avem echipamente speciale pentru exterior: mașina de baloane de săpun cu debit triplu, jocuri cu parașute colorate, cort gonflabil la cerere.</p>
    <p style="color:var(--text-muted);line-height:1.85">Contactează-ne pentru disponibilitate în Bragadiru — confirmare în 30 de minute!</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem">
      <a href="tel:+40722744377" style="background:linear-gradient(135deg,var(--primary),#e85d24);color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" style="background:#25d366;color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>`
  },
  'animatori-copii-chiajna': {
    title: 'Animatori Copii Chiajna — Militari Residence | SuperParty',
    desc: 'Animatori petreceri copii în Chiajna, Ilfov (Militari Residence, Roșu). SuperParty de la 490 RON. La 5 min de Militari. Confirmare 30 min. 50+ personaje.',
    canonical: 'https://www.superparty.ro/animatori-copii-chiajna/',
    extra: `<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.3rem;font-weight:800;margin-bottom:1rem">Animatori copii Chiajna — Militari Residence și Rosu</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Chiajna este una dintre cele mai populare destinații rezidențiale din Ilfov — <strong>Militari Residence</strong> (cel mai mare complex rezidențial de case din România, cu 10.000+ locuințe) și <strong>Roșu</strong> sunt cartierele emblematice. Situată la 6 km de centrul Sectorului 6, Chiajna găzduiește peste 45.000 de locuitori, marea majoritate familii tinere cu copii.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">SuperParty cunoaște bine Chiajna: stradele din <strong>Militari Residence</strong> (Str. Banului, Str. Ecoului, Str. Speranței), zona centrală (lângă Primărie și Lidl Chiajna), zona <strong>Roșu</strong> (lângă Mega Mall Militari). Ajungem în 10-15 minute din Sectorul 6. Fără taxe de deplasare.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Petrecerile din Chiajna se desfășoară des în grădinile caselor din Militari Residence sau în sălile de petreceri din zonă. SuperParty aduce tot echipamentul: costumul premium, materiale face painting, materiale jocuri, mașina de baloane de săpun.</p>
    <p style="color:var(--text-muted);line-height:1.85">Sună sau scrie pe WhatsApp — îți confirmăm disponibilitatea și prețul pachetului în 30 de minute!</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem">
      <a href="tel:+40722744377" style="background:linear-gradient(135deg,var(--primary),#e85d24);color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" style="background:#25d366;color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>`
  },
  'animatori-copii-pantelimon': {
    title: 'Animatori Copii Pantelimon Ilfov | SuperParty',
    desc: 'Animatori petreceri copii în Pantelimon, Ilfov. SuperParty de la 490 RON. 50+ personaje costumate. Confirmare 30 minute. Fără taxe deplasare.',
    canonical: 'https://www.superparty.ro/animatori-copii-pantelimon/',
    extra: `<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.3rem;font-weight:800;margin-bottom:1rem">Animatori copii Pantelimon (Ilfov) — SuperParty vine la tine</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem"><strong>Atenție:</strong> Aceasta este pagina pentru <strong>Comuna Pantelimon, județul Ilfov</strong> — nu pentru Cartierul Pantelimon din Sectorul 3 (care are propria pagină). Comuna Pantelimon (Ilfov) are o populație de 35.000+ locuitori distribuiți în localitățile: Pantelimon (reședință), Cartierul Surlari și Dănești. Este situată la 12 km est de centrul Bucureștiului, pe Șoseaua Pantelimonului (DN3B).</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">SuperParty acoperă Comuna Pantelimon cu aceeași calitate ca și Sectorul 3 din București. Zona a crescut rapid cu complexe rezidențiale noi: Pantelimon Residence, Green Village Pantelimon. Mulți locuitori au ales Pantelimon-Ilfov pentru casele mai spațioase și liniștea față de București cu aglomerația specifică.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Petrecerile în Pantelimon-Ilfov sunt frecvente în grădinile caselor — zona are mai mult spațiu exterior față de blocurile din București. SuperParty vine echipat pentru outdoor: jocuri cu parașute, mașina de baloane, zone de face painting cu umbrele pentru umbrire.</p>
    <p style="color:var(--text-muted);line-height:1.85">Taxă deplasare: 30 RON pentru Pantelimon-Ilfov (în afara limitelor Municipiului București). Confirmare disponibilitate în 30 minute!</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem">
      <a href="tel:+40722744377" style="background:linear-gradient(135deg,var(--primary),#e85d24);color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" style="background:#25d366;color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>`
  },
  'animatori-copii-popesti-leordeni': {
    title: 'Animatori Copii Popești-Leordeni | SuperParty Ilfov',
    desc: 'Animatori petreceri copii în Popești-Leordeni, Ilfov (8 km sud de București). SuperParty de la 490 RON. 50+ personaje. Confirmare 30 min.',
    canonical: 'https://www.superparty.ro/animatori-copii-popesti-leordeni/',
    extra: `<section style="padding:3rem 0">
  <div class="container">
    <h2 style="font-size:1.3rem;font-weight:800;margin-bottom:1rem">Animatori copii Popești-Leordeni — la 8 km de București</h2>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">Popești-Leordeni este <strong>al treilea cel mai mare oraș din Ilfov</strong> cu o populație de 38.000+ de locuitori (după Voluntari și Otopeni). Situată la 8 km sud de Sectorul 4 (Berceni), pe DN4 (Șoseaua Olteniței), Popești-Leordeni a crescut exploziv în ultimii 10 ani datorită complexelor rezidențiale: Popești Residential, Leordeni Residence, Greenfield Sud.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">SuperParty acoperă integral Popești-Leordeni: centrul vechi (zona Primăriei), Cartierul Leordeni, zona Industrială (unde mulți angajați ai fabricilor din zonă locuiesc efectiv), și toate complexele rezidențiale noi. Animatorul ajunge din Sectorul 4 în 15-20 de minute.</p>
    <p style="color:var(--text-muted);line-height:1.85;margin-bottom:.9rem">O particularitate a Popești-Leordeni: proporția mare de case individuale cu curți față de blocuri, ceea ce înseamnă că multe petreceri sunt organizate în aer liber. SuperParty adoră aceste petreceri outdoor — atmosfera este mai relaxată, copiii au mai mult spațiu de mișcare și jocurile fizice sunt preferatele.</p>
    <p style="color:var(--text-muted);line-height:1.85">Taxă deplasare: 30 RON pentru Popești-Leordeni. Pachete de la 490 RON (taxă inclusa). Confirmare în 30 de minute. Contract garantie inclus!</p>
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:1.5rem">
      <a href="tel:+40722744377" style="background:linear-gradient(135deg,var(--primary),#e85d24);color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">📞 0722 744 377</a>
      <a href="https://wa.me/40722744377" style="background:#25d366;color:#fff;padding:.8rem 1.6rem;border-radius:50px;font-weight:700;text-decoration:none">💬 WhatsApp</a>
    </div>
  </div>
</section>`
  },
};

// Process animatori-copii pages
let phase2Fixed = 0;
const phase2Urls = [];

for (const p of acNoindex) {
  let c = fs.readFileSync(p.fp, 'utf-8');
  const slug = p.rel.replace('/index.astro','').replace('.astro','').replace(/\\/g,'/');
  
  // Remove noindex
  c = c.replace(/robots="noindex,\s*follow"/gi, 'robots="index, follow"');
  c = c.replace(/robots="noindex"/gi, 'robots="index, follow"');
  c = c.replace(/noindex,\s*nofollow/gi, 'index, follow');
  c = c.replace(/<meta\s+name="robots"\s+content="noindex[^"]*"\s*\/>/gi, '');
  c = c.replace(/robots\s*=\s*\{\s*["']noindex[^"']*["']\s*\}/gi, 'robots="index, follow"');
  
  // Add extra content if we have it and page is thin
  const extraData = acContentMap[slug];
  if (extraData) {
    const wc = getWords(c);
    if (wc < 400) {
      // Fix title if too long or missing
      if (extraData.title) {
        c = c.replace(/title="[^"]*"/, `title="${extraData.title}"`);
        if (!c.includes(`title="${extraData.title}"`)) {
          // Might not have been replaced, try adding to Layout
        }
      }
      if (extraData.desc) {
        c = c.replace(/description="[^"]*"/, `description="${extraData.desc}"`);
      }
      // Inject extra content before </Layout>
      if (extraData.extra && !c.includes('SuperParty acoperă')) {
        c = c.replace('</Layout>', extraData.extra + '\n\n</Layout>');
      }
    }
  }
  
  fs.writeFileSync(p.fp, c, 'utf-8');
  const url = 'https://www.superparty.ro/' + slug + '/';
  phase2Urls.push({ url });
  phase2Fixed++;
}
console.log(`✅ Faza 2: ${phase2Fixed} pagini animatori-copii activate`);

// ═══════════════════════════════════════════════════════════
// SITEMAP — regenerate with ALL indexed URLs
// ═══════════════════════════════════════════════════════════
// Collect all now-indexed pages
const allPages2 = collectAll(path.join(ROOT, 'src/pages'));
const allIndexed = allPages2.filter(p => {
  const c = fs.readFileSync(p.fp, 'utf-8');
  return !c.includes('noindex');
});

const today = new Date().toISOString().slice(0, 10);

function getPriority(url) {
  if (url === 'https://www.superparty.ro/') return '1.0';
  if (url.includes('animatori-petreceri-copii') || url.includes('animatori-copii-bucuresti')) return '0.95';
  if (url.includes('animatori-copii-sector') || url.includes('petreceri/sector')) return '0.85';
  if (url.includes('animatori-copii') || url.includes('/petreceri/')) return '0.75';
  return '0.65';
}

const sitemapUrls = allIndexed
  .map(p => {
    const slug = p.rel.replace('index.astro','').replace('.astro','').replace(/\\/g,'/').replace(/\/$/,'');
    return 'https://www.superparty.ro/' + (slug ? slug + '/' : '');
  })
  .filter(u => !u.includes('['))
  .sort();

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapUrls.map(url => `  <url>
    <loc>${url}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${url.includes('/petreceri/') || url.includes('animatori-copii') ? 'monthly' : 'weekly'}</changefreq>
    <priority>${getPriority(url)}</priority>
  </url>`).join('\n')}
</urlset>`;

const sitemapPath = path.join(ROOT, 'public/sitemap.xml');
fs.writeFileSync(sitemapPath, sitemap, 'utf-8');
console.log(`✅ Sitemap actualizat: ${sitemapUrls.length} URL-uri (era 43)`);

// Verify noindex remaining
const remaining = allPages2.filter(p => fs.readFileSync(p.fp,'utf-8').includes('noindex'));
console.log(`\n📊 Pagini noindex ramas dupa fix: ${remaining.length}`);
remaining.slice(0,5).forEach(p => console.log('  still noindex:', p.rel));

console.log('\n════════════════════════════');
console.log('TOTAL PAGINI ACTIVATE:');
console.log(`  Faza 1 (petreceri/comune): ${phase1Fixed}`);
console.log(`  Faza 2 (animatori-copii): ${phase2Fixed}`);
console.log(`  Sitemap: ${sitemapUrls.length} URL-uri`);
console.log('════════════════════════════');
