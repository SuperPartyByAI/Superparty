# Contributing — SuperParty

## Instalare hook-uri locale (o singură dată)

```bash
git config core.hooksPath .githooks
# Verificare: adaugă o imagine mare → pre-commit va fi avertizat
```

## Exemplu complet: adaugă o imagine nouă în galerie

```bash
# 1. Copiază imaginea în folder-ul corect
cp ~/Downloads/animatoare-noi.jpg public/wp-content/uploads/2026/03/

# 2. Generează versiunile WebP optimizate
npm install sharp --no-save   # o singură dată
node scripts/optimize-images.mjs
# → generează public/optimized/thumb/2026/03/animatoare-noi.webp
# → generează public/optimized/hero/2026/03/animatoare-noi.webp

# 3. Adaugă URL în gallery.ts
# Editează src/data/gallery.ts → adaugă în galleryAll:
# { url: 'https://www.superparty.ro/wp-content/uploads/2026/03/animatoare-noi.jpg', alt: '...', category: 'animatori' }

# 4. Commit tot
git add public/wp-content/uploads/2026/03/animatoare-noi.jpg \
        public/optimized/thumb/2026/03/animatoare-noi.webp \
        public/optimized/hero/2026/03/animatoare-noi.webp \
        src/data/gallery.ts
git commit -m "feat(gallery): imagine nouă animatoare 2026-03"

# 5. Push → CI verifică local că fișierele există
git push origin feat/imagine-noua
# Deschide PR → checklist apare automat → CI rulează
```

## Adaugă imagini în galerie (checklist obligatoriu)

Dacă adaugi sau modifici URL-uri în `src/data/gallery.ts`:

1. **Adaugă fișierul fizic** în `public/wp-content/uploads/...` în **același commit/PR**.
2. **Verifică local** înainte de push:
   ```bash
   # Verifică că toate URL-urile din gallery.ts au fișier corespunzător în public/
   grep -oE "/wp-content/uploads/[^'\",\` )>]+" src/data/gallery.ts | while read p; do
     [ -f "public$p" ] && echo "OK $p" || echo "MISSING public$p"
   done
   ```
3. **Format URL obligatoriu** în `gallery.ts`:
   ```
   https://www.superparty.ro/wp-content/uploads/<an>/<luna>/<fisier.ext>
   ```
4. **CI blochează PR-ul** dacă vreun fișier lipsește din `public/`. Nu e un warning — e un fail hard.
5. **Imagini mari** (>2MB): deschide issue înainte, ca să fie negociat impactul asupra build-ului.

## Imagini optimizate (opțional dar recomandat)

Dacă lucrezi cu imagini noi și vrei să generezi versiuni WebP optimizate:

```bash
npm install sharp --no-save
node scripts/optimize-images.mjs
# Rezultat: public/_optimized/thumb/<fisier>.webp + hero/<fisier>.webp
```

## Pull Request

- Titlu clar: `fix(gallery): ...` / `feat(ui): ...` / `ops(health): ...`
- Descriere: ce schimbi + de ce + ce ai testat
- CI trebuie să fie verde înainte de merge

## Structură fișiere relevante

| Fișier | Rol |
|---|---|
| `src/data/gallery.ts` | Sursă de adevăr pentru URL-uri imagini galerie + slider |
| `public/wp-content/uploads/` | Fișiere statice servite de Vercel |
| `public/wp-content/uploads/catalog/` | Costume personaje (105 PNG) |
| `scripts/optimize-images.mjs` | Generează versiuni WebP optimizate |
| `scripts/health_check.sh` | Health check server Hetzner |
| `.github/workflows/check-gallery-urls.yml` | CI: verifică fișiere locale + spot-check live |
