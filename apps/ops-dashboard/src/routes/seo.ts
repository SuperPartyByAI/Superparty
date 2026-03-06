import { Router } from "express";
import { getOverview } from "../services/overview";

export const seoRouter = Router();

seoRouter.get("/", async (req: any, res) => {
    let data: any = {};
    try { data = await getOverview(); } catch (e: any) { data = { error: e.message }; }

    const user = req.user;
    const now = new Date().toLocaleString("ro-RO");

    const moneyPages = [
        { path: "/animatori-petreceri-copii", label: "🎯 Pilon", tier: "A" },
        { path: "/petreceri/bucuresti", label: "🏙️ Hub București", tier: "A" },
        { path: "/petreceri/ilfov", label: "🌆 Hub Ilfov", tier: "A" },
        { path: "/petreceri/sector-1", label: "📍 Sector 1", tier: "B" },
        { path: "/petreceri/sector-2", label: "📍 Sector 2", tier: "B" },
        { path: "/petreceri/sector-3", label: "📍 Sector 3", tier: "B" },
        { path: "/petreceri/sector-4", label: "📍 Sector 4", tier: "B" },
        { path: "/petreceri/sector-5", label: "📍 Sector 5", tier: "B" },
        { path: "/petreceri/sector-6", label: "📍 Sector 6", tier: "B" },
    ];

    const states: Record<string, any> = data.urlStates || {};
    const frozen = data.switches?.SEO_FREEZE === "1";
    const agentBadge = frozen
        ? `<span class="badge red">❄️ FROZEN</span>`
        : `<span class="badge green">✅ RUNNING</span>`;

    const moneyRows = moneyPages.map(p => {
        const s = states[p.path] || {};
        const state = (typeof s === "string" ? s : s.state) || "eligible";
        const stateColors: Record<string, string> = {
            eligible: "green", applied_real: "purple", winner: "green",
            frozen: "red", manual_lock: "red", blocked_cooldown: "yellow",
            experiment_A: "blue", experiment_B: "blue", reverted: "yellow", planned: "blue"
        };
        const tc = p.tier === "A" ? "#22c55e" : p.tier === "B" ? "#3b82f6" : "#a855f7";
        return `<tr>
      <td><span style="background:${tc};color:#fff;padding:1px 6px;border-radius:4px;font-size:11px">T${p.tier}</span></td>
      <td style="color:#e2e8f0">${p.label}</td>
      <td style="font-family:monospace;font-size:12px;color:#94a3b8">${p.path}</td>
      <td><span class="badge ${stateColors[state] || "gray"}">${state}</span></td>
      <td><a href="https://www.superparty.ro${p.path}" target="_blank" style="color:#3b82f6">↗</a></td>
    </tr>`;
    }).join("");

    const experiments: any[] = data.experiments || [];
    const expRows = experiments.length ? experiments.map(e => {
        const sc = e.status?.includes("RUNNING") ? "blue" : e.status === "WINNER" ? "green" : e.status === "REVERTED" ? "yellow" : "red";
        return `<tr>
      <td style="font-size:12px">${e.url_path || ""}</td>
      <td><span class="badge ${sc}">${e.status || "?"}</span></td>
      <td style="font-size:11px">${(e.variant_a_title || "").slice(0, 40)}</td>
      <td style="font-size:11px">${(e.variant_b_title || "").slice(0, 40)}</td>
      <td style="font-size:12px">${e.winner_variant || "—"}</td>
      <td style="font-size:11px">${(e.started_at || "").slice(0, 10)}</td>
    </tr>`;
    }).join("") : `<tr><td colspan="6" style="color:#64748b;padding:20px">Niciun experiment în DB.</td></tr>`;

    const audits: any[] = data.recentAudits || [];
    const auditBlocks = audits.length ? audits.map(a => {
        const applied = a.applied?.length || 0;
        const skipped = a.skipped?.length || 0;
        const reasons: Record<string, number> = {};
        (a.skipped || []).forEach((s: any) => { reasons[s.reason || "unknown"] = (reasons[s.reason || "unknown"] || 0) + 1; });
        const reasonBadges = Object.entries(reasons).map(([r, n]) => `<span class="badge yellow">${r}: ${n}</span>`).join(" ");
        return `<div class="audit-block">
      <div style="color:#64748b;font-size:11px">${a._file || ""}</div>
      <div style="margin-top:4px">
        <span class="badge green">Aplicate: ${applied}</span>
        <span class="badge gray">Skip: ${skipped}</span>
        ${reasonBadges}
      </div>
    </div>`;
    }).join("") : `<div style="color:#64748b;padding:10px">Niciun audit log găsit.</div>`;

    const switchBadges = Object.entries(data.switches || {}).map(([k, v]) => {
        const c = v === "1" ? "red" : v === "0" ? "green" : "blue";
        return `<span class="badge ${c}">${k}=${v}</span>`;
    }).join(" ");

    res.send(`<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SEO Ops Dashboard — Superparty</title>
<meta name="robots" content="noindex,nofollow">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0f172a; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; padding: 20px; }
  h1 { font-size: 22px; font-weight: 700; }
  h2 { font-size: 14px; font-weight: 600; color: #64748b; margin: 24px 0 8px; text-transform: uppercase; letter-spacing: 1px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin: 12px 0; }
  .card { background: #1e293b; border-radius: 10px; padding: 16px; }
  .card-val { font-size: 28px; font-weight: 700; }
  .card-label { font-size: 12px; color: #64748b; margin-top: 4px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { color: #64748b; text-align: left; padding: 6px 8px; border-bottom: 1px solid #1e293b; font-size: 11px; text-transform: uppercase; }
  td { padding: 8px; border-bottom: 1px solid #1e293b; vertical-align: middle; }
  tr:hover td { background: #1e293b; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; color: #fff; margin: 1px; }
  .badge.green { background: #22c55e; }
  .badge.red { background: #ef4444; }
  .badge.yellow { background: #f59e0b; }
  .badge.blue { background: #3b82f6; }
  .badge.purple { background: #a855f7; }
  .badge.gray { background: #4b5563; }
  .status-bar { display: flex; align-items: center; gap: 12px; background: #1e293b; padding: 12px 16px; border-radius: 10px; margin: 12px 0; flex-wrap: wrap; }
  .audit-block { background: #1e293b; padding: 10px 14px; border-radius: 8px; margin: 6px 0; }
  .user-bar { color: #64748b; font-size: 12px; margin-bottom: 4px; }
  a { color: #3b82f6; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>

<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
  <h1>🎯 SEO Ops Dashboard — Superparty</h1>
  <a href="/auth/logout" style="font-size:13px;color:#64748b">Logout (${user?.email || ""})</a>
</div>
<div class="user-bar">Generat: ${now} | <a href="https://www.superparty.ro" target="_blank">www.superparty.ro</a></div>

<div class="status-bar">
  ${agentBadge}
  ${switchBadges}
</div>

<div class="grid">
  <div class="card">
    <div class="card-val" style="color:#22c55e">${data.activeExperiments || 0}</div>
    <div class="card-label">Experimente active</div>
  </div>
  <div class="card">
    <div class="card-val" style="color:#f59e0b">${data.rollbackCount || 0}</div>
    <div class="card-label">Rollback-uri</div>
  </div>
  <div class="card">
    <div class="card-val" style="color:#3b82f6">${data.indexableCount || 0}</div>
    <div class="card-label">URL-uri indexabile</div>
  </div>
  <div class="card">
    <div class="card-val" style="color:#a855f7">${audits.length}</div>
    <div class="card-label">Cicluri apply (7d)</div>
  </div>
</div>

<h2>📄 Pagini Money — Ownership & Status</h2>
<table>
  <tr><th>Tier</th><th>Pagina</th><th>Path</th><th>Status</th><th>Link</th></tr>
  ${moneyRows}
</table>

<h2>🧪 Experimente CTR (ultimele 10)</h2>
<table>
  <tr><th>URL</th><th>Status</th><th>Variant A</th><th>Variant B</th><th>Winner</th><th>Start</th></tr>
  ${expRows}
</table>

<h2>📋 Apply Audit Log (ultimele 7 cicluri)</h2>
${auditBlocks}

<div style="margin-top:30px;border-top:1px solid #1e293b;padding-top:16px;color:#475569;font-size:11px">
  📚 Runbooks: <a href="https://github.com/SuperPartyByAI/Superparty/tree/main/docs/runbooks/seo">docs/runbooks/seo/</a> |
  🔄 <a href="/seo">Refresh</a> |
  <a href="/api/overview">API JSON</a>
</div>
</body>
</html>`);
});
