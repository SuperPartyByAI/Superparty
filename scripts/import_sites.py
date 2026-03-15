"""
import_sites.py — Import domains into Supabase sites table.

Reads from embedded inventory or CSV file.
Usage:
  python scripts/import_sites.py
  python scripts/import_sites.py --csv sites_inventory.csv
"""
from __future__ import annotations

import csv
import json
import logging
import os
import sys
import urllib.request
import urllib.error

log = logging.getLogger("import_sites")

# ── Full domain inventory ─────────────────────────────────────────────────────

SITES_INVENTORY = [
    # Original 3 (already seeded)
    {"domain": "superparty.ro", "name": "SuperParty", "brand": "SuperParty", "environment": "production", "freeze_until": "2026-03-21T23:59:59Z"},
    {"domain": "animatopia.ro", "name": "Animatopia", "brand": "Animatopia", "environment": "production"},
    {"domain": "wowparty.ro", "name": "WowParty", "brand": "WowParty", "environment": "production"},
    # 14 new domains
    {"domain": "123party.ro", "name": "123Party", "brand": "123Party", "environment": "production"},
    {"domain": "animaparty.ro", "name": "AnimaParty", "brand": "AnimaParty", "environment": "production"},
    {"domain": "clubuldisney.ro", "name": "ClubulDisney", "brand": "ClubulDisney", "environment": "production"},
    {"domain": "divertix.ro", "name": "Divertix", "brand": "Divertix", "environment": "production"},
    {"domain": "joyparty.ro", "name": "JoyParty", "brand": "JoyParty", "environment": "production"},
    {"domain": "kassia.ro", "name": "Kassia", "brand": "Kassia", "environment": "production"},
    {"domain": "partymania.ro", "name": "PartyMania", "brand": "PartyMania", "environment": "production"},
    {"domain": "petreceritematice.ro", "name": "PetreceriTematice", "brand": "PetreceriTematice", "environment": "production"},
    {"domain": "planetparty.ro", "name": "PlanetParty", "brand": "PlanetParty", "environment": "production"},
    {"domain": "playparty.ro", "name": "PlayParty", "brand": "PlayParty", "environment": "production"},
    {"domain": "teraparty.ro", "name": "TeraParty", "brand": "TeraParty", "environment": "production"},
    {"domain": "universeparty.ro", "name": "UniverseParty", "brand": "UniverseParty", "environment": "production"},
    {"domain": "ursitoaremagice.ro", "name": "UrsitoareMagice", "brand": "UrsitoareMagice", "environment": "production"},
    {"domain": "youparty.ro", "name": "YouParty", "brand": "YouParty", "environment": "production"},
]


def import_via_rest(sites: list[dict]) -> tuple[int, int, list[str]]:
    """Import sites via Supabase REST API (no supabase-py needed)."""
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        return 0, 0, ["SUPABASE_URL/KEY not set in environment"]

    api_url = f"{url}/rest/v1/sites"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",  # ON CONFLICT DO NOTHING
    }

    inserted = 0
    skipped = 0
    errors = []

    for site in sites:
        row = {
            "domain": site["domain"],
            "name": site["name"],
            "brand": site["brand"],
            "environment": site.get("environment", "production"),
        }
        if site.get("freeze_until"):
            row["freeze_until"] = site["freeze_until"]

        try:
            data = json.dumps(row).encode("utf-8")
            req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    inserted += 1
                    log.info(f"✅ {site['domain']}")
                else:
                    skipped += 1
                    log.info(f"⏭️  {site['domain']} (status {resp.status})")
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            if "duplicate" in body.lower() or e.code == 409:
                skipped += 1
                log.info(f"⏭️  {site['domain']} (already exists)")
            else:
                errors.append(f"{site['domain']}: HTTP {e.code} — {body[:200]}")
                log.error(f"❌ {site['domain']}: {e.code} {body[:200]}")
        except Exception as e:
            errors.append(f"{site['domain']}: {e}")
            log.error(f"❌ {site['domain']}: {e}")

    return inserted, skipped, errors


def import_via_sql_values(sites: list[dict]) -> str:
    """Generate SQL INSERT for manual execution in Supabase SQL Editor."""
    values = []
    for s in sites:
        freeze = f"'{s['freeze_until']}'" if s.get("freeze_until") else "NULL"
        values.append(
            f"  ('{s['domain']}', '{s['name']}', '{s['brand']}', "
            f"'{s.get('environment', 'production')}', {freeze})"
        )
    sql = "INSERT INTO sites (domain, name, brand, environment, freeze_until) VALUES\n"
    sql += ",\n".join(values)
    sql += "\nON CONFLICT (domain) DO NOTHING;"
    return sql


def load_csv(filepath: str) -> list[dict]:
    """Load sites from CSV file."""
    sites = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            site = {
                "domain": row["domain"].strip(),
                "name": row.get("name", row["domain"].split(".")[0]).strip(),
                "brand": row.get("brand", row["domain"].split(".")[0]).strip(),
                "environment": row.get("environment", "production").strip(),
            }
            if row.get("freeze_until"):
                site["freeze_until"] = row["freeze_until"].strip()
            sites.append(site)
    return sites


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Parse args
    sites = SITES_INVENTORY
    if len(sys.argv) > 1 and sys.argv[1] == "--csv":
        csv_path = sys.argv[2] if len(sys.argv) > 2 else "sites_inventory.csv"
        log.info(f"Loading from CSV: {csv_path}")
        sites = load_csv(csv_path)

    log.info(f"\n{'='*50}")
    log.info(f"  Importing {len(sites)} sites into Supabase")
    log.info(f"{'='*50}\n")

    # Try REST API first
    inserted, skipped, errors = import_via_rest(sites)

    log.info(f"\n{'='*50}")
    log.info(f"  Results: {inserted} inserted, {skipped} skipped, {len(errors)} errors")
    log.info(f"{'='*50}")

    if errors:
        log.info("\nErrors:")
        for e in errors:
            log.info(f"  ❌ {e}")

        # If REST fails, output SQL for manual execution
        log.info("\n\nFallback: copy this SQL into Supabase SQL Editor:\n")
        print(import_via_sql_values(sites))

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
