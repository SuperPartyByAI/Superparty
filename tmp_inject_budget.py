import os
import re

os.chdir(r"C:\Users\ursac\Superparty")

with open('agent/tasks/seo.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update _orig_seo_plan_task to dedupe using hash
old_plan_write = """    plan = {"wave": wave, "created": str(date.today()), "opportunities": opportunities, "count": len(opportunities)}
    plan_dir = Path(f"reports/{site_id}/seo_plans")
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plan_dir / f"plan_{date.today()}_{wave}.json"
    plan_file.write_text(json.dumps(plan, indent=2))
    return {"ok": True, "opportunities": len(opportunities), "file": str(plan_file)}"""

new_plan_write = """    import hashlib
    plan_json_str = json.dumps(opportunities, sort_keys=True)
    plan_hash = hashlib.sha256(plan_json_str.encode('utf-8')).hexdigest()
    
    plan = {"wave": wave, "created": str(date.today()), "opportunities": opportunities, "count": len(opportunities), "hash": plan_hash}
    plan_dir = Path(f"reports/{site_id}/seo_plans")
    plan_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if a plan with the same hash already exists today
    existing_plans = sorted(plan_dir.glob(f"plan_*.json"))
    if existing_plans:
        import logging
        try:
            last_plan = json.loads(existing_plans[-1].read_text(encoding='utf-8'))
            if last_plan.get("hash") == plan_hash:
                logging.getLogger(__name__).info("SEO Plan deduplicated (same hash).")
                return {"ok": True, "opportunities": len(opportunities), "note": "deduped_hash"}
        except Exception:
            pass

    import time
    run_id = time.strftime("%H%M%S")
    plan_file = plan_dir / f"plan_{date.today()}_{run_id}_{wave}.json"
    plan_file.write_text(json.dumps(plan, indent=2))
    return {"ok": True, "opportunities": len(opportunities), "file": str(plan_file)}"""

text = text.replace(old_plan_write, new_plan_write)


# 2. Update _orig_seo_apply_task state budget
start_of_apply_logic = """    audit_log = {"applied": [], "skipped": [], "unmapped": [], "date": str(date.today())}
    applied_files = []
    
    succes_count = 0
    import agent.common.env
    max_files = agent.common.env.getenv_int("SEO_REAL_MAX_FILES_PER_RUN", 3)"""

injection_apply_state = """    audit_log = {"applied": [], "skipped": [], "unmapped": [], "date": str(date.today())}
    applied_files = []
    
    succes_count = 0
    import agent.common.env
    max_files_per_run = agent.common.env.getenv_int("SEO_REAL_MAX_FILES_PER_RUN", 3)
    max_files_per_day = agent.common.env.getenv_int("SEO_REAL_MAX_FILES_PER_DAY", 15)
    max_prs_per_day = agent.common.env.getenv_int("SEO_REAL_MAX_PRS_PER_DAY", 4)
    cooldown_days = agent.common.env.getenv_int("SEO_REAL_COOLDOWN_DAYS", 7)
    
    state_file = Path(f"reports/{site_id}/seo_apply_state.json")
    state = {"date": str(date.today()), "files_applied_today": 0, "prs_created_today": 0, "page_last_applied": {}}
    if state_file.exists():
        try:
            old_state = json.loads(state_file.read_text(encoding='utf-8'))
            if old_state.get("date") == str(date.today()):
                state = old_state
            else:
                state["page_last_applied"] = old_state.get("page_last_applied", {})
        except Exception:
            pass
            
    if state["files_applied_today"] >= max_files_per_day:
        return {"ok": True, "note": "budget_reached", "reason": "max_files_per_day"}
    if state["prs_created_today"] >= max_prs_per_day:
        return {"ok": True, "note": "budget_reached", "reason": "max_prs_per_day"}
"""

text = text.replace(start_of_apply_logic, injection_apply_state)

# 3. Handle COOLDOWN logic during iteration
iteration_old = """    for opp in opportunities:
        url_path = opp.get("page", "")
        fpath = resolve_astro_path(url_path)
        if not fpath:
            audit_log["unmapped"].append({"page": url_path, "reason": "not_resolved"})
            continue"""
            
iteration_new = """    from datetime import datetime
    for opp in opportunities:
        url_path = opp.get("page", "")
        fpath = resolve_astro_path(url_path)
        if not fpath:
            audit_log["unmapped"].append({"page": url_path, "reason": "not_resolved"})
            continue
            
        # COOLDOWN Check
        last_applied_str = state["page_last_applied"].get(url_path)
        if last_applied_str:
            last_applied_date = datetime.strptime(last_applied_str, "%Y-%m-%d").date()
            if (date.today() - last_applied_date).days < cooldown_days:
                audit_log["skipped"].append({"page": url_path, "reason": "cooldown"})
                continue"""
text = text.replace(iteration_old, iteration_new)

# 4. Handle STATE UPDATE when gate passes
gate_pass_old = """        if gate_passed:
            fpath.write_text(new_text, encoding="utf-8")
            applied_files.append(str(fpath))
            audit_log["applied"].append({"page": url_path, "file": str(fpath), "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})
            succes_count += 1
        else:
            audit_log["skipped"].append({"page": url_path, "reason": "failed_gate", "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})

        if succes_count >= max_files:
            break"""

gate_pass_new = """        if gate_passed:
            fpath.write_text(new_text, encoding="utf-8")
            applied_files.append(str(fpath))
            audit_log["applied"].append({"page": url_path, "file": str(fpath), "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})
            succes_count += 1
            state["files_applied_today"] += 1
            state["page_last_applied"][url_path] = str(date.today())
        else:
            audit_log["skipped"].append({"page": url_path, "reason": "failed_gate", "gate": {"delta": text_delta, "faqs": faq_count, "links": links_count}})

        if succes_count >= max_files_per_run or state["files_applied_today"] >= max_files_per_day:
            break"""
text = text.replace(gate_pass_old, gate_pass_new)


# 5. Handle Final State Save on valid PR
pr_old = """    try:
        pr_url = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}T{run_id}Z",
            commit_msg=f"feat(seo): gsc apply real {date.today()}T{run_id}Z",
            files=applied_files,
            pr_title=f"SEO Apply Real: {succes_count} pagini optimizate on-page ({date.today()})",
            pr_body=f"S-a folosit funcția llm deterministica de apply safe pentru modificari pe text.\\n\\nPagini îmbunătățite:\\n" + "\\n".join([f"- `{k}`" for k in applied_files])
        )
        return {"ok": True, "pr_url": pr_url}
    except Exception as e:
        return {"ok": False, "error": str(e), "files": applied_files}"""

pr_new = """    try:
        pr_url = git_commit_push_pr(
            branch=f"agent/seo-gsc-apply-{date.today()}T{run_id}Z",
            commit_msg=f"feat(seo): gsc apply real {date.today()}T{run_id}Z",
            files=applied_files,
            pr_title=f"SEO Apply Real: {succes_count} pagini optimizate on-page ({date.today()})",
            pr_body=f"S-a folosit funcția llm deterministica de apply safe pentru modificari pe text.\\n\\nPagini îmbunătățite:\\n" + "\\n".join([f"- `{k}`" for k in applied_files])
        )
        
        state["prs_created_today"] += 1
        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        
        return {"ok": True, "pr_url": pr_url}
    except Exception as e:
        return {"ok": False, "error": str(e), "files": applied_files}"""
text = text.replace(pr_old, pr_new)


with open('agent/tasks/seo.py', 'w', encoding='utf-8') as f:
    f.write(text)
    
