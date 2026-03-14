#!/usr/bin/env python3
"""
SEO Measurement Window — Daily Monitoring Script
Checks HTTP status, robots, canonical, title, H1, and sitemap validity
for all 3 brands: Superparty, Animatopia, WowParty.

Usage: python scripts/daily_monitor.py
Output: Console report + optional JSON file

SAFE: Read-only. Does NOT modify any live pages.
"""

import json
import sys
import os
import re
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "monitoring_config.json")


class HeadParser(HTMLParser):
    """Extract robots, canonical, title, and H1 from HTML."""

    def __init__(self):
        super().__init__()
        self.robots = None
        self.canonical = None
        self.title = None
        self.h1 = None
        self._in_title = False
        self._in_h1 = False
        self._title_parts = []
        self._h1_parts = []
        self._in_head = False
        self._past_head = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "head":
            self._in_head = True
        elif tag == "title" and self._in_head:
            self._in_title = True
        elif tag == "meta" and self._in_head:
            name = attrs_dict.get("name", "").lower()
            if name == "robots":
                self.robots = attrs_dict.get("content", "")
        elif tag == "link" and self._in_head:
            if attrs_dict.get("rel", "").lower() == "canonical":
                self.canonical = attrs_dict.get("href", "")
        elif tag == "h1" and self._past_head and self.h1 is None:
            self._in_h1 = True

    def handle_endtag(self, tag):
        if tag == "head":
            self._in_head = False
            self._past_head = True
        elif tag == "title":
            if self._in_title:
                self.title = "".join(self._title_parts).strip()
            self._in_title = False
        elif tag == "h1":
            if self._in_h1:
                self.h1 = "".join(self._h1_parts).strip()
            self._in_h1 = False

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)
        if self._in_h1:
            self._h1_parts.append(data)


def fetch_page(url, timeout=15):
    """Fetch a URL and return (status_code, body_text)."""
    req = Request(url, headers={"User-Agent": "SEO-Monitor/1.0"})
    try:
        resp = urlopen(req, timeout=timeout)
        body = resp.read().decode("utf-8", errors="replace")
        return resp.status, body
    except HTTPError as e:
        return e.code, ""
    except (URLError, Exception) as e:
        return 0, str(e)


def check_page(base_url, page_config):
    """Check a single page and return a result dict."""
    path = page_config["path"]
    url = base_url.rstrip("/") + path
    is_sitemap = page_config.get("is_sitemap", False)

    result = {
        "url": url,
        "path": path,
        "priority": page_config.get("priority", "medium"),
        "issues": [],
        "status": None,
    }

    status, body = fetch_page(url)
    result["status"] = status

    if status != 200:
        result["issues"].append(f"HTTP {status} (expected 200)")
        return result

    if is_sitemap:
        if "<urlset" in body or "<sitemapindex" in body:
            url_count = body.count("<loc>")
            result["sitemap_urls"] = url_count
        else:
            result["issues"].append("Sitemap does not contain valid XML")
        return result

    # Parse HTML
    parser = HeadParser()
    try:
        parser.feed(body)
    except Exception:
        result["issues"].append("HTML parse error")
        return result

    result["robots"] = parser.robots
    result["canonical"] = parser.canonical
    result["title"] = parser.title
    result["h1"] = parser.h1

    # Check robots
    expected_robots = page_config.get("expected_robots")
    if expected_robots and parser.robots != expected_robots:
        result["issues"].append(
            f"robots='{parser.robots}' (expected '{expected_robots}')"
        )

    # Check H1
    expected_h1 = page_config.get("expected_h1")
    if expected_h1 and parser.h1 and expected_h1.lower() not in parser.h1.lower():
        result["issues"].append(f"H1 mismatch: '{parser.h1}' (expected '{expected_h1}')")

    # Check canonical exists
    if not parser.canonical:
        result["issues"].append("Missing canonical tag")

    # Check robots exists
    if not parser.robots:
        result["issues"].append("Missing robots meta tag")

    return result


def run_monitoring():
    """Run full monitoring across all brands."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_results = {}
    total_issues = 0
    total_pages = 0

    print("=" * 70)
    print(f"  SEO DAILY MONITOR — {timestamp}")
    print("=" * 70)

    for brand_key, brand_config in config.items():
        brand = brand_config["brand"]
        base_url = brand_config["base_url"]
        pages = brand_config["monitored_pages"]

        print(f"\n{'─' * 50}")
        print(f"  {brand.upper()} ({brand_config['role']})")
        print(f"{'─' * 50}")

        brand_results = []
        for page in pages:
            result = check_page(base_url, page)
            brand_results.append(result)
            total_pages += 1

            is_sitemap = page.get("is_sitemap", False)
            status_icon = "✅" if result["status"] == 200 else "❌"

            if is_sitemap:
                sitemap_count = result.get("sitemap_urls", "?")
                print(f"  {status_icon} {result['path']:40s} HTTP {result['status']}  sitemap: {sitemap_count} URLs")
            else:
                robots = result.get("robots", "n/a")
                print(f"  {status_icon} {result['path']:40s} HTTP {result['status']}  robots: {robots}")
                if result.get("canonical"):
                    print(f"     canonical: {result['canonical']}")
                if result.get("h1"):
                    h1_display = result["h1"][:60] + "..." if len(result.get("h1", "")) > 60 else result.get("h1", "")
                    print(f"     H1: {h1_display}")

            if result["issues"]:
                for issue in result["issues"]:
                    print(f"     ⚠️  {issue}")
                total_issues += len(result["issues"])

        all_results[brand_key] = brand_results

    # Summary
    print(f"\n{'=' * 70}")
    verdict = "PASS ✅" if total_issues == 0 else f"ISSUES FOUND ⚠️ ({total_issues})"
    print(f"  VERDICT: {verdict}")
    print(f"  Pages checked: {total_pages}")
    print(f"  Issues found: {total_issues}")
    print(f"{'=' * 70}")

    # Save JSON report
    report_dir = os.path.join(SCRIPT_DIR, "..", "monitoring_reports")
    os.makedirs(report_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(report_dir, f"monitor_{date_str}.json")
    report = {
        "timestamp": timestamp,
        "total_pages": total_pages,
        "total_issues": total_issues,
        "verdict": "PASS" if total_issues == 0 else "ISSUES",
        "results": all_results,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  Report saved: {report_path}")

    return total_issues


if __name__ == "__main__":
    issues = run_monitoring()
    sys.exit(1 if issues > 0 else 0)
