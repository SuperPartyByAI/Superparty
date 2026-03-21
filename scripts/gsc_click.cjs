const puppeteer = require('puppeteer-core');
(async () => {
    try {
        console.log("Conectare la Chrome-ul activ pe port 9222...");
        const browser = await puppeteer.connect({ browserURL: 'http://localhost:9222' });
        const pages = await browser.pages();
        let page = pages.find(p => p.url().includes('search-console'));
        
        if (!page) {
            console.log("Nu am gasit GSC. Deschid tab nou...");
            page = await browser.newPage();
            await page.goto('https://search.google.com/search-console', {waitUntil: 'networkidle2'});
        } else {
            console.log("Aducem pagina GSC in prim plan...");
            await page.bringToFront();
        }

        console.log("Pagina GSC deschisa. Cautam bara de inspectie...");
        
        // Wait for the inspect Search Bar
        const searchSelector = 'input'; // Just focus the first input if aria-label is flaky
        await page.waitForTimeout(3000); // Give it time to react
        
        // Use evaluate to find the exact search bar by aria-label since input[aria-label] can be tricky
        await page.evaluate(() => {
            const inputs = document.querySelectorAll('input');
            for(let inp of inputs) {
                if(inp.getAttribute('aria-label') && inp.getAttribute('aria-label').includes('Inspect')) {
                    inp.focus();
                }
            }
        });
        
        // Wait 1s and then TYPE
        await page.waitForTimeout(1000);
        // We can just type directly if focus worked
        const urlToPing = "https://www.superparty.ro/animatori-petreceri-copii";
        await page.keyboard.type(urlToPing, {delay: 50});
        await page.keyboard.press('Enter');
        
        console.log("Apelam analiza...");
        // Wait for the "Solicită indexarea" button to appear.
        let indexBtnClicked = false;
        
        for(let i=0; i<30; i++) {
            await page.waitForTimeout(2000);
            const btns = await page.$$('div[role="button"]');
            for(let btn of btns) {
                const text = await btn.evaluate(el => el.innerText || "");
                if(text.toUpperCase().includes('SOLICITĂ INDEXAREA') || text.toUpperCase().includes('REQUEST INDEXING')) {
                    console.log("Buton GASIT! Efectuam click invizibil...");
                    await btn.click();
                    indexBtnClicked = true;
                    break;
                }
            }
            if(indexBtnClicked) break;
        }
        
        if(!indexBtnClicked) {
            console.log("EROARE: Nu am gasit butonul Solicită Indexarea in intervalul de 60s.");
        } else {
            console.log("Succes! Robotul a apasat click-ul interzis. Asteptam 10 secunde sa proceseze Google...");
            await page.waitForTimeout(10000);
        }
        
        await browser.disconnect();
        console.log("Misiune Hacker Mode INCHEIATA.");
    } catch(err) {
        console.error("Crash la automatizare:", err);
    }
})();
