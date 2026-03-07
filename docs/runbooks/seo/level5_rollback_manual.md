# Runbook: Level 5 Manual Rollback — Meta Description Revert

**Versiune:** 1.0
**PR:** #60
**Scope:** Revertire manuală a unui apply controlat de `meta_description_update` pe o pagină Tier C.
**Ultima actualizare:** 2026-03-07

---

## 1. Când se aplică acest runbook

Aplici acest runbook NUMAI când:

- `seo_level5_apply_execution.json` raportează `applied = 1`
- Vrei să reverți modificarea aplicată de executor
- Fie din decizie operațională, fie din cauza unui incident SEO

**NU aplici rollback automat.** Rollback-ul este întotdeauna decid și executat manual.

---

## 2. Artefacte necesare înainte de a începe

Verifică că toate cele 4 artefacte există și sunt coerente:

```
reports/superparty/
├── seo_level5_approval_log.json       ← conține decision_id
├── seo_level5_apply_plan.json         ← conține plan_id
├── seo_level5_apply_execution.json    ← conține execution_id, rollback_payload_path
└── seo_level5_rollback_payload.json   ← conține file_path, before, after
```

**Verificare rapidă de coerență:**
```bash
python agent/tasks/seo_level5_rollback_executor.py --dry-run --validate-only
```

Dacă validarea eșuează, mergi direct la **Scenariul B** sau **C** de mai jos.

---

## 3. Pași normali de rollback (Scenariul A — rollback_ready=true)

### Pasul A1 — Citește rollback_payload.json

```bash
cat reports/superparty/seo_level5_rollback_payload.json
```

Verifică că există:
- `file_path` — calea relativă la fișierul .astro modificat
- `before.meta_description` — valoarea originală de restaurat
- `after.meta_description` — valoarea care a fost aplicată (ca referință)
- `rollback_mode: "single_file_revert"`
- `action_id`, `plan_id`, `decision_id` — coerente cu execution report

### Pasul A2 — Verifică starea curentă a fișierului

```bash
python agent/tasks/seo_level5_rollback_executor.py --dry-run
```

Output-ul va arăta:
```json
{
  "file_path": "src/pages/blog/exemplu.astro",
  "current_meta_description": "<valoarea actuală din fișier>",
  "expected_after": "<valoarea din payload.after>",
  "expected_before": "<valoarea originală de restaurat>",
  "current_matches_after": true,
  "rollback_feasible": true
}
```

**Dacă `current_matches_after: false`** → fișierul a fost modificat manual după apply. Stop. Escalate.

### Pasul A3 — Execută rollback

```bash
python agent/tasks/seo_level5_rollback_executor.py --execute
```

Executorul:
1. Re-citește `rollback_payload.json` (nu caching)
2. Verifică că fișierul conține `payload.after.meta_description` (drift check)
3. Înlocuiește cu `payload.before.meta_description`
4. Verifică că fișierul conține noua valoare (post-rollback read)
5. Scrie `reports/superparty/seo_level5_rollback_execution.json`

### Pasul A4 — Verificare post-rollback

```bash
python agent/tasks/seo_level5_rollback_executor.py --verify-only
```

Verificat:
- [ ] Fișierul `.astro` conține `payload.before.meta_description`
- [ ] `rollback_execution.json` există cu `reverted: true`
- [ ] `rollback_execution.json` conține `decision_id`, `plan_id`, `execution_id` originale
- [ ] Niciun alt fișier SEO nu a fost modificat

### Pasul A5 — Notificare

Notifică echipa cu:
- `decision_id` original
- `execution_id` original
- URL-ul paginii revertite
- Motivul rollback-ului
- Timestamp

---

## 4. Scenariul B — rollback_ready=false

**Cauze posibile:**
- `rollback_payload.json` corupt sau incomplet
- `before.meta_description` lipsă
- `file_path` lipsă sau incorect

**Pași:**

1. Deschide `seo_level5_apply_execution.json`
2. Localizează `blocked_actions[].blocking_reason` sau `applied_actions[0].before`
3. Dacă `before.meta_description` este disponibil în execution report → folosește-l manual
4. Deschide fișierul `.astro` direct în editor
5. Localizează câmpul `description =` în frontmatter sau `<meta name="description" content=...>`
6. Înlocuiește manual cu valoarea `before.meta_description` din execution report
7. Salvează fișierul
8. Verifică manual că modificarea este corectă
9. Documentează acțiunea manual în `seo_level5_rollback_execution.json` (creat manual):
   ```json
   {
     "rollback_type": "manual_editor",
     "reason": "rollback_ready=false",
     "file_path": "...",
     "value_restored": "...",
     "reverted_by": "<operator>",
     "reverted_at": "<ISO timestamp>",
     "decision_id": "...",
     "plan_id": "...",
     "execution_id": "..."
   }
   ```

