// googlebot_ascii_test.mjs — fara emoji, output ASCII curat pentru PowerShell
import https from 'https';
import http from 'http';

const GOOGLEBOT_UA = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)';

function fetch_url(url) {
  return new Promise((resolve) => {
    const protocol = url.startsWith('https') ? https : http;
    const req = protocol.get(url, {
      headers: { 'User-Agent': GOOGLEBOT_UA, 'Accept': 'text/html' },
      timeout: 10000,
    }, (res) => {
      let body = '';
      res.on('data', d => body += d);
      res.on('end', () => {
        const title = (body.match(/<title[^>]*>([^<]{1,100})<\/title>/i)||[])[1]||'';
        const canonical = (body.match(/rel="canonical"\s+href="([^"]{1,200})"/)||body.match(/href="([^"]{1,200})"\s+rel="canonical"/)||[])[1]||'';
        const noindex = /noindex/i.test(body);
        const h1match = body.match(/<h1[^>]*>([^<]{1,80})<\/h1>/i);
        const h1 = h1match ? h1match[1].replace(/<[^>]+>/g,'').trim() : '';
        const hasSchema = body.includes('application/ld+json') || body.includes('"@context"');
        const wordCount = body.replace(/<[^>]+>/g,' ').split(/\s+/).filter(w=>w.length>2).length;
        const metaDesc = (body.match(/name="description"[^>]*content="([^"]{1,150})"/i)||body.match(/content="([^"]{1,150})"[^>]*name="description"/i)||[])[1]||'';
        resolve({ status: res.statusCode, location: res.headers.location||'', contentType: res.headers['content-type']||'', size: body.length, title, canonical, noindex, h1, hasSchema, wordCount, metaDesc });
      });
    });
    req.on('error', (e) => resolve({ status: 0, error: e.message }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, error: 'TIMEOUT' }); });
  });
}

const L = (s) => process.stdout.write(s + '\n');
const SEP = (t) => L(`\n------ ${t} ------`);

L(`SIMULARE GOOGLEBOT - SUPERPARTY.RO - ${new Date().toISOString().slice(0,19)}`);
L(`UA: ${GOOGLEBOT_UA}`);

const issues = [];

// ====== SITEMAPS ======
SEP('A. SITEMAPS (Nu s-a putut prelua in GSC)');
for (const url of ['https://www.superparty.ro/sitemap.xml','https://www.superparty.ro/sitemap_index.xml']) {
  const r = await fetch_url(url);
  const isXml = r.contentType.includes('xml');
  const status_icon = r.status===200 && isXml ? 'OK ' : 'ERR';
  L(`[${status_icon}] HTTP ${r.status} | ${r.size}b | ContentType: ${r.contentType}`);
  L(`       URL: ${url}`);
  if (r.status !== 200) issues.push({url, issue: `Sitemap HTTP ${r.status}`});
  if (!isXml) issues.push({url, issue: `Sitemap ContentType gresit: ${r.contentType}`});
}

// ====== 404 ======
SEP('B. PAGINI CU 404 IN GSC (20 pagini)');
const urls404 = [
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
  'https://www.superparty.ro/petreceri/sfaturi-ghiduri',
];
for (const url of urls404) {
  const r = await fetch_url(url);
  const slug = url.replace('https://www.superparty.ro','');
  const icon = r.status===301?'301-OK ':r.status===308?'308-WARN':r.status===200?'200-WARN':r.status===404?'404-ERR ':r.status+'-?  ';
  L(`[${icon}] ${slug}`);
  if (r.location) L(`          -> ${r.location}`);
  if (r.status === 404) issues.push({url: slug, issue: 'INCA 404 - redirect lipseste'});
  if (r.status === 308) issues.push({url: slug, issue: '308 (nu 301) - SEO suboptimal'});
  if (r.status === 200 && !url.includes('sfaturi')) issues.push({url: slug, issue: 'Returneaza 200 - nu e redirect'});
}

