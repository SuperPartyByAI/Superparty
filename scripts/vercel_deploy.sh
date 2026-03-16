#!/usr/bin/env bash
set -euo pipefail

# ─── Vercel Multi-Domain Deploy ──────────────────────────────────────────
# Usage:
#   export VERCEL_TOKEN="..."
#   export SUPABASE_URL="https://cijvmpxctjnqniyfhlny.supabase.co"
#   export SUPABASE_KEY="..."
#   ./scripts/vercel_deploy.sh [domain1] [domain2] ...
#
# If no domains specified, deploys all 14 sites.
# ─────────────────────────────────────────────────────────────────────────

if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "❌ Set VERCEL_TOKEN in env"; exit 1
fi
if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_KEY:-}" ]; then
  echo "❌ Set SUPABASE_URL and SUPABASE_KEY in env"; exit 1
fi

ALL_DOMAINS=(
  "123party.ro"
  "animatopia.ro"
  "clubuldisney.ro"
  "divertix.ro"
  "joyparty.ro"
  "kassia.ro"
  "partymania.ro"
  "petreceritematice.ro"
  "planetparty.ro"
  "playparty.ro"
  "teraparty.ro"
  "universeparty.ro"
  "ursitoaremagice.ro"
  "youparty.ro"
)

DOMAINS=( "${@:-${ALL_DOMAINS[@]}}" )
if [ ${#DOMAINS[@]} -eq 0 ]; then
  DOMAINS=("${ALL_DOMAINS[@]}")
fi

REPORT_FILE="reports/vercel_deploy_$(date +%Y%m%d_%H%M%S).txt"
mkdir -p reports

echo "══════════════════════════════════════════════" | tee "$REPORT_FILE"
echo "  Vercel Multi-Domain Deploy — $(date)"        | tee -a "$REPORT_FILE"
echo "  Domains: ${#DOMAINS[@]}"                      | tee -a "$REPORT_FILE"
echo "══════════════════════════════════════════════" | tee -a "$REPORT_FILE"

for DOMAIN in "${DOMAINS[@]}"; do
  echo "" | tee -a "$REPORT_FILE"
  echo "━━━ Processing: $DOMAIN ━━━" | tee -a "$REPORT_FILE"

  # 1. Create project
  echo "  → Creating Vercel project..." | tee -a "$REPORT_FILE"
  npx vercel projects create "$DOMAIN" --token "$VERCEL_TOKEN" 2>&1 || echo "  (project may already exist)" | tee -a "$REPORT_FILE"

  # 2. Add domain
  echo "  → Adding domain to Vercel..." | tee -a "$REPORT_FILE"
  npx vercel domains add "$DOMAIN" --token "$VERCEL_TOKEN" 2>&1 || echo "  (domain may already exist)" | tee -a "$REPORT_FILE"

  # 3. Set env vars
  echo "  → Setting environment variables..." | tee -a "$REPORT_FILE"
  echo "$SUPABASE_URL" | npx vercel env add SUPABASE_URL production --token "$VERCEL_TOKEN" 2>&1 || true
  echo "$SUPABASE_KEY" | npx vercel env add SUPABASE_KEY production --token "$VERCEL_TOKEN" 2>&1 || true

  if [ -n "${GA4_MEASUREMENT_ID:-}" ]; then
    echo "$GA4_MEASUREMENT_ID" | npx vercel env add GA4_MEASUREMENT_ID production --token "$VERCEL_TOKEN" 2>&1 || true
  fi

  echo "  ✓ $DOMAIN — project created, domain added, env set" | tee -a "$REPORT_FILE"
  echo "  DNS: set nameservers to ns1.vercel-dns.com / ns2.vercel-dns.com" | tee -a "$REPORT_FILE"
  echo "" | tee -a "$REPORT_FILE"
done

echo "══════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "  DONE — ${#DOMAINS[@]} domains processed"     | tee -a "$REPORT_FILE"
echo "  Report saved: $REPORT_FILE"                   | tee -a "$REPORT_FILE"
echo ""
echo "▸ Next: update nameservers at Hosterion to:"
echo "  ns1.vercel-dns.com"
echo "  ns2.vercel-dns.com"
echo ""
echo "▸ Then: push code to trigger Vercel builds"
echo "══════════════════════════════════════════════"
