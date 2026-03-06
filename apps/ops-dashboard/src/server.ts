import express from "express";
import session from "express-session";
import passport from "passport";
import helmet from "helmet";
import path from "path";
import { setupAuth } from "./auth";
import { authRouter } from "./routes/auth";
import { seoRouter } from "./routes/seo";
import { apiRouter } from "./routes/api";
import { requireAuth } from "./middleware/requireAuth";
import { config } from "./config";

const app = express();

// Security headers
app.use(helmet({
    contentSecurityPolicy: false, // relaxat pentru dashboard intern
    crossOriginEmbedderPolicy: false,
}));

// Trust proxy (Nginx în față)
app.set("trust proxy", 1);

// Session Configuration
let sessionStore;
try {
    const SQLiteStore = require("connect-sqlite3")(session);
    sessionStore = new SQLiteStore({ db: "sessions.db", dir: config.dataDir });
    console.log("[ops-dashboard] Folosesc SQLiteStore pentru sesiuni.");
} catch (e) {
    console.warn("[ops-dashboard] WARNING: connect-sqlite3 a esuat. Folosesc MemoryStore (not recommended for production).", e);
    sessionStore = new session.MemoryStore();
}

app.use(session({
    store: sessionStore,
    secret: config.sessionSecret,
    resave: false,
    saveUninitialized: false,
    cookie: {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        maxAge: 8 * 60 * 60 * 1000, // 8 ore
    },
}));

// Passport
setupAuth();
app.use(passport.initialize());
app.use(passport.session());

// Static files
app.use("/static", express.static(path.join(__dirname, "../public")));

// No-index header pe toate rutele
app.use((_req, res, next) => {
    res.setHeader("X-Robots-Tag", "noindex, nofollow, noarchive");
    next();
});

// Auth routes (publice)
app.use("/auth", authRouter);

// Protected routes
app.use("/seo", requireAuth, seoRouter);
app.use("/api", requireAuth, apiRouter);

// Root → redirect la /seo
app.get("/", (req, res) => {
    if (req.isAuthenticated()) res.redirect("/seo");
    else res.redirect("/auth/login");
});

// Healthcheck (public, fara date sensibile)
app.get("/healthz", (_req, res) => res.json({ status: "ok" }));

// 404
app.use((_req, res) => res.status(404).send("Not found"));

app.listen(config.port, "127.0.0.1", () => {
    console.log(`[ops-dashboard] Running on http://127.0.0.1:${config.port}`);
    console.log(`[ops-dashboard] Allowed emails: ${config.allowedEmails.join(", ")}`);
});
