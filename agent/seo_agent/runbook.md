# SEO Agent — Runbook (SOP)

## 1. Freeze Management

### Set freeze
```sql
UPDATE sites SET freeze_until = '2026-03-21T23:59:59Z' WHERE domain = 'superparty.ro';
```

### Remove freeze
```sql
UPDATE sites SET freeze_until = NULL WHERE domain = 'superparty.ro';
```

### Verify freeze status
```python
from agent.seo_agent.rules_engine import check_freeze, SiteContext
from datetime import datetime, timezone

site = SiteContext(domain="superparty.ro", freeze_until=datetime(2026,3,21,23,59,59,tzinfo=timezone.utc))
result = check_freeze(site)
print(result.to_dict())
# {allowed: False, reasons: ["Site superparty.ro is frozen until ..."]}
```

---

## 2. Owner Page Assignment

### Register new owner
```python
from agent.seo_agent.owner_mapper import OwnerMapper
mapper = OwnerMapper()
ok, msg = mapper.register_owner("animatopia.ro", "mascote si personaje", "/mascote", "Mascote | AT", "Mascote")
print(ok, msg)
```

### Check for conflicts
```python
conflicts = mapper.validate_no_conflicts()
print(conflicts)  # [] = no conflicts
```

---

## 3. PR Workflow

### Generate PR (dry-run)
```python
from agent.seo_agent.pr_generator import PRRequest, generate_pr
req = PRRequest(site_domain="animatopia.ro", head_term="mascote", slug="mascote")
result = generate_pr(req, repo_dir=".", dry_run=True)
print(result.branch_name, result.pr_body[:200])
```

### Approve PR
Update pr_queue status in Supabase: `open` → `approved` → `merged`

### Reject PR
Update pr_queue status: `open` → `rejected`

---

## 4. Monitoring

### Run owner_share check
```python
from agent.seo_agent.monitor import PageMetrics, calculate_owner_share, check_thresholds
metrics = [
    PageMetrics(url="/", impressions=354, clicks=0),
    PageMetrics(url="/animatori-petreceri-copii", impressions=223, clicks=3, ctr=0.013)
]
share = calculate_owner_share(metrics, "/animatori-petreceri-copii")
alert = check_thresholds(share)
print(f"owner_share={share.owner_share:.1%}, severity={alert.severity}")
```

### Alert thresholds
| Metric | Warning | Critical |
|--------|---------|----------|
| owner_share | < 60% target | < 30% minimum |
| CTR regression | — | > 15% drop |
| Clicks regression | > 15% drop | — |

---

## 5. Canary Rollout

### Start canary
1. Rules engine validates (freeze, uniqueness, links)
2. PR generated for canary site only (default: animatopia.ro)
3. Monitor for 72h
4. Evaluate: proceed / extend / rollback

### Decision criteria
- **Proceed**: owner_share ≥ 40% + no critical alerts
- **Extend**: warnings present or share not at target
- **Rollback**: critical alerts (share < 20%, CTR drop > 10%)

---

## 6. Emergency Rollback

### Trigger rollback
```python
from agent.seo_agent.rollback import RollbackRequest, execute_rollback
req = RollbackRequest(
    site_domain="animatopia.ro",
    pr_branch="agent/seo/animatopia-owner-mascote-202603150200",
    head_term="mascote si personaje",
    reason="CTR dropped 20%",
    severity="critical"
)
result = execute_rollback(req, repo_dir=".", dry_run=True)
print(result.steps_completed)
```

### Rollback steps (automatic)
1. Create revert branch
2. CDN purge (Vercel auto-purges)
3. Queue re-indexing requests
4. Audit log entry

---

## 7. Security

- **Credentials**: All in `.env` (SUPABASE_URL, SUPABASE_KEY, GITHUB_TOKEN, GSC keys)
- **Never commit**: `.env` is in `.gitignore`
- **Rotate**: If any key is exposed, rotate immediately in Supabase dashboard
- **RLS**: Enable Row Level Security for production (service_role key bypasses RLS)
- **Audit trail**: All agent actions logged in `audit_logs` table
