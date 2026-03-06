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

        const tier = req.query.tier as string;
        const warnings = req.query.warnings === "1";
        const cluster_type = req.query.cluster_type as string;

        if (tier || warnings || cluster_type) {
            const filteredClusters: Record<string, any> = {};
            for (const [id, c] of Object.entries<any>(data.clusters || {})) {
                let keep = true;
                // tier is not inside cluster JSON. It requires map, but let's do simplistic filtering if we add the fields later. 
                // wait, the json hasn't tier or type directly. So we return all for now or filter money_clusters.
                if (warnings && (!c.cannibalization_warnings || c.cannibalization_warnings.length === 0)) keep = false;

                if (keep) filteredClusters[id] = c;
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
