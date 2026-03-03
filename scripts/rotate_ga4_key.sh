#!/usr/bin/env bash
# Rotate GA4 service account key monthly (run via GH Actions or manually).
# Requires: gcloud (authenticated with GCP_ROTATION_SA_KEY), gh CLI, SLACK_WEBHOOK_URL
set -euo pipefail

PROJECT="${GCP_PROJECT:-gen-lang-client-0203593088}"
SA_EMAIL="${GA4_SA_EMAIL:-superparty-seo-agent@${PROJECT}.iam.gserviceaccount.com}"
REPO="${GITHUB_REPOSITORY:-SuperPartyByAI/Superparty}"
KEY_FILE="$(mktemp --suffix=.json)"
SERVER="root@46.225.182.127"
ENV_FILE="/srv/superparty/.env.agent"

echo "=== [GA4 KEY ROTATE] Starting $(date -u) ==="
echo "SA: $SA_EMAIL"

cleanup() { rm -f "$KEY_FILE"; }
trap cleanup EXIT

# 1. Create new key
echo "Creating new SA key..."
gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SA_EMAIL" \
    --project="$PROJECT"

NEW_KEY_JSON=$(cat "$KEY_FILE" | jq -c .)
if [ -z "$NEW_KEY_JSON" ]; then
    echo "ERROR: empty key JSON"
    exit 1
fi

# 2. Update GitHub Secret
echo "Updating GitHub Secret..."
echo "$NEW_KEY_JSON" | gh secret set GA4_SERVICE_ACCOUNT_JSON --repo="$REPO"

# 3. Update .env.agent on server
echo "Updating server .env.agent..."
ESCAPED=$(echo "$NEW_KEY_JSON" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))" | sed "s/^'//;s/'$//")
ssh -o StrictHostKeyChecking=no "$SERVER" bash <<SSHEOF
python3 - <<'PY'
import re, pathlib, json, sys

env_path = pathlib.Path('${ENV_FILE}')
content = env_path.read_text(encoding='utf-8') if env_path.exists() else ''

new_line = 'GA4_SERVICE_ACCOUNT_JSON=${NEW_KEY_JSON}'
if 'GA4_SERVICE_ACCOUNT_JSON=' in content:
    content = re.sub(r'^GA4_SERVICE_ACCOUNT_JSON=.*$', new_line, content, flags=re.MULTILINE)
else:
    content += '\n' + new_line + '\n'
env_path.write_text(content, encoding='utf-8')
print('env.agent updated')
PY
docker restart sp_worker_seo
echo "sp_worker_seo restarted"
SSHEOF

# 4. Smoke test on server
echo "Running smoke test..."
sleep 5
RESULT=$(ssh -o StrictHostKeyChecking=no "$SERVER" \
    "docker exec sp_worker_seo python3 -c \"from agent.tasks.ga4 import ga4_collect_task; r=ga4_collect_task('superparty',7); print('ok' if r.get('ok') else 'fail')\"" 2>&1)
echo "Smoke test: $RESULT"

# 5. Alert
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
if echo "$RESULT" | grep -q "^ok"; then
    MSG=":white_check_mark: *GA4 key rotated* successfully at ${TIMESTAMP}"
else
    MSG=":red_circle: *GA4 key rotate smoke test FAILED* at ${TIMESTAMP}. Result: ${RESULT}"
    # Create GitHub Issue
    gh issue create --repo="$REPO" \
        --title="GA4 key rotation smoke test failed" \
        --body="Rotation ran at ${TIMESTAMP} but smoke test failed: ${RESULT}"
fi
[ -n "${SLACK_WEBHOOK_URL:-}" ] && curl -sS -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"${MSG}\"}" "$SLACK_WEBHOOK_URL"
echo "=== [GA4 KEY ROTATE] Done: $RESULT ==="
[ "$RESULT" = "ok" ] || exit 1
