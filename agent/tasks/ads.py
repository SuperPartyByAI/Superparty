import json, requests
from datetime import date
from pathlib import Path
from agent.common.env import getenv
import logging
log=logging.getLogger("ads")

def ads_plan_task(site="superparty"):
    outdir=Path(f"reports/ads_drafts/{site}")
    outdir.mkdir(parents=True,exist_ok=True)
    try:
        r=requests.post(getenv("LLM_WORKER_URL","http://localhost:8100")+"/generate",
                       json={"prompt":f"Ad campaign draft for {site}. Return JSON: {{campaign_name,objective,daily_cap_eur,headlines[3],descriptions[3],landing_page}}"},timeout=60)
        result=r.json()
    except Exception as e: result={"error":str(e)}
    out=outdir/f"ads_plan_{date.today().isoformat()}.json"
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return {"ok":True,"file":str(out)}

def ads_draft_task(site="superparty"):
    return {"ok":True,"note":"Platform adapters not configured yet"}
