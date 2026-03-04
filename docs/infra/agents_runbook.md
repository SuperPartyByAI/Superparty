# Agents Runbook — SuperParty.ro (Hetzner)

> **Unde rulează**: Hetzner VPS (nu local)
> **Stack**: Docker Compose (Redis + Orchestrator + Workers)
> **Fișier compose**: `docker-compose.multiagent.yml`

---

## 1. Pornire stack (full)

```bash
# SSH în Hetzner
ssh root@<IP_HETZNER>
cd /path/to/superparty   # directorul unde ai clonat repo-ul

# Construieste + porneste toate containerele (cu rebuild)
docker compose -f docker-compose.multiagent.yml up -d --build

# Verifică că toate sunt UP
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Rezultat așteptat:
```
NAMES              STATUS          PORTS
sp_redis           Up X minutes    6379/tcp
sp_orchestrator    Up X minutes
sp_worker_seo      Up X minutes
sp_worker_apply    Up X minutes
sp_worker_backup   Up X minutes
sp_worker_ads      Up X minutes
sp_llm_worker      Up X minutes    8100/tcp
sp_ollama          Up X minutes    11434/tcp
```

---

## 2. Verificare logs (dovezi că rulează)

```bash
# Orchestratorul — vrei să vezi "Scheduler starting" + "Using Redis/RQ queues (real)"
docker logs --tail 200 sp_orchestrator

# Worker SEO — vrei să vezi că procesează joburi (RQ worker listening)
docker logs --tail 200 sp_worker_seo

# Worker Ads
docker logs --tail 200 sp_worker_ads

# Redis
docker logs --tail 50 sp_redis
```

---

## 3. Test: enqueue manual un job și verifică că worker-ul îl procesează

```bash
# Pune un job în coada "audit"
docker exec -it sp_orchestrator python -c "
from agent.common.redisq import get_queue
job = get_queue('audit').enqueue('agent.tasks.pre_gsc_audit.pre_gsc_audit_task', site_id='superparty')
print('Job ID:', job.id)
"

# Verifică câte joburi sunt în coadă (0 = procesate)
docker exec -it sp_redis redis-cli LLEN rq:queue:audit

# Urmărește log-ul worker-ului (ar trebui să apară jobul în ~seconds)
docker logs --tail 100 -f sp_worker_seo
```

---

## 4. Verificare cozi Redis (RQ)

```bash
# Lista tuturor cozilor
docker exec -it sp_redis redis-cli KEYS "rq:queue:*"

# Lungime cozi (0 = idle, >0 = joburi în așteptare)
for queue in seo_collect seo_index seo_plan ga4 audit apply backup ads_plan ads_draft; do
  echo -n "$queue: "
  docker exec sp_redis redis-cli LLEN rq:queue:$queue
done

# Workers activi (RQ)
docker exec -it sp_redis redis-cli SMEMBERS rq:workers
```

---

## 5. Upgrade fără downtime

```bash
# Pull ultima versiune din GitHub
git pull origin main

# Rebuild + restart DOAR containerele modificate (celelalte rămân UP)
docker compose -f docker-compose.multiagent.yml up -d --build --no-deps orchestrator worker_seo

# Sau restart complet (< 30s downtime pe agenți, site-ul (Vercel) nu e afectat)
docker compose -f docker-compose.multiagent.yml down
docker compose -f docker-compose.multiagent.yml up -d --build
```

---

## 6. Restart policy (nonstop)

Toate containerele au `restart: unless-stopped` în `docker-compose.multiagent.yml`.
Asta înseamnă că la reboot al serverului Hetzner, **docker trebuie pornit automat** și containerele pornesc singure.

**Verificare că Docker pornește la boot:**
```bash
systemctl is-enabled docker   # trebuie să fie "enabled"
# Dacă nu:
systemctl enable docker
```

**Opțional: systemd service pentru compose** (dacă Docker nu pornește automat compose la boot):

```ini
# /etc/systemd/system/superparty-agents.service
[Unit]
Description=SuperParty AI Agents
After=docker.service
Requires=docker.service

[Service]
WorkingDirectory=/path/to/superparty
ExecStart=/usr/bin/docker compose -f docker-compose.multiagent.yml up
ExecStop=/usr/bin/docker compose -f docker-compose.multiagent.yml down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activare
systemctl daemon-reload
systemctl enable superparty-agents
systemctl start superparty-agents
```

---

## 7. Config obligatorie (.env.agent)

```env
REDIS_URL=redis://sp_redis:6379
GSC_SERVICE_ACCOUNT_JSON={"type":"service_account",...}   # JSON complet
GA4_PROPERTY_ID=properties/XXXXXXXX                       # dacă ai GA4
```

> **Atenție**: Redis NU trebuie expus public. Verifică că în `docker-compose.multiagent.yml`
> serviciul `redis` NU are `ports: ["6379:6379"]` (sau are doar `127.0.0.1:6379:6379`).

---

## 8. Checklist post-deploy (10 teste rapide)

| # | Test | Comandă | Rezultat așteptat |
|---|------|---------|-------------------|
| 1 | Deploy Vercel green | GitHub PR → status check | ✅ Vercel = success |
| 2 | Redirect www | `curl -I https://superparty.ro/` | 301 → https://www.superparty.ro/ |
| 3 | Sitemap www | `curl -s https://www.superparty.ro/sitemap.xml \| head -5` | `<loc>https://www.superparty.ro/...` |
| 4 | Canonical pilon | `curl -s https://www.superparty.ro/animatori-petreceri-copii \| grep canonical` | `href="https://www.superparty.ro/animatori-petreceri-copii"` |
| 5 | Redirect WP /?p= | `curl -I "https://www.superparty.ro/?p=59"` | 301 → pagina corectă |
| 6 | JSON-LD valid | Schema validator pe pilon | 0 erori |
| 7 | Noindex pe hold | Pagina hold → `<meta name="robots" content="noindex">` | Nu apare în sitemap |
| 8 | Mobile hamburger | DevTools mobile 375px | Menu se deschide/închide |
| 9 | WA cu text | Click WA float | URL conține `?text=Data:` |
| 10 | GA4 events | DevTools Network → `/collect` | click_to_call, click_to_whatsapp |

---

## 9. Containere și cozi (arhitectură)

```
sp_redis ──────────────────────────────────────────────────┐
                                                            │ (Redis/RQ)
sp_orchestrator ─────── enqueue_daily() ──────────────────►│
                 └───── enqueue_weekly() ──────────────────►│
                                                            │
sp_worker_seo ◄─── queues: seo_collect, seo_index,        │
                            seo_plan, ga4, audit ◄─────────┘
sp_worker_apply ◄── queue: apply ◄────────────────────────┘
sp_worker_backup ◄── queue: backup ◄─────────────────────┘
sp_worker_ads ◄──── queues: ads_plan, ads_draft ◄────────┘
sp_llm_worker ◄──── HTTP (port 8100) ◄───────────────────┘
sp_ollama ◄──────── HTTP (port 11434) ◄──────────────────┘
```

> Joburile zilnice rulează la **03:00 UTC** (orchestrator).
> Joburile săptămânale rulează **Duminică 10:00 UTC** (SEO plan/apply prin cozi).
