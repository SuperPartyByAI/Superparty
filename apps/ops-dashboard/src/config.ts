import path from "path";
import dotenv from "dotenv";

dotenv.config({ path: path.join(process.cwd(), ".env") });

export const config = {
    port: Number(process.env.OPS_PORT || 8787),
    baseUrl: process.env.OPS_BASE_URL || "https://ops.superparty.ro",
    dataDir: process.env.OPS_DATA_DIR || path.join(process.cwd(), "data"),

    // Acces: doar emailul exact (case-insensitive)
    allowedEmails: (process.env.OPS_ALLOWED_EMAILS || "ursache.andrei1995@gmail.com")
        .split(",")
        .map(s => s.trim().toLowerCase())
        .filter(Boolean),

    // Google OAuth
    googleClientId: process.env.OPS_GOOGLE_CLIENT_ID || "",
    googleClientSecret: process.env.OPS_GOOGLE_CLIENT_SECRET || "",

    // Session
    sessionSecret: process.env.OPS_SESSION_SECRET || "SCHIMBA-ASTA-CU-UN-SECRET-RANDOM-LUNG",

    // Paths catre datele agentului SEO (pe server Hetzner)
    reportsDir: process.env.OPS_REPORTS_DIR || path.join(process.cwd(), "../../reports/superparty"),
    seoReportsDir: process.env.OPS_SEO_REPORTS_DIR || path.join(process.cwd(), "../../reports/seo"),
    experimentsDb: process.env.OPS_EXPERIMENTS_DB || path.join(process.cwd(), "../../reports/superparty/seo_experiments.db"),
    manifestPath: process.env.OPS_MANIFEST_PATH || path.join(process.cwd(), "../../reports/seo/indexing_manifest.json"),
    sitemapPath: process.env.OPS_SITEMAP_PATH || path.join(process.cwd(), "../../public/sitemap.xml"),
};
