const fs = require('fs');
const path = require('path');

const domain = 'https://www.superparty.ro';
const distDir = path.join(__dirname, '../dist');
const outPath = path.join(__dirname, '../public/sitemap.xml');

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

const htmlFiles = getHtmlFiles(distDir);
let urls = '';

htmlFiles.forEach(file => {
  let relativePath = file.replace(distDir, '').replace(/\\/g, '/');
  if (relativePath.endsWith('index.html')) {
    relativePath = relativePath.replace('index.html', '');
  } else if (relativePath.endsWith('.html')) {
    relativePath = relativePath.replace('.html', '');
  }
  if (!relativePath.startsWith('/')) relativePath = '/' + relativePath;
  
  if (!relativePath.includes('404')) {
    urls += `  <url>\n    <loc>${domain}${relativePath}</loc>\n    <changefreq>daily</changefreq>\n    <priority>${relativePath === '/' ? '1.0' : '0.8'}</priority>\n  </url>\n`;
  }
});

const sitemapXML = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}</urlset>`;

fs.writeFileSync(outPath, sitemapXML);
console.log(`Generated sitemap cu SUCCES. Total URL-uri injectate: ${htmlFiles.length}`);
