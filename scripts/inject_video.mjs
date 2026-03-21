import fs from 'fs';
import path from 'path';

function walk(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    file = path.join(dir, file);
    const stat = fs.statSync(file);
    if (stat && stat.isDirectory()) {
      results = results.concat(walk(file));
    } else if (file.endsWith('.astro')) {
      results.push(file);
    }
  });
  return results;
}

const files = walk('src/pages');
let count = 0;

const videoSection = `
<!-- DWELL TIME INJECTION (YOUTUBE EMBED) -->
<section class="seo-video-dwell" style="padding: 3.5rem 0; background: #fff;">
  <div class="container" style="max-width: 800px; margin: 0 auto; text-align: center;">
    <h2 style="font-size: 1.6rem; font-weight: 800; color: #1a202c; margin-bottom: 1.5rem;">Magia SuperParty în Acțiune — Vezi Video</h2>
    <div style="position: relative; padding-bottom: 56.25%; height: 0; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 4px solid #fff;">
      <iframe 
        src="https://www.youtube.com/embed/Pj1L6zG3M0w?rel=0" 
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border:0;" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen
        loading="lazy"
        title="SuperParty Animatori Petreceri Copii"
      ></iframe>
    </div>
    <p style="margin-top: 1.2rem; color: #4a5568; font-size: 0.95rem; font-style: italic;">Apasă Play pentru a vedea energia și costumele noastre impecabile la o petrecere reală.</p>
  </div>
</section>
`;

files.forEach(f => {
  let code = fs.readFileSync(f, 'utf8');
  let changed = false;
  
  if(!code.includes('seo-video-dwell')) {
      code = code.replace(/<\/section>\s*<script type="application\/ld\+json">/i, `</section>\n${videoSection}\n<script type="application/ld+json">`);
      changed = true;
  }
  
  if(changed) {
    fs.writeFileSync(f, code);
    count++;
  }
});

console.log("Dwell Time Video Injected in " + count + " files!");
