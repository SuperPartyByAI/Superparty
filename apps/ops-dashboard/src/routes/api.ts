import { Router } from "express";
import { getOverview } from "../services/overview";

export const apiRouter = Router();

// GET /api/overview — date complete pentru dashboard
apiRouter.get("/overview", async (_req, res) => {
    try {
        const data = await getOverview();
        res.json(data);
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// GET /api/cluster-health — Level 4 Read-Only Advisory Report
apiRouter.get("/cluster-health", async (req, res) => {
    try {
        const { loadClusterHealth } = await import("../services/overview");
        let data = loadClusterHealth();
        if (!data) return res.status(404).json({ error: "No cluster health report found" });

        const warnings = req.query.warnings === "1";

        if (warnings) {
            const filteredClusters: Record<string, any> = {};
            for (const [id, c] of Object.entries<any>(data.clusters || {})) {
                if (c.cannibalization_warnings && c.cannibalization_warnings.length > 0) {
                    filteredClusters[id] = c;
                }
            }
            data.clusters = filteredClusters;
            res.json(data);
            return;
        }

        res.json(data);
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// GET /api/cluster-priority — Level 4 Business Priority Intelligence (Phase 13)
apiRouter.get("/cluster-priority", async (req, res) => {
    try {
        const { loadClusterPriority } = await import("../services/overview");
        let data = loadClusterPriority();
        if (!data) return res.status(404).json({ error: "No cluster priority report found" });

        const band = req.query.band as string;
        const action = req.query.action as string;

        if (band || action) {
            const filteredClusters: Record<string, any> = {};
            for (const [id, c] of Object.entries<any>(data.clusters || {})) {
                if (band && c.intelligence?.priority_band !== band) continue;
                if (action && c.intelligence?.recommended_action !== action) continue;
                filteredClusters[id] = c;
            }
            data.clusters = filteredClusters;
            res.json(data);
            return;
        }

        res.json(data);
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// GET /api/cluster-gaps — Level 4 Gap Detector Opportunities (Faza 14)
apiRouter.get("/cluster-gaps", async (req, res) => {
    try {
        const { loadClusterGaps } = await import("../services/overview");
        let data = loadClusterGaps();
        if (!data) return res.status(404).json({ error: "No gap opportunities report found" });

        const tier = req.query.tier as string;
        const type = req.query.type as string;
        const confidence = req.query.confidence as string;

        if (tier || type || confidence) {
            data.opportunities = (data.opportunities || []).filter((opp: any) => {
                if (tier && opp.tier !== tier) return false;
                if (type && opp.opportunity_type !== type) return false;
                if (confidence && opp.confidence !== confidence) return false;
                return true;
            });
        }

        res.json(data);
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});

// GET /api/cluster-trends — Level 4.1 Trend Delta (PR #51 contract)
// Consumă EXCLUSIV seo_trend_delta.json. Nu recalculează trendul.
apiRouter.get("/cluster-trends", async (req, res) => {
    try {
        const { loadTrendDelta } = await import("../services/overview");
        const raw = loadTrendDelta();

        if (!raw) return res.status(404).json({ error: "No trend delta report found. Run seo_trend_analyzer first." });

        const filterStatus = req.query.status as string;
        // NOTE: filtrul `tier` a fost eliminat intenționat în PR #52.
        // Contractul din PR #51 (seo_trend_delta.json) normalizează `priority_band`, nu `tier`.
        // Filtrul tier va fi reintroduce corect după extinderea contractului în seo_trend_analyzer.py.
        const limitParam = parseInt((req.query.limit as string) || "0");
        const sortParam = (req.query.sort as string) || "";

        let clusters = [...(raw.clusters || [])];

        // Filter — doar status este suportat în PR #52
        if (filterStatus) clusters = clusters.filter((c: any) => c.status === filterStatus);

        // Sort
        if (sortParam === "owner_share_desc") {
            clusters.sort((a: any, b: any) => (b.current?.owner_share ?? -1) - (a.current?.owner_share ?? -1));
        } else if (sortParam === "owner_share_delta_asc") {
            // null delta_owner_share (pre-PR50 snaphot) → sortat la final, nu comprimat spre 0
            clusters.sort((a: any, b: any) => {
                const av = a.delta_owner_share;
                const bv = b.delta_owner_share;
                if (av === null && bv === null) return 0;
                if (av === null) return 1;  // null → end
                if (bv === null) return -1;
                return av - bv;
            });
        } else if (sortParam === "forbidden_delta_desc") {
            clusters.sort((a: any, b: any) => (b.delta_forbidden ?? 0) - (a.delta_forbidden ?? 0));
        } else if (sortParam === "status") {
            const order: any = { regressed: 0, mixed: 1, new: 2, stable: 3, improved: 4, missing: 5 };
            clusters.sort((a: any, b: any) => (order[a.status] ?? 9) - (order[b.status] ?? 9));
        }

        // Limit
        if (limitParam > 0) clusters = clusters.slice(0, limitParam);

        // Summary counts from the full unfiltered data (for dashboard stat awareness)
        const statusCounts: any = { improved: 0, regressed: 0, stable: 0, mixed: 0, new: 0, missing: 0 };
        for (const c of (raw.clusters || [])) {
            if (c.status in statusCounts) statusCounts[c.status]++;
        }

        res.json({
            metadata: raw.metadata,
            summary: statusCounts,
            clusters,
        });
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
});
