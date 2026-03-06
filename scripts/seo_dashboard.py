#!/usr/bin/env python3
"""
seo_dashboard.py — Dashboard HTML operațional pentru agentul SEO Superparty.

Generează reports/seo/dashboard.html dintr-o singura comanda.
Afiseaza: status agent, pagini money, experimente, budget, skip reasons, policy drift.

Rulare: python scripts/seo_dashboard.py
Output: reports/seo/dashboard.html (deschide in browser)

Pe server Hetzner: poate fi servit pe un port local cu:
  python -m http.server 8080 --directory reports/seo/
  Acces: http://localhost:8080/dashboard.html
"""

import json, os, sqlite3, re
from pathlib import Path
from datetime import date, datetime, timedelta

# ─── Paths ───────────────────────────────────────────────────────────────────
REPORTS_DIR = Path("reports/seo")
MANIFEST_PATH = REPORTS_DIR / "indexing_manifest.json"
DB_PATH = Path(os.environ.get("SEO_DB_PATH", "reports/seo/seo_experiments.db"))
AUDIT_GLOB = "seo_apply_gsc_*.json"
URL_STATES_PATH = REPORTS_DIR / "url_states.json"
OUTPUT = REPORTS_DIR / "dashboard.html"

BASE_URL = "https://www.superparty.ro"

MONEY_PAGES = [
    ("/animatori-petreceri-copii", "🎯 Pilon", "A"),
    ("/petreceri/bucuresti", "🏙️ Hub București", "A"),
    ("/petreceri/ilfov", "🌆 Hub Ilfov", "A"),
    ("/petreceri/sector-1", "📍 Sector 1", "B"),
    ("/petreceri/sector-2", "📍 Sector 2", "B"),
    ("/petreceri/sector-3", "📍 Sector 3", "B"),
    ("/petreceri/sector-4", "📍 Sector 4", "B"),
    ("/petreceri/sector-5", "📍 Sector 5", "B"),
    ("/petreceri/sector-6", "📍 Sector 6", "B"),
]

# ─── Data collectors ─────────────────────────────────────────────────────────

def load_experiments():
    if not DB_PATH.exists():
        return []
    try:
        con = sqlite3.connect(str(DB_PATH))
        con.row_factory = sqlite3.Row
        rows = con.execute("""
            SELECT exp_id, url_path, exp_type, status, started_at, ends_at,
                   variant_a_title, variant_b_title, winner_variant, decision_reason,
                   variant_a_start, variant_b_start, variant_a_end, variant_b_end
            FROM seo_experiments
            ORDER BY started_at DESC LIMIT 20
        """).fetchall()
        con.close()
        return [dict(r) for r in rows]
    except Exception as e:
        return [{"error": str(e)}]

def load_recent_audits():
    """Ultimele apply audit logs."""
    audits = []
    for f in sorted(REPORTS_DIR.glob(AUDIT_GLOB), reverse=True)[:7]:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            data["_file"] = f.name
            audits.append(data)
        except Exception:
            pass
    return audits

def load_url_states():
    if URL_STATES_PATH.exists():
        try:
            return json.loads(URL_STATES_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def load_manifest_stats():
    if not MANIFEST_PATH.exists():
        return {"total": 0, "indexable": 0}
    m = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"total": len(m), "indexable": sum(1 for e in m if e.get("indexable"))}

def get_kill_switch_status():
    switches = {
        "SEO_FREEZE": os.environ.get("SEO_FREEZE", "0"),
        "SEO_FREEZE_APPLY": os.environ.get("SEO_FREEZE_APPLY", "0"),
        "SEO_FREEZE_EXPERIMENTS": os.environ.get("SEO_FREEZE_EXPERIMENTS", "0"),
        "SEO_PILLAR_LOCK": os.environ.get("SEO_PILLAR_LOCK", "0"),
        "SEO_CONTINUOUS": os.environ.get("SEO_CONTINUOUS", "0"),
        "SEO_APPLY_MODE": os.environ.get("SEO_APPLY_MODE", "report"),
        "SEO_ALLOWLIST": os.environ.get("SEO_ALLOWLIST", ""),
        "SEO_DENYLIST": os.environ.get("SEO_DENYLIST", ""),
        "SEO_TIER_A_ONLY": os.environ.get("SEO_TIER_A_ONLY", "0"),
    }
    frozen = switches["SEO_FREEZE"] == "1"
    return switches, frozen

