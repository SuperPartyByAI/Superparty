# Critical Fix Runbook

## When to Intervene
Fix ONLY if one of these occurs during the measurement window:

### 🔴 CRITICAL — Fix Immediately
1. **Page 404**: Any monitored page returns 404
2. **Wrong robots**: `noindex` appears on a page that should be `index, follow`
3. **Wrong canonical**: Canonical points to wrong URL or is missing
4. **Sitemap broken**: Sitemap endpoint returns non-200 or invalid XML
5. **Deploy regression**: Vercel deployment fails or serves old build
6. **Owner page loss**: SP `/animatori-petreceri-copii/` loses correct technical state

### 🟡 INVESTIGATE — Assess Before Acting
1. **Cannibalization signal**: Same query splits across 2+ brands
2. **Unexpected redirect**: Page starts redirecting unexpectedly
3. **Content drift**: Title/H1/meta changed accidentally

### 🟢 IGNORE — Normal During Measurement
1. **No impressions yet**: Normal for new pages (AN, WP)
2. **Low CTR**: Too early to judge
3. **Position fluctuation**: Normal Google behavior
4. **"Unknown URL" in GSC**: Expected for newly submitted pages

## Fix Procedure

### Step 1: Identify
```
python scripts/daily_monitor.py
```
Review output for ❌ or ⚠️ markers.

### Step 2: Diagnose
- Check Vercel deployment status
- Check git log for recent changes
- Verify the issue is not cached/transient

### Step 3: Fix
- Make the **smallest possible fix**
- Commit with message: `fix(critical): [description]`
- Push and verify Vercel deploys correctly
- Re-run monitoring script

### Step 4: Document
- Add entry to daily measurement report
- Note what changed and why

## Decision Matrix

| Issue | Severity | Action |
|-------|----------|--------|
| Page 404 on monitored URL | CRITICAL | Fix immediately |
| `noindex` regression | CRITICAL | Fix immediately |
| Canonical missing/wrong | CRITICAL | Fix immediately |
| Sitemap 404 | HIGH | Fix same day |
| Vercel build failure | HIGH | Redeploy |
| Title changed accidentally | MEDIUM | Fix if significant |
| New 404 on non-monitored page | LOW | Note, fix later |
| Low impressions | NONE | Expected, monitor |
