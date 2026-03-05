#!/bin/bash
# scripts/test-restore.sh — Restore test periodic + smoke checks + metrici
# Cron: 0 3 * * 1  (luni, 03:00 AM noapte)
#   0 3 * * 1 bash /srv/superparty/scripts/test-restore.sh >> /var/log/superparty_restore_test.log 2>&1

set -e

BACKUP_DIR="${BACKUP_DIR:-/srv/superparty_backups/uploads}"
REPO_DIR="${REPO_DIR:-/srv/superparty}"
RESTORE_TMP="/tmp/superparty_restore_test_$$"
HISTORY_FILE="$REPO_DIR/reports/ops/restore_history.json"
SITE="https://www.superparty.ro"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
START_TS=$(date +%s)
FAIL=0
CHECKS_PASS=0
CHECKS_FAIL=0

mkdir -p "$REPO_DIR/reports/ops"
echo "[$TIMESTAMP] === SuperParty Restore Test START ==="

# Secrets (Telegram)
SECRETS_FILE="${SECRETS_FILE:-/etc/superparty-secrets}"
[ -f "$SECRETS_FILE" ] && source "$SECRETS_FILE"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

send_telegram() {
    local msg="$1"
    [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ] && return 0
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" -d "parse_mode=HTML" \
        --data-urlencode "text=${msg}" --max-time 10 > /dev/null 2>&1 || true
}

check() {
    local label="$1" result="$2"
    if [ "$result" = "ok" ]; then
        echo "[$TIMESTAMP] ✅ $label"; CHECKS_PASS=$((CHECKS_PASS + 1))
    else
        echo "[$TIMESTAMP] ❌ $label"; CHECKS_FAIL=$((CHECKS_FAIL + 1)); FAIL=1
    fi
}

# ── 1. Selectează arhivă ───────────────────────────────────────────────────────
ARCHIVE="${1:-$(ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -n1)}"
if [ -z "$ARCHIVE" ] || [ ! -f "$ARCHIVE" ]; then
    echo "[$TIMESTAMP] ERROR: Nicio arhivă găsită în $BACKUP_DIR"
    send_telegram "❌ <b>Restore Test FAIL</b> — $TIMESTAMP%0ANicio arhivă în $BACKUP_DIR"
    exit 1
fi
ARCHIVE_SIZE=$(du -sh "$ARCHIVE" | cut -f1)
echo "[$TIMESTAMP] Arhivă: $ARCHIVE ($ARCHIVE_SIZE)"

# ── 2. Restore în tmp ─────────────────────────────────────────────────────────
mkdir -p "$RESTORE_TMP"
TAR_START=$(date +%s)
tar -xzf "$ARCHIVE" -C "$RESTORE_TMP" 2>&1
TAR_END=$(date +%s)
RESTORE_TIME_S=$((TAR_END - TAR_START))
RESTORE_COUNT=$(find "$RESTORE_TMP" -type f | wc -l | tr -d ' ')
echo "[$TIMESTAMP] Restaurate: $RESTORE_COUNT fișiere în ${RESTORE_TIME_S}s"

# ── 3. Verificări structurale ─────────────────────────────────────────────────
for expected_dir in "2021/04" "2022/08" "2025/01" "catalog"; do
    found=$(find "$RESTORE_TMP" -type d -name "$expected_dir" 2>/dev/null | head -1)
    check "Dir $expected_dir" "$( [ -n "$found" ] && echo ok || echo fail )"
done

# ── 4. Fișiere hero critice ───────────────────────────────────────────────────
for f in "animatori-1.jpg" "animatori-copii-1.jpg" "ursitoare-la-botez.jpg" "catalog_batman_v2.png"; do
    found=$(find "$RESTORE_TMP" -name "$f" 2>/dev/null | head -1)
    check "Fișier hero: $f" "$( [ -n "$found" ] && echo ok || echo fail )"
done

# ── 5. Smoke check live ───────────────────────────────────────────────────────
for url in \
    "$SITE/wp-content/uploads/2021/04/animatori-1.jpg" \
    "$SITE/wp-content/uploads/2025/01/ursitoare-la-botez.jpg" \
    "$SITE/wp-content/uploads/catalog/catalog_batman_v2.png" \
    "$SITE/sitemap.xml" \
    "$SITE/galerie/"; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -L "$url" 2>/dev/null || echo "000")
    check "LIVE $CODE ${url##*/}" "$( [ "$CODE" = "200" ] && echo ok || echo fail )"
done

# ── 6. Cleanup ────────────────────────────────────────────────────────────────
rm -rf "$RESTORE_TMP"
END_TS=$(date +%s)
TOTAL_TIME=$((END_TS - START_TS))
echo "[$TIMESTAMP] Cleanup done. Total: ${TOTAL_TIME}s"

# ── 7. Scrie restore_history.json ─────────────────────────────────────────────
STATUS="$( [ "$FAIL" -eq 0 ] && echo "PASSED" || echo "FAILED" )"
ENTRY=$(python3 -c "
import json, os, sys
history_file='$HISTORY_FILE'
entry={
  'timestamp': '$TIMESTAMP',
  'archive': '$ARCHIVE',
  'archive_size': '$ARCHIVE_SIZE',
  'restore_files': $RESTORE_COUNT,
  'restore_time_s': $RESTORE_TIME_S,
  'total_time_s': $TOTAL_TIME,
  'checks_pass': $CHECKS_PASS,
  'checks_fail': $CHECKS_FAIL,
  'status': '$STATUS',
}
history=[]
if os.path.isfile(history_file):
    try:
        with open(history_file) as f: history=json.load(f)
    except: pass
history.append(entry)
# Păstrează ultimele 52 (1 an de rulări săptămânale)
history=history[-52:]
with open(history_file,'w') as f: json.dump(history,f,indent=2)
print(json.dumps(entry))
" 2>/dev/null || echo "{}")
echo "[$TIMESTAMP] Metrici scrise în $HISTORY_FILE"

# ── 8. Telegram notification ──────────────────────────────────────────────────
if [ "$FAIL" -eq 0 ]; then
    send_telegram "✅ <b>Restore Test PASSED</b> — $TIMESTAMP%0A📦 $ARCHIVE_SIZE | ⏱ ${TOTAL_TIME}s | ✅ $CHECKS_PASS checks"
    echo "[$TIMESTAMP] === RESTORE TEST PASSED ✅ ==="
    exit 0
else
    send_telegram "❌ <b>Restore Test FAILED</b> — $TIMESTAMP%0A📦 $ARCHIVE_SIZE | ✅ $CHECKS_PASS / ❌ $CHECKS_FAIL checks%0AVezi log: /var/log/superparty_restore_test.log"
    echo "[$TIMESTAMP] === RESTORE TEST FAILED ❌ ==="
    exit 1
fi
