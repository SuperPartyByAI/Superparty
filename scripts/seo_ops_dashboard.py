"""
SEO Ops Dashboard Generator — L6/L7 + L5 Audit Trail

Generates a static HTML dashboard at reports/superparty/ops_dashboard.html
by reading EXCLUSIVELY from source-of-truth artefacts (read-only).

Sources consumed — L7/L6 Ops Health:
    reports/superparty/gsc_collection_ledger.json      → L7 run history
    reports/superparty/seo_report_worker_status.json   → L6 last run status
    reports/superparty/seo_reports_ledger.json         → L6 run history
    reports/superparty/seo_cluster_health.json         → freshness
    reports/superparty/seo_cluster_priority.json       → freshness
    reports/superparty/seo_trend_delta.json            → freshness + baseline flag
    reports/superparty/gsc/collect_*.json  (latest)   → raw snapshot metadata

Sources consumed — L5 Planning / Apply / Rollback Audit Trail:
    reports/superparty/seo_level5_dry_run_actions.json → proposals
    reports/superparty/seo_level5_approval_log.json    → approval decisions
    reports/superparty/seo_level5_apply_plan.json      → apply plan (ready / blocked)
    reports/superparty/seo_level5_apply_execution.json → applied changes
    reports/superparty/seo_level5_rollback_payload.json  → rollback payload
    reports/superparty/seo_level5_rollback_execution.json → rollback executions

Does NOT touch:
    scripts/seo_dashboard.py     (legacy, untouched)
    reports/seo/                 (legacy, untouched)
    Apply Plane                  (untouched)
    src/pages                    (untouched)
"""

from __future__ import annotations

import json
import os
import sys
import glob
import html
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# ─── Paths (relative to repo root, used both locally and on Hetzner) ────────

ROOT = Path(__file__).parent.parent
REPORTS = ROOT / "reports" / "superparty"

L7_LEDGER = REPORTS / "gsc_collection_ledger.json"
L6_STATUS = REPORTS / "seo_report_worker_status.json"
L6_LEDGER = REPORTS / "seo_reports_ledger.json"
HEALTH_JSON = REPORTS / "seo_cluster_health.json"
PRIORITY_JSON = REPORTS / "seo_cluster_priority.json"
TREND_JSON = REPORTS / "seo_trend_delta.json"
GSC_SNAPSHOTS_GLOB = str(REPORTS / "gsc" / "collect_*.json")

# ─── L5 Paths (read-only) ────────────────────────────────────────────────────
L5_DRY_RUN    = REPORTS / "seo_level5_dry_run_actions.json"
L5_APPROVAL   = REPORTS / "seo_level5_approval_log.json"
L5_APPLY_PLAN = REPORTS / "seo_level5_apply_plan.json"
L5_APPLY_EXEC = REPORTS / "seo_level5_apply_execution.json"
L5_ROLLBACK_PAYLOAD  = REPORTS / "seo_level5_rollback_payload.json"
L5_ROLLBACK_EXEC     = REPORTS / "seo_level5_rollback_execution.json"

OUTPUT_HTML = REPORTS / "ops_dashboard.html"

