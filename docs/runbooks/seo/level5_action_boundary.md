# Level 5 — Action Boundary Document

> **Tip:** Design Boundary Only — PR #53
> **Nu conține nicio implementare runtime.**
> Execuția primei acțiuni controlate este condiționată de aprobarea manuală a acestui document și a contractului `level5_action_policy.json`.

---

## 1. Scop

Acest document definește **ce este permis** și **ce este explicit interzis** la Level 5 al Enterprise SEO Agent.

**Level 5 ≠ AI care decide și execută autonom.**
**Level 5 = Execuție strict controlată a acțiunilor low-risk pre-aprobate de un operator uman.**

---

## 2. Ce rămâne definitiv interzis (în orice circumstanță)

| Acțiune | Motivul interdicției |
|---|---|
| `change_canonical` | Risc maxim: schimbarea canonicalului poate dezindexiza pagini |
| `change_robots` | Risc maxim: poate bloca crawling-ul complet |
| `change_noindex` | Risc maxim: poate elimina pagini din index |
| `change_registry` | Schimbă definiția de ownership — necesită revizie arhitecturală |
| `change_cluster_schema` | Schimbă structura de guvernanță SEO — modificare de schemă |
| `change_internal_ownership` | Redistribuie autoritate inter-cluster — risc strategic |
| `modify_pillar_page` | Paginile pilon sunt baza rankingului — orice modificare este manuală |
| `modify_sitemap_policy` | Afectează toată indexarea site-ului |

> **Regula: Dacă acțiunea poate afecta crawling, indexing sau ownership structural → interzisă la Level 5.**

---

## 3. Ce este „Low-Risk Eligible" (definit, dar neactivat în PR #53)

Aceste acțiuni sunt **descrise** ca potențial admisibile la Level 5, dar **nu sunt activate** în PR #53. Activarea individuală necesită un PR separat cu `dry_run_required: true` și `approval_gate: manual`.

| Acțiune | Descriere | Condiții de activare |
|---|---|---|
| `meta_title_update` | Actualizarea tag-ului `<title>` pentru pagini non-pilon | PR separat + dry-run + Tier C sau B restricted |
| `meta_description_update` | Actualizarea meta description | PR separat + dry-run + Tier C sau B restricted |

**Nu sunt incluse** (și nu vor fi incluse fără revizie separată):
- headings (H1/H2/H3)
- body copy
- internal links
- schema markup
- title template rewrites
- template-level changes
- pagini Tier A / money pages

---

## 4. Tier Restrictions

| Tier | Statut Level 5 |
|---|---|
| **A** | `read_only` — nicio acțiune executabilă, indiferent de tip |
| **B** | `restricted` — acțiuni eligibile numai cu PR explicit + dry-run + manual review |
| **C** | `low_risk_eligible` — acțiunile din `low_risk_eligible_actions` sunt candidați |

> **Tier A = read_only este absolut.** Nicio excepție în PR #53 sau #54.

---

## 5. Guardrails Obligatorii (pentru orice acțiune viitoare)

Indiferent de tipul acțiunii sau tier:

| Guardrail | Valoare în PR #53 |
|---|---|
| `dry_run_required` | `true` — orice acțiune rulează mai întâi în mod simulat |
| `approval_gate` | `manual` — un operator uman aprobă explicit înainte de execuție |
| `rollback_required` | `true` — orice acțiune trebuie să aibă un rollback documentat |
| `max_actions_per_run` | `0` — PR #53 nu execută nimic; activarea vine din PR #54+ |

---

## 6. Feedback Loop — Ce este permis să măsurăm

### Semnale permise

Feedback-ul observabil poate include exclusiv:

