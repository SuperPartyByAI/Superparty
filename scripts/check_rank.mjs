import puppeteer from 'puppeteer-core';

(async () => {
    const keywords = [
        "animatori petreceri copii",
        "animatori copii",
        "ursitoare botez bucuresti",
        "animatori copii sector 1",
        "animatori copii ilfov"
    ];
    
    const executablePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

    try {
        console.log("Pornim interogarea Live a serverelor Google pentru 15 cuvinte cheie de top...");
        const browser = await puppeteer.launch({
            executablePath: executablePath,
            headless: "new",
            args: [
                '--no-sandbox', 
                '--disable-setuid-sandbox', 
                '--window-size=1920,1080', 
                '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"'
            ]
        });
        
        const page = await browser.newPage();
        
        for(let i=0; i<keywords.length; i++) {
            const keyword = keywords[i];
            
            await page.goto(`https://www.google.ro/search?q=${encodeURIComponent(keyword)}&num=30`, { waitUntil: 'domcontentloaded', timeout: 30000 });
            
            // Check for Captcha / Consent
            const isCaptcha = await page.$eval('form[action="/errors/"], form#captcha-form', () => true).catch(() => false);
            if(isCaptcha) {
                console.log(`[EROARE] Google a blocat interogările cu CAPTCHA! Ne-am oprit la cuvântul ${i+1}.`);
                break;
            }
            
            // Agree to consent if it pops up
            await page.evaluate(() => {
                const agreeBtn = Array.from(document.querySelectorAll('button')).find(btn => btn.innerText.includes('Accept'));
                if(agreeBtn) agreeBtn.click();
            }).catch(() => {});
            
            const results = await page.evaluate(() => {
                const links = Array.from(document.querySelectorAll('#search .g a[href]'));
                const validUrls = links.map(a => a.href).filter(href => href.startsWith('http') && !href.includes('google.') && !href.includes('youtube.'));
                return [...new Set(validUrls)]; // remove duplicates
            });
            
            let rank = -1;
            let foundUrl = "";
            for(let j=0; j<results.length; j++) {
                if(results[j].includes('superparty.ro')) {
                    rank = j + 1;
                    foundUrl = results[j];
                    break;
                }
            }
            
            if(rank > 0) {
                console.log(`[Rank ${rank}] | "${keyword}" -> URL: ${foundUrl.split('superparty.ro')[1] || '/'}`);
            } else {
                console.log(`[NEGASIT top 30] | "${keyword}"`);
            }
            
            // Pause 3-5 seconds to evade anti-bot logic
            await new Promise(r => setTimeout(r, 3000 + Math.random() * 2000));
        }
        
        await browser.close();
        console.log("== Evaluare Generala Finalizata ==");
        
    } catch (e) {
        console.log("Eroare tehnica la Scraping Google:", e.message);
    }
})();
