# Secrets Rotation System — Setup Guide

## GitHub Secrets Required

Add these to GitHub → Settings → Secrets → Actions:

| Secret | Description | How to get |
|---|---|---|
| `DEPLOY_SSH_PRIVATE_KEY` | SSH private key for server access | `ssh-keygen -t ed25519 -C "gh-actions-deploy"` → add pub to server `~/.ssh/authorized_keys` |
| `GCP_ROTATION_SA_KEY` | SA JSON with `roles/iam.serviceAccountKeyAdmin` | GCP Console → IAM → Service Accounts → create key |
| `GCP_PROJECT` | `gen-lang-client-0203593088` | Fixed |
| `GA4_SA_EMAIL` | `superparty-seo-agent@...gserviceaccount.com` | Fixed |
| `META_APP_ID` | Facebook App ID | Meta Developers → Your App |
| `META_APP_SECRET` | Facebook App Secret | Meta Developers → Your App → Settings |
| `META_SHORT_LIVED_TOKEN` | Short-lived user token | [Graph API Explorer](https://developers.facebook.com/tools/explorer/) |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook | Already in .env.agent |
| `VERCEL_TOKEN_CREATED_AT` | Date you created current token | e.g. `2026-03-03` |
| `GITHUB_APP_ID` | GitHub App numeric ID | After creating App |
| `GITHUB_APP_PRIVATE_KEY` | Base64-encoded PEM | `base64 -w0 private-key.pem` |
| `GITHUB_INSTALLATION_ID` | Installation ID | GitHub App settings → Installations |

---

## GitHub App Creation (one-time)

1. Go to [GitHub Developer Settings](https://github.com/settings/apps) → New GitHub App
2. Name: `superparty-agent-app`
3. Permissions:
   - **Contents**: Read & write
   - **Pull requests**: Write
   - **Issues**: Write
   - **Checks**: Read
   - **Metadata**: Read
4. Where can this GitHub App be installed: **Only on this account**
5. Create → Download private key → Store as `GITHUB_APP_PRIVATE_KEY` GitHub Secret
6. Install App on `SuperPartyByAI/Superparty`
7. Note App ID + Installation ID

---

## Deploy SSH Key (one-time)

```bash
# On your local machine:
ssh-keygen -t ed25519 -C "gh-actions-deploy" -f ~/.ssh/gh_deploy -N ""

# Copy public key to server:
ssh root@46.225.182.127 "echo '$(cat ~/.ssh/gh_deploy.pub)' >> ~/.ssh/authorized_keys"

# Add private key content as GitHub Secret DEPLOY_SSH_PRIVATE_KEY
```

---

## Manual Rotation Schedule

| Secret | Rotation | Method |
|---|---|---|
| GA4 service account key | Monthly (auto) | GH Actions `rotate-ga4.yml` |
| Meta access token | Every 50 days (auto) | GH Actions `rotate-meta.yml` |
| Vercel token | Every 80 days (alert only) | Manual — follow GitHub Issue |
| GitHub App private key | Yearly (optional) | Manual |
| GITHUB_TOKEN PAT | Now → replaced by GitHub App | GitHub App tokens auto-expire 1h |

---

## Testing Rotation Manually

```bash
# Trigger manually in GitHub UI:
# Actions → Rotate GA4 Key → Run workflow

# Or locally (with .env loaded):
source .env.agent
bash scripts/rotate_ga4_key.sh
```
