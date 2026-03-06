import { Request, Response, NextFunction } from "express";
import { config } from "../config";

export function requireAuth(req: Request, res: Response, next: NextFunction) {
    if (!req.isAuthenticated()) {
        req.session.returnTo = req.originalUrl;
        return res.redirect("/auth/login");
    }

    // Verificare server-side pe FIECARE request — nu doar la login
    const user = req.user as any;
    const email = user?.email?.toLowerCase() || "";
    if (!config.allowedEmails.includes(email)) {
        return res.status(403).send(`
      <html><body style="background:#0f172a;color:#ef4444;font-family:sans-serif;padding:40px;text-align:center">
        <h1>403 Forbidden</h1>
        <p>${email} nu are acces la acest dashboard.</p>
        <a href="/auth/logout" style="color:#3b82f6">Logout</a>
      </body></html>
    `);
    }

    next();
}
