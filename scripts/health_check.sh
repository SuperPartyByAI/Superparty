#!/bin/bash
# SuperParty Health Check Script
# Cron: */5 * * * * /srv/superparty/scripts/health_check.sh >> /var/log/superparty_health.log 2>&1

REPO="/srv/superparty"
STATUS_FILE="$REPO/reports/ops/status.json"
LOG_FILE="/var/log/superparty_health.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
ALERTS=()
ALL_OK=true

mkdir -p "$REPO/reports/ops"

# ─── 1. Docker containers check ──────────────────────────────────────────────
EXPECTED_CONTAINERS="sp_orchestrator sp_worker_seo sp_worker_ads sp_worker_apply sp_worker_backup sp_redis sp_ollama sp_llm_worker"
CONTAINERS_STATUS="{}"
for name in $EXPECTED_CONTAINERS; do
    status=$(docker inspect --format='{{.State.Status}}' "$name" 2>/dev/null)
    restarts=$(docker inspect --format='{{.RestartCount}}' "$name" 2>/dev/null)
    if [ "$status" != "running" ]; then
        ALERTS+=("CRITICAL: $name is $status (not running)")
        ALL_OK=false
    elif [ "${restarts:-0}" -gt 5 ]; then
        ALERTS+=("WARNING: $name has $restarts restarts (restart loop?)")
        ALL_OK=false
    fi
done

# ─── 2. Redis queue lengths ───────────────────────────────────────────────────
QUEUES="seo_collect seo_index seo_plan ga4 audit apply backup"
QUEUE_STATUS="{}"
MAX_QUEUE_LENGTH=10
for q in $QUEUES; do
    len=$(docker exec sp_redis redis-cli LLEN "rq:queue:$q" 2>/dev/null)
    if [ "${len:-0}" -gt $MAX_QUEUE_LENGTH ]; then
        ALERTS+=("WARNING: queue $q has $len stuck jobs")
        ALL_OK=false
    fi
done

# ─── 3. Live site checks ─────────────────────────────────────────────────────
SITE_STATUS="unknown"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://www.superparty.ro/animatori-petreceri-copii" 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    SITE_STATUS="ok"
else
    SITE_STATUS="ERROR_$HTTP_CODE"
    ALERTS+=("CRITICAL: site returned HTTP $HTTP_CODE")
    ALL_OK=false
fi

REDIRECT_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -L0 "https://superparty.ro/" 2>/dev/null)
REDIRECT_LOCATION=$(curl -sI --max-time 10 "https://superparty.ro/" 2>/dev/null | grep -i "^location:" | tr -d '\r')

# ─── 4. Sitemap check ────────────────────────────────────────────────────────
SITEMAP_COUNT=$(curl -s --max-time 15 "https://www.superparty.ro/sitemap.xml" 2>/dev/null | grep -c "<loc>")
SITEMAP_STATUS="ok_$SITEMAP_COUNT"
if [ "${SITEMAP_COUNT:-0}" -lt 80 ]; then
    ALERTS+=("WARNING: sitemap only has $SITEMAP_COUNT URLs (expected 88)")
    ALL_OK=false
fi

# ─── 5. Write status.json ────────────────────────────────────────────────────
ALERT_JSON=$(printf '%s\n' "${ALERTS[@]}" | python3 -c "import sys,json; lines=sys.stdin.read().splitlines(); print(json.dumps(lines))")
STATUS_JSON=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "all_ok": $( [ "$ALL_OK" = true ] && echo "true" || echo "false" ),
  "site": "$SITE_STATUS",
  "sitemap_count": $SITEMAP_COUNT,
  "redirect": "$REDIRECT_CODE",
  "alerts": ${ALERT_JSON:-[]},
  "checked_at": "$TIMESTAMP"
}
EOF
)

echo "$STATUS_JSON" > "$STATUS_FILE"

# ─── 6. Log summary ──────────────────────────────────────────────────────────
echo "[$TIMESTAMP] all_ok=$ALL_OK site=$SITE_STATUS sitemap=$SITEMAP_COUNT alerts=${#ALERTS[@]}"
if [ ${#ALERTS[@]} -gt 0 ]; then
    for alert in "${ALERTS[@]}"; do
        echo "[$TIMESTAMP] ALERT: $alert"
    done
fi

exit $( [ "$ALL_OK" = true ] && echo 0 || echo 1 )
