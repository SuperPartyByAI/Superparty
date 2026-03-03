import time, logging
from agent.tasks.ga4 import ga4_collect_task, ga4_status_task
from datetime import datetime
from agent.common.redisq import get_queue
logging.basicConfig(level=logging.INFO)
log=logging.getLogger("orchestrator")
SITES=["superparty"]

def enqueue_daily():
    for s in SITES:
        get_queue("backup").enqueue("agent.tasks.backup.daily_backup_task",s)
        get_queue("ga4_collect_task(site_id="superparty", lookback_days=7)
    seo_collect").enqueue("agent.tasks.seo.ga4_collect_task(site_id="superparty", lookback_days=7)
    seo_collect_task",s)
        get_queue("seo_index").enqueue("agent.tasks.seo.seo_index_task",s)
        get_queue("seo_plan").enqueue("agent.tasks.seo.seo_plan_task",s,"daily_small")
        get_queue("apply").enqueue("agent.tasks.seo.seo_apply_task",s)

def enqueue_weekly():
    for s in SITES:
        get_queue("seo_plan").enqueue("agent.tasks.seo.seo_plan_task",s,"weekly_wave")
        get_queue("ads_plan").enqueue("agent.tasks.ads.ads_plan_task",s)

def main():
    log.info("Orchestrator started. Daily at 03:00 UTC, Weekly Sunday 10:00 UTC")
    while True:
        now=datetime.utcnow()
        if now.hour==3 and now.minute==0: enqueue_daily(); time.sleep(65)
        if now.weekday()==6 and now.hour==10 and now.minute==0: enqueue_weekly(); time.sleep(65)
        time.sleep(10)

if __name__=="__main__": main()