# ─── Freshness thresholds (mirror readiness.py definitions) ─────────────────
FRESH_HOURS = {
    "health":   48,
    "priority": 48,
    "trends":   72,
}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _read_json(path: Path) -> dict | list | None:
    """Read and parse a JSON file. Returns None on any error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _age_hours(iso_str: str | None) -> float | None:
    """Return age in hours since an ISO timestamp. None if unparseable."""
    if not iso_str:
        return None
    try:
        ts = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return (_now() - ts).total_seconds() / 3600
    except ValueError:
        return None


def _freshness_verdict(age_h: float | None, max_h: int) -> str:
    """Returns 'ready', 'warning', or 'stale'."""
    if age_h is None:
        return "stale"
    if age_h > max_h:
        return "stale"
    if age_h > max_h * 0.75:
        return "warning"
    return "ready"


def _fmt_age(age_h: float | None) -> str:
    if age_h is None:
        return "N/A"
    if age_h < 1:
        return f"{int(age_h * 60)} min"
    return f"{age_h:.1f}h"


def _latest_snapshot() -> dict | None:
    """Return parsed metadata of the most recent collect_*.json."""
    files = sorted(glob.glob(GSC_SNAPSHOTS_GLOB))
    if not files:
        return None
    data = _read_json(Path(files[-1]))
    if not data:
        return None
    meta = data.get("metadata", {})
    meta["_filename"] = os.path.basename(files[-1])
    return meta


# ─── Data collection ─────────────────────────────────────────────────────────

def collect_l7() -> dict:
    """Parse L7 collection ledger."""
    raw = _read_json(L7_LEDGER)
    if not isinstance(raw, list) or not raw:
        return {"ok": False, "last": None, "history": [], "error": "Ledger missing or empty"}
    entries = sorted(raw, key=lambda x: x.get("collected_at", ""))
    last = entries[-1]
    return {
        "ok": True,
        "last": last,
        "history": entries[-5:],
    }


def collect_l6() -> dict:
    """Parse L6 worker status and ledger."""
    status = _read_json(L6_STATUS)
    ledger_raw = _read_json(L6_LEDGER)
    history = []
    if isinstance(ledger_raw, list) and ledger_raw:
        history = sorted(ledger_raw, key=lambda x: x.get("timestamp", ""))[-5:]
    return {
        "ok": status is not None,
        "status": status or {},
        "history": history,
    }


def collect_freshness() -> dict:
    """Check freshness of the three main output artefacts."""
    results = {}
    for key, path, max_h in [
        ("health",   HEALTH_JSON,   FRESH_HOURS["health"]),
        ("priority", PRIORITY_JSON, FRESH_HOURS["priority"]),
        ("trends",   TREND_JSON,    FRESH_HOURS["trends"]),
    ]:
        data = _read_json(path)
        if data is None:
            results[key] = {"verdict": "stale", "generated_at": None, "age": None, "missing": True}
            continue
        meta = data.get("metadata", {})
        ts = meta.get("generated_at") or meta.get("priority_generated_at")
        age_h = _age_hours(ts)
        results[key] = {
            "verdict": _freshness_verdict(age_h, max_h),
            "generated_at": ts,
            "age": _fmt_age(age_h),
            "missing": False,
        }
    return results


def collect_trend_flags(freshness: dict) -> dict:
    """Pull trend-specific flags (baseline_only, etc.)."""
    data = _read_json(TREND_JSON)
    if not data:
        return {"baseline_only": None, "available": False}
    meta = data.get("metadata", {})
    return {
        "available": True,
        "baseline_only": meta.get("baseline_only", False),
        "schema_version": meta.get("schema_version"),
    }


# ─── L5 Data collectors (strictly read-only) ─────────────────────────────────

def collect_l5_proposals() -> dict:
    """Parse dry-run proposals from seo_level5_dry_run_actions.json."""
    raw = _read_json(L5_DRY_RUN)
    if not raw:
        return {"available": False, "actions": [], "generated_at": None, "total": 0}
    actions = raw.get("actions", [])
    meta = raw.get("metadata", {})
    return {
        "available": True,
        "actions": actions,
        "generated_at": meta.get("generated_at"),
        "total": meta.get("total_candidates", len(actions)),
        "mode": meta.get("mode", "—"),
    }


def collect_l5_approval() -> dict:
    """Parse approval log and apply plan."""
    approval_log = _read_json(L5_APPROVAL)
    if not isinstance(approval_log, list):
        approval_log = []
    apply_plan_raw = _read_json(L5_APPLY_PLAN)
    plan = []
    blocked = []
    ready_to_apply = False
    plan_generated_at = None
    if apply_plan_raw and isinstance(apply_plan_raw, dict):
        plan = apply_plan_raw.get("plan", [])
        blocked = apply_plan_raw.get("blocked", [])
        ready_to_apply = apply_plan_raw.get("preflight", {}).get("ready_to_apply", False)
        plan_generated_at = apply_plan_raw.get("generated_at")
    return {
        "approval_log": approval_log,
        "approved": [e for e in approval_log if e.get("decision") == "approved"],
        "rejected": [e for e in approval_log if e.get("decision") == "rejected"],
        "plan": plan,
        "blocked": blocked,
        "ready_to_apply": ready_to_apply,
        "plan_generated_at": plan_generated_at,
    }


def collect_l5_execution() -> dict:
    """Parse apply execution and rollback artefacts."""
    apply_exec   = _read_json(L5_APPLY_EXEC)
    rollback_pay = _read_json(L5_ROLLBACK_PAYLOAD)
    rollback_exec = _read_json(L5_ROLLBACK_EXEC)
    return {
        "apply_exec":    apply_exec,
        "rollback_payload": rollback_pay,
        "rollback_exec": rollback_exec,
    }


# ─── Verdict engine ──────────────────────────────────────────────────────────

def compute_verdict(l7: dict, l6: dict, freshness: dict) -> str:
    """
    Returns 'GREEN', 'YELLOW', or 'RED'.
    Rules are derived 1-to-1 from the SOP (docs/runbooks/seo/agent_operations_sop.md).
    """
    # ── RED conditions ────────────────────────────────────────────────────────
    if not l7["ok"]:
        return "RED"
    if not l6["ok"]:
        return "RED"
    last_l7 = l7.get("last") or {}
    if last_l7.get("status", "").upper() == "FAILED":
        return "RED"
    l6_status = l6.get("status", {})
    if l6_status.get("overall_status", "").lower() == "failed":
        return "RED"
    if any(f.get("missing") for f in freshness.values()):
        return "RED"
    if any(f.get("verdict") == "stale" for f in freshness.values()):
        return "RED"

    # ── YELLOW conditions ─────────────────────────────────────────────────────
    if last_l7.get("status", "").upper() not in ("SUCCESS", "FAILED"):
        return "YELLOW"
    if l6_status.get("overall_status", "").lower() not in ("success", "failed"):
        return "YELLOW"
    if any(f.get("verdict") == "warning" for f in freshness.values()):
        return "YELLOW"
    l6_history = l6.get("history", [])
    if any(e.get("status", "").lower() == "partial_failure" for e in l6_history[-3:]):
        return "YELLOW"

    return "GREEN"


# ─── HTML rendering ──────────────────────────────────────────────────────────

_VERDICT_COLOR = {"GREEN": "#22c55e", "YELLOW": "#eab308", "RED": "#ef4444"}
_VERDICT_LABEL = {"GREEN": "🟢 VERDE — System Operational", "YELLOW": "🟡 GALBEN — Atenție", "RED": "🔴 ROȘU — Incident Activ"}
_STATUS_PILL = {
    "success": '<span class="pill green">SUCCESS</span>',
    "failed":  '<span class="pill red">FAILED</span>',
    "partial_failure": '<span class="pill yellow">PARTIAL_FAILURE</span>',
    "skipped": '<span class="pill grey">SKIPPED</span>',
    "ready":   '<span class="pill green">ready</span>',
    "warning": '<span class="pill yellow">warning</span>',
    "stale":   '<span class="pill red">stale</span>',
}


def _pill(s: str) -> str:
    return _STATUS_PILL.get(str(s).lower(), f'<span class="pill grey">{html.escape(str(s))}</span>')


def _row(label: str, value: str) -> str:
    return f'<tr><td class="label">{html.escape(label)}</td><td>{value}</td></tr>'


def _section(title: str, rows: list[str]) -> str:
    inner = "\n".join(rows)
    return f"""
