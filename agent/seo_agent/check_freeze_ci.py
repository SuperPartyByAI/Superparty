"""
check_freeze_ci.py — CI-safe freeze gate.

Checks if a site is frozen. Exits non-zero if frozen,
blocking the CI canary job from proceeding.

Usage:
  python -m agent.seo_agent.check_freeze_ci superparty.ro
  python -m agent.seo_agent.check_freeze_ci animatopia.ro
"""
from __future__ import annotations

import os
import sys
import json
import logging
from datetime import datetime, timezone

log = logging.getLogger("seo_agent.check_freeze_ci")


def check_via_supabase(domain: str) -> tuple[bool, str]:
    """Check freeze via Supabase API (requires SUPABASE_URL + SUPABASE_KEY)."""
    try:
        import urllib.request

        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
        if not url or not key:
            return False, "SUPABASE_URL/KEY not set"

        api_url = f"{url}/rest/v1/sites?domain=eq.{domain}&select=domain,freeze_until"
        req = urllib.request.Request(
            api_url,
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        if not data:
            return False, f"Site {domain} not found in DB"

        site = data[0]
        freeze_until = site.get("freeze_until")
        if not freeze_until:
            return True, f"{domain}: no freeze set"

        freeze_dt = datetime.fromisoformat(freeze_until.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if freeze_dt > now:
            return False, f"{domain}: FROZEN until {freeze_until} (now: {now.isoformat()})"
        else:
            return True, f"{domain}: freeze expired at {freeze_until}"

    except Exception as e:
        return False, f"Error checking freeze: {e}"


def check_via_rules_engine(domain: str) -> tuple[bool, str]:
    """Check freeze via local rules engine (no DB needed)."""
    try:
        from .rules_engine import SiteContext, check_freeze

        # Known freeze dates (fallback)
        known_freezes = {
            "superparty.ro": datetime(2026, 3, 21, 23, 59, 59, tzinfo=timezone.utc),
        }

        freeze_until = known_freezes.get(domain)
        site = SiteContext(domain=domain, freeze_until=freeze_until)
        result = check_freeze(site)

        if result.allowed:
            return True, f"{domain}: not frozen"
        else:
            return False, f"{domain}: {'; '.join(result.reasons)}"

    except Exception as e:
        return False, f"Rules engine error: {e}"


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(sys.argv) < 2:
        print("Usage: python -m agent.seo_agent.check_freeze_ci <domain>")
        print("Example: python -m agent.seo_agent.check_freeze_ci animatopia.ro")
        sys.exit(2)

    domain = sys.argv[1]

    # Try Supabase first, fall back to rules engine
    ok, msg = check_via_supabase(domain)
    if "not set" in msg or "Error" in msg:
        log.info(f"Supabase unavailable ({msg}), trying rules engine...")
        ok, msg = check_via_rules_engine(domain)

    if ok:
        print(f"✅ FREEZE CHECK PASSED: {msg}")
        sys.exit(0)
    else:
        print(f"🚫 FREEZE CHECK FAILED: {msg}")
        print("Canary deployment BLOCKED — site is in measurement window.")
        sys.exit(1)


if __name__ == "__main__":
    main()
