#!/bin/bash
# SuperParty Health Check - Production Grade v2
# Cron: */5 * * * * /srv/superparty/scripts/health_check.sh >> /var/log/superparty_health.log 2>&1

REPO="/srv/superparty"
STATUS_FILE="$REPO/reports/ops/status.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
ALERTS=()
ALL_OK=true

mkdir -p "$REPO/reports/ops"

# ─── 1. Docker containers ────────────────────────────────────────────────────
EXPECTED="sp_orchestrator sp_worker_seo sp_worker_ads sp_worker_apply sp_worker_backup sp_redis sp_ollama sp_llm_worker"
for name in $EXPECTED; do
    status=$(docker inspect --format='{{.State.Status}}' "$name" 2>/dev/null || echo "not_found")
    restarts=$(docker inspect --format='{{.RestartCount}}' "$name" 2>/dev/null || echo "0")
    if [ "$status" != "running" ]; then
        ALERTS+=("CRITICAL:$name=$status")
        ALL_OK=false
    elif [ "${restarts:-0}" -gt 5 ]; then
        ALERTS+=("WARNING:$name restart_loop=$restarts")
        ALL_OK=false
    fi
done

# ─── 2. Redis queues ─────────────────────────────────────────────────────────
for q in seo_collect seo_index seo_plan ga4 audit apply backup; do
    len=$(docker exec sp_redis redis-cli LLEN "rq:queue:$q" 2>/dev/null || echo "0")
    if [ "${len:-0}" -gt 10 ]; then
        ALERTS+=("WARNING:queue_$q=$len stuck")
        ALL_OK=false
    fi
done

# ─── 3. Redirect non-www -> www (301) ────────────────────────────────────────
REDIRECT_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 --max-redirs 0 "https://superparty.ro/animatori-petreceri-copii" 2>/dev/null)
REDIRECT_LOC=$(curl -sI --max-time 10 --max-redirs 0 "https://superparty.ro/animatori-petreceri-copii" 2>/dev/null | grep -i "^location:" | tr -d '\r\n' | sed 's/location: //i')
if [ "$REDIRECT_HTTP" != "301" ] || [[ "$REDIRECT_LOC" != *"www."* ]]; then
    ALERTS+=("CRITICAL:redirect=${REDIRECT_HTTP}_loc=${REDIRECT_LOC}")
    ALL_OK=false
fi

# ─── 4. Site www returns 200 ─────────────────────────────────────────────────
SITE_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://www.superparty.ro/animatori-petreceri-copii" 2>/dev/null)
if [ "$SITE_CODE" != "200" ]; then
    ALERTS+=("CRITICAL:site_www=HTTP_$SITE_CODE")
    ALL_OK=false
fi

# ─── 5. Sitemap count EXACT 88 ───────────────────────────────────────────────
SITEMAP_COUNT=$(curl -s --max-time 15 "https://www.superparty.ro/sitemap.xml" 2>/dev/null | grep -c "<loc>")
if [ "$SITEMAP_COUNT" -ne 88 ]; then
    ALERTS+=("WARNING:sitemap_count=${SITEMAP_COUNT}_expected=88")
    ALL_OK=false
fi

# ─── 6. robots.txt contains www sitemap ──────────────────────────────────────
ROBOTS=$(curl -s --max-time 10 "https://www.superparty.ro/robots.txt" 2>/dev/null)
if ! echo "$ROBOTS" | grep -q "www.superparty.ro/sitemap.xml"; then
    ALERTS+=("WARNING:robots_sitemap_not_www")
    ALL_OK=false
fi

# ─── 7. Canonical on pilon is www ────────────────────────────────────────────
CANONICAL=$(curl -s --max-time 15 "https://www.superparty.ro/animatori-petreceri-copii" 2>/dev/null | grep -i "canonical" | head -1)
if ! echo "$CANONICAL" | grep -q "www.superparty.ro"; then
    ALERTS+=("WARNING:canonical_not_www")
    ALL_OK=false
fi

# ─── 8. Telegram alert (optional) ────────────────────────────────────────────
if [ "$ALL_OK" = "false" ] && [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    MSG="[SuperParty HealthCheck] ALERT at $TIMESTAMP"$'\n'
    for a in "${ALERTS[@]}"; do MSG="$MSG- $a"$'\n'; done
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${MSG}" > /dev/null 2>&1
fi

# ─── 9. Write status.json ────────────────────────────────────────────────────
ALERT_JSON="["
first=true
for a in "${ALERTS[@]}"; do
    $first || ALERT_JSON+=","
    ALERT_JSON+="\"$a\""
    first=false
done
ALERT_JSON+="]"

cat > "$STATUS_FILE" << EOFSTATUS
{
  "timestamp": "$TIMESTAMP",
  "all_ok": $([ "$ALL_OK" = "true" ] && echo "true" || echo "false"),
  "site_www_http": "$SITE_CODE",
  "redirect_301_www": $([ "$REDIRECT_HTTP" = "301" ] && echo "true" || echo "false"),
  "sitemap_count": $SITEMAP_COUNT,
  "sitemap_exact_88": $([ "$SITEMAP_COUNT" -eq 88 ] && echo "true" || echo "false"),
  "robots_www": $(echo "$ROBOTS" | grep -q "www.superparty.ro/sitemap.xml" && echo "true" || echo "false"),
  "canonical_www": $(echo "$CANONICAL" | grep -q "www.superparty.ro" && echo "true" || echo "false"),
  "redirect_location": "$REDIRECT_LOC",
  "alerts": $ALERT_JSON
}
EOFSTATUS

# ─── 10. Log ─────────────────────────────────────────────────────────────────
echo "[$TIMESTAMP] all_ok=$ALL_OK site=$SITE_CODE redirect=$REDIRECT_HTTP sitemap=$SITEMAP_COUNT alerts=${#ALERTS[@]}"
for a in "${ALERTS[@]}"; do echo "[$TIMESTAMP] ALERT: $a"; done

exit $([ "$ALL_OK" = "true" ] && echo 0 || echo 1)
