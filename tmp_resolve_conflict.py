import re

with open('agent/tasks/seo.py', 'r', encoding='utf-8') as f:
    text = f.read()

conflict_pattern = re.compile(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [a-f0-9]+', re.DOTALL)

def resolver(match):
    head_content = match.group(1) # From main (PR 35)
    incoming_content = match.group(2) # From PR 36
    
    # head_content contains the sorting and local_intent_score logic.
    # incoming_content contains the plan_hash, deduplication and fast-lane reporting.
    # We want to build the ultimate planner block.
    
    # Find the top part: opportunities list building (exists in both, but HEAD has robust intent score)
    # The actual resolution isn't just string joining, let's just extract the core parts from HEAD and append the trailing from PR 36.
    
    return """
    opportunities = []
    
    for x in index:
        query = x.get("query", "").lower()
        page = x.get("page", "")
        if "animatori" not in query and "petreceri" not in query and "mascote" not in query:
            continue
        if x.get("impressions", 0) < getenv_int("SEO_IMPRESSIONS_MIN", 50):
            continue
        if not (getenv_int("SEO_POS_MIN", 3) <= x.get("avg_position", 99) <= getenv_int("SEO_POS_MAX", 50)):
            continue
            
        # Priorizare locala pe baza Whitelist-ului
        score, matched = compute_local_intent(query, whitelist_slugs)
        
        # Filtru strict pe Buc/Ilfov (scor > 0)
        if score > 0:
            opp = x.copy()
            opp["local_intent_score"] = score
            opp["matched_terms"] = list(matched)
            opportunities.append(opp)
            
    # Sortare primara pe local intent score DESC, apoi impresii DESC, apoi pozitie ASC
    opportunities.sort(key=lambda x: (-x.get("local_intent_score", 0), -x.get("impressions", 0), x.get("avg_position", 99)))
    
    wave_size = getenv_int("SEO_WAVE_SIZE", 25)
    opportunities = opportunities[:wave_size]

    plan_dir = Path(f"reports/{site_id}/seo_plans")
    plan_dir.mkdir(parents=True, exist_ok=True)
    
    plan_file = plan_dir / f"plan_{date.today()}.json"
    
    # Dedupe and Hash from PR 36
    import hashlib
    plan_json_str = json.dumps(opportunities, sort_keys=True)
    plan_hash = hashlib.md5(plan_json_str.encode('utf-8')).hexdigest()
    
    plan_data = {
        "date": str(date.today()),
        "wave": wave,
        "opportunities": opportunities,
        "plan_hash": plan_hash
    }
    
    # Detect daca a mai rulat azi (pentru fast-lane check)
    if plan_file.exists():
        old_data = json.loads(plan_file.read_text(encoding='utf-8'))
        if old_data.get("plan_hash") == plan_hash:
            return {"ok": True, "note": "plan_hash_unchanged", "file": str(plan_file)}

    plan_file.write_text(json.dumps(plan_data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    import time
    run_id = time.strftime("%H%M%S")
    from agent.common.git_pr import git_commit_push_pr
    result = git_commit_push_pr(
        branch=f"agent/seo-gsc-plan-{date.today()}T{run_id}Z",
        commit_msg=f"feat(seo): gsc plan {date.today()}T{run_id}Z",
        files=[str(plan_file)],
        pr_title=f"SEO Plan: {len(opportunities)} opportunities ({wave})",
        pr_body=f"Automated SEO plan generated.\n\nTop: {opportunities[0].get('query') if opportunities else 'none'}"
    )
    return {"ok": True, "pr_url": result, "file": str(plan_file)}
"""

resolved_text = conflict_pattern.sub(resolver, text)

with open('agent/tasks/seo.py', 'w', encoding='utf-8') as f:
    f.write(resolved_text)
