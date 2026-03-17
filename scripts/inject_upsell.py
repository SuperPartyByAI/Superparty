import os
import glob
import re
import sys

# Windows UTF-8 console fix
sys.stdout.reconfigure(encoding='utf-8')

print("Initializing Upsell Injection Sequence (Astro Mode)...")

spoke_dir = r"C:\Users\ursac\Superparty\src\pages\petreceri"
hub_dir = r"C:\Users\ursac\Superparty\src\pages"

# Find all Astro spokes and hubs
spoke_files = glob.glob(os.path.join(spoke_dir, "**", "*.astro"), recursive=True)
hub_files = glob.glob(os.path.join(hub_dir, "animatori-copii-*", "index.astro"))

upsell_block_astro = """

      <!-- ── UPSELL SECTION ────────────────────────────────────────────────── -->
      <div class="mt-16 mb-8 text-center">
        <h2 class="text-3xl font-extrabold text-gray-900 dark:text-white mb-8">✨ Fă petrecerea cu adevărat memorabilă! Adaugă și:</h2>
        <div class="grid gap-6 md:grid-cols-2 text-left">
          <ServiceLinkCard 
            title="Închiriere Aparat Vată de Zahăr" 
            description="Porții nelimitate și operator uman inclus. Oferă aroma copilăriei invitaților tăi!"
            href="/vata-de-zahar-si-popcorn/" 
            image="https://www.superparty.ro/hero1.jpg"
          />
          <ServiceLinkCard 
            title="Decorațiuni & Arcade Baloane" 
            description="Intrări spectaculoase și fundaluri perfecte pentru poze de neuitat. Montaj gratuit!"
            href="/arcade-baloane/" 
            image="https://www.superparty.ro/hero2.jpg"
          />
        </div>
      </div>

"""

import_statement_astro = "import ServiceLinkCard from '../../components/blog/ServiceLinkCard.astro';\n"
import_statement_hub = "import ServiceLinkCard from '../components/blog/ServiceLinkCard.astro';\n"

spokes_injected = 0
hubs_injected = 0

def inject_file(filepath, is_hub=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already injected
    if "Fă petrecerea cu adevărat memorabilă" in content or "vata-de-zahar-si-popcorn" in content:
        return False

    import_state = import_statement_hub if is_hub else import_statement_astro

    # Insert import if missing
    if "import ServiceLinkCard" not in content:
        content = re.sub(r'(^---\n)', r'\1' + import_state, content, count=1, flags=re.MULTILINE)

    # Inject component before FAQ or Layout end
    if "<FAQ " in content:
        content = content.replace("<FAQ ", upsell_block_astro + "\n      <FAQ ")
    elif "</Layout>" in content:
        content = content.replace("</Layout>", upsell_block_astro + "\n</Layout>")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return True

for astro_path in spoke_files:
    if inject_file(astro_path, is_hub=False):
        spokes_injected += 1

for astro_path in hub_files:
    if inject_file(astro_path, is_hub=True):
        hubs_injected += 1

print("=== DOVADA INJECȚIEI (Python Log) ===")
print(f"Success: Injected Upsell component on {spokes_injected} Spoke pages (.astro)")
print(f"Success: Injected Upsell component on {hubs_injected} Hub pages (.astro)")
print(f"Total Integrations: {spokes_injected + hubs_injected}")
