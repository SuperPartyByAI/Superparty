// fix_schema_canonical.mjs — adauga schema JSON-LD + canonical la toate paginile lipsa
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, '..');

// Configuratie pentru fiecare pagina fara schema
const PAGE_CONFIG = {
  'animatori-copii-bragadiru/index.astro': {
    name: 'Animatori Copii Bragadiru', city: 'Bragadiru', url: 'https://www.superparty.ro/animatori-copii-bragadiru/',
    area: 'Bragadiru, Ilfov'
  },
  'animatori-copii-bucuresti/index.astro': {
    name: 'Animatori Copii București', city: 'București', url: 'https://www.superparty.ro/animatori-copii-bucuresti/',
    area: 'București'
  },
  'animatori-copii-chiajna/index.astro': {
    name: 'Animatori Copii Chiajna', city: 'Chiajna', url: 'https://www.superparty.ro/animatori-copii-chiajna/',
    area: 'Chiajna, Ilfov'
  },
  'animatori-copii-ilfov/index.astro': {
    name: 'Animatori Copii Ilfov', city: 'Ilfov', url: 'https://www.superparty.ro/animatori-copii-ilfov/',
    area: 'Județul Ilfov'
  },
  'animatori-copii-otopeni/index.astro': {
    name: 'Animatori Copii Otopeni', city: 'Otopeni', url: 'https://www.superparty.ro/animatori-copii-otopeni/',
    area: 'Otopeni, Ilfov'
  },
  'animatori-copii-pantelimon/index.astro': {
    name: 'Animatori Copii Pantelimon', city: 'Pantelimon', url: 'https://www.superparty.ro/animatori-copii-pantelimon/',
    area: 'Pantelimon, Ilfov'
  },
  'animatori-copii-popesti-leordeni/index.astro': {
    name: 'Animatori Copii Popești-Leordeni', city: 'Popești-Leordeni', url: 'https://www.superparty.ro/animatori-copii-popesti-leordeni/',
    area: 'Popești-Leordeni, Ilfov'
  },
  'animatori-copii-sector-1/index.astro': {
    name: 'Animatori Copii Sector 1 București', city: 'Sector 1', url: 'https://www.superparty.ro/animatori-copii-sector-1/',
    area: 'Sector 1, București', canon: 'https://www.superparty.ro/animatori-copii-sector-1/'
  },
  'animatori-copii-sector-2/index.astro': {
    name: 'Animatori Copii Sector 2 București', city: 'Sector 2', url: 'https://www.superparty.ro/animatori-copii-sector-2/',
    area: 'Sector 2, București', canon: 'https://www.superparty.ro/animatori-copii-sector-2/'
  },
  'animatori-copii-sector-3/index.astro': {
    name: 'Animatori Copii Sector 3 București', city: 'Sector 3', url: 'https://www.superparty.ro/animatori-copii-sector-3/',
    area: 'Sector 3, București', canon: 'https://www.superparty.ro/animatori-copii-sector-3/'
  },
  'animatori-copii-sector-4/index.astro': {
    name: 'Animatori Copii Sector 4 București', city: 'Sector 4', url: 'https://www.superparty.ro/animatori-copii-sector-4/',
    area: 'Sector 4, București', canon: 'https://www.superparty.ro/animatori-copii-sector-4/'
  },
  'animatori-copii-sector-5/index.astro': {
    name: 'Animatori Copii Sector 5 București', city: 'Sector 5', url: 'https://www.superparty.ro/animatori-copii-sector-5/',
    area: 'Sector 5, București', canon: 'https://www.superparty.ro/animatori-copii-sector-5/'
  },
  'animatori-copii-sector-6/index.astro': {
    name: 'Animatori Copii Sector 6 București', city: 'Sector 6', url: 'https://www.superparty.ro/animatori-copii-sector-6/',
    area: 'Sector 6, București', canon: 'https://www.superparty.ro/animatori-copii-sector-6/'
  },
  'animatori-copii-voluntari/index.astro': {
    name: 'Animatori Copii Voluntari', city: 'Voluntari', url: 'https://www.superparty.ro/animatori-copii-voluntari/',
    area: 'Voluntari, Ilfov'
  },
  'animatori-petreceri-copii/index.astro': {
    name: 'Animatori Petreceri Copii București', city: 'București', url: 'https://www.superparty.ro/animatori-petreceri-copii/',
    area: 'București și zona metropolitană'
  },
  'index.astro': {
    name: 'SuperParty — Animatori Petreceri Copii', city: 'București', url: 'https://www.superparty.ro/',
    area: 'București și zona metropolitană Ilfov'
  },
};

