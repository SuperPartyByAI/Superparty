/**
 * gallery.ts — imagini reale din wp-content/uploads
 * Categorizate: animatori / personaje / decor / vata-popcorn / ursitoare
 *
 * CONSTRÂNGERE: toate URL-urile TREBUIE să conțină /wp-content/uploads/
 */

export type GalleryCategory = 'animatori' | 'personaje' | 'decor' | 'vata-popcorn' | 'ursitoare';

export interface GalleryImage {
    url: string;
    alt: string;
    category: GalleryCategory;
}

const BASE = 'https://www.superparty.ro/wp-content/uploads';
const CAT = `${BASE}/catalog`;

/** Hero slider (12 imagini curate) */
export const galleryHero: GalleryImage[] = [
    { url: `${BASE}/2021/04/animatori-1.jpg`, alt: 'Animatori profesioniști SuperParty', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-copii-1.jpg`, alt: 'Animatori pentru copii', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-elsa-ana-olaf.jpg`, alt: 'Elsa, Ana și Olaf la petrecere', category: 'personaje' },
    { url: `${BASE}/2025/01/animator-spiderman.jpg`, alt: 'Animator Spiderman petreceri', category: 'personaje' },
    { url: `${BASE}/2025/01/animatori-elsa-ana-si-olaf.jpg`, alt: 'Elsa Ana Olaf 2025', category: 'personaje' },
    { url: `${BASE}/2023/08/arcada-baloane-superparty.jpg`, alt: 'Arcadă baloane SuperParty', category: 'decor' },
    { url: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`, alt: 'Decorațiuni baloane', category: 'decor' },
    { url: `${BASE}/2021/04/vata-de-zahar-1.jpg`, alt: 'Vată de zahăr la petrecere', category: 'vata-popcorn' },
    { url: `${BASE}/2025/01/ursitoare-la-botez.jpg`, alt: 'Ursitoare la botez', category: 'ursitoare' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-mickey-mouse-si-minnie-mouse.jpg`, alt: 'Mickey și Minnie Mouse', category: 'personaje' },
    { url: `${BASE}/2021/04/cenusareasa-si-print-1.jpg`, alt: 'Cenușăreasa și Prințul', category: 'animatori' },
    { url: `${BASE}/2022/08/baloane-cu-heliu-superparty.jpg`, alt: 'Baloane cu heliu SuperParty', category: 'decor' },
];

