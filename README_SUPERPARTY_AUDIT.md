# Cum rulezi Auditul SEO & Upgrade-ul pentru Superparty

Acest repository folosește un sistem strict de tip `namespace` pentru a preveni coliziunile de indexare și configurare cu alte proiecte viitoare (ex: Animatopia). Toate scripturile și output-urile legate de acest domeniu forțează `siteId: "superparty"`.

## Pașii de Reproducere Locală:

### 1. Rularea Auditului Inițial (Strict)
Rulează scriptul nativ Python (nu necesită PIP):
```bash
python super_seo_audit.py
```
**Ce va face?**
- Va scana `src/content/seo-articles/` (500 MDX-uri).
- Va calcula limitele TF-IDF (Cosine Similarity). Risc ridicat = `>= 0.60`.
- Va raporta prezența Testimonialelor pe baza verificării URL Slug-ului în `src/data/superparty_testimonials.json`.
- Va produce rapoarte JSON/CSV strict separate în folderul `superparty_seo_audit_results/`.

### 2. Gestiunea Testimonialelor a Paginilor `Ready`
Paginile care nu au un JSON Valid în BD-ul dedicat ratează scorul de 10/10. Verificați manual raportul de lipsuri:
`superparty_seo_audit_results/superparty_testimonials_missing.csv`

Părinții (Editorii de conținut) pot injecta recenzii reale adăugând un obiect în formatul vizând `siteId`:
```json
{
  "siteId": "superparty",
  "slug": "Numele-Slug-Din-CSV",
  "location": "București",
  "name": "Maria Pop",
  "text": "..."
}
```

### 3. Rularea de Algoritm Upgrade SEO (Anti-Doorway)
Pentru transformarea articolelor noindex în unele scalabile 100% cu introduceri/concluzii generos diversificate matematic:
```bash
python rewrite_500_mdx.py
```

### 4. Generarea de Pagini Tăgăduite / Hubs
```bash
python create_hubs.py
```
Sitemap-ul final (`superparty_sitemap_recommendation.xml`) indexează strict paginile aprobate de auditor și de motorul Python (Status: Ready). Orice pagină hold rămâne ignorată automat.
