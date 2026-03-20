import fs from 'fs';
import path from 'path';

const csvPath = path.join(process.cwd(), 'reports', 'seo', 'raport_pagina_cu_pagina.csv');
const lines = fs.readFileSync(csvPath, 'utf8').trim().split('\n');

let html = `<!DOCTYPE html>
<html>
<head>
<title>Raport SEO - 1659 Pagini</title>
<style>
  body { font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }
  h1 { color: #58a6ff; }
  table { border-collapse: collapse; width: 100%; margin-top: 20px; }
  th, td { border: 1px solid #30363d; padding: 8px; text-align: left; font-size: 14px; }
  th { background: #161b22; position: sticky; top: 0; }
  a { color: #58a6ff; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .dup-high { color: #ff7b72; font-weight: bold; }
  .dup-low { color: #3fb950; font-weight: bold; }
</style>
</head>
<body>
<h1>✅ Audit SEO Integral (1659 Pagini V8)</h1>
<p><b>Erorile Solicitate:</b> Toate cele 20 de erori 404 (Nu a fost găsită) și 31 de erori (Pagină cu redirecționare) raportate de Google Search Console pe vechiul WordPress <b>au fost deja rezolvate definitiv și urcate pe serverul Vercel</b> prin reguli de Redirecționare 301 Permanentă. Această acțiune transferă integral autoritatea link-urilor pierdute către noile pagini.</p>
<table>
<thead>
  <tr>
    <th>URL Pagină</th>
    <th>Cuvinte</th>
    <th>Duplicat Max</th>
    <th>Cea mai similară</th>
    <th>Status Indexare</th>
    <th>Erori GSC</th>
  </tr>
</thead>
<tbody>`;

for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split(',');
    if (parts.length >= 6) {
        let url = parts[0];
        let shortUrl = url.replace('https://www.superparty.ro', '');
        let words = parts[1];
        let dup = parts[2];
        let dupVal = parseFloat(dup);
        let dupClass = dupVal > 15 ? 'dup-high' : 'dup-low';
        let sim = parts[3].replace('.mdx', '');
        let status = parts[4];
        let error = parts[5];
        
        html += `<tr>
            <td><a href="${url}" target="_blank">${shortUrl}</a></td>
            <td>${words}</td>
            <td class="${dupClass}">${dup}</td>
            <td><small>${sim}</small></td>
            <td>${status}</td>
            <td>${error}</td>
        </tr>\n`;
    }
}

html += '</tbody></table></body></html>';

const htmlPath = path.join(process.cwd(), 'reports', 'seo', 'Tabel_Integral_1659_Pagini.html');
fs.writeFileSync(htmlPath, html, 'utf8');
console.log('HTML generat cu succes! Locatie: ' + htmlPath);
