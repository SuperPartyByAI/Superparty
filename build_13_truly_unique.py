import os
import random

domains = [
    ("Kassia", "kassia.ro", "#10b981", "'Outfit', sans-serif"),
    ("WowParty", "wowparty.ro", "#f43f5e", "'Fredoka One', cursive"),
    ("Universeparty", "universeparty.ro", "#6366f1", "'Righteous', cursive"),
    ("Animaparty", "animaparty.ro", "#14b8a6", "'Nunito', sans-serif"),
    ("Clubuldisney", "clubuldisney.ro", "#ef4444", "'Playfair Display', serif"),
    ("Petreceritematice", "petreceritematice.ro", "#d946ef", "'Jost', sans-serif"),
    ("Ursitoaremagice", "ursitoaremagice.ro", "#c026d3", "'Caveat', cursive"),
    ("Teraparty", "teraparty.ro", "#3b82f6", "'Roboto Mono', monospace"),
    ("Youparty", "youparty.ro", "#f59e0b", "'Oswald', sans-serif"),
    ("Joyparty", "joyparty.ro", "#10b981", "'Comfortaa', cursive"),
    ("Playparty", "playparty.ro", "#000000", "'Archivo Black', sans-serif"),
    ("123party", "123party.ro", "#ec4899", "'Comic Neue', cursive"),
    ("Happyparty", "happyparty.ro", "#f43f5e", "'Pacifico', cursive")
]

packages_data = [
    {"n": "Pachet 1", "price": "490 lei", "d": "1 Personaj · 2 ore", "f": ["Jocuri", "Baloane", "Pictură", "Mini disco"]},
    {"n": "Pachet 2", "price": "490 lei", "d": "1 Oră Animatie", "f": ["Costume", "Facepainting", "Jocuri", "Sunet"]},
    {"n": "Pachet 3", "price": "840 lei", "d": "2 Personaje · 2 ore", "f": ["Confetti", "Coregrafii", "Pictură", "Concursuri"]},
    {"n": "Pachet 4", "price": "590 lei", "d": "1 Animator + Tort", "f": ["Tort masiv", "Sesiune Foto", "Distracție", "Artificii"]},
    {"n": "Pachet 5", "price": "840 lei", "d": "1 Pers. + Vată Zahăr", "f": ["Kiosk Vată", "Popcorn", "Nelimitat 1H", "Muzică", "Jocuri"]},
    {"n": "Pachet 6", "price": "540 lei", "d": "Animator + Banner", "f": ["Banner", "Program 2h", "Baloane"]},
    {"n": "Pachet 7", "price": "1290 lei", "d": "Ursitoare", "f": ["Spectacol", "Program 3h", "Botez"]}
]

# --- HERO TYPES ---
def hero_center_dark(name, color):
    return f"""
    <header style="background:#111; color:#fff; padding:6rem 2rem; text-align:center;">
        <h1 style="font-size:4rem; color:{color}; margin-bottom:1rem;">{name}</h1>
        <p style="font-size:1.5rem; max-width:800px; margin:0 auto;">Echipa numărul 1 pentru evenimente wow!</p>
        <a href="#pkgs" style="display:inline-block; margin-top:2rem; background:{color}; color:#fff; padding:1rem 2rem; text-decoration:none; border-radius:50px;">Vezi Pachetele</a>
    </header>
    """

def hero_split_white(name, color):
    return f"""
    <header style="background:#fff; color:#000; padding:4rem 2rem; display:flex; flex-wrap:wrap; align-items:center; border-bottom:5px solid {color};">
        <div style="flex:1; min-width:300px; padding:2rem;">
            <h1 style="font-size:3.5rem; border-left:10px solid {color}; padding-left:1rem;">Super Petreceri {name}</h1>
            <p style="font-size:1.2rem; margin-top:1rem;">Mascote, baloane si magie direct acasa la tine!</p>
        </div>
        <div style="flex:1; min-width:300px; text-align:center; font-size:8rem;">🎪🤡🎉</div>
    </header>
    """

def hero_gradient_fun(name, color):
    return f"""
    <header style="background:linear-gradient(135deg, {color}, #333); color:#fff; padding:8rem 1rem; text-align:center; border-radius:0 0 50px 50px;">
        <h1 style="font-size:5rem; text-shadow:2px 2px 0 #000;">{name}</h1>
        <h2 style="font-weight:300;">Distracție fără limite pentru copii de toate vârstele.</h2>
    </header>
    """

def hero_minimalist_border(name, color):
    return f"""
    <header style="border: 2px solid {color}; margin:2rem; padding:4rem; text-align:center;">
        <h1 style="color:{color}; font-size:3rem; text-transform:uppercase; letter-spacing:5px;">Agentia {name}</h1>
        <p style="font-size:1.2rem; color:#555;">Servicii premium de organizare petreceri.</p>
    </header>
    """

# --- PACKAGES TYPES ---
def pkgs_grid(color):
    html = f"""<section id="pkgs" style="padding:4rem 2rem; background:#f9fafb;"><h2 style="text-align:center; font-size:2.5rem; color:{color};">Pachetele Noastre</h2><div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:2rem; max-width:1200px; margin:0 auto;">"""
    for p in packages_data:
        html += f"""
        <div style="background:#fff; padding:2rem; border-radius:15px; box-shadow:0 4px 6px rgba(0,0,0,0.05); text-align:center; border-top:4px solid {color};">
            <h3>{p['n']}</h3>
            <div style="font-size:2rem; color:{color}; font-weight:bold; margin:1rem 0;">{p['price']}</div>
            <p style="color:#666;">{p['d']}</p>
            <ul style="list-style:none; padding:0;">{''.join([f'<li style="padding:0.5rem 0; border-bottom:1px solid #eee;">{f}</li>' for f in p['f']])}</ul>
        </div>"""
    html += "</div></section>"
    return html

