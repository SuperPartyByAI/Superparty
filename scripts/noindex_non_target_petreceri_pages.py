import os
import json
import re

MANIFEST_PATH = r"C:\Users\ursac\Superparty\reports\seo\indexing_manifest.json"
PAGES_DIR = r"C:\Users\ursac\Superparty\src\pages\petreceri"

def main():
    if not os.path.exists(MANIFEST_PATH):
        print("Manifest_JSON lipseste! Runeza generate_manifest... intai.")
        return

    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    # Colectam ce slug-uri nu sunt target.
    # Un "non-target" este orice unde indexable=False (asa cum a prevazut manifest generatorul)
    non_target_slugs = set()
    target_slugs = set()
    for m in manifest:
        if m.get('indexable') is False:
            non_target_slugs.add(m.get('slug'))
        else:
            target_slugs.add(m.get('slug'))
    
    # Procesam directory-ul
    updated_files = 0
    skipped_files = 0

    for fname in os.listdir(PAGES_DIR):
        if not fname.endswith('.astro') or fname == '[slug].astro':
            continue
        
        slug = fname[:-6]
        fpath = os.path.join(PAGES_DIR, fname)
        
        # Daca e in whitelist, verificam daca cumva era noindex si-l reparam? 
        # (doar daca e hub/town). Altfel, daca e non-target punem noindex.
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        
        if slug in non_target_slugs:
            # Trebuie pus noindex. 
            # Cautam robots="index, follow" in zona layout-ului 
            # sau robots={...} etc. Cel mai intalnit e: robots="index, follow"
            if 'robots="index, follow" ' in new_content or 'robots="index, follow"\n' in new_content or 'robots="index, follow"' in new_content:
                new_content = new_content.replace('robots="index, follow"', 'robots="noindex, follow"')
            # Uneori e doar robots=""? Parsez Layout
            elif 'robots=' not in new_content and '<Layout' in new_content:
                new_content = new_content.replace('<Layout', '<Layout\n  robots="noindex, follow"')
                
            # Dacă canonica dădea spre el însăși, o mutăm spre Hub? Mai bine lăsăm canonical așa pe moment + noindex 
            if new_content != content:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_files += 1
            else:
                skipped_files += 1
                
        elif slug in target_slugs:
            # Ne asigurăm ca cele legit (voluntari) sunt index, follow
            if 'robots="noindex, follow"' in new_content:
                new_content = new_content.replace('robots="noindex, follow"', 'robots="index, follow"')
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                updated_files += 1
            else:
                skipped_files += 1

    print(f"✅ Gata! Fisiere cu meta robots modificate: {updated_files}")
    print(f"   (Skiped/No changes: {skipped_files})")
    
if __name__ == "__main__":
    main()