/** Galerie extinsă — animatori + personaje catalog + decor + vată + ursitoare */
export const galleryAll: GalleryImage[] = [
    // ── Animatori (10) ───────────────────────────────────────────────────────────
    { url: `${BASE}/2021/04/animatori-1.jpg`, alt: 'Animatori profesioniști', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-copii-1.jpg`, alt: 'Animatori copii distracție', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-acasa.jpg`, alt: 'Animatori la domiciliu', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`, alt: 'SuperParty animatori', category: 'animatori' },
    { url: `${BASE}/2021/04/printesele-disney.jpg`, alt: 'Prințesele Disney la petrecere', category: 'animatori' },
    { url: `${BASE}/2021/04/cenusareasa-si-print-1.jpg`, alt: 'Cenușăreasa și Prințul', category: 'animatori' },
    { url: `${BASE}/2025/01/mascote-petreceri-copii-bucuresti.jpg`, alt: 'Mascote petreceri copii București', category: 'animatori' },
    { url: `${BASE}/2025/01/animatori-elsa-ana-si-olaf.jpg`, alt: 'Elsa Ana și Olaf animatori 2025', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-elsa-ana-olaf.jpg`, alt: 'Elsa, Ana și Olaf animatori', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-mickey-mouse-si-minnie-mouse.jpg`, alt: 'Mickey și Minnie Mouse animatori', category: 'animatori' },

    // ── Personaje catalog (20) ───────────────────────────────────────────────────
    { url: `${CAT}/catalog_batman_v2.png`, alt: 'Batman costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_catboy_v2.png`, alt: 'Catboy PJ Masks petreceri', category: 'personaje' },
    { url: `${CAT}/catalog_chase_v2.png`, alt: 'Chase PAW Patrol petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_creeper_mascot_white_bg_1772227659492.png`, alt: 'Creeper Minecraft mascotă', category: 'personaje' },
    { url: `${CAT}/catalog_jerry_white_socks_1772227473767.png`, alt: 'Jerry mascotă petreceri', category: 'personaje' },
    { url: `${CAT}/catalog_luigi_white_bg_1772228548656.png`, alt: 'Luigi costume petreceri', category: 'personaje' },
    { url: `${CAT}/catalog_marshall_white_bg_1772228862325.png`, alt: 'Marshall PAW Patrol petreceri', category: 'personaje' },
    { url: `${CAT}/catalog_mickey_minnie_white_socks_1772227498889.png`, alt: 'Mickey și Minnie Mouse costume', category: 'personaje' },
    { url: `${CAT}/catalog_minion_white_bg_1772228616789.png`, alt: 'Minion costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_minnie_pink_white_bg_1772228695778.png`, alt: 'Minnie Mouse roz costume', category: 'personaje' },
    { url: `${CAT}/catalog_pikachu_white_bg_1772227634017.png`, alt: 'Pikachu Pokemon costume petreceri', category: 'personaje' },
    { url: `${CAT}/catalog_pirate_boy_white_bg_1772228804806.png`, alt: 'Pirat costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_princess_peach_white_bg_1772228877627.png`, alt: 'Prințesa Peach costume petreceri', category: 'personaje' },
    { url: `${CAT}/catalog_rocky_white_bg_1772228534226.png`, alt: 'Rocky PAW Patrol costume', category: 'personaje' },
    { url: `${CAT}/catalog_sonic_white_bg_1772227646947.png`, alt: 'Sonic The Hedgehog costume', category: 'personaje' },
    { url: `${CAT}/catalog_tinkerbel_white_bg_1772228708465.png`, alt: 'Tinker Bell costume petreceri', category: 'personaje' },
    { url: `${CAT}/catalog_tom_white_socks_1772227485311.png`, alt: 'Tom mascotă petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_unicorn_colorful_white_bg_1772228722896.png`, alt: 'Unicorn colorat costume petreceri', category: 'personaje' },
    { url: `${BASE}/2025/01/animator-spiderman.jpg`, alt: 'Animator Spiderman petreceri', category: 'personaje' },
    { url: `${BASE}/2021/04/spiderman.jpg`, alt: 'Spiderman la petrecere', category: 'personaje' },
    { url: `${BASE}/2021/04/batman.jpg`, alt: 'Batman animatori copii', category: 'personaje' },
    { url: `${BASE}/2021/04/superman.jpg`, alt: 'Superman petreceri copii', category: 'personaje' },
    { url: `${BASE}/2021/04/testoasele-ninja.jpg`, alt: 'Testoasele Ninja', category: 'personaje' },

    // ── Decor & baloane (8) ──────────────────────────────────────────────────────
    { url: `${BASE}/2023/08/arcada-baloane-superparty.jpg`, alt: 'Arcadă baloane SuperParty', category: 'decor' },
    { url: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`, alt: 'Decorațiuni baloane', category: 'decor' },
    { url: `${BASE}/2022/08/baloane-cu-heliu-superparty.jpg`, alt: 'Baloane cu heliu SuperParty', category: 'decor' },
    { url: `${BASE}/2021/04/decoratiuni-baloane-1.jpg`, alt: 'Decorațiuni baloane petrecere', category: 'decor' },
    { url: `${BASE}/2021/04/decoratiuni-baloane-pentru-copii-1.jpg`, alt: 'Decorațiuni baloane copii', category: 'decor' },
    { url: `${BASE}/2021/04/decoratiuni-din-baloane-1.jpg`, alt: 'Decorațiuni din baloane', category: 'decor' },
    { url: `${BASE}/2021/04/piniata-1.jpg`, alt: 'Piniată SuperParty', category: 'decor' },
    { url: `${BASE}/2021/04/piniata-copii-1.jpg`, alt: 'Piniată petreceri copii', category: 'decor' },

    // ── Vată & Popcorn (4) ───────────────────────────────────────────────────────
    { url: `${BASE}/2021/04/vata-de-zahar-1.jpg`, alt: 'Vată de zahăr petreceri', category: 'vata-popcorn' },
    { url: `${BASE}/2021/04/popcorn-1.jpg`, alt: 'Popcorn petreceri copii', category: 'vata-popcorn' },
    { url: `${BASE}/2021/04/vata-de-zahar-pe-bat.jpg`, alt: 'Vată de zahăr pe băț', category: 'vata-popcorn' },
    { url: `${BASE}/2021/04/vata-pe-bat-1.jpg`, alt: 'Vată colorată pe băț', category: 'vata-popcorn' },

    // ── Ursitoare (4) ────────────────────────────────────────────────────────────
    { url: `${BASE}/2025/01/ursitoare-la-botez.jpg`, alt: 'Ursitoare la botez 2025', category: 'ursitoare' },
    { url: `${BASE}/2022/08/ursitoare-botez-bucuresti-superparty.jpg`, alt: 'Ursitoare botez București', category: 'ursitoare' },
    { url: `${BASE}/2021/10/mos-craciun-de-inchiriat-1-a.jpg`, alt: 'Moș Crăciun de închiriat', category: 'ursitoare' },
    { url: `${BASE}/2021/10/inchiriere-mos-craciun-bucuresti-1-a.jpg`, alt: 'Închiriere Moș Crăciun București', category: 'ursitoare' },
];

// ── Build-time validation ─────────────────────────────────────────────────────
const UPLOADS_PATTERN = /\/wp-content\/uploads\//;
const allImages = [...galleryHero, ...galleryAll];
const invalid = allImages.filter(img => !UPLOADS_PATTERN.test(img.url));
if (invalid.length > 0) {
    throw new Error(`[gallery.ts] INVALID IMAGE URLs (must be from /wp-content/uploads/): ${invalid.map(i => i.url).join(', ')}`);
}

/** productImages: mapare Super 1-7 → URL imagine */
export const productImages: Record<string, string> = {
    super1: `${BASE}/2021/04/animatori-1.jpg`,
    super2: `${BASE}/2021/04/animatori-copii-1.jpg`,
    super3: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`,
    super4: `${BASE}/2021/10/pachet-4-a.jpg`,
    super5: `${BASE}/2021/04/vata-de-zahar-1.jpg`,
    super6: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`,
    super7: `${BASE}/2025/01/ursitoare-la-botez.jpg`,
};
