import os
import re

os.chdir(r"C:\Users\ursac\Superparty")

with open('agent/tasks/seo_ctr_experiments.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add switch task
switch_task = """
def seo_ctr_experiments_switch_task(site_id="superparty"):
    from agent.common.env import getenv_int
    from datetime import datetime, date, timedelta
    
    con = db_connect()
    db_init(con)
    
    # We find experiments running A that have reached half of their duration (e.g. 10 days)
    # The spec allows 21 days total, let's switch to B around midway
    rows = con.execute("SELECT * FROM seo_experiments WHERE site_id=? AND status='RUNNING_A'", (site_id,)).fetchall()
    
    switched = 0
    for r in rows:
        exp = dict(r)
        
        # Check if 10 days have passed since A started
        v_start = datetime.strptime(exp["variant_start"], "%Y-%m-%d").date()
        days_running_a = (date.today() - v_start).days
        
        switch_days = getenv_int("SEO_EXPERIMENTS_SWITCH_DAYS", 10)
        
        if days_running_a >= switch_days:
            # We must apply B
            res = apply_title_desc_variant(site_id, exp["url_path"], exp["page_url"], "B", exp["variant_b_title"], exp["variant_b_description"])
            
            if res.get("ok"):
                # Mark it as RUNNING_B and update variant_start so we can track B's start time properly 
                # (Note: A true A/B system might track A and B stats separately, here we just switch the phase)
                update_experiment(con, exp["exp_id"], status="RUNNING_B", variant_start=str(date.today() + timedelta(days=3)))
                switched += 1
                
                try:
                    from pathlib import Path
                    import json
                    sf = Path(f"reports/{site_id}/seo_apply_state.json")
                    if sf.exists():
                        st = json.loads(sf.read_text(encoding="utf-8"))
                        st["prs_created_today"] = st.get("prs_created_today", 0) + 1
                        sf.write_text(json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass
            
    return {"ok": True, "switched": switched}
"""

if "def seo_ctr_experiments_switch_task(" not in text:
    text += "\n" + switch_task
    
    # Also hook it in Orchestrator's evaluate queue (run it daily)
    with open('agent/services/orchestrator.py', 'r', encoding='utf-8') as orch_f:
        orch_text = orch_f.read()
    
    if "get_queue(\"learn\").enqueue(\"agent.tasks.seo_ctr_experiments.seo_ctr_experiments_switch_task\"" not in orch_text:
        orch_text = orch_text.replace(
            'get_queue("learn").enqueue("agent.tasks.seo_ctr_experiments.seo_ctr_experiments_evaluate_task", site_id="superparty")',
            'get_queue("learn").enqueue("agent.tasks.seo_ctr_experiments.seo_ctr_experiments_switch_task", site_id="superparty")\n                get_queue("learn").enqueue("agent.tasks.seo_ctr_experiments.seo_ctr_experiments_evaluate_task", site_id="superparty")'
        )
        with open('agent/services/orchestrator.py', 'w', encoding='utf-8') as orch_f:
            orch_f.write(orch_text)

with open('agent/tasks/seo_ctr_experiments.py', 'w', encoding='utf-8') as f:
    f.write(text)

