import fs from 'fs';
const html = fs.readFileSync('c:/Users/ursac/Superparty/reports/seo/lighthouse_super_performance.html', 'utf8');
const match = html.match(/window\.__LIGHTHOUSE_JSON__\s*=\s*({.*});/);
if (match) {
  let out = '';
  const data = JSON.parse(match[1]);
  const cats = data.categories;
  out += 'Scores:\n';
  for (let k in cats) out += (`${k}: ${cats[k].score * 100}\n`);
  const audits = data.audits;
  out += ('\nTop Opportunities:\n');
  const opps = Object.values(audits).filter(a => a.details && a.details.type === 'opportunity' && a.score < 1).sort((a,b) => b.details.overallSavingsMs - a.details.overallSavingsMs);
  opps.slice(0,5).forEach(o => out += (`${o.id} - ${o.title}: ${o.details.overallSavingsMs}ms savings\n`));
  out += ('\nDiagnostics:\n');
  const diag = Object.values(audits).filter(a => a.score !== null && a.score < 1 && !opps.includes(a)).sort((a,b) => (a.score||0) - (b.score||0));
  diag.slice(0,10).forEach(d => out += (`${d.id} - ${d.title}: score ${d.score}\n`));
  fs.writeFileSync('c:/Users/ursac/Superparty/lh_parsed_utf8.txt', out, 'utf8');
} else {
  fs.writeFileSync('c:/Users/ursac/Superparty/lh_parsed_utf8.txt', 'JSON not found in HTML', 'utf8');
}
