import os
import random
import string
import subprocess

domains = [
    ("Kassia", "Kassia", "kassia.ro", "#10b981", "'Outfit', sans-serif", "https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap"),
    ("WowParty", "Wow", "wowparty.ro", "#f43f5e", "'Fredoka One', cursive", "https://fonts.googleapis.com/css2?family=Fredoka+One&display=swap"),
    ("Universeparty", "Universe", "universeparty.ro", "#6366f1", "'Righteous', cursive", "https://fonts.googleapis.com/css2?family=Righteous&display=swap"),
    ("Animaparty", "Anima", "animaparty.ro", "#14b8a6", "'Nunito', sans-serif", "https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap"),
    ("Clubuldisney", "Clubuldisney", "clubuldisney.ro", "#ef4444", "'Playfair Display', serif", "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap"),
    ("Petreceritematice", "Petreceri-T.", "petreceritematice.ro", "#d946ef", "'Jost', sans-serif", "https://fonts.googleapis.com/css2?family=Jost:wght@400;700&display=swap"),
    ("Ursitoaremagice", "Ursitoaremagice", "ursitoaremagice.ro", "#c026d3", "'Caveat', cursive", "https://fonts.googleapis.com/css2?family=Caveat:wght@700&display=swap"),
    ("Teraparty", "Teraparty", "teraparty.ro", "#3b82f6", "'Roboto Mono', monospace", "https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap"),
    ("Youparty", "Youparty", "youparty.ro", "#f59e0b", "'Oswald', sans-serif", "https://fonts.googleapis.com/css2?family=Oswald:wght@700&display=swap"),
    ("Joyparty", "Joyparty", "joyparty.ro", "#10b981", "'Comfortaa', cursive", "https://fonts.googleapis.com/css2?family=Comfortaa:wght@700&display=swap"),
    ("Playparty", "Playparty", "playparty.ro", "#000000", "'Archivo Black', sans-serif", "https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap"),
    ("123party", "123party", "123party.ro", "#ec4899", "'Comic Neue', cursive", "https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap"),
    ("Happyparty", "Happyparty", "happyparty.ro", "#f43f5e", "'Pacifico', cursive", "https://fonts.googleapis.com/css2?family=Pacifico&display=swap")
]

base_dir = r"C:\Users\ursac"

packages_data = [
    {"n": "1", "price": "490 lei", "d": "1 Personaj · 2 ore", "f": ["Jocuri interactive", "Baloane modelate", "Pictură pe față", "Mini disco", "Diplome", "Boxă inclusă"]},
    {"n": "2", "price": "490 lei", "d": "1 Oră Animatie Specială", "f": ["Costume de lux", "Facepainting sigur", "Jocuri adaptate", "Sunet asigurat"]},
    {"n": "3 MAGIA", "price": "840 lei", "d": "2 Personaje · 2 ore + Tun Confetti", "f": ["Tun spectaculos de confetti", "Coregrafii", "Pictură, Baloane", "Concursuri exclusive"]},
    {"n": "4 DULCE", "price": "590 lei", "d": "1 Animator + Tort special", "f": ["Tort masiv (22-26 pers)", "Sesiune Foto", "Distracție organizată", "Artificii tort"]},
    {"n": "5 MASINA", "price": "840 lei", "d": "1 Pers. + 1h Vată de Zahăr + 1h Popcorn", "f": ["Kiosk Vată Zahăr", "Kiosk Popcorn", "Consum nelimitat 1H", "Muzică și Voie bună"]},
    {"n": "6 DELUXE", "price": "540 lei", "d": "Animator + Banner Imens Petrecere", "f": ["Banner 'La Multi Ani'", "Program structurat 2h", "Baloane în formă animale"]},
    {"n": "7 URSITOARE", "price": "1290 lei", "d": "Spectacol de Gale cu 4 Ursitoare", "f": ["Reprezentație live", "Program muzical 3h", "Atenție extinsă la botez", "Microfoane incluse"]}
]

def rc(): 
    # Random class Name (Anti-PBN)
    return "w" + "".join(random.choices(string.ascii_lowercase, k=6))

def render_features_list(feat, tag):
    random.shuffle(feat)
    return f"<{tag} " + " ".join([f"><li>&#x2714; {x}</li>" for x in feat]) + f"</{tag}>"

