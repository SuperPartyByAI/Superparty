#!/usr/bin/env bash
# Vercel token rotation helper (manual fallback — Vercel API doesn't support programmatic rotation).
# This script: checks token age, creates GitHub Issue + Slack alert if rotation needed.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-SuperPartyByAI/Superparty}"
TOKEN_MAX_AGE_DAYS=80  # alert if token is older than this
TOKEN_CREATED_AT="${VERCEL_TOKEN_CREATED_AT:-}"  # set in GH Secrets as ISO date (YYYY-MM-DD)

echo "=== [VERCEL TOKEN CHECK] Starting $(date -u) ==="

if [ -z "$TOKEN_CREATED_AT" ]; then
    echo "WARN: VERCEL_TOKEN_CREATED_AT not set — cannot check age"
    exit 0
fi

# Compute age in days
CREATED_TS=$(date -d "$TOKEN_CREATED_AT" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$TOKEN_CREATED_AT" +%s)
NOW_TS=$(date +%s)
AGE_DAYS=$(( (NOW_TS - CREATED_TS) / 86400 ))
echo "Token age: $AGE_DAYS days (threshold: $TOKEN_MAX_AGE_DAYS)"

if [ "$AGE_DAYS" -ge "$TOKEN_MAX_AGE_DAYS" ]; then
    echo "ACTION REQUIRED: Vercel token needs rotation!"
    TITLE="Vercel token rotation required (age: ${AGE_DAYS} days)"
    BODY="## Vercel Token Rotation Required\n\nToken created: ${TOKEN_CREATED_AT}\nAge: ${AGE_DAYS} days\n\n### Steps\n1. Go to [Vercel Tokens](https://vercel.com/account/tokens) → Create new token\n2. Update GitHub Secret: \`gh secret set VERCEL_TOKEN --repo=${REPO}\`\n3. Update \`.env.agent\` on server: \`sed -i 's/^VERCEL_TOKEN=.*/VERCEL_TOKEN=<new>/' /srv/superparty/.env.agent\`\n4. Restart workers: \`docker restart sp_worker_seo sp_worker_apply\`\n5. Update \`VERCEL_TOKEN_CREATED_AT\` secret to today's date\n6. Close this issue"
    gh issue create --repo="$REPO" --title="$TITLE" --body="$BODY" || true
    [ -n "${SLACK_WEBHOOK_URL:-}" ] && curl -sS -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\":warning: *${TITLE}* — check GitHub Issues for steps\"}" "$SLACK_WEBHOOK_URL"
else
    echo "Token OK (${AGE_DAYS}/${TOKEN_MAX_AGE_DAYS} days)"
fi
echo "=== [VERCEL TOKEN CHECK] Done ==="
