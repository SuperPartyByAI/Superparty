// googlebot_real_test.mjs
// Simuleaza exact ce vede Googlebot cand acceseaza URL-urile problematice din GSC
// Testeaza: sitemap-uri, pagini 404, redirecturi, duplicate, canonice
import https from 'https';
import http from 'http';

// Googlebot User-Agent real
const GOOGLEBOT_UA = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)';

function fetch_url(url, follow = false) {
  return new Promise((resolve) => {
    const protocol = url.startsWith('https') ? https : http;
    const req = protocol.get(url, {
      headers: {
        'User-Agent': GOOGLEBOT_UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ro,en;q=0.5',
      },
      timeout: 10000,
    }, (res) => {
      let body = '';
      res.on('data', d => body += d);
      res.on('end', () => {
        // Extrage elemente SEO din HTML
        const title = (body.match(/<title[^>]*>([^<]{1,100})<\/title>/i)||[])[1]||'';
        const canonical = (body.match(/rel="canonical"\s+href="([^"]{1,200})"/)||body.match(/href="([^"]{1,200})"\s+rel="canonical"/)||[])[1]||'';
        const noindex = /noindex/.test(body);
        const h1 = (body.match(/<h1[^>]*>([^<]{1,100})<\/h1>/i)||[])[1]||'';
        const hasSchema = body.includes('application/ld+json') || body.includes('@context');
        const wordCount = body.replace(/<[^>]+>/g,' ').split(/\s+/).filter(w=>w.length>2).length;
        const metaDesc = (body.match(/name="description"\s+content="([^"]{1,200})"/i)||body.match(/content="([^"]{1,200})"\s+name="description"/i)||[])[1]||'';
        resolve({
          status: res.statusCode,
          location: res.headers.location || '',
          contentType: res.headers['content-type'] || '',
          size: body.length,
          title, canonical, noindex, h1, hasSchema, wordCount, metaDesc,
          body200: body.slice(0, 300),
        });
      });
    });
    req.on('error', (e) => resolve({ status: 0, error: e.message }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, error: 'TIMEOUT' }); });
  });
}

function print(msg) { process.stdout.write(msg + '\n'); }
function sep(title) { print(`\n${'═'.repeat(60)}\n  ${title}\n${'═'.repeat(60)}`); }

// URL-urile REALE din GSC pe categorii
const TEST_URLS = {
  'SITEMAPS (Nu s-a putut prelua)': [
    'https://www.superparty.ro/sitemap.xml',
    'https://www.superparty.ro/sitemap_index.xml',
  ],
  '404 (20 pagini in GSC)': [
    'https://www.superparty.ro/petreceri/animator-mickey-mouse-petreceri-copii-bucuresti',
    'https://www.superparty.ro/petreceri/animator-batman-petreceri-copii-bucuresti',
    'https://www.superparty.ro/petreceri/animator-paw-patrol-petreceri-copii-bucuresti',
    'https://www.superparty.ro/petreceri/animator-pikachu-petreceri-copii-bucuresti',
    'https://www.superparty.ro/petreceri/animator-spiderman-petreceri-copii-bucuresti',
    'https://www.superparty.ro/petreceri/animator-moana-petreceri-copii-bucuresti',
    'https://www.superparty.ro/petreceri/animator-rapunzel-petreceri-copii-bucuresti',
    'https://www.superparty.ro/balonase-modelate',
    'https://www.superparty.ro/animatoare-botez',
    'https://www.superparty.ro/blog/',
  ],
  'REDIRECTURI (31 pagini in GSC)': [
    'https://www.superparty.ro/animatori-petreceri',
    'https://www.superparty.ro/vata-de-zahar',
    'https://www.superparty.ro/popcorn-masina',
    'https://www.superparty.ro/animatori-petreceri-copii/',
    'https://www.superparty.ro/contact/',
  ],
  'DUPLICATE FARA CANONICAL (212 pagini)': [
    'https://www.superparty.ro/petreceri/animatori-petreceri-copii-cenusareasa-domnesti',
    'https://www.superparty.ro/petreceri/petrecere-tematica-incredibles-copii-bucuresti',
    'https://www.superparty.ro/petreceri/animatori-petreceri-copii-miraculous-ladybug-copaceni',
    'https://www.superparty.ro/petreceri/animatori-petreceri-copii-iasi-superparty',
    'https://www.superparty.ro/petreceri/animatori-petreceri-copii-iron-man-chiajna',
    'https://www.superparty.ro/petreceri/sfaturi-ghiduri',
  ],
  'EROARE REDIRECTIONARE (1 pagina)': [
    'https://superparty.ro/animatori-petreceri-copii',
  ],
  'PAGINI PRINCIPALE (trebuie 200+canonical+schema)': [
    'https://www.superparty.ro/',
    'https://www.superparty.ro/animatori-petreceri-copii',
    'https://www.superparty.ro/recenzii',
    'https://www.superparty.ro/animatori-copii-sector-1',
  ],
};

print(`\n🤖 SIMULARE GOOGLEBOT — SUPERPARTY.RO — ${new Date().toISOString().slice(0,19).replace('T',' ')}`);
print(`User-Agent: ${GOOGLEBOT_UA}\n`);

