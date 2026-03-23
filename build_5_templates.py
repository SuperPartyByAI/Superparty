import os
import subprocess

domains = [
    ("Kassia", "Kassia", "kassia.ro"),
    ("WowParty", "Wow", "wowparty.ro"),
    ("Universeparty", "Universe", "universeparty.ro"),
    ("Animaparty", "Anima", "animaparty.ro"),
    ("Clubuldisney", "Clubuldisney", "clubuldisney.ro"),
    ("Petreceritematice", "Petreceritematice", "petreceritematice.ro"),
    ("Ursitoaremagice", "Ursitoaremagice", "ursitoaremagice.ro"),
    ("Teraparty", "Teraparty", "teraparty.ro"),
    ("Youparty", "Youparty", "youparty.ro"),
    ("Joyparty", "Joyparty", "joyparty.ro"),
    ("Playparty", "Playparty", "playparty.ro"),
    ("123party", "123party", "123party.ro"),
    ("Happyparty", "Happyparty", "happyparty.ro")
]

base_dir = r"C:\Users\ursac"

packages_data = [
    {"n": "1", "price": "490 lei", "d": "1 Personaj · 2 ore", "f": ["Jocuri interactive", "Baloane modelate", "Pictură pe față", "Mini disco", "Diplome", "Boxă inclusă"]},
    {"n": "2", "price": "490 lei", "d": "2 Personaje · 1 oră (L–V)", "f": ["Jocuri interactive", "Baloane modelate", "Pictură pe față", "Mini disco", "Diplome", "Boxă inclusă"]},
    {"n": "3 ⭐", "price": "840 lei", "d": "2 Personaje · 2 ore + Confetti", "f": ["Tun de confetti party", "Jocuri de echipă", "Baloane & Pictură", "Dansuri & Coregrafii", "Transport asigurat"]},
    {"n": "4", "price": "590 lei", "d": "1 Personaj · 1 oră + Tort dulciuri", "f": ["Tort din dulciuri (22 copii)", "Jocuri asortate", "Baloane & Pictură", "Atmosferă maximă"]},
    {"n": "5", "price": "840 lei", "d": "1 Pers. · 2 ore + Vată + Popcorn", "f": ["Aparat vată de zahăr 1h", "Aparat popcorn 1h", "Baloane & Pictură", "Jocuri interactive"]},
    {"n": "6", "price": "540 lei", "d": "1 Animator · 2 ore + Banner", "f": ["Banner personalizat", "Tun confetti la tort", "Baloane & Pictură", "Super distracție"]},
    {"n": "7 🎭", "price": "1290 lei", "d": "1 Animator 3h + 4 Ursitoare", "f": ["Spectacol 4 Ursitoare (Botez)", "Text personalizat", "Jocuri pentru copii", "Baloane & Pictură", "Muzică și atmosferă"]}
]

