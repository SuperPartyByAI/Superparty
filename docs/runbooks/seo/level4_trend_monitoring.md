# Level 4.1 — SEO Trend Monitoring: Runbook Operațional

> **Scopul acestui runbook**: Interpretarea raportului `seo_trend_delta.json` și escaladarea corectă a problemelor detectate în trending.

---

## 1. Introducere

### Ce este `seo_trend_delta.json`?

Fișierul `reports/superparty/seo_trend_delta.json` conține **delte calculate** între snapshot-ul curent și snapshot-ul anterior (ziua precedentă).

Este produsul modulului `seo_trend_analyzer.py` (PR #51) și **NU recalculează** logica de scoring sau health — doar compară.

### Ce reprezintă `owner_share`?

`owner_share = owner_impressions / total_impressions (cluster)`

| Valoare | Semnificație |
|---|---|
| `>= 0.4` | Control acceptabil al owner-ului |
| `< 0.4` | `weak_owner` — semnalul de gap este activ |
| `0.0` | Owner ranking cu share real zero (critic) |
| `null` | Date lipsă — snapshot anterior fără `owner_share` (pre-PR50) |

> **IMPORTANT**: `null` ≠ `0.0`. Un `null` înseamnă că data nu era disponibilă în snapshot-ul vechi, **nu** că owner-ul are share zero. Nu escalada pe `null`.

---

## 2. Praguri Operaționale

### Owner Share — Praguri de alertă

| Prag | Acțiune |
|---|---|
| `delta_owner_share <= -0.10` | **Deteriorare semnificativă** → investigație imediată |
| `-0.10 < delta_owner_share < 0` | Deteriorare ușoară → monitorizare, review la ciclul următor |
| `delta_owner_share = 0.0` | Stabil pe owner share |
| `delta_owner_share > 0` | Îmbunătățire → notat, fără acțiune |
| `delta_owner_share = null` | Snapshot incomparabil (pre-PR50) → skip pentru trend, re-verifică la ciclul următor |

### Forbidden URLs — Praguri de alertă

| Prag | Acțiune |
|---|---|
| `delta_forbidden >= 2` pe Tier A | **ESCALATION STRONG** → verificare imediată registry + canibalizare |
| `delta_forbidden >= 1` | Regression pe canibalizare → review registry și URL-urile noi |
| `delta_forbidden = 0` | Stabil |
| `delta_forbidden < 0` | Améliorer — forbidden URLs s-au redus |

---

## 3. Status Cluster — Interpretare

| Status | Semnificație | Acțiune |
|---|---|---|
| `improved` | `delta_owner_share > 0` SAU `delta_forbidden < 0` | Notat, fără acțiune urgentă |
| `regressed` | `delta_owner_share < 0` SAU `delta_forbidden > 0` | Review imediat (Tier A = escaladare) |
| `mixed` | Unele semnale îmbunătățite, altele regresate | Review manual — nu concluzie automată |
| `stable` | Nicio schimbare reală | Monitoring regulat |
| `new` | Cluster apărut în snapshot curent, absent în anterior | Verificare registry |
| `missing` | Cluster dispărut din snapshot curent | Verificare dacă clusterul a fost eliminat intenționat |

> **IMPORTANT**: `status = mixed` nu înseamnă că sistemul este OK sau NOK. Necesită **review manual**.

---

## 4. Prioritizare Investigație

Ordinea de investigație recomandată:

1. **Tier A + status `regressed`** → prioritate maximă
2. **Tier A + status `mixed`** → investigație obligatorie
3. **Tier B + status `regressed`** → investigație urgentă
4. **Tier B + status `mixed`** → monitoring activ
5. **Orice tier + `delta_forbidden >= 2`** → escaladare automată
6. Restul → monitoring de rutină

---

## 5. Proceduri de Triage

### Scenariu A: Cluster Tier A — `delta_owner_share <= -0.10`

1. Deschide `/seo/cluster-trends` în ops-dashboard → filtrează `regressed`
2. Identifică `cluster_id` afectat
3. Verifică `/seo/cluster-health` → `owner_impressions` vs `total_impressions`
4. Verifică în GSC dacă owner URL și-a pierdut poziția
5. Verifică `/seo/cluster-gaps` → `weak_owner` semnal activ?
6. Dacă DA: escaladează în GitHub Issues cu eticheta `seo-priority-1`
7. Nu modifica automat nimic — raportul este **read-only**

### Scenariu B: Cluster Tier A — `delta_forbidden >= 2`

1. Deschide `/seo/cluster-trends` → filtrează `regressed`
2. Identifică `cluster_id` cu `delta_forbidden >= 2`
3. Deschide `/seo/cluster-health` → `cannibalization_warnings`
4. Identifică URL-urile `forbidden` noi apărute
5. Verifică `config/seo/query_ownership_registry.json` → clasificare corectă?
6. Dacă URL-urile sunt greșit clasificate → deschide PR pentru registry update
7. Dacă URL-urile sunt canibalizare reală → escaladează cu `seo-canibalizare` label

### Scenariu C: `delta_priority_band` = `A->B` sau `B->C`

1. Verifică `/seo/cluster-priority` → scoring curent
2. Identifică ce semnal a scăzut (`importance_score` vs `risk_score`)
3. Verifică GSC pentru schimbări de impresii sau CTR
4. Dacă degradarea este confirmată → review editorial al owner URL-ului

---

## 6. Ce NU face acest runbook

- **Nu recomandă modificări automate** pe site
- **Nu trigggerează** niciun deploy sau apply engine
- **Nu clasifică** definitiv un cluster ca „eșuat" pe baza unui singur delta

---

## 7. Surse de Date

| Sursă | Cale |
|---|---|
| Trend Delta (PR #51) | `reports/superparty/seo_trend_delta.json` |
| Cluster Health (PR #43) | `reports/superparty/seo_cluster_health.json` |
| Priority Scoring (PR #46) | `reports/superparty/seo_cluster_priority.json` |
| Gap Opportunities (PR #48) | `reports/superparty/seo_gap_opportunities.json` |
| Snapshot History | `reports/superparty/history/YYYY-MM-DD/` |

---

## 8. Limitări Cunoscute

| Limitare | Impact | Follow-up |
|---|---|---|
| `delta_owner_share = null` pentru snapshot-uri pre-PR50 | Nu poți compara owner_share din prima rulare după upgrade | Se rezolvă automat după 2 zile de arhivare cu PR #50+ |
| `schema_version 1.0` în health/priority reports vechi | Compatibilitate aditivă, fără impact funcțional | Schema bump în PR viitor |
| Un singur snapshot pe zi (overwrite) | Nu detectează fluctuații intraday | Acceptabil pentru nivel tactical |

---

*Runbook actualizat: 2026-03-07 | Level 4.1 PR #52 | Read-Only Intelligence Layer*