<section>
  <h2>{html.escape(title)}</h2>
  <table>{inner}</table>
</section>"""


def _history_table(entries: list, cols: list[tuple]) -> str:
    if not entries:
        return "<p class='dim'>No history available.</p>"
    headers = "".join(f"<th>{html.escape(h)}</th>" for (h, _) in cols)
    rows_html = ""
    for e in reversed(entries):
        cells = "".join(f"<td>{_pill(e.get(k,'')) if is_pill else html.escape(str(e.get(k,'—')))}</td>"
                        for (_, k), is_pill in [(c, c[1] in ("status",)) for c in cols])
        rows_html += f"<tr>{cells}</tr>"
    return f"<table class='hist'><tr>{headers}</tr>{rows_html}</table>"


def render_html(l7: dict, l6: dict, freshness: dict, snapshot: dict | None, trend_flags: dict, verdict: str,
                l5_proposals: dict | None = None, l5_approval: dict | None = None, l5_execution: dict | None = None) -> str:
    now_str = _now().strftime("%Y-%m-%d %H:%M UTC")
    vc = _VERDICT_COLOR[verdict]
    vl = _VERDICT_LABEL[verdict]

    # ── A. Source Acquisition (L7) ────────────────────────────────────────────
    last7 = l7.get("last") or {}
    l7_rows = [
        _row("Status", _pill(last7.get("status", "N/A"))),
        _row("Run time", html.escape(last7.get("collected_at", "—")[:19].replace("T", " "))),
        _row("Row count", html.escape(str(last7.get("row_count", "N/A")))),
        _row("Snapshot file", html.escape(last7.get("snapshot_filename", "N/A"))),
        _row("Failing stage", html.escape(str(last7.get("failing_stage") or "—"))),
        _row("Error reason", html.escape(str(last7.get("error_reason") or "—"))),
    ]
    l7_hist = _history_table(
        l7["history"],
        [("Run time", "collected_at"), ("Status", "status"), ("Rows", "row_count"), ("Snapshot", "snapshot_filename")]
    )

    # ── B. Report Plane (L6) ─────────────────────────────────────────────────
    s6 = l6.get("status", {})
    l6_rows = [
        _row("Overall status", _pill(s6.get("overall_status", "N/A"))),
        _row("Health", _pill(s6.get("health", "N/A"))),
        _row("Priority", _pill(s6.get("priority", "N/A"))),
        _row("Trend", _pill(s6.get("trend", "N/A"))),
        _row("Ledger status", _pill(s6.get("ledger_status", "N/A"))),
        _row("Run at", html.escape(str(s6.get("run_at", "—"))[:19].replace("T", " "))),
    ]
    l6_hist = _history_table(
        l6["history"],
        [("Run time", "timestamp"), ("Status", "status"), ("Health", "health_status"), ("Priority", "priority_status"), ("Trend", "trend_status")]
    )

    # ── C. Freshness ─────────────────────────────────────────────────────────
    freshness_rows = []
    for key in ("health", "priority", "trends"):
        f = freshness.get(key, {})
        freshness_rows += [
            _row(f"{key.capitalize()} generated_at", html.escape(str(f.get("generated_at") or "—")[:19].replace("T", " "))),
            _row(f"{key.capitalize()} age", html.escape(f.get("age", "N/A"))),
            _row(f"{key.capitalize()} status", _pill(f.get("verdict", "stale"))),
        ]

    # ── D. Latest Raw Snapshot ────────────────────────────────────────────────
    if snapshot:
        snap_rows = [
            _row("Filename", html.escape(snapshot.get("_filename", "—"))),
            _row("Collected at", html.escape(str(snapshot.get("collected_at", "—"))[:19].replace("T", " "))),
            _row("Property", html.escape(snapshot.get("property", "—"))),
            _row("Row count", html.escape(str(snapshot.get("row_count", "N/A")))),
            _row("Schema version", html.escape(str(snapshot.get("schema_version", "—")))),
            _row("Source", html.escape(snapshot.get("source", "—"))),
        ]
    else:
        snap_rows = [_row("Status", '<span class="pill red">No snapshot found</span>')]

    # ── E. Trend / State Summary ──────────────────────────────────────────────
    trend_rows = [
        _row("Trend available", "Yes" if trend_flags["available"] else "No"),
        _row("Baseline only", "Yes — waiting for comparison data" if trend_flags.get("baseline_only") else "No — comparisons active"),
    ]
    recent_fails = [e for e in l6.get("history", []) if e.get("status") in ("failed", "partial_failure")][-3:]
    trend_rows.append(_row("Recent L6 failures", str(len(recent_fails)) if recent_fails else "None"))

    # ── F. L5 Proposals ───────────────────────────────────────────────────────
    l5p = l5_proposals or {}
    if l5p.get("available"):
        proposals_rows = [
            _row("Generated at", html.escape(str(l5p.get("generated_at") or "—")[:19].replace("T", " "))),
            _row("Mode", html.escape(str(l5p.get("mode", "—")))),
            _row("Total proposals", html.escape(str(l5p.get("total", 0)))),
        ]
        for a in l5p.get("actions", [])[:5]:
            url_e = html.escape(a.get("url", "—"))
            before_e = html.escape((a.get("before", {}).get("meta_description") or "(gol)")[:80])
            proposal_e = html.escape((a.get("proposal", {}).get("meta_description") or "—")[:80])
            tier_e = html.escape(str(a.get("tier", "—")))
            status_e = a.get("status", "proposed_only")
            proposals_rows.append(_row(
                f"↳ {url_e}",
                f"Tier {tier_e} | {_pill(status_e)}<br>"
                f"<span class='dim'>Before:</span> {before_e}<br>"
                f"<span class='dim'>Proposal:</span> {proposal_e}"
            ))
    else:
        proposals_rows = [_row("Status", '<span class="pill grey">Niciun dry-run disponibil</span>')]

    # ── G. L5 Approval + Apply Plan ───────────────────────────────────────────
    l5a = l5_approval or {}
    approval_rows = [
        _row("Total decizii", html.escape(str(len(l5a.get("approval_log", []))))),
        _row("Aprobate", html.escape(str(len(l5a.get("approved", []))))),
        _row("Respinse", html.escape(str(len(l5a.get("rejected", []))))),
        _row("Apply Plan generat la", html.escape(str(l5a.get("plan_generated_at") or "—")[:19].replace("T", " "))),
        _row("Ready to apply", _pill("success") if l5a.get("ready_to_apply") else _pill("warning")),
        _row("Acțiuni în plan", html.escape(str(len(l5a.get("plan", []))))),
        _row("Acțiuni blocate", html.escape(str(len(l5a.get("blocked", []))))),
    ]
    for dec in l5a.get("approved", [])[:3]:
        url_e = html.escape(dec.get("url", "—"))
        by_e  = html.escape(dec.get("decided_by", "—"))
        at_e  = html.escape(str(dec.get("decided_at") or "—")[:19].replace("T", " "))
        approval_rows.append(_row(f"✓ {url_e}", f"{_pill('success')} by {by_e} la {at_e}"))
    for dec in l5a.get("rejected", [])[:3]:
        url_e = html.escape(dec.get("url", "—"))
        by_e  = html.escape(dec.get("decided_by", "—"))
        at_e  = html.escape(str(dec.get("decided_at") or "—")[:19].replace("T", " "))
        approval_rows.append(_row(f"✗ {url_e}", f"{_pill('failed')} by {by_e} la {at_e}"))
    if not l5a.get("approval_log"):
        approval_rows.append(_row("Status", '<span class="pill grey">Niciun log de aprobare</span>'))

    # ── H. L5 Applied / Rollback Audit Trail ─────────────────────────────────
    l5e = l5_execution or {}
    exec_rows = []
    apply_exec = l5e.get("apply_exec")
    if apply_exec and isinstance(apply_exec, dict):
        exec_rows += [
            _row("Apply exec ID", html.escape(str(apply_exec.get("execution_id") or "—"))),
            _row("Applied at", html.escape(str(apply_exec.get("executed_at") or "—")[:19].replace("T", " "))),
            _row("Status apply", _pill(str(apply_exec.get("status") or "—"))),
            _row("URL aplicat", html.escape(str(apply_exec.get("url") or "—"))),
        ]
    else:
        exec_rows.append(_row("Apply Execution", '<span class="pill grey">Niciun apply executat</span>'))
    rollback_pay = l5e.get("rollback_payload")
    if rollback_pay and isinstance(rollback_pay, dict):
        exec_rows += [
            _row("Rollback payload ID", html.escape(str(rollback_pay.get("plan_id") or "—"))),
            _row("Before (rollback)", html.escape(str((rollback_pay.get("before") or {}).get("meta_description") or "—")[:80])),
        ]
    else:
        exec_rows.append(_row("Rollback Payload", '<span class="pill grey">Niciun rollback payload</span>'))
    rollback_exec = l5e.get("rollback_exec")
    if rollback_exec and isinstance(rollback_exec, dict):
        exec_rows += [
            _row("Rollback exec ID", html.escape(str(rollback_exec.get("execution_id") or "—"))),
            _row("Rollback at", html.escape(str(rollback_exec.get("executed_at") or "—")[:19].replace("T", " "))),
            _row("Rollback status", _pill(str(rollback_exec.get("status") or "—"))),
        ]
    else:
        exec_rows.append(_row("Rollback Execution", '<span class="pill grey">Niciun rollback executat</span>'))

    sections = (
        _section("A. Source Acquisition — L7", l7_rows) +
        f"<div class='hist-wrap'><h3>Ultimele 5 rulări L7</h3>{l7_hist}</div>" +
        _section("B. Report Plane — L6", l6_rows) +
        f"<div class='hist-wrap'><h3>Ultimele 5 rulări L6</h3>{l6_hist}</div>" +
        _section("C. Freshness Rapoarte", freshness_rows) +
        _section("D. Latest Raw Snapshot (GSC)", snap_rows) +
        _section("E. Trend / State Summary", trend_rows) +
        "<hr style='border:1px solid #1e293b;margin:1.5rem 0'>" +
        "<p style='color:#64748b;font-size:.8rem;margin-bottom:.75rem'>" +
        "&#8212; Level 5: Planning / Apply / Rollback Audit Trail &#8212;</p>" +
        _section("F. L5 Proposals (Dry-Run)", proposals_rows) +
        _section("G. L5 Approval + Apply Plan", approval_rows) +
        _section("H. L5 Applied / Rollback Audit Trail", exec_rows)
    )

    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SEO Ops Dashboard — L6/L7</title>
<style>
  :root{{--green:#22c55e;--yellow:#eab308;--red:#ef4444;--bg:#0f172a;--card:#1e293b;--txt:#e2e8f0;--dim:#64748b}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--txt);font-family:system-ui,sans-serif;padding:1.5rem}}
  h1{{font-size:1.4rem;margin-bottom:.25rem}}
  .meta{{color:var(--dim);font-size:.8rem;margin-bottom:1.5rem}}
  .verdict{{border-radius:12px;padding:1.25rem 1.75rem;margin-bottom:1.75rem;border-left:6px solid {vc};background:var(--card)}}
  .verdict h2{{font-size:1.5rem;color:{vc}}}
  section{{background:var(--card);border-radius:10px;padding:1.2rem 1.5rem;margin-bottom:1.2rem}}
  section h2{{font-size:1rem;text-transform:uppercase;letter-spacing:.05em;color:var(--dim);margin-bottom:.75rem}}
  table{{width:100%;border-collapse:collapse;font-size:.88rem}}
  td{{padding:.35rem .5rem;border-bottom:1px solid #ffffff10;vertical-align:top}}
  td.label{{color:var(--dim);width:220px;white-space:nowrap}}
  .hist-wrap{{background:var(--card);border-radius:10px;padding:1rem 1.5rem;margin-bottom:1.2rem}}
  .hist-wrap h3{{font-size:.85rem;color:var(--dim);margin-bottom:.5rem}}
  table.hist td,table.hist th{{padding:.3rem .5rem;font-size:.8rem;border:none;border-bottom:1px solid #ffffff0d}}
  table.hist th{{color:var(--dim);font-weight:500;text-align:left}}
  .pill{{border-radius:4px;padding:1px 9px;font-size:.75rem;font-weight:600;display:inline-block}}
  .pill.green{{background:#166534;color:#bbf7d0}}
  .pill.red{{background:#7f1d1d;color:#fecaca}}
  .pill.yellow{{background:#713f12;color:#fef08a}}
  .pill.grey{{background:#334155;color:#94a3b8}}
  .dim{{color:var(--dim)}}
  footer{{margin-top:2rem;font-size:.75rem;color:var(--dim)}}
</style>
</head>
<body>
<h1>🛰 SEO Ops Dashboard — L6/L7</h1>
<p class="meta">Generat: {now_str} | Proprietate: sc-domain:superparty.ro | Dashboard legacy: <code>reports/seo/dashboard.html</code> (neconectat la pipeline-ul nou)</p>

<div class="verdict">
  <h2>{vl}</h2>
</div>

{sections}

<footer>Dashboard generat de <code>scripts/seo_ops_dashboard.py</code>. 
Nu modifică niciun artefact. Numai citire (read-only).<br>
Dashboard legacy (L3/L4): <code>scripts/seo_dashboard.py → reports/seo/dashboard.html</code> — ignorat.</footer>
</body>
</html>"""


# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> int:
    l7 = collect_l7()
    l6 = collect_l6()
    freshness = collect_freshness()
    snapshot = _latest_snapshot()
    trend_flags = collect_trend_flags(freshness)
    verdict = compute_verdict(l7, l6, freshness)

    # L5 Audit Trail — read-only, graceful if artefacts absent
    l5_proposals = collect_l5_proposals()
    l5_approval  = collect_l5_approval()
    l5_execution = collect_l5_execution()

    html_out = render_html(l7, l6, freshness, snapshot, trend_flags, verdict,
                           l5_proposals=l5_proposals,
                           l5_approval=l5_approval,
                           l5_execution=l5_execution)

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)

    # Atomic write (temp file + rename)
    import tempfile, shutil
    fd, tmp = tempfile.mkstemp(dir=OUTPUT_HTML.parent, suffix=".tmp.html")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(html_out)
        shutil.move(tmp, OUTPUT_HTML)
    except Exception as e:
        print(f"ERROR writing dashboard: {e}", file=sys.stderr)
        if Path(tmp).exists():
            Path(tmp).unlink()
        return 1

    print(f"Dashboard written: {OUTPUT_HTML}")
    print(f"Verdict: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