def tpl_pwa_horizontal(prefix, name, color, font_url, font_family, idx):
    # OBFUSCATED DOM, PWA BOTTOM NAV, HORIZONTAL SCROLLING SNAP (Mobile CSS)
    
    # 20 unique random class names
    c_wrap = rc()
    c_hero = rc()
    c_titl = rc()
    c_btns = rc()
    c_pckg = rc()
    c_grid = rc()
    c_card = rc()
    c_foot = rc()
    c_nav = rc()
    c_list = rc()
    
    html = f'''---
import Layout from '../layouts/Layout.astro';
---
<Layout title="Animatie {name} | Botez, Aniversari Copii" description="Cele mai wow experiente alaturi de marca {name}. Mascote, baloane, vata zahar." canonicalURL="https://www.{domains[idx][2]}/">
  <div class="{c_wrap}">
    
    <header class="{c_hero}">
      <div class="inner">
         <h1 class="{c_titl}">{name} - Fă-i Ziua Magică!</h1>
         <p>Rezervă online sau telefonic cea mai bună echipă de animatori din județ.</p>
         <a href="#preturi" class="{c_btns}">Vezi ce am pregătit 👉</a>
      </div>
    </header>

    <div class="{c_pckg}" id="preturi">
      <h2 style="text-align:center; padding:2rem 1rem 0;">Alege pachetul tău The {name}</h2>
      
      <!-- HORIZONTAL SCROLL SNAP pe mobil -->
      <div class="{c_grid}">
'''
    for p in packages_data:
        html += f'''
        <article class="{c_card}">
          <div class="t-head"><strong>{prefix} Pachetul {p["n"]}</strong></div>
          <div class="t-price">{p["price"]}</div>
          <div class="t-desc">{p["d"]}</div>
          <div class="{c_list}">
            {''.join([f"<div>✓ {f}</div>" for f in random.sample(p["f"], len(p["f"]))])}
          </div>
          <a href="/contact/" class="{c_btns} action">SUNĂ ACUM</a>
        </article>
'''
    
    html += f'''
      </div>
    </div>
    
    <div style="padding:4rem 1rem; text-align:center; background:#111; color:#fff;" class="{c_foot}">
       <h2>Cuvantul nostru este lege în Distracție!</h2>
       <p>Echipa {name}</p>
    </div>

    <!-- PWA BOTTOM NAV -->
    <nav class="{c_nav}">
      <a href="#">🏠 Acasă</a>
      <a href="#preturi">💰 Oferte</a>
      <a href="/contact/" style="color: {color}; font-weight: bold;">📞 Rezervă</a>
    </nav>
  </div>
</Layout>

<style>
  :root {{ --main: {color}; --t-font: {font_family}; --bg: #f8fafc; }}
  .{c_wrap} {{ padding-bottom: 70px; font-family: var(--t-font); background: var(--bg); overflow-x: hidden; }}
  
  .{c_hero} {{ background: var(--main); color: white; min-height: 50vh; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; position:relative; border-bottom-left-radius: 40px; border-bottom-right-radius: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }}
  .inner {{ max-width: 800px; padding: 2rem; }}
  .{c_titl} {{ font-size: clamp(2.5rem, 8vw, 5rem); margin-bottom: 1rem; text-shadow: 1px 2px 0px rgba(0,0,0,0.2); }}
  
  .{c_btns} {{ background: white; color: var(--main); padding: 1rem 2rem; border-radius: 30px; font-weight: 900; text-decoration: none; text-transform: uppercase; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; margin-top:2rem; }}
  .{c_btns}.action {{ background: var(--main); color: white; width: calc(100% - 2rem); margin: 1rem; position:absolute; bottom: 0; box-sizing: border-box; }}
  
  /* Horizontal Snap Scrolling */
  .{c_grid} {{ display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 1.5rem; padding: 2rem; -webkit-overflow-scrolling: touch; scroll-padding: 2rem; }}
  /* Ascunde scrollbarul orizontal */
  .{c_grid}::-webkit-scrollbar {{ display: none; }}
  
  .{c_card} {{ scroll-snap-align: start; flex: 0 0 85vw; max-width: 380px; background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); position: relative; padding-bottom: 5rem; overflow: hidden; border: 1px solid #e2e8f0; }}
  @media(min-width: 768px) {{ .{c_grid} {{ flex-wrap: wrap; justify-content: center; overflow-x: hidden; }} .{c_card}{{ flex: 1 1 300px; }} }}
  
  .t-head {{ background: var(--main); color: white; padding: 1.5rem; font-size: 1.3rem; text-align: center; }}
  .t-price {{ font-size: 2.2rem; text-align: center; color: var(--main); font-weight: 900; padding: 1.5rem 0 0.5rem; }}
  .t-desc {{ text-align: center; color: #64748b; font-size: 0.95rem; margin-bottom: 1.5rem; }}
  
  .{c_list} {{ padding: 0 1.5rem; display: flex; flex-direction: column; gap: 0.8rem; font-size: 0.95rem; color: #334155; }}
  
  /* PWA NAV */
  .{c_nav} {{ position: fixed; bottom: 0; left: 0; right: 0; height: 70px; background: white; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-around; align-items: center; z-index: 1000; box-shadow: 0 -4px 10px rgba(0,0,0,0.05); font-family: var(--t-font); }}
  .{c_nav} a {{ text-decoration: none; color: #64748b; font-weight: 700; font-size: 0.9rem; display:flex; flex-direction:column; align-items:center; transition: 0.2s; }}
</style>
'''
    return html

def inject_layout(path, theme):
    layout_path = os.path.join(path, "src", "layouts", "Layout.astro")
    if not os.path.exists(layout_path): return
    with open(layout_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    font_link = f'    <link href="{theme[5]}" rel="stylesheet">\n'
    if font_link not in content:
        content = content.replace('</head>', font_link + '</head>')
        
    with open(layout_path, "w", encoding="utf-8") as f:
        f.write(content)

for idx, params in enumerate(domains):
    folder, prefix, url, color, font, font_link = params
    path_root = os.path.join(base_dir, folder)
    
    print(f"Injecting Anti-PBN PWA DOM in {folder}...")
    inject_layout(path_root, params)
    
    # Write fully obfuscated DOM + Horizontal Snap PWA layout
    final_html = tpl_pwa_horizontal(prefix, folder, color, font, font, idx)
    
    with open(os.path.join(path_root, "src", "pages", "index.astro"), "w", encoding="utf-8") as f:
        f.write(final_html)

print("TOATE SITE-URILE AU FOST PROTEJATE PRIN OBFUSCARE DOM SI AU PRIMIT ARHITECTURA PWA!")
