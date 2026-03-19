// diagnostic.mjs - Rulează cu: node diagnostic.mjs
// Dumpează tot DOM-ul și frame-urile de pe pagina de consent

import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import fs from 'fs';

puppeteer.use(StealthPlugin());

const SEARCH_URL = `https://www.google.ro/search?q=animatori+petreceri+copii+bucuresti&num=30&hl=ro&gl=ro`;

const iPhone13Pro = {
  name: 'iPhone 13 Pro',
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
  viewport: { width: 390, height: 844, deviceScaleFactor: 3, isMobile: true, hasTouch: true, isLandscape: false }
};

async function run() {
  const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox', '--disable-setuid-sandbox', '--lang=ro-RO'] });
  const page = await browser.newPage();
  await page.emulate(iPhone13Pro);
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'ro-RO,ro;q=0.9' });

  await page.goto(SEARCH_URL, { waitUntil: 'networkidle2' });

  // 1. Dump URL
  console.log('URL:', page.url());

  // 2. Dump frames
  const frames = page.frames();
  console.log(`\nFrames (${frames.length}):`);
  frames.forEach((f, i) => console.log(`  [${i}] url: ${f.url()}, name: ${f.name()}`));

  // 3. Dump all button texts from MAIN frame
  const mainButtons = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('button, [role="button"], input[type="button"]')).map(b => ({
      tag: b.tagName,
      id: b.id,
      classes: b.className,
      text: b.textContent?.trim()?.substring(0, 80),
      jsname: b.getAttribute('jsname'),
      type: b.type
    }));
  });
  console.log(`\nMain frame buttons (${mainButtons.length}):`);
  mainButtons.forEach((b, i) => console.log(`  [${i}]`, JSON.stringify(b)));

  // 4. Per frame button dump
  for (const [i, frame] of frames.entries()) {
    try {
      const frameButtons = await frame.evaluate(() => {
        return Array.from(document.querySelectorAll('button, [role="button"]')).map(b => ({
          id: b.id,
          text: b.textContent?.trim()?.substring(0, 80),
          jsname: b.getAttribute('jsname')
        }));
      });
      if (frameButtons.length > 0) {
        console.log(`\nFrame [${i}] ${frame.url()} buttons (${frameButtons.length}):`);
        frameButtons.forEach((b, j) => console.log(`  [${j}]`, JSON.stringify(b)));
      }
    } catch(e) {}
  }

  // 5. Dump outer HTML of body (first 5000 chars)
  const html = await page.evaluate(() => document.body.outerHTML.substring(0, 5000));
  fs.writeFileSync('diagnostic_body.html', html);
  console.log('\nBody HTML salvat în diagnostic_body.html (primele 5000 chars)');

  await browser.close();
}

run().catch(console.error);
