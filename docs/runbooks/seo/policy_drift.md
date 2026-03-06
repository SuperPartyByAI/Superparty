# Runbook: Policy Drift

## Scope
Detectat când sitemap-ul, manifest-ul sau canonical-urile deviază de la policy:
- URL non-www în sitemap
- Slug non-target indexabil în manifest
- Noindex în sitemap
- Canonical fără www în paginile Astro

## Trigger
- Alertă automată: `seo_premerge_checks.py` exit 1
- Alertă manuală: URL non-www observat în GSC
- CI fail pe PR nou

## Severity: P0
**Blochează imediat orice merge/deploy până la rezolvare.**

---

## Immediate Safeguards

```bash
# 1. Oprești complet agentul
SEO_FREEZE=1  # în .env, restart orchestrator

# 2. Oprești apply real
SEO_FREEZE_APPLY=1

# 3. Verifici imediat policy
python scripts/seo_premerge_checks.py
```

---

## Diagnostic

```bash
# Verificare sitemap
grep -c "superparty.ro/" public/sitemap.xml      # trebuie 0
grep "superparty.ro/petreceri" public/sitemap.xml # trebuie 0 non-www

# Verificare manifest
python -c "
import json; from pathlib import Path
m = json.loads(Path('reports/seo/indexing_manifest.json').read_text(encoding='utf-8'))
for e in m:
    if e.get('indexable') and e.get('county','').lower() in {'teleorman','calarasi','giurgiu','ialomita'}:
        print('NON-TARGET:', e.get('slug'))
"

# Verificare sitemap complet
python scripts/seo_premerge_checks.py
```

**Fișiere de verificat:**
- `public/sitemap.xml`
- `reports/seo/indexing_manifest.json`
- `src/layouts/*.astro` (canonical tags)
- Ultimele commit-uri: `git log --oneline -10`

---

## Decision Tree

```
Policy drift detectat
├── Non-www în sitemap?
│   └── YES → Regenerezi sitemap: python tmp_regen_sitemap.py
│             Verifici ce script a produs sitemap-ul greșit
│             Commit + push fix
│
├── Slug non-target indexabil?
│   └── YES → Setezi indexable:false în manifest
│             Regenerezi sitemap
│             Adaugi slug în NON_TARGET_SLUGS din premerge_checks.py
│
├── Noindex în sitemap?
│   └── YES → Verifici mapping manifest → path
│             Fix în entry_to_path() din seo_premerge_checks.py
│
└── Canonical non-www în Astro?
    └── YES → Fix în layout-ul Astro afectat
              Verifici că SITE_URL începe cu https://www.
```

---

## Recovery

```bash
# 1. Fix-ul aplicat (sitemap / manifest / layout)
python scripts/seo_premerge_checks.py  # trebuie PASS

# 2. Build
pnpm run build  # trebuie EXIT 0

# 3. Commit + push
git add public/sitemap.xml reports/seo/indexing_manifest.json
git commit -m "fix(policy): corectare drift [non-www/noindex/non-target]"
git push origin HEAD

# 4. Dezgheți agentul
# Scoți SEO_FREEZE=1 din .env, restart orchestrator
```

---

## Exit Criteria
- `python scripts/seo_premerge_checks.py` → PREMERGE OK
- `pnpm run build` → exit 0
- Drift-ul nu mai apare în GSC după next crawl (24-48h)

## Evidence
Salvezi output-ul de la `seo_premerge_checks.py` + commit SHA + timestamp.

## Owner
Andrei Ursache — ursache.andrei1995@gmail.com
