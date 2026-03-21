import fs from 'fs';

let c = fs.readFileSync('src/pages/recenzii.astro','utf8');
const search = '          <div class="review-meta">\r\n            <span class="src-badge" title={sourceLabel(r.source)}>{sourceIcon(r.source)}</span>';
const search2 = '          <div class="review-meta">\n            <span class="src-badge" title={sourceLabel(r.source)}>{sourceIcon(r.source)}</span>';

const replace = `          {idx % 4 === 0 && idx < 40 && (
            <div class="review-attached-img" style="margin-bottom:1rem; border-radius:8px; overflow:hidden; border: 1px solid rgba(255,255,255,0.1);">
              <img 
                src={[
                  '/optimized/animatori-1.webp',
                  '/optimized/batman.webp',
                  '/optimized/cenusareasa-si-print-1.webp',
                  '/optimized/animatori-petreceri-copii-acasa.webp',
                  '/optimized/animatori-petreceri-copii-superparty-2.webp',
                  '/optimized/animatori-copii-1.webp'
                ][(Math.floor(idx/4)) % 6]} 
                alt="Poza reala de la petrecere copii București" 
                loading="lazy" 
                style="width:100%; height:160px; object-fit:cover; display:block;" 
              />
            </div>
          )}

          <div class="review-meta">
            <span class="src-badge" title={sourceLabel(r.source)}>{sourceIcon(r.source)}</span>`;

if (c.includes(search)) {
  c = c.replace(search, replace);
  fs.writeFileSync('src/pages/recenzii.astro', c);
  console.log('recenzii.astro FIXAT CU SUCCES (Windows CRLF)!');
} else if (c.includes(search2)) {
  c = c.replace(search2, replace);
  fs.writeFileSync('src/pages/recenzii.astro', c);
  console.log('recenzii.astro FIXAT CU SUCCES (Linux LF)!');
} else {
  console.log('Eroare: Baza codului pentru review-meta nu a putut fi interceptata.');
}
