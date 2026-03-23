import os
import shutil
import re
import subprocess

domains = [
    "clubuldisney.ro", "petreceritematice.ro", "ursitoaremagice.ro",
    "teraparty.ro", "youparty.ro", "joyparty.ro", "playparty.ro",
    "123party.ro", "happyparty.ro"
]

base_dir = r"C:\Users\ursac"
template_dir = os.path.join(base_dir, "Kassia")

def uppercase_first(s):
    if not s: return s
    return s[0].upper() + s[1:]

for d in domains:
    name_lower = d.replace('.ro', '')
    name_display = uppercase_first(name_lower)
    target_dir = os.path.join(base_dir, name_display)
    prefix = name_display
    
    print(f"[{name_display}] Creare proiect...")
    if not os.path.exists(target_dir):
        print(f"Copiind template-ul (fara nod_modules)...")
        shutil.copytree(template_dir, target_dir, ignore=shutil.ignore_patterns('.git', 'node_modules', 'dist'))
        
        print(f"Ruland npm install în {target_dir}...")
        subprocess.run(['npm', 'install'], cwd=target_dir, shell=True)
    else:
        print(f"Folderul {target_dir} exista deja.")
    
    # 1. Update package.json
    pkg_path = os.path.join(target_dir, 'package.json')
    if os.path.exists(pkg_path):
        with open(pkg_path, 'r', encoding='utf-8') as f:
            pkg = f.read()
        pkg = re.sub(r'"name":\s*"[^"]+"', f'"name": "{name_lower}"', pkg)
        with open(pkg_path, 'w', encoding='utf-8') as f:
            f.write(pkg)
            
    # 2. Update Layout.astro
    layout_path = os.path.join(target_dir, 'src', 'layouts', 'Layout.astro')
    if os.path.exists(layout_path):
        with open(layout_path, 'r', encoding='utf-8') as f:
            layout = f.read()
        # Modificam textul vizual
        layout = layout.replace('Kassia', name_display)
        layout = layout.replace('kassia.ro', f"{name_lower}.ro")
        with open(layout_path, 'w', encoding='utf-8') as f:
            f.write(layout)
            
    # 3. Update index.astro
    idx_path = os.path.join(target_dir, 'src', 'pages', 'index.astro')
    if os.path.exists(idx_path):
        with open(idx_path, 'r', encoding='utf-8') as f:
            idx = f.read()
            
        # Inlocuire titlu, domeniu etc
        idx = idx.replace('Kassia', name_display)
        idx = idx.replace('kassia.ro', f"{name_lower}.ro")
        
        # Inlocuire prefix prețuri generat de scriptul vechi (Daca e Kassia 1 -> Clubuldisney 1)
        for i in range(1, 8):
            idx = idx.replace(f'{name_display} {i}', f'{prefix} {i}')
            # in caz ca mai era Kassia ramas
            idx = idx.replace(f'Kassia {i}', f'{prefix} {i}')
            
        with open(idx_path, 'w', encoding='utf-8') as f:
            f.write(idx)
    
    print(f"[{name_display}] Gata.\n")

print("TOATE PROIECTELE AU FOST GENERATE SI CONFIGURATE CORECT!")
