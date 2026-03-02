import os

HUBS = ["bucuresti", "ilfov", "sector-1", "sector-2", "sector-3", "sector-4", "sector-5", "sector-6"]
DEST_DIR = "src/pages/petreceri"

HUB_TEMPLATE = """---
import Layout from '../../layouts/Layout.astro';
import { getCollection } from 'astro:content';

const allArticles = await getCollection('seo-articles');

// Filtram articolele care apartin acestui hub si sunt indexabile
const hubArticles = allArticles.filter(article => 
  article.slug.includes('{target_slug}') && article.data.indexStatus !== 'hold'
);

const pageTitle = "Animatori Petreceri Copii {target_name} | Superparty";
const pageDesc = "Găsește cel mai potrivit animator pentru petrecerea copilului tău în {target_name}. Pachete premium, zeci de personaje și distracție garantată cu Superparty.";
---

<Layout title={pageTitle} description={pageDesc} canonical={`https://superparty.ro/petreceri/{target_slug}`}>
  <div class="relative bg-white pt-10 pb-20 lg:pt-16 lg:pb-28">
    <div class="relative mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16">
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-extrabold text-gray-900 tracking-tight mb-4">
          Petreceri de Vis în {target_name}
        </h1>
        <p class="text-xl text-gray-500 max-w-2xl mx-auto">
          {pageDesc}
        </p>
      </div>

      <div class="bg-white rounded-3xl shadow-xl shadow-pink-500/5 ring-1 ring-gray-100 overflow-hidden p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Personajele Disponibile în {target_name}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {{hubArticles.map(article => (
            <a href={`/petreceri/${article.slug}`} class="block p-4 border border-gray-200 rounded-xl hover:border-pink-500 hover:shadow-md transition">
              <h3 class="font-semibold text-lg text-pink-600">{article.data.title}</h3>
              <p class="text-sm text-gray-500 mt-1 truncate">{article.data.description}</p>
            </a>
          ))}}
          {{hubArticles.length === 0 && <p class="text-gray-500 italic">Momentan actualizăm lista de servicii pentru această zonă.</p>}}
        </div>
      </div>
    </div>
  </div>
</Layout>
"""

def create_hubs():
    os.makedirs(DEST_DIR, exist_ok=True)
    for slug in HUBS:
        name = slug.replace("-", " ").title()
        content = HUB_TEMPLATE.replace("{target_slug}", slug).replace("{target_name}", name).replace("{{", "{").replace("}}", "}")
        
        path = os.path.join(DEST_DIR, f"{slug}.astro")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created Hub: {path}")

if __name__ == "__main__":
    create_hubs()
