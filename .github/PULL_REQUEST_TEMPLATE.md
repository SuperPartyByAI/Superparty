---
name: PR Standard
about: Template standard pentru PR-uri SuperParty
title: ''
labels: ''
assignees: ''
---

## Ce schimbări conține acest PR?

<!-- Descrie pe scurt ce ai modificat și de ce -->

## Checklist obligatoriu

### Imagini (dacă ai adăugat/modificat imagini în `public/wp-content/uploads/`)
- [ ] Fișierele fizice sunt adăugate în `public/wp-content/uploads/<an>/<luna>/` sau `public/wp-content/uploads/catalog/`
- [ ] URL-ul a fost adăugat în `src/data/gallery.ts` cu formatul corect: `https://www.superparty.ro/wp-content/uploads/...`
- [ ] Versiunile WebP optimizate sunt adăugate în `public/optimized/` (rulează `node scripts/optimize-images.mjs` sau descarcă artifact din CI)
- [ ] CI `check-gallery-urls` trece (local file check)

### Cod
- [ ] Testare locală (`npm run dev` sau `npx astro build`)
- [ ] Nicio eroare TypeScript/Astro în consolă
- [ ] Funcționalitate verificată în browser (filtre galerie, slider, recenzii)

### Docs
- [ ] `CONTRIBUTING.md` respectat
- [ ] `CHANGELOG.md` actualizat dacă e o schimbare semnificativă

## Link preview Vercel (după push)

<!-- Vercel postează automat link-ul preview pe PR -->

## Screenshot / înregistrare (opțional pentru schimbări UI)

<!-- Adaugă screenshot dacă e relevant -->