# ─── HTML generation ─────────────────────────────────────────────────────────

def badge(text, color):
    colors = {"green": "#22c55e", "red": "#ef4444", "yellow": "#f59e0b",
              "blue": "#3b82f6", "gray": "#6b7280", "purple": "#a855f7"}
    c = colors.get(color, "#6b7280")
    return f'<span style="background:{c};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600">{text}</span>'

def render_experiment(exp):
    if "error" in exp:
        return f"<tr><td colspan='6' style='color:red'>{exp['error']}</td></tr>"
    status_colors = {
        "RUNNING_A": "blue", "RUNNING_B": "purple",
        "WINNER": "green", "LOSER": "red", "REVERTED": "yellow", "PENDING": "gray"
    }
    color = status_colors.get(exp.get("status", ""), "gray")
    return f"""<tr>
        <td style='font-size:12px'>{exp.get('url_path','')}</td>
        <td>{badge(exp.get('status','?'), color)}</td>
        <td style='font-size:11px'>{(exp.get('variant_a_title','') or '')[:40]}</td>
        <td style='font-size:11px'>{(exp.get('variant_b_title','') or '')[:40]}</td>
        <td style='font-size:12px'>{exp.get('winner_variant','—')}</td>
        <td style='font-size:11px'>{(exp.get('started_at','') or '')[:10]}</td>
    </tr>"""

def render_audit(audit):
    applied = audit.get("applied", [])
    skipped = audit.get("skipped", [])
    skip_reasons = {}
    for s in skipped:
        r = s.get("reason", "unknown")
        skip_reasons[r] = skip_reasons.get(r, 0) + 1
    return f"""<div style='background:#1e293b;padding:12px;border-radius:8px;margin:8px 0'>
        <div style='color:#94a3b8;font-size:11px'>{audit.get('_file','')}</div>
        <div style='margin-top:4px'>
            {badge(f"Aplicate: {len(applied)}", "green")}
            {badge(f"Skip: {len(skipped)}", "gray")}
            {''.join(badge(f"{r}: {n}", "yellow") for r,n in skip_reasons.items())}
        </div>
    </div>"""

def build_dashboard():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    experiments = load_experiments()
    audits = load_recent_audits()
    url_states = load_url_states()
    manifest_stats = load_manifest_stats()
    switches, frozen = get_kill_switch_status()

    active_exp = [e for e in experiments if "RUNNING" in e.get("status", "")]
    rollbacks = [e for e in experiments if e.get("status") in {"REVERTED", "LOSER"}]

    agent_status_color = "#ef4444" if frozen else "#22c55e"
    agent_status_text = "❄️ FROZEN" if frozen else "✅ RUNNING"

    exp_rows = "\n".join(render_experiment(e) for e in experiments[:10])
    audit_blocks = "\n".join(render_audit(a) for a in audits)

    # URL states for money pages
    money_rows = ""
    for path, label, tier in MONEY_PAGES:
        state_data = url_states.get(path, {"state": "eligible"})
        state = state_data.get("state", "eligible") if isinstance(state_data, dict) else state_data
        state_colors = {
            "eligible": "green", "planned": "blue",
            "applied_real": "purple", "winner": "green",
            "frozen": "red", "manual_lock": "red",
            "blocked_cooldown": "yellow", "blocked_budget": "yellow",
            "experiment_A": "blue", "experiment_B": "purple",
            "reverted": "yellow"
        }
        sc = state_colors.get(state, "gray")
        tier_color = {"A": "#22c55e", "B": "#3b82f6", "C": "#a855f7"}.get(tier, "#6b7280")
        money_rows += f"""<tr>
            <td><span style='background:{tier_color};color:#fff;padding:1px 6px;border-radius:4px;font-size:11px'>T{tier}</span></td>
            <td style='color:#e2e8f0'>{label}</td>
            <td style='font-family:monospace;font-size:12px;color:#94a3b8'>{path}</td>
            <td>{badge(state, sc)}</td>
            <td><a href='{BASE_URL}{path}' target='_blank' style='color:#3b82f6;text-decoration:none'>↗</a></td>
        </tr>"""

    switch_badges = ""
    for k, v in switches.items():
        color = "red" if v == "1" else "green" if v == "0" else "blue"
        display = f"{k}={v}" if v not in ("0","") else k
        switch_badges += badge(display, color) + " "

    html = f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SEO Dashboard — Superparty</title>
