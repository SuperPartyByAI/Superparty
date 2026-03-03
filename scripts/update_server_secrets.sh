#!/usr/bin/env bash
# Update specific secrets on server .env.agent and restart minimal containers.
# Called by rotation jobs after updating GitHub Secrets.
# Usage: update_server_secrets.sh KEY=VALUE [KEY2=VALUE2 ...]
set -euo pipefail

ENV_FILE="/srv/superparty/.env.agent"
COMPOSE_FILE="/srv/superparty/docker-compose.multiagent.yml"

for arg in "$@"; do
    KEY="${arg%%=*}"
    VALUE="${arg#*=}"
    echo "Updating $KEY in .env.agent..."
    if grep -q "^${KEY}=" "$ENV_FILE" 2>/dev/null; then
        sed -i "s|^${KEY}=.*|${KEY}=${VALUE}|" "$ENV_FILE"
    else
        echo "${KEY}=${VALUE}" >> "$ENV_FILE"
    fi
done

chmod 600 "$ENV_FILE"
echo ".env.agent updated"

# Minimal restart: only workers that read secrets at startup
docker compose -f "$COMPOSE_FILE" up -d --no-deps --build sp_worker_seo sp_worker_apply sp_worker_ads 2>&1
echo "Workers restarted"
