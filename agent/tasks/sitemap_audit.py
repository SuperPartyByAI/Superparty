"""sitemap_audit.py — verify sitemap.xml completeness and repair if needed."""
import re
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import date


def sitemap_audit_task(site_id="superparty", base_url="https://superparty.ro"):
    """
    1. Read public/sitemap.xml and verify each URL returns 200.
    2. Scan public/*.html for pages missing from sitemap.
    3. Generate corrected sitemap if differences found.
    4. Optionally ping IndexNow.
    """
    sitemap_path = Path("public/sitemap.xml")
    issues = []
    missing_from_sitemap = []
    broken_in_sitemap = []
    sitemap_urls = []

    # Parse existing sitemap
    if sitemap_path.exists():
        content = sitemap_path.read_text(encoding="utf-8", errors="ignore")
        sitemap_urls = re.findall(r"<loc>([^<]+)</loc>", content)
    else:
        issues.append({"issue": "sitemap_missing", "severity": "critical"})

    # Verify sample of sitemap URLs (max 20)
    checked = 0
    for url in sitemap_urls[:20]:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "SEO-Agent-SitemapAudit/1.0"},
                method="HEAD"
            )
            resp = urllib.request.urlopen(req, timeout=6)
            if resp.status >= 400:
                broken_in_sitemap.append({"url": url, "status": resp.status})
        except urllib.error.HTTPError as e:
            broken_in_sitemap.append({"url": url, "status": e.code})
        except Exception as ex:
            broken_in_sitemap.append({"url": url, "error": str(ex)[:60]})
        checked += 1

    # Check for HTML pages not in sitemap
    public_dir = Path("public")
    if public_dir.exists():
        html_files = list(public_dir.glob("**/*.html"))
        for hf in html_files:
            rel = str(hf).replace("public", "").replace("\\", "/")
            if rel.endswith("/index.html"):
                rel = rel[: -len("/index.html")] + "/"
            url = base_url.rstrip("/") + rel
            # Normalize
            if url not in sitemap_urls and url.replace("//", "/") not in [u.replace("//", "/") for u in sitemap_urls]:
                missing_from_sitemap.append(url)

    # Build corrected sitemap if needed
    corrected_sitemap = None
    if missing_from_sitemap or broken_in_sitemap:
        all_valid_urls = [u for u in sitemap_urls if u not in [b.get("url") for b in broken_in_sitemap]]
        all_valid_urls += missing_from_sitemap

        # Deduplicate
        seen = set()
        unique = []
        for u in all_valid_urls:
            if u not in seen:
                seen.add(u)
                unique.append(u)

        loc_entries = "\n".join(
            f"  <url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>"
            for u in unique
        )
        corrected_sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{loc_entries}
</urlset>"""

    # Write report
    report = {
        "date": str(date.today()),
        "sitemap_exists": sitemap_path.exists(),
        "urls_in_sitemap": len(sitemap_urls),
        "urls_verified": checked,
        "broken_in_sitemap": broken_in_sitemap,
        "missing_from_sitemap": missing_from_sitemap[:50],
        "issues": issues,
        "corrected_sitemap_generated": corrected_sitemap is not None,
    }

    report_dir = Path(f"reports/{site_id}/sitemap_audit")
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / f"sitemap_audit_{date.today()}.json"
    out.write_text(json.dumps(report, indent=2))

    # Save corrected sitemap for PR
    corrected_path = None
    if corrected_sitemap:
        corrected_path = report_dir / f"sitemap_corrected_{date.today()}.xml"
        corrected_path.write_text(corrected_sitemap)

    # Ping IndexNow if sitemap exists
    indexed_now = False
    try:
        key = "superparty-indexnow"  # simple key; ideally configurable
        ping_url = f"https://api.indexnow.org/indexnow?url={base_url}/sitemap.xml&key={key}"
        urllib.request.urlopen(ping_url, timeout=5)
        indexed_now = True
    except Exception:
        pass

    return {
        "ok": True,
        "urls_in_sitemap": len(sitemap_urls),
        "broken_in_sitemap": len(broken_in_sitemap),
        "missing_from_sitemap": len(missing_from_sitemap),
        "corrected_sitemap": str(corrected_path) if corrected_path else None,
        "indexnow_pinged": indexed_now,
        "report_file": str(out),
    }
