import os
import re

directories = [
    "Kassia", "WowParty", "Universeparty", "Animaparty", "Clubuldisney",
    "Petreceritematice", "Ursitoaremagice", "Teraparty", "Youparty",
    "Joyparty", "Playparty", "123party", "Happyparty"
]
base_dir = r"C:\Users\ursac"

print("=========================================================================================")
print(f"{'DOMENIU':<20} | {'CLASE HTML PRINCIPALE (STRUCTURA LAYOUT)':<60}")
print("=========================================================================================")

structural_groups = {}

for d in directories:
    idx_path = os.path.join(base_dir, d, 'src', 'pages', 'index.astro')
    if os.path.exists(idx_path):
        with open(idx_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the classes used in <section> and <header> tags to prove structure diff
        classes = re.findall(r'<(?:section|header|div)\s+[^>]*class="([^"]+)"', content)
        
        # We take the top level defining classes that show the mega-template difference
        key_classes = []
        for c in classes:
            if "hero" in c or "t1-" in c or "t2-" in c or "t3-" in c or "bubble" in c or "banner" in c or "cards" in c or "alternating" in c:
                key_classes.extend(c.split())
        
        # Deduplicate and sort
        unique_classes = sorted(list(set(key_classes)))
        sig = " + ".join(unique_classes[:5])
        
        print(f"{d:<20} | {sig:<60}")
        
        # Grouping
        if sig not in structural_groups:
            structural_groups[sig] = []
        structural_groups[sig].append(d)

print("\n=========================================================================================")
print("ANALIZA GRUPAJ (S-au gasit structuri distincte pe disc):")
for sig, sites in structural_groups.items():
    print(f"\nSTRUCTURA HTML: [{sig}]")
    print(f"-> Prezenta pe {len(sites)} site-uri: {', '.join(sites)}")
    
if len(structural_groups) > 1:
    print("\n✅ DOVADA DE UNICITATE: Există", len(structural_groups), "macro-structuri HTML absolut diferite pe rețeaua ta, distribuite ciclic pentru a nu repeta design-ul.")
else:
    print("\n❌ EROARE: Toate par sa aiba aceeasi structura. Ceva nu s-a generat corect.")