function buildSchema(cfg) {
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "LocalBusiness",
        "name": "SuperParty",
        "@id": "https://www.superparty.ro/#business",
        "url": "https://www.superparty.ro",
        "telephone": "+40722744377",
        "priceRange": "490-1290 RON",
        "image": "https://www.superparty.ro/icon.png",
        "aggregateRating": {
          "@type": "AggregateRating",
          "ratingValue": "4.9",
          "reviewCount": "1498",
          "bestRating": "5"
        },
        "areaServed": cfg.area,
        "address": {
          "@type": "PostalAddress",
          "addressLocality": "București",
          "addressCountry": "RO"
        }
      },
      {
        "@type": "Service",
        "name": cfg.name,
        "provider": {"@type": "LocalBusiness", "name": "SuperParty", "telephone": "+40722744377"},
        "areaServed": cfg.city,
        "url": cfg.url,
        "offers": [
          {"@type": "Offer", "name": "Pachet Classic", "price": "490", "priceCurrency": "RON", "description": "2 ore animatie, 1 animator, personaj ales"},
          {"@type": "Offer", "name": "Pachet Premium", "price": "790", "priceCurrency": "RON", "description": "3 ore animatie, 1 animator, personaj ales"},
          {"@type": "Offer", "name": "Pachet VIP", "price": "1290", "priceCurrency": "RON", "description": "3 ore animatie, 2 animatori, personaje alese"}
        ]
      },
      {
        "@type": "FAQPage",
        "mainEntity": [
          {"@type":"Question","name":`Organizati animatori in ${cfg.city}?`,"acceptedAnswer":{"@type":"Answer","text":`Da — SuperParty acoperă ${cfg.area}. Sunați la 0722 744 377 cu data și adresa pentru confirmare disponibilitate.`}},
          {"@type":"Question","name":"Ce personaje sunt disponibile?","acceptedAnswer":{"@type":"Answer","text":"Peste 50 de personaje: Elsa, Spiderman, Batman, Sonic, Bluey, Moana, Pikachu, Stitch, Iron Man, PAW Patrol și multe altele. Verificati disponibilitatea la 0722 744 377."}},
          {"@type":"Question","name":"Cât costă un animator pentru petrecere?","acceptedAnswer":{"@type":"Answer","text":"Prețurile încep de la 490 RON (2 ore, Pachet Classic) și ajung la 1.290 RON (Pachet VIP, 3 ore, 2 animatori). Taxa de deplasare se stabileste transparent la rezervare."}},
          {"@type":"Question","name":"Cu cât timp înainte rezervăm?","acceptedAnswer":{"@type":"Answer","text":"Minim 7-14 zile pentru saptamani normale, 3-4 saptamani pentru weekendurile de mai-septembrie. Confirmarea disponibilitatii este gratuita si rapida."}}
        ]
      },
      {
        "@type": "BreadcrumbList",
        "itemListElement": [
          {"@type":"ListItem","position":1,"name":"Acasa","item":"https://superparty.ro"},
          {"@type":"ListItem","position":2,"name":cfg.name,"item":cfg.url}
        ]
      }
    ]
  };
}

let fixed = 0, canonFixed = 0;

for (const [relPath, cfg] of Object.entries(PAGE_CONFIG)) {
  const fp = path.join(ROOT, 'src/pages', relPath);
  if (!fs.existsSync(fp)) { process.stdout.write('NOT FOUND: ' + relPath + '\n'); continue; }
  
  let c = fs.readFileSync(fp, 'utf-8');
  
  // 1. Adauga schema JSON-LD daca lipseste
  if (!/application\/ld\+json|schema\s*=\s*JSON/.test(c)) {
    const schemaJson = JSON.stringify(buildSchema(cfg), null, 2);
    const schemaScript = `\n<script type="application/ld+json">\n${schemaJson}\n</script>`;
    
    // Insereaza inainte de </Layout> sau la finalul fisierului
    const ins = c.lastIndexOf('</Layout>');
    if (ins !== -1) {
      c = c.slice(0, ins) + schemaScript + '\n' + c.slice(ins);
    } else {
      c += schemaScript;
    }
    fixed++;
  }
  
  // 2. Adauga canonical la sectoare (care au Layout fara canonical=)
  if (cfg.canon && !/canonical/.test(c)) {
    // Gaseste <Layout robots= sau <Layout si adauga canonical
    c = c.replace(/(<Layout\s[^>]*?)(\s+robots=)/, `$1\n  canonical="${cfg.canon}"$2`);
    canonFixed++;
  }
  
  fs.writeFileSync(fp, c, 'utf-8');
}

