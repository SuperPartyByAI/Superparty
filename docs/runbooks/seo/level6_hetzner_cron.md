# Runbook: Hetzner Scheduled Report Worker (Level 6.2)

Acest document descrie instalarea și mentenanța worker-ului Python responsabil de generarea asincronă, sigură a datelor de Input (Health, Priority, Trends) SEO, pe un mediu tipic VPS (Hetzner).

## 1. Instalare CRON Job (Fără SystemD extins)

Jobul trebuie să pună în mișcare pachetul existent Python, o singură dată pe zi, într-o fereastră fixă predictibilă. O facem la **03:00 AM UTC**, ora la care prezența pe SERP-uri e minimală iar API-ul GSC stochează deja date reci de ieri.

```bash
# Deschide editorul de crontab
crontab -e

# Adaugă următoarea linie (ajustând căile OS absolut)
0 3 * * * cd /path/to/Superparty && /usr/bin/python3 scripts/hetzner_daily_report_worker.py >> /var/log/seo_hetzner_worker.log 2>&1
```

## 2. Principiul de Funcționare (Fail-Closed)

La rigoarea Master Worker-ului aprobat:
1. Noua generare se face mereu într-un director `/tmp`.
2. Validarea schemei JSON și a vechimii are loc local pe acel json generat — **Strict Match Validations**:
   - `seo_cluster_health.json` (schema 1.0)
   - `seo_cluster_priority.json` (schema 2.0)
   - `seo_trend_delta.json` (schema 1.1)
3. Fără "spoofing". Tot lanțul necesită re-generare totală din material brut GSC. 
4. API-urile pot eșua pe Quota Google GSC. Excepția *nu distruge rapoartele de ieri*. E ok să rateze rulajul. Raportul "Freshness Gate" (L6.1) din pre-flight executor va invalida natural munca dacă depășește termenul de grație de ~48 hr stabilit limitând fail-safe tot apply-plane-ul offline.

## 3. Comenzi Mentenanță

Verificare manuală a logurilor (ultimele raportări):
```bash
tail -n 50 /var/log/seo_hetzner_worker.log
```

Rulare forțată off-schedule (trigger manual test):
```bash
cd /path/to/Superparty
export PYTHONPATH=$(pwd)
python3 scripts/hetzner_daily_report_worker.py
```
