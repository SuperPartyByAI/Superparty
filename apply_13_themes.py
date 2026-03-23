import os
import re

directories = [
    ("Kassia", "Kassia"),
    ("WowParty", "Wow"),
    ("Universeparty", "Universe"),
    ("Animaparty", "Anima"),
    ("Clubuldisney", "Clubuldisney"),
    ("Petreceritematice", "Petreceritematice"),
    ("Ursitoaremagice", "Ursitoaremagice"),
    ("Teraparty", "Teraparty"),
    ("Youparty", "Youparty"),
    ("Joyparty", "Joyparty"),
    ("Playparty", "Playparty"),
    ("123party", "123party"),
    ("Happyparty", "Happyparty")
]

themes = [
    {
        # 1. Kassia: Modern Corporate Soft
        "font_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap",
        "font_family": "'Inter', sans-serif",
        "bg_color": "#f8fafc",
        "p_bg": "#ffffff",
        "primary": "#2563eb",
        "secondary": "#3b82f6",
        "text": "#1e293b",
        "radius": "8px",
        "shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "hero_bg": "linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)",
        "card_border": "1px solid #e2e8f0"
    },
    {
        # 2. WowParty: Playful Kids Fredoka
        "font_url": "https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;700&display=swap",
        "font_family": "'Nunito', sans-serif",
        "font_head": "'Fredoka One', cursive",
        "bg_color": "#fffdf2",
        "p_bg": "#ffffff",
        "primary": "#ff007f",
        "secondary": "#ffb800",
        "text": "#333333",
        "radius": "24px",
        "shadow": "0 10px 20px rgba(255, 0, 127, 0.15)",
        "hero_bg": "radial-gradient(circle at top right, #ffb800, #ff007f)",
        "card_border": "4px solid #ffb800"
    },
    {
        # 3. Universeparty: Dark Space Neon
        "font_url": "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;700&display=swap",
        "font_family": "'Rajdhani', sans-serif",
        "font_head": "'Orbitron', sans-serif",
        "bg_color": "#0b0c10",
        "p_bg": "#1f2833",
        "primary": "#66fcf1",
        "secondary": "#45a29e",
        "text": "#c5c6c7",
        "radius": "0px",
        "shadow": "0 0 15px rgba(102, 252, 241, 0.4)",
        "hero_bg": "linear-gradient(to bottom, #0b0c10, #1f2833)",
        "card_border": "1px solid #45a29e"
    },
    {
        # 4. Animaparty: Forest Organic
        "font_url": "https://fonts.googleapis.com/css2?family=Quicksand:wght@400;700&display=swap",
        "font_family": "'Quicksand', sans-serif",
        "bg_color": "#f1f8f5",
        "p_bg": "#ffffff",
        "primary": "#2d6a4f",
        "secondary": "#52b788",
        "text": "#1b4332",
        "radius": "30px 0 30px 0",
        "shadow": "2px 2px 10px rgba(0,0,0,0.05)",
        "hero_bg": "linear-gradient(120deg, #d8f3dc 0%, #b7e4c7 100%)",
        "card_border": "none"
    },
    {
        # 5. Clubuldisney: Magic Elegant Red
        "font_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@400;700&display=swap",
        "font_family": "'Lato', sans-serif",
        "font_head": "'Playfair Display', serif",
        "bg_color": "#fff5f5",
        "p_bg": "#ffffff",
        "primary": "#e53e3e",
        "secondary": "#d69e2e",
        "text": "#2d3748",
        "radius": "12px",
        "shadow": "0 20px 25px -5px rgba(229, 62, 62, 0.1)",
        "hero_bg": "#e53e3e",
        "card_border": "1px solid #fed7d7"
    },
    {
        # 6. Petreceritematice: Retrowave Brutalism
        "font_url": "https://fonts.googleapis.com/css2?family=Righteous&family=Work+Sans:wght@400;700&display=swap",
        "font_family": "'Work Sans', sans-serif",
        "font_head": "'Righteous', cursive",
        "bg_color": "#ffe8f4",
        "p_bg": "#ffffff",
        "primary": "#805ad5",
        "secondary": "#dd6b20",
        "text": "#1a202c",
        "radius": "0px",
        "shadow": "8px 8px 0px #1a202c",
        "hero_bg": "linear-gradient(45deg, #805ad5, #dd6b20)",
        "card_border": "3px solid #1a202c"
    },
    {
        # 7. Ursitoaremagice: Ethereal Fairy Glass
        "font_url": "https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Montserrat:wght@300;400;700&display=swap",
        "font_family": "'Montserrat', sans-serif",
        "font_head": "'Caveat', cursive",
        "bg_color": "#f3e8ff",
        "p_bg": "rgba(255, 255, 255, 0.7)",
        "primary": "#a855f7",
        "secondary": "#ec4899",
        "text": "#4c1d95",
        "radius": "16px",
        "shadow": "0 8px 32px 0 rgba(31, 38, 135, 0.07)",
        "hero_bg": "linear-gradient(135deg, #fdf4ff 0%, #f3e8ff 100%)",
        "card_border": "1px solid rgba(255, 255, 255, 0.5)"
    },
    {
        # 8. Teraparty: Clean Tech
        "font_url": "https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap",
        "font_family": "'Roboto Mono', monospace",
        "bg_color": "#ffffff",
        "p_bg": "#f4f4f5",
        "primary": "#000000",
        "secondary": "#3f3f46",
        "text": "#27272a",
        "radius": "0px",
        "shadow": "none",
        "hero_bg": "#f4f4f5",
        "card_border": "1px dashed #d4d4d8"
    },
    {
        # 9. Youparty: Skewed Orange
        "font_url": "https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Open+Sans:wght@400;700&display=swap",
        "font_family": "'Open Sans', sans-serif",
        "font_head": "'Oswald', sans-serif",
        "bg_color": "#fffaf0",
        "p_bg": "#ffffff",
        "primary": "#dd6b20",
        "secondary": "#2b6cb0",
        "text": "#1a202c",
        "radius": "4px",
        "shadow": "0 4px 14px 0 rgba(221, 107, 32, 0.39)",
        "hero_bg": "#dd6b20",
        "card_border": "none"
    },
    {
        # 10. Joyparty: Soft Pastel Waves
        "font_url": "https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;700&display=swap",
        "font_family": "'Comfortaa', cursive",
        "bg_color": "#f0fdf4",
        "p_bg": "#ffffff",
        "primary": "#10b981",
        "secondary": "#f59e0b",
        "text": "#064e3b",
        "radius": "20px",
        "shadow": "0 10px 15px -3px rgba(16, 185, 129, 0.1)",
        "hero_bg": "linear-gradient(to right, #6ee7b7, #3b82f6)",
        "card_border": "none"
    },
    {
        # 11. Playparty: Contrast Dots
        "font_url": "https://fonts.googleapis.com/css2?family=Archivo+Black&family=Rubik:wght@400;700&display=swap",
        "font_family": "'Rubik', sans-serif",
        "font_head": "'Archivo Black', sans-serif",
        "bg_color": "#fef08a",
        "p_bg": "#ffffff",
        "primary": "#000000",
        "secondary": "#ef4444",
        "text": "#000000",
        "radius": "10px",
        "shadow": "5px 5px 0px rgba(0,0,0,1)",
        "hero_bg": "#fef08a",
        "card_border": "2px solid #000"
    },
    {
        # 12. 123party: Colorful Blocks
        "font_url": "https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&family=Poppins:wght@400;700&display=swap",
        "font_family": "'Poppins', sans-serif",
        "font_head": "'Comic Neue', cursive",
        "bg_color": "#e0e7ff",
        "p_bg": "#ffffff",
        "primary": "#4f46e5",
        "secondary": "#10b981",
        "text": "#312e81",
        "radius": "0 20px 0 20px",
        "shadow": "0 4px 6px rgba(0,0,0,0.05)",
        "hero_bg": "linear-gradient(90deg, #4f46e5 0%, #ec4899 100%)",
        "card_border": "3px solid #4f46e5"
    },
    {
        # 13. Happyparty: Sunset Vibe
        "font_url": "https://fonts.googleapis.com/css2?family=Pacifico&family=Mulish:wght@400;800&display=swap",
        "font_family": "'Mulish', sans-serif",
        "font_head": "'Pacifico', cursive",
        "bg_color": "#fff1f2",
        "p_bg": "#ffffff",
        "primary": "#f43f5e",
        "secondary": "#fb923c",
        "text": "#881337",
        "radius": "30px",
        "shadow": "0 20px 25px -5px rgba(244, 63, 94, 0.1)",
        "hero_bg": "linear-gradient(to right, #f43f5e, #fb923c)",
        "card_border": "none"
    }
]

