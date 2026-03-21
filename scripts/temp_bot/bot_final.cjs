const puppeteer = require('puppeteer-core');
const { execSync } = require('child_process');
const os = require('os');
const path = require('path');

(async () => {
    console.log("Încerc uciderea proceselor ascunse Chrome (extensii etc) pentru a prelua controlul...");
    try {
        execSync('taskkill /F /IM chrome.exe /T', { stdio: 'ignore' });
    } catch (e) {
        // e normal sa pice daca nu e niciun chrome pornit
    }

    // Asteptam nitel sa se elibereze lock-urile
    await new Promise(r => setTimeout(r, 2000));

    const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
    const userData = path.join(os.homedir(), 'AppData', 'Local', 'Google', 'Chrome', 'User Data');

    console.log("Lansare robot cu datele tale de utilizator...");
    let browser;
    try {
        browser = await puppeteer.launch({
            executablePath: chromePath,
            userDataDir: userData,
            headless: false,
            defaultViewport: null,
            args: ['--start-maximized', '--restore-last-session']
        });
    } catch (err) {
        console.error("\nFATAL: Nu am putut prelua profilul tau. Exista Chrome deschis cumva?", err.message);
        process.exit(1);
    }

    try {
        console.log("Navigare spre Search Console...");
        const page = await browser.newPage();
        await page.goto('https://search.google.com/search-console', { waitUntil: 'networkidle2' });

        console.log("Cautam box-ul de inspectie...");
        await page.waitForTimeout(3000);

        // Click on the input search bar
        await page.evaluate(() => {
            const inputs = document.querySelectorAll('input');
            for (let inp of inputs) {
                const label = inp.getAttribute('aria-label');
                if (label && label.toLowerCase().includes('inspect')) {
                    inp.focus();
                    return;
                }
            }
        });

        await page.waitForTimeout(1000);
        const targetUrl = 'https://www.superparty.ro/animatori-petreceri-copii';
        console.log("Tastam adresa...", targetUrl);
        await page.keyboard.type(targetUrl, { delay: 50 });
        await page.keyboard.press('Enter');

        console.log("Asteptam generarea butonului...");
        let indexClicked = false;
        
        for (let i = 0; i < 30; i++) {
            await page.waitForTimeout(2000);
            const btns = await page.$$('div[role="button"]');
            for (let btn of btns) {
                const text = await btn.evaluate(el => el.innerText || "");
                const upText = text.toUpperCase();
                if (upText.includes('SOLICITĂ INDEXAREA') || upText.includes('REQUEST INDEXING')) {
                    console.log("Am găsit butonul! SĂPĂM CLICKUL...");
                    await btn.click();
                    indexClicked = true;
                    break;
                }
            }
            if (indexClicked) break;
        }

        if (indexClicked) {
            console.log("SUCCES ABSOLUT! Cererea a fost trimisă algoritmic.");
            await page.waitForTimeout(8000); // Wait for the visual confirmation before exit
        } else {
            console.log("Eroare! Nu a putut gasi butonul de indexare. A iesit la timp?");
        }

    } catch (e) {
        console.log("Eroare navigare vizuala:", e);
    } finally {
        await browser.disconnect();
    }
})();
