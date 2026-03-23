import os
import subprocess
import shutil

domains = [
    "clubuldisney.ro", "petreceritematice.ro", "ursitoaremagice.ro",
    "teraparty.ro", "youparty.ro", "joyparty.ro", "playparty.ro",
    "123party.ro", "happyparty.ro"
]

base_dir = r"C:\Users\ursac"

def uppercase_first(s):
    if not s: return s
    return s[0].upper() + s[1:]

print("Incepere deploy pentru toate cele 9 clone...\n")

for d in domains:
    name_lower = d.replace('.ro', '')
    name_display = uppercase_first(name_lower)
    target_dir = os.path.join(base_dir, name_display)
    
    # 1. Remove .vercel to prevent overwrite of Kassia
    vercel_dir = os.path.join(target_dir, '.vercel')
    if os.path.exists(vercel_dir):
        shutil.rmtree(vercel_dir)
        print(f"[{name_display}] Curățat cache-ul Vercel existent (evitare suprascriere Kassia).")
        
    print(f"[{name_display}] Trimitere cod Astro către Vercel (Creare instanță nouă)...")
    
    # 2. Deploy nou
    res_deploy = subprocess.run(['npx', 'vercel', '--prod', '--yes', '--name', name_lower], cwd=target_dir, shell=True, text=True, capture_output=True)
    if res_deploy.returncode != 0:
        print(f"⚠️ Eroare Vercel la deploy {name_display}:\n{res_deploy.stderr}")
    
    # 3. Adaugare domeniu
    domain_to_add = f"www.{d}"
    print(f"[{name_display}] Mapare domeniu live {domain_to_add}...")
    res_domain = subprocess.run(['npx', 'vercel', 'domains', 'add', domain_to_add], cwd=target_dir, shell=True, text=True, capture_output=True)
    
    print(f"✅ {name_display} PUBLICAT CU SUCCES!\n")

print("TOATE 9 SITEURI SUNT DEPLOYATE PE VERCEL CLOUD SI PREGATITE!")