const issues = [];
let total = 0;

for (const [category, urls] of Object.entries(TEST_URLS)) {
  sep(category);
  for (const url of urls) {
    total++;
    const r = await fetch_url(url);
    const shortUrl = url.replace('https://www.superparty.ro','').replace('https://superparty.ro','[no-www]') || '/';
    
    if (r.status === 0) {
      print(`⛔ ERROR  ${shortUrl}`);
      print(`   Eroare: ${r.error}`);
      issues.push({url, issue: 'CONEXIUNE ESUATA: '+r.error});
    } else if (category.includes('SITEMAP')) {
      const isXml = r.contentType.includes('xml');
      const urlCount = (r.body200.match(/<loc>/g)||[]).length;
      print(`${r.status===200?'✅':'⛔'} ${r.status} — ${shortUrl}`);
      print(`   ContentType: ${r.contentType}`);
      print(`   Size: ${r.size} bytes | XML valid: ${isXml?'DA':'NU'}`);
      print(`   <loc> in primul chunk: ${urlCount}`);
      if(r.status !== 200 || !isXml) issues.push({url, issue:`Sitemap status=${r.status} xml=${isXml}`});
    } else if (category.includes('404')) {
      const expected = r.status === 301 || r.status === 308 ? '→ REDIRECT' : r.status === 404 ? '→ 404 ⛔' : `→ ${r.status}`;
      const icon = r.status === 301 ? '✅' : r.status === 308 ? '🟡' : r.status === 200 ? '🔵' : '⛔';
      print(`${icon} ${r.status} ${expected} — ${shortUrl}`);
      if(r.location) print(`   Redirect catre: ${r.location}`);
      if(r.status === 404) issues.push({url, issue:'404 NEACOPERIT'});
      if(r.status === 308) issues.push({url, issue:'308 in loc de 301 (SEO suboptimal)'});
      if(r.status === 200) issues.push({url, issue:'200 fara redirect — pagina inca viva!'});
    } else if (category.includes('REDIRECT')) {
      const icon = r.status === 301 ? '✅' : r.status === 308 ? '🟡' : r.status === 200 ? '🔵' : '⛔';
      print(`${icon} ${r.status} — ${shortUrl}  →  ${r.location||'(no location)'}`);
      if(r.status === 308) issues.push({url, issue:'308 in loc de 301'});
      if(r.status > 400) issues.push({url, issue:`Eroare ${r.status}`});
    } else if (category.includes('DUPLICATE')) {
      const icon = r.status !== 200 ? '⛔' : r.canonical ? '✅' : '🔴';
      print(`${icon} ${r.status} — ${shortUrl}`);
      if(r.canonical) print(`   canonical: ${r.canonical}`);
      else print(`   ⛔ LIPSESTE canonical in HTML!`);
      if(r.noindex) print(`   ⛔ ARE noindex — Google nu va indexa!`);
      print(`   H1: "${r.h1.slice(0,50)||'LIPSA'}"`);
      print(`   Schema: ${r.hasSchema?'✅':'⛔'} | Cuvinte: ${r.wordCount}`);
      if(!r.canonical) issues.push({url, issue:'LIPSA canonical in HTML render'});
    } else if (category.includes('EROARE')) {
      const icon = r.status === 301 ? '✅' : r.status === 308 ? '🟡' : '⛔';
      print(`${icon} ${r.status} — ${shortUrl}`);
      if(r.location) print(`   Redirect catre: ${r.location}`);
      if(r.status === 308) issues.push({url, issue:'308 in loc de 301 pentru non-www'});
    } else {
      // Pagini principale
      const icon = r.status===200 && r.canonical && r.hasSchema && !r.noindex ? '✅' : '⚠️';
      print(`${icon} ${r.status} — ${shortUrl}`);
      print(`   Title: "${r.title.slice(0,60)}"`);
      print(`   canonical: ${r.canonical ? r.canonical.slice(-40) : '⛔ LIPSA'}`);
      print(`   Schema: ${r.hasSchema?'✅':'⛔'} | noindex: ${r.noindex?'⛔ DA':'✅ NU'} | cuvinte: ${r.wordCount}`);
      print(`   description: "${r.metaDesc.slice(0,60)}"`);
      if(!r.canonical) issues.push({url, issue:'LIPSA canonical'});
      if(!r.hasSchema) issues.push({url, issue:'LIPSA schema'});
      if(r.noindex) issues.push({url, issue:'NOINDEX prezent'});
    }
  }
}

// SUMAR FINAL
sep('SUMAR FINAL GOOGLEBOT');
print(`Total URL-uri testate:  ${total}`);
print(`Probleme detectate:     ${issues.length}`);
if (issues.length === 0) {
  print(`\n🏆 PERFECT — Googlebot nu va gasi nicio problema!`);
} else {
  print(`\nProbleme de rezolvat:`);
  issues.forEach((iss, i) => {
    print(`  ${i+1}. [${iss.issue}]`);
    print(`     ${iss.url.replace('https://www.superparty.ro','')}`);
  });
}