<meta name="robots" content="noindex,nofollow">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0f172a; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; padding: 20px; }}
  h1 {{ font-size: 22px; font-weight: 700; margin-bottom: 4px; }}
  h2 {{ font-size: 15px; font-weight: 600; color: #94a3b8; margin: 20px 0 8px; text-transform: uppercase; letter-spacing: 1px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 12px 0; }}
  .card {{ background: #1e293b; border-radius: 10px; padding: 16px; }}
  .card-val {{ font-size: 28px; font-weight: 700; }}
  .card-label {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ color: #64748b; text-align: left; padding: 6px 8px; border-bottom: 1px solid #1e293b; font-size: 11px; text-transform: uppercase; }}
  td {{ padding: 8px; border-bottom: 1px solid #1e293b; vertical-align: middle; }}
  tr:hover td {{ background: #1e293b; }}
  .status-bar {{ display: flex; align-items: center; gap: 12px; background: #1e293b; padding: 12px 16px; border-radius: 10px; margin-bottom: 16px; }}
  .status-dot {{ width: 12px; height: 12px; border-radius: 50%; background: {agent_status_color}; box-shadow: 0 0 8px {agent_status_color}; }}
  .ts {{ color: #475569; font-size: 11px; }}
</style>
</head>
<body>
<h1>🎯 SEO Dashboard — Superparty</h1>
<div class='ts'>Generat: {now} | <a href='{BASE_URL}' style='color:#3b82f6'>{BASE_URL}</a></div>

<div class='status-bar' style='margin-top:12px'>
  <div class='status-dot'></div>
  <strong>{agent_status_text}</strong>
  <div style='margin-left:8px;font-size:13px'>{switch_badges}</div>
</div>

<div class='grid'>
  <div class='card'>
    <div class='card-val' style='color:#22c55e'>{len(active_exp)}</div>
    <div class='card-label'>Experimente active</div>
  </div>
  <div class='card'>
    <div class='card-val' style='color:#f59e0b'>{len(rollbacks)}</div>
    <div class='card-label'>Rollback-uri total</div>
  </div>
  <div class='card'>
    <div class='card-val' style='color:#3b82f6'>{manifest_stats.get("indexable",0)}</div>
    <div class='card-label'>URL-uri indexabile</div>
  </div>
  <div class='card'>
    <div class='card-val' style='color:#a855f7'>{len(audits)}</div>
    <div class='card-label'>Cicluri apply (7d)</div>
  </div>
</div>

<h2>📄 Pagini Money — Ownership & Status</h2>
<table>
  <tr><th>Tier</th><th>Pagina</th><th>Path</th><th>Status</th><th>Link</th></tr>
  {money_rows}
</table>

<h2>🧪 Experimente CTR (ultimele 10)</h2>
<table>
  <tr><th>URL</th><th>Status</th><th>Variant A Title</th><th>Variant B Title</th><th>Winner</th><th>Start</th></tr>
  {exp_rows if exp_rows else '<tr><td colspan="6" style="color:#64748b;padding:20px">Niciun experiment în DB.</td></tr>'}
</table>

<h2>📋 Apply Audit Log (ultimele 7 cicluri)</h2>
{audit_blocks if audit_blocks else '<div style="color:#64748b;padding:10px">Niciun audit log găsit în reports/seo/</div>'}

<div style='margin-top:30px;color:#475569;font-size:11px'>
  🔧 Pentru server local: <code>python -m http.server 8080 --directory reports/seo/</code> →
  <a href='http://localhost:8080/dashboard.html' style='color:#3b82f6'>http://localhost:8080/dashboard.html</a>
</div>
</body>
</html>"""

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Dashboard generat: {OUTPUT}")
    print(f"  Agent status: {agent_status_text}")
    print(f"  Experimente active: {len(active_exp)}")
    print(f"  Cicluri audit: {len(audits)}")
    print(f"  URL-uri indexabile: {manifest_stats.get('indexable',0)}")

if __name__ == "__main__":
    build_dashboard()
