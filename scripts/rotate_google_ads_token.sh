#!/usr/bin/env bash
# Google Ads OAuth refresh token renewal helper.
# Refresh tokens are long-lived but can be revoked. Run this if you get
# UNAUTHENTICATED errors. Requires: GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET in env.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-SuperPartyByAI/Superparty}"

echo "=== [GOOGLE ADS TOKEN] Check $(date -u) ==="

# Test current token
CUST_ID="${GOOGLE_ADS_CUSTOMER_ID:-}"
DEV_TOKEN="${GOOGLE_ADS_DEVELOPER_TOKEN:-}"
REFRESH_TOKEN="${GOOGLE_ADS_REFRESH_TOKEN:-}"
CLIENT_ID="${GOOGLE_ADS_CLIENT_ID:-}"
CLIENT_SECRET="${GOOGLE_ADS_CLIENT_SECRET:-}"

if [ -z "$REFRESH_TOKEN" ] || [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    echo "ERROR: Missing Google Ads credentials"
    gh issue create --repo="$REPO" \
        --title="Google Ads credentials missing" \
        --body="GOOGLE_ADS_CLIENT_ID, CLIENT_SECRET, or REFRESH_TOKEN not set in GH Secrets." || true
    exit 1
fi

# Exchange refresh token → access token to verify validity
RESP=$(curl -sS -X POST https://oauth2.googleapis.com/token \
    -d "client_id=${CLIENT_ID}" \
    -d "client_secret=${CLIENT_SECRET}" \
    -d "refresh_token=${REFRESH_TOKEN}" \
    -d "grant_type=refresh_token")

ACCESS_TOKEN=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null)
ERROR=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',''))" 2>/dev/null)

if [ -n "$ACCESS_TOKEN" ]; then
    echo "Google Ads OAuth token: VALID"
    TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    [ -n "${SLACK_WEBHOOK_URL:-}" ] && curl -sS -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\":white_check_mark: Google Ads OAuth token valid at ${TIMESTAMP}\"}" \
        "$SLACK_WEBHOOK_URL"
else
    echo "Google Ads OAuth token INVALID: $ERROR"
    echo "Manual re-auth required:"
    echo "1. Run: python3 scripts/google_ads_auth.py"
    echo "2. Update GOOGLE_ADS_REFRESH_TOKEN in GitHub Secrets"
    gh issue create --repo="$REPO" \
        --title="Google Ads OAuth token INVALID ($(date -u +%Y-%m-%d))" \
        --body="Error: ${ERROR}\n\nRe-run OAuth flow: open Google OAuth2 Playground or run \`scripts/google_ads_auth.py\`.\n\nThen update \`GOOGLE_ADS_REFRESH_TOKEN\` in GitHub Secrets." || true
    [ -n "${SLACK_WEBHOOK_URL:-}" ] && curl -sS -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\":red_circle: Google Ads OAuth token INVALID: ${ERROR} — check GitHub Issues\"}" \
        "$SLACK_WEBHOOK_URL"
    exit 1
fi
echo "=== [GOOGLE ADS TOKEN] Done ==="
