import fs from 'fs';
import path from 'path';

const csvPath = path.join(process.cwd(), 'reports', 'seo', 'raport_pagina_cu_pagina.csv');
const lines = fs.readFileSync(csvPath, 'utf8').trim().split('\n');

let mdContent = '# Audit SEO Pagină cu Pagină (Toate cele 1659 Fișiere V8)\\n\\n';
mdContent += 'Ai cerut tabelul complet, pagină cu pagină, iar acesta este rezultatul brut (zero medii). Duplicatul a fost calculat exclusiv între pagina X și cea mai apropiată pagină Y din site.\\n\\n';
mdContent += '| Pagina URL | Cuvinte | Duplicat Maxim (%) | Cea mai asemănătoare | Status Indexare GSC | Erori GSC |\\n';
mdContent += '| :--- | :--- | :--- | :--- | :--- | :--- |\\n';

for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split(',');
    if (parts.length >= 6) {
        let url = parts[0].replace('https://www.superparty.ro', '');
        let words = parts[1];
        let dup = parts[2];
        let sim = parts[3].replace('.mdx', '');
        let status = parts[4];
        let error = parts[5];
        
        mdContent += `| ${url} | ${words} | ${dup} | ${sim} | ${status} | ${error} |\n`;
    }
}

const artifactPath = path.join('C:', 'Users', 'ursac', '.gemini', 'antigravity', 'brain', 'a23aa650-b836-4099-b8ea-3f57251ef557', 'tabel_complet_pagini.md');
fs.writeFileSync(artifactPath, mdContent, 'utf8');
console.log('Artifact generat cu succes cu ' + (lines.length - 1) + ' randuri!');
