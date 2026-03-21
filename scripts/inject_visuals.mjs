import fs from 'fs';
import path from 'path';

function findImages(dir, fileList = []) {
  if (!fs.existsSync(dir)) return fileList;
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory()) {
      findImages(filePath, fileList);
    } else if (filePath.match(/\.(webp|jpg|jpeg|png)$/i)) {
      if (filePath.includes('optimized') || file.includes('animatori') || file.includes('petrecere')) {
        let rel = filePath.split('public')[1];
        if (rel) {
           rel = rel.replace(/\\/g, '/');
           if (!rel.startsWith('/')) rel = '/' + rel;
           fileList.push(rel);
        }
      }
    }
  }
  return fileList;
}

const publicDir = path.join(process.cwd(), 'public');
let allImages = findImages(publicDir);

if (allImages.length === 0) {
  allImages = ['/optimized/animatori-1.webp', '/optimized/batman.webp', '/optimized/cenusareasa-si-print-1.webp'];
}

const seoDir = path.join(process.cwd(), 'src', 'content', 'seo-articles');
const files = fs.readdirSync(seoDir).filter(f => f.endsWith('.md'));

let injectedTotal = 0;
let modifiedFiles = 0;

for (const file of files) {
  const filePath = path.join(seoDir, file);
  let content = fs.readFileSync(filePath, 'utf-8');
  
  if (content.includes('![')) {
     // Skip daca am bagat deja azi
     continue;
  }

  const lines = content.split('\n');
  let newLines = [];
  let emptyLineCount = 0;
  
  // Excludem block-ul incapsulat de frontmatter (---)
  let insideFrontmatter = false;
  let dashesSeen = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    newLines.push(line);
    
    if (line.trim() === '---') {
      dashesSeen++;
      if (dashesSeen === 1) insideFrontmatter = true;
      if (dashesSeen === 2) insideFrontmatter = false;
      continue;
    }

    if (!insideFrontmatter && line.trim() === '') {
      emptyLineCount++;
      // La al 4-lea si 9-lea spatiu (paragraf) dupa frontmatter bagam artileria vizuala
      if (emptyLineCount === 4 || emptyLineCount === 9) {
        const randomImg = allImages[Math.floor(Math.random() * allImages.length)];
        const citySEO = file.replace('.md', '').split('-').join(' ');
        
        newLines.push(`![Animatori petreceri copii in ${citySEO} Baloane, Jucarii si Zâmbete Realiste](${randomImg})`);
        newLines.push('');
        injectedTotal++;
      }
    }
  }
  
  if (newLines.length !== lines.length) {
    fs.writeFileSync(filePath, newLines.join('\n'), 'utf-8');
    modifiedFiles++;
  }
}

console.log(`Bilanț final: ${files.length} fișiere SEO de cartier/oras procesate.`);
console.log(`DWELL TIME ASIGURAT: ${injectedTotal} portrete fotografice HD au prins radacini vitale in ${modifiedFiles} de pagini moarte!`);
