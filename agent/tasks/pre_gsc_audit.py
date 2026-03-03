"""pre_gsc_audit.py — Enhanced pre-GSC SEO audit with duplicate detection and internal link analysis."""
import re
import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import date


def _read_html_pages(search_dirs=None):
    """Find all HTML/Astro/MD files in the site."""
    if search_dirs is None:
        search_dirs = ["dist", "out", "public", ".vercel/output", "src/pages", "src/content"]
    files = []
    for d in search_dirs:
        p = Path(d)
        if p.exists():
            files.extend(list(p.rglob("*.html"))[:200])
    return files[:300]


def pre_gsc_audit_task(site_id="superparty"):
    """
    Full pre-GSC audit:
    - Missing/duplicate titles, meta descriptions, canonicals
    - h1 count per page
    - Forbidden brand names
    - Internal linking analysis (pages with 0 inbound links)
    - noindex detection
    """
    html_files = _read_html_pages()
    pages_audited = 0
    issues = []

    # Per-page metadata
    page_data = {}  # path -> {title, description, canonical, h1_count, links_out, noindex}

    for fpath in html_files:
        pages_audited += 1
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel = str(fpath).replace("\\", "/")

        # Extract title
        title_match = re.search(r"<title[^>]*>([^<]{1,200})</title>", content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ""

        # Extract meta description
        desc_match = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']{1,500})',
            content, re.IGNORECASE
        )
        if not desc_match:
            desc_match = re.search(
                r'<meta[^>]+content=["\']([^"\']{1,500})["\'][^>]+name=["\']description["\']',
                content, re.IGNORECASE
            )
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract canonical
        canonical_match = re.search(
            r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',
            content, re.IGNORECASE
        )
        canonical = canonical_match.group(1).strip() if canonical_match else ""

        # Count h1
        h1_count = len(re.findall(r"<h1[^>]*>", content, re.IGNORECASE))

        # noindex
        noindex = bool(re.search(r'content=["\'][^"\']*noindex', content, re.IGNORECASE))

        # Extract outbound internal links
        links_out = re.findall(r'href=["\'](/[^"\'#?\s]{1,200})["\']', content)
        links_out = list(set(links_out))[:50]

        page_data[rel] = {
            "title": title,
            "description": description,
            "canonical": canonical,
            "h1_count": h1_count,
            "noindex": noindex,
            "links_out": links_out,
        }

        # Per-page issues
        if not title:
            issues.append({"file": rel, "issue": "missing_title", "severity": "high"})
        elif len(title) < 10:
            issues.append({"file": rel, "issue": "title_too_short", "value": title[:40], "severity": "medium"})
        elif len(title) > 70:
            issues.append({"file": rel, "issue": "title_too_long", "chars": len(title), "severity": "low"})

        if not description:
            issues.append({"file": rel, "issue": "missing_meta_description", "severity": "high"})
        elif len(description) < 50:
            issues.append({"file": rel, "issue": "meta_description_too_short", "chars": len(description), "severity": "medium"})
        elif len(description) > 160:
            issues.append({"file": rel, "issue": "meta_description_too_long", "chars": len(description), "severity": "low"})

        if not canonical:
            issues.append({"file": rel, "issue": "missing_canonical", "severity": "medium"})

        if h1_count == 0:
            issues.append({"file": rel, "issue": "missing_h1", "severity": "high"})
        elif h1_count > 1:
            issues.append({"file": rel, "issue": "multiple_h1", "count": h1_count, "severity": "medium"})

        # Forbidden brands
        for brand in ["animatopia", "animatopia.ro"]:
            if brand in content.lower():
                issues.append({"file": rel, "issue": f"forbidden_brand_{brand}", "severity": "critical"})

    # Duplicate title detection (cross-page)
    title_count = defaultdict(list)
    for rel, data in page_data.items():
        t = data.get("title", "").strip()
        if t:
            title_count[t].append(rel)

    dup_titles = []
    for t, pages in title_count.items():
        if len(pages) > 1:
            dup_titles.append({"title": t[:80], "pages": pages[:5], "count": len(pages)})
            for p in pages:
                issues.append({
                    "file": p,
                    "issue": "duplicate_title",
                    "title": t[:60],
                    "shared_with": len(pages) - 1,
                    "severity": "high"
                })

    # Internal link analysis: find pages with 0 inbound links (orphan pages)
    all_pages = set(page_data.keys())
    inbound = defaultdict(int)
    for rel, data in page_data.items():
        for link in data.get("links_out", []):
            # Find matching page
            for candidate in all_pages:
                if link in candidate or candidate.endswith(link.rstrip("/") + "/index.html"):
                    inbound[candidate] += 1

    orphan_pages = [p for p in all_pages if inbound[p] == 0 and len(page_data[p].get("title", "")) > 0]

    # Sort issues by severity
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    issues.sort(key=lambda x: sev_order.get(x.get("severity", "low"), 3))

    # Write report
    report = {
        "date": str(date.today()),
        "mode": "pre_gsc",
        "pages_audited": pages_audited,
        "total_issues": len(issues),
        "duplicate_titles": dup_titles,
        "orphan_pages": orphan_pages[:20],
        "critical": [i for i in issues if i.get("severity") == "critical"],
        "high": [i for i in issues if i.get("severity") == "high"],
        "medium": [i for i in issues if i.get("severity") == "medium"],
        "low": [i for i in issues if i.get("severity") == "low"],
    }

    report_dir = Path(f"reports/{site_id}/seo_audit")
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / f"pre_gsc_audit_{date.today()}.json"
    out.write_text(json.dumps(report, indent=2, default=str))

    # Markdown summary
    md = [
        f"# SEO Audit Report (pre-GSC) — {date.today()}",
        "",
        f"**Pages audited:** {pages_audited} | **Total issues:** {len(issues)}",
        f"**Critical:** {len(report['critical'])} | **High:** {len(report['high'])} | **Medium:** {len(report['medium'])}",
        "",
    ]
    if report["critical"]:
        md.append("## 🚨 Critical")
        for i in report["critical"][:5]:
            md.append(f"- **{i['issue']}** — `{i['file']}`")
        md.append("")
    if report["high"]:
        md.append("## ⚠️ High Priority")
        for i in report["high"][:10]:
            v = i.get("value", i.get("title", ""))
            suffix = f" ({v})" if v else ""
            md.append(f"- {i['issue']}{suffix} — `{i['file']}`")
        md.append("")
    if dup_titles:
        md.append("## 🔁 Duplicate Titles")
        for d in dup_titles[:5]:
            md.append(f"- `{d['title']}` — used in {d['count']} pages")
        md.append("")
    if orphan_pages:
        md.append("## 🔗 Orphan Pages (0 inbound links)")
        for p in orphan_pages[:10]:
            md.append(f"- `{p}`")

    md_file = report_dir / f"pre_gsc_audit_{date.today()}.md"
    md_file.write_text("\n".join(md))

    return {
        "ok": True,
        "note": "pre_gsc_audit",
        "pages_audited": pages_audited,
        "total_issues": len(issues),
        "critical": len(report["critical"]),
        "high": len(report["high"]),
        "medium": len(report["medium"]),
        "duplicate_titles": len(dup_titles),
        "orphan_pages": len(orphan_pages),
        "report_file": str(out),
        "md_file": str(md_file),
    }
