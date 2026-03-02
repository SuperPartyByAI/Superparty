# ⛔ DO NOT USE — Deprecated Scripts

These scripts were used to **build** the initial 1498 testimonials database during the SEO overhaul (batches 1-10, March 2026). 

**They must NOT be re-run** because:
- They add synthetic/AI-generated testimonials from raw text
- Running them again would create duplicates or overwrite real testimonials  
- The `src/data/superparty_testimonials.json` file is now the source of truth

## What these scripts did
- `add_testimonials.py` through `add_testimonials_batch10.py` → parsed raw text and populated superparty_testimonials.json
- `rewrite_500_mdx.py` → rewrote MDX body content (already run, files finalized)
- `audit_and_fix_ready.py`, `fix_placeholders.py`, `fix_titles_and_brand.py` → one-time fixes (applied)

## If you need to ADD NEW testimonials
Only add to `src/data/superparty_testimonials.json` manually or via a dedicated SAFE script that:
1. Validates `siteId: "superparty"`
2. Validates slug exists in `src/content/seo-articles/`
3. Does NOT overwrite existing entries

## Guardrails
The CI workflow `.github/workflows/superparty-guardrails.yml` enforces `siteId=superparty` only.
