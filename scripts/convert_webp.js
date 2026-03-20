const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const dir = 'public/wp-content/uploads/generated';

async function main() {
  if (!fs.existsSync(dir)) {
    console.log('Directory not found');
    return;
  }
  const files = fs.readdirSync(dir);
  for (const f of files) {
    if (f.endsWith('.png') || f.endsWith('.jpg')) {
      const p = path.join(dir, f);
      const out = path.join(dir, f.replace(/\.(png|jpg)$/, '.webp'));
      if (!fs.existsSync(out)) {
        await sharp(p).webp({ quality: 80 }).toFile(out);
        console.log('Converted ' + f + ' to WebP');
      }
    }
  }
}

main().catch(console.error);
