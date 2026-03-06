import sqlite3, json, uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import math
import re
from collections import defaultdict
from agent.common.env import getenv_int, getenv

DB_PATH = Path("reports/superparty/seo_experiments.db")

def db_connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    return con

def db_init(con: sqlite3.Connection) -> None:
    ddl = Path("agent/tasks/ddl_seo_experiments.sql").read_text(encoding="utf-8")
    con.executescript(ddl)
    con.commit()

def now_ymd() -> str:
    return str(date.today())

def upsert_page_state(con, site_id: str, url_path: str, **fields) -> None:
    # fields: last_touched_at, cooldown_until, active_exp_id
    cur = con.execute("SELECT 1 FROM page_state WHERE site_id=? AND url_path=?", (site_id, url_path))
    exists = cur.fetchone() is not None
    if not exists:
        con.execute(
            "INSERT INTO page_state(site_id,url_path,last_touched_at,cooldown_until,active_exp_id) VALUES (?,?,?,?,?)",
            (site_id, url_path, fields.get("last_touched_at"), fields.get("cooldown_until"), fields.get("active_exp_id"))
        )
    else:
        sets, vals = [], []
        for k, v in fields.items():
            sets.append(f"{k}=?")
            vals.append(v)
        vals.extend([site_id, url_path])
        con.execute(f"UPDATE page_state SET {', '.join(sets)} WHERE site_id=? AND url_path=?", tuple(vals))
    con.commit()

def get_page_state(con, site_id: str, url_path: str) -> Dict[str, Any]:
    row = con.execute(
        "SELECT * FROM page_state WHERE site_id=? AND url_path=?",
        (site_id, url_path)
    ).fetchone()
    return dict(row) if row else {}

def list_active_experiments(con, site_id: str) -> List[Dict[str, Any]]:
    rows = con.execute(
        "SELECT * FROM seo_experiments WHERE site_id=? AND status IN ('PLANNED','RUNNING_A','RUNNING_B','EVALUATING')",
        (site_id,)
    ).fetchall()
    return [dict(r) for r in rows]

def create_experiment(con, site_id: str, url_path: str, page_url: str, file_path: str,
                      baseline: Dict[str, Any],
                      baseline_title: str, baseline_description: str,
                      varA: Dict[str, str], varB: Dict[str, str],
                      duration_days: int = 21) -> str:
    exp_id = str(uuid.uuid4())
    started = date.today()
    ends = started + timedelta(days=duration_days)
    # latency-safe windows:
    baseline_end = started - timedelta(days=3)
    baseline_start = baseline_end - timedelta(days=14)
    variant_start = started + timedelta(days=3)

    con.execute("""
      INSERT INTO seo_experiments(
        exp_id, site_id, url_path, page_url, file_path,
        exp_type, status,
        started_at, ends_at,
        baseline_start, baseline_end, variant_start,
        baseline_clicks, baseline_impressions, baseline_avg_position,
        baseline_title, baseline_description,
        variant_a_title, variant_a_description,
        variant_b_title, variant_b_description,
        created_at, updated_at
      ) VALUES (?,?,?,?,?,
                'ctr_title_desc','PLANNED',
                ?,?,
                ?,?,?,
                ?,?,?,
                ?,?,
                ?,?,
                ?,?,
                ?,?
      )
    """, (
        exp_id, site_id, url_path, page_url, file_path,
        str(started), str(ends),
        str(baseline_start), str(baseline_end), str(variant_start),
        int(baseline["clicks"]), int(baseline["impressions"]), float(baseline["avg_position"]),
        baseline_title, baseline_description,
        varA["title"], varA["description"],
        varB["title"], varB["description"],
        now_ymd(), now_ymd()
    ))
    con.commit()
    upsert_page_state(con, site_id, url_path, active_exp_id=exp_id, cooldown_until=str(ends + timedelta(days=14)))
    return exp_id

def update_experiment(con, exp_id: str, **fields) -> None:
    sets, vals = [], []
    fields["updated_at"] = now_ymd()
    for k, v in fields.items():
        sets.append(f"{k}=?")
        vals.append(v)
    vals.append(exp_id)
    con.execute(f"UPDATE seo_experiments SET {', '.join(sets)} WHERE exp_id=?", tuple(vals))
    con.commit()

def get_experiment(con, exp_id: str) -> Dict[str, Any]:
    row = con.execute("SELECT * FROM seo_experiments WHERE exp_id=?", (exp_id,)).fetchone()
    return dict(row) if row else {}

def normalize_to_path(page_url: str) -> str:
    if not page_url: return ""
    p = page_url.replace("https://www.superparty.ro", "").replace("https://superparty.ro", "")
    p = p.split("?")[0]
    if not p.startswith("/"): p = "/" + p
    return p.rstrip("/") if p != "/" else "/"

