# Meta Ads Adapter — Superparty

## Purpose
Creates **PAUSED** campaigns from approved manifests. Publish is always manual.

## Required Environment Variables (.env.agent)
```
META_ACCESS_TOKEN=<long-lived user token or system user token>
META_AD_ACCOUNT=act_<numeric_id>
META_PAGE_ID=<facebook_page_id>
```

## Usage
```python
from agent.ads.meta_adapter import create_paused_campaign

manifest = {
    "site_id": "superparty",
    "campaign_name": "Superparty - Pachete Evenimente",
    "objective": "OUTCOME_TRAFFIC",
    "daily_budget_eur": 5.0,
    "landing_page": "https://superparty.ro/pachete",
    "targeting": {
        "age_min": 22, "age_max": 50,
        "geo_locations": {"cities": [{"key": "536713", "name": "Bucharest"}]}
    },
    "creatives": [
        {"title": "Pachete petreceri Bucuresti", "body": "Organizăm petreceri memorabile."}
    ]
}

result = create_paused_campaign(manifest)
print(result)
# {"ok": true, "campaign_id": "...", "status": "PAUSED"}
```

## Safety Rules
- ALL objects created with `status: PAUSED`
- UTM parameters auto-added to landing page URL
- Saved to `reports/ads_drafts/<site_id>/`
- To activate: go to Meta Ads Manager → change status manually
