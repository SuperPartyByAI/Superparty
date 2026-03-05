# CHANGELOG

## v1.1.0 — 2026-03-05

### 🎉 Imagini & Galerie
- **galerie `/galerie/`**: extinsă de la 40 → **136 imagini** (10 animatori + 105 catalog costume + 8 decor + 4 vată + 4 ursitoare)
- **Load More**: galerie afișează 24 inițial, buton „↓ Încarcă mai multe" (+24/click) → DOM performant
- **105 poze catalog** personaje copiate din `Poze site superparty` (OneDrive Desktop) → `public/wp-content/uploads/catalog/`
- **448 versiuni WebP** generate cu `sharp` (thumb 400px + hero 1200px) → `public/optimized/`
- **GalleryGrid**: `<picture srcset>` WebP cu fallback JPEG — browser modern primește WebP 400px

### 🐛 Fix-uri
- **PhotoSlider**: URL-uri absolute (`SITE_ORIGIN`) + placeholder când imagini lipsesc
- **Testimonials**: `processReview()` aplicat pe homepage → mojibake **0** pe toate paginile
- **Canonical**: `www.superparty.ro` uniform peste tot (`SITE_ORIGIN` helper în `src/config/site.ts`)
- **WebP folder**: redenumit `_optimized → optimized` (Vercel blochează `_` prefix)
- **gallery.ts**: căi verificate din `public/` (nu mai sunt 404)

### 📋 Copy & UX
- **Benefits homepage**: „Peste 150 de personaje", ton neutru, disclaimer nevoi speciale
- **`galerie.astro`**: stat actualizat `30+ → 150+ Personaje`

### 🔧 Ops & CI
- **`scripts/optimize-images.mjs`**: generare WebP batch cu `sharp` (skip dacă deja există)
- **`scripts/backup-uploads.sh`**: arhivă `tar.gz` cu rotație (ultimele 7)
- **`scripts/restore-uploads.sh`**: rollback dintr-o arhivă
- **`.github/workflows/check-gallery-urls.yml`**: CI blocant (fișiere locale) + spot-check live non-blocant
- **`.github/workflows/optimize-images.yml`**: CI manual pentru generare WebP
- **`scripts/health_check.sh`**: gallery ≥49 check + CRITICAL alert pentru hero images non-200
- **`CONTRIBUTING.md`**: checklist adăugare imagini + regulă CI

### 📦 Commits incluse
| Commit | Descriere |
|---|---|
| `a3089e1` | `SITE_ORIGIN` + `siteUrl()` helper |
| `4292780` | PhotoSlider fix + benefits copy + Testimonials processReview |
| `c9e4e99` | gallery_images.ts căi verificate |
| `780fb6a` | 105 poze catalog |
| `33de369` | gallery.ts 136 imagini + CI guardrail |
| `ecb69b3` | Load More + optimize script + backup + hero health + CONTRIBUTING |
| `2cee8aa` | 448 WebP generate cu sharp |
| `b63da5b` | GalleryGrid picture srcset WebP |
| `latest` | Rename optimized + tag v1.1.0 |

---

## v1.0.0 — 2026-02-28
- Lansare inițială Astro site (migrare de pe WordPress/Hosterion)
- 89 URL-uri live, 230+ redirect-uri 301 din WordPress
- SEO: canonical www, sitemap.xml, robots.txt
- Hetzner VPS: Docker, Redis/RQ, health_check cron