---

## 5. Scenariul C — post_write_verification_failed

**Contextul:** Executorul a scris fișierul, dar verificarea post-write a eșuat. Fișierul poate fi în stare nedeterminată.

**Pași:**

1. Deschide fișierul `.astro` din `rollback_payload.file_path` direct în editor
2. Verifică ce valoare are câmpul `meta_description`
3. Cazuri:
   - **Conține valoarea nouă (`after`)** — scrie valoarea originală (`before`) manual
   - **Conține valoarea originală (`before`)** — write-ul a eșuat, nicio acțiune necesară. Documentează.
   - **Conține altceva** — escalate imediat (fișier corupt)
4. Dacă ai restaurat manual valoarea `before`, documentează ca în Scenariul B

---

## 6. Scenariul D — mismatch între fișier și payload

**Contextul:** La pasul A2, `current_matches_after: false`. Fișierul nu conține `payload.after`, ceea ce înseamnă că a fost modificat ulterior.

**Stop. Nu aplica rollback automat.**

**Pași:**
1. Compară manual conținutul fișierului cu `payload.before` și `payload.after`
2. Dacă fișierul conține o valoare total diferită — modificare manuală externă. Escalate.
3. Dacă fișierul conține `payload.before` — fișierul a fost deja revertit. Verifică de cine și documentează.
4. Dacă fișierul conține `payload.after` cu diferențe minore (whitespace) — decide manual

---

## 7. Criterii de stop / escalation

**Oprește-te și escalatează dacă:**

- Fișierul `.astro` conține HTML corupt sau structură frontmatter ruptă
- `decision_id` din `rollback_payload` nu se regăsește în `approval_log.json`
- Există mai mult de o înregistrare cu același `action_id` în `approval_log`
- `file_path` din payload nu există pe disc
- Rollback-ul ar afecta mai mult de un câmp sau mai mult de un fișier

**Contact escalation:**
- Verifică `approval_log.json` pentru `decided_by` — acesta este operatorul care a aprobat acțiunea originală
- Notifică cu `action_id`, `decision_id`, `execution_id`, și starea curentă a fișierului

---

## 8. Ce NU se face în rollback

| ❌ Interzis | Motiv |
|---|---|
| Batch rollback (mai multe acțiuni deodată) | Out of scope — un rollback per execuție |
| Revertit titlul paginii | `meta_title_update` nu este activ |
| Revertit alte câmpuri SEO | Boundary strict: numai `meta_description` |
| Auto-commit sau auto-PR după rollback | Rollback este manual, fără automatizare |
| Overwrite `approval_log.json` | Log-ul este append-only și imutabil |
| Ștergere `rollback_payload.json` | Payload-ul trebuie păstrat ca audit trail |
| Rollback fără a documenta în `rollback_execution.json` | Fiecare rollback trebuie înregistrat |

---

## 9. Artefacte generate de rollback

```
reports/superparty/
└── seo_level5_rollback_execution.json
```

Structura minimă:
```json
{
  "schema_version": "1.0",
  "rollback_type": "automated_executor | manual_editor",
  "reverted": true,
  "reverted_at": "<ISO timestamp>",
  "reverted_by": "<operator>",
  "original_lineage": {
    "execution_id": "...",
    "plan_id": "...",
    "decision_id": "...",
    "action_id": "..."
  },
  "file_path": "...",
  "before_restored": "<valoarea restaurată>",
  "after_reverted": "<valoarea care a fost înlăturată>",
  "post_rollback_verification": true
}
```

---

## 10. Referințe

- Executor apply: `agent/tasks/seo_level5_meta_description_apply.py`
- Executor rollback: `agent/tasks/seo_level5_rollback_executor.py`
- Policy: `config/seo/level5_action_policy.json`
- Artefacte de run: `reports/superparty/seo_level5_*.json`
- Runbook boundary: `docs/runbooks/seo/level5_action_boundary.md`
