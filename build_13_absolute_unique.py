import os

themes = {
    "Kassia": {
        "color": "#10b981", "font": "Arial, sans-serif",
        "html": """
        <header style="background:#10b981; color:#fff; padding:6rem 2rem; text-align:center;">
            <h1>Magia Kassia Pentru Copilul Tău</h1>
            <p>Zâmbete memorabile cu mascote și animatori profesioniști.</p>
        </header>
        <section style="padding:4rem; background:#f9fafb;">
            <h2>Calitate Superioară</h2>
            <div style="column-count: 2;">Aducem energia pozitivă, baloane uriașe și jocuri captivante pentru o zi de neuitat. Nu facem compromisuri la costume.</div>
        </section>
        <section style="padding:4rem; text-align:center;">
            <h2>Servicii Exclusive</h2>
            <div style="display:flex; gap:1rem; flex-wrap:wrap; justify-content:center;">
                <div style="border:2px solid #10b981; padding:2rem;">🎭 Animatie Specială 490lei</div>
                <div style="border:2px solid #10b981; padding:2rem;">🎉 Paket Mega 840lei</div>
                <div style="border:2px solid #10b981; padding:2rem;">👗 Ursitoare 1290lei</div>
            </div>
        </section>
        """
    },
    "WowParty": {
        "color": "#f43f5e", "font": "Georgia, serif",
        "html": """
        <div style="display:flex; min-height:60vh;">
            <div style="flex:1; background:#f43f5e; color:white; padding:5rem;">
                <h1 style="font-size:4rem;">WOW! Așa petrecere?</h1>
                <p>Singura agenție care transformă serbările în spectacole explozive.</p>
            </div>
            <div style="flex:1; background:#222; padding:5rem; color:yellow;">
                <h2>Oferte Wow</h2>
                <ul>
                    <li>Clasic (1h) - 490 RON</li>
                    <li>Extins + Vata zahar - 840 RON</li>
                    <li>Premium Ursitoare - 1290 RON</li>
                </ul>
            </div>
        </div>
        """
    },
    "Universeparty": {
        "color": "#6366f1", "font": "Tahoma, sans-serif",
        "html": """
        <header style="background:url('https://images.unsplash.com/photo-1530103862676-de88d1f2eab1?auto=format&fit=crop&q=80'); background-size:cover; padding:10rem 2rem; text-align:center; color:white;">
            <h1 style="background:rgba(0,0,0,0.7); display:inline-block; padding:1rem;">O Galaxie de Distracție</h1>
        </header>
        <div style="background:#111; color:#ccc; padding:4rem;">
            <h2>Explorăm bucuria copiilor</h2>
            <p>De la pictură galactică pe față, la baloane în formă de rachete.</p>
            <hr>
            <h3>Tarifele Universe</h3>
            <p>Pachet Stea (490 lei) / Pachet Supernova (840 lei) / Pachet Botez (1290 lei)</p>
        </div>
        """
    },
    "Animaparty": {
        "color": "#14b8a6", "font": "Verdana, sans-serif",
        "html": """
        <main style="max-width:900px; margin:0 auto; padding:3rem; border:left 10px solid #14b8a6;">
            <h1 style="color:#14b8a6; font-size:4rem; border-bottom:1px solid #eee;">Sufletul Petrecerii Tale</h1>
            <p style="font-size:1.5rem; color:#555;">La AnimaParty, trăim pentru râsetele copiilor. Mascote curate, actori cu experiență pe scene de teatru.</p>
            <div style="background:#f4f4f4; padding:2rem; margin-top:3rem;">
                <h2>Alegeți Programul</h2>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:2rem;">
                    <div><strong>Standard (490L)</strong><br>Baloane si muzica</div>
                    <div><strong>Masiv (840L)</strong><br>Confetti si Vata Zahar</div>
                </div>
            </div>
        </main>
        """
    },
    "Clubuldisney": {
        "color": "#ef4444", "font": "Times New Roman, serif",
        "html": """
        <header style="background:#ef4444; color:white; text-align:center; padding:5rem 0; border-radius:0 0 50% 50%;">
            <h1 style="font-size:4.5rem;">Lumea Desenelor Animate 🏰</h1>
            <p>Zilnic aducem eroii preferați ai celor mici la realitate!</p>
        </header>
        <section style="padding:3rem 1rem; max-width:1000px; margin:0 auto;">
            <h2 style="text-align:center;">Opțiuni de Basm</h2>
            <table style="width:100%; border-collapse:collapse; margin-top:2rem;">
                <tr style="background:#eee;"><th>Nume Pachet</th><th>Detalii</th><th>Pret</th></tr>
                <tr><td>Mini-Prietenie</td><td>Figurine din baloane si dans</td><td>490 lei</td></tr>
                <tr><td>Petrecere Regala</td><td>Face painting, Boxa, Tun Confetti</td><td>840 lei</td></tr>
                <tr><td>Botez Basm</td><td>Patru Zâne Ursitoare Live</td><td>1290 lei</td></tr>
            </table>
        </section>
        """
    },
    "Petreceritematice": {
        "color": "#d946ef", "font": "Courier New, monospace",
        "html": """
        <div style="border:10px solid #d946ef; margin:2rem; padding:3rem; background:#000; color:#0f0;">
            <h1 style="font-size:3rem; text-transform:uppercase;">[Petreceri_Tematice_System]</h1>
            <p>Activare mod: DISTRACTIE ABSOLUTA.</p>
            <p>> Cautare Pirați, Prințese, Super-Eroi... GĂSIT!</p>
            <h2>// Pachete Disponibile</h2>
            <ul style="list-style-type:square;">
                <li>>> Basic_Run [490 LEI]: 1 character, 2 ore.</li>
                <li>>> Advanced_Setup [840 LEI]: Popcorn, Muzica, Confetti.</li>
                <li>>> Ultimate_Ursitoare [1290 LEI]: Show complet.</li>
            </ul>
        </div>
        """
    },
    "Ursitoaremagice": {
        "color": "#c026d3", "font": "Georgia, serif",
        "html": """
        <div style="background:linear-gradient(to bottom, #f3e8ff, #fff); padding:5rem 2rem; text-align:center;">
            <h1 style="color:#c026d3; font-style:italic; font-size:4rem;">Ursitoare Magice & Animatoare</h1>
            <p style="font-size:1.3rem; color:#666;">Scriem destine frumoase la botezuri și celebrăm primii ani de viață.</p>
        </div>
        <div style="display:flex; gap:2rem; padding:4rem; align-items:flex-start; justify-content:center; background:#fafafa;">
            <div style="background:#fff; padding:2rem; border-radius:20px; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
                <h3 style="color:#c026d3;">Zâne Botez</h3><p>Spectacol live, text personalizat, masina fum greu. - 1290 Lei</p>
            </div>
            <div style="background:#fff; padding:2rem; border-radius:20px; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
                <h3 style="color:#c026d3;">Zâne Petrecere (Aniversări)</h3><p>Jocuri dinamice si facepainting zanesc. - 490 Lei</p>
            </div>
             <div style="background:#fff; padding:2rem; border-radius:20px; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
                <h3 style="color:#c026d3;">Zâne Premium</h3><p>Popcorn, Tun confeti si magie pura. - 840 Lei</p>
            </div>
        </div>
        """
    },
    "Teraparty": {
        "color": "#3b82f6", "font": "Arial Black, sans-serif",
        "html": """
        <section style="display:flex; flex-direction:column; height:100vh;">
            <div style="flex:2; background:#3b82f6; display:flex; align-items:center; justify-content:center; color:white;">
                <h1 style="font-size:5rem; letter-spacing:-2px;">TeraParty.ro</h1>
            </div>
            <div style="flex:1; background:#111; display:flex; justify-content:space-around; align-items:center; color:white; padding:2rem;">
                <div><strong>Standard</strong> 490 lei<br><small>Doar distractie</small></div>
                <div><strong>Super</strong> 840 lei<br><small>Cu Vata & Popcorn</small></div>
                <div><strong>Elite</strong> 1290 lei<br><small>Botez VIP</small></div>
            </div>
        </section>
        """
    },
    "Youparty": {
        "color": "#f59e0b", "font": "Trebuchet MS, sans-serif",
        "html": """
        <div style="padding:4rem; text-align:right; border-right:20px solid #f59e0b; background:#fffcf2;">
            <h1 style="font-size:4rem; color:#333;">Aici Tu Faci Regulile!</h1>
            <p style="font-size:1.5rem;">Cea mai smechera echipa de Kids Party din oras.</p>
            <br><br>
            <h2 style="color:#f59e0b;">Lista de preturi (Scurta si la obiect):</h2>
            <div style="font-size:1.2rem; line-height:2;">
                👉 Pachet Distractie Generala = 490 LEI<br>
                👉 Pachet Show Confetti/Vata = 840 LEI<br>
                👉 Pachet Spectacol Botez = 1290 LEI
            </div>
        </div>
        """
    },
    "Joyparty": {
         "color": "#10b981", "font": "Arial, sans-serif",
         "html": """
        <header style="background:radial-gradient(circle, #fff, #bbf7d0); padding:8rem 2rem; text-align:center;">
            <h1 style="color:#065f46; font-size:4rem; margin-bottom:2rem;">Pură Bucurie Joy!</h1>
            <div style="display:inline-block; padding:2rem; background:#fff; border-radius:30px; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
                <p><strong>Bucurie Pachet Mica</strong> - 490 RON (Baloane, boxa mica)</p>
                <p><strong>Bucurie Pachet Mare</strong> - 840 RON (Aparat popcorn, jocuri)</p>
                <p><strong>Bucurie Botez</strong> - 1290 RON (Cele 4 Zâne Ursitoare)</p>
            </div>
        </header>
         """
    },
    "Playparty": {
        "color": "#000000", "font": "Impact, sans-serif",
        "html": """
        <div style="background:#000; color:#fff; padding:5rem; text-transform:uppercase;">
            <h1 style="font-size:6rem; color:#fef08a; margin:0;">PLAY! PARTY!</h1>
            <h2>Apasa butonul de basm.</h2>
            <hr style="border-color:#333; margin:3rem 0;">
            <div style="display:flex; justify-content:space-between; font-size:1.5rem;">
                <span>START GAME (490 LEI)</span>
                <span>LEVEL UP (840 LEI)</span>
                <span>BOSS STAGE BOTEZ (1290 LEI)</span>
            </div>
        </div>
        """
    },
    "123party": {
        "color": "#ec4899", "font": "Comic Sans MS, cursive",
        "html": """
        <div style="text-align:center; padding:3rem; background:#fdf2f8;">
            <h1 style="color:#ec4899; font-size:5rem;">1, 2, 3... Gata Petrecerea!</h1>
            <p style="font-size:1.4rem;">Fără bătăi de cap, fără stres. Tu suni, noi venim cu nebunia!</p>
            <div style="margin-top:4rem; display:flex; gap:1rem; overflow-x:auto;">
                <div style="min-width:300px; background:white; padding:2rem; border-radius:10px; border:2px dashed #ec4899;">1️⃣ Varianta Simpla - 490 Lei</div>
                <div style="min-width:300px; background:white; padding:2rem; border-radius:10px; border:2px dashed #ec4899;">2️⃣ Varianta cu Delicii - 840 Lei</div>
                <div style="min-width:300px; background:white; padding:2rem; border-radius:10px; border:2px dashed #ec4899;">3️⃣ Varianta Magica Botez - 1290 Lei</div>
            </div>
        </div>
        """
    },
    "Happyparty": {
        "color": "#f43f5e", "font": "Georgia, serif",
        "html": """
        <header style="padding:5rem 2rem; display:flex; align-items:center; justify-content:space-between; background:#fff0f2;">
            <h1 style="font-size:4rem; color:#e11d48; width:50%;">Zâmbește! A sosit Happy Party 😁</h1>
            <div style="width:40%; background:white; padding:2rem; border-radius:15px; box-shadow:0 0 20px rgba(0,0,0,0.05);">
                <h3>Alege pachetul de zâmbete:</h3>
                <ul style="line-height:2.5;">
                    <li>🎈 Pachet Happy - 490 lei</li>
                    <li>🍿 Pachet Super Happy - 840 lei</li>
                    <li>🧚‍♀️ Ursitoare Happy - 1290 lei</li>
                </ul>
            </div>
        </header>
        """
    }
}

base_dir = r"C:\Users\ursac"

for domain, data in themes.items():
    path = os.path.join(base_dir, domain, "src", "pages", "index.astro")
    html_content = f"""---
import Layout from '../layouts/Layout.astro';
---
<Layout title="Petreceri Copii Premium - {domain}" description="Agentia lider in animatori petreceri copii {domain}." canonicalURL="https://www.{domain.lower()}.ro/">
    <main style="font-family: {data['font']};">
        {data['html']}
        <footer style="text-align:center; padding:2rem; margin-top:3rem; font-size:0.9rem; color:#aaa;">
            &copy; 2026 {domain} Bucuresti - Ilfov. All rights reserved. Servicii Animatie Premium.
        </footer>
    </main>
</Layout>
"""
    if os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Generated ABSOLUTE UNIQUE design & text for {domain}")
    else:
        print(f"Directory {domain} missing.")
