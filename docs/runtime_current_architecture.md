# Arhitectura Curentă a Agentului Superparty

> **Status**: PRODUCȚIE (LEVEL 3 ENTERPRISE)  
> **Host**: Hetzner VPS (Debian)  
> **Arhitectură**: Systemd + Redis Nativ + NGINX/Express.  

Acest document este **Sursa de Adevăr** privind funcționarea și guvernarea agenților SEO Superparty conform noului standard "Enterprise Operational" (eliminând infrastructura anterioară de Docker Compose `sp_worker`).

---

## 1. Servicii Rulează Nativ pe Systemd

Serviciile agenților sunt coordonate direct prin Daemon-ul OS-ului și gestionate sub un utilizator izolat `superparty-agent` (fără privilegii de execuție ca root). Toate definițiile fisierelor unit se regăsesc localizate în `.github/workflows` ori sub `infrastructure/systemd/`. 

Servicii active managed prin `systemctl`:
- `superparty-orchestrator.service` (cron control)
- `superparty-worker-apply.service`
- `superparty-worker-seo.service`
- `superparty-worker-ads.service`
- `superparty-worker-backup.service`

**Atenție**: Containerele Docker, ca metode de execuție, au fost integral eliminate. Orice script, runbook sau README din commiturile vechi care prezintă comenzile de `docker ps`, `docker exec sp_worker` sunt **arhi-depășite**. Dacă descoperiți astfel de documente, ignorați-le.

### Comenzile Unice Aprobare (pe mașina de Host)

Pentru a vizualiza starea curentă a serviciilor:
```bash
systemctl status superparty-* --no-pager
```

Pentru restart sau recitirea Environment Variable-urilor:
```bash
systemctl restart superparty-worker-seo
```

Pentru a vedea logurile persistente non-infinite:
```bash
tail -n 100 /var/www/superparty/logs/worker_seo.log
tail -n 100 /var/www/superparty/logs/worker_apply.log
tail -n 100 /var/www/superparty/logs/orchestrator.log
```

---

## 2. Locație Cod și Cont Utilizator
- Codul repo-ului este setat în **WorkingDirectory**: `/var/www/superparty`
- Baza de date a experimentelor e păstrată local sub: `reports/superparty/seo_experiments.db`
- Ecosistemul de agent rulează sub propriul lui utilizator non-root: `superparty-agent`

---

## 3. Gestionarea Mediului

Toate serviciile Systemd încarcă automat mediul folosind piesa unică:
`EnvironmentFile=/var/www/superparty/.env`

O listă completă cu parametrii obligatorii ce trebuie să existe la nivel de fișier `.env` de bază:
- `SEO_CONTINUOUS=1` (Posedă control asupra rulării zilnice continue SEO pentru planuri)
- `SEO_APPLY_MODE=real` (Determină efectivitatea scrierii datelor versus report)
- Keys GA4 / Google Search Console credentials (inclusiv path point).

---

## 4. Baza Message Broker / Cozi
Aplicația utilizează nativ `rq` pe un server **Redis** ascultând local. 
Redis nu mai operează ca docker image `sp_redis`. Serviciul curat (pachet Debian `redis-server`) susține prezența la viață. 

Pentru a testa prezența broker-ului care conectează `orchestrator` cu restul worker-ilor, verificați din host:
```bash
redis-cli ping
# Trebuie să obțineți PONG.
```

---

## 5. Control Plane și Dashboard Privat
Aplicația React PWA rulează separat prin stack modern pre-compilat, expus ca web endpoint restricționat de un proxy NGINX, vizând nodul Node.Js de Express.

- **Adresă Dashboard**: `https://ops.superparty.ro/seo`
- Autentificarea impune regulă strictă Google OAuth validată back-end pe lista ta predefinită (ursache.andrei1995@).
- Pagina afișează Statusul Agentului (`✅ RUNNING`), Cicluri, și URL-uri validate / Experimente live conform bazelor de date extrase din repo.
