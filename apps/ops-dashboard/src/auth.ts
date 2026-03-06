import passport from "passport";
import { Strategy as GoogleStrategy } from "passport-google-oauth20";
import { config } from "./config";

export interface AuthUser {
    id: string;
    email: string;
    name: string;
    picture?: string;
}

export function setupAuth() {
    passport.use(
        new GoogleStrategy(
            {
                clientID: config.googleClientId,
                clientSecret: config.googleClientSecret,
                callbackURL: `${config.baseUrl}/auth/google/callback`,
            },
            (_accessToken, _refreshToken, profile, done) => {
                const email = profile.emails?.[0]?.value?.toLowerCase() || "";
                const allowed = config.allowedEmails.includes(email);

                if (!allowed) {
                    return done(null, false, { message: `Access denied for: ${email}` });
                }

                const user: AuthUser = {
                    id: profile.id,
                    email,
                    name: profile.displayName || email,
                    picture: profile.photos?.[0]?.value,
                };
                return done(null, user);
            }
        )
    );

    passport.serializeUser((user: any, done) => done(null, user));
    passport.deserializeUser((user: any, done) => done(null, user));
}