def load_page_metrics_from_index(site_id="superparty") -> Dict[str, Dict[str, float]]:
    idx = Path(f"reports/{site_id}/gsc/index.json")
    rows = json.loads(idx.read_text(encoding="utf-8")) if idx.exists() else []
    agg = defaultdict(lambda: {"clicks":0, "impressions":0, "pos_weighted_sum":0.0})
    for r in rows:
        page = normalize_to_path(r.get("page",""))
        imp = int(r.get("impressions",0))
        clk = int(r.get("clicks",0))
        pos = float(r.get("avg_position",99))
        agg[page]["clicks"] += clk
        agg[page]["impressions"] += imp
        agg[page]["pos_weighted_sum"] += pos * max(imp,1)

    out = {}
    for page, a in agg.items():
        imps = a["impressions"]
        out[page] = {
            "clicks": a["clicks"],
            "impressions": imps,
            "avg_position": round(a["pos_weighted_sum"]/max(imps,1), 2),
            "ctr": (a["clicks"]/max(imps,1))
        }
    return out

def page_type_from_path(path: str) -> str:
    if path == "/animatori-petreceri-copii": return "pilon"
    if path == "/petreceri/ilfov": return "hub_ilfov"
    if path == "/petreceri/bucuresti": return "hub_bucuresti"
    if path.startswith("/petreceri/sector-"): return "sector"
    if path.startswith("/petreceri/"): return "local_or_service"
    return "other"

def load_indexable_paths_from_manifest() -> set:
    mp = Path("reports/seo/indexing_manifest.json")
    if not mp.exists(): return set()
    data = json.loads(mp.read_text(encoding="utf-8"))
    out = set()
    for m in data:
        if m.get("indexable") is True:
            slug = m.get("slug")
            p = m.get("path") or (f"/petreceri/{slug}" if slug else None)
            if p: out.add(p.rstrip("/"))
    # include pilon explicitly
    out.add("/animatori-petreceri-copii")
    out.add("/petreceri/ilfov")
    out.add("/petreceri/bucuresti")
    return out

def select_ctr_candidates(site_id="superparty",
                          min_impressions=80,
                          pos_min=2.0, pos_max=20.0,
                          max_candidates=10) -> list:
    metrics = load_page_metrics_from_index(site_id)
    indexable = load_indexable_paths_from_manifest()

    eligible = []
    for path, m in metrics.items():
        if path not in indexable: 
            continue
        if not (path == "/animatori-petreceri-copii" or path.startswith("/petreceri/")):
            continue
        if m["impressions"] < min_impressions:
            continue
        if not (pos_min <= m["avg_position"] <= pos_max):
            continue
        eligible.append({"url_path": path, **m, "page_type": page_type_from_path(path)})

    # cluster medians
    by_type = {}
    for t in set(x["page_type"] for x in eligible):
        ctrs = sorted(x["ctr"] for x in eligible if x["page_type"] == t)
        if ctrs:
            by_type[t] = ctrs[len(ctrs)//2]
        else:
            by_type[t] = 0.0

    # CTR-gap: sub median - 0.3pp OR sub 70% din median
    candidates = []
    for x in eligible:
        median = by_type.get(x["page_type"], 0.0)
        if median <= 0:
            continue
        if x["ctr"] < (median - 0.003) or x["ctr"] < (median * 0.70):
            candidates.append(x)

    # prioritize by impressions desc, then pos asc
    candidates.sort(key=lambda r: (-r["impressions"], r["avg_position"]))
    return candidates[:max_candidates]

def wilson_interval(clicks: int, impressions: int, z: float = 1.96) -> tuple:
    # returns (low, high) for CTR proportion
    if impressions <= 0:
        return (0.0, 0.0)
    phat = clicks / impressions
    denom = 1 + (z*z)/impressions
    center = (phat + (z*z)/(2*impressions)) / denom
    margin = (z * math.sqrt((phat*(1-phat) + (z*z)/(4*impressions)) / impressions)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))

def decide_experiment(baseline, variant,
                      min_variant_imps=800,
                      min_rel_lift=0.15,
                      max_pos_drop_winner=1.5,
                      max_pos_drop_loser=2.0) -> tuple:
    b_ctr = baseline["clicks"] / max(1, baseline["impressions"])
    v_ctr = variant["clicks"] / max(1, variant["impressions"])
    rel = (v_ctr - b_ctr) / max(b_ctr, 1e-9)
    pos_drop = variant["avg_position"] - baseline["avg_position"]

    if variant["impressions"] < min_variant_imps:
        return ("WAIT", f"insufficient_impressions:{variant['impressions']}")

    b_low, b_high = wilson_interval(baseline["clicks"], baseline["impressions"])
    v_low, v_high = wilson_interval(variant["clicks"], variant["impressions"])

    # LOSER hard if rank tanks
    if pos_drop > max_pos_drop_loser:
        return ("LOSER", f"pos_drop_hard:{pos_drop:.2f}")

    # WINNER
    if rel >= min_rel_lift and pos_drop <= max_pos_drop_winner and v_low > b_high:
        return ("WINNER", f"rel_lift:{rel:.2%} pos_drop:{pos_drop:.2f} wilson:{v_low:.4f}>{b_high:.4f}")

    # LOSER significant ctr drop
    if (v_ctr <= b_ctr or rel < 0) and (v_high < b_low):
        return ("LOSER", f"ctr_drop_sig rel:{rel:.2%} wilson:{v_high:.4f}<{b_low:.4f}")

    return ("INCONCLUSIVE", f"rel:{rel:.2%} pos_drop:{pos_drop:.2f} wilson_b:[{b_low:.4f},{b_high:.4f}] v:[{v_low:.4f},{v_high:.4f}]")

