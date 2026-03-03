"""Pre-GSC growth audit: runs when no GSC data available.
Audits repo for missing/broken SEO elements and creates a PR."""
import json, os, re
from pathlib import Path
from datetime import date


def pre_gsc_audit_task(site_id="superparty"):
    """Audit site pages for SEO issues without needing GSC data."""
    issues = []
    pages_audited = 0

    # Find all HTML pages in dist/ or src/
    search_dirs = ["dist", "out", ".vercel/output", "src/pages", "src/content"]
    html_files = []
    for d in search_dirs:
        p = Path(d)
        if p.exists():
            html_files.extend(list(p.rglob("*.html"))[:200])
            html_files.extend(list(p.rglob("*.astro"))[:200])
            html_files.extend(list(p.rglob("*.md"))[:200])

    for fpath in html_files[:100]:
        pages_audited += 1
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel = str(fpath)

        # Check title
        title_match = re.search(r"<title>([^<]{1,200})</title>", content, re.IGNORECASE)
        if not title_match and not fpath.suffix == ".md":
            issues.append({"file": rel, "issue": "missing_title", "severity": "high"})
        elif title_match:
            title = title_match.group(1).strip()
            if len(title) < 10:
                issues.append({"file": rel, "issue": "title_too_short", "value": title, "severity": "medium"})
            if len(title) > 60:
                issues.append({"file": rel, "issue": "title_too_long", "chars": len(title), "severity": "low"})

        # Check meta description
        desc_match = re.search(r'<meta[^>]+name=["']description["'][^>]+content=["']([^"']{1,500})', content, re.IGNORECASE)
        if not desc_match and not fpath.suffix in (".md", ".astro"):
            issues.append({"file": rel, "issue": "missing_meta_description", "severity": "high"})
        elif desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 50:
                issues.append({"file": rel, "issue": "meta_description_too_short", "chars": len(desc), "severity": "medium"})

        # Check canonical
        if "<link" in content and "canonical" not in content.lower() and fpath.suffix == ".html":
            issues.append({"file": rel, "issue": "missing_canonical", "severity": "medium"})

        # Check for animatopia (forbidden brand)
        if "animatopia" in content.lower():
            issues.append({"file": rel, "issue": "forbidden_brand_animatopia", "severity": "critical"})

        # Check h1
        h1_count = len(re.findall(r"<h1[^>]*>", content, re.IGNORECASE))
        if h1_count > 1:
            issues.append({"file": rel, "issue": "multiple_h1", "count": h1_count, "severity": "medium"})

    # Also check sitemap
    sitemap = Path("public/sitemap.xml")
    if not sitemap.exists():
        issues.append({"file": "public/sitemap.xml", "issue": "missing_sitemap", "severity": "critical"})

    robots = Path("public/robots.txt")
    if not robots.exists():
        issues.append({"file": "public/robots.txt", "issue": "missing_robots", "severity": "high"})

    # Write report
    report_dir = Path(f"reports/{site_id}/seo_audit")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"pre_gsc_audit_{date.today()}.json"
    report = {
        "date": str(date.today()),
        "pages_audited": pages_audited,
        "total_issues": len(issues),
        "critical": [i for i in issues if i.get("severity") == "critical"],
        "high": [i for i in issues if i.get("severity") == "high"],
        "medium": [i for i in issues if i.get("severity") == "medium"],
        "low": [i for i in issues if i.get("severity") == "low"],
        "all_issues": issues,
    }
    report_file.write_text(json.dumps(report, indent=2, default=str))

    # Also write markdown summary
    md_lines = [
        f"# SEO Audit Report (pre-GSC) — {date.today()}",
        "",
        f"Pages audited: {pages_audited} | Issues: {len(issues)}",
        "",
    ]
    if issues:
        md_lines.append("## Critical Issues")
        for i in [x for x in issues if x.get("severity") == "critical"][:10]:
            md_lines.append(f"- **{i['issue']}** in `{i['file']}`")
        md_lines.append("")
        md_lines.append("## High Priority")
        for i in [x for x in issues if x.get("severity") == "high"][:10]:
            md_lines.append(f"- {i['issue']} in `{i['file']}`")
    else:
        md_lines.append("No issues found.")

    md_file = report_dir / f"pre_gsc_audit_{date.today()}.md"
    md_file.write_text("\n".join(md_lines))

    return {
        "ok": True,
        "note": "pre_gsc_audit",
        "pages_audited": pages_audited,
        "total_issues": len(issues),
        "critical": len([i for i in issues if i.get("severity") == "critical"]),
        "high": len([i for i in issues if i.get("severity") == "high"]),
        "report_file": str(report_file),
        "md_file": str(md_file),
    }
