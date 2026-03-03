#!/usr/bin/env bash
# Refresh Meta long-lived token (every 50 days).
# Long-lived tokens expire after 60 days; refresh at day 50 to be safe.
# Requires: META_APP_ID, META_APP_SECRET, META_SHORT_LIVED_TOKEN in GH Secrets
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-SuperPartyByAI/Superparty}"
SERVER="root@46.225.182.127"
ENV_FILE="/srv/superparty/.env.agent"
GRAPH="https://graph.facebook.com/v19.0"

echo "=== [META TOKEN REFRESH] Starting $(date -u) ==="

# 1. Exchange short-lived → long-lived token
echo "Exchanging Meta token..."
RESP=$(curl -sS "${GRAPH}/oauth/access_token?grant_type=fb_exchange_token\
&client_id=${META_APP_ID}&client_secret=${META_APP_SECRET}\
&fb_exchange_token=${META_SHORT_LIVED_TOKEN}")

NEW_TOKEN=$(echo "$RESP" | jq -r '.access_token // empty')
EXPIRY=$(echo "$RESP" | jq -r '.expires_in // "unknown"')

if [ -z "$NEW_TOKEN" ]; then
    ERR=$(echo "$RESP" | jq -r '.error.message // "unknown error"')
    echo "ERROR: $ERR"
    gh issue create --repo="$REPO" \
        --title="Meta token refresh FAILED" \
        --body="Error at $(date -u): ${ERR}\n\nFull response: ${RESP}"
    [ -n "${SLACK_WEBHOOK_URL:-}" ] && curl -sS -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\":red_circle: *Meta token refresh FAILED*: ${ERR}\"}" "$SLACK_WEBHOOK_URL"
    exit 1
fi
echo "New token obtained (expires in: $EXPIRY seconds)"

# 2. Update GitHub Secrets
echo "$NEW_TOKEN" | gh secret set META_ACCESS_TOKEN --repo="$REPO"
echo "GitHub Secret updated"

# 3. Update server .env.agent
ssh -o StrictHostKeyChecking=no "$SERVER" bash <<SSHEOF
python3 - <<PY
import re, pathlib
env_path = pathlib.Path('${ENV_FILE}')
content = env_path.read_text(encoding='utf-8') if env_path.exists() else ''
new_line = 'META_ACCESS_TOKEN=${NEW_TOKEN}'
if 'META_ACCESS_TOKEN=' in content:
    content = re.sub(r'^META_ACCESS_TOKEN=.*$', new_line, content, flags=re.MULTILINE)
else:
    content += '\n' + new_line + '\n'
env_path.write_text(content, encoding='utf-8')
print('env.agent updated')
PY
docker restart sp_worker_ads
echo "sp_worker_ads restarted"
SSHEOF

# 4. Alert success
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
MSG=":white_check_mark: *Meta token refreshed* at ${TIMESTAMP} (expires in ${EXPIRY}s, next rotation: ~50 days)"
[ -n "${SLACK_WEBHOOK_URL:-}" ] && curl -sS -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"${MSG}\"}" "$SLACK_WEBHOOK_URL"
echo "=== [META TOKEN REFRESH] Done ==="
