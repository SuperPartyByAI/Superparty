# Runbook: Experiment Failure / Rollback Storm

## Scope
Un experiment CTR eșuează, produce rollback automat, sau mai multe experimente dau rollback simultan (rollback storm).

## Trigger
- Rollback automat detectat în DB: `status = REVERTED` sau `status = LOSER`
- Mai mult de 1 experiment cu rollback în aceeași zi
- Experiment evaluat pe volum insuficient (<800 impresii pe variant)
- Experiment blocat în `RUNNING_B` mai mult de 30 zile

## Severity: P1
**Investighezi în 24h. Rollback storm (>2 experimente) → P0.**

---

## Immediate Safeguards

```bash
# 1. Verifici câte experimente au dat rollback azi
python -c "
import sqlite3; from datetime import date
con = sqlite3.connect('reports/superparty/seo_experiments.db')
rows = con.execute('''
    SELECT url_path, exp_type, winner_variant, decision_reason, started_at, ends_at
    FROM seo_experiments
    WHERE status IN (\"REVERTED\",\"LOSER\")
    ORDER BY ends_at DESC LIMIT 10
''').fetchall()
for r in rows: print(r)
"

# 2. Dacă >2 rollback-uri:
SEO_FREEZE_EXPERIMENTS=1   # oprești toate experimentele noi
SEO_PILLAR_LOCK=1           # protejezi pilonul

# 3. Verifici ce URL-uri sunt afectate
python -c "
import sqlite3
con = sqlite3.connect('reports/superparty/seo_experiments.db')
rows = con.execute(\"SELECT url_path, status, winner_variant FROM seo_experiments WHERE status='RUNNING_A' OR status='RUNNING_B'\").fetchall()
print('ACTIVE experiments:')
for r in rows: print(' ', r)
"
```

---

## Diagnostic

```bash
# 1. Verifici detalii experiment eșuat
python -c "
import sqlite3
con = sqlite3.connect('reports/superparty/seo_experiments.db')
con.row_factory = sqlite3.Row
rows = con.execute('''
    SELECT * FROM seo_experiments
    WHERE status IN ('REVERTED','LOSER')
    ORDER BY ends_at DESC LIMIT 5
''').fetchall()
for r in rows:
    print('=== Experiment:', r['exp_id'])
    print('  URL:', r['url_path'])
    print('  Type:', r['exp_type'])
    print('  Decision:', r['decision_reason'])
    print('  Variant A start/end:', r['variant_a_start'], '->', r['variant_a_end'])
    print('  Variant B start/end:', r['variant_b_start'], '->', r['variant_b_end'])
    print('  Winner:', r['winner_variant'])
"

# 2. Verifici că baseline-ul a fost restaurat corect
# Dacă rollback a eșuat (pagina are conținut din Variant B):
git diff HEAD -- src/pages/<pagina-afectata>.astro

# 3. Verifici volumul de date (evaluat pe suficiente impresii?)
# Dacă variant_b_impressions < 800, evaluarea poate fi nesemnificativă statistic
```

**Cauze frecvente:**
- Variant B with titlu slab / conținut sub gate (< 2500 chars)
- Volum insuficient pentru evaluare statistică
- Experiment rulat pe pagină cu trafic scăzut
- Rollback corect — Variant A câștigă (comportament normal)
- Eroare de scriere a variantei în fișierul .astro

---

## Decision Tree

```
Rollback automat detectat
│
├── Rollback storm (>2 experimente azi)?
│   ├── YES → SEO_FREEZE_EXPERIMENTS=1 + SEO_PILLAR_LOCK=1
│   │          Verifici dacă e corelat cu un deploy/merge recent
│   │          Verifici că toate paginile au conținut baseline restaurat
│   └── NO  → Experiment izolat → vezi mai jos
│
├── Baseline restaurat corect pe pagina afectată?
│   ├── NO  → Restaurezi manual:
│   │          git show HEAD:src/pages/<pagina>.astro > src/pages/<pagina>.astro
│   │          git commit + push
│   └── YES → Experiment s-a comportat corect, Variant A câștigă
│
├── Experimentul a rulat pe volum suficient?
│   ├── NO (<800 impresii pe variant) → Evaluare nesemnificativă
│   │    Ajustezi SEO_EXPERIMENTS_MIN_VARIANT_IMPRESSIONS=800
│   │    Restarți cu mai mult timp de acumulare
│   └── YES → Evaluare validă, Variant B a pierdut
│
├── Variant B era pe pilon?
│   ├── YES → SEO_PILLAR_LOCK=1 (pilonul nu trebuie experimentat agresiv)
│   └── NO  → Analizezi ce a mers greșit pe Variant B și îmbunătățești
│
└── Decision_reason = "both_lost"?
    └── YES → Ambele variante au pierdut față de baseline
               Reviezi dacă baseline-ul este cu adevărat solid
               Considerezi că pagina nu e eligibilă pentru experiments acum
               Adaugi temporar în SEO_DENYLIST
```

---

## Recovery

```bash
# 1. Verifici că toate paginile cu rollback au conținut corect
for page in reports/superparty/seo_apply_gsc_*.json; do
    python -c "
import json
data = json.loads(open('$page').read())
for r in data.get('reverted',[]): print('REVERTED:', r.get('page'))
"
done

# 2. Verifici că DB-ul nu are experimente blocate
python -c "
import sqlite3
con = sqlite3.connect('reports/superparty/seo_experiments.db')
rows = con.execute(\"SELECT exp_id, url_path, status, started_at FROM seo_experiments WHERE status NOT IN ('WINNER','LOSER','REVERTED')\").fetchall()
print('Non-finished experiments:', len(rows))
for r in rows: print(' ', r)
"

# 3. Dezgheți experiments (dacă ai oprit)
# Scoți SEO_FREEZE_EXPERIMENTS=1 din .env
# restart orchestrator
```

---

## Exit Criteria
- Toate paginile afectate au conținut baseline corect
- DB-ul nu conține experimente blocate
- Nu apar rollback-uri noi 48h după rezolvare
- `SEO_FREEZE_EXPERIMENTS=0` (dacă a fost activat)

## Evidence
Salvezi: output DB experimente, SHA fix, paginile afectate, timestamp, decision_reason.

## Owner
Andrei Ursache — ursache.andrei1995@gmail.com