// ====== REDIRECTURI ======
SEP('C. PAGINI CU REDIRECTIONARE IN GSC (31 pagini)');
const urlsRedir = [
  'https://www.superparty.ro/animatori-petreceri',
  'https://www.superparty.ro/vata-de-zahar',
  'https://www.superparty.ro/popcorn-masina',
  'https://www.superparty.ro/animatori-petreceri-copii/',
  'https://www.superparty.ro/contact/',
  'https://www.superparty.ro/recenzii/',
  'https://superparty.ro/animatori-petreceri-copii',
];
for (const url of urlsRedir) {
  const r = await fetch_url(url);
  const slug = url.replace('https://www.superparty.ro','').replace('https://superparty.ro','[noWWW]');
  const icon = r.status===301?'301-OK ':r.status===308?'308-WARN':r.status===200?'200-OK? ':r.status+'-?   ';
  L(`[${icon}] ${slug} -> ${r.location||'(no redirect)'}`);
  if (r.status === 308) issues.push({url: slug, issue: '308 in loc de 301'});
}

// ====== DUPLICATE FARA CANONICAL ======
SEP('D. PAGINI DUPLICATE FARA CANONICAL (212 in GSC) - Test 5 exemple');
const urlsDup = [
  'https://www.superparty.ro/petreceri/animatori-petreceri-copii-cenusareasa-domnesti',
  'https://www.superparty.ro/petreceri/petrecere-tematica-incredibles-copii-bucuresti',
  'https://www.superparty.ro/petreceri/animatori-petreceri-copii-miraculous-ladybug-copaceni',
  'https://www.superparty.ro/petreceri/animatori-petreceri-copii-iron-man-chiajna',
  'https://www.superparty.ro/petreceri/animatori-petreceri-copii-ariel-berceni',
];
for (const url of urlsDup) {
  const r = await fetch_url(url);
  const slug = url.replace('https://www.superparty.ro','');
  if (r.status !== 200) {
    L(`[${r.status}] ${slug} -> ${r.location||'ERR'}`);
    if(r.status===404) issues.push({url:slug, issue:'404 - pagina stearsa'});
  } else {
    const hasCanon = !!r.canonical;
    const icon = hasCanon ? 'OK ' : 'ERR';
    L(`[${icon}] ${r.status} ${slug}`);
    L(`       canonical: ${r.canonical || 'LIPSA!'}`);
    L(`       noindex: ${r.noindex ? 'DA (nu se va indexa)' : 'NU (indexabila)'}`);
    L(`       schema: ${r.hasSchema ? 'prezent' : 'LIPSA'} | cuvinte: ${r.wordCount}`);
    L(`       H1: "${r.h1.slice(0,60)||'LIPSA'}"`);
    if (!hasCanon) issues.push({url:slug, issue:'LIPSA tag canonical in HTML renderit de Googlebot'});
    if (!r.hasSchema) issues.push({url:slug, issue:'LIPSA schema JSON-LD'});
  }
}

// ====== PAGINI PRINCIPALE ======
SEP('E. PAGINI PRINCIPALE (trebuie 200 + canonical + schema + no noindex)');
const urlsMain = [
  'https://www.superparty.ro/',
  'https://www.superparty.ro/animatori-petreceri-copii',
  'https://www.superparty.ro/recenzii',
  'https://www.superparty.ro/animatori-copii-sector-1',
  'https://www.superparty.ro/petreceri/adunatii-copaceni',
];
for (const url of urlsMain) {
  const r = await fetch_url(url);
  const slug = url.replace('https://www.superparty.ro','') || '/';
  const ok = r.status===200 && r.canonical && r.hasSchema && !r.noindex;
  L(`[${ok?'OK ':'WARN'}] ${r.status} ${slug}`);
  L(`       title: "${r.title.slice(0,60)}"`);
  L(`       canonical: ${r.canonical ? r.canonical.replace('https://www.superparty.ro','') : 'LIPSA!'}`);
  L(`       schema: ${r.hasSchema?'OK':'LIPSA'} | noindex: ${r.noindex?'DA-ERR':'NU'} | cuvinte: ${r.wordCount}`);
  if (!r.canonical) issues.push({url:slug, issue:'LIPSA canonical'});
  if (!r.hasSchema) issues.push({url:slug, issue:'LIPSA schema'});
  if (r.noindex) issues.push({url:slug, issue:'NOINDEX activ!'});
}

// ====== SUMAR ======
L('\n====== SUMAR FINAL GOOGLEBOT ======');
L(`Total URL-uri testate: ${urls404.length + urlsRedir.length + urlsDup.length + urlsMain.length + 2}`);
L(`Probleme detectate:    ${issues.length}`);
if (issues.length === 0) {
  L('PERFECT - Googlebot nu gaseste nicio problema!');
} else {
  L('\nProbleme detaliate:');
  issues.forEach((iss, i) => L(`  ${i+1}. [${iss.issue}] -- ${iss.url}`));
}
