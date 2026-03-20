const fs = require('fs');
let c = fs.readFileSync('scripts/spintax_v5.mjs', 'utf8');
c = c.replace(/\\`/g, '`');
c = c.replace(/\\\\\{/g, '\\{');
c = c.replace(/\\\\\}/g, '\\}');
c = c.replace(/\\\\\$/g, '\\$');
fs.writeFileSync('scripts/spintax_v5.mjs', c);
console.log('Fixed syntax safely');
