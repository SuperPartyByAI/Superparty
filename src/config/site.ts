/**
 * Sursa unica pentru origin-ul site-ului.
 * 
 * NICIODATĂ nu hardcoda https://superparty.ro (non-www) în altă parte.
 * Folosește mereu SITE_ORIGIN din acest fișier.
 * 
 * @example
 *   import { SITE_ORIGIN, siteUrl } from '@/config/site';
 *   canonical={siteUrl('/animatori-petreceri-copii')}
 */
export const SITE_ORIGIN = 'https://www.superparty.ro' as const;

/**
 * Construiește URL complet cu trailing slash opțional.
 * @param path - calea relativă (ex: '/animatori-petreceri-copii')
 * @param trailingSlash - adaugă slash final (default: false)
 */
export function siteUrl(path: string, trailingSlash = false): string {
    const normalized = path.startsWith('/') ? path : `/${path}`;
    const withSlash = trailingSlash
        ? normalized.endsWith('/') ? normalized : normalized + '/'
        : normalized.replace(/\/$/, '');
    return `${SITE_ORIGIN}${withSlash}`;
}

/** Canonical complet auto-generat din Astro.url.pathname dacă nu e specificat manual. */
export function autoCanonical(pathname: string, trailingSlash = true): string {
    return siteUrl(pathname, trailingSlash);
}
