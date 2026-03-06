# Level 4 Cluster Health — Triage & Response Runbook

## 1. Scop

Acest runbook definește răspunsul operațional standardizat (Human-in-the-loop) la alertele generate de **Level 4 Advisory Engine (Cluster Health)** din Ops Dashboard. 

**IMPORTANT**: 
* Sistemul Level 4 este momentan **READ-ONLY (Advisory)**. 
* Acest strat **NU** modifică `seo_apply_task.py`, **NU** alterează `seo_control.py`, **NU** blochează automat experimente și **NU** declară victorii de business (locul 1) în mod autonom. 
* Obiectivul său este aducerea derivei de arhitectură la suprafață. Răspunsul este exclusiv administrativ/uman, urmând procedurile de mai jos.

---

## 2. Semnale Observabile în Dashboard (ops.superparty.ro/seo/cluster-health)

Datele brute despre sănătatea clusterelor sunt relevate sub forma unor KPI-uri de stare și liste agregate de Warnings. Operatorul trebuie să urmărească activ:

- `owner_present = false`: Clusterul nu obține impresii pe URL-ul Pilon decretat.
- `forbidden_count > 0`: Pagini aflate în blacklist-ul clusterului respectiv captează organic trafic pe query-urile sale.
- `unknown_count > 0`: Pagini neasociate/neaprobate captează impresii destinate acestui cluster.
- **Money cluster cu warnings**: Risc comercial direct de canibalizare pe Tier A sau B.
- **Warnings severity = HIGH**: Instanțe unde URL-ul deviant este strict `forbidden` în Registry.
- **Warnings severity = MEDIUM**: Instanțe unde URL-ul deviant este `unknown` (sandbox).

---

## 3. Matrice de Severitate (Severity Matrix)

Pentru standardizarea reacției, evaluăm alertele pe 4 niveluri:

### [S0] — Informational (Zgomot Neutru / Sănătos)
- Clusterul nu are niciun warning de canibalizare.
- Owner-ul captează trafic stabil.
- Supporterii autorizați captează trafic rezidual inofensiv.
- *Status:* **Doar monitorizare.**

### [S1] — Low Risk (Derivă Minora)
- Apariția unui conflict `unknown` pe un cluster non-money (ex: rută de suport / blog).
- Fluctuații lejere fără impact direct pe un Owner critic de Tier A sau Tier B.
- *Status:* **Review în sesiunea curentă de mentenanță.**

### [S2] — Medium Risk (Problemă de Arhitectură / Indexare)
- Conflict `unknown` activ pe un **Money Cluster** (Tier A/B).
- `owner_present = false` pe un Money cluster aflat anterior pe radar.
- Drift local/învecinat: Un URL hub sau de sector (ex. `/petreceri/sector-2`) canibalizează fragmente de pe alt hub (ex. `/petreceri/sector-3`).
- *Status:* **Intervenție necesară la finalul analizei săptămânale / Prioritizare de patching SEO.**

### [S3] — High Risk (Canibalizare Critică)
- Conflict alertat cu **`forbidden`** pe un Money Root sau Geo Tier A (ex. pagina principală `/animatori-petreceri-copii`).
- Suprapunere directă a zonelor majore (ex. `/petreceri/bucuresti` fură intenția critică a `/petreceri/ilfov`).
- O pagină locală minoră sau de suport preia masiv click-uri din clusterul Pilon (Trafic comercial prădat).
- *Status:* **Escaladare imediată. Stopare alterări SEO automate pe clusterul afectat.**

---

## 4. Playbook Triage per Caz (Exemple Răspuns)

### Caz A: Conflict `forbidden` pe Pilon (`money_root_animatori_petreceri_copii`) (S3)
**Semnal:** Un slug neautorizat (ex: `/servicii-optionale/mascote`) indexează organic și atrage click-uri pe query-ul master "animatori petreceri copii".
**Acțiune:**
1. Deschide raportul detaliat în GSC / Ops Dashboard.
2. Analizează on-page elementul deviant: are un `title` sau o sintaxă *root focus* nepermisă?
3. Verifică internal linking-ul sitului (Poate `anchor text`-ul site-wide trimite confuz link value?).
4. Deschide Issue formal (Task de consolidare / Refactor conținut pe URL-ul deviant).
5. **DO NOT:** Nu lansa SEO Experiments pe Root în acest timp. Nu activa modificări automate oarbe în `seo_control.py` pentru a forța canibalizatorul în afara indexului fără audit.