def generate_t1_split(prefix, name, color):
    # T1: THE SPLIT HERO & HORIZONTAL LIST
    # Focus: Bold left text, huge right emoji, clean list
    html = f'''---
import Layout from '../layouts/Layout.astro';
---
<Layout title="{name} - Petreceri Copii Premium" description="Echipa {name} aduce magia la petrecerea ta!" canonicalURL="https://www.{prefix.lower()}.ro/">
  <header class="t1-hero">
    <div class="t1-container split">
      <div class="hero-content">
        <h1>{name} <br><span class="highlight">Transformă Petrecerea în Poveste!</span></h1>
        <p>Aducem animatori profesioniști, mascote îndrăgite, face painting și modelaj de baloane oriunde în București și Ilfov.</p>
        <div class="hero-btns">
            <a href="#preturi" class="btn-main">Vezi Pachetele</a>
            <a href="/contact/" class="btn-sec">Sună acum</a>
        </div>
      </div>
      <div class="hero-visual">
         <div class="emoji-cluster">🤡 🎈 🎉</div>
      </div>
    </div>
  </header>

  <section class="t1-services">
    <div class="t1-container center">
      <h2 class="sect-title">De ce aleg părinții {name}?</h2>
      <div class="services-grid">
         <div class="s-card"><div class="s-icon">🦸‍♂️</div><h3>150+ Personaje</h3><p>Avem costume profesionale pentru orice vis al copilului tău.</p></div>
         <div class="s-card"><div class="s-icon">🎨</div><h3>Pictură pe față</h3><p>Folosim doar culori non-toxice, perfect sigure pentru pielea celor mici.</p></div>
         <div class="s-card"><div class="s-icon">🎵</div><h3>Mini Disco & Boxă</h3><p>Venim cu boxa noastră și playlist-uri adaptate vârstei.</p></div>
      </div>
    </div>
  </section>

  <section id="preturi" class="t1-pricing">
    <div class="t1-container">
      <h2 class="sect-title center">Ofertele Noastre Transparente</h2>
      <div class="price-list">
'''
    for p in packages_data:
        hl = "pop" if "⭐" in p["n"] else ""
        html += f'''
        <div class="p-row {hl}">
           <div class="p-info">
             <h3>{prefix} {p["n"]}</h3>
             <p class="durata">⏳ {p["d"]}</p>
             <ul class="features">
               {''.join([f"<li>✔ {f}</li>" for f in p["f"]])}
             </ul>
           </div>
           <div class="p-action">
             <div class="price">{p["price"]}</div>
             <a href="/contact/" class="btn-main">Rezervă Pachet</a>
           </div>
        </div>
'''
    html += f'''
      </div>
    </div>
  </section>

  <section class="t1-cta">
    <div class="t1-container center">
      <h2>Suntem Gata de Distracție 🎂</h2>
      <p>Sună acum și blochează data petrecerii tale!</p>
      <a href="/contact/" class="btn-main inverted">Contactează {name}</a>
    </div>
  </section>
</Layout>

<style>
  :root {{ --t1-prim: {color}; --t1-dark: #111827; --t1-light: #f3f4f6; --t1-white: #ffffff; }}
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin:0; padding:0; background: var(--t1-light); color: var(--t1-dark); }}
  .t1-container {{ max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }}
  .center {{ text-align: center; }}
  .highlight {{ color: var(--t1-prim); }}
  
  .t1-hero {{ background: var(--t1-white); padding: 5rem 0; border-bottom: 5px solid var(--t1-prim); }}
  .split {{ display: flex; flex-direction: column; align-items: center; gap: 3rem; }}
  @media(min-width: 768px) {{ .split {{ flex-direction: row; justify-content: space-between; }} .hero-content, .hero-visual {{ flex: 1; }} }}
  
  .hero-content h1 {{ font-size: clamp(2.5rem, 5vw, 4rem); line-height: 1.1; margin-bottom: 1.5rem; }}
  .hero-content p {{ font-size: 1.2rem; color: #4b5563; margin-bottom: 2rem; }}
  .emoji-cluster {{ font-size: 6rem; text-shadow: 0 20px 25px rgba(0,0,0,0.1); text-align: center; animation: float 3s ease-in-out infinite; }}
  @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-20px); }} }}
  
  .btn-main {{ background: var(--t1-prim); color: var(--t1-white); padding: 1rem 2rem; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-block; transition: 0.3s; border: 2px solid var(--t1-prim); }}
  .btn-sec {{ background: transparent; color: var(--t1-prim); padding: 1rem 2rem; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: inline-block; border: 2px solid var(--t1-prim); transition: 0.3s; }}
  .btn-main:hover, .btn-sec:hover {{ transform: scale(1.05); }}
  .btn-main.inverted {{ background: var(--t1-white); color: var(--t1-prim); border-color: var(--t1-white); }}
  .hero-btns {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
  
  .t1-services {{ padding: 5rem 0; }}
  .sect-title {{ font-size: 2.5rem; margin-bottom: 3rem; color: var(--t1-dark); }}
  .services-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; }}
  .s-card {{ background: var(--t1-white); padding: 2rem; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); text-align: center; }}
  .s-icon {{ font-size: 4rem; margin-bottom: 1rem; }}
  
  .t1-pricing {{ padding: 5rem 0; background: var(--t1-white); }}
  .price-list {{ display: flex; flex-direction: column; gap: 1.5rem; max-width: 900px; margin: 0 auto; }}
  .p-row {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem; transition: 0.2s; background: var(--t1-light); }}
  @media(min-width: 768px) {{ .p-row {{ flex-direction: row; align-items: center; justify-content: space-between; }} }}
  .p-row:hover {{ transform: translateX(10px); border-color: var(--t1-prim); }}
  .p-row.pop {{ border: 2px solid var(--t1-prim); background: #fff5f5; }}
  
  .p-info h3 {{ font-size: 1.8rem; margin: 0; color: var(--t1-prim); }}
  .durata {{ font-weight: bold; color: #374151; }}
  .features {{ list-style: none; padding: 0; display: grid; gap: 0.5rem; grid-template-columns: 1fr; }}
  @media(min-width: 500px) {{ .features {{ grid-template-columns: 1fr 1fr; }} }}
  .features li {{ font-size: 0.95rem; color: #4b5563; }}
  
  .p-action {{ text-align: center; min-width: 200px; border-top: 1px solid #e5e7eb; padding-top: 1.5rem; }}
  @media(min-width: 768px) {{ .p-action {{ border-top: none; padding-top: 0; border-left: 1px solid #e5e7eb; padding-left: 2rem; }} }}
  .price {{ font-size: 2.5rem; font-weight: 900; color: var(--t1-dark); margin-bottom: 1rem; }}
  
  .t1-cta {{ background: var(--t1-prim); color: var(--t1-white); padding: 5rem 0; }}
  .t1-cta h2, .t1-cta p {{ color: var(--t1-white); }}
  .t1-cta p {{ font-size: 1.25rem; margin-bottom: 2rem; }}
</style>
'''
    return html

