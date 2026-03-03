# Multi-site Onboarding Guide

## Adding a New Site

### 1. Create site config
```yaml
# agent/sites/<new_site_id>.yml
site_id: new_site
site_url: https://new-site.ro
repo: YourOrg/YourRepo
gsc_property: sc-domain:new-site.ro
ga4_property_id: "123456789"
content_dirs:
  - src/content
  - src/pages
seo:
  max_weekly_wave: 25
  min_conversions_gate: 5
  dedup_days: 14
monitoring:
  sitemap_url: https://new-site.ro/sitemap.xml
  ga4_fail_threshold: 2
ads:
  enabled: false
```

### 2. Add environment variables to .env.agent
```bash
# Site-specific (prefix with SITE_<SITE_ID>_ if sharing agent)
GA4_PROPERTY_ID_<SITE_ID>=<property_id>
GSC_PROPERTY_<SITE_ID>=sc-domain:new-site.ro
GITHUB_REPOSITORY_<SITE_ID>=YourOrg/YourRepo
```

### 3. Verify
```bash
docker exec -it sp_worker_seo python3 -c "
from agent.services.site_loader import load_sites
print(load_sites())
"
```

### 4. Reports location
All outputs namespaced: `reports/<site_id>/ga4/`, `reports/<site_id>/gsc/` etc.

## Secrets per site
- Each repo should have its own `GITHUB_TOKEN` and GSC/GA4 credentials
- Use Docker secrets or `.env.<site_id>` files
- Never mix credentials between sites in production