def pkgs_alternating(color):
    html = f"""<section id="pkgs" style="padding:4rem 2rem; background:#fff;"><h2 style="text-align:center; font-size:2.5rem; border-bottom:2px solid {color}; display:inline-block; margin-bottom:3rem;">Alege Pachetul</h2><div style="max-width:900px; margin:0 auto; display:flex; flex-direction:column; gap:3rem;">"""
    for i, p in enumerate(packages_data):
        direction = "row" if i%2==0 else "row-reverse"
        bg = "#fafafa" if i%2==0 else "#fff"
        html += f"""
        <div style="display:flex; flex-direction:{direction}; align-items:center; background:{bg}; padding:2rem; border-radius:8px; border:1px solid #eee;">
            <div style="flex:1; padding:1rem; text-align:center;"><div style="font-size:4rem;">🎭</div></div>
            <div style="flex:2; padding:1rem;">
                <h3 style="font-size:1.8rem; margin:0; color:{color};">{p['n']}</h3>
                <div style="font-size:1.5rem; font-weight:bold; margin:0.5rem 0;">{p['price']}</div>
                <p><strong>{p['d']}</strong></p>
                <div style="display:flex; flex-wrap:wrap; gap:0.5rem;">{''.join([f'<span style="background:#eee; padding:5px 10px; border-radius:4px; font-size:0.9rem;">{f}</span>' for f in p['f']])}</div>
            </div>
        </div>"""
    html += "</div></section>"
    return html

def pkgs_table(color):
    html = f"""<section id="pkgs" style="padding:4rem 1rem; background:#111; color:#fff;"><h2 style="text-align:center; font-size:3rem; color:{color};">Tarife</h2><div style="max-width:800px; margin:0 auto;">"""
    for p in packages_data:
        html += f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:1.5rem; border-bottom:1px solid #333; flex-wrap:wrap;">
            <div style="flex:1; min-width:200px;">
                <h3 style="margin:0; font-size:1.5rem;">{p['n']}</h3>
                <p style="margin:0; color:#888;">{p['d']}</p>
            </div>
            <div style="flex:2; min-width:250px; padding:0 1rem; color:#bbb; font-size:0.9rem;">{', '.join(p['f'])}</div>
            <div style="font-size:1.5rem; font-weight:bold; color:{color}; text-align:right;">{p['price']}</div>
        </div>"""
    html += "</div></section>"
    return html

# --- SERVICES TYPES ---
def srv_cards(color):
    return f"""
    <section style="padding:4rem 2rem;">
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:2rem; max-width:1000px; margin:0 auto;">
            <div style="background:{color}; color:#fff; padding:2rem; text-align:center; border-radius:10px;"><h3 style="font-size:3rem; margin:0;">🧚‍♀️</h3><h4>Animatori Profesionisti</h4></div>
            <div style="background:{color}; color:#fff; padding:2rem; text-align:center; border-radius:10px;"><h3 style="font-size:3rem; margin:0;">🎨</h3><h4>Face Painting Sigur</h4></div>
            <div style="background:{color}; color:#fff; padding:2rem; text-align:center; border-radius:10px;"><h3 style="font-size:3rem; margin:0;">🎵</h3><h4>Boxa & Muzica</h4></div>
            <div style="background:{color}; color:#fff; padding:2rem; text-align:center; border-radius:10px;"><h3 style="font-size:3rem; margin:0;">🎈</h3><h4>Modelaj Baloane</h4></div>
        </div>
    </section>"""

def srv_text(color):
    return f"""
    <section style="padding:5rem 2rem; background:#f4f4f5; text-align:center;">
        <h2 style="font-size:2.5rem; color:{color};">De ce să ne alegi pe noi?</h2>
        <p style="font-size:1.2rem; max-width:700px; margin:1rem auto; color:#555;">Pentru că aducem zâmbete reale! Folosim doar recuzită de lux, costume profesionale curățate mereu, și traineri specializați pe interacțiunea cu copiii. Nu există petrecere la care copiii să nu ne iubească.</p>
    </section>"""

heros = [hero_center_dark, hero_split_white, hero_gradient_fun, hero_minimalist_border]
pkgs = [pkgs_grid, pkgs_alternating, pkgs_table]
srvs = [srv_cards, srv_text]

def generate_full_site(idx, name, color, font):
    h = heros[idx % len(heros)](name, color)
    p = pkgs[idx % len(pkgs)](color)
    s = srvs[idx % len(srvs)](color)
    
    # Amestecam ordinea sectiunilor pentru a nu fi deloc similare 
    # Site 0: Hero -> Services -> Packages
    # Site 1: Hero -> Packages -> Services
    order = idx % 2
    if order == 0:
        body = h + s + p
    else:
        body = h + p + s
    
    html = f'''---
import Layout from '../layouts/Layout.astro';
---
<Layout title="{name} - Petreceri Copii" description="Cele mai wow experiente alaturi de marca {name}. Mascote, baloane, vata zahar." canonicalURL="https://www.{(name.lower().replace('-',''))}.ro/">
    <main style="font-family: {font};">
        {body}
        <footer style="padding:4rem; text-align:center; background:#222; color:#fff;">
            <h2>Contactează {name}</h2>
            <p>Ne găsești la telefon pentru detalii și rezervări rapide.</p>
        </footer>
    </main>
</Layout>
'''
    return html

import subprocess
for idx, (folder, url, color, font) in enumerate(domains):
    path = os.path.join(r"C:\Users\ursac", folder, "src", "pages", "index.astro")
    html = generate_full_site(idx, folder, color, font)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

print("TOATE SITE-URILE AU FOST RESCRISE CU ARHITECTURI COMPLET DIFERITE!")