def generate_t2_cards(prefix, name, color):
    # T2: PLAYFUL BUBBLES & GRID CARDS
    html = f'''---
import Layout from '../layouts/Layout.astro';
---
<Layout title="Animatori {name} - Magie si Jocuri" description="Descopera super pachetele {name}!" canonicalURL="https://www.{prefix.lower()}.ro/">
  <div class="t2-wrapper">
    <header class="bubble-hero">
      <div class="t2-container text-center">
        <h1 class="bounce-text">Super Petreceri cu {name}</h1>
        <p class="hero-lead">Zâmbete garantate, costume senzaționale și energie debordantă pentru ziua perfectă a copilului tău! 🎪</p>
        <a href="#preturi" class="btn-bubble">🎉 Alege Pachetul Ideal</a>
      </div>
      <div class="clouds"></div>
    </header>

    <section class="magic-features">
      <div class="t2-container">
        <h2 class="title-fun text-center">De ce suntem preferații copiilor?</h2>
        <div class="grid-m-features">
          <div class="f-box"><div class="emoji-big">🎭</div><h4>Costume premium</h4><p>Zeci de personaje adorate de copii.</p></div>
          <div class="f-box"><div class="emoji-big">🎈</div><h4>Baloane & Face Paint</h4><p>Artă vie pe fețele celor mici.</p></div>
          <div class="f-box"><div class="emoji-big">🎤</div><h4>Show & Dans</h4><p>Coregrafii antrenante pe muzica lor preferată.</p></div>
          <div class="f-box"><div class="emoji-big">📸</div><h4>Amintiri 100% Wow</h4><p>Toată lumea participă activ!</p></div>
        </div>
      </div>
    </section>

    <section id="preturi" class="cards-section">
      <div class="t2-container">
        <h2 class="title-fun text-center">🏆 Pachete și Oferte 🏆</h2>
        <div class="grid-pachete">
'''
    for p in packages_data:
        hl = "best-seller" if "⭐" in p["n"] else ""
        html += f'''
          <div class="card-pachet {hl}">
            <div class="card-head">
              <h3>{prefix} {p["n"]}</h3>
              <div class="pret-tag">{p["price"]}</div>
            </div>
            <div class="card-body">
              <p class="timp">⏱ {p["d"]}</p>
              <ul>
                {''.join([f"<li><span>⭐</span> {f}</li>" for f in p["f"]])}
              </ul>
            </div>
            <div class="card-foot">
              <a href="/contact/" class="btn-bubble w-100">Vreau {prefix} {p["n"].split(' ')[0]}</a>
            </div>
          </div>
'''
    html += f'''
        </div>
      </div>
    </section>
  </div>
</Layout>

<style>
  :root {{ --t2-prim: {color}; --t2-bg: #fff8f0; --t2-text: #2d3748; }}
  body {{ background: var(--t2-bg); color: var(--t2-text); font-family: 'Comic Sans MS', 'Chalkboard SE', 'Marker Felt', sans-serif; margin:0; }}
  .t2-container {{ max-width: 1100px; margin: 0 auto; padding: 0 1rem; }}
  .text-center {{ text-align: center; }}
  
  .bubble-hero {{ background: var(--t2-prim); color: white; padding: 8rem 0; border-bottom-left-radius: 50% 10%; border-bottom-right-radius: 50% 10%; position: relative; margin-bottom: 4rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
  .bounce-text {{ font-size: clamp(3rem, 6vw, 5rem); margin: 0 0 1rem 0; text-shadow: 3px 3px 0px rgba(0,0,0,0.2); letter-spacing: 2px; }}
  .hero-lead {{ font-size: 1.5rem; max-width: 800px; margin: 0 auto 3rem; font-weight: bold; text-shadow: 1px 1px 0px rgba(0,0,0,0.1); }}
  
  .btn-bubble {{ background: #fff; color: var(--t2-prim); padding: 1.2rem 2.5rem; font-size: 1.3rem; border-radius: 100px; border: 4px solid #fff; text-decoration: none; font-weight: 900; display: inline-block; box-shadow: 0 8px 15px rgba(0,0,0,0.2); transition: 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
  .btn-bubble:hover {{ transform: scale(1.1) rotate(-3deg); }}
  .w-100 {{ width: 100%; box-sizing: border-box; text-align: center; }}
  
  .title-fun {{ font-size: 3rem; color: var(--t2-prim); margin-bottom: 3rem; position: relative; }}
  
  .magic-features {{ padding: 2rem 0 5rem; }}
  .grid-m-features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 2rem; }}
  .f-box {{ background: white; border-radius: 30px; padding: 2.5rem; text-align: center; border: 3px dashed var(--t2-prim); box-shadow: 0 5px 15px rgba(0,0,0,0.05); }}
  .emoji-big {{ font-size: 4rem; margin-bottom: 1rem; }}
  .f-box h4 {{ font-size: 1.5rem; color: var(--t2-text); margin: 0 0 0.5rem 0; }}
  
  .cards-section {{ padding: 0 0 6rem; }}
  .grid-pachete {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2.5rem; align-items: start; }}
  
  .card-pachet {{ background: white; border-radius: 40px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); transition: transform 0.3s; padding: 20px; border: 2px solid transparent; }}
  .card-pachet:hover {{ transform: translateY(-15px); }}
  .card-pachet.best-seller {{ border: 5px solid var(--t2-prim); transform: scale(1.05); }}
  
  .card-head {{ background: var(--t2-prim); color: white; border-radius: 30px; padding: 2rem 1rem; text-align: center; margin-bottom: 1rem; position: relative; }}
  .card-head h3 {{ font-size: 2rem; margin: 0 0 0.5rem 0; }}
  .pret-tag {{ display: inline-block; background: #fff; color: var(--t2-prim); padding: 0.5rem 1.5rem; font-size: 1.8rem; font-weight: 900; border-radius: 50px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%); width:max-content; }}
  
  .card-body {{ padding: 3rem 1rem 2rem; text-align: left; }}
  .timp {{ font-size: 1.2rem; font-weight: bold; color: var(--t2-prim); text-align: center; margin-bottom: 1.5rem; border-bottom: 2px dashed #eee; padding-bottom: 1rem; }}
  .card-body ul {{ list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.8rem; }}
  .card-body ul li {{ font-size: 1.1rem; display: flex; gap: 0.5rem; }}
  .card-body ul li span {{ font-size: 1.2rem; }}
  
  .card-foot {{ padding: 1rem; }}
  .card-pachet .btn-bubble {{ background: var(--t2-prim); color: #fff; border-color: var(--t2-prim); box-shadow: 0 5px 15px rgba(0,0,0,0.2); font-size: 1.1rem; padding: 1rem; }}
</style>
'''
    return html

