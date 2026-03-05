# Contributing — SuperParty

Mulțumim că contribui! Urmează ghidul de mai jos.

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
