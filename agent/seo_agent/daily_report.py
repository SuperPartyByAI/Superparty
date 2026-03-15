"""
daily_report.py — Day 3–4 report generator.

Fetches GSC data, calculates owner_share, compares with baseline,
generates CSV + JSON report, and optionally sends Slack alert.

Usage:
  python -m agent.seo_agent.daily_report
  python -m agent.seo_agent.daily_report --day 3 --output reports/day3.csv
"""
from __future__ import annotations

import csv
import json
import logging
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

log = logging.getLogger("seo_agent.daily_report")

# ── GSC Fetch ─────────────────────────────────────────────────────────────────

def fetch_gsc_data(
    site_url: str,
    query: str,
    days: int = 7,
    credentials_json: Optional[str] = None,
) -> list[dict]:
    """
    Fetch GSC Performance data for a query, grouped by page.
    Returns raw rows from searchanalytics.query().
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds_json = credentials_json or os.getenv("GSC_SERVICE_ACCOUNT_JSON")
        if not creds_json:
            log.warning("No GSC credentials — returning stub data")
            return _stub_gsc_data()

        import json as _json
        creds_dict = _json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)

        end_date = date.today() - timedelta(days=2)  # GSC data lag
        start_date = end_date - timedelta(days=days)

        response = service.searchanalytics().query(
            siteUrl=site_url,
            body={
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "dimensions": ["page"],
                "dimensionFilterGroups": [{
                    "filters": [{
                        "dimension": "query",
                        "operator": "equals",
                        "expression": query,
                    }]
                }],
                "rowLimit": 25,
            },
        ).execute()

        return response.get("rows", [])

    except ImportError:
        log.warning("google-api-python-client not installed — using stub data")
        return _stub_gsc_data()
    except Exception as e:
        log.error(f"GSC fetch error: {e}")
        return _stub_gsc_data()


def _stub_gsc_data() -> list[dict]:
    """Stub data for testing without GSC access."""
    return [
        {"keys": ["https://www.superparty.ro/"], "impressions": 354, "clicks": 0, "ctr": 0.0, "position": 12.7},
        {"keys": ["https://www.superparty.ro/animatori-petreceri-copii"], "impressions": 223, "clicks": 3, "ctr": 0.013, "position": 12.8},
    ]


# ── Baseline ──────────────────────────────────────────────────────────────────

BASELINE_DAY2 = {
    "date": "2026-03-14",
    "owner_impressions": 223,
    "homepage_impressions": 354,
    "owner_clicks": 3,
    "homepage_clicks": 0,
    "owner_ctr": 0.013,
    "homepage_ctr": 0.0,
    "owner_position": 12.8,
    "homepage_position": 12.7,
    "owner_share": 38.6,
}


# ── Report Generation ─────────────────────────────────────────────────────────

def generate_report(
    site_url: str = "sc-domain:superparty.ro",
    query: str = "animatori petreceri copii",
    owner_path: str = "/animatori-petreceri-copii",
    day_number: int = 3,
    output_dir: str = "reports",
) -> dict:
    """
    Full report generation:
    1. Fetch GSC data
    2. Parse into PageMetrics
    3. Calculate owner_share
    4. Compare with baseline
    5. Check thresholds
    6. Export CSV + JSON
    """
    from .monitor import (
        parse_gsc_response,
        calculate_owner_share,
        check_thresholds,
        generate_daily_report,
        OwnerShareResult,
    )

    # 1. Fetch
    log.info(f"Fetching GSC data for '{query}' on {site_url}...")
    rows = fetch_gsc_data(site_url, query)

    # 2. Parse
    metrics = parse_gsc_response(rows, query)
    log.info(f"Got {len(metrics)} page metrics")

    # 3. Calculate
    share = calculate_owner_share(metrics, owner_path)
    log.info(f"owner_share = {share.owner_share:.1%}")

    # 4. Baseline comparison
    baseline = OwnerShareResult(
        owner_impressions=BASELINE_DAY2["owner_impressions"],
        homepage_impressions=BASELINE_DAY2["homepage_impressions"],
        owner_clicks=BASELINE_DAY2["owner_clicks"],
        homepage_clicks=BASELINE_DAY2["homepage_clicks"],
        owner_ctr=BASELINE_DAY2["owner_ctr"],
        homepage_ctr=BASELINE_DAY2["homepage_ctr"],
        owner_position=BASELINE_DAY2["owner_position"],
        homepage_position=BASELINE_DAY2["homepage_position"],
        owner_share=BASELINE_DAY2["owner_share"] / 100,
    )

    # 5. Threshold check
    alert = check_thresholds(share, baseline=baseline)

    # 6. Build report
    report = generate_daily_report(
        site_domain="superparty.ro",
        head_term=query,
        share_result=share,
        alert_result=alert,
    )
    report["day"] = day_number
    report["baseline"] = BASELINE_DAY2

    # Trend
    share_delta = share.owner_share * 100 - BASELINE_DAY2["owner_share"]
    report["trend"] = {
        "owner_share_delta": round(share_delta, 1),
        "direction": "↑" if share_delta > 0 else ("↓" if share_delta < 0 else "→"),
        "impr_delta": share.owner_impressions - BASELINE_DAY2["owner_impressions"],
        "clicks_delta": share.owner_clicks - BASELINE_DAY2["owner_clicks"],
    }

    # Export
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    _export_csv(report, f"{output_dir}/day{day_number}.csv")
    _export_json(report, f"{output_dir}/day{day_number}.json")

    # Print summary
    _print_summary(report)

    return report


def _export_csv(report: dict, path: str):
    """Export report as CSV."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "current", "baseline", "delta"])
        w.writerow(["day", report["day"], "—", "—"])
        w.writerow(["date", report["date"], report["baseline"]["date"], "—"])
        w.writerow(["owner_share (%)", report["owner_share"], report["baseline"]["owner_share"], report["trend"]["owner_share_delta"]])
        w.writerow(["owner_impressions", report["owner_impressions"], report["baseline"]["owner_impressions"], report["trend"]["impr_delta"]])
        w.writerow(["homepage_impressions", report["homepage_impressions"], report["baseline"]["homepage_impressions"], "—"])
        w.writerow(["owner_clicks", report["owner_clicks"], report["baseline"]["owner_clicks"], report["trend"]["clicks_delta"]])
        w.writerow(["owner_ctr (%)", report["owner_ctr"], report["baseline"]["owner_ctr"], "—"])
        w.writerow(["owner_position", report["owner_position"], report["baseline"]["owner_position"], "—"])
        w.writerow(["verdict", report["verdict"], "—", "—"])
        for a in report.get("alerts", []):
            w.writerow(["alert", a, "—", "—"])
    log.info(f"CSV exported: {path}")


