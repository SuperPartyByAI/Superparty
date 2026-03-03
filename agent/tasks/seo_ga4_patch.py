"""seo_ga4_patch.py - GA4-driven SEO plan and apply tasks."""
import json
import os
import re
import logging
from datetime import date
from pathlib import Path

log = logging.getLogger(__name__)


def seo_plan_ga4_wave(site_id="superparty", mode="ga4_weekly_wave"):
    """GA4-driven SEO planner: selects top converting pages and drafts title/desc improvements."""
    from agent.tasks.ga4_planner import (
        load_latest_ga4_report, select_top_pages_from_ga4,
        resolve_pagepath_to_file, MAX_WEEKLY_WAVE
    )

    ga4_data = load_latest_ga4_report(site_id)
    if not ga4_data:
        return {"ok": True, "note": "no_ga4_report_yet"}

    top_pages = select_top_pages_from_ga4(ga4_data, limit=MAX_WEEKLY_WAVE)
    if not top_pages:
        return {"ok": True, "note": "no_ga4_conversions_yet"}

    content_dirs = ["src/content", "src/pages", "content", "pages", "src"]
    plan = []
    unmapped = []

    ollama_url = os.environ.get("OLLAMA_URL", "http://sp_ollama:11434")
    llm_model = os.environ.get("LLM_MODEL", "llama3.1:8b")

    for page_info in top_pages:
        page_path = page_info["pagePath"]
        fpath, reason = resolve_pagepath_to_file(page_path, content_dirs)

        if fpath is None:
            unmapped.append({"pagePath": page_path, "reason": reason})
            continue

        # Read current frontmatter
        fm = {}
        try:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
            fm_m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
            if fm_m:
                for line in fm_m.group(1).split("\n"):
                    kv = re.match(r"^([\w_-]+):\s*(.*)", line)
                    if kv:
                        fm[kv.group(1).strip()] = kv.group(2).strip().strip("\"'")
        except Exception:
            pass

        current_title = fm.get("title", fm.get("meta_title", ""))
        current_desc = fm.get("description", fm.get("meta_description", ""))

        suggested_title = None
        suggested_desc = None

        # Call LLM for suggestions
        try:
            import urllib.request as ureq
            prompt = (
                f"You are an SEO expert for a Romanian website.\n"
                f"Page path: {page_path}\n"
                f"Current title: \"{current_title}\"\n"
                f"Current description: \"{current_desc}\"\n\n"
                f"This page has high converting traffic. Generate EXACTLY this JSON (no markdown):\n"
                f'{{\"title\": \"max 60 chars, Romanian, factual\", '
                f'\"description\": \"max 155 chars, Romanian, factual\"}}\n\n'
                f"Rules: factual only, no guarantees, no testimonials, no prices, "
                f"use natural Romanian keywords."
            )
            payload = json.dumps({
                "model": llm_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 200}
            }).encode()
            req = ureq.Request(
                f"{ollama_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            resp = ureq.urlopen(req, timeout=30)
            raw = json.loads(resp.read()).get("response", "")
            json_m = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
            if json_m:
                sugg = json.loads(json_m.group(0))
                suggested_title = sugg.get("title", "").strip()[:60]
                suggested_desc = sugg.get("description", "").strip()[:155]
        except Exception as e:
            log.warning(f"LLM failed for {page_path}: {e}")

        plan.append({
            "pagePath": page_path,
            "file": str(fpath),
            "conversions": page_info["conversions"],
            "current_title": current_title,
            "current_desc": current_desc,
            "suggested_title": suggested_title,
            "suggested_desc": suggested_desc,
            "match_reason": reason,
        })

    plan_data = {
        "date": str(date.today()),
        "mode": mode,
        "site_id": site_id,
        "total": len(plan),
        "unmapped_count": len(unmapped),
        "unmapped_paths": unmapped[:20],
        "items": plan,
    }

    plan_dir = Path(f"reports/{site_id}")
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plan_dir / f"seo_plan_ga4_{date.today()}.json"
    plan_file.write_text(json.dumps(plan_data, indent=2, ensure_ascii=False))

    return {
        "ok": True,
        "mode": mode,
        "plan_file": str(plan_file),
        "count": len(plan),
        "unmapped": len(unmapped),
    }


def seo_apply_ga4_plan(site_id="superparty"):
    """Apply the most recent GA4 SEO plan safely with allowlist + wave limits."""
    from agent.tasks.ga4_planner import safe_apply_frontmatter, MAX_WEEKLY_WAVE

    plan_dir = Path(f"reports/{site_id}")
    plan_files = sorted(plan_dir.glob("seo_plan_ga4_*.json"), reverse=True)
    if not plan_files:
        return {"ok": True, "note": "no_ga4_plan_file"}

    plan_file = plan_files[0]
    plan_data = json.loads(plan_file.read_text(encoding="utf-8"))
    items = plan_data.get("items", [])

    if not items:
        return {"ok": True, "note": "empty_ga4_plan"}

    applied = []
    skipped = []
    wave_count = 0

    for item in items[:MAX_WEEKLY_WAVE]:
        fpath_str = item.get("file")
        if not fpath_str:
            skipped.append({"pagePath": item.get("pagePath"), "reason": "no_file"})
            continue

        fpath = Path(fpath_str)
        if not fpath.exists():
            skipped.append({"pagePath": item.get("pagePath"), "reason": "file_not_found"})
            continue

        changed, reason = safe_apply_frontmatter(
            fpath,
            new_title=item.get("suggested_title"),
            new_description=item.get("suggested_desc"),
        )

        if changed:
            applied.append({"pagePath": item.get("pagePath"), "file": fpath_str, "change": reason})
            wave_count += 1
        else:
            skipped.append({"pagePath": item.get("pagePath"), "reason": reason})

        if wave_count >= MAX_WEEKLY_WAVE:
            break

    apply_report = {
        "date": str(date.today()),
        "plan_file": str(plan_file),
        "applied": applied,
        "skipped": skipped,
        "files_changed": wave_count,
    }

    apply_file = plan_dir / f"seo_apply_ga4_{date.today()}.json"
    apply_file.write_text(json.dumps(apply_report, indent=2, ensure_ascii=False))

    if not applied:
        return {"ok": True, "note": "no_changes_applied", "skipped": len(skipped)}

    # Create PR with changed files
    changed_files = {}
    for item in applied:
        fp = Path(item["file"])
        if fp.exists():
            changed_files[item["file"]] = fp.read_text(encoding="utf-8")
    changed_files[str(apply_file)] = apply_file.read_text()

    try:
        from agent.common.github_utils import create_pr
        pr_result = create_pr(
            site_id=site_id,
            title=f"SEO GA4 quick wins: {wave_count} pages improved ({date.today()})",
            body=(
                f"## GA4 SEO Quick Wins\n\n"
                f"Changes: {wave_count} files updated (title/description)\n"
                f"Plan: `{plan_file}`\n\n"
                + "\n".join(f"- `{a['file']}`: {a['change']}" for a in applied[:15])
            ),
            files=changed_files,
        )
        return {"ok": True, "files_changed": wave_count, "pr": pr_result}
    except Exception as e:
        log.error(f"PR creation failed: {e}")
        return {"ok": True, "files_changed": wave_count, "note": f"pr_error:{str(e)[:80]}"}
