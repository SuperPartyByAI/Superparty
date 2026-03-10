# seo-control-plane

> SEO Control Plane — engine comun L5/L6 pentru multi-site

Engine SEO reutilizabil extras din SuperParty. Permite operarea L5/L6 pe orice site
prin adapters specifice, fără a duplica logica core.

**Status:** Private — faza pilot SuperParty + Animatopia

---

## Structură

```
seo-control-plane/
  core/
    site_adapter.py        ← ABC: interfata obligatorie per-site
    run_readiness.py       ← readiness report (adapter-aware)
    run2_planner.py        ← Run 2 candidate planner (adapter-aware)
  adapters/
    superparty/adapter.py  ← SuperPartyAdapter
    animatopia/adapter.py  ← AnimatopiaAdapter (cu guard editorial)
  scripts/
    smoke_test_animatopia.py ← smoke test read-only Animatopia
  tests/
    test_adapters.py       ← 42 teste (ABC, SP, AT, core readiness/planner)
  docs/
    onboarding.md          ← cum adaugi un site nou
```

---

## Instalare ca subtree în site-repouri

```bash
# Adaugă engine în SuperParty
cd SuperParty/
git subtree add --prefix engine \
  https://github.com/SuperPartyByAI/seo-control-plane.git main --squash

# Update când engine-ul se schimbă
git subtree pull --prefix engine \
  https://github.com/SuperPartyByAI/seo-control-plane.git main --squash
```

Același proces pentru Animatopia și orice site nou.

---

## Cum adaugi un site nou

1. Creează `adapters/my-site/adapter.py` — extinde `SiteAdapter`
2. Implementează metodele obligatorii (vezi `core/site_adapter.py`)
3. Adaugă teste în `tests/test_adapters.py`
4. Rulează smoke test: `python scripts/smoke_test_animatopia.py /path/to/site`
5. Subtree add în repo-ul site-ului

**See:** [docs/onboarding.md](docs/onboarding.md)

---

## Rulare teste

```bash
cd seo-control-plane
python -m pytest tests/ -q
```

---

## Guardrails (neschimbabile)

- Doar `meta_description_update`
- Doar Tier C
- Max 1 auto-apply per run
- Fără canonical / robots / noindex / sitemap
- Fără commit automat
- Fără PR automat
- Feedback observability-only
- Totul explicabil și reversibil
