const https = require('https');
const tests = [
  'https://www.superparty.ro/',
  'https://www.superparty.ro/petreceri/animator-aladin-petreceri-copii-bucuresti'
];

async function runTests() {
  for (let url of tests) {
    console.log(`\nTesting ${url} on LIGHTHOUSE (Google Servers)...`);
    const api = `https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed?url=${url}&category=seo&category=performance&category=best-practices&category=accessibility&strategy=mobile`;
    
    await new Promise(resolve => {
      https.get(api, res => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            if (json.error) {
              console.log("API Error:", json.error.message);
            } else {
              const cats = json.lighthouseResult.categories;
              console.log("MOBILE SCORES:");
              console.log("Performance (Speed):", Math.round(cats.performance.score * 100) + "/100");
              console.log("Accessibility:", Math.round(cats.accessibility.score * 100) + "/100");
              console.log("Best Practices:", Math.round(cats['best-practices'].score * 100) + "/100");
              console.log("SEO Technical:", Math.round(cats.seo.score * 100) + "/100");
            }
          } catch(e) {
            console.log("Parse Error");
          }
          resolve();
        });
      }).on("error", () => resolve());
    });
  }
}
runTests();
