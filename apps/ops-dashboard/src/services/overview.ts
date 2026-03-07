import path from "path";
import fs from "fs";
import { glob } from "glob";
import { config } from "../config";

// Citim DB-ul de experimente dacă există
function loadExperiments() {
    try {
        if (!fs.existsSync(config.experimentsDb)) return [];
        const Database = require("better-sqlite3");
        const db = new Database(config.experimentsDb, { readonly: true });
        const rows = db.prepare(`
      SELECT exp_id, url_path, exp_type, status, started_at, ends_at,
             variant_a_title, variant_b_title, winner_variant, decision_reason
      FROM seo_experiments
      ORDER BY started_at DESC LIMIT 20
    `).all();
        db.close();
        return rows;
    } catch (e: any) {
        return [{ error: e.message }];
    }
}

// Citim ultimele audit logs
function loadRecentAudits() {
    try {
        const pattern = path.join(config.reportsDir, "seo_apply_gsc_*.json");
        const files = glob.sync(pattern).sort().reverse().slice(0, 7);
        return files.map(f => {
            try {
                const data = JSON.parse(fs.readFileSync(f, "utf-8"));
                data._file = path.basename(f);
                return data;
            } catch { return { _file: path.basename(f), error: "parse error" }; }
        });
    } catch { return []; }
}

// Citim URL states
function loadUrlStates() {
    try {
        const p = path.join(config.seoReportsDir, "url_states.json");
        if (!fs.existsSync(p)) return {};
        return JSON.parse(fs.readFileSync(p, "utf-8"));
    } catch { return {}; }
}

// Statistici manifest
function loadManifestStats() {
    try {
        if (!fs.existsSync(config.manifestPath)) return { total: 0, indexable: 0 };
        const m = JSON.parse(fs.readFileSync(config.manifestPath, "utf-8"));
        return { total: m.length, indexable: m.filter((e: any) => e.indexable).length };
    } catch { return { total: 0, indexable: 0 }; }
}

// Kill switch status
function getKillSwitches() {
    return {
        SEO_FREEZE: process.env.SEO_FREEZE || "0",
        SEO_FREEZE_APPLY: process.env.SEO_FREEZE_APPLY || "0",
        SEO_FREEZE_EXPERIMENTS: process.env.SEO_FREEZE_EXPERIMENTS || "0",
        SEO_PILLAR_LOCK: process.env.SEO_PILLAR_LOCK || "0",
        SEO_CONTINUOUS: process.env.SEO_CONTINUOUS || "0",
        SEO_APPLY_MODE: process.env.SEO_APPLY_MODE || "report",
    };
}

// Citim Level 4 Cluster Health
export function loadClusterHealth() {
    try {
        const p = path.join(config.reportsDir, "seo_cluster_health.json");
        if (!fs.existsSync(p)) return null;
        return JSON.parse(fs.readFileSync(p, "utf-8"));
    } catch { return null; }
}

// Citim Level 4 Cluster Priority (Intelligence)
export function loadClusterPriority() {
    try {
        const p = path.join(config.reportsDir, "seo_cluster_priority.json");
        if (!fs.existsSync(p)) return null;
        return JSON.parse(fs.readFileSync(p, "utf-8"));
    } catch { return null; }
}

// Citim Level 4 Gap Opportunities (Faza 14)
export function loadClusterGaps() {
    try {
        const p = path.join(config.reportsDir, "seo_gap_opportunities.json");
        if (!fs.existsSync(p)) return null;
        return JSON.parse(fs.readFileSync(p, "utf-8"));
    } catch { return null; }
}

// Citim Level 4.1 Trend Delta (PR #51 — seo_trend_delta.json este singurul contract consumat)
export function loadTrendDelta() {
    try {
        const p = path.join(config.reportsDir, "seo_trend_delta.json");
        if (!fs.existsSync(p)) return null;
        return JSON.parse(fs.readFileSync(p, "utf-8"));
    } catch { return null; }
}

export async function getOverview() {
    const experiments = loadExperiments();
    const recentAudits = loadRecentAudits();
    const urlStates = loadUrlStates();
    const manifestStats = loadManifestStats();
    const switches = getKillSwitches();

    const activeExperiments = experiments.filter((e: any) => e.status?.includes("RUNNING")).length;
    const rollbackCount = experiments.filter((e: any) => ["REVERTED", "LOSER"].includes(e.status)).length;

    const clusterHealth = loadClusterHealth();
    let clusterHealthSummary = {
        totalClusters: 0,
        moneyWithWarnings: 0,
        forbiddenConflicts: 0,
        unknownConflicts: 0,
        generatedAt: ""
    };

    if (clusterHealth && clusterHealth.clusters) {
        const clusters = clusterHealth.clusters;
        clusterHealthSummary.generatedAt = clusterHealth.metadata?.generated_at || "";
        clusterHealthSummary.totalClusters = Object.keys(clusters).length;

        for (const [id, c] of Object.entries<any>(clusters)) {
            if (c.is_money_cluster && c.cannibalization_warnings?.length > 0) {
                clusterHealthSummary.moneyWithWarnings++;
            }
            clusterHealthSummary.forbiddenConflicts += (c.forbidden_count || 0);
            clusterHealthSummary.unknownConflicts += (c.unknown_count || 0);
        }
    }

    const clusterPriority = loadClusterPriority();
    let prioritySummary = {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        generatedAt: ""
    };
    if (clusterPriority && clusterPriority.clusters) {
        prioritySummary.generatedAt = clusterPriority.metadata?.priority_generated_at || "";
        for (const c of Object.values<any>(clusterPriority.clusters)) {
            const band = c.intelligence?.priority_band;
            if (band === "critical") prioritySummary.critical++;
            else if (band === "high") prioritySummary.high++;
            else if (band === "medium") prioritySummary.medium++;
            else if (band === "low") prioritySummary.low++;
        }
    }

    const clusterGaps = loadClusterGaps();
    let gapSummary = {
        high: 0,
        medium: 0,
        low: 0,
        total: 0,
        generatedAt: ""
    };
    if (clusterGaps && clusterGaps.opportunities) {
        gapSummary.generatedAt = clusterGaps.metadata?.gap_detected_at || "";
        gapSummary.total = clusterGaps.opportunities.length;
        for (const opp of clusterGaps.opportunities) {
            if (opp.confidence === "high") gapSummary.high++;
            else if (opp.confidence === "medium") gapSummary.medium++;
            else gapSummary.low++;
        }
    }

    const trendDelta = loadTrendDelta();
    let trendSummary = {
        improved: 0, regressed: 0, stable: 0, mixed: 0, new: 0, missing: 0,
        baselineOnly: true, previousSnapshotDate: "", generatedAt: ""
    };
    if (trendDelta) {
        trendSummary.baselineOnly = !!trendDelta.metadata?.baseline_only;
        trendSummary.previousSnapshotDate = trendDelta.metadata?.previous_snapshot_date || "";
        trendSummary.generatedAt = trendDelta.metadata?.generated_at || "";
        for (const c of (trendDelta.clusters || [])) {
            const s = c.status as string;
            if (s in trendSummary) (trendSummary as any)[s]++;
        }
    }

    return {
        experiments,
        recentAudits,
        urlStates,
        indexableCount: manifestStats.indexable,
        manifestTotal: manifestStats.total,
        activeExperiments,
        rollbackCount,
        switches,
        clusterHealthSummary,
        prioritySummary,
        gapSummary,
        trendSummary,
        generatedAt: new Date().toISOString(),
    };
}
