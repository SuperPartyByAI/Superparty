"""ga4_planner.py - GA4-driven SEO quick wins planner."""
import json
import os
import re
import logging
from collections import defaultdict
from datetime import date
from pathlib import Path

log = logging.getLogger(__name__)

MAX_WEEKLY_WAVE = 25
GA4_CONVERSION_EVENTS = {
    "form_submit", "cta_click", "click_to_call",
    "click_to_whatsapp", "lead_created", "contact_click"
}

SAFE_FRONTMATTER_KEYS = {"title", "description", "meta_title", "meta_description"}

# ─── Animatori cluster: query keywords that get priority boost ────────────────
ANIMATORI_KEYWORDS = [
    "animatori", "animator", "animatie", "animator copii", "animatori copii",
    "petreceri copii", "petrecere copii", "animatoare", "animatoare copii",
    "zana", "personaje", "clown", "jongler", "magie", "spectacol copii",
]
GEO_BOOST_KEYWORDS = [
    "bucuresti", "ilfov", "sector", "sector 1", "sector 2", "sector 3",
    "sector 4", "sector 5", "sector 6",
]
KEYWORD_BOOST_FACTOR = 5    # x5 for animatori cluster
GEO_BOOST_FACTOR = 2        # extra x2 for geo queries

WEAK_TITLE_PATTERNS = re.compile(
    r"^(home|acas[ar]|untitled|todo|index|page|default|welcome|pagina)$",
    re.IGNORECASE
)


def load_latest_ga4_report(site_id="superparty"):
    ga4_dir = Path(f"reports/{site_id}/ga4")
    if not ga4_dir.exists():
        return None
    collect_files = sorted(ga4_dir.glob("collect_*.json"), reverse=True)
    if not collect_files:
        return None
    try:
        data = json.loads(collect_files[0].read_text(encoding="utf-8"))
        log.info(f"Loaded GA4 report: {collect_files[0]}")
        return data
    except Exception as e:
        log.error(f"Failed reading GA4 report: {e}")
        return None


def _animatori_boost(query: str) -> float:
    """Return score multiplier for 'animatori petreceri copii' cluster queries."""
    q = query.lower()
    boost = 1.0
    if any(kw in q for kw in ANIMATORI_KEYWORDS):
        boost *= KEYWORD_BOOST_FACTOR
    if any(kw in q for kw in GEO_BOOST_KEYWORDS):
        boost *= GEO_BOOST_FACTOR
    return boost


def select_top_pages_from_ga4(ga4_data, limit=MAX_WEEKLY_WAVE):
    if not ga4_data:
        return []

    conversion_by_page = defaultdict(int)

    for ev in ga4_data.get("events", []):
        event_name = ev.get("eventName", "")
        page_path = ev.get("pagePath", "")
        if event_name in GA4_CONVERSION_EVENTS and page_path:
            conversion_by_page[page_path] += int(ev.get("eventCount", 0))

    if not conversion_by_page:
        for page in ga4_data.get("top_pages", []):
            page_path = page.get("pagePath", "")
            sessions = int(page.get("sessions", 0))
            if page_path and sessions > 0:
                conversion_by_page[page_path] += sessions

    # ─── Apply animatori cluster boost ───────────────────────────────────────
    # Boost pages matching animatori/petreceri-copii/sector keywords
    boosted = {}
    for page_path, base_score in conversion_by_page.items():
        q = page_path.lower()
        multiplier = 1.0
        if any(kw.replace(" ", "-") in q or kw in q for kw in ANIMATORI_KEYWORDS):
            multiplier *= KEYWORD_BOOST_FACTOR
        if any(kw.replace(" ", "-") in q or kw in q for kw in GEO_BOOST_KEYWORDS):
            multiplier *= GEO_BOOST_FACTOR
        boosted[page_path] = base_score * multiplier

    ranked = sorted(boosted.items(), key=lambda x: x[1], reverse=True)[:limit]
    log.info("Animatori cluster boost applied. Top page: %s score=%.1f",
             ranked[0][0] if ranked else 'none',
             ranked[0][1] if ranked else 0)
    return [
        {
            "pagePath": p,
            "score": round(s, 2),
            "keyword_priority_applied": True,
            "boost": round(boosted.get(p, s) / max(conversion_by_page.get(p, 1), 1), 2)
        }
        for p, s in ranked
    ]


