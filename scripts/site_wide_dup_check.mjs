// site_wide_dup_check.mjs — Verifica duplicate pe TOT site-ul (145 pagini)
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagesDir = path.join(__dirname, '../src/pages');

function extractText(fp) {
  let c = fs.readFileSync(fp, 'utf-8');
  c = c.replace(/^---[\s\S]*?---/m, '');
  c = c.replace(/<style[\s\S]*?<\/style>/gi, ' ');
  c = c.replace(/<script[\s\S]*?<\/script>/gi, ' ');
  c = c.replace(/\{[^{}]*\}/g, ' ');
  c = c.replace(/<[^>]+>/g, ' ');
  c = c.replace(/https?:\/\/\S+/g, ' ');
  return c.replace(/\s+/g, ' ').trim().toLowerCase();
}

function wordCount(text) {
  return text.split(/\s+/).filter(w => w.length > 3).length;
}

function jaccard(textA, textB, minLen = 6) {
  const setA = new Set(textA.split(/\s+/).filter(w => w.length >= minLen));
  const setB = new Set(textB.split(/\s+/).filter(w => w.length >= minLen));
  if (setA.size === 0 || setB.size === 0) return 0;
  const inter = [...setA].filter(x => setB.has(x)).length;
  const union = new Set([...setA, ...setB]).size;
  return union ? inter / union : 0;
}

// Recursiv fara glob
function walkDir(dir, results = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkDir(full, results);
    } else if (entry.name.endsWith('.astro') && !entry.name.includes('[')) {
      const rel = full.replace(pagesDir + path.sep, '').replace(/\\/g, '/');
      results.push({ rel, abs: full });
    }
  }
  return results;
}

const allFiles = walkDir(pagesDir);


console.log(`Scanez ${allFiles.length} pagini...\n`);

// Extrage text din toate paginile
const pages = [];
for (const { rel, abs } of allFiles) {
  const text = extractText(abs);
  const wc = wordCount(text);
  if (wc < 50) continue; // Skip pagini goale/sablon
  pages.push({ rel, wc, text });
}

console.log(`Pagini cu continut suficient: ${pages.length}\n`);

// Verifica perechi
const THRESHOLD = 0.20; // 20%
const issues = [];
const nearIssues = [];

let checked = 0;
const total = (pages.length * (pages.length - 1)) / 2;
process.stdout.write(`Analizez ${total} perechi...\r`);

for (let i = 0; i < pages.length; i++) {
  for (let j = i + 1; j < pages.length; j++) {
    const sim = jaccard(pages[i].text, pages[j].text);
    checked++;
    if (checked % 500 === 0) process.stdout.write(`  ${checked}/${total} perechi verificate...\r`);
    
    if (sim >= THRESHOLD) {
      issues.push({ a: pages[i].rel, b: pages[j].rel, sim, wcA: pages[i].wc, wcB: pages[j].wc });
    } else if (sim >= 0.15) {
      nearIssues.push({ a: pages[i].rel, b: pages[j].rel, sim });
    }
  }
}

process.stdout.write('\n');

// Grupeaza issues pe categorie
const dupGroups = {
  'pagini/cartiere': issues.filter(x => x.a.includes('petreceri/') && x.b.includes('petreceri/')),
  'sectoare': issues.filter(x => (x.a.includes('sector-') || x.b.includes('sector-'))),
  'ilfov/comune': issues.filter(x => !x.a.includes('petreceri/') || !x.b.includes('petreceri/')),
  'pagini principale': issues.filter(x => !x.a.includes('/') && !x.b.includes('/')),
};

// OUTPUT
console.log('\n' + '═'.repeat(65));
console.log('  REZULTATE AUDIT DUPLICATE — TOT SITE-UL');
console.log('═'.repeat(65));
console.log(`\n  Pagini analizate:  ${pages.length}`);
console.log(`  Perechi verificate: ${total}`);
console.log(`  DUPLICATE (>20%):   ${issues.length}`);
console.log(`  APROAPE (15-20%):   ${nearIssues.length}`);

if (issues.length === 0) {
  console.log('\n  ✅ ZERO pagini cu continut duplicat peste 20%!');
} else {
  console.log('\n\n  ❌ PAGINI CU CONTINUT DUPLICAT:\n');
  const sorted = [...issues].sort((a, b) => b.sim - a.sim);
  sorted.slice(0, 40).forEach(({ a, b, sim, wcA, wcB }) => {
    console.log(`  ${(sim*100).toFixed(1)}%  ${a}`);
    console.log(`         <-> ${b}`);
    console.log(`         (${wcA} vs ${wcB} cuvinte)\n`);
  });
  
  if (sorted.length > 40) {
    console.log(`  ... si inca ${sorted.length - 40} perechi similare\n`);
  }
}

// Grupuri de pagini aproape identice (clustere)
if (issues.length > 0) {
  console.log('  CLUSTERIZARE (grupuri de pagini similare):');
  const graph = {};
  issues.forEach(({ a, b }) => {
    if (!graph[a]) graph[a] = new Set();
    if (!graph[b]) graph[b] = new Set();
    graph[a].add(b);
    graph[b].add(a);
  });
  
  const visited = new Set();
  const clusters = [];
  for (const node of Object.keys(graph)) {
    if (visited.has(node)) continue;
    const cluster = [node];
    visited.add(node);
    for (const neighbor of graph[node]) {
      if (!visited.has(neighbor)) {
        cluster.push(neighbor);
        visited.add(neighbor);
      }
    }
    if (cluster.length > 1) clusters.push(cluster);
  }
  
  clusters.sort((a, b) => b.length - a.length).forEach((cluster, i) => {
    console.log(`\n  Cluster ${i + 1} (${cluster.length} pagini similare intre ele):`);
    cluster.forEach(p => console.log(`    - ${p}`));
  });
}

// Near threshold
if (nearIssues.length > 0 && nearIssues.length <= 20) {
  console.log('\n  ⚠️  APROAPE DE LIMITA (15-20%):\n');
  nearIssues.sort((a, b) => b.sim - a.sim).slice(0, 15).forEach(({ a, b, sim }) => {
    console.log(`  ${(sim*100).toFixed(1)}%  ${a} <-> ${b}`);
  });
}

console.log('\n' + '═'.repeat(65));
console.log(`  VERDICT: ${issues.length === 0 ? '✅ SITE CURAT — ZERO DUPLICATE!' : `❌ ${issues.length} PERECHI CU DUPLICATE (necesita fix)`}`);
console.log('═'.repeat(65));
