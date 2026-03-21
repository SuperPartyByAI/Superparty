import fs from 'fs';
import path from 'path';

const contentDir = path.join(process.cwd(), 'src/content/seo-articles');
const targetKeyword = /animatori petreceri copii/i;
const targetUrl = '/animatori-petreceri-copii/';

let modifiedFiles = 0;
let totalLinksInjected = 0;

function processFile(filePath) {
    let content = fs.readFileSync(filePath, 'utf-8');
    const parts = content.split('---');
    if (parts.length < 3) return; // skip
    
    const frontmatter = parts[1];
    let body = parts.slice(2).join('---');

    let lines = body.split('\n');
    let injected = false;

    // Line-by-Line Safe Scanner
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        
        // Skip images, H1/H2, lists, and lines that already contain a markdown link
        if (line.startsWith('!') || line.startsWith('#') || line.startsWith('-') || line.includes('](') || line === '') {
            continue;
        }
        
        // If line contains the target keyword naturally in prose
        if (targetKeyword.test(line)) {
            // Replace the keyword with a powerful Internal DoFollow link
            lines[i] = lines[i].replace(targetKeyword, (match) => `[${match}](${targetUrl})`);
            injected = true;
            break; // Stop after strictly 1 injection per file (to maintain Google credibility)
        }
    }

    if (injected) {
        const newContent = `---${frontmatter}---${lines.join('\n')}`;
        fs.writeFileSync(filePath, newContent, 'utf-8');
        modifiedFiles++;
        totalLinksInjected++;
    }
}

function walkDir(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            walkDir(fullPath);
        } else if (file.endsWith('.md')) {
             processFile(fullPath);
        }
    }
}

console.log(`[START] Lansez robotul Wikipedia pentru Pilonul Central...`);
walkDir(contentDir);
console.log(`[SUCCESS] Panza interna a fost unificata matematic.`);
console.log(`- Fisiere SEO modificate: ${modifiedFiles}`);
console.log(`- Voturi PageRank pompate spre Root: ${totalLinksInjected}`);
