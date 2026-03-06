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

def db_migrate(con: sqlite3.Connection) -> None:
    """Add missing columns to seo_experiments (safe for existing DBs on server)."""
    existing_cols = {row[1] for row in con.execute("PRAGMA table_info(seo_experiments)").fetchall()}
    new_cols = {
        "variant_a_start": "TEXT",
        "variant_a_end": "TEXT",
        "variant_a_clicks": "INTEGER DEFAULT 0",
        "variant_a_impressions": "INTEGER DEFAULT 0",
        "variant_a_avg_position": "REAL DEFAULT 99.0",
        "variant_b_start": "TEXT",
        "variant_b_end": "TEXT",
        "variant_b_clicks": "INTEGER DEFAULT 0",
        "variant_b_impressions": "INTEGER DEFAULT 0",
        "variant_b_avg_position": "REAL DEFAULT 99.0",
    }
    for col, col_type in new_cols.items():
        if col not in existing_cols:
            try:
                con.execute(f"ALTER TABLE seo_experiments ADD COLUMN {col} {col_type}")
            except Exception:
                pass
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
    # Latency-safe baseline window (before experiment started)
    baseline_end = started - timedelta(days=3)
    baseline_start = baseline_end - timedelta(days=14)
    # A starts 3 days after apply (GSC latency)
    variant_a_start = started + timedelta(days=3)

    con.execute("""
      INSERT INTO seo_experiments(
        exp_id, site_id, url_path, page_url, file_path,
        exp_type, status,
        started_at, ends_at,
        baseline_start, baseline_end,
        variant_a_start,
        baseline_clicks, baseline_impressions, baseline_avg_position,
        baseline_title, baseline_description,
        variant_a_title, variant_a_description,
        variant_b_title, variant_b_description,
        created_at, updated_at
      ) VALUES (?,?,?,?,?,
                'ctr_title_desc','PLANNED',
                ?,?,
                ?,?,
                ?,
                ?,?,?,
                ?,?,
                ?,?,
                ?,?,
                ?,?
      )
    """, (
        exp_id, site_id, url_path, page_url, file_path,
        str(started), str(ends),
        str(baseline_start), str(baseline_end),
        str(variant_a_start),
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
    db_init(con)
    active = list_active_experiments(con, site_id)
    if len(active) >= max_active:
        return {"ok": True, "note": "max_active_reached"}
        
    # Risk Canary Check:
    active_urls = [a["url_path"] for a in active if a["status"] in ["RUNNING_A", "RUNNING_B", "PLANNED"]]
    if "/animatori-petreceri-copii" in active_urls:
        log.info("Canary experiment running on Pilon. Halting new experiments.")
        return {"ok": True, "note": "canary_active"}

    min_imps = getenv_int("SEO_EXPERIMENTS_MIN_IMPRESSIONS_7D", 80)
    candidates = select_ctr_candidates(site_id, min_impressions=min_imps, max_candidates=10)
    
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
        from agent.tasks.seo import resolve_astro_path
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
    db_init(con)
    db_migrate(con)

    rows = con.execute("SELECT * FROM seo_experiments WHERE site_id=? AND status='PLANNED' LIMIT 1", (site_id,)).fetchall()
    if not rows:
        return {"ok": True, "note": "nothing_planned"}

    exp = dict(rows[0])

    # Apply Variant A (canary start)
    res = apply_title_desc_variant(site_id, exp["url_path"], exp["page_url"], "A",
                                   exp["variant_a_title"], exp["variant_a_description"])

    if res.get("ok"):
        a_start = str(date.today() + timedelta(days=3))  # GSC latency
        update_experiment(con, exp["exp_id"], status="RUNNING_A", variant_a_start=a_start)
        try:
            sf = Path(f"reports/{site_id}/seo_apply_state.json")
            if sf.exists():
                import json as _json
                st = _json.loads(sf.read_text(encoding="utf-8"))
                st["prs_created_today"] = st.get("prs_created_today", 0) + 1
                sf.write_text(_json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    return res

def seo_ctr_experiments_evaluate_task(site_id="superparty"):
    con = db_connect()
    db_init(con)
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
    """Compare A vs B (real two-window A/B) with Wilson + baseline guard + rollback."""
    from agent.common.env import getenv_int

    baseline = {
        "clicks": exp["baseline_clicks"] or 0,
        "impressions": exp["baseline_impressions"] or 0,
        "avg_position": exp["baseline_avg_position"] or 99.0,
    }

    end_date = str(date.today() - timedelta(days=3))  # GSC latency
    gsc_prop = getenv("GSC_PROPERTY", "https://www.superparty.ro/").strip()
    min_imps = getenv_int("SEO_EXPERIMENTS_MIN_VARIANT_IMPRESSIONS", 800)

    status = exp.get("status", "")

    # --- Determine which window to fetch based on status ---
    if status == "RUNNING_A" and exp.get("variant_a_start"):
        # Still in A phase: fetch A metrics so far
        m_a = get_page_metrics_with_fallback(service, gsc_prop, exp["page_url"],
                                              exp["variant_a_start"], end_date)
        if early_stop and m_a["impressions"] < min_imps:
            return  # not enough volume

        # Only baseline vs A at this stage
        decision, reason = decide_experiment(baseline, m_a, min_variant_imps=min_imps)
        update_experiment(con, exp["exp_id"],
            variant_a_clicks=m_a["clicks"],
            variant_a_impressions=m_a["impressions"],
            variant_a_avg_position=m_a["avg_position"]
        )

        if decision == "LOSER":  # A is already a loser vs baseline -> rollback now
            rollback_title_desc(exp["site_id"], exp["url_path"], exp["file_path"],
                                exp["baseline_title"], exp["baseline_description"], reason)
            update_experiment(con, exp["exp_id"], status="REVERTED", winner_variant="baseline", decision_reason=reason)
            upsert_page_state(con, exp["site_id"], exp["url_path"],
                              active_exp_id=None, cooldown_until=str(date.today() + timedelta(days=30)))
        return

    elif status == "RUNNING_B" and exp.get("variant_a_start") and exp.get("variant_b_start"):
        # Both phases available: compare A vs B
        a_end = exp.get("variant_a_end") or str(date.today() - timedelta(days=1))
        m_a = get_page_metrics_with_fallback(service, gsc_prop, exp["page_url"],
                                              exp["variant_a_start"], a_end)
        m_b = get_page_metrics_with_fallback(service, gsc_prop, exp["page_url"],
                                              exp["variant_b_start"], end_date)

        if early_stop and m_b["impressions"] < min_imps:
            return

        # Save metrics
        update_experiment(con, exp["exp_id"],
            variant_a_clicks=m_a["clicks"],
            variant_a_impressions=m_a["impressions"],
            variant_a_avg_position=m_a["avg_position"],
            variant_b_clicks=m_b["clicks"],
            variant_b_impressions=m_b["impressions"],
            variant_b_avg_position=m_b["avg_position"],
            variant_b_end=end_date
        )

        # --- Wilson comparison: A vs B ---
        a_low, a_high = wilson_interval(m_a["clicks"], m_a["impressions"])
        b_low, b_high = wilson_interval(m_b["clicks"], m_b["impressions"])
        b_ctr = m_b["clicks"] / max(1, m_b["impressions"])
        a_ctr = m_a["clicks"] / max(1, m_a["impressions"])
        base_ctr = baseline["clicks"] / max(1, baseline["impressions"])

        min_rel_lift = 0.15  # +15% CTR relative
        max_pos_drop_winner = 1.5
        max_pos_drop_loser = 2.0

        b_vs_baseline_drop = m_b["avg_position"] - baseline["avg_position"]
        a_vs_baseline_drop = m_a["avg_position"] - baseline["avg_position"]

        # Hard rollback: both lost rank significantly vs baseline
        if b_vs_baseline_drop > max_pos_drop_loser and a_vs_baseline_drop > max_pos_drop_loser:
            reason = f"both_losers_vs_baseline pos_drop_b:{b_vs_baseline_drop:.1f} a:{a_vs_baseline_drop:.1f}"
            rollback_title_desc(exp["site_id"], exp["url_path"], exp["file_path"],
                                exp["baseline_title"], exp["baseline_description"], reason)
            update_experiment(con, exp["exp_id"], status="REVERTED", winner_variant="baseline", decision_reason=reason)
            upsert_page_state(con, exp["site_id"], exp["url_path"],
                              active_exp_id=None, cooldown_until=str(date.today() + timedelta(days=30)))
            return

        # B wins over A
        if (b_ctr >= a_ctr * (1 + min_rel_lift) and
                b_low > a_high and
                b_vs_baseline_drop <= max_pos_drop_winner):
            reason = f"B_wins_A lift:{(b_ctr-a_ctr)/max(a_ctr,1e-9):.1%} b_low:{b_low:.4f}>a_high:{a_high:.4f}"
            # B is already applied; just mark winner
            update_experiment(con, exp["exp_id"], status="WINNER", winner_variant="B", decision_reason=reason)
            upsert_page_state(con, exp["site_id"], exp["url_path"],
                              active_exp_id=None, cooldown_until=str(date.today() + timedelta(days=14)))
            return

        # A wins over B -> revert to A
        if (a_ctr >= b_ctr * (1 + min_rel_lift) and
                a_low > b_high and
                a_vs_baseline_drop <= max_pos_drop_winner):
            reason = f"A_wins_B lift:{(a_ctr-b_ctr)/max(b_ctr,1e-9):.1%} a_low:{a_low:.4f}>b_high:{b_high:.4f}"
            apply_title_desc_variant(exp["site_id"], exp["url_path"], exp["page_url"], "A",
                                     exp["variant_a_title"], exp["variant_a_description"])
            update_experiment(con, exp["exp_id"], status="WINNER", winner_variant="A", decision_reason=reason)
            upsert_page_state(con, exp["site_id"], exp["url_path"],
                              active_exp_id=None, cooldown_until=str(date.today() + timedelta(days=14)))
            return

        # Both variants worse than baseline CTR significantly
        if b_ctr < base_ctr * 0.85 and a_ctr < base_ctr * 0.85:
            reason = f"both_losers_vs_baseline_ctr b:{b_ctr:.3f} a:{a_ctr:.3f} base:{base_ctr:.3f}"
            rollback_title_desc(exp["site_id"], exp["url_path"], exp["file_path"],
                                exp["baseline_title"], exp["baseline_description"], reason)
            update_experiment(con, exp["exp_id"], status="REVERTED", winner_variant="baseline", decision_reason=reason)
            upsert_page_state(con, exp["site_id"], exp["url_path"],
                              active_exp_id=None, cooldown_until=str(date.today() + timedelta(days=30)))
            return

        if not early_stop:
            # Timeout with no clear winner: rollback to baseline (conservative)
            reason = f"inconclusive_timeout b:{b_ctr:.3f} a:{a_ctr:.3f} base:{base_ctr:.3f}"
            rollback_title_desc(exp["site_id"], exp["url_path"], exp["file_path"],
                                exp["baseline_title"], exp["baseline_description"], reason)
            update_experiment(con, exp["exp_id"], status="REVERTED", winner_variant="baseline", decision_reason=reason)
            upsert_page_state(con, exp["site_id"], exp["url_path"],
                              active_exp_id=None, cooldown_until=str(date.today() + timedelta(days=14)))


def seo_ctr_experiments_switch_task(site_id="superparty"):
    """Switch from Variant A to Variant B, recording A end date and B start date with GSC latency."""
    from agent.common.env import getenv_int
    from datetime import datetime

    con = db_connect()
    db_init(con)
    db_migrate(con)

    rows = con.execute(
        "SELECT * FROM seo_experiments WHERE site_id=? AND status='RUNNING_A'",
        (site_id,)
    ).fetchall()

    switched = 0
    for r in rows:
        exp = dict(r)

        # Check if enough days elapsed since A's effective start
        a_start_str = exp.get("variant_a_start")
        if not a_start_str:
            continue
        a_start = datetime.strptime(a_start_str, "%Y-%m-%d").date()
        days_running_a = (date.today() - a_start).days

        switch_days = getenv_int("SEO_EXPERIMENTS_SWITCH_DAYS", 10)
        if days_running_a < switch_days:
            continue

        # Apply Variant B
        res = apply_title_desc_variant(
            site_id, exp["url_path"], exp["page_url"], "B",
            exp["variant_b_title"], exp["variant_b_description"]
        )

        if res.get("ok"):
            switch_date = date.today()
            # A window ends yesterday (last full day of A)
            variant_a_end = str(switch_date - timedelta(days=1))
            # B window starts 3 days after switch (GSC latency)
            variant_b_start = str(switch_date + timedelta(days=3))

            update_experiment(con, exp["exp_id"],
                status="RUNNING_B",
                variant_a_end=variant_a_end,
                variant_b_start=variant_b_start
            )
            switched += 1

            try:
                import json as _json
                sf = Path(f"reports/{site_id}/seo_apply_state.json")
                if sf.exists():
                    st = _json.loads(sf.read_text(encoding="utf-8"))
                    st["prs_created_today"] = st.get("prs_created_today", 0) + 1
                    sf.write_text(_json.dumps(st, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass

    return {"ok": True, "switched": switched}