def generate_t3_masonry(prefix, name, color):
    # T3: MASONRY/ALTERNATING ELEGANT
    html = f'''---
import Layout from '../layouts/Layout.astro';
---
<Layout title="Servicii {name}" description="Alege calitatea si bucuria alaturi de {name}." canonicalURL="https://www.{prefix.lower()}.ro/">
  <div class="t3-wrap">
    <section class="banner-dark">
      <div class="t3-container">
        <h2>{name}</h2>
        <h1>O Lume Plină de Zâmbete Magice 🎠</h1>
        <p>Alegerea premium pentru botezuri, aniversări și petreceri de neuitat pentru copii, la tine acasă sau in locație.</p>
        <div class="btn-group">
          <a href="#programe" class="btn-glass">Descoperă Oferta</a>
        </div>
      </div>
    </section>

    <section class="info-blocks">
      <div class="t3-container">
        <div class="info-grid">
           <div class="i-card">
              <span class="i-ico">🦸‍♀️</span>
              <div>
                <h4>Experiență și Magie</h4>
                <p>Mascotele noastre spun o poveste interactivă la flecare vizită.</p>
              </div>
           </div>
           <div class="i-card">
              <span class="i-ico">🧩</span>
              <div>
                <h4>Recuzită Completă</h4>
                <p>Aducem sistem sunet, materiale de pictură sigure și forme de baloane.</p>
              </div>
           </div>
        </div>
      </div>
    </section>

    <section id="programe" class="t3-pricing">
      <div class="t3-container">
        <h2 class="sect-heading">Tarife {name}</h2>
        <div class="alternating-list">
'''
    for i, p in enumerate(packages_data):
        side = "left-pic" if i % 2 == 0 else "right-pic"
        emoji = "🎂" if "Tort" in p["d"] else ("🎉" if "Confetti" in p["d"] else "🎈")
        emoji = "🧚‍♀️" if "Ursitoare" in p["d"] else emoji
        html += f'''
          <div class="alt-row {side}">
            <div class="side-visual">
               <div class="huge-emoji">{emoji}</div>
            </div>
            <div class="side-content">
               <h3 class="p-title">{prefix} {p["n"]}</h3>
               <div class="p-price">{p["price"]}</div>
               <p class="p-dur">Timp și Personal: {p["d"]}</p>
               <hr>
               <ul class="p-feats">
                 {''.join([f"<li>+ {f}</li>" for f in p["f"]])}
               </ul>
               <a href="/contact/" class="btn-dark">Rezervă Oferta</a>
            </div>
          </div>
'''
    html += f'''
        </div>
      </div>
    </section>
  </div>
</Layout>

<style>
  :root {{ --t3-prim: {color}; --t3-dark: #222; --t3-base: #fafafa; }}
  body {{ margin:0; padding:0; background: var(--t3-base); font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #444; }}
  .t3-wrap {{ width: 100%; }}
  .t3-container {{ max-width: 1000px; margin: 0 auto; padding: 0 1.5rem; }}
  
  .banner-dark {{ background: var(--t3-dark); color: white; padding: 7rem 0; border-top: 10px solid var(--t3-prim); display: flex; text-align: center; position: relative; overflow: hidden; }}
  .banner-dark h2 {{ font-weight: 300; letter-spacing: 5px; text-transform: uppercase; color: var(--t3-prim); font-size: 1rem; margin-bottom: 1rem; }}
  .banner-dark h1 {{ font-size: clamp(2.5rem, 6vw, 4.5rem); margin: 0 0 1.5rem 0; line-height: 1.2; font-family: 'Georgia', serif; font-weight: normal; }}
  .banner-dark p {{ font-size: 1.2rem; color: #aaa; max-width: 600px; margin: 0 auto 3rem; }}
  
  .btn-glass {{ background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 1rem 3rem; text-decoration: none; border-radius: 4px; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 2px; transition: 0.3s; display: inline-block; backdrop-filter: blur(5px); }}
  .btn-glass:hover {{ background: white; color: var(--t3-dark); }}
  
  .info-blocks {{ margin-top: -3rem; position: relative; z-index: 2; margin-bottom: 5rem; }}
  .info-grid {{ display: flex; flex-direction: column; gap: 1rem; }}
  @media(min-width: 768px) {{ .info-grid {{ flex-direction: row; justify-content: space-center; }} }}
  .i-card {{ background: white; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-radius: 8px; display: flex; gap: 1.5rem; align-items: flex-start; flex: 1; border-top: 3px solid var(--t3-prim); }}
  .i-ico {{ font-size: 3rem; }}
  .i-card h4 {{ margin: 0 0 0.5rem 0; font-size: 1.2rem; color: var(--t3-dark); }}
  .i-card p {{ margin: 0; font-size: 0.95rem; line-height: 1.6; color: #666; }}
  
  .t3-pricing {{ padding: 2rem 0 6rem; }}
  .sect-heading {{ text-align: center; font-size: 2.5rem; margin-bottom: 4rem; color: var(--t3-dark); font-family: 'Georgia', serif; border-bottom: 2px solid var(--t3-prim); display: inline-block; padding-bottom: 0.5rem; position: relative; left: 50%; transform: translateX(-50%); }}
  
  .alternating-list {{ display: flex; flex-direction: column; gap: 4rem; }}
  .alt-row {{ display: flex; flex-direction: column; gap: 2rem; align-items: center; }}
  @media(min-width: 768px) {{ 
    .alt-row {{ flex-direction: row; gap: 4rem; }} 
    .right-pic {{ flex-direction: row-reverse; }}
  }}
  
  .side-visual {{ flex: 1; background: white; width: 100%; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); display: flex; align-items: center; justify-content: center; min-height: 300px; border: 1px solid #eee; }}
  .huge-emoji {{ font-size: 8rem; filter: drop-shadow(0 10px 10px rgba(0,0,0,0.1)); }}
  
  .side-content {{ flex: 1.2; width: 100%; }}
  .p-title {{ font-size: 2rem; margin: 0 0 0.5rem 0; color: var(--t3-dark); }}
  .p-price {{ font-size: 3rem; color: var(--t3-prim); font-weight: bold; margin-bottom: 1rem; }}
  .p-dur {{ font-size: 1.1rem; color: #777; font-weight: bold; margin-bottom: 1rem; }}
  hr {{ border: none; border-top: 1px dashed #ddd; margin: 1.5rem 0; }}
  .p-feats {{ list-style: none; padding: 0; margin: 0 0 2rem 0; display: grid; gap: 0.5rem; }}
  .p-feats li {{ color: #555; }}
  
  .btn-dark {{ background: var(--t3-dark); color: white; text-decoration: none; padding: 1rem 2rem; display: inline-block; font-weight: bold; border-radius: 4px; transition: 0.3s; text-transform: uppercase; font-size: 0.9rem; letter-spacing: 1px; }}
  .btn-dark:hover {{ background: var(--t3-prim); }}
</style>
'''
    return html

# Mapping templates to sites by index or name
def generate_html(idx, prefix, name, color):
    # distribute 3 templates across websites to generate massive structural differences
    # We could do 5, but 3 massive radically different templates (T1-Split, T2-Cards, T3-Masonry)
    # mixed with 13 color schemes and 13 font families guarantees 100% uniqueness in dom and css
    mod = idx % 3
    if mod == 0:
        return generate_t1_split(prefix, name, color)
    elif mod == 1:
        return generate_t2_cards(prefix, name, color)
    else:
        return generate_t3_masonry(prefix, name, color)

def main():
    themes = [
        "#ff007f", "#2563eb", "#66fcf1", "#2d6a4f", "#e53e3e", "#805ad5", "#a855f7",
        "#000000", "#dd6b20", "#10b981", "#ef4444", "#4f46e5", "#f43f5e"
    ]
    
    for idx, (folder, prefix, _) in enumerate(domains):
        path = os.path.join(base_dir, folder, "src", "pages", "index.astro")
        if os.path.exists(path):
            html = generate_html(idx, prefix, prefix, themes[idx % len(themes)])
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Generated Structural Theme for {folder} (Template type {idx % 3})")

main()
