/**
 * normalizeReview.ts — fix mojibake + normalize punctuation + child label helper
 */

/**
 * Fix mojibake: re-encode Windows-1252 / latin1-misinterpreted UTF-8, max 3 passes.
 * Needed because mojibake strings can contain CP1252 chars like "ƒ", "€", "\u2018", "\u2019" etc.
 */
const WIN1252_CODEPOINT_TO_BYTE: Record<number, number> = {
    0x20AC: 0x80, 0x201A: 0x82, 0x0192: 0x83, 0x201E: 0x84, 0x2026: 0x85, 0x2020: 0x86, 0x2021: 0x87,
    0x02C6: 0x88, 0x2030: 0x89, 0x0160: 0x8A, 0x2039: 0x8B, 0x0152: 0x8C, 0x017D: 0x8E,
    0x2018: 0x91, 0x2019: 0x92, 0x201C: 0x93, 0x201D: 0x94, 0x2022: 0x95, 0x2013: 0x96, 0x2014: 0x97,
    0x02DC: 0x98, 0x2122: 0x99, 0x0161: 0x9A, 0x203A: 0x9B, 0x0153: 0x9C, 0x017E: 0x9E, 0x0178: 0x9F,
};

export function fixMojibake(s: string, maxPasses = 3): string {
    if (!s || typeof s !== 'string') return s;
    let prev = s;
    for (let i = 0; i < maxPasses; i++) {
        try {
            const bytes = new Uint8Array(prev.length);
            for (let j = 0; j < prev.length; j++) {
                const code = prev.charCodeAt(j);
                const b = (code <= 0xFF) ? code : WIN1252_CODEPOINT_TO_BYTE[code];
                if (b === undefined) return prev; // not a single-byte mojibake string
                bytes[j] = b;
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


// Mojibake detection patterns (aligned with CI guardrail signals)
const MOJIBAKE_PATTERNS = /(BucureÈ|PÄ|mulÈ|Ã.|Â.|â€.|È™|È›|Å£|ÅŸ)/;

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
