# SEO Level 5 Auto-Apply — Ops Runbook

> **Scope:** Activare, dezactivare, smoke test, verificare artefacte, rollback manual.
> **Referinta:** `agent/tasks/seo_level5_auto_apply.py` · `config/seo/level5_action_policy.json`

---

## 1. Verificare stare curentă (înainte de orice)

```powershell
# Verifica policy (default safe)
python -c "import json; p=json.load(open('config/seo/level5_action_policy.json')); print('Policy enabled:', p['auto_apply_config']['enabled'])"

# Verifica override (sursa prioritara)
python -c "import json; p=json.load(open('config/seo/auto_apply_runtime_override.json')); print('Override enabled:', p.get('enabled'))"

# Verifica status report (ultimul run)
python -c "import json; p=json.load(open('reports/superparty/seo_level5_status.json')); print(json.dumps(p, indent=2, ensure_ascii=False))"
```

---

## 2. Activare auto-apply (pentru rulare controlată)

```jsonc
// Editeaza: config/seo/auto_apply_runtime_override.json
// ATENTIE: fisier neversioned (.gitignore), nu se commiteaza
{
  "enabled": true
}
```

**Prioritatea sursei de activare:**
1. `auto_apply_runtime_override.json` (daca exista) — **prioritate maxima**
2. `level5_action_policy.json` → `auto_apply_config.enabled`
3. Daca niciuna nu e `true` → agentul nu face nimic

---

## 3. Dezactivare instant

```jsonc
// Option A (recomandat): override file
{ "enabled": false }

// Option B: sterge fisierul override
// del config\seo\auto_apply_runtime_override.json

// Option C: policy (nu e recomandat in mod obisnuit)
// Seteaza auto_apply_config.enabled: false in level5_action_policy.json
```

---

## 4. Pregătire candidat Tier C

Editează `reports/superparty/seo_level5_apply_plan.json`:

```json
{
  "plan_id": "run-YYYY-MM-DD-<slug>",
  "generated_at": "ISO8601",
  "schema_version": "1.3",
  "plan": [{
    "action_id": "uuid",
    "plan_id": "run-YYYY-MM-DD-<slug>",
    "action_type": "meta_description_update",
    "url": "/slug-pagina",
    "tier": "C",
    "is_money_page": false,
    "is_pillar_page": false,
    "ready_to_apply": true,
    "proposal_source": "deterministic_fallback",
    "before": { "meta_description": "Textul exact din pagina acum" },
    "proposal": { "meta_description": "Text nou optimizat 120-155 chars fara ghilimele" }
  }],
  "blocked": []
}
```

> ⚠️ **Verifică obligatoriu:**
> - URL-ul nu este în `config/seo/pillar_pages_registry.json`
> - `before.meta_description` este identic cu textul din fișier (drift check)
> - URL-ul nu a fost aplicat în ultimele 14 zile (cooldown)

---

## 5. Smoke test

```powershell
cd c:\Users\ursac\Superparty

# A. Ruleaza testele de safety (trebuie 0 failed)
python -m pytest tests/test_seo_level5_auto_apply.py tests/test_seo_level5_auto_apply_policy.py -v --tb=short

# B. Ruleaza engine-ul (cu override enabled=true)
python -m agent.tasks.seo_level5_auto_apply

# Output asteptat:
# AUTO_APPLY: success
```

---

## 6. Verificare artefacte post-run

```powershell
# Audit log — ultima intrare
python -c "
import json
log = json.load(open('reports/superparty/seo_level5_auto_apply_log.json', encoding='utf-8'))
last = log[-1]
print('URL:', last['url'])
print('approved_by:', last['approved_by'])
print('activation_source:', last['activation_source'])
print('BEFORE:', last['before']['meta_description'][:80])
print('AFTER:', last['after']['meta_description'][:80])
"

# Status report
python -c "
import json
s = json.load(open('reports/superparty/seo_level5_status.json', encoding='utf-8'))
print(json.dumps(s, indent=2, ensure_ascii=False))
"

# Rollback payload
python -c "
import json
p = json.load(open('reports/superparty/seo_level5_rollback_payload.json', encoding='utf-8'))
print('FILE:', p['file_path'])
print('BEFORE:', p['before']['meta_description'])
print('AFTER:', p['after']['meta_description'])
"
```

---

## 7. Rollback manual

```powershell
# Citeste rollback payload
python -c "
import json
from pathlib import Path

payload = json.load(open('reports/superparty/seo_level5_rollback_payload.json', encoding='utf-8'))
file_path = Path(payload['file_path'])
before_desc = payload['before']['meta_description']
after_desc = payload['after']['meta_description']

content = file_path.read_text(encoding='utf-8')
if after_desc in content:
    restored = content.replace(after_desc, before_desc, 1)
    file_path.write_text(restored, encoding='utf-8')
    print('ROLLBACK OK:', str(file_path))
    print('Restaurat:', before_desc[:80])
else:
    print('ERROR: textul AFTER nu mai e in fisier. Rollback manual necesar.')
    print('Expected AFTER:', after_desc[:80])
"
```

> ⚠️ Dupa rollback: dezactiveaza automat flag-ul prin override file.

---

## 8. Contractul care trebuie respectat întotdeauna

| Invariant | Valoare |
|---|---|
| Max candidati per run | 1 |
| Tier eligibil | C |
| Action type permis | `meta_description_update` |
| Tier A | Interzis |
| Tier B | Interzis |
| Money pages | Interzise |
| Pillar pages (plan + registry) | Interzise |
| Commit automat | ❌ |
| PR automat | ❌ |
| Cooldown per URL | 14 zile |
| Rollback obligatoriu | ✅ |
| Audit trail obligatoriu | ✅ |
