"""monitoring.py - Health checks + alerts for Superparty agent platform."""
import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

log = logging.getLogger(__name__)

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "")
SITE_URL = os.environ.get("SITE_URL", "https://superparty.ro")

STATE_DIR = Path("data/monitor")
STATE_DIR.mkdir(parents=True, exist_ok=True)


def _slack(msg: str):
    if not SLACK_WEBHOOK:
        log.info("Slack not configured: %s", msg[:80])
        return
    try:
        if HAS_REQUESTS:
            import requests as req
            req.post(SLACK_WEBHOOK, json={"text": msg}, timeout=10)
        else:
            import urllib.request, urllib.parse
            payload = json.dumps({"text": msg}).encode()
            urllib.request.urlopen(
                urllib.request.Request(SLACK_WEBHOOK, data=payload,
                                       headers={"Content-Type": "application/json"}), timeout=10)
    except Exception as e:
        log.error("Slack notify failed: %s", e)


def _gh_issue(title: str, body: str):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        log.warning("GitHub issue skipped: no token/repo")
        return None
    import urllib.request, urllib.error
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    h = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json",
         "Content-Type": "application/json"}
    try:
        payload = json.dumps({"title": title, "body": body}).encode()
        req = urllib.request.Request(url, data=payload, headers=h)
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read()).get("html_url")
    except urllib.error.HTTPError as e:
        log.error("GH issue HTTP %s: %s", e.code, e.read()[:100])
    except Exception as e:
        log.error("GH issue error: %s", e)
    return None


def _read_state(key: str) -> dict:
    p = STATE_DIR / f"{key}.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write_state(key: str, obj: dict):
    (STATE_DIR / f"{key}.json").write_text(json.dumps(obj, default=str), encoding="utf-8")


def check_orchestrator() -> tuple:
    """Check if superparty-orchestrator service is Active."""
    try:
        out = subprocess.check_output(
            ["systemctl", "is-active", "superparty-orchestrator"], timeout=10
        ).decode().strip()
    except subprocess.CalledProcessError as e:
        out = "inactive"
    except Exception as e:
        return False, f"docker_ps_failed:{e}"


    if out == "active":
        _write_state("orch", {"down": False, "last_ok": datetime.utcnow().isoformat()})
        return True, "Up: active"
    else:
        prev = _read_state("orch").get("down", False)
        _write_state("orch", {"down": True, "last": datetime.utcnow().isoformat()})
        if not prev:
            msg = f":red_circle: *superparty-orchestrator DOWN*: {out}"
            _slack(msg)
            _gh_issue("superparty-orchestrator down",
                      f"Status: {out}\nTime: {datetime.utcnow().isoformat()}Z")
        return False, out



def check_ga4_collect(site_id: str = "superparty") -> tuple:
    """Check GA4 collect freshness; alert after 2 consecutive failures."""
    rp = Path(f"reports/{site_id}/ga4")
    if not rp.exists():
        return False, "no_ga4_dir"

    files = sorted(rp.glob("collect_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        return False, "no_collect_files"

    try:
        data = json.loads(files[0].read_text(encoding="utf-8"))
        ok = data.get("ok") is True
    except Exception:
        ok = False

    state = _read_state("ga4_fail")
    if not ok:
        fails = state.get("fails", 0) + 1
        _write_state("ga4_fail", {"fails": fails, "last_fail": datetime.utcnow().isoformat()})
        if fails >= 2:
            _slack(f":warning: *GA4 collect failing* {fails} consecutive times. File: `{files[0].name}`")
            _gh_issue(f"GA4 collect failing (x{fails})",
                      f"Consecutive failures: {fails}\nLatest: {files[0]}\nTime: {datetime.utcnow().isoformat()}Z")
        return False, f"ok=False fails={fails}"

    _write_state("ga4_fail", {"fails": 0, "last_ok": datetime.utcnow().isoformat()})
    return True, "ok=True"


def check_sitemap(site_url: str = None) -> tuple:
    """Check sitemap.xml returns 200."""
    url = f"{site_url or SITE_URL}/sitemap.xml"
    try:
        import urllib.request
        resp = urllib.request.urlopen(url, timeout=15)
        status = resp.status
    except Exception as e:
        _slack(f":warning: Sitemap check error: {e}")
        return False, str(e)

    if status != 200:
        prev = _read_state("sitemap").get("status", 200)
        _write_state("sitemap", {"status": status, "last": datetime.utcnow().isoformat()})
        if prev == 200:
            _slack(f":warning: *{url}* returned `{status}` (was 200)")
            _gh_issue(f"Sitemap non-200 ({status})",
                      f"URL: {url}\nStatus: {status}\nTime: {datetime.utcnow().isoformat()}Z")
        return False, f"status={status}"

    _write_state("sitemap", {"status": 200, "last_ok": datetime.utcnow().isoformat()})
    return True, "status=200"


def run_checks(site_id: str = "superparty") -> dict:
    """Run all checks and send daily summary to Slack."""
    results = {}

    orch_ok, orch_msg = check_orchestrator()
    results["orchestrator"] = {"ok": orch_ok, "msg": orch_msg}

    ga4_ok, ga4_msg = check_ga4_collect(site_id)
    results["ga4_collect"] = {"ok": ga4_ok, "msg": ga4_msg}

    sitemap_ok, sitemap_msg = check_sitemap()
    results["sitemap"] = {"ok": sitemap_ok, "msg": sitemap_msg}

    all_ok = all(v["ok"] for v in results.values())
    emoji = ":large_green_circle:" if all_ok else ":warning:"
    lines = [f"{emoji} *Platform health* {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"]
    for k, v in results.items():
        icon = ":white_check_mark:" if v["ok"] else ":x:"
        lines.append(f"  {icon} {k}: {v['msg']}")
    _slack("\n".join(lines))

    report_dir = Path(f"reports/{site_id}")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"monitoring_{datetime.utcnow().strftime('%Y-%m-%d')}.json"
    report_file.write_text(json.dumps({"date": datetime.utcnow().isoformat(), "results": results},
                                       indent=2, ensure_ascii=False), encoding="utf-8")

    return {"ok": all_ok, "results": results, "report": str(report_file)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(json.dumps(run_checks(), indent=2))
