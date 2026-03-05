#!/usr/bin/env node
/**
 * scripts/optimize-images.mjs
 * Generează versiuni WebP optimizate (thumb 400px + hero 1200px)
 * pentru toate imaginile din public/wp-content/uploads/
 *
 * Rulare: node scripts/optimize-images.mjs
 * Deps:   npm i sharp  (sau npm i -D sharp)
 */
import fs from 'fs';
import path from 'path';

const SRC = process.env.SRC_DIR || 'public/wp-content/uploads';
const OUT = process.env.OUT_DIR || 'public/optimized';
const SIZES = [
    { name: 'thumb', w: 400 },
    { name: 'hero', w: 1200 },
];
const QUALITY = 80;

function walk(dir) {
    if (!fs.existsSync(dir)) return [];
    const result = [];
    for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
        const p = path.join(dir, f.name);
        if (f.isDirectory()) result.push(...walk(p));
        else result.push(p);
    }
    return result;
}

async function main() {
    let sharp;
    try {
        ({ default: sharp } = await import('sharp'));
    } catch {
        console.error('sharp nu e instalat. Rulează: npm i sharp');
        process.exit(1);
    }

    const files = walk(SRC).filter(f => /\.(jpe?g|png|webp)$/i.test(f));
    console.log(`Optimizez ${files.length} imagini din ${SRC} -> ${OUT}`);

    const manifest = {};
    let ok = 0, skipped = 0, errors = 0;

    for (const f of files) {
        const rel = path.relative(SRC, f).replace(/\\/g, '/');
        manifest[rel] = {};

        for (const s of SIZES) {
            const outDir = path.join(OUT, s.name, path.dirname(rel));
            fs.mkdirSync(outDir, { recursive: true });
            const baseName = path.basename(rel, path.extname(rel));
            const outFile = path.join(outDir, `${baseName}.webp`);

            if (fs.existsSync(outFile)) {
                skipped++;
                manifest[rel][s.name] = `/_optimized/${s.name}/${path.dirname(rel)}/${baseName}.webp`;
                continue;
            }

            try {
                await sharp(f).resize({ width: s.w, withoutEnlargement: true }).webp({ quality: QUALITY }).toFile(outFile);
                manifest[rel][s.name] = `/_optimized/${s.name}/${path.dirname(rel)}/${baseName}.webp`;
                ok++;
            } catch (err) {
                console.error(`  ERR: ${rel} (${s.name}):`, err.message);
                errors++;
            }
        }
    }

    // Scrie manifest
    fs.mkdirSync('src/data', { recursive: true });
    fs.writeFileSync('src/data/gallery_optimized_manifest.json', JSON.stringify(manifest, null, 2), 'utf8');

    console.log(`Done: ${ok} generate, ${skipped} deja exist, ${errors} erori`);
    console.log(`Manifest: src/data/gallery_optimized_manifest.json`);
}

main().catch(e => { console.error(e); process.exit(1); });
