import os
import re

os.chdir(r"C:\Users\ursac\Superparty")

with open('agent/tasks/seo.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Sector title in get_deterministic_payload
text = text.replace(
    'payload["title"] = f"Animatori copii Sector {slug.replace(\'sector-\', \'\')} București | Superparty"',
    'payload["title"] = f"Animatori petreceri copii Sector {slug.replace(\'sector-\', \'\')} București | Superparty"'
)

# 2. Update hub links to be distinct
# Hub Ilfov points to animatori-petreceri-copii right now. Let's make it point to Bucuresti
text = text.replace(
    '        payload["hub_url"] = "/animatori-petreceri-copii"\n        payload["hub_label"] = "Animatori petreceri copii (pilon)"',
    '        payload["hub_url"] = "/petreceri/bucuresti"\n        payload["hub_label"] = "Hub București"'
)
# Hub Bucuresti defaults to illicit. Let's make sure it points to Ilfov explicitly
text = text.replace(
    '        elif page_type == "hub_bucuresti":\n            payload["description"] = "Animatori pentru petreceri copii în București, pe sectoare. Activități adaptate vârstei și spațiului. Cere ofertă și verifică disponibilitatea."\n',
    '        elif page_type == "hub_bucuresti":\n            payload["description"] = "Animatori pentru petreceri copii în București, pe sectoare. Activități adaptate vârstei și spațiului. Cere ofertă și verifică disponibilitatea."\n            payload["hub_url"] = "/petreceri/ilfov"\n            payload["hub_label"] = "Hub județul Ilfov"\n'
)

# 3. Add _load_apply_state and _save_apply_state inside _orig_seo_apply_task
# We'll inject it right before the Load Manifest section

load_save_code = """
    def _load_apply_state(state_path: Path) -> dict:
        today = str(date.today())
        if state_path.exists():
            try:
                st = json.loads(state_path.read_text(encoding="utf-8"))
            except Exception:
                st = {}
        else:
            st = {}

        if st.get("date") != today:
            st = {
                "date": today,
                "files_applied_today": 0,
                "prs_created_today": 0,
                "page_last_applied": st.get("page_last_applied", {}),
            }

        st.setdefault("page_last_applied", {})
        st.setdefault("files_applied_today", 0)
        st.setdefault("prs_created_today", 0)
        return st

    def _save_apply_state(state_path: Path, st: dict) -> None:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")
"""

text = text.replace('    # Load Manifest for Source of Truth', load_save_code + '\n    # Load Manifest for Source of Truth')

# 4. Replace the old broken state block with usage of _load_apply_state
old_broken_state = """    audit_log = {"applied": [], "skipped": [], "unmapped": [], "date": str(date.today())}
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

new_working_state = """    audit_log = {"applied": [], "skipped": [], "unmapped": [], "date": str(date.today())}
    applied_files = []
    
    succes_count = 0
    import agent.common.env
    max_files_per_run = agent.common.env.getenv_int("SEO_REAL_MAX_FILES_PER_RUN", 3)
    max_files_per_day = agent.common.env.getenv_int("SEO_REAL_MAX_FILES_PER_DAY", 15)
    max_prs_per_day = agent.common.env.getenv_int("SEO_REAL_MAX_PRS_PER_DAY", 4)
    cooldown_days = agent.common.env.getenv_int("SEO_REAL_COOLDOWN_DAYS", 7)
    
    state_file = Path(f"reports/{site_id}/seo_apply_state.json")
    state = _load_apply_state(state_file)
            
    if state["files_applied_today"] >= max_files_per_day:
        return {"ok": True, "note": "budget_reached", "reason": "max_files_per_day"}
    if state["prs_created_today"] >= max_prs_per_day:
        return {"ok": True, "note": "budget_reached", "reason": "max_prs_per_day"}
"""
text = text.replace(old_broken_state, new_working_state)

# 5. Save state at the end before PR creation (We already increment prs_created_today)
old_save_state = """    try:
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
        
new_save_state = """    # Save state before doing anything else
    _save_apply_state(state_file, state)

    try:
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
        return {"ok": False, "error": str(e), "files": applied_files}"""

text = text.replace(old_save_state, new_save_state)

with open('agent/tasks/seo.py', 'w', encoding='utf-8') as f:
    f.write(text)
