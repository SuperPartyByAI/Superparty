#!/bin/bash
# scripts/test-restore.sh — Test periodic restore backup în directorul temporar + smoke checks
# Rulare: bash scripts/test-restore.sh [archive.tar.gz]
# Cron recomandat: 0 3 * * 1  (luni, 03:00 AM)
#   0 3 * * 1 bash /srv/superparty/scripts/test-restore.sh >> /var/log/superparty_restore_test.log 2>&1
set -e

BACKUP_DIR="${BACKUP_DIR:-/srv/superparty_backups/uploads}"
RESTORE_TMP="/tmp/superparty_restore_test_$$"
SITE="https://www.superparty.ro"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FAIL=0

echo "[$TIMESTAMP] === SuperParty Restore Test START ==="

# 1) Selectează cea mai recentă arhivă dacă nu e specificată
ARCHIVE="${1:-$(ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -n1)}"
if [ -z "$ARCHIVE" ] || [ ! -f "$ARCHIVE" ]; then
    echo "[$TIMESTAMP] ERROR: Nicio arhivă găsită în $BACKUP_DIR"
    exit 1
fi
echo "[$TIMESTAMP] Arhivă selectată: $ARCHIVE ($(du -sh "$ARCHIVE" | cut -f1))"

# 2) Restore în dir temporar
mkdir -p "$RESTORE_TMP"
echo "[$TIMESTAMP] Restore în $RESTORE_TMP ..."
tar -xzf "$ARCHIVE" -C "$RESTORE_TMP" 2>&1
RESTORE_COUNT=$(find "$RESTORE_TMP" -type f | wc -l | tr -d ' ')
echo "[$TIMESTAMP] Fișiere restaurate: $RESTORE_COUNT"

# 3) Verificări structurale pe arhivă restaurată
echo "[$TIMESTAMP] --- Verificări structurale ---"
for expected_dir in "2021/04" "2022/08" "2025/01" "catalog"; do
    if [ -d "$RESTORE_TMP/$expected_dir" ] || find "$RESTORE_TMP" -type d -name "$expected_dir" | grep -q .; then
        echo "[$TIMESTAMP] ✅ Dir $expected_dir există în arhivă"
    else
        echo "[$TIMESTAMP] ❌ Dir $expected_dir LIPSEȘTE din arhivă"
        FAIL=1
    fi
done

# 4) Verifică fișiere critice (hero images) sunt prezente în arhivă
echo "[$TIMESTAMP] --- Verificare fișiere hero ---"
HERO_FILES=(
    "2021/04/animatori-1.jpg"
    "2021/04/animatori-copii-1.jpg"
    "2025/01/ursitoare-la-botez.jpg"
    "catalog/catalog_batman_v2.png"
)
for f in "${HERO_FILES[@]}"; do
    found=$(find "$RESTORE_TMP" -name "$(basename "$f")" | head -1)
    if [ -n "$found" ]; then
        echo "[$TIMESTAMP] ✅ $f"
    else
        echo "[$TIMESTAMP] ❌ LIPSĂ: $f"
        FAIL=1
    fi
done

# 5) Smoke check live: hero images HEAD + sitemap + galerie
echo "[$TIMESTAMP] --- Smoke check live ---"
for url in \
    "$SITE/wp-content/uploads/2021/04/animatori-1.jpg" \
    "$SITE/wp-content/uploads/2025/01/ursitoare-la-botez.jpg" \
    "$SITE/wp-content/uploads/catalog/catalog_batman_v2.png" \
    "$SITE/sitemap.xml" \
    "$SITE/galerie/"; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -L "$url" 2>/dev/null || echo "000")
    if [ "$CODE" = "200" ]; then
        echo "[$TIMESTAMP] ✅ $CODE ${url##*/}"
    else
        echo "[$TIMESTAMP] ❌ $CODE $url"
        FAIL=1
    fi
done

# 6) Cleanup
rm -rf "$RESTORE_TMP"
echo "[$TIMESTAMP] Cleanup $RESTORE_TMP — done"

if [ "$FAIL" -eq 0 ]; then
    echo "[$TIMESTAMP] === RESTORE TEST PASSED ✅ ==="
    exit 0
else
    echo "[$TIMESTAMP] === RESTORE TEST FAILED ❌ — verifică output-ul de mai sus ==="
    exit 1
fi
