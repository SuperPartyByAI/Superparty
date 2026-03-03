import time, logging
from datetime import datetime

log = logging.getLogger(__name__)
SITES = ["superparty"]


def get_queue(name):
    class _Q:
        def enqueue(self, fn_path, *args, **kwargs):
            try:
                parts = fn_path.split(".")
                import importlib
                mod = importlib.import_module(".".join(parts[:-1]))
                return getattr(mod, parts[-1])(*args, **kwargs)
            except Exception as e:
                log.error("Queue %s %s: %s", name, fn_path, e)
    return _Q()


def enqueue_daily():
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
    # GA4-driven SEO quick wins (Sunday 10:00 UTC)
    try:
        from agent.tasks.seo import seo_plan_task, seo_apply_task
        seo_plan_task(mode="ga4_weekly_wave")
        seo_apply_task()
    except Exception as e:
        log.warning("GA4 weekly wave: %s", e)


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(name)s %(levelname)s %(message)s")
    log.info("Scheduler starting")
    while True:
        now = datetime.utcnow()
        if now.hour == 3 and now.minute == 0:
            enqueue_daily()
            time.sleep(65)
        elif now.weekday() == 6 and now.hour == 10 and now.minute == 0:
            enqueue_weekly()
            time.sleep(65)
        else:
            time.sleep(10)


if __name__ == "__main__":
    main()
