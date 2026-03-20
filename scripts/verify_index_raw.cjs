const fs = require('fs');
const path = require('path');

const filePath = path.join(process.cwd(), 'src/pages/index.astro');
const html = fs.readFileSync(filePath, 'utf8');

// Foarte curat: excludem Frontmatter (--- ... ---) ca sa nu numaram codul JS
const bodyStart = html.indexOf('---', 5) + 3;
const bodyText = html.substring(bodyStart);

let text = bodyText.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, ' ');
text = text.replace(/<[^>]+>/g, ' ');
text = text.replace(/[{}]/g, ' '); // Strip astro bindings {}
text = text.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&');
text = text.toLowerCase();

const words = text.match(/[a-zăâîșț]+/g) || [];
const wordCount = words.length;

const phrases = [
  "copilul tau",
  "copilului tau",
  "copii bucuresti",
  "orice petrecere",
  "petreceri copii",
  "vata de zahar",
  "popcorn",
  "baloane cu heliu",
  "arcada baloane"
];

const normalize = str => str.toLowerCase().replace(/ă/g, 'a').replace(/â/g, 'a').replace(/î/g, 'i').replace(/ș/g, 's').replace(/ț/g, 't');
const normText = normalize(text);

console.log("==================================================");
console.log("📊 AUDIT SEMANTIC HONEST (DOVADA INJECȚIEI LSI)");
console.log("==================================================");
console.log(`📝 Număr Total Cuvinte pe Pagină: ${wordCount} (Media Liderilor Top 3: 1627)`);

if (wordCount > 1627) {
  console.log("✅ SUCCES MATEMATIC: S-a depășit media densității oficiale a inamicilor!");
} else {
  console.log("⚠️ ATENȚIE: Volumul încă e sub 1627.");
}

console.log("\n🔍 Raportul de Expresii Organice Injectate:");
for (const phrase of phrases) {
  const normPhrase = normalize(phrase);
  const regex = new RegExp(normPhrase, 'g');
  const matches = normText.match(regex);
  const count = matches ? matches.length : 0;
  console.log(` - "${phrase}": ${count} apariții`);
}

console.log("\n🎩 Magicieni pe pagină? " + (normText.includes('magician') ? "Da (Eroare - Stuffing)" : "0 apariții (Curat!)"));
console.log("==================================================");
