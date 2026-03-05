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
SITEMAP_EXPECTED=89
if [ "${SITEMAP_COUNT:-0}" -ne "$SITEMAP_EXPECTED" ]; then
    ALERTS+=("WARNING: sitemap has $SITEMAP_COUNT URLs (expected exactly $SITEMAP_EXPECTED) — check for accidental additions or deletions")
    ALL_OK=false
fi

# ─── 4.b Gallery count check ─────────────────────────────────────────────
GALLERY_EXPECTED=49
GALLERY_COUNT=$(curl -s --max-time 15 "https://www.superparty.ro/galerie/" 2>/dev/null | grep -c "gg-item" || echo 0)
if [ "${GALLERY_COUNT:-0}" -lt "$GALLERY_EXPECTED" ]; then
    ALERTS+=("WARNING: gallery has $GALLERY_COUNT items (expected at ≥ $GALLERY_EXPECTED)")
    ALL_OK=false
fi

# ─── 4.c Hero images HEAD check (CRITICAL) ──────────────────────────────────
REPO_DIR="${REPO_DIR:-/srv/superparty}"
GALLERY_TS="$REPO_DIR/src/data/gallery.ts"
if [ -f "$GALLERY_TS" ]; then
    # Extrage primele 12 URL-uri (galleryHero) din gallery.ts
    HERO_URLS=$(grep -oE "https://www\.superparty\.ro/wp-content/uploads/[^'\",\` )>]+" "$GALLERY_TS" | head -n 12)
    for url in $HERO_URLS; do
        CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -L "$url" 2>/dev/null || echo "000")
        if [ "$CODE" != "200" ]; then
            ALERTS+=("CRITICAL: hero image returned $CODE — $url")
            ALL_OK=false
        fi
    done
fi

# ─── 5. Write status.json ────────────────────────────────────────────────────
ALERT_JSON=$(printf '%s\n' "${ALERTS[@]}" | python3 -c "import sys,json; lines=sys.stdin.read().splitlines(); print(json.dumps(lines))")
STATUS_JSON=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "all_ok": $( [ "$ALL_OK" = true ] && echo "true" || echo "false" ),
  "site": "$SITE_STATUS",
  "sitemap_count": $SITEMAP_COUNT,
  "gallery_count": ${GALLERY_COUNT:-0},
  "redirect": "$REDIRECT_CODE",
  "alerts": ${ALERT_JSON:-[]},
  "checked_at": "$TIMESTAMP"
}
EOF
)

echo "$STATUS_JSON" > "$STATUS_FILE"

# ─── 7. Telegram alert (opțional) ────────────────────────────────────────────
# Setează TELEGRAM_BOT_TOKEN și TELEGRAM_CHAT_ID în /etc/superparty-secrets sau env
# Sursă secrets dacă există:
SECRETS_FILE="${SECRETS_FILE:-/etc/superparty-secrets}"
if [ -f "$SECRETS_FILE" ]; then
    # shellcheck source=/dev/null
    source "$SECRETS_FILE"
fi

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

send_telegram() {
    local msg="$1"
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
        return 0  # Telegram neconfigurat — skip silentios
    fi
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "parse_mode=HTML" \
        --data-urlencode "text=${msg}" \
        --max-time 10 > /dev/null 2>&1 || true
}

if [ ${#ALERTS[@]} -gt 0 ]; then
    # Construieste mesajul grupat pe severity
    CRITICAL_LIST=$(printf '%s\n' "${ALERTS[@]}" | grep "^CRITICAL" | head -n 10)
    WARNING_LIST=$(printf '%s\n' "${ALERTS[@]}" | grep "^WARNING" | head -n 5)
    MSG="🚨 <b>SuperParty Alert — $TIMESTAMP</b>%0A"
    if [ -n "$CRITICAL_LIST" ]; then
        MSG+="❌ CRITICAL:%0A$(echo "$CRITICAL_LIST" | sed 's/CRITICAL: /• /g' | tr '\n' '|' | sed 's/|/%0A/g')%0A"
    fi
    if [ -n "$WARNING_LIST" ]; then
        MSG+="⚠️ WARNINGS:%0A$(echo "$WARNING_LIST" | sed 's/WARNING: /• /g' | tr '\n' '|' | sed 's/|/%0A/g')"
    fi
    send_telegram "$MSG"
else
    # All OK — trimite heartbeat la fiecare oră (min 0 sau via flag)
    MINUTE=$(date +%M)
    if [ "$MINUTE" = "00" ]; then
        send_telegram "✅ <b>SuperParty OK</b> — $TIMESTAMP%0Asitemap: $SITEMAP_COUNT gallery: ${GALLERY_COUNT:-?}"
    fi
fi

echo "[$TIMESTAMP] all_ok=$ALL_OK site=$SITE_STATUS sitemap=$SITEMAP_COUNT alerts=${#ALERTS[@]}"
if [ ${#ALERTS[@]} -gt 0 ]; then
    for alert in "${ALERTS[@]}"; do
        echo "[$TIMESTAMP] ALERT: $alert"
    done
fi

exit $( [ "$ALL_OK" = true ] && echo 0 || echo 1 )
