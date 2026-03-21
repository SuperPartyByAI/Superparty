import fs from 'fs';

let c = fs.readFileSync('src/pages/recenzii.astro', 'utf8');

// Stergem vechiul bloc stricat de imagine (daca mai exista)
c = c.replace(/\{idx % 4 === 0 && idx < 40 && \([\s\S]*?<\/div>\s*\)\}/g, '');

const search1 = "        const text     = processReview(r.text || '');\r\n        return (\r\n        <article";
const search1b = "        const text     = processReview(r.text || '');\n        return (\n        <article";

const replace1 = `        const text     = processReview(r.text || '');
        
        const showImage = (idx % 4 === 0 && idx < 40);
        const images = [
          '/optimized/animatori-1.webp',
          '/optimized/batman.webp',
          '/optimized/cenusareasa-si-print-1.webp',
          '/optimized/animatori-petreceri-copii-acasa.webp',
          '/optimized/animatori-petreceri-copii-superparty-2.webp',
          '/optimized/animatori-copii-1.webp'
        ];
        const attachedImgUrl = images[Math.floor(idx/4) % images.length];

        return (
        <article`;

if (c.includes(search1)) c = c.replace(search1, replace1);
else if (c.includes(search1b)) c = c.replace(search1b, replace1);

const search2 = '          <p class="review-text">"{text}"</p>\r\n          <div class="review-meta">';
const search2b = '          <p class="review-text">"{text}"</p>\n          <div class="review-meta">';

const replace2 = `          <p class="review-text">"{text}"</p>
          
          {showImage && (
            <div class="review-attached-img" style="margin-bottom:1rem; border-radius:8px; overflow:hidden; border: 1px solid rgba(255,255,255,0.1);">
              <img 
                src={attachedImgUrl} 
                alt="Poza reala de la petrecere copii București" 
                loading="lazy" 
                style="width:100%; height:160px; object-fit:cover; display:block;" 
              />
            </div>
          )}

          <div class="review-meta">`;

if (c.includes(search2)) c = c.replace(search2, replace2);
else if (c.includes(search2b)) c = c.replace(search2b, replace2);

fs.writeFileSync('src/pages/recenzii.astro', c);
console.log('Fisier reparat prin extractia logicii.');
