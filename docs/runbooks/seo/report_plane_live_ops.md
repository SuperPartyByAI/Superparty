# Report Plane Live Operations (Level 6.5)

Acest document este manualul de supraviețuire și exploatare operațională a Report Plane-ului (Hetzner Scheduled Worker) pentru nivelul L6 enterprise. Fără aceste instrucțiuni asertive, deciziile sistemelor inferioare de write pot denatura.

## 1. Monitorizare & Audit Status

### Cum verifici statusul imediat (JSON Status)
Worker-ul exportă starea la finalul rulajului în `reports/superparty/seo_report_worker_status.json`. Acest artefact mașină-citibil arată punctual eșecul:
```json
{
  "health": "success",
  "priority": "success",
  "trend": "success",
  "overall_status": "success",
  "ledger_status": "success",
  "run_at": "2026-03-08T00:00:00Z"
}
```

### Cum citești istoricul operațional (Run Ledger)
Zilnic este append-uit max 30-zile un status ledger pentru observabilitate liniară:
```bash
# Citește din terminal stadiul live (Fresh vs. Failed) pe ultimele acționări
python agent/tasks/seo_level6_report_ledger.py --summary
```
Output-ul îți va arăta direct: `[2026-03-08 03:00:00] Status: SUCCESS | Health: Fresh | Priorities: Fresh | Trends: Fresh`.

---

## 2. Triajul de Erori pe `overall_status` (Fail-Closed)

Orice status non-`success` din worker semnalizează o decuplare a sistemului L6 de sursa sa de input, ocrotind platformele de execuție L5.

### Scenariul 1: `health failed`
**Efect**: Worker-ul dă "abort" procesului de Priority (`skipped`), dar **Trend Analyzer va rula în continuare independent** (poate fi `success` sau `failed`). Cu toate acestea, `overall_status` va fi forțat la `failed`.
**Motiv**:
- GSC (Google Search Console) nu are un fișier raw actualizat în `reports/superparty/gsc/collect_*.json` (ex: limită de quota).
- Schema JSON (1.0) pentru engine este spartă (nu contine `clusters`).
**Acțiune**: 
- Verifică sursa GSC pentru Health. Procesul dependent (Priority) s-a oprit pentru a nu calcula decizii pe volum ne-actualizat, însă scripturile independente (cum ar fi Trends) au mers mai departe. Poți reporni master-ul după remedierea GSC (Readiness Gate va impune `stale report` lock la ~48h pe restul output-urilor).

### Scenariul 2: `priority failed`
**Efect**: Health e valid, dar prioritatea crapă. Status: `partial_failure`.
**Motiv**:
- Registry-ul `query_ownership_registry.json` conține chei corupte.
- Schema validării impuse pe Atomic Deploy per priority nu coincide ("2.0").
**Acțiune**: Rulează independent `python agent/tasks/seo_level4_priority.py` pentru a detecta de ce crapă logica matrix-ului de business.

### Scenariul 3: `trend failed`
**Efect**: Status `partial_failure`. Celelalte documente SEO se află live pe disk.
**Motiv**:
- Raportul vechi `snapshots` nu reușește să fie arhivat corect.
- Contract version match fail pe "1.1".
**Acțiune**: Rulează trend_analyzer manual și verifică console log-ul cu `pytest tests/test_seo_level4_trend_analyzer.py`.

### Scenariul 4: `ledger_status: failed`
**Efect**: Rapoartele de sistem s-au generat cu succes și sunt online. Nu e problemă SEO, **este o problemă de Audit Trail**. 
**Motiv**: 
- Ledgerul global e blocat la scriere pe server (Permission Denied).
- Fișierul e iremediabil corupt, iar `corrupt.bak`-ul n-a putut fis scris de script.
**Acțiune**: Du-te în `reports/superparty/seo_reports_ledger.json` și curăță buffer-ul distructiv.

---

## 3. Checklist de Validare Live (Cum Execuți primul Deploy Hetzner)

Primul trigger direct va proba pipeline-ului la roșu în terminalul VPS:

- [ ] 1. **Execută manual** o rulare completă: `python scripts/hetzner_daily_report_worker.py`.
- [ ] 2. Verifică generarea pe orologia curentă a `reports/superparty/seo_cluster_health.json`. Asigură-te că pe `metadata` ai regimul izolat `source_gsc_file`.
- [ ] 3. Cheamă Gate-ul L6.1: `python agent/tasks/seo_level6_report_readiness.py` din orice alt job (mock dry-run) pentru a proba că citește `generated_at` din schema nouă și ridică un steag Verde.
- [ ] 4. Verifică din consolă Ledgere-ul folosind parametrul `--summary` pentru a confirma validitatea înregistrării rotative.
- [ ] 5. Confirmă funcționarea corectă a `.bak`-ului în cazul corupției (opțional - strică un `seo_reports_ledger.json` intenționat și vezi preluarea imediată a unei file nolă).
- [ ] 6. Aliniază cron-ul (`crontab -e`) ca ora să pice pe 03:00 UTC conform runbook-ului anex L6.2.