base_dir = r"C:\Users\ursac"

def inject_layout(path, theme):
    layout_path = os.path.join(path, "src", "layouts", "Layout.astro")
    if not os.path.exists(layout_path): return
    with open(layout_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Adaugam fonturile Google in <head>
    font_link = f'    <link href="{theme["font_url"]}" rel="stylesheet">\n'
    if 'fonts.googleapis' not in content:
        content = content.replace('</head>', font_link + '</head>')
        
    with open(layout_path, "w", encoding="utf-8") as f:
        f.write(content)

def get_html_packages(prefix, display_name):
    packages = [
        {"n": "1", "price": "490 lei", "d": "1 Personaj · 2 ore", "f": ["Jocuri & concursuri", "Baloane & Pictură", "Dansuri & Diplome"]},
        {"n": "2", "price": "490 lei", "d": "2 Personaje · 1 oră (L–V)", "f": ["Jocuri & concursuri", "Baloane & Pictură", "Dansuri & Diplome"]},
        {"n": "3 ⭐", "price": "840 lei", "d": "2 Personaje · 2 ore + Confetti", "f": ["Confetti party", "Jocuri & concursuri", "Baloane & Pictură", "Dansuri & Diplome", "Boxă + Transport"]},
        {"n": "4", "price": "590 lei", "d": "1 Personaj · 1 oră + Tort dulciuri", "f": ["Tort dulciuri", "Jocuri & concursuri", "Baloane & Pictură"]},
        {"n": "5", "price": "840 lei", "d": "1 Pers. · 2 ore + 1h Vată + 1h Popcorn", "f": ["Aparat vată de zahăr", "Aparat popcorn", "Baloane & Pictură", "Jocuri & Dansuri"]},
        {"n": "6", "price": "540 lei", "d": "1 Animator · 2 ore + Banner + Confetti", "f": ["Banner personalizat", "Tun confetti", "Baloane & Pictură"]},
        {"n": "7 🎭", "price": "1290 lei", "d": "1 Animator · 3 ore + 4 Ursitoare", "f": ["Spectacol 4 ursitoare", "Baloane & Pictură", "Jocuri", "Extra atenție"]}
    ]
    
    html = f'''<section class="packages-section" id="pachete-rapide">
  <div class="container container-packages">
    <h2 class="section-title">Prețuri și Pachete {display_name}</h2>
    <p class="section-desc">Pachete perfecte, croite special pentru petreceri de neuitat. Transparență totală.</p>
    <div class="pricing-list-vertical">
    '''
    for i, p in enumerate(packages):
        hl = "highlight-row" if "⭐" in p["n"] else ""
        badge = '<span class="badge-pop">🔥 Recomandat</span>' if hl else ""
        html += f'''
      <div class="pricing-row {hl}">
        <div class="pricing-details">
          {badge}
          <h3 class="pkg-title">{prefix} {p["n"]}</h3>
          <p class="pkg-desc">{p["d"]}</p>
          <ul class="pkg-features">
'''
        for f in p["f"]:
            html += f'            <li><span>✓</span> {f}</li>\n'
        html += f'''          </ul>
        </div>
        <div class="pricing-cta">
          <div class="price-val">{p["price"]}</div>
          <a href="/contact/" class="btn-primary">Rezervă Pachetul</a>
        </div>
      </div>
'''
    html += '''    </div>
  </div>
</section>
'''
    return html

def inject_index(path, theme, prefix, display_name):
    idx_path = os.path.join(path, "src", "pages", "index.astro")
    if not os.path.exists(idx_path): return
    with open(idx_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extragem bucata de Hero și restul, curățăm styling-ul vechi.
    # Pentru unicitate 100%, rescriem body-ul din index folosind strict elementele de care avem nevoie.
    
    hero_html = f'''
  <section class="hero-section text-center">
    <div class="container hero-container">
      <h1 class="hero-title">{display_name} - Petreceri Copii</h1>
      <p class="hero-subtitle">Distracție absolută, animatori profesioniști, bucurie debordantă pentru toți copiii!</p>
      <div class="hero-cta">
        <a href="#pachete-rapide" class="btn-primary">Vezi Prețurile</a>
        <a href="/contact/" class="btn-secondary">Contact</a>
      </div>
    </div>
  </section>
'''

    new_html = hero_html + get_html_packages(prefix, display_name)
    
    # CSS Custom pentru unicitate maxima (Mobile-First responsive)
    # Folosim variabilele din theme
    font_head = theme.get("font_head", theme["font_family"])
    
    is_hero_dark = theme.get("hero_bg").startswith("linear") or theme.get("hero_bg").startswith("radial") or theme.get("hero_bg") == "#e53e3e" or theme.get("hero_bg") == "#dd6b20" or theme.get("hero_bg") == "#0b0c10" or theme.get("hero_bg") == "#4f46e5" or theme.get("hero_bg") == "#1e293b"

    hero_text_color = "#ffffff" if is_hero_dark else theme["text"]
    
    # Un pic de variatie suplimentara: unele designuri centreaza cardurile pe mobil, altele le tin flex row-wrap.
    # Pachetele sunt gandite ca flex box vertical care pe desktop devin randuri orizontale.
    
    css = f'''
<style>
  :root {{
    --bg-color: {theme["bg_color"]};
    --p-bg: {theme["p_bg"]};
    --primary: {theme["primary"]};
    --secondary: {theme["secondary"]};
    --text: {theme["text"]};
    --radius: {theme["radius"]};
    --shadow: {theme["shadow"]};
    --hero-bg: {theme["hero_bg"]};
    --card-border: {theme["card_border"]};
    --font-base: {theme["font_family"]};
    --font-head: {font_head};
  }}
  
  /* Reset and base styles */
  html, body {{
    margin: 0; padding: 0;
    background-color: var(--bg-color);
    color: var(--text);
    font-family: var(--font-base);
    line-height: 1.6;
    overflow-x: hidden;
  }}
  
  h1, h2, h3, .hero-title, .section-title, .pkg-title {{
    font-family: var(--font-head);
  }}
  
  .container {{
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
    box-sizing: border-box;
  }}
  
  /* HERO SECTION */
  .hero-section {{
    background: var(--hero-bg);
    color: {hero_text_color};
    padding: 6rem 1rem;
    position: relative;
    border-bottom: var(--card-border);
  }}
  
  /* Pentru teme asimetrice */
  @media(min-width: 992px) {{
    .hero-section {{
       padding: 8rem 2rem;
       display: flex; align-items: center; justify-content: center;
    }}
  }}
  
  .hero-title {{
    font-size: clamp(2.5rem, 5vw, 4rem);
    margin-bottom: 1rem;
    line-height: 1.2;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }}
  .hero-subtitle {{
    font-size: clamp(1.1rem, 2vw, 1.4rem);
    opacity: 0.9;
    max-width: 600px;
    margin: 0 auto 2.5rem;
  }}
  
  .hero-cta {{
    display: flex;
    flex-direction: column;
    gap: 1rem;
    align-items: center;
  }}
  
  @media(min-width: 600px) {{
    .hero-cta {{ flex-direction: row; justify-content: center; }}
  }}
  
  /* BUTTONS */
  .btn-primary, .btn-secondary {{
    display: inline-flex;
    justify-content: center;
    align-items: center;
    padding: 0.8rem 1.8rem;
    font-size: 1.1rem;
    font-weight: bold;
    text-decoration: none;
    border-radius: var(--radius);
    transition: all 0.3s ease;
    width: 100%;
    box-sizing: border-box;
    text-align: center;
    cursor: pointer;
  }}
  
  @media(min-width: 600px) {{
    .btn-primary, .btn-secondary {{ width: auto; }}
  }}
  
  .btn-primary {{
    background-color: var(--primary);
    color: #fff;
    border: 2px solid var(--primary);
  }}
  .btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow);
    filter: brightness(110%);
  }}
  
  .btn-secondary {{
    background-color: transparent;
    color: var(--primary);
    border: 2px solid var(--primary);
  }}
  /* For hero dark backgrounds */
  .hero-section .btn-secondary {{
    border-color: {hero_text_color};
    color: {hero_text_color};
  }}
  .btn-secondary:hover {{
    background-color: {hero_text_color};
    color: var(--primary);
  }}
  
  /* PACKAGES LIST (100% Mobile Friendly) */
  .packages-section {{
    padding: 4rem 1rem;
  }}
  
  .section-title {{
    text-align: center;
    font-size: clamp(2rem, 4vw, 3rem);
    color: var(--primary);
    margin-bottom: 0.5rem;
  }}
  .section-desc {{
    text-align: center;
    font-size: 1.1rem;
    color: var(--text);
    opacity: 0.8;
    margin-bottom: 3rem;
  }}
  
  .pricing-list-vertical {{
    display: flex;
    flex-direction: column;
    gap: 2rem;
    max-width: 900px;
    margin: 0 auto;
  }}
  
  .pricing-row {{
    background-color: var(--p-bg);
    border: var(--card-border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    transition: transform 0.2s;
  }}
  
  @media(min-width: 768px) {{
    .pricing-row {{
       flex-direction: row;
       align-items: center;
       justify-content: space-between;
       padding: 2rem 2.5rem;
    }}
  }}
  
  .pricing-row:hover {{
    transform: scale(1.02);
  }}
  
  .highlight-row {{
    border: 3px solid var(--secondary);
    position: relative;
    transform: scale(1.03);
    z-index: 10;
  }}
  .highlight-row:hover {{ transform: scale(1.05); }}
  
  .badge-pop {{
    background-color: var(--secondary);
    color: #fff;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 1rem;
    letter-spacing: 1px;
    text-transform: uppercase;
  }}
  
  .pricing-details {{
    flex: 1;
  }}
  
  .pkg-title {{
    font-size: 1.8rem;
    margin: 0 0 0.5rem 0;
    color: var(--text);
  }}
  .pkg-desc {{
    font-size: 1rem;
    opacity: 0.8;
    margin: 0 0 1.5rem 0;
  }}
  
  .pkg-features {{
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }}
  .pkg-features li {{
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    font-size: 0.95rem;
  }}
  .pkg-features li span {{
    color: var(--secondary);
    font-weight: bold;
  }}
  
  .pricing-cta {{
    text-align: center;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(0,0,0,0.05);
  }}
  
  @media(min-width: 768px) {{
    .pricing-cta {{
       border-top: none;
       border-left: 1px solid rgba(0,0,0,0.05);
       padding-top: 0;
       padding-left: 2rem;
       min-width: 200px;
    }}
  }}
  
  .price-val {{
    font-size: 2.5rem;
    font-weight: 900;
    color: var(--primary);
    margin-bottom: 1rem;
    font-family: var(--font-head);
  }}
  
  /* Fix layout overflow issue */
  img {{ max-width: 100%; height: auto; }}
</style>
'''
    
    # We load Layout.astro and import Layout
    import_html = f'''---
import Layout from '../layouts/Layout.astro';
---

<Layout 
  title="{display_name} - Animatori Petreceri Copii" 
  description="Pachete complete {display_name} pentru o petrecere de neuitat!"
  canonicalURL="https://www.{prefix.lower()}.ro/"
>
'''
    final_content = import_html + new_html + "\n</Layout>\n" + css
    
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write(final_content)

for t_idx, (dir_name, prefix) in enumerate(directories):
    theme = themes[t_idx % len(themes)]
    target_path = os.path.join(base_dir, dir_name)
    
    print(f"Applying Theme {t_idx+1} to {dir_name}...")
    inject_layout(target_path, theme)
    inject_index(target_path, theme, prefix, dir_name)

print("Toate cele 13 site-uri au primit noile identități vizuale (13 teme 100% distincte)!")
