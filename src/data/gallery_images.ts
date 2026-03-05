/**
 * gallery_images.ts — Real photos from public/wp-content/uploads
 * All paths verified to exist in public/wp-content/uploads/
 */

const BASE = "/wp-content/uploads";

// ─── Hero images (12) — animatori + personaje + actiune ──────────────────────
export const heroImages = [
  { src: `${BASE}/2021/04/animatori-1.jpg`, alt: "Animatori profesioniști SuperParty" },
  { src: `${BASE}/2021/04/animatori-copii-1.jpg`, alt: "Animatori pentru copii" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-elsa-ana-olaf.jpg`, alt: "Animatori Elsa, Ana și Olaf" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-mickey-mouse-si-minnie-mouse.jpg`, alt: "Mickey și Minnie Mouse la petrecere" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`, alt: "Animatori SuperParty" },
  { src: `${BASE}/2025/01/animator-spiderman.jpg`, alt: "Animator Spiderman" },
  { src: `${BASE}/2025/01/animatori-elsa-ana-si-olaf.jpg`, alt: "Elsa, Ana și Olaf 2025" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-acasa.jpg`, alt: "Animatori la domiciliu" },
  { src: `${BASE}/2021/04/printesele-disney.jpg`, alt: "Prințesele Disney" },
  { src: `${BASE}/2021/04/spiderman.jpg`, alt: "Spiderman la petrecere" },
  { src: `${BASE}/2021/04/batman.jpg`, alt: "Batman animatori" },
  { src: `${BASE}/2021/04/cenusareasa-si-print-1.jpg`, alt: "Cenușăreasa și Prințul" },
] as const;

// ─── Gallery images (30+) — mixed categories ──────────────────────────────────
export const galleryImages = [
  // Animatori
  { src: `${BASE}/2021/04/animatori-1.jpg`, alt: "Animatori profesioniști", category: "animatori" },
  { src: `${BASE}/2021/04/animatori-copii-1.jpg`, alt: "Animatori copii", category: "animatori" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-acasa.jpg`, alt: "Animatori la domiciliu", category: "animatori" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`, alt: "SuperParty animatori", category: "animatori" },
  { src: `${BASE}/2021/04/cenusareasa-si-print-1.jpg`, alt: "Cenușăreasa și Prințul", category: "animatori" },
  { src: `${BASE}/2021/04/printesele-disney.jpg`, alt: "Prințesele Disney", category: "animatori" },
  { src: `${BASE}/2025/01/mascote-petreceri-copii-bucuresti.jpg`, alt: "Mascote petreceri copii", category: "animatori" },
  // Personaje
  { src: `${BASE}/2025/01/animator-spiderman.jpg`, alt: "Spiderman", category: "personaje" },
  { src: `${BASE}/2021/04/spiderman.jpg`, alt: "Spiderman la petrecere", category: "personaje" },
  { src: `${BASE}/2021/04/batman.jpg`, alt: "Batman", category: "personaje" },
  { src: `${BASE}/2021/04/superman.jpg`, alt: "Superman", category: "personaje" },
  { src: `${BASE}/2021/04/testoasele-ninja.jpg`, alt: "Testoasele Ninja", category: "personaje" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-elsa-ana-olaf.jpg`, alt: "Elsa Ana Olaf", category: "personaje" },
  { src: `${BASE}/2025/01/animatori-elsa-ana-si-olaf.jpg`, alt: "Elsa Ana Olaf 2025", category: "personaje" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-mickey-mouse-si-minnie-mouse.jpg`, alt: "Mickey Minnie Mouse", category: "personaje" },
  // Decor
  { src: `${BASE}/2023/08/arcada-baloane-superparty.jpg`, alt: "Arcadă baloane", category: "decor" },
  { src: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`, alt: "Decorațiuni baloane", category: "decor" },
  { src: `${BASE}/2022/08/baloane-cu-heliu-superparty.jpg`, alt: "Baloane cu heliu", category: "decor" },
  { src: `${BASE}/2021/04/decoratiuni-baloane-1.jpg`, alt: "Decorațiuni baloane petrecere", category: "decor" },
  // Extra
  { src: `${BASE}/2021/04/vata-de-zahar-1.jpg`, alt: "Vată de zahăr", category: "extra" },
  { src: `${BASE}/2021/04/popcorn-1.jpg`, alt: "Popcorn petreceri", category: "extra" },
  { src: `${BASE}/2021/04/piniata-1.jpg`, alt: "Piniată SuperParty", category: "extra" },
  { src: `${BASE}/2025/01/ursitoare-la-botez.jpg`, alt: "Ursitoare la botez", category: "extra" },
  { src: `${BASE}/2022/08/ursitoare-botez-bucuresti-superparty.jpg`, alt: "Ursitoare botez București", category: "extra" },
] as const;

// ─── Product images (Super 1–7) ───────────────────────────────────────────────
export const productImages: Record<string, string> = {
  super1: `${BASE}/2021/04/animatori-1.jpg`,
  super2: `${BASE}/2021/04/animatori-copii-1.jpg`,
  super3: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`,
  super4: `${BASE}/2021/10/pachet-4-a.jpg`,
  super5: `${BASE}/2021/04/vata-de-zahar-1.jpg`,
  super6: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`,
  super7: `${BASE}/2025/01/ursitoare-la-botez.jpg`,
};

// ─── Slider images (10 cele mai bune) ────────────────────────────────────────
export const sliderImages = heroImages.slice(0, 10);
