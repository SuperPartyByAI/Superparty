import fs from 'fs';
import path from 'path';

const seoDir = path.join(process.cwd(), 'src', 'content', 'seo-articles');
const files = fs.readdirSync(seoDir).filter(f => f.endsWith('.md'));

console.log('🚨 Pornesc Misiunea V8 Frontmatter Rescue peste ' + files.length + ' fisiere...');
let repaired = 0;

for (const file of files) {
  const filePath = path.join(seoDir, file);
  const content = fs.readFileSync(filePath, 'utf-8');
  
  // Transformam ORICE format de line-endings stricat 
  // (gen \r\n, \r singuratic, \n\r, etc.) in \n-uri pure de UNIX.
  const unixContent = content.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  
  // Reducem secventele stupide de tip \n\n\n\n\n create de injectiile gresite
  const cleanContent = unixContent.replace(/\n{3,}/g, '\n\n');

  if (content !== cleanContent) {
    fs.writeFileSync(filePath, cleanContent, 'utf-8');
    repaired++;
  }
}

console.log(`✅ OOM EVITAT! Am reparat si normalizat sintaxa YAML AST in ${repaired} de fisiere. V8 Engine ul respira din nou!`);
