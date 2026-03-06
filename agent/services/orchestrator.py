import time, logging
from datetime import datetime

log = logging.getLogger(__name__)
SITES = ["superparty"]

try:
    from agent.common.redisq import get_queue
    log.info("Using Redis/RQ queues (real)")
except ImportError:
    log.warning("Redis not available, using direct execution fallback")
    def get_queue(name):
        class _Q:
            def enqueue(self, fn_path, *args, **kwargs):
                try:
                    parts = fn_path.split(".")
                    import importlib
                    mod = importlib.import_module(".".join(parts[:-1]))
                    return getattr(mod, parts[-1])(*args, **kwargs)
                except Exception as e:
                    log.error("FallbackQueue %s %s: %s", name, fn_path, e)
        return _Q()


def enqueue_daily():

    # Monitoring checks (daily)
    try:
        from agent.tasks.monitoring import run_checks
        run_checks(site_id="superparty")
    except Exception as _me:
        import logging; logging.getLogger(__name__).warning("monitoring: %s", _me)
    for site_id in SITES:
        try:
            get_queue("seo_collect").enqueue("agent.tasks.seo.seo_collect_task", site_id=site_id)
            get_queue("seo_index").enqueue("agent.tasks.seo.seo_index_task", site_id=site_id)
            get_queue("backup").enqueue("agent.tasks.backup.daily_backup_task", site_id=site_id)
            get_queue("ga4").enqueue("agent.tasks.ga4.ga4_collect_task", site_id=site_id, lookback_days=7)
            get_queue("audit").enqueue("agent.tasks.pre_gsc_audit.pre_gsc_audit_task", site_id=site_id)
        except Exception as e:
            log.error("daily %s: %s", site_id, e)


def enqueue_weekly():
    # GA4-driven SEO quick wins (Sunday 10:00 UTC) — runs in worker, not orchestrator
    for site_id in SITES:
        try:
            get_queue("seo_plan").enqueue("agent.tasks.seo.seo_plan_task", mode="ga4_weekly_wave")
            get_queue("apply").enqueue("agent.tasks.seo.seo_apply_task")
        except Exception as e:
            log.warning("GA4 weekly wave %s: %s", site_id, e)



def main():
    import os
    from agent.common.env import getenv_int
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s")
    log.info("Scheduler starting")
    
    FAST_MIN = getenv_int("SEO_FAST_INTERVAL_MIN", 60)
    next_fast = time.time()
    
    while True:
        now = datetime.utcnow()
        if now.hour == 3 and now.minute == 0:
            enqueue_daily()
            time.sleep(65)
            continue
            
        if now.weekday() == 6 and now.hour == 10 and now.minute == 0:
            enqueue_weekly()
            time.sleep(65)
            continue
            
        if os.environ.get("SEO_CONTINUOUS", "0") == "1" and time.time() >= next_fast:
            log.info(f"Fast Lane triggers: enqueuing seo_plan and seo_apply (interval {FAST_MIN}m)")
            try:
                get_queue("seo_plan").enqueue("agent.tasks.seo.seo_plan_task", mode="default")
                get_queue("apply").enqueue("agent.tasks.seo.seo_apply_task")
            except Exception as e:
                log.error(f"Failed Fast Lane enqueue: {e}")
            next_fast = time.time() + FAST_MIN * 60
            
        time.sleep(10)

if __name__ == "__main__":
    main()
