# Multi-Agent Platform — Superparty

## Architecture

Docker Compose microservices on a single Hetzner host.

| Container | Role |
|-----------|------|
| `sp_redis` | Job queues (Redis/RQ) + locks |
| `sp_ollama` | Local LLM (llama3.2:3b) |
| `sp_llm_worker` | HTTP wrapper for Ollama (:8100) |
| `sp_orchestrator` | Daily 03:00 UTC + Weekly Sunday 10:00 UTC scheduler |
| `sp_worker_seo` | SEO collect/index/plan (queues: seo_collect, seo_index, seo_plan) |
| `sp_worker_apply` | Git PR automation (queue: apply) |
| `sp_worker_backup` | Daily backup (queue: backup) |
| `sp_worker_ads` | Ads draft manifests (queues: ads_plan, ads_draft) |

## Setup

```bash
cp .env.agent.example .env.agent
# Edit .env.agent with real values
docker compose -f docker-compose.multiagent.yml up -d --build
docker exec sp_ollama ollama pull llama3.2:3b
```

## Health check

```bash
curl http://localhost:8100/health
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## Manual trigger (example)

```bash
# Test backup
docker exec sp_worker_backup python3 -c "from agent.tasks.backup import daily_backup_task; print(daily_backup_task())"

# Test SEO collect (after adding GSC_SERVICE_ACCOUNT_JSON)
docker exec sp_worker_seo python3 -c "from agent.tasks.seo import seo_collect_task; print(seo_collect_task())"
```

## Workflows

- **Daily 03:00 UTC**: backup → seo_collect → seo_index → seo_plan(daily_small) → seo_apply
- **Weekly Sunday 10:00 UTC**: seo_plan(weekly_wave) → ads_plan

## PR-only pattern

All structural changes are created as Pull Requests. Only `sp_worker_apply` has GitHub access.