def _load_frontmatter_slug(fpath):
    try:
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^---\s*(.*?)\s*---", text, re.DOTALL | re.MULTILINE)
        if not m:
            return {}
        fm_text = m.group(1)
        keys = {}
        for line in fm_text.split("\n"):
            kv = re.match(r"^(slug|path|url|permalink|canonical):\s*[\"']?([^\"'\n]+)[\"']?", line.strip())
            if kv:
                keys[kv.group(1)] = kv.group(2).strip().rstrip("/")
        return keys
    except Exception:
        return {}


def resolve_pagepath_to_file(page_path, content_dirs=None):
    if content_dirs is None:
        content_dirs = ["src/content", "src/pages", "content", "pages", "."]

    page_path = page_path.strip().rstrip("/")
    if page_path == "":
        page_path = "/"

    slug = page_path.lstrip("/")
    slug_parts = [p for p in slug.split("/") if p]
    last_slug = slug_parts[-1] if slug_parts else "index"

    candidates = []
    for d in content_dirs:
        base = Path(d)
        if base.exists():
            candidates.extend(base.rglob("*.md"))
            candidates.extend(base.rglob("*.mdx"))

    # Pass 1: exact frontmatter match
    for fpath in candidates:
        fm = _load_frontmatter_slug(fpath)
        for key in ("slug", "path", "url", "permalink", "canonical"):
            val = fm.get(key, "").lstrip("/").rstrip("/")
            if val and val == slug:
                return fpath, f"frontmatter.{key}={slug}"

    # Pass 2: filename similarity
    for fpath in candidates:
        fname = fpath.stem.lower()
        if fname in (last_slug.lower(), slug.lower(),
                     slug.replace("/", "-").lower(),
                     slug.replace("/", "_").lower()):
            return fpath, f"filename={fname}"

    # Pass 3: directory + index
    for fpath in candidates:
        if fpath.stem.lower() in ("index",) and last_slug:
            parent = fpath.parent.name.lower()
            if parent == last_slug.lower():
                return fpath, f"parent_dir={parent}"

    return None, f"no_match_for:{page_path}"


def _parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}, text

    fm_raw = m.group(1)
    body = text[m.end():]

    fm = {}
    for line in fm_raw.split("\n"):
        kv = re.match(r"^([\w_-]+):\s*(.*)", line)
        if kv:
            key = kv.group(1).strip()
            val = kv.group(2).strip().strip("\"'")
            fm[key] = val
    return fm, body


def _serialize_frontmatter(fm_dict, body):
    lines = ["---"]
    for k, v in fm_dict.items():
        needs_quote = any(c in str(v) for c in (":", "#", "|", ">", "[", "{"))
        if needs_quote:
            lines.append(f'{k}: "{v}"')
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + body


def is_title_weak(title):
    if not title:
        return True
    t = title.strip()
    if len(t) < 8:
        return True
    if WEAK_TITLE_PATTERNS.match(t):
        return True
    return False


def safe_apply_frontmatter(fpath, new_title=None, new_description=None, dry_run=False):
    try:
        original = fpath.read_text(encoding="utf-8", errors="ignore")
        fm, body = _parse_frontmatter(original)
    except Exception as e:
        return False, f"read_error:{e}"

    changed = False
    reasons = []

    if new_title:
        current_title = fm.get("title", fm.get("meta_title", ""))
        if is_title_weak(current_title) or not current_title:
            fm["title"] = new_title
            changed = True
            reasons.append(f"title:'{current_title}'->'{new_title}'")

    if new_description:
        current_desc = fm.get("description", fm.get("meta_description", ""))
        if not current_desc or len(current_desc.strip()) < 20:
            fm["description"] = new_description
            changed = True
            reasons.append("desc:added")

    if not changed:
        return False, "no_change_needed"

    if not dry_run:
        new_content = _serialize_frontmatter(fm, body)
        fpath.write_text(new_content, encoding="utf-8")

    return True, "; ".join(reasons)