process.stdout.write(`✅ Schema adaugata: ${fixed} pagini\n`);
process.stdout.write(`✅ Canonical adaugat: ${canonFixed} pagini\n`);

// FIX RECENZII
const recenziiPath = path.join(ROOT, 'src/pages/recenzii.astro');
if (fs.existsSync(recenziiPath)) {
  let r = fs.readFileSync(recenziiPath, 'utf-8');
  
  // Verifica ce lipseste
  const hasTitle = /(title|<title)/i.test(r);
  const hasDesc = /description/i.test(r);
  const hasCanon = /canonical/i.test(r);
  const hasSchema = /application\/ld\+json/.test(r);
  
  process.stdout.write(`\nRecenzii: title=${hasTitle} desc=${hasDesc} canon=${hasCanon} schema=${hasSchema}\n`);
  
  // Daca pagina foloseste Layout Astro, adauga atributele lipsa
  if (!hasTitle || !hasDesc || !hasCanon) {
    // Verifica daca are <Layout
    if (/<Layout/.test(r)) {
      // Adauga title, description, canonical la Layout daca lipsesc
      if (!hasTitle) {
        r = r.replace('<Layout', '<Layout\n  title="Recenzii Clienți SuperParty — 1.498 Recenzii Verificate Google 4.9/5"');
        process.stdout.write('Adaugat title la recenzii\n');
      }
      if (!hasDesc) {
        r = r.replace('<Layout', '<Layout\n  description="Citeste recenziile reale ale clientilor SuperParty: 1.498 parinti verificati Google, rating 4.9/5. Petreceri copii cu animatori profesionisti in Bucuresti si Ilfov."');
        process.stdout.write('Adaugata description la recenzii\n');
      }
      if (!hasCanon) {
        r = r.replace('<Layout', '<Layout\n  canonical="https://www.superparty.ro/recenzii/"');
        process.stdout.write('Adaugat canonical la recenzii\n');
      }
    }
  }
  
  // Adauga schema la recenzii
  if (!hasSchema) {
    const revSchema = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "LocalBusiness",
      "name": "SuperParty",
      "url": "https://www.superparty.ro",
      "telephone": "+40722744377",
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.9",
        "reviewCount": "1498",
        "bestRating": "5",
        "worstRating": "1"
      }
    }, null, 2);
    const ins = r.lastIndexOf('</Layout>');
    if (ins !== -1) {
      r = r.slice(0, ins) + `\n<script type="application/ld+json">\n${revSchema}\n</script>\n` + r.slice(ins);
    }
    process.stdout.write('Adaugat schema AggregateRating la recenzii\n');
  }
  
  fs.writeFileSync(recenziiPath, r, 'utf-8');
  process.stdout.write('✅ recenzii.astro fixat\n');
}

// FIX HOMEPAGE — title mai lung + schema
const homePath = path.join(ROOT, 'src/pages/index.astro');
if (fs.existsSync(homePath)) {
  let h = fs.readFileSync(homePath, 'utf-8');
  const curTitle = (h.match(/title="([^"]*)"/) || [])[1] || '';
  if (curTitle.length < 30) {
    h = h.replace(/title="[^"]*"/, 'title="SuperParty — Animatori Petreceri Copii București | de la 490 RON | Rating 4.9/5"');
    process.stdout.write(`Homepage title updated: ${curTitle} -> nou\n`);
    fs.writeFileSync(homePath, h, 'utf-8');
  }
  process.stdout.write('✅ homepage title fixat\n');
}

// Verificare finala rapida
process.stdout.write('\n── Verificare finala ──\n');
let ok=0, fail=0;
for (const [relPath] of Object.entries(PAGE_CONFIG)) {
  const fp = path.join(ROOT, 'src/pages', relPath);
  if (!fs.existsSync(fp)) continue;
  const c = fs.readFileSync(fp, 'utf-8');
  const hasS = /application\/ld\+json|schema\s*=\s*JSON/.test(c);
  const hasC = /canonical/.test(c);
  if (hasS && hasC) { ok++; }
  else { fail++; process.stdout.write(`⛔ ${relPath} — schema:${hasS} canon:${hasC}\n`); }
}
process.stdout.write(`✅ Pagini complete (schema+canonical): ${ok}/${Object.keys(PAGE_CONFIG).length}\n`);
process.stdout.write(`⛔ Pagini incomplete: ${fail}\n`);
