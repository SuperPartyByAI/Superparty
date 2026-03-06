# Runbook: CTR Drop

## Scope
CTR (click-through rate) scade semnificativ pe paginile money (pilon, hub-uri, sectoare) fără o scădere corespunzătoare de poziție.

## Trigger
- Alertă: CTR 7d scade cu >20% față de săptămâna anterioară pe oricare pagină Tier A
- Detectat manual în GSC: CTR < 3% pe pilon la avg_position < 3
- Raport săptămânal automat arată CTR trend negativ

## Severity: P1
**Investighezi în 24h. Nu blochezi agentul dacă rank-ul e stabil.**

---

## Immediate Safeguards

```bash
# Dacă scăderea e pe pilon și e bruscă (>30% în 7d):
SEO_PILLAR_LOCK=1   # protejezi pilon de experiments noi

# Dacă scăderea coincide cu un experiment activ:
SEO_FREEZE_EXPERIMENTS=1
```

---

## Diagnostic

```bash
# 1. Verifici últimele date GSC
python -c "
import json
from pathlib import Path
f = max(Path('reports/superparty/gsc').glob('collect_*.json'))
data = json.loads(f.read_text(encoding='utf-8'))
print('File:', f.name)
rows = data if isinstance(data, list) else data.get('rows', [])
rows.sort(key=lambda r: r.get('clicks', 0), reverse=True)
for row in rows[:10]:
    print(f'  CTR:{row.get(\"ctr\",0):.2%} | pos:{row.get(\"position\",0):.1f} | {row.get(\"keys\",[])}')
"

# 2. Verifici titlul și meta description pe paginile afectate
# CTR drop fără rank drop = titlu/snippet slab sau concurenta SERP îmbunătățită
grep -n "title\|description\|og:title" src/pages/animatori-petreceri-copii.astro | head -20

# 3. Verifici că nu există duplicate title/description pe alte pagini
python -c "
from pathlib import Path
import re
titles = {}
for f in Path('src/pages').rglob('*.astro'):
    text = f.read_text(encoding='utf-8', errors='ignore')
    m = re.search(r'<title[^>]*>([^<]+)</title>', text)
    if m:
        t = m.group(1).strip()
        titles.setdefault(t, []).append(str(f))
for t, files in titles.items():
    if len(files) > 1:
        print('DUPLICATE TITLE:', t, '->', files)
"

# 4. Verifici dacă experiment activ a schimbat titlul paginii
python -c "
import sqlite3
con = sqlite3.connect('reports/superparty/seo_experiments.db')
rows = con.execute(\"SELECT url_path, exp_type, variant_b_title, status FROM seo_experiments WHERE status IN ('RUNNING_B','WINNER') ORDER BY started_at DESC\").fetchall()
for r in rows: print(r)
"
```

**Cauze frecvente:**
- Titlu nedescriptiv sau prea generic după un apply/experiment
- Concurență nouă în SERP (alt site cu snippet mai bun)
- Sezonalitate (cererea scade natural)
- Sitelinks sau rich snippets disparute

---

## Decision Tree

```
CTR drop detectat
│
├── Rank-ul s-a schimbat și el?
│   ├── YES (rank drop + CTR drop) → Vezi runbook rank_drop.md
│   └── NO  (rank stabil, CTR scade) → Problema de snippet/titlu
│
├── A apărut după un experiment de tip title/description?
│   ├── YES → Verifici variant_b_title din DB
│   │          Dacă titlul e slab, rollback experiment
│   │          Restaurezi variant_a_title
│   └── NO  → Verifici pasul următor
│
├── Titlu sau description modificat recent de apply?
│   ├── YES → Verifici titlul curent vs cel original
│   │          git diff HEAD~5 src/pages/animatori-petreceri-copii.astro | grep title
│   │          Dacă e regresie, rollback manual
│   └── NO  → Verifici pasul următor
│
├── Sezonalitate?
│   ├── YES (ex. august, sărbători) → Monitorizezi pasiv,
│   │                                 nu schimbi titlurile sub presiune
│   └── NO  → Analizezi SERP manual (ce arată Google pe query)
│
└── Concurență nouă în SERP?
    └── YES → Îmbunătățești titlul: mai specific, mai orientat pe intent
               Testezi cu un experiment title nou (Variant B)
```

---

## Recovery

```bash
# Dacă ai identificat titlul slab — îl îmbunătățești manual:
# src/pages/animatori-petreceri-copii.astro → <title> și og:title

# Verifici că nu crești keyword stuffing
# Titlu bun: "Animatori Petreceri Copii București & Ilfov | SuperParty"

# Build și push
pnpm run build
git add src/pages/animatori-petreceri-copii.astro
git commit -m "fix(ctr): titlu îmbunătățit pilon după CTR drop"
git push origin HEAD
```

---

## Exit Criteria
- CTR 7d revine la nivelul anterior (±5%)
- Sau CTR se stabilizează și nu mai scade
- Titlul paginii verificat ca neduplicated
- Nu există experiment activ cu titlu slab

## Evidence
Salvezi: screenshot GSC CTR trend, titlul înainte și după, SHA fix, timestamp.

## Owner
Andrei Ursache — ursache.andrei1995@gmail.com
