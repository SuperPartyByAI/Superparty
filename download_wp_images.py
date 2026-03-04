"""
Descarca imaginile WordPress din Wayback Machine si le salveaza in public/wp-content/uploads/
Astfel imaginile vor fi servite ca fisiere statice pe Vercel (fara redirect).
"""
import urllib.request, urllib.error, os, time, json
from datetime import datetime

# ==========================================
# Extrage URL-urile de imagini din old_wp_urls.txt
# ==========================================
IMG_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico')

with open('old_wp_urls.txt', 'r') as f:
    raw_urls = [l.strip() for l in f.readlines() if l.strip()]

image_paths = []
for url in raw_urls:
    path = url.replace('https://www.superparty.ro', '').replace('https://superparty.ro', '').strip()
    # Pastreaza numai imaginile din wp-content/uploads/
    if '/wp-content/uploads/' in path:
        # Scoate query strings
        path = path.split('?')[0]
        ext = os.path.splitext(path)[1].lower()
        if ext in IMG_EXTENSIONS:
            image_paths.append(path)

print(f"Imagini de descarcat: {len(image_paths)}")

# ==========================================
# Descarca fiecare imagine din Wayback Machine
# ==========================================
WAYBACK_BASE = "https://web.archive.org/web/20250101000000if_/https://www.superparty.ro"
PUBLIC_DIR = "public"

stats = {"downloaded": 0, "skipped": 0, "failed": 0}
results = []

def download_image(path, retries=2):
    """Descarca imaginea din Wayback Machine si o salveaza local."""
    local_path = os.path.join(PUBLIC_DIR, path.lstrip('/'))
    
    # Skip daca exista deja
    if os.path.exists(local_path) and os.path.getsize(local_path) > 100:
        return "skipped"
    
    # Creeaza directorul daca nu exista
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    # Incearca sa descarce din Wayback Machine
    wayback_url = WAYBACK_BASE + path
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                wayback_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'image/*,*/*'
                }
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                content = r.read()
                # Verifica ca e o imagine (nu HTML)
                if len(content) > 1000 and not content[:100].startswith(b'<!DOCTYPE'):
                    with open(local_path, 'wb') as f:
                        f.write(content)
                    return "downloaded"
                else:
                    # Incearca URL-ul original (live) ca backup
                    live_url = f"https://superparty.ro{path}"
                    req2 = urllib.request.Request(live_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req2, timeout=15) as r2:
                        content2 = r2.read()
                        if len(content2) > 1000:
                            with open(local_path, 'wb') as f:
                                f.write(content2)
                            return "downloaded"
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return f"failed: {e}"
    
    return "failed: all retries"

print(f"\nIncep descarcarea a {len(image_paths)} imagini...")
print("-" * 60)

for i, path in enumerate(image_paths):
    result = download_image(path)
    results.append({"path": path, "result": result})
    
    if result == "downloaded":
        stats["downloaded"] += 1
        print(f"[{i+1}/{len(image_paths)}] ✓  {path}")
    elif result == "skipped":
        stats["skipped"] += 1
        print(f"[{i+1}/{len(image_paths)}] →  SKIP (exista deja): {path}")
    else:
        stats["failed"] += 1
        print(f"[{i+1}/{len(image_paths)}] ✗  FAIL: {path} ({result})")
    
    # Rate limiting - nu spam Wayback Machine
    time.sleep(0.5)

# ==========================================
# Raport final
# ==========================================
print("\n" + "=" * 60)
print(f"RAPORT FINAL:")
print(f"  ✓ Descarcate: {stats['downloaded']}")
print(f"  → Sarite (deja existente): {stats['skipped']}")
print(f"  ✗ Esuate: {stats['failed']}")

# Salveaza raportul
with open('reports/superparty/images_download_report.json', 'w') as f:
    json.dump({
        "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "stats": stats,
        "results": results
    }, f, indent=2)

print(f"\nRaport salvat: reports/superparty/images_download_report.json")
print("\nPasi urmatori:")
print("1. Sterge regulile wp-content/uploads din vercel.json (imaginile exista acum in public/)")
print("2. git add public/wp-content/uploads/")
print("3. git commit + push")
