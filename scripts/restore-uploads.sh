#!/bin/bash
# scripts/restore-uploads.sh <archive.tar.gz> [dest_dir]
# Exemplu: bash scripts/restore-uploads.sh /srv/superparty_backups/uploads/uploads_20260305_120000.tar.gz
set -e

ARCHIVE="$1"
DEST="${2:-/srv/superparty/public/wp-content/uploads}"

if [ -z "$ARCHIVE" ] || [ ! -f "$ARCHIVE" ]; then
  echo "Usage: $0 <archive.tar.gz> [dest_dir]"
  echo "Archive not found: $ARCHIVE"
  exit 1
fi

echo "[restore] Restaurez $ARCHIVE -> $DEST"
mkdir -p "$DEST"
tar -xzf "$ARCHIVE" -C "$(dirname "$DEST")"
echo "[restore] Done."
