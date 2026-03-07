import os
import json

os.chdir(r"C:\Users\ursac\Superparty")

with open('agent/tasks/seo_ctr_experiments.py', 'r', encoding='utf-8') as f:
    text = f.read()

tasks_code = """
VARIANTS = {
  "pilon": {
    "A": {
      "title": "Animatori petreceri copii București & Ilfov | SuperParty",
      "description": "Animatori pentru petreceri copii în București și Ilfov. Programe adaptate vârstei, personaje, jocuri și activități. Cere ofertă."
    },
    "B": {
      "title": "SuperParty – Animatori petreceri copii București & Ilfov",
      "description": "Petreceri copii cu animatori în București și Ilfov. Activități adaptate spațiului și vârstei. Verifică disponibilitatea și cere ofertă."
    }
  },
  "hub_bucuresti": {
    "A": {
      "title": "Animatori petreceri copii în București | SuperParty",
      "description": "Animatori pentru petreceri copii în București, pe sectoare. Activități adaptate vârstei și spațiului. Cere ofertă."
    },
    "B": {
      "title": "București: animatori petreceri copii – SuperParty",
      "description": "Cauți animatori copii în București? Programe flexibile pentru aniversări și evenimente. Solicită ofertă și verifică disponibilitatea."
    }
  },
  "hub_ilfov": {
    "A": {
      "title": "Animatori petreceri copii în Ilfov | SuperParty",
      "description": "Animatori pentru petreceri copii în Ilfov (orașe și comune). Programe adaptate vârstei și spațiului. Cere ofertă."
    },
    "B": {
      "title": "Ilfov: animatori petreceri copii – SuperParty",
      "description": "Animatori copii pentru petreceri în Ilfov. Ne adaptăm spațiului disponibil (acasă/curte/sală pusă la dispoziție). Solicită ofertă."
    }
  },
  "sector": {
    "A": {
      "title": "Animatori petreceri copii Sector {N} București | SuperParty",
      "description": "Animatori pentru petreceri copii în Sector {N}, București. Activități adaptate vârstei și spațiului. Cere ofertă."
    },
    "B": {
      "title": "Sector {N} București: animatori petreceri copii – SuperParty",
      "description": "Petreceri copii în Sector {N} cu animatori. Programe flexibile pentru aniversări și evenimente. Verifică disponibilitatea."
    }
  },
  "localitate_ilfov": {
    "A": {
      "title": "Animatori petreceri copii în {LOC} | SuperParty",
      "description": "Animatori pentru petreceri copii în {LOC}. Programe adaptate vârstei, acasă/curte/sală pusă la dispoziție. Cere ofertă."
    },
    "B": {
      "title": "{LOC}: animatori petreceri copii – SuperParty",
      "description": "Cauți animatori copii în {LOC}? Activități potrivite pentru aniversări și evenimente. Solicită ofertă și verifică disponibilitatea."
    }
  }
}

def get_variants_for_path(url_path: str) -> dict:
    ptype = page_type_from_path(url_path)
    if ptype == "pilon": return VARIANTS["pilon"]
    if ptype == "hub_bucuresti": return VARIANTS["hub_bucuresti"]
    if ptype == "hub_ilfov": return VARIANTS["hub_ilfov"]
    
    if ptype == "sector":
        slug = url_path.split("/")[-1]
        n_str = slug.replace("sector-", "")
        v = {"A": {}, "B": {}}
        for var in ["A", "B"]:
            v[var]["title"] = VARIANTS["sector"][var]["title"].replace("{N}", n_str)
            v[var]["description"] = VARIANTS["sector"][var]["description"].replace("{N}", n_str)
        return v
        
    if ptype == "local_or_service":
        slug = url_path.split("/")[-1]
        loc_str = slug.replace("-", " ").title()
        v = {"A": {}, "B": {}}
        for var in ["A", "B"]:
            v[var]["title"] = VARIANTS["localitate_ilfov"][var]["title"].replace("{LOC}", loc_str)
            v[var]["description"] = VARIANTS["localitate_ilfov"][var]["description"].replace("{LOC}", loc_str)
        return v
        
    return {"A": {"title": "", "description": ""}, "B": {"title": "", "description": ""}}

import logging
log = logging.getLogger(__name__)

def seo_ctr_experiments_plan_task(site_id="superparty"):
    from agent.common.env import getenv_int
    max_active = getenv_int("SEO_EXPERIMENTS_MAX_ACTIVE", 10)
    
    con = db_connect()
    active = list_active_experiments(con, site_id)
    if len(active) >= max_active:
        return {"ok": True, "note": "max_active_reached"}
        
    # Risk Canary Check:
    active_urls = [a["url_path"] for a in active if a["status"] in ["RUNNING_A", "RUNNING_B", "PLANNED"]]
    if "/animatori-petreceri-copii" in active_urls:
        log.info("Canary experiment running on Pilon. Halting new experiments.")
        return {"ok": True, "note": "canary_active"}

    candidates = select_ctr_candidates(site_id, max_candidates=10)
    
    # Load Real Apply Cooldowns to avoid cross-contamination
    content_cooldowns = {}
    try:
        from pathlib import Path
        import json
        sf = Path(f"reports/{site_id}/seo_apply_state.json")
        if sf.exists():
            st = json.loads(sf.read_text(encoding="utf-8"))
            content_cooldowns = st.get("page_last_applied", {})
    except Exception:
        pass
        
    from datetime import datetime    
    planned = 0
    for cand in candidates:
        if len(active) + planned >= max_active:
            break
            
        url_path = cand["url_path"]
        if url_path in active_urls:
            continue
            
        # Check real-apply cooldown cross contamination
        last_applied_str = content_cooldowns.get(url_path)
        if last_applied_str:
            last_applied_date = datetime.strptime(last_applied_str, "%Y-%m-%d").date()
            if (date.today() - last_applied_date).days < getenv_int("SEO_REAL_COOLDOWN_DAYS", 7):
                continue
                
        # Get baseline text
        fpath = resolve_astro_path(url_path)
        if not fpath: continue
        
        text = Path(str(fpath)).read_text(encoding="utf-8", errors="ignore")
        btitle, bdesc = extract_layout_title_desc(text)
        
        variants = get_variants_for_path(url_path)
        if not variants["A"]["title"]: continue
        
        # Avoid creating experiment if current title IS variant A or variant B (already optimized or manual)
        if btitle == variants["A"]["title"] or btitle == variants["B"]["title"]:
            continue
            
        page_url = f"https://www.superparty.ro{url_path}" if url_path != "/" else "https://www.superparty.ro/"
        
        exp_id = create_experiment(
            con, site_id, url_path, page_url, str(fpath),
            baseline=cand, 
            baseline_title=btitle, baseline_description=bdesc,
            varA=variants["A"], varB=variants["B"],
            duration_days=getenv_int("SEO_EXPERIMENTS_DURATION_DAYS", 21)
        )
        planned += 1

    return {"ok": True, "planned": planned}

def seo_ctr_experiments_apply_task(site_id="superparty"):
    from agent.common.env import getenv_int
    max_prs = getenv_int("SEO_REAL_MAX_PRS_PER_DAY", 3)
    
    con = db_connect()
    
    # Check if we should Switch someone to B
    # Simplified logic: just apply A for now. A full implementation would apply A, and maybe later apply B if configured as Multi-Armed.
    # The spec required 14 days per variant if pure A/B, or we just test Variant A against Baseline. Let's start A.
    
    rows = con.execute("SELECT * FROM seo_experiments WHERE site_id=? AND status='PLANNED' LIMIT 1", (site_id,)).fetchall()
    if not rows:
        return {"ok": True, "note": "nothing_planned"}
        
    exp = dict(rows[0])
    
    # We apply A
    res = apply_title_desc_variant(site_id, exp["url_path"], exp["page_url"], "A", exp["variant_a_title"], exp["variant_a_description"])
    
    if res.get("ok"):
        update_experiment(con, exp["exp_id"], status="RUNNING_A")
        # Ensure we increment PR count
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
            
    return res

def seo_ctr_experiments_evaluate_task(site_id="superparty"):
    con = db_connect()
    from datetime import datetime
    
    # Check T+21
    rows = con.execute(
        "SELECT * FROM seo_experiments WHERE site_id=? AND status IN ('RUNNING_A', 'RUNNING_B')",
        (site_id,)
    ).fetchall()
    
    evaluated = 0
    from agent.services.credentials import get_gsc_service
    service = get_gsc_service()
    if not service: return {"ok": False, "reason": "no_gsc"}
    
    for r in rows:
        exp = dict(r)
        
        # Check if 21 days passed or early stop logic
        ends_date = datetime.strptime(exp["ends_at"], "%Y-%m-%d").date()
        started_date = datetime.strptime(exp["started_at"], "%Y-%m-%d").date()
        
        days_running = (date.today() - started_date).days
        
        # evaluate if full duration passed
        if date.today() >= ends_date:
            evaluate_experiment(con, exp, service)
            evaluated += 1
        elif days_running >= 10:
            # Check early stop
            evaluate_experiment(con, exp, service, early_stop=True)
            evaluated += 1
            
    return {"ok": True, "evaluated": evaluated}

def evaluate_experiment(con, exp, service, early_stop=False):
    baseline = {
        "clicks": exp["baseline_clicks"],
        "impressions": exp["baseline_impressions"],
        "avg_position": exp["baseline_avg_position"]
    }
    
    endDate = str(date.today() - timedelta(days=3)) # 3 days latency
    
    # Fetch variant metrics
    variant = get_page_metrics_with_fallback(service, "https://www.superparty.ro/", exp["page_url"], exp["variant_start"], endDate)
    
    # Early stop checks volume
    from agent.common.env import getenv_int
    min_imps = getenv_int("SEO_EXPERIMENTS_MIN_VARIANT_IMPRESSIONS", 800)
    
    if early_stop and variant["impressions"] < min_imps:
        return # Not enough volume for early stop
        
    decision, reason = decide_experiment(baseline, variant, min_variant_imps=min_imps)
    
    update_experiment(con, exp["exp_id"], 
        variant_clicks=variant["clicks"],
        variant_impressions=variant["impressions"],
        variant_avg_position=variant["avg_position"],
        decision_reason=reason,
        variant_end=endDate
    )
    
    if decision == "WAIT":
        if not early_stop:
            # Over 21 days and still WAIT? mark INCONCLUSIVE
            update_experiment(con, exp["exp_id"], status="EVALUATING", decision_reason="timeout_" + reason)
        return
        
    if decision == "WINNER":
        update_experiment(con, exp["exp_id"], status="WINNER", winner_variant=exp["status"].split("_")[-1])
        # It's a winner, we do nothing and keep it.
        # Clear active state
        from agent.tasks.seo_ctr_experiments import upsert_page_state
        upsert_page_state(con, exp["site_id"], exp["url_path"], active_exp_id=None, cooldown_until=str(date.today() + timedelta(days=14)))
        
    elif decision == "LOSER":
        # REVERT!
        res = rollback_title_desc(exp["site_id"], exp["url_path"], exp["file_path"], exp["baseline_title"], exp["baseline_description"], reason)
        update_experiment(con, exp["exp_id"], status="REVERTED")
        from agent.tasks.seo_ctr_experiments import upsert_page_state
        upsert_page_state(con, exp["site_id"], exp["url_path"], active_exp_id=None, cooldown_until=str(date.today() + timedelta(days=30)))
        
    elif decision == "INCONCLUSIVE" and not early_stop:
        # Keep winner by absolute clicks or just baseline. Let's baseline.
        res = rollback_title_desc(exp["site_id"], exp["url_path"], exp["file_path"], exp["baseline_title"], exp["baseline_description"], reason)
        update_experiment(con, exp["exp_id"], status="REVERTED", decision_reason="inconclusive_timeout")
        from agent.tasks.seo_ctr_experiments import upsert_page_state
        upsert_page_state(con, exp["site_id"], exp["url_path"], active_exp_id=None, cooldown_until=str(date.today() + timedelta(days=14)))
"""

text += "\n" + tasks_code

with open('agent/tasks/seo_ctr_experiments.py', 'w', encoding='utf-8') as f:
    f.write(text)
