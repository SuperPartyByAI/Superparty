import json
from datetime import date
from pathlib import Path
import logging
log=logging.getLogger("backup")

def daily_backup_task(site_id=None, site="superparty", **kwargs):
    site = site_id or site  # orchestrator passes site_id=..., fallback to 'superparty'
    d=date.today().strftime("%Y%m%d")
    bdir=Path(f"reports/{site}/backups/{d}")
    bdir.mkdir(parents=True,exist_ok=True)
    for p in [f"agent/sites/{site}.yml","agent/allowlist.yml","public/robots.txt","public/sitemap.xml"]:
        src=Path(p)
        if src.exists(): (bdir/src.name).write_bytes(src.read_bytes())
    (bdir/"meta.json").write_text(json.dumps({"date":d,"site":site},indent=2),encoding="utf-8")
    log.info("Backup: %s",bdir)
    return {"ok":True,"dir":str(bdir)}
