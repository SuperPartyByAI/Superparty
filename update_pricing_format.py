import os
import re

sites = {
    r'c:\Users\ursac\WowParty': 'Wow',
    r'c:\Users\ursac\Universeparty': 'Universe',
    r'c:\Users\ursac\Animaparty': 'Anima',
    r'c:\Users\ursac\Kassia': 'Kassia'
}

def generate_html(prefix):
    return f"""<section id="pachete-rapide" class="pricing-horizontal-section">
  <div class="container">
    <h2 class="section-title text-center">Alege Pachetul Potrivit pentru Tine</h2>
    <p class="section-desc text-center">Pachete transparente și clare. Distracție maximă, zero costuri ascunse.</p>
    
    <div class="pricing-list-vertical">
      
      <div class="pricing-row">
        <div class="pricing-details">
          <h3>{prefix} 1</h3>
          <p class="pkg-desc">1 Personaj · 2 ore</p>
          <ul class="pkg-features">
            <li><span>✓</span> Jocuri & concursuri interactive</li>
            <li><span>✓</span> Baloane modelate & Pictură pe față</li>
            <li><span>✓</span> Dansuri, Tatuaje temporare, Diplome</li>
            <li><span>✓</span> Boxă portabilă & Transport gratuit (Buc+Ilfov)</li>
          </ul>
        </div>
        <div class="pricing-cta">
          <div class="price-val">490 lei</div>
          <a href="/contact/" class="btn-primary" style="display:block;text-align:center;">Rezervă Acum</a>
        </div>
      </div>

      <div class="pricing-row">
        <div class="pricing-details">
          <h3>{prefix} 2</h3>
          <p class="pkg-desc">2 Personaje · 1 oră (L–V)</p>
          <ul class="pkg-features">
            <li><span>✓</span> Jocuri & concursuri interactive</li>
            <li><span>✓</span> Baloane modelate & Pictură pe față</li>
            <li><span>✓</span> Dansuri, Tatuaje temporare, Diplome</li>
            <li><span>✓</span> Boxă portabilă & Transport gratuit (Buc+Ilfov)</li>
          </ul>
        </div>
        <div class="pricing-cta">
          <div class="price-val">490 lei</div>
          <a href="/contact/" class="btn-primary" style="display:block;text-align:center;">Rezervă Acum</a>
        </div>
      </div>

      <div class="pricing-row highlight-row">
        <div class="pricing-details">
          <span class="badge-pop">🔥 Cel mai ales</span>
          <h3>{prefix} 3 ⭐</h3>
          <p class="pkg-desc">2 Personaje · 2 ore + Confetti</p>
          <ul class="pkg-features">
            <li><span>✓</span> Confetti party spectaculos</li>
            <li><span>✓</span> Jocuri & concursuri interactive</li>
            <li><span>✓</span> Baloane modelate & Pictură pe față</li>
            <li><span>✓</span> Dansuri, Tatuaje temporare, Diplome</li>
            <li><span>✓</span> Boxă portabilă & Transport gratuit</li>
          </ul>
        </div>
        <div class="pricing-cta">
          <div class="price-val">840 lei</div>
          <a href="/contact/" class="btn-primary" style="display:block;text-align:center;">Rezervă Acum</a>
        </div>
      </div>

      <div class="pricing-row">
        <div class="pricing-details">
          <h3>{prefix} 4</h3>
          <p class="pkg-desc">1 Personaj · 1 oră + Tort dulciuri</p>
          <ul class="pkg-features">
            <li><span>✓</span> Tort din dulciuri (22–24 copii)</li>
            <li><span>✓</span> Jocuri, concursuri & Dansuri</li>
            <li><span>✓</span> Baloane modelate & Pictură pe față</li>
            <li><span>✓</span> Diplome magnetice, Boxă, Transport gratuit</li>
          </ul>
        </div>
        <div class="pricing-cta">
          <div class="price-val">590 lei</div>
          <a href="/contact/" class="btn-primary" style="display:block;text-align:center;">Rezervă Acum</a>
        </div>
      </div>

      <div class="pricing-row">
        <div class="pricing-details">
          <h3>{prefix} 5</h3>
          <p class="pkg-desc">1 Personaj · 2 ore + 1h Vată + 1h Popcorn</p>
          <ul class="pkg-features">
            <li><span>✓</span> Mașină vată de zahăr + popcorn</li>
            <li><span>✓</span> Jocuri, concursuri & Dansuri</li>
            <li><span>✓</span> Baloane modelate & Pictură pe față</li>
            <li><span>✓</span> Diplome magnetice, Boxă, Transport gratuit</li>
          </ul>
        </div>
        <div class="pricing-cta">
          <div class="price-val">840 lei</div>
          <a href="/contact/" class="btn-primary" style="display:block;text-align:center;">Rezervă Acum</a>
        </div>
      </div>

      <div class="pricing-row">
        <div class="pricing-details">
          <h3>{prefix} 6</h3>
          <p class="pkg-desc">1 Animator · 2 ore + Banner + Confetti</p>
          <ul class="pkg-features">
            <li><span>✓</span> Banner personalizat + Tun confetti</li>
            <li><span>✓</span> Jocuri, concursuri & Dansuri</li>
            <li><span>✓</span> Baloane modelate & Pictură pe față</li>
            <li><span>✓</span> Diplome magnetice, Boxă, Transport gratuit</li>
          </ul>
        </div>
        <div class="pricing-cta">
          <div class="price-val">540 lei</div>
          <a href="/contact/" class="btn-primary" style="display:block;text-align:center;">Rezervă Acum</a>
        </div>
      </div>

      <div class="pricing-row">
        <div class="pricing-details">
          <h3>{prefix} 7 🎭</h3>
          <p class="pkg-desc">1 Animator · 3 ore + 4 Ursitoare</p>
          <ul class="pkg-features">
            <li><span>✓</span> Spectacol 4 ursitoare botez</li>
            <li><span>✓</span> Jocuri, concursuri & Dansuri pentru extra copii</li>
            <li><span>✓</span> Baloane modelate & Pictură pe față</li>
            <li><span>✓</span> Diplome magnetice, Boxă, Transport gratuit</li>
          </ul>
        </div>
        <div class="pricing-cta">
          <div class="price-val">1290 lei</div>
          <a href="/contact/" class="btn-secondary" style="display:block;text-align:center;">Rezervă Acum</a>
        </div>
      </div>

    </div>
  </div>
</section>"""

for path, prefix in sites.items():
    idx_path = os.path.join(path, 'src', 'pages', 'index.astro')
    with open(idx_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = re.compile(r'<section[^>]*id="pachete-rapide".*?</section>', re.DOTALL)
    html = generate_html(prefix)
    
    if pattern.search(content):
        content = pattern.sub(html, content)
        with open(idx_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {prefix} with 7 packages at {path}")
    else:
        print(f"⚠️ Section not found in {path}")
