# SEO Runbooks — Superparty

Runbook-uri pentru incidente SEO enterprise. Fiecare runbook acoperă un tip specific de incident cu trigger clar, safeguard-uri imediate și decision tree.

**Regula principală:** Primul pas este ÎNTOTDEAUNA să protejezi pilonul și policy. Abia apoi investighezi.

## Runbook-uri disponibile

| Runbook | Trigger | Severitate |
|---|---|---|
| [rank_drop.md](rank_drop.md) | Pilonul iese din top 3 | **P0** |
| [ctr_drop.md](ctr_drop.md) | CTR 7d scade >20% | **P1** |
| [policy_drift.md](policy_drift.md) | Non-www / noindex / slug non-target detectat | **P0** |
| [experiment_failure.md](experiment_failure.md) | Rollback automat / experiment eșuat | **P1** |

## Ordinea de verificare la orice incident

1. Verifici mai întâi **policy drift** (sitemap, manifest, canonical)
2. Verifici **rank drop** pe pilon
3. Verifici **CTR** pe paginile money
4. Verifici **experimente active**

## Owner

Andrei Ursache — ursache.andrei1995@gmail.com

## Link-uri rapide

- Dashboard ops: https://ops.superparty.ro/seo
- GitHub: https://github.com/SuperPartyByAI/Superparty
- Premerge checks: `python scripts/seo_premerge_checks.py`
- Control plane: `python agent/tasks/seo_control.py`
