# Runbook: Level 4 Gap Detector — Triage Operațional

**Scop:** Proceduri pentru operatori la interpretarea și triajul oportunităților detectate de `seo_level4_gap_detector.py`.
**Mod:** Read-Only. Zero enforcement. Zero creare automată de pagini.

---

## Structura Output-ului

Fișierul `reports/superparty/seo_gap_opportunities.json` conține lista de oportunități sortată:
1. **Confidence**: `high` → `medium` → `low`
2. **Tier**: `A` → `B` → `C`

Dashboard: [`/seo/cluster-gaps`](https://ops.superparty.ro/seo/cluster-gaps)

---

## Tipuri de Gap și Reguli de Triage

### 1. `optimize_owner` — Owner Absent sau Slab

**Semnal trigger:** `missing_owner` sau `weak_owner`

| Situație | Regula Operatorului |
|---|---|
| **Owner complet absent** (Tier A) | Prioritate maximă. Verifică dacă URL-ul owner din registry mai există. Dacă a fost șters sau redirecționat, actualizează registry. |
| **Owner absent** (Tier B/C) | Prioritate medie. Lasă pe lista de triage săptămânală. |
| **Owner cu impresii prea mici** (weak_owner) | Verifică dacă este un URL nou care n-a acumulat trafic sau dacă a suferit un drop real. Corelează cu GSC. |

**Ce NU faci:** Nu creezi pagini noi fără aprobare editorială. Nu modifici structura URL-urilor owner fără testare.

---

### 2. `add_support` — Acoperire Insuficientă

**Semnal trigger:** `low_coverage`

| Situație | Regula Operatorului |
|---|---|
| Cluster sub pragul minim de impresii | Verifică dacă topic-ul este valid (există căutări) sau dacă este un cluster fantasmă (volum zero în GSC). |
| Topic valid, volum mic | Propune articol de acoperire sau pagina de suport. Trimite pentru aprobare editorială. |
| Topic fără volum | Marchează ca `reject` în registry pentru a exclude din rapoartele viitoare. |

**Ce NU faci:** Nu crea pagini suport automat. Nu aplica modificări SEO fără verificare.

---

### 3. `review_registry_mapping` — URL-uri Inclasificate în Exces

**Semnal trigger:** `high_unknown_ratio`

| Situație | Regula Operatorului |
|---|---|
| >50% URL-uri `unknown` în cluster | Deschide `query_ownership_registry.json` și verifică dacă URL-urile respective sunt deja declarate corect. |
| URL-uri noi apărute în GSC | Clasifică manual: `supporter`, `forbidden`, sau adaugă la registry ca owner alternativ. |
| URL-uri de blog/articole | De obicei `supporter` legitim — adaugă în `allowed_support_urls`. |

**Ce NU faci:** Nu muta URL-uri în `forbidden` fără validare că nu sunt pagini active.

---

### 4. `reject_risky_expansion` — Expansion Blocat de Policy Conservativă

**Semnal trigger:** `risky_expansion_guard` (supplement, nu standalone)

> Acest semnal apare **suplimentar** pe clustere Tier A care au deja un alt gap detectat.
> Înseamnă că, deși există un gap, **NU** se poate forța extinderea de content.

| Situație | Regula Operatorului |
|---|---|
| Gap detectat + Tier A + conservativ | Rezolvă gapul prin optimizare internă (nu prin pagini noi). |
| Vrei să adaugi conținut nou lângă un cluster Tier A | Cere aprobare explicită și schimbă `expansion_policy` la `flexible` în registry după decizie documentată. |

---

## Escaladare

| Tip Gap | Cine Decide |
|---|---|
| `optimize_owner` pe Tier A | Decizie obligatorie cu operator senior |
| `review_registry_mapping` | Oricine poate propune, operator senior aprobă |
| `add_support` pe Tier B/C | Poate fi delegat editorial |
| `low_coverage` pe Tier C | Review în ciclu lunar, nu urgent |

---

## Frecvență Recomandată de Rulare

| Tip Raport | Frecvență |
|---|---|
| `run_gap_detection()` manual | Săptămânal sau după fiecare ciclu advisory |
| Triage complet `high confidence` | La fiecare run |
| Triage `medium confidence` | Lunar |
| Triage `low confidence` | Trimestrial |

---

## Note Tehnice

- **`weak_owner`** detectează în prezent clustere cu impresii total sub prag, **nu** `owner_impressions / total_impressions`. Aceasta este o limitare documentată — o rafinare viitoare poate introduce `owner_share` din health report.
- Pragurile (min impressions, unknown ratio threshold) sunt configurabile din `config/seo/gap_detector_config.json`.
- Rapoartele sunt **read-only**. Nicio acțiune din dashboard nu modifică conținutul site-ului.
