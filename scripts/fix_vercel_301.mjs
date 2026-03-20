// fix_vercel_301.mjs — inlocuieste permanent:true cu statusCode:301 in vercel.json
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const fp = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'vercel.json');
let c = fs.readFileSync(fp, 'utf-8');
const before = (c.match(/"permanent": true/g)||[]).length;
// Inlocuieste permanent:true cu statusCode:301 (Vercel recunoaste statusCode pentru 301 explicit)
c = c.replace(/"permanent": true/g, '"statusCode": 301');
fs.writeFileSync(fp, c, 'utf-8');
const after = (c.match(/"statusCode": 301/g)||[]).length;
process.stdout.write(`Inlocuit: ${before} "permanent":true → "statusCode":301\nTotal redirecturi 301: ${after}\n`);
// Valideaza JSON
try { JSON.parse(c); process.stdout.write('✅ vercel.json JSON valid\n'); }
catch(e) { process.stdout.write('⛔ JSON invalid: '+e.message+'\n'); }
