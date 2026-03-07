import os

os.chdir(r"C:\Users\ursac\Superparty")

with open('agent/tasks/seo.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add normalize_page_to_path below resolve_astro_path
norm_func = """
def normalize_page_to_path(page: str) -> str:
    import urllib.parse
    p = urllib.parse.unquote(page or "")
    p = p.replace("https://www.superparty.ro", "").replace("https://superparty.ro", "")
    p = p.split("?")[0]
    if not p.startswith("/"):
        p = "/" + p
    p = p.rstrip("/") if p != "/" else "/"
    return p
"""
text = text.replace("def resolve_astro_path(url_path):", norm_func + "\ndef resolve_astro_path(url_path):")

# 2. Add budgets right after state load
state_load = """    state_file = Path(f"reports/{site_id}/seo_apply_state.json")
    state = _load_apply_state(state_file)"""

budgets_inject = """    state_file = Path(f"reports/{site_id}/seo_apply_state.json")
    state = _load_apply_state(state_file)

    max_files_per_run = getenv_int("SEO_REAL_MAX_FILES_PER_RUN", getenv_int("SEO_REAL_MAX_FILES", 5))
    max_files_per_day = getenv_int("SEO_REAL_MAX_FILES_PER_DAY", 15)
    max_prs_per_day   = getenv_int("SEO_REAL_MAX_PRS_PER_DAY", 4)
    cooldown_days     = getenv_int("SEO_REAL_COOLDOWN_DAYS", 7)"""
text = text.replace(state_load, budgets_inject)

# 3. Handle early budget exits saving state
budget_exit_old = """    if state["files_applied_today"] >= max_files_per_day:
        return {"ok": True, "note": "budget_reached", "reason": "max_files_per_day"}
    if state["prs_created_today"] >= max_prs_per_day:
        return {"ok": True, "note": "budget_reached", "reason": "max_prs_per_day"}"""

budget_exit_new = """    if state["files_applied_today"] >= max_files_per_day:
        _save_apply_state(state_file, state)
        return {"ok": True, "note": "budget_reached", "reason": "max_files_per_day"}
    if state["prs_created_today"] >= max_prs_per_day:
        _save_apply_state(state_file, state)
        return {"ok": True, "note": "budget_reached", "reason": "max_prs_per_day"}"""
text = text.replace(budget_exit_old, budget_exit_new)


# 4. Refactor the application loop
# We replace:
#     for opp in opportunities:
#         url_path = opp.get("page", "")
#         fpath = resolve_astro_path(url_path)
#         if not fpath:
#             audit_log["unmapped"].append({"page": url_path, "reason": "not_resolved"})
#             continue
#             
#         # Check active experiment contamination
#         if db_con:
#             try:
#                 page_db_state = get_page_state(db_con, site_id, url_path)
#                 if page_db_state and page_db_state.get("active_exp_id"):
#                     audit_log["skipped"].append({"page": url_path, "reason": "active_experiment"})
#                     continue
#             except Exception:
#                 pass
#             
#         # COOLDOWN Check
#         last_applied_str = state["page_last_applied"].get(url_path)
#         if last_applied_str:
#             last_applied_date = datetime.strptime(last_applied_str, "%Y-%m-%d").date()
#             if (date.today() - last_applied_date).days < cooldown_days:
#                 audit_log["skipped"].append({"page": url_path, "reason": "cooldown"})
#                 continue
#             
#         clean_path = urllib.parse.unquote(url_path).replace("https://www.superparty.ro", "").replace("https://superparty.ro", "").split("?")[0].strip("/")

# WITH THE NEW PAGE_KEY BLOCK:

old_loop_start = """    for opp in opportunities:
        url_path = opp.get("page", "")
        fpath = resolve_astro_path(url_path)
        if not fpath:
            audit_log["unmapped"].append({"page": url_path, "reason": "not_resolved"})
            continue
            
        # Check active experiment contamination
        if db_con:
            try:
                page_db_state = get_page_state(db_con, site_id, url_path)
                if page_db_state and page_db_state.get("active_exp_id"):
                    audit_log["skipped"].append({"page": url_path, "reason": "active_experiment"})
                    continue
            except Exception:
                pass
            
        # COOLDOWN Check
        last_applied_str = state["page_last_applied"].get(url_path)
        if last_applied_str:
            last_applied_date = datetime.strptime(last_applied_str, "%Y-%m-%d").date()
            if (date.today() - last_applied_date).days < cooldown_days:
                audit_log["skipped"].append({"page": url_path, "reason": "cooldown"})
                continue
            
        clean_path = urllib.parse.unquote(url_path).replace("https://www.superparty.ro", "").replace("https://superparty.ro", "").split("?")[0].strip("/")"""

new_loop_start = """    try:
        pass
    finally:
        pass

    import urllib.parse
    for opp in opportunities:
        page_raw = opp.get("page", "")
        page_key = normalize_page_to_path(page_raw)
        fpath = resolve_astro_path(page_key)
        if not fpath:
            audit_log["unmapped"].append({"page": page_key, "raw": page_raw, "reason": "not_resolved"})
            continue
            
        # Check active experiment contamination
        if db_con:
            try:
                page_db_state = get_page_state(db_con, site_id, page_key)
                if page_db_state and page_db_state.get("active_exp_id"):
                    audit_log["skipped"].append({"page": page_key, "raw": page_raw, "reason": "active_experiment"})
                    continue
            except Exception:
                pass
            
        # COOLDOWN Check
        last_applied_str = state["page_last_applied"].get(page_key)
        if last_applied_str:
            last_applied_date = datetime.strptime(last_applied_str, "%Y-%m-%d").date()
            if (date.today() - last_applied_date).days < cooldown_days:
                audit_log["skipped"].append({"page": page_key, "raw": page_raw, "reason": "cooldown"})
                continue
            
        clean_path = page_key.strip("/")"""
text = text.replace(old_loop_start, new_loop_start)

# 5. Fix audit logs inside the rest of the loop
audit_applied_old = """audit_log["applied"].append({"page": url_path, "file": str(fpath), "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})"""
audit_applied_new = """audit_log["applied"].append({"page": page_key, "raw": page_raw, "file": str(fpath), "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})"""
text = text.replace(audit_applied_old, audit_applied_new)

state_last_app_old = """state["page_last_applied"][url_path] = str(date.today())"""
state_last_app_new = """state["page_last_applied"][page_key] = str(date.today())"""
text = text.replace(state_last_app_old, state_last_app_new)

audit_skipped_old = """audit_log["skipped"].append({"page": url_path, "reason": "failed_gate", "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})"""
audit_skipped_new = """audit_log["skipped"].append({"page": page_key, "raw": page_raw, "reason": "failed_gate", "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})"""
text = text.replace(audit_skipped_old, audit_skipped_new)

# 6. Save state in the end blocks
end_block_old = """    if not succes_count:
        return {"ok": True, "note": "no_pages_passed_gate", "audit": str(audit_file)}

    try:
        import time
        run_id = time.strftime("%H%M%S")
        pr_url = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}T{run_id}Z",
            commit_msg=f"feat(seo): gsc apply real {date.today()}T{run_id}Z",
            files=applied_files,
            pr_title=f"SEO Apply Real: {succes_count} pagini optimizate on-page ({date.today()})",
            pr_body=f"S-a folosit funcția llm deterministica de apply safe pentru modificari pe text.\\n\\nPagini îmbunătățite:\\n" + "\\n".join([f"- `{k}`" for k in applied_files])
        )
        # Remove old save blocks as we will overwrite them cleanly
        state["prs_created_today"] += 1
        _save_apply_state(state_file, state)
        
        return {"ok": True, "pr_url": pr_url}
    except Exception as e:
        return {"ok": False, "error": str(e), "files": applied_files}"""

# Re-read the file to check existing old block
fpath_str = text.split("if not succes_count:")[1] if "if not succes_count:" in text else ""

end_block_new = """    if not succes_count:
        _save_apply_state(state_file, state)
        return {"ok": True, "note": "no_pages_passed_gate", "audit": str(audit_file)}

    try:
        import time
        run_id = time.strftime("%H%M%S")
        pr_url = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}T{run_id}Z",
            commit_msg=f"feat(seo): gsc apply real {date.today()}T{run_id}Z",
            files=applied_files,
            pr_title=f"SEO Apply Real: {succes_count} pagini optimizate on-page ({date.today()})",
            pr_body=f"S-a folosit funcția llm deterministica de apply safe pentru modificari pe text.\\n\\nPagini îmbunătățite:\\n" + "\\n".join([f"- `{k}`" for k in applied_files])
        )
        state["prs_created_today"] += 1
        _save_apply_state(state_file, state)
        return {"ok": True, "pr_url": pr_url}
    except Exception as e:
        _save_apply_state(state_file, state)
        return {"ok": False, "error": str(e), "files": applied_files}"""

import re
text = re.sub(r'    if not succes_count:[\s\S]*return {"ok": False, "error": str\(e\), "files": applied_files}', end_block_new, text)


with open('agent/tasks/seo.py', 'w', encoding='utf-8') as f:
    f.write(text)
    
print("seo.py patched!")

# NOW for seo_ctr_experiments.py
with open('agent/tasks/seo_ctr_experiments.py', 'r', encoding='utf-8') as f:
    ctr_text = f.read()

# db_init injections
ctr_text = ctr_text.replace(
    '    con = db_connect()\n    active = list_active_experiments(con, site_id)',
    '    con = db_connect()\n    db_init(con)\n    active = list_active_experiments(con, site_id)'
)

ctr_text = ctr_text.replace(
    '    con = db_connect()\n    \n    # Check if we should Switch someone to B',
    '    con = db_connect()\n    db_init(con)\n    \n    # Check if we should Switch someone to B'
)

ctr_text = ctr_text.replace(
    '    con = db_connect()\n    from datetime import datetime\n    \n    # Check T+21',
    '    con = db_connect()\n    db_init(con)\n    from datetime import datetime\n    \n    # Check T+21'
)

# min impressions 7d configuration injections
ctr_text = ctr_text.replace(
    '    candidates = select_ctr_candidates(site_id, max_candidates=10)',
    '    min_imps = getenv_int("SEO_EXPERIMENTS_MIN_IMPRESSIONS_7D", 80)\n    candidates = select_ctr_candidates(site_id, min_impressions=min_imps, max_candidates=10)'
)


# resolving astro path
ctr_text = ctr_text.replace(
    '        fpath = resolve_astro_path(cand["url_path"])' if '        fpath = resolve_astro_path(cand["url_path"])' in ctr_text else '        fpath = resolve_astro_path(url_path)',
    '        from agent.tasks.seo import resolve_astro_path\n        fpath = resolve_astro_path(url_path)'
)


# GSC PROPERTY fallback instead of hardcoded 
ctr_text = ctr_text.replace(
    'variant = get_page_metrics_with_fallback(service, "https://www.superparty.ro/", exp["page_url"], exp["variant_start"], endDate)',
    'gsc_prop = getenv("GSC_PROPERTY", "https://www.superparty.ro/").strip()\n    variant = get_page_metrics_with_fallback(service, gsc_prop, exp["page_url"], exp["variant_start"], endDate)'
)

with open('agent/tasks/seo_ctr_experiments.py', 'w', encoding='utf-8') as f:
    f.write(ctr_text)
    
print("seo_ctr_experiments.py patched!")

