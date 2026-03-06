import os
import json
from pathlib import Path
from datetime import date, timedelta
import logging

log = logging.getLogger(__name__)

def generate_weekly_report(site_id="superparty"):
    report_dir = Path(f"reports/{site_id}")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"enterprise_seo_weekly_{date.today()}.md"

    # Load GSC Data
    index_file = report_dir / "gsc" / "index.json"
    gsc_data = []
    if index_file.exists():
        try:
            gsc_data = json.loads(index_file.read_text(encoding='utf-8'))
        except Exception:
            pass
            
    # Load Apply Audit Logs for Unmapped
    audit_files = sorted(report_dir.glob("seo_apply_gsc_*.json"))
    unmapped_pages = set()
    for af in audit_files[-7:]: # last 7 days
        try:
            audit = json.loads(af.read_text(encoding='utf-8'))
            for item in audit.get("unmapped", []):
                unmapped_pages.add(item.get("page"))
        except Exception:
            pass

    # Sort GSC by impressions to find top CTR gaps
    gsc_data.sort(key=lambda x: x.get("impressions", 0), reverse=True)
    
    top_queries = gsc_data[:20]
    
    # Calculate average CTR for top 100
    top_100 = gsc_data[:100]
    avg_ctr = 0
    if top_100:
        total_clicks = sum(x.get("clicks", 0) for x in top_100)
        total_impressions = sum(x.get("impressions", 1) for x in top_100)
        avg_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0

    ctr_candidates = [
        q for q in top_100 
        if q.get("impressions", 0) > 20 and 
        ((q.get("clicks", 0) / q.get("impressions", 1)) * 100) < avg_ctr
    ]

    # Generate MD Let's build the strings safely
    lines = [
        f"# Enterprise SEO Weekly Report — {date.today()}",
        f"**Site:** {site_id} | **Average CTR (Top 100):** {avg_ctr:.2f}%",
        "",
        "## 1. Top 20 Local Queries (Performance)",
        "| Query | Page | Impressions | Clicks | Avg Position | Score |",
        "|-------|------|-------------|--------|--------------|-------|"
    ]
    
    for q in top_queries:
        pos = q.get("avg_position", 99)
        clicks = q.get("clicks", 0)
        imps = q.get("impressions", 0)
        score = q.get("local_intent_score", "-")
        page = q.get("page", "").replace("https://www.superparty.ro", "").replace("https://superparty.ro", "")
        lines.append(f"| {q.get('query','')} | {page} | {imps} | {clicks} | {pos} | {score} |")
        
    lines.extend([
        "",
        f"## 2. CTR Optimization Candidates (Below {avg_ctr:.2f}%)",
        "> Pagini locale ce fac impresii, dar pierd click-uri. Necesită Meta-Title tweaks / Emoticon-uri.",
        "| Query | Page | Impressions | CTR | Position |",
        "|-------|------|-------------|-----|----------|"
    ])
    
    for c in sorted(ctr_candidates, key=lambda x: x.get("impressions", 0), reverse=True)[:15]:
        imps = c.get("impressions", 1)
        clks = c.get("clicks", 0)
        ctr = (clks / imps) * 100
        pos = c.get("avg_position", 99)
        page = c.get("page", "").replace("https://www.superparty.ro", "")
        lines.append(f"| {c.get('query','')} | {page} | {imps} | {ctr:.2f}% | {pos} |")
        
    lines.extend([
        "",
        "## 3. Unmapped Pages (Resolver Gaps)",
        "> Următoarele URL-uri din GSC nu au fost găsite fizic pe disk (.astro/.mdx) în timpul Apply-ului Turbo."
    ])
    
    if unmapped_pages:
        for p in sorted(list(unmapped_pages))[:20]:
            lines.append(f"- `{p}`")
    else:
        lines.append("- *Toate rutele au fost rezolvate corect săptămâna aceasta.*")
        
    lines.extend([
        "",
        "## 4. GBP / Local Pack Operational Checklist",
        "- [ ] Răspuns recenzii la zi (<24h SLA) ?",
        "- [ ] 2x Postări GBP publicate săptămâna curentă (CTA spre `/animatori-petreceri-copii`) ?",
        "- [ ] Cel puțin 3 poze reale (fără fețe copii nesecurizate) adăugate ?",
        "- [ ] Trimis workflow de review request din T+24h la toate evenimentele săptămânii ?",
        "- [ ] Target de Outreach Local realizat (min 2 emails direct la grădinițe / săli de evenimente) ?"
    ])

    report_file.write_text("\\n".join(lines), encoding="utf-8")
    log.info(f"Weekly enterprise report generated at {report_file}")
    
    # Try to push PR if git_pr is available
    try:
        from agent.common.git_pr import git_commit_push_pr
        pr_url = git_commit_push_pr(
            branch=f"agent/seo-weekly-report-{date.today()}",
            commit_msg=f"docs(seo): weekly enterprise report {date.today()}",
            files=[str(report_file)],
            pr_title=f"📊 SEO Weekly Enterprise Report - {date.today()}",
            pr_body=f"Raport auto cu Top Queries, Gaps, CTR Drop și Local Pack Checklist."
        )
        return {"ok": True, "file": str(report_file), "pr": pr_url}
    except Exception as e:
        log.warning(f"Failed to push weekly report PR: {e}")
        return {"ok": True, "file": str(report_file), "error": str(e)}

if __name__ == "__main__":
    print(generate_weekly_report())
