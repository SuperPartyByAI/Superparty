# Runbook: Rank Drop

## Scope
Pilonul (`/animatori-petreceri-copii`) sau hub-urile principale (București/Ilfov) ies din top 3 pe query-urile money.

## Trigger
- Alertă: avg_position > 3.5 pe query „animatori petreceri copii" (7d)
- Alertă: poziție medie crește cu >1.5 față de săptămâna anterioară pe pilon
- Detectat manual în GSC sau dashboard ops

## Severity: P0
**Acțiune imediată. Nu lași să treacă o zi fără investigație.**

---

## Immediate Safeguards

```bash
# 1. Blochezi experiments pe pilon imediat
SEO_PILLAR_LOCK=1   # în .env, restart orchestrator

# 2. Dacă scăderea e bruscă (>3 poziții într-o săptămână):
SEO_FREEZE_EXPERIMENTS=1   # oprești tot experiment engine

# 3. Verifici că agentul nu a aplicat ceva greșit pe pilon
cat reports/superparty/seo_apply_gsc_*.json | python -c "
import json,sys
for line in sys.stdin:
    try:
        d=json.loads(line)
        for a in d.get('applied',[]):
            if 'animatori' in a.get('page',''):
                print('APPLIED ON PILON:', a)
    except: pass
"
```

---

## Diagnostic

```bash
# 1. Verifici că sitemap-ul și canonical sunt OK
python scripts/seo_premerge_checks.py

# 2. Verifici ultimele apply-uri pe pilon
ls -la reports/superparty/seo_apply_gsc_*.json

# 3. Verifici că nu există experiment activ pe pilon (risc overlay)
python -c "
import sqlite3
con = sqlite3.connect('reports/superparty/seo_experiments.db')
rows = con.execute(\"SELECT * FROM seo_experiments WHERE url_path LIKE '%animatori%' ORDER BY started_at DESC LIMIT 5\").fetchall()
for r in rows: print(r)
"

# 4. Verifici conținutul actual al paginii pilon
head -c 2000 src/pages/animatori-petreceri-copii.astro

# 5. Verifici că pilonul are link-urile interne corecte
python -c "
from pathlib import Path
text = Path('src/pages/animatori-petreceri-copii.astro').read_text(encoding='utf-8')
for link in ['/arie-acoperire', '/petreceri/bucuresti', '/petreceri/ilfov']:
    print(link, ':', link in text)
"
```

**Cauze frecvente:**
- Experiment activ care a degradat conținutul pilonului
- Apply real care a înlocuit conținut bun cu conținut prost
- Drift canonical (www vs non-www)
- Concurență neașteptată de pe alt URL al site-ului (cannibalization)

---

## Decision Tree

```
Rank drop pe pilon
│
├── A apărut după un apply real pe pilon?
│   ├── YES → Rollback manual: restaurezi fișierul din git
│   │          git checkout HEAD~1 -- src/pages/animatori-petreceri-copii.astro
│   │          git commit -m "fix: rollback pilon după rank drop"
│   │          git push + deploy
│   └── NO  → Verifici pasul următor
│
├── Există experiment activ pe pilon?
│   ├── YES → SEO_PILLAR_LOCK=1
│   │          Rollback experiment: setezi winner_variant=BASELINE în DB
│   │          Restaurezi conținutul baseline
│   └── NO  → Verifici pasul următor
│
├── Canonical sau sitemap drift?
│   ├── YES → Fix policy drift (vezi policy_drift.md)
│   └── NO  → Verifici pasul următor
│
├── Concurență internă (alt URL pe același query)?
│   ├── YES → Adaugi URL concurent în SEO_DENYLIST
│   │          Verifici query map (docs/runbooks/seo/README.md)
│   └── NO  → Verifici pasul următor
│
└── Scădere naturală (Google update)?
    └── YES → Menții SEO_PILLAR_LOCK=1
               Lași apply real activ (conținut)
               Monitorizezi 7-14 zile
               Nu schimbi structura URL sau titlurile
```

---

## Recovery

```bash
# Verifici că pilonul arată bine
python scripts/seo_premerge_checks.py   # PASS obligatoriu

# Confirmi conținut corect (>2500 chars, 4+ FAQ, 3 links interne)
python -c "
import re
text = open('src/pages/animatori-petreceri-copii.astro',encoding='utf-8').read()
clean = re.sub(r'<[^>]+>', '', text)
print('CHARS:', len(clean.strip()))
print('FAQ items:', text.count('faq-item'))
for link in ['/arie-acoperire', '/petreceri/bucuresti', '/petreceri/ilfov']:
    print(link, ':', link in text)
"

# Build OK
pnpm run build
```

---

## Exit Criteria
- Pilonul revine în top 3 pe query principal (7d rolling average)
- `seo_premerge_checks.py` → PASS
- Nu există experiment activ pe pilon (`SEO_PILLAR_LOCK=1` rămâne până la stabilizare)
- Pilon conținut verificat: >2500 chars, 4+ FAQ, 3 links interne

## Evidence
Salvezi: screenshot GSC, output seo_premerge_checks.py, SHA commit fix, timestamp.

## Owner
Andrei Ursache — ursache.andrei1995@gmail.com