- `impressions` — impresii GSC
- `clicks` — click-uri GSC
- `ctr` — click-through rate
- `average_position` — poziția medie în SERP
- `owner_share_delta` — variația owner_share (din trend report PR #51)
- `forbidden_delta` — variația URL-urilor canicbalizatoare
- `trend_status` — improved / regressed / stable / mixed

### Claims interzise

Sunt **explicit interzise** felătoarele formulări sau comportamente:

| Claim interzis | De ce este interzis |
|---|---|
| „Am obținut #1 în SERP" | Nu poate fi validat fără date SERP externe independente |
| „Acțiunea a produs câștig SEO confirmat" | Outcome-ul SEO necesită validare externă, nu auto-interpretare |
| „AI a optimizat pagina cu succes" | Formulare de outcome claim fără dovadă empirică validată |

> **Formularea corectă:** „Semnalul X s-a modificat cu Y după acțiunea Z. Interpretarea SEO necesită revizie manuală."

---

## 7. Requires Human Review (obligatoriu, fără excepție)

Înainte de orice acțiune, un operator uman revizuiește explicit dacă pagina sau clusterul se încadrează în:

- `all_tier_a` — orice cluster sau pagină Tier A
- `all_money_pages` — orice pagini marcate ca money (is_money_cluster: true)
- `all_registry_touches` — orice operație care implică sau poate implica query_ownership_registry.json

---

## 8. Ordinea corectă de implementare după PR #53

| PR | Conținut | Condiție |
|---|---|---|
| **#53** (acesta) | Design boundary doc + policy contract + test validare | Design only, nicio execuție |
| **#54** | Primul executor strict dry-run pentru 1 acțiune `low_risk_eligible` | Numai după aprobarea manuală a PR #53 |
| **#55+** | Extinderea gradată a acțiunilor permise | Numai pe baza feedback-ului observabil din PR #54 |

---

## 9. Ce NU este Level 5

- NU este un AI care decide autonom ce să schimbe
- NU este un sistem de recomandare care se auto-aplică
- NU este un feedback loop care „învață" din outcome SEO și ajustează singur
- NU este un sistem de ranking claim sau outcome validation

---


*Document de Design Boundary — Level 5 | Actualizat PR #85 | 2026-03-09 | Read-Only*

---

## 10. Modul Controlled Single Auto-Apply (PR #85)

> **Activare:** exclusiv prin `auto_apply_config.enabled: true` în `level5_action_policy.json`.
> **Default:** `enabled: false` — comportament identic cu schema_version 1.2.

### Condiții stricte pentru eligibilitate auto-apply

Toate condițiile trebuie să fie îndeplinite simultan:

| # | Condiție | Blocker dacă nu trece |
|---|---|---|
| 1 | `auto_apply_config.enabled: true` (feature flag explicit) | Auto-apply nu rulează |
| 2 | Exact 1 candidat eligibil Tier C în dry-run | Blocat — max 1 per run |
| 3 | Proposal valid (lungime 140–160 ch, fără HTML/ghilimele/newline) | Blocat |
| 4 | Pagina NU este `is_money_page` | Blocat |
| 5 | Pagina NU este `is_pillar_page` | Blocat |
| 6 | Before-state fișier corespunde exact planului | Blocat — drift detection |
| 7 | `action_type` în `auto_apply_actions_allowlist` (doar `meta_description_update`) | Blocat |
| 8 | Tier în `auto_apply_tier_allowlist` (doar `C`) | Blocat |

### Audit Trail Obligatoriu

Fiecare auto-apply scrie în `seo_level5_auto_apply_log.json` (append-only):

```json
{
  "auto_apply_id": "uuid",
  "approved_by": "system_auto_apply",
  "approval_mode": "auto_applied",
  "proposal_source": "llm | deterministic_fallback",
  "auto_apply_reason": ["tier_c_eligible", "valid_proposal", "file_match_ok"],
  "before": {"meta_description": "..."},
  "after": {"meta_description": "..."},
  "rollback_reference": "seo_level5_rollback_payload.json",
  "applied_at": "ISO8601",
  "policy_version": "1.3"
}
```

### Status distinct în execution report

| Valoare `approval_mode` | Semnificație |
|---|---|
| `proposed_only` | Dry-run propunere, nicio aplicare |
| `manually_approved` | Aprobat manual de operator |
| `auto_applied` | Aplicat automat (feature flag ON) |
| `rolled_back` | Reverted de rollback executor |

### Ce NU este modul auto-apply

- NU este batch apply (max 1 candidat per run)
- NU este feedback loop cu auto-learning
- NU atinge Tier A, Tier B, money pages sau pillar pages
- NU schimbă canonical, robots, noindex sau sitemap
- NU activează `meta_title_update` (neactivat)
- NU emite claim-uri de tip „SEO win confirmat automat"

### Oprire instant

Setează `auto_apply_config.enabled: false` în `level5_action_policy.json`.
Nicio altă modificare necesară.
