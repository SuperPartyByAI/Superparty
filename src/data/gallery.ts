/**
 * gallery.ts — imagini reale din wp-content/uploads
 * Categorizate: animatori / personaje / decor / vata-popcorn / ursitoare
 * 
 * CONSTRÂNGERE: toate URL-urile TREBUIE să conțină /wp-content/uploads/
 * Validare automată la build.
 */

export type GalleryCategory = 'animatori' | 'personaje' | 'decor' | 'vata-popcorn' | 'ursitoare';

export interface GalleryImage {
    url: string;
    alt: string;
    category: GalleryCategory;
}

const BASE = 'https://www.superparty.ro/wp-content/uploads';

/** Hero slider (12 imagini curate) */
export const galleryHero: GalleryImage[] = [
    { url: `${BASE}/2022/09/animatori-petreceri-copii-bucuresti.jpg`, alt: 'Animatori petreceri copii București', category: 'animatori' },
    { url: `${BASE}/2023/08/animatori-petreceri-copii-super-party-1.jpg`, alt: 'SuperParty animatori 2023', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-elsa-ana-olaf.jpg`, alt: 'Elsa, Ana și Olaf la petrecere', category: 'personaje' },
    { url: `${BASE}/2025/01/animator-spiderman.jpg`, alt: 'Animator Spiderman petreceri', category: 'personaje' },
    { url: `${BASE}/2025/01/animatori-elsa-ana-si-olaf.jpg`, alt: 'Elsa Ana Olaf animatori 2025', category: 'personaje' },
    { url: `${BASE}/2023/08/arcada-baloane-superparty.jpg`, alt: 'Arcadă baloane SuperParty', category: 'decor' },
    { url: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`, alt: 'Decorațiuni baloane', category: 'decor' },
    { url: `${BASE}/2021/04/vata-de-zahar-1.jpg`, alt: 'Vată de zahăr la petrecere', category: 'vata-popcorn' },
    { url: `${BASE}/2025/01/ursitoare-la-botez.jpg`, alt: 'Ursitoare la botez', category: 'ursitoare' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-mickey-mouse-si-minnie-mouse.jpg`, alt: 'Mickey și Minnie Mouse', category: 'personaje' },
    { url: `${BASE}/2021/04/animatori-copii-1.jpg`, alt: 'Animatori pentru copii', category: 'animatori' },
    { url: `${BASE}/2022/08/baloane-cu-heliu-superparty.jpg`, alt: 'Baloane cu heliu SuperParty', category: 'decor' },
];

/** Galerie extinsă (40 imagini, toate categoriile) */
export const galleryAll: GalleryImage[] = [
    // ── Animatori (12) ─────────────────────────────────────────────
    { url: `${BASE}/2022/09/animatori-petreceri-copii-bucuresti.jpg`, alt: 'Animatori petreceri copii București', category: 'animatori' },
    { url: `${BASE}/2022/09/animatori-petreceri-copii.jpg`, alt: 'Animatori petreceri copii', category: 'animatori' },
    { url: `${BASE}/2023/08/animatori-petreceri-copii-super-party-1.jpg`, alt: 'SuperParty animatori 2023', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-1.jpg`, alt: 'Animatori profesioniști', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-copii-1.jpg`, alt: 'Animatori copii distracție', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-acasa.jpg`, alt: 'Animatori la domiciliu', category: 'animatori' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`, alt: 'SuperParty animatori', category: 'animatori' },
    { url: `${BASE}/2021/04/printesele-disney.jpg`, alt: 'Prințesele Disney la petrecere', category: 'animatori' },
    { url: `${BASE}/2021/04/cenusareasa-si-print-1.jpg`, alt: 'Cenușăreasa și Prințul', category: 'animatori' },
    { url: `${BASE}/2025/01/mascote-petreceri-copii-bucuresti.jpg`, alt: 'Mascote petreceri copii București', category: 'animatori' },
    { url: `${BASE}/2023/08/animatori-petreceri-copii-superparty-2023.jpg`, alt: 'Animatori SuperParty 2023', category: 'animatori' },
    { url: `${BASE}/2021/04/petrecere-copii-acasa-1.jpg`, alt: 'Petrecere copii acasă', category: 'animatori' },

    // ── Personaje (10) ──────────────────────────────────────────────
    { url: `${BASE}/2025/01/animator-spiderman.jpg`, alt: 'Animator Spiderman', category: 'personaje' },
    { url: `${BASE}/2021/04/spiderman.jpg`, alt: 'Spiderman la petrecere', category: 'personaje' },
    { url: `${BASE}/2021/04/batman.jpg`, alt: 'Batman animatori copii', category: 'personaje' },
    { url: `${BASE}/2021/04/superman.jpg`, alt: 'Superman petreceri copii', category: 'personaje' },
    { url: `${BASE}/2021/04/testoasele-ninja.jpg`, alt: 'Testoasele Ninja', category: 'personaje' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-elsa-ana-olaf.jpg`, alt: 'Elsa Ana Olaf', category: 'personaje' },
    { url: `${BASE}/2025/01/animatori-elsa-ana-si-olaf.jpg`, alt: 'Elsa Ana Olaf 2025', category: 'personaje' },
    { url: `${BASE}/2021/04/animatori-petreceri-copii-mickey-mouse-si-minnie-mouse.jpg`, alt: 'Mickey Minnie Mouse', category: 'personaje' },
    { url: `${BASE}/2021/04/printesele-disney.jpg`, alt: 'Prințesele Disney', category: 'personaje' },
    { url: `${BASE}/2021/04/cenusareasa-si-print-1.jpg`, alt: 'Cenușăreasa și Prințul', category: 'personaje' },

    // ── Decor & baloane (10) ────────────────────────────────────────
    { url: `${BASE}/2023/08/arcada-baloane-superparty.jpg`, alt: 'Arcadă baloane SuperParty', category: 'decor' },
    { url: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`, alt: 'Decorațiuni baloane', category: 'decor' },
    { url: `${BASE}/2022/08/baloane-cu-heliu-superparty.jpg`, alt: 'Baloane cu heliu SuperParty', category: 'decor' },
    { url: `${BASE}/2023/08/decoratiuni-baloane-aranjamente.jpg`, alt: 'Aranjamente baloane', category: 'decor' },
    { url: `${BASE}/2025/01/baloane-heliu.jpg`, alt: 'Baloane heliu 2025', category: 'decor' },
    { url: `${BASE}/2022/07/arcada-baloane-botez-1.jpg`, alt: 'Arcadă baloane botez', category: 'decor' },
    { url: `${BASE}/2022/07/arcada-baloane-majorat-1.jpg`, alt: 'Arcadă baloane majorat', category: 'decor' },
    { url: `${BASE}/2022/07/baloane-cu-heliu-1.jpg`, alt: 'Baloane cu heliu', category: 'decor' },
    { url: `${BASE}/2022/07/decor-petreceri-copii-bucuresti-1.jpg`, alt: 'Decor petreceri copii', category: 'decor' },
    { url: `${BASE}/2021/04/piniata-superparty-1.jpg`, alt: 'Piniată SuperParty', category: 'decor' },

    // ── Vată & Popcorn (4) ──────────────────────────────────────────
    { url: `${BASE}/2021/04/vata-de-zahar-1.jpg`, alt: 'Vată de zahăr petreceri', category: 'vata-popcorn' },
    { url: `${BASE}/2021/04/popcorn-1.jpg`, alt: 'Popcorn petreceri copii', category: 'vata-popcorn' },
    { url: `${BASE}/2021/04/vata-de-zahar-pe-bat.jpg`, alt: 'Vată de zahăr pe băț', category: 'vata-popcorn' },
    { url: `${BASE}/2021/04/vata-pe-bat-1.jpg`, alt: 'Vată colorată pe băț', category: 'vata-popcorn' },

    // ── Ursitoare (4) ────────────────────────────────────────────────
    { url: `${BASE}/2025/01/ursitoare-la-botez.jpg`, alt: 'Ursitoare la botez 2025', category: 'ursitoare' },
    { url: `${BASE}/2022/08/ursitoare-botez-bucuresti-superparty.jpg`, alt: 'Ursitoare botez București', category: 'ursitoare' },
    { url: `${BASE}/2022/07/ursitoare-botez.jpg`, alt: 'Ursitoare botez', category: 'ursitoare' },
    { url: `${BASE}/2022/07/ursitoare-botez-superparty.jpg`, alt: 'Ursitoare SuperParty botez', category: 'ursitoare' },
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
    super1: `${BASE}/2022/09/animatori-petreceri-copii-bucuresti.jpg`,
    super2: `${BASE}/2022/09/animatori-petreceri-copii.jpg`,
    super3: `${BASE}/2023/08/animatori-petreceri-copii-super-party-1.jpg`,
    super4: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`,
    super5: `${BASE}/2021/04/vata-de-zahar-1.jpg`,
    super6: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`,
    super7: `${BASE}/2025/01/ursitoare-la-botez.jpg`,
};