### Caz B: Conflict `unknown` pe un Hub Judetean (București/Ilfov) (S2)
**Semnal:** O pagină nouă sau necartografiată primește ranking localizat pe query-ul "animatori copii bucuresti".
**Acțiune:**
1. Desfășoară investigație on-site: Pagina e legitimă dar abia lansată (ex: un landing specializat valid)? 
2. Dacă pagina e legitimă -> Deschide PR Proposal de extindere a `query_ownership_registry.json`, clasificând-o ca `supporter`.
3. Dacă pagina constituie drift real -> Formulează un plan de fix `on-page` / retargetare keywords în content.

### Caz C: `owner_present = false` pe un Cluster Critic (S2 / S3)
**Semnal:** The Owner URL (`/petreceri/sector-1`) are 0 impresii GSC raportate pe clusterul alocat.
**Acțiune:**
1. Confirmă dacă lipsa e din latenta datelor (GSC delay), performanță on-site sau de-indexare.
2. Rulează raport audit de sănătate a site-ului.
3. **DO NOT:** Nu concluziona automat „Owner-ul e mort”. Nu schimba owner-ul în Registry orbește.
4. Escaladează pentru revizie manuală SEO.

---

## 5. Acțiuni Permise vs Interzise (Rules of Engagement)

Agentul și Operatorului li se aplică următoarele distincții stricte de Phase 4:

✅ **PERMIS ÎN Faza 4:**
- Investigație tehnică (GSC, Crawl Log).
- Deschidere tichete / Issue creation detaliate cu plan de adresare.
- PR Proposal pentru updatarea arhitecturilor JSON Level 4 (`clusters` și `registry`).
- Content Review sau Internal Linking Review proposals.
- Recomandarea introducerii unui Kill-Switch / SEO_FREEZE limitat la nivel de operator pentru analiza daunei.

❌ **INTERZIS ÎN Faza 4:**
- **Zero hard blocks automate** pe baza json-ului pasiv (Nu se alterează deciziile Level 3 on the fly).
- Nu se practică auto-fix (mutarea sau rescrierea codului sursă `seo_apply_task.py`) bazată doar pe citirea tabelei.
- Evitarea mutării automate a The Owner.
- Nicio procedură de `auto-create` noi pagini direct din dashboard.
- Este strict interzis a declara victoria de business ("Am atins Locul 1") folosindu-ne de absența conflictelor din Dashboard. Tabela dovedește protecția clusterului, SERP Checker-ul validează clasamentul final.

---

## 6. Escalation Path

1. **[S0 / S1]** Banal → Se lasă în **backlog**; Operatorul revizuiește statistic la finalul lunii.
2. **[S2]** Derivă → Intră în **Review Prioritar Săptămânal**. Se pregătește un roadmap de tăiere din intenția paginilor parazite.
3. **[S3]** Urgență Canibalizare → **Escaladare imediată**. Freeze la orice experiment pe bucket-ul vizat. Lansare Issue "Blocker" de reconsolidare arhitecturală (ex: Canonicalizări 301, ștergere thin-content agresiv, redirecționarea anchorului intern).

---

## 7. Integrare Dashboard & Shortcuts

Acest Runbook tratează strict interfața **Level 4** operaționalizată pe `ops.superparty.ro`:
* **Summary View:** `ops.superparty.ro/seo` - Oferă semnalul inițial de sănătate / overview global.
* **Deep-Dive Table View:** `ops.superparty.ro/seo/cluster-health`
* **Filtre Triage Rapide:**
   * Apasă `[Warnings Only]` pentru a filtra curat drifturile active.
   * Apasă `[Money Only]` pentru triaj imediat pe sursele S3/S2 care impactează financiar Pilonii.
   * Filtrează individual coliziunile severe apăsând `Forbidden` în secțiunea de clasificare. 
   * Clickează un ID din tabelă (`?cluster=ID`) pentru focus mode 1:1 într-o ședință de Issue Tracking.
