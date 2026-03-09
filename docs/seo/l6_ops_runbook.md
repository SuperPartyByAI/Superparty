# L6 Ops Runbook — SuperParty SEO Agent

## Scopul acestui runbook

Proceduri operaționale pentru faza de observație Run 1 și decizia Run 2 în sistemul L6 Learning Loop.

---

## 1. Cum importi exportul GSC

### Export din GSC

1. Deschide [Google Search Console](https://search.google.com/search-console) → superparty.ro
2. **Performance > Pagini** → filtru dată: ultimele 28 zile (sau de la data Run 1: 9 martie)
3. **Export** → CSV sau JSON
4. Salvează local ca `gsc_export_YYYY-MM-DD.csv` (sau `.json`)

### Ingestie în pipeline

```bash
# Cu export CSV
python -c "
from pathlib import Path
from agent.tasks.seo_level6_gsc_ingestion import run_gsc_ingestion
report = run_gsc_ingestion(
    export_file=Path('gsc_export_2026-03-16.csv'),
    outcome_memory_path=Path('reports/superparty/seo_level6_outcome_memory.json'),
    mode='after',  # sau 'before' daca e baseline dinainte de apply
    output_report_path=Path('reports/superparty/seo_level6_gsc_ingestion_report.json'),
)
print(report)
"
```

### Verificare post-ingestie

```bash
python scripts/seo/l6_generate_readiness.py
```

Dacă URL-urile din Run 1 apar acum cu `impressions >= 80`, câmpul `run2_allowed` va reflecta statut actualizat.

---

## 2. Cum generezi Run Readiness Report

```bash
python scripts/seo/l6_generate_readiness.py
```

Output: `reports/superparty/seo_level6_run_readiness.json`

### Cum interpretezi `run2_allowed`

| Valoare | Semnificație |
|---|---|
| `true` | Run 2 PERMIS. Selectează candidații din planner și execută. |
| `false` | Run 2 BLOCAT. Vezi `blocked_reasons`. |

### `blocked_reasons` posibile

| Motiv | Ce înseamnă | Ce faci |
|---|---|---|
| `all_experiments_insufficient_data` | Niciun URL nu are date GSC suficiente | Aștepți sau injectezi export GSC |
| `cooldown_not_lifted` | URL-urile din Run 1 sunt în cooldown | Aștepți 7 zile de la apply (după 16 martie) |
| `no_url_above_min_impressions` | Niciun URL nu a atins 80 impresii post-apply | Aștepți re-crawl Google |
| `observation_window_not_closed_for_all` | Fereastra de 14 zile nu s-a încheiat | Aștepți 23 martie |
| `active_rollback_conflict` | Există rollback activ | Verifici manual cauza și resetezi |

---

## 3. Cum citești Run 2 Candidate Planner

```bash
# Dupa generare readiness (include si planner-ul)
cat reports/superparty/seo_level6_run2_candidates.json
```

### Schema per candidat

```json
{
  "url": "/petreceri/otopeni",
  "tier": "C",
  "suggested_strategy": "local_intent",
  "selection_reason": "...",
  "data_quality": "insufficient | limited | good",
  "eligible_now": true,
  "blocked_reasons": [],
  "earliest_possible_run_date": "2026-03-16"
}
```

| `data_quality` | Semnificație |
|---|---|
| `good` | ≥ 80 impresii post-apply — verdict SEO posibil |
| `limited` | < 80 impresii — scoarterul va returna `insufficient_data` |
| `insufficient` | Nicio dată GSC — nu putem judeca impactul |

---

## 4. Ce faci pe 16 martie 2026

**Checklist 16 martie:**

```
□ 1. Exportezi GSC Performance > Pagini (date 9 mart – 16 mart)
□ 2. python scripts/seo/l6_generate_readiness.py
□ 3. Verifici dacă vreun URL din Run 1 are impressions >= 80
□ 4. Dacă DA: run_gsc_ingestion cu modul 'after' → scorer re-evaluează
□ 5. Dacă NU: "wait for data" — cooldown-ul s-a ridicat dar datele lipsesc
□ 6. Dacă run2_allowed = true: execuți Run 2 cu candidații eligibili acum
□ 7. Dacă run2_allowed = false: notezi motivul și programezi check 23 martie
```

---

## 5. Ce faci pe 23 martie 2026

**Checklist 23 martie:**

```
□ 1. Exportezi GSC Performance > Pagini (date 9 mart – 23 mart, 14 zile)
□ 2. python scripts/seo/l6_generate_readiness.py
□ 3. Injectezi export GSC cu modul 'after' pentru toate 3 URL-uri Run 1
□ 4. Verifici fiecare URL: impressions, CTR, position
□ 5. Scorerul rulează automat pe experimentele expirate -> verdict per URL
□ 6. Citești raportul comparativ:
     - improved: strategia merită Run 2
     - neutral: strategia e OK dar nu spectaculoasă
     - worse / strong_negative: evită strategia în Run 2
     - insufficient_data: fereastra e prea scurtă — prelungești observația
□ 7. Decizi Run 2 pe baza datelor reale:
     - cel puțin 1 URL non-insufficient_data → Run 2 permis
     - toate insufficient_data → Run 2 amânat, prelungești fereastra
```

---

## 6. Reguli Run 2 (documentate)

```
Run 2 PERMIS dacă:
  ✅ min_observation_days >= 7 (cooldown minim ridicat)
  ✅ cel puțin 1 URL cu impressions >= 80
  ✅ cel puțin 1 verdict din Run 1 ≠ insufficient_data
  ✅ zero rollback active
  ✅ fereastra de observație Run 1 ≥ 7 zile elapsed

Run 2 INTERZIS dacă orice din:
  ⛔ toate URL-urile Run 1 au insufficient_data
  ⛔ cooldown activ pe URL-uri Run 1
  ⛔ rollback activ
  ⛔ Threshold-ul minim de 80 impresii neîndeplinit pe niciun URL
```

---

## 7. Fișiere și locații

| Fișier | Descriere |
|---|---|
| `reports/superparty/seo_level6_run_readiness.json` | Readiness report curent |
| `reports/superparty/seo_level6_run2_candidates.json` | Shortlist candidați Run 2 |
| `reports/superparty/seo_level6_outcome_memory.json` | Outcome memory (pending/closed) |
| `reports/superparty/seo_level6_gsc_ingestion_report.json` | Raport ultima ingestie GSC |
| `reports/superparty/seo_level6_status.json` | Status snapshot L6 |
| `agent/tasks/seo_level6_gsc_ingestion.py` | GSC ingestion tool |
| `agent/tasks/seo_level6_run_readiness.py` | Readiness report generator |
| `agent/tasks/seo_level6_run2_planner.py` | Run 2 candidate planner |
| `scripts/seo/l6_generate_readiness.py` | CLI runner (rulat zilnic) |
