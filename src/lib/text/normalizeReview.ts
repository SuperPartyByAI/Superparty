/**
 * normalizeReview.ts — fix mojibake + normalize punctuation + child label helper
 */

/**
 * Fix mojibake: re-encode latin1-misinterpreted UTF-8, max 3 passes.
 */
export function fixMojibake(s: string, maxPasses = 3): string {
    if (!s || typeof s !== 'string') return s;
    let prev = s;
    for (let i = 0; i < maxPasses; i++) {
        try {
            const bytes = new Uint8Array(prev.length);
            for (let j = 0; j < prev.length; j++) {
                const code = prev.charCodeAt(j);
                if (code > 255) return prev; // already valid unicode, stop
                bytes[j] = code;
            }
            const decoded = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
            if (decoded === prev) break;
            prev = decoded;
        } catch {
            break; // not valid utf-8, keep previous
        }
    }
    return prev;
}

// Common mojibake detection patterns
const MOJIBAKE_PATTERNS = /Ã[¢®°ÃÂ¯]|Ä[Ă€ƒ†]|È[™Š]|â€[˜™š]|BucureÈ|Ã®n?|Å[£¸ ]|ÅŸ|ÄÆ'/;

export function hasMojibake(s: string): boolean {
    return MOJIBAKE_PATTERNS.test(s ?? '');
}

/**
 * Normalize Romanian typography:
 * - Fix mojibake if detected
 * - Normalize quotes: â€œ/â€ → „/", â€™ → '
 * - Normalize dashes: â€" → —, â€" → –
 * - Normalize non-breaking spaces → regular spaces
 * - Clean double spaces
 */
export function normalizeReview(text: string): string {
    if (!text) return text;

    let s = text;

    // Fix mojibake first
    if (hasMojibake(s)) {
        s = fixMojibake(s);
    }

    // Normalize quotes and dashes (after mojibake fix)
    s = s
        .replace(/\u00e2\u0080\u009c|\u201c/g, '„')   // opening quote
        .replace(/\u00e2\u0080\u009d|\u201d/g, '"')   // closing quote
        .replace(/\u00e2\u0080\u0099|\u2019/g, "'")   // apostrophe
        .replace(/\u00e2\u0080\u0093|\u2013/g, '–')   // en dash
        .replace(/\u00e2\u0080\u0094|\u2014/g, '—')   // em dash
        .replace(/\u00a0/g, ' ')                        // non-breaking space
        .replace(/  +/g, ' ')                            // double spaces
        .trim();

    return s;
}

/**
 * Gender-safe phrasing for Romanian reviews.
 * - "Ei, Prenume," → "Fetiței Prenume," (girls by context)
 * - "lui Prenume" stays as-is (boys)
 * - No pronoun when uncertain
 */
export function genderSafeText(text: string): string {
    if (!text) return text;
    let s = text;
    // "Ei, Name," → "Fetiței Name,"
    s = s.replace(/\bEi,\s+([A-ZĂÎȘȚÂ][a-zăîșțâA-ZĂÎȘȚÂ\-]+),/g, 'Fetiței $1,');
    // "Ei, Name verb" (no comma after name)
    s = s.replace(/\bEi,\s+([A-ZĂÎȘȚÂ][a-zăîșțâA-ZĂÎȘȚÂ\-]+)\s+(i-au|i-a|l-au|a\s|ei\s)/g, 'Fetiței $1 $2');
    return s.replace(/  +/g, ' ');
}

/**
 * Infer child label from testimonial text (neutral default).
 * Returns: 'băiețel' | 'fetiță' | 'copil'
 * Only uses explicit words in text — does NOT invent.
 */
export function inferChildLabel(text: string): 'băiețel' | 'fetiță' | 'copil' {
    if (!text) return 'copil';
    const t = text.toLowerCase();
    if (/\b(băiețel|băiat|fiul|fiul meu|lui)\b/.test(t)) return 'băiețel';
    if (/\b(fetiță|fata|fiica|fiica mea)\b/.test(t)) return 'fetiță';
    return 'copil';
}

/**
 * Full pipeline: fix encoding + gender-safe phrasing
 */
export function processReview(text: string): string {
    return genderSafeText(normalizeReview(text));
}
