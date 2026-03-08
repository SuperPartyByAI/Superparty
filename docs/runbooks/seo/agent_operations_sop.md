# Superparty Agent SEO - Standard Operating Procedure (SOP)

Acest document standardizează modul în care performanța și calitatea Agentului SEO autonom trebuie verificată pentru a garanta atât funcționarea tehnică, cât și un outcome SEO real, pe arhitectura Level 3 - Level 7.

## 1. Scop
Standardizarea procesului de audit tehnic și SEO al Agentului Superparty. Acest SOP asigură că operatorul poate face diferența clară între o *rulare mecanică a codului* și generarea de *valoare SEO demonstrabilă*.

## 2. Domeniu de aplicare
Sistemul acoperă întregul lanț funcțional curent:
- **Level 7 (Source Acquisition):** Colectarea rapoartelor brute (GSC Worker).
- **Level 6 (Report Plane):** Ingurgitarea și clasificarea datelor (Health, Priority, Trend).
- **Nu conține:** Instrucțiuni de execuție autonomă (Level 8) sau Apply Plane direct (momentan închise/hands-off).

## 3. Arhitectura pe scurt / Straturi de Bază
Orice audit trebuie despărțit în cele **4 straturi fundamentale**:
1. **Execuție tehnică:** A rulat sau a picat?
2. **Calitatea datelor:** A tras date bune sau gunoi?
3. **Calitatea inteligenței:** Ce rapoarte și decizii produce?
4. **Rezultatul SEO real:** Se vede ceva în Google Serps sau nu?

---

## I. STRATUL 1 — HEALTH OPERAȚIONAL
Răspunde la: *"A rulat corect, complet și fără avarii?"*

Verificarea demonstrează stabilitatea software-ului pe server. Datele sunt izolate în fișiere și rapoarte de status (`ledgers`).

### Comenzi Exacte de Control (Executate pe Serverul Hetzner):
Se vor rula pe partiția `/srv/superparty/` prin instanța centrală.

```bash
# Verifică dacă L7 a tras date reale din GSC sau a picat
python agent/tasks/seo_level7_gsc_ledger.py --summary

# Verifică dacă L6 a procesat cu succes health / priority / trend
python agent/tasks/seo_level6_report_ledger.py --summary

# Verifică dacă rapoartele sunt proaspete și valide
python agent/tasks/seo_level6_report_readiness.py

# Verifică existența mecanică a snapshotului brut L7 din GSC
ls -la /srv/superparty/reports/superparty/gsc/collect_*.json | tail

# Verifică ultimul status scurt al workerului L6
cat /srv/superparty/reports/superparty/seo_report_worker_status.json
```

---

## II. STRATUL 2 — CALITATEA DATELOR
Răspunde la: *"Datele pe care le procesează robotul sunt reale, coerente și utile?"*

Nu e suficient ca L7 să deschidă un fisier `.json`. Conținutul lui se validează manual:
1. **Verificare snapshot brut (`collect_*.json`)**:
   - `metadata.schema_version` trebuie să fie `1.0`.
   - `metadata.source` trebuie să fie `google_search_console`.
   - `metadata.property` trebuie să fie exact `sc-domain:superparty.ro`.
   - `metadata.row_count` trebuie să conțină numărul real de rânduri GSC (dacă rândurile sunt absente constant, apare suspiciunea de drop API).

2. **Verificare L6 Consume**:
   - Health / Priority / Trend Report trebuie generate direct din snapshotul *nou*. Folosirea de snapshoturi *stale/vechi* indică problemă de Freshness Gate.

---

## III. STRATUL 3 — CALITATEA INTELIGENȚEI
Răspunde la: *"Produce output bun, credibil și folositor?"*

1. **Health Report:** Verificare distribuire clustere, money vs non-money (Canibalizează? Există suprapuneri ilogice de ownership pe pagini suport?).
2. **Priority Report:** Confirmare oportunități și aliniere rezonabilă cu Triage. Erorile L3 Astro trebuie prioritizate natural.
3. **Trend Report:** Identificare schimbări (îmbunătățiri sau regresii clare). La lansare va raporta `baseline_only=True`, ulterior va extrage diferențele matematice stricte.
**Crucial:** *Explainability* (există un motiv logic pentru concluzie?) și *Stability* (aceleași surse duc la aceleași decizii pe rulări succesive).

---

