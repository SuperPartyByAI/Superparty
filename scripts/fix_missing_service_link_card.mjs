// fix_missing_service_link_card.mjs
// Creează componenta ServiceLinkCard.astro lipsă care blochează build-ul Vercel

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const COMPONENT_PATH = path.join(__dirname, '../src/components/blog/ServiceLinkCard.astro');
const COMPONENT_DIR = path.dirname(COMPONENT_PATH);

// Creăm directorul dacă nu există
if (!fs.existsSync(COMPONENT_DIR)) {
  fs.mkdirSync(COMPONENT_DIR, { recursive: true });
  console.log(`✅ Creat director: src/components/blog/`);
}

// Componenta ServiceLinkCard - card simplu de link spre serviciu
const componentContent = `---
interface Props {
  title: string;
  description: string;
  href: string;
  image?: string;
}
const { title, description, href, image } = Astro.props;
---

<a href={href} class="service-link-card">
  {image && <img src={image} alt={title} loading="lazy" width="400" height="225" />}
  <div class="slc-content">
    <h3>{title}</h3>
    <p>{description}</p>
    <span class="slc-cta">Află mai mult →</span>
  </div>
</a>

<style>
  .service-link-card {
    display: flex;
    flex-direction: column;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    transition: box-shadow 0.2s, transform 0.2s;
  }
  .service-link-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    transform: translateY(-2px);
  }
  .service-link-card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
  }
  .slc-content {
    padding: 1.25rem;
  }
  .slc-content h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a202c;
    margin: 0 0 0.5rem;
  }
  .slc-content p {
    font-size: 0.9rem;
    color: #718096;
    margin: 0 0 1rem;
    line-height: 1.5;
  }
  .slc-cta {
    color: #3182ce;
    font-weight: 600;
    font-size: 0.9rem;
  }
</style>
`;

fs.writeFileSync(COMPONENT_PATH, componentContent, 'utf-8');
console.log(`✅ Creat: src/components/blog/ServiceLinkCard.astro`);
console.log(`\n🎉 Build-ul Vercel ar trebui să treacă acum!`);