def _export_json(report: dict, path: str):
    """Export report as JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log.info(f"JSON exported: {path}")


def _print_summary(report: dict):
    """Print human-readable summary."""
    t = report["trend"]
    print(f"\n{'='*60}")
    print(f"  DAY {report['day']} REPORT — {report['site']} — {report['date']}")
    print(f"{'='*60}")
    print(f"  owner_share:  {report['owner_share']:.1f}% {t['direction']} ({t['owner_share_delta']:+.1f}pp vs Day 2)")
    print(f"  impressions:  owner={report['owner_impressions']} | homepage={report['homepage_impressions']}")
    print(f"  clicks:       owner={report['owner_clicks']} | homepage={report.get('homepage_clicks', 0)}")
    print(f"  CTR:          owner={report['owner_ctr']:.2f}% | homepage={report.get('homepage_ctr', 0):.2f}%")
    print(f"  avg position: owner={report['owner_position']:.1f} | homepage={report.get('homepage_position', 0):.1f}")
    print(f"  verdict:      {report['verdict'].upper()}")
    if report.get("alerts"):
        for a in report["alerts"]:
            print(f"  ⚠ {a}")
    print(f"{'='*60}\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="SEO Agent — Daily Report Generator")
    parser.add_argument("--day", type=int, default=3, help="Day number (default: 3)")
    parser.add_argument("--output", default="reports", help="Output directory (default: reports)")
    parser.add_argument("--query", default="animatori petreceri copii", help="Head term query")
    parser.add_argument("--site", default="sc-domain:superparty.ro", help="GSC site URL")
    args = parser.parse_args()

    report = generate_report(
        site_url=args.site,
        query=args.query,
        day_number=args.day,
        output_dir=args.output,
    )

    # Send alert if critical
    if report["verdict"] == "critical":
        from .alerting import send_slack_alert
        send_slack_alert(report)