## IV. STRATUL 4 — REZULTATUL SEO REAL
Răspunde la: *"După ce sistemul produce date și decizii, se vede ceva real în Google?"*

Atenție: GSC are întotdeauna **latență de 3-4 zile**. Nu confunda "Merge tehnic" (Stratul 1) cu "Produce valoare SEO" (Stratul 4). Analiza pe outcome a Agentului implică verificarea directă a UI-ului Google Search Console. 

**Formularea Verdictului (Fără "Pare ok"):**
- `positive signal detected`
- `weak signal only`
- `no signal yet`
- `technical blockage detected`
- `insufficient data window`

1. **Performance Overview:** Clicks, impressions, CTR, average position (Before vs After launch date pe 8 Martie 2026).
2. **Query Audit:** animatori petreceri copii, animatori copii bucurești, the long-tail geo targets.
3. **Page Audit:** Câștigă URL-ul corect query-ul dorit?
4. **Cannibalization:** Există două pagini care „se luptă” pe un query unde agentul a editat Meta Tags?
5. **Indexing / Coverage:** Noua arhitectură nu cauzează `Discovered - currently not indexed` sau `Soft 404` la refreshul UI-ului. (Notă: Verificare mereu prin API URL Inspection/UI direct pe URL-urile suspecte).

---

## 8. Praguri de Escaladare (Verde, Galben, Roșu)

### Starea VERDE 🟢
- Totul pe ledgere este `SUCCESS`.
- Readiness indică status = `ready`.
- Apar snapshoturi noi L7 fără contract fail.
- Fără erori (pe paginile canonice) în GSC Excluded.

### Starea GALBEN 🟡
- Apariția de `partial_failure` în L6 (salvat dar fără scor ideal).
- `row_count` anormal de mic în L7.
- Trendul stă pe `baseline_only` inexplicabil de mult (mai mult de 2 cicliuri GSC).
- Snapshot nou dar suspect calitativ.

### Starea ROȘU 🔴
- L7 / L6 indică `FAILED` ca ultim status în Ledger.
- Snapshot lipsă sau Readiness blocat complet (`not_ready`).
- Un URL Astro Canonic *curent* apare raportat cu erori 4xx/Excluded în GSC.
- GSC arată un URL greșit care canibalizează direct query-ul strategic în mod activ.

---

## 9. Cadrul de Control și Checklist-uri

### ✅ Ritual Zilnic de Ops (Axa Health - 2 minute)
- [ ] Ledger L7 = `SUCCESS`
- [ ] Ledger L6 = `SUCCESS`
- [ ] Readiness = `ready`
- [ ] `seo_report_worker_status.json` = All Fresh & Success

### ✅ Ritual Săptămânal de Intelligence (Axa Qualitate - 15 min)
- [ ] Comparare Health Report (existența patternurilor anormale).
- [ ] Verificare Trend Report (se observă diferențe semantice).
- [ ] Evaluare `row_count` (evoluția volumului de date GSC agregate).

### ✅ Ritual Bilunar / Lunar SEO Reality Check (Axa GSC Outcome - 30 min)
- [ ] Query Audit pe targeturile strategice.
- [ ] Page rank distribution.
- [ ] Indexing & Cannibalization (Nu apar pagini noi în Excluded).

---

## 10. Checklist de Stabilizare Operațională Strictă
*Precondiție obligatorie pentru trecerea la Level 8 (Decision Intelligence Planes).*
- [ ] 3 rulări Cron reale.
- [ ] Pe 3 zile calendaristice distincte.
- [ ] **Fără nicio formă de intervenție manuală sau scriere de cod**.
- [ ] L7 status pe SUCCESS (fără fail API_FETCH).
- [ ] L6 status FĂRĂ `partial_failure` neexplicat.
- [ ] Readiness mereu `ready`.
- [ ] Ledgere curate, coerente, persistând liniar.

---

## 11. Ce NU trebuie confundat niciodată
- Nu confunda **"am rulat codul cu exit 0"** cu **"agentul a produs outcome SEO cert"**. 
- Nu confunda **"A existat 1 pagină neindexată URL vechi de la WordPress"** cu **"Eroare tehnică activă de producție pe noua arhitectură"**.
- Momentan se măsoară *stabilitatea inteligenței*. Write Plane-urile Agentului (L8/L5 Auto-Apply) sunt oprite, lăsând strict L6 și L7 să raporteze.
