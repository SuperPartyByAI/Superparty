import puppeteer from 'puppeteer-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
import chalk from 'chalk';

puppeteer.use(StealthPlugin());

const KEYWORD = 'animatori petreceri copii bucuresti';
const TARGET_DOMAIN = 'superparty.ro';
const MAX_RESULTS = 30;
const SEARCH_URL = `https://www.google.ro/search?q=${encodeURIComponent(KEYWORD)}&num=30&hl=ro&gl=ro`;

// ─── Consent Handler ────────────────────────────────────────────────────────
async function solveConsentIfPresent(page) {
  try {
    const isConsentPage = await page.evaluate(() =>
      document.querySelector('.saveButtonContainer') !== null ||
      window.location.hostname.includes('consent.google')
    );
    if (!isConsentPage) {
      console.log(chalk.gray('ℹ️  Nu există pagina de consent. Continuăm...'));
      return false;
    }
    console.log(chalk.green('✅ Pagina de consent detectată. Submitem "Acceptă tot"...'));
    await page.evaluate(() => {
      const forms = Array.from(document.querySelectorAll('form[action*="consent.google"]'));
      const acceptForm = forms.find(f => {
        const btn = f.querySelector('input[type="submit"]');
        return btn && (
          btn.getAttribute('aria-label')?.includes('Acceptă') ||
          btn.value?.includes('Acceptă') ||
          f.querySelector('input[name="set_sc"]') !== null
        );
      });
      if (acceptForm) acceptForm.submit();
    });
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });
    console.log(chalk.green(`✅ Consent trecut! URL: ${page.url()}`));
    return true;
  } catch (e) {
    console.log(chalk.gray(`ℹ️  Consent (non-fatal): ${e.message}`));
    return false;
  }
}

// ─── Extragere domenii din pagina curentă ───────────────────────────────────
async function extractDomains(page) {
  return page.evaluate(() => {
    const mainEl =
      document.querySelector('#search') ||
      document.querySelector('#rso') ||
      document.querySelector('#main') ||
      document.body;

    const BLOCKED = [
      'google.com', 'google.ro', 'youtube.com', 'facebook.com',
      'googleadservices.com', '/aclk?', 'support.google.com',
      'maps.google.com', 'accounts.google.com', 'webcache.googleusercontent.com',
      'translate.google', 'policies.google', 'gstatic.com'
    ];

    const allLinks = Array.from(mainEl.querySelectorAll('a[href^="http"]'));
    const domains = allLinks.map(a => {
      const href = a.href;
      if (BLOCKED.some(b => href.includes(b))) return null;
      try {
        const host = new URL(href).hostname.replace(/^www\./, '');
        return host && !host.includes('google') ? host : null;
      } catch { return null; }
    }).filter(Boolean);

    return [...new Set(domains)];
  });
}

