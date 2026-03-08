# SEO Ops Dashboard — Runbook Operațional

## Ce este

`scripts/seo_ops_dashboard.py` este generatorul de dashboard operațional pentru **nivelurile L6 și L7** ale Agentului SEO Superparty. Produce `reports/superparty/ops_dashboard.html` — o pagină HTML statică care reflectă starea reală a pipeline-ului de colectare și procesare a datelor.

---

> **IMPORTANT:** Acesta NU este dashboardul vechi (`reports/seo/dashboard.html` / `scripts/seo_dashboard.py`).
> Dashboardul vechi era cuplat la experimente MAB și url_states L3/L4 și nu reflectă pipeline-ul L6/L7.
> Dashboardul vechi rămâne pe server nemodificat dar **nu este sursa de adevăr pentru L6/L7**.

---

## Cum generezi dashboardul

Se rulează pe instanța Hetzner (sau local cu datele din `reports/superparty/`):

```bash
python scripts/seo_ops_dashboard.py
```

Output: `reports/superparty/ops_dashboard.html`

Opțional, poți programa generarea automată printr-un cron job dacă este nevoie de refresh periodic.

---

## Ce surse citește (read-only, nu modifică nimic)

| Sursă | Conținut |
|---|---|
| `reports/superparty/gsc_collection_ledger.json` | Istoria rulărilor L7 (GSC Collector) |
| `reports/superparty/seo_report_worker_status.json` | Ultima stare L6 (worker status) |
| `reports/superparty/seo_reports_ledger.json` | Istoria rulărilor L6 (Report Worker) |
| `reports/superparty/seo_cluster_health.json` | Freshness Health Report |
| `reports/superparty/seo_cluster_priority.json` | Freshness Priority Report |
| `reports/superparty/seo_trend_delta.json` | Freshness Trend Report + flag baseline_only |
| `reports/superparty/gsc/collect_*.json` (cel mai recent) | Metadata ultimul snapshot brut GSC |

---

## Secțiunile dashboardului

**A. Source Acquisition (L7)** — A rulat Collectorul GSC? Câte rânduri a extras?
**B. Report Plane (L6)** — A procesat Health, Priority, Trend cu succes?
**C. Freshness** — Sunt rapoartele proaspete sau stale?
**D. Latest Raw Snapshot** — Ce date brute a adus ultima colectare?
**E. Trend / State Summary** — Sistemul are deja date istorice sau este încă în baseline?

---

## Ce înseamnă Verde / Galben / Roșu

### 🟢 VERDE — System Operational
Toate condițiile sunt îndeplinite:
- L7 Ledger: `SUCCESS`
- L6 Overall Status: `success`
- Freshness (`health`, `priority`, `trends`): `ready`
- Artefactele principale există și nu sunt stale

### 🟡 GALBEN — Atenție
Una sau mai multe condiții sunt la limită:
- `partial_failure` în ultimele 3 rulări L6
- Freshness la `warning` (>75% din pragul maxim)
- Status L7/L6 neașteptat (ex. `unknown`, `skipped`)
- `baseline_only` activ mult timp

### 🔴 ROȘU — Incident Activ
Condiție critică confirmată:
- L7 FAILED (última rulare)
- L6 `overall_status: failed`
- Readiness blocat — artefact lips sau stale
- Status file `seo_report_worker_status.json` lipsă sau corupt

---

## Ce NU trebuie confundat

| Confuzie frecventă | Realitate |
|---|---|
| "Dashboardul arată verde deci SEO merge bine" | VERDE = robotul funcționează tehnic. Impactul SEO se vede **numai în GSC**. |
| "Dashboardul vechi nu mai funcționează" | Dashboardul vechi (`reports/seo/`) este legacy și nu a fost conectat la L6/L7 niciodată. |
| "Row count 0 = eroare" | Google poate returna legal zero rânduri în ferestre fără date. Verifică `failing_stage`. |

---

## Cum se folosește în auditul zilnic

1. Rulează comanda de generare: `python scripts/seo_ops_dashboard.py`
2. Deschide `reports/superparty/ops_dashboard.html` în browser
3. Verifică verdictul global (Verde/Galben/Roșu)
4. Dacă GALBEN sau ROȘU → urmează SOP-ul de escaladare din `docs/runbooks/seo/agent_operations_sop.md`

---

## Teste

```bash
python -m pytest tests/test_seo_ops_dashboard.py -v
```

Acoperire: verdict logic, freshness, _read_json resilience, collect_l7, render_html.
