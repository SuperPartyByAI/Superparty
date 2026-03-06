import { Router } from "express";
import passport from "passport";

export const authRouter = Router();

authRouter.get("/login", (req, res) => {
    if (req.isAuthenticated()) return res.redirect("/seo");
    res.send(`
    <!DOCTYPE html><html lang="ro">
    <head><meta charset="UTF-8"><title>Login — Superparty Ops</title>
    <meta name="robots" content="noindex,nofollow">
    <style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { background: #0f172a; display: flex; align-items: center; justify-content: center; min-height: 100vh; font-family: system-ui, sans-serif; }
      .card { background: #1e293b; border-radius: 16px; padding: 40px; text-align: center; width: 340px; box-shadow: 0 25px 60px rgba(0,0,0,.5); }
      h1 { color: #f1f5f9; font-size: 20px; margin-bottom: 8px; }
      p { color: #64748b; font-size: 14px; margin-bottom: 28px; }
      a.btn { display: block; background: #fff; color: #1e1e1e; border-radius: 8px; padding: 12px 20px; font-size: 15px; font-weight: 600; text-decoration: none; transition: opacity .2s; }
      a.btn:hover { opacity: .9; }
      .logo { font-size: 32px; margin-bottom: 16px; }
    </style>
    </head>
    <body>
      <div class="card">
        <div class="logo">🎯</div>
        <h1>Superparty SEO Ops</h1>
        <p>Dashboard privat — acces restricționat</p>
        <a class="btn" href="/auth/google">
          <img src="https://www.google.com/favicon.ico" width="16" style="vertical-align:middle;margin-right:8px">
          Continuă cu Google
        </a>
      </div>
    </body></html>
  `);
});

authRouter.get("/google",
    passport.authenticate("google", { scope: ["profile", "email"] })
);

authRouter.get("/google/callback",
    passport.authenticate("google", { failureRedirect: "/auth/denied" }),
    (req: any, res) => {
        const returnTo = req.session.returnTo || "/seo";
        delete req.session.returnTo;
        res.redirect(returnTo);
    }
);

authRouter.get("/denied", (_req, res) => {
    res.status(403).send(`
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Access Denied</title>
    <meta name="robots" content="noindex,nofollow">
    <style>body{background:#0f172a;color:#ef4444;font-family:sans-serif;padding:40px;text-align:center}</style></head>
    <body><h1>403 — Access Denied</h1>
    <p style="color:#94a3b8;margin:16px 0">Emailul tău nu este autorizat pentru acest dashboard.</p>
    <a href="/auth/logout" style="color:#3b82f6">Încearcă alt cont</a></body></html>
  `);
});

authRouter.post("/logout", (req, res, next) => {
    req.logout((err) => { if (err) return next(err); res.redirect("/auth/login"); });
});
authRouter.get("/logout", (req, res, next) => {
    req.logout((err) => { if (err) return next(err); res.redirect("/auth/login"); });
});
