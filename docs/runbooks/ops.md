# Superparty Platform — Operations Runbook

## PR Review Checklist

Before merging any agent-generated PR:

- [ ] Files changed are only in allowed paths: `agent/**`, `reports/**` (output only), allowed frontmatter keys
- [ ] No body text of pages modified — only `title`, `description`, `meta_title`, `meta_description`
- [ ] Wave limit respected (≤25 files)
- [ ] CI `guardrails` workflow: green
- [ ] No secrets, credentials, or `.env` content in diff
- [ ] For Ads PRs: all objects have `status: PAUSED`
- [ ] For SEO PRs: verify LLM suggestions are factual (no guarantees/prices/availability)

---

## Restore Procedure

### 1. Restore .env.agent
```bash
# From backup
cp /root/backup_superparty/.env.agent.bak /srv/superparty/.env.agent
chmod 600 /srv/superparty/.env.agent
```

### 2. Restore repo to known state
```bash
cd /srv/superparty
git fetch origin
git reset --hard origin/main
git clean -fd -e .env.agent -e reports/ -e data/ -e ollama_data/
```

### 3. Rebuild stack
```bash
cd /srv/superparty
docker compose -f docker-compose.multiagent.yml up -d --build
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### 4. Verify
```bash
docker logs --tail 50 sp_orchestrator
docker exec -it sp_worker_seo python3 -c "from agent.tasks.ga4 import ga4_collect_task; print(ga4_collect_task('superparty', 7))"
```

---

## Ads Circuit-Breaker (Emergency Pause All)

If ads spend anomaly or unexpected activation:

### Option A — Via Meta Ads Manager
1. Go to Meta Ads Manager → Campaigns
2. Select all → Pause

### Option B — Via API (emergency)
```python
# Pause ALL ads in account
import os, urllib.request, json, urllib.parse

TOKEN = os.environ["META_ACCESS_TOKEN"]
ACCOUNT = os.environ["META_AD_ACCOUNT"]
URL = f"https://graph.facebook.com/v19.0/{ACCOUNT}/ads"

params = urllib.parse.urlencode({"access_token": TOKEN, "status": "PAUSED"})
req = urllib.request.Request(f"{URL}?{params}", method="POST")
print(urllib.request.urlopen(req).read())
```

### Option C — Revoke token
1. Go to Meta Developers → Apps → Your App → Tools → Access Tokens
2. Revoke the token
3. Update `META_ACCESS_TOKEN` in `.env.agent` with new restricted token
4. Restart workers: `docker compose restart sp_worker_ads`

---

## Escalation / Contact

| Issue | Action |
|---|---|
| Orchestrator crash loop | Check `docker logs sp_orchestrator`; if syntax error → `git reset --hard origin/main` + rebuild |
| GA4 data missing | Check service account Viewer role in GA4 property |
| GSC 0 rows | Verify `GSC_PROPERTY=sc-domain:<domain>` in `.env.agent` |
| Sitemap 404 | Check Vercel deploy (`vercel ls`, `vercel inspect`) |
| PR guardrails failing | Check `.github/workflows/agent-guardrails.yml` on GitHub Actions |
| Vercel deploy failing | Check `VERCEL_TOKEN` is valid, run `vercel --prod` manually |

---

## Daily Health Check (one-liner)
```bash
docker ps --format "table {{.Names}}\t{{.Status}}" && \
  docker logs --tail 5 sp_orchestrator && \
  curl -sI https://superparty.ro/sitemap.xml | head -2
```

## Useful Commands
```bash
# Restart all workers
docker compose -f /srv/superparty/docker-compose.multiagent.yml restart

# Manual GA4 collect
docker exec -it sp_worker_seo python3 -c "from agent.tasks.ga4 import ga4_collect_task; print(ga4_collect_task('superparty', 7))"

# Manual SEO plan
docker exec -it sp_worker_seo python3 -c "from agent.tasks.seo import seo_plan_task; print(seo_plan_task(mode='ga4_weekly_wave'))"

# Check monitoring
docker exec -it sp_worker_seo python3 -c "from agent.tasks.monitoring import run_checks; print(run_checks())"

# View latest GA4 report
ls -la /srv/superparty/reports/superparty/ga4/
cat $(ls -t /srv/superparty/reports/superparty/ga4/collect_*.json | head -1)
```