def gsc_query_page_metrics(service, site_prop: str, page_url: str, start: str, end: str) -> dict:
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": ["page"],
        "rowLimit": 250,
        "dimensionFilterGroups": [{
            "filters": [{
                "dimension": "page",
                "operator": "equals",
                "expression": page_url
            }]
        }]
    }
    resp = service.searchanalytics().query(siteUrl=site_prop, body=body).execute()
    rows = resp.get("rows", [])
    if not rows:
        return {"clicks":0, "impressions":0, "avg_position":99.0}
    r = rows[0]
    return {"clicks": int(r.get("clicks",0)), "impressions": int(r.get("impressions",0)), "avg_position": float(r.get("position",99.0))}

def get_page_metrics_with_fallback(service, gsc_property: str, page_url: str, start: str, end: str) -> dict:
    host = gsc_property.replace("https://","").replace("http://","").rstrip("/")
    candidates = [f"sc-domain:{host}", gsc_property]
    last = {"clicks":0,"impressions":0,"avg_position":99.0}
    for prop in candidates:
        try:
            m = gsc_query_page_metrics(service, prop, page_url, start, end)
            # accept first non-zero, else keep last
            if m["impressions"] > 0:
                return m
            last = m
        except Exception:
            continue
    return last

def extract_layout_title_desc(text: str) -> tuple:
    m = re.search(r"<Layout\\b[\\s\\S]*?>", text)
    if not m:
        return ("","")
    tag = m.group(0)
    t = re.search(r'\\btitle\\s*=\\s*"([^"]*)"', tag)
    d = re.search(r'\\bdescription\\s*=\\s*"([^"]*)"', tag)
    title = t.group(1) if t else ""
    desc = d.group(1) if d else ""
    return (title, desc)

def apply_title_desc_variant(site_id: str, url_path: str, page_url: str, variant: str, title: str, desc: str) -> dict:
    from agent.common.git_pr import git_commit_push_pr
    from agent.tasks.seo import patch_layout_title_description, resolve_astro_path
    
    fpath = resolve_astro_path(url_path)
    if not fpath:
        return {"ok": False, "reason": "unmapped", "url_path": url_path}

    text = Path(str(fpath)).read_text(encoding="utf-8", errors="ignore")
    new_text = patch_layout_title_description(text, title, desc)
    if new_text == text:
        return {"ok": True, "note": "no_change"}

    Path(str(fpath)).write_text(new_text, encoding="utf-8")

    import time
    run_id = time.strftime("%H%M%S")
    branch = f"agent/seo-ctr-{variant}-{date.today()}T{run_id}Z"
    pr_url = git_commit_push_pr(
        branch=branch,
        commit_msg=f"feat(seo): ctr exp {variant} {url_path} {date.today()}T{run_id}Z",
        files=[str(fpath)],
        pr_title=f"SEO CTR Experiment {variant}: {url_path}",
        pr_body=f"Apply {variant} title/desc for CTR experiment on {url_path} (PR-only)."
    )
    return {"ok": True, "pr_url": pr_url, "file": str(fpath)}

def rollback_title_desc(site_id: str, url_path: str, file_path: str, old_title: str, old_desc: str, reason: str) -> dict:
    from agent.common.git_pr import git_commit_push_pr
    from agent.tasks.seo import patch_layout_title_description
    
    p = Path(file_path)
    text = p.read_text(encoding="utf-8", errors="ignore")
    new_text = patch_layout_title_description(text, old_title, old_desc)
    if new_text == text:
        return {"ok": True, "note": "already_rolled_back"}

    p.write_text(new_text, encoding="utf-8")

    import time
    run_id = time.strftime("%H%M%S")
    branch = f"agent/seo-ctr-rollback-{date.today()}T{run_id}Z"
    pr_url = git_commit_push_pr(
        branch=branch,
        commit_msg=f"fix(seo): auto-rollback ctr exp {url_path} {date.today()}T{run_id}Z",
        files=[str(p)],
        pr_title=f"fix(seo_agent): Auto-rollback {url_path} (CTR/Rank)",
        pr_body=f"Auto-rollback based on experiment evaluation.\\nReason: {reason}"
    )
    return {"ok": True, "pr_url": pr_url}
