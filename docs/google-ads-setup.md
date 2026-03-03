# Google Ads — Setup Guide

## Required GitHub Secrets

| Secret | Description | How to get |
|---|---|---|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Developer token from MCC | Google Ads → Tools → API Center |
| `GOOGLE_ADS_CLIENT_ID` | OAuth2 client ID | GCP Console → Credentials → OAuth 2.0 |
| `GOOGLE_ADS_CLIENT_SECRET` | OAuth2 client secret | Same as above |
| `GOOGLE_ADS_REFRESH_TOKEN` | OAuth2 refresh token | Run `scripts/google_ads_auth.py` |
| `GOOGLE_ADS_CUSTOMER_ID` | Account ID (no dashes) | Google Ads account number |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | MCC ID (if using MCC) | Same format; leave blank if no MCC |

---

## Step 1: Google Ads Developer Token

1. Login to [Google Ads](https://ads.google.com) with manager account
2. **Tools & Settings** → **Setup** → **API Center**
3. Apply for developer token (test token available immediately)
4. Copy token → `GOOGLE_ADS_DEVELOPER_TOKEN`

---

## Step 2: Google Cloud OAuth2 Credentials

1. [GCP Console](https://console.cloud.google.com) → **APIs & Services** → **Library**
2. Enable: **Google Ads API**
3. **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
   - Type: **Desktop app** (or Web — add `urn:ietf:wg:oauth:2.0:oob` redirect URI)
   - Download JSON → extract `client_id` and `client_secret`

---

## Step 3: Get Refresh Token (one-time)

```bash
# On server or local machine:
GOOGLE_ADS_CLIENT_ID=your_client_id \
GOOGLE_ADS_CLIENT_SECRET=your_client_secret \
python3 scripts/google_ads_auth.py
```

Follow the URL → authorize → paste code → copy `GOOGLE_ADS_REFRESH_TOKEN`.

---

## Step 4: Add Secrets to .env.agent

```bash
echo 'GOOGLE_ADS_DEVELOPER_TOKEN=xxx' >> /srv/superparty/.env.agent
echo 'GOOGLE_ADS_CLIENT_ID=xxx.apps.googleusercontent.com' >> /srv/superparty/.env.agent
echo 'GOOGLE_ADS_CLIENT_SECRET=xxx' >> /srv/superparty/.env.agent
echo 'GOOGLE_ADS_REFRESH_TOKEN=1//xxx' >> /srv/superparty/.env.agent
echo 'GOOGLE_ADS_CUSTOMER_ID=1234567890' >> /srv/superparty/.env.agent
chmod 600 /srv/superparty/.env.agent
docker restart sp_worker_ads
```

---

## Step 5: Test

```bash
# Dry run
docker exec -it sp_worker_ads python3 -c \
  "from agent.tasks.ads_google import google_ads_plan_task; import json; print(json.dumps(google_ads_plan_task(dry_run=True), indent=2))"

# Create PAUSED campaign
docker exec -it sp_worker_ads python3 -c \
  "from agent.tasks.ads_google import google_ads_plan_task; import json; print(json.dumps(google_ads_plan_task(dry_run=False), indent=2))"
```

---

## Install google-ads library

```bash
docker exec sp_worker_ads pip install google-ads==33.0.0
# Or add to requirements.txt and rebuild:
echo "google-ads==33.0.0" >> /srv/superparty/requirements.txt
docker compose -f /srv/superparty/docker-compose.multiagent.yml up -d --build sp_worker_ads
```

---

## GA4 ↔ Google Ads Linking

1. **GA4 Admin** → Property → **Product Links** → **Google Ads Links**
2. Link Google Ads account → enable **Import conversions** + **Remarketing**
3. Verify `form_submit` / `cta_click` events are marked as conversions in GA4
4. In Google Ads → **Tools** → **Conversions** → confirm GA4 conversions imported
