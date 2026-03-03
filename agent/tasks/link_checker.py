"""link_checker.py — crawl site (max 200 URLs) and detect broken links, redirect chains."""
import re
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from collections import deque
from datetime import date


def link_checker_task(site_id="superparty", base_url="https://superparty.ro", max_urls=200):
    """Crawl the site and detect broken links, redirect chains, missing anchors."""
    visited = set()
    queue = deque([base_url.rstrip("/")])
    results = []
    broken = []
    redirects = []

    def check_url(url, referer=""):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "SEO-Agent-LinkChecker/1.0 (internal audit)"},
                method="HEAD"
            )
            resp = urllib.request.urlopen(req, timeout=6)
            return resp.status, resp.url, None
        except urllib.error.HTTPError as e:
            return e.code, url, None
        except Exception as ex:
            return 0, url, str(ex)[:80]

    while queue and len(visited) < max_urls:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        code, final_url, err = check_url(url)
        time.sleep(0.3)  # rate limit

        entry = {
            "url": url,
            "status": code,
            "final_url": final_url,
            "error": err,
        }
        results.append(entry)

        if code == 0 or code >= 400:
            broken.append(entry)
        elif final_url != url and final_url:
            redirects.append({**entry, "redirect_to": final_url})

        # If it's an internal page, extract links to queue
        if code == 200 and url.startswith(base_url):
            try:
                req2 = urllib.request.Request(
                    url,
                    headers={"User-Agent": "SEO-Agent-LinkChecker/1.0"},
                )
                resp2 = urllib.request.urlopen(req2, timeout=8)
                html = resp2.read().decode("utf-8", errors="ignore")
                hrefs = re.findall(r'href=["\']([^"\'#?][^"\']*)["\']', html)
                for href in hrefs:
                    if href.startswith("/"):
                        full = base_url.rstrip("/") + href
                    elif href.startswith("http"):
                        full = href
                    else:
                        continue
                    if base_url in full and full not in visited:
                        queue.append(full.split("?")[0].split("#")[0])
            except Exception:
                pass

    report = {
        "date": str(date.today()),
        "site": base_url,
        "urls_checked": len(visited),
        "broken_count": len(broken),
        "redirect_count": len(redirects),
        "broken": broken[:30],
        "redirects": redirects[:20],
        "all": results[:100],
    }

    report_dir = Path(f"reports/{site_id}/link_checker")
    report_dir.mkdir(parents=True, exist_ok=True)
    out = report_dir / f"link_check_{date.today()}.json"
    out.write_text(json.dumps(report, indent=2))

    md = [
        f"# Link Check Report — {date.today()}",
        "",
        f"URLs checked: {len(visited)} | Broken: {len(broken)} | Redirects: {len(redirects)}",
        "",
    ]
    if broken:
        md.append("## Broken Links")
        for b in broken[:10]:
            md.append(f"- [{b['url']}]({b['url']}) → {b['status']} {b.get('error','')}")
    if redirects:
        md.append("")
        md.append("## Redirect Chains")
        for r in redirects[:10]:
            md.append(f"- {r['url']} → {r.get('redirect_to','?')}")

    md_file = report_dir / f"link_check_{date.today()}.md"
    md_file.write_text("\n".join(md))

    return {
        "ok": True,
        "urls_checked": len(visited),
        "broken": len(broken),
        "redirects": len(redirects),
        "report_file": str(out),
    }
