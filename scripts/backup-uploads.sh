#!/bin/bash
# scripts/backup-uploads.sh — arhivă incrementală a public/wp-content/uploads
# Rulare: bash scripts/backup-uploads.sh
set -e

SRC="${SRC_DIR:-/srv/superparty/public/wp-content/uploads}"
BACKUP_DIR="${BACKUP_DIR:-/srv/superparty_backups/uploads}"
KEEP="${KEEP_LAST:-7}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

ARCHIVE="$BACKUP_DIR/uploads_${TIMESTAMP}.tar.gz"
echo "[backup] Arhivez $SRC -> $ARCHIVE"
tar -czf "$ARCHIVE" -C "$(dirname "$SRC")" "$(basename "$SRC")"
echo "[backup] Arhivă creată: $ARCHIVE ($(du -sh "$ARCHIVE" | cut -f1))"

# Rotație: păstrează ultimele $KEEP arhive
COUNT=$(ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
if [ "$COUNT" -gt "$KEEP" ]; then
  ls -1t "$BACKUP_DIR"/*.tar.gz | tail -n "+$((KEEP+1))" | xargs -r rm -f
  echo "[backup] Rotație: păstrate ultimele $KEEP arhive"
fi

echo "[backup] Done."