// ─── Main ────────────────────────────────────────────────────────────────────
async function run() {
  console.log(chalk.cyan(`\n🚀 RANK CHECKER — SCAN EXTINS (Max ${MAX_RESULTS} rezultate)`));
  console.log(chalk.gray(`🔍 Keyword: "${KEYWORD}"`));
  console.log(chalk.gray(`🎯 Target: ${TARGET_DOMAIN}`));
  console.log(chalk.yellow(`\n⚠️  Dacă apare reCAPTCHA, rezolvă-l MANUAL în browser. Ai 60 secunde.\n`));

  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null,
    args: ['--start-maximized', '--no-sandbox', '--disable-setuid-sandbox', '--lang=ro-RO']
  });

  const page = await browser.newPage();
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7' });

  try {
    // 1. Pagina 1
    console.log(chalk.yellow('🛰️  Navigăm la SERP Google RO...'));
    await page.goto(SEARCH_URL, { waitUntil: 'networkidle2' });
    console.log(chalk.gray(`📍 URL: ${page.url()}`));

    // 2. Consent
    await solveConsentIfPresent(page);

    // 3. Așteptăm rezultatele (60s pentru intervenție umană la CAPTCHA)
    console.log(chalk.cyan('⏳ Așteptăm rezultatele (max 60 secunde)...'));
    console.log(chalk.yellow('   → Bifează CAPTCHA dacă apare!'));
    await page.waitForSelector('#search a[href^="http"], #rso a[href^="http"]', { timeout: 60000 });
    console.log(chalk.green('✅ Pagina 1 încărcată!\n'));

    let allDomains = [];
    let pageNum = 1;
    let foundAt = -1;

    // ─── Loop pagini ──────────────────────────────────────────────────────
    while (allDomains.length < MAX_RESULTS && foundAt === -1) {
      console.log(chalk.gray(`--- Pagina ${pageNum} (total găsite: ${allDomains.length}) ---`));

      // Scroll lent ca un utilizator uman
      for (let s = 0; s < 5; s++) {
        await page.evaluate(() => window.scrollBy(0, 500));
        await new Promise(r => setTimeout(r, 400));
      }
      await new Promise(r => setTimeout(r, 800));

      // Extrage domenii din pagina curentă
      const pageDomains = await extractDomains(page);

      // Adaugă doar cele noi
      for (const d of pageDomains) {
        if (!allDomains.includes(d)) {
          allDomains.push(d);
          if (d.includes(TARGET_DOMAIN)) {
            foundAt = allDomains.length;
            console.log(chalk.bgGreen.black.bold(`  ⚡ SUPERPARTY DETECTAT în timp real la poziția ${foundAt}!`));
          }
        }
        if (allDomains.length >= MAX_RESULTS) break;
      }

      if (foundAt !== -1 || allDomains.length >= MAX_RESULTS) break;

      // Încearcă să meargă la pagina următoare
      const nextBtn = await page.$('a#pnnext, a[aria-label="Pagina următoare"], a[aria-label="Next"]');
      if (nextBtn) {
        console.log(chalk.yellow(`➡️  Mergem la pagina ${pageNum + 1}...`));
        await nextBtn.click();
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 });
        pageNum++;
      } else {
        console.log(chalk.gray('ℹ️  Nu mai există pagini de rezultate.'));
        break;
      }
    }

    // 4. Screenshot DOVADA
    await page.screenshot({ path: 'DOVADA_SERP.png', fullPage: false });
    console.log(chalk.magenta('\n📸 Screenshot salvat: DOVADA_SERP.png'));

    // 5. Output Final
    console.log(chalk.cyan(`\n📊 REZULTATE FINALE (${allDomains.length} domenii unice):`));
    console.log(chalk.gray('──────────────────────────────────────────'));

    allDomains.forEach((domain, idx) => {
      const pos = idx + 1;
      const line = `${String(pos).padStart(2, ' ')}. ${domain}`;
      if (domain.includes(TARGET_DOMAIN)) {
        console.log(chalk.bgGreen.black.bold(`${line}  ◀◀◀ SUPERPARTY!`));
      } else {
        console.log(line);
      }
    });

    console.log(chalk.gray('──────────────────────────────────────────'));

    if (foundAt !== -1) {
      console.log(chalk.green.bold(`\n🎯 SUPERPARTY.RO → Locul ${foundAt} în Google RO\n`));
    } else {
      console.log(chalk.red.bold(`\n❌ SUPERPARTY.RO nu apare în primele ${allDomains.length} rezultate.`));
      console.log(chalk.gray('💡 Site-ul nu e indexat pentru acest keyword sau e după pagina 3.\n'));
    }

  } catch (err) {
    if (err.message?.includes('timeout')) {
      console.error(chalk.red('\n⏰ TIMEOUT: Rezolvă CAPTCHA-ul manual și rulează din nou!'));
    } else {
      console.error(chalk.red('\n💥 EROARE:'), err.message);
    }
    try { await page.screenshot({ path: 'DOVADA_EROARE.png', fullPage: true }); } catch {}
  } finally {
    console.log(chalk.gray('\nBrowserul rămâne deschis. Apasă CTRL+C când ai terminat.'));
  }
}

run();
