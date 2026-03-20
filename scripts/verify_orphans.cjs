const fs = require('fs');
const path = require('path');

const sitemapPath = path.join(process.cwd(), 'public/sitemap.xml');
if (!fs.existsSync(sitemapPath)) {
  console.log('EROARE: Sitemap-ul public nu a fost gasit la ' + sitemapPath);
  process.exit(1);
}

const sitemapContent = fs.readFileSync(sitemapPath, 'utf8');
const locRegex = /<loc>(.*?)<\/loc>/gi;
const xmlUrls = new Set();
let match;
while ((match = locRegex.exec(sitemapContent)) !== null) {
  xmlUrls.add(match[1]);
}

const distDir = path.join(process.cwd(), 'dist');
function getHtmlFiles(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory()) {
      if (file !== '_astro' && file !== 'optimized') {
        getHtmlFiles(filePath, fileList);
      }
    } else if (file.endsWith('.html')) {
      fileList.push(filePath);
    }
  }
  return fileList;
}

const physicalFiles = getHtmlFiles(distDir);
let orphans = [];
let totalVerified = 0;

for (const file of physicalFiles) {
  let relativePath = file.replace(distDir, '').replace(/\\/g, '/');
  if (relativePath.endsWith('index.html')) {
    relativePath = relativePath.replace('index.html', '');
  } else if (relativePath.endsWith('.html')) {
    relativePath = relativePath.replace('.html', '');
  }
  
  if (!relativePath.startsWith('/')) {
    relativePath = '/' + relativePath;
  }
  
  if (relativePath.includes('404')) continue;
  
  const expectedUrl = 'https://www.superparty.ro' + relativePath;
  totalVerified++;
  
  if (!xmlUrls.has(expectedUrl)) {
    orphans.push(expectedUrl);
  }
}

console.log('==============================================');
console.log('🤖 GOOGLE SITEMAP ORPHAN PAGE SCANNER V2');
console.log('==============================================');
console.log('🔍 URL-uri Gasite Fizic pe Server: ' + totalVerified);
console.log('📦 URL-uri Declarate Oficial in `sitemap.xml`: ' + xmlUrls.size);
console.log('----------------------------------------------');
if (orphans.length === 0) {
  console.log('✅ REZULTAT EXCELENT: Exact 0 Pagini Orfane detectate!');
  console.log('Toate cele ' + totalVerified + ' pagini V8 sunt perfect integrate si gata sa fie indexate de Google!');
} else {
  console.log('❌ ALERTA: S-au gasit ' + orphans.length + ' pagini izolate (orfane) care nu exista in Harta!');
  console.log('Exemple orfane:');
  orphans.slice(0, 3).forEach(o => console.log(' - ' + o));
}
