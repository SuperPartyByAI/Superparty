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
