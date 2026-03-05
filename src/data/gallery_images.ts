/**
 * gallery_images.ts — Real photos from wp-content/uploads
 * Used for Hero, Gallery slider, and Product images.
 * All photos are real (no AI/stock).
 */

const BASE = "/wp-content/uploads";

// ─── Hero images (12) — animatori + personaje + actiune ──────────────────────
export const heroImages = [
  { src: `${BASE}/2022/09/animatori-petreceri-copii-bucuresti.jpg`, alt: "Animatori petreceri copii București" },
  { src: `${BASE}/2023/08/animatori-petreceri-copii-super-party-1.jpg`, alt: "SuperParty animatori copii" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-elsa-ana-olaf.jpg`, alt: "Animatori Elsa, Ana și Olaf" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-mickey-mouse-si-minnie-mouse.jpg`, alt: "Mickey și Minnie Mouse la petrecere" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`, alt: "Animatori SuperParty București" },
  { src: `${BASE}/2025/01/animator-spiderman.jpg`, alt: "Animator Spiderman petreceri copii" },
  { src: `${BASE}/2025/01/animatori-elsa-ana-si-olaf.jpg`, alt: "Elsa, Ana și Olaf la petrecere" },
  { src: `${BASE}/2021/04/animatori-copii-1.jpg`, alt: "Animatori pentru copii București" },
  { src: `${BASE}/2022/09/animatori-petreceri-copii.jpg`, alt: "Animatori petreceri copii" },
  { src: `${BASE}/2021/04/animatori-1.jpg`, alt: "Animatori profesionisti" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-acasa.jpg`, alt: "Animatori petreceri copii acasă" },
  { src: `${BASE}/2021/04/printesele-disney.jpg`, alt: "Prințesele Disney la petrecere" },
] as const;

// ─── Gallery images (30) — mixed: animatori + personaje + decor ───────────────
export const galleryImages = [
  // Animatori în acțiune (10)
  { src: `${BASE}/2022/09/animatori-petreceri-copii-bucuresti.jpg`, alt: "Animatori copii București", category: "animatori" },
  { src: `${BASE}/2023/08/animatori-petreceri-copii-super-party-1.jpg`, alt: "Animatori SuperParty", category: "animatori" },
  { src: `${BASE}/2021/04/animatori-copii-1.jpg`, alt: "Animatori pentru copii", category: "animatori" },
  { src: `${BASE}/2021/04/animatori-1.jpg`, alt: "Animatori profesioniști", category: "animatori" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-acasa.jpg`, alt: "Animatori la domiciliu", category: "animatori" },
  { src: `${BASE}/2022/09/animatori-petreceri-copii.jpg`, alt: "Animatori petreceri", category: "animatori" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`, alt: "SuperParty animatori", category: "animatori" },
  { src: `${BASE}/2025/01/mascote-petreceri-copii-bucuresti.jpg`, alt: "Mascote petreceri copii București", category: "animatori" },
  { src: `${BASE}/2021/04/cenusareasa-si-print-1.jpg`, alt: "Cenușăreasa și Prințul", category: "animatori" },
  { src: `${BASE}/2021/04/printesele-disney.jpg`, alt: "Prințesele Disney", category: "animatori" },
  // Personaje (10)
  { src: `${BASE}/2025/01/animator-spiderman.jpg`, alt: "Animator Spiderman", category: "personaje" },
  { src: `${BASE}/2021/04/spiderman.jpg`, alt: "Spiderman la petrecere", category: "personaje" },
  { src: `${BASE}/2021/04/batman.jpg`, alt: "Batman animatori copii", category: "personaje" },
  { src: `${BASE}/2021/04/superman.jpg`, alt: "Superman petreceri copii", category: "personaje" },
  { src: `${BASE}/2021/04/testoasele-ninja.jpg`, alt: "Testoasele Ninja", category: "personaje" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-elsa-ana-olaf.jpg`, alt: "Elsa Ana Olaf", category: "personaje" },
  { src: `${BASE}/2025/01/animatori-elsa-ana-si-olaf.jpg`, alt: "Elsa Ana Olaf 2025", category: "personaje" },
  { src: `${BASE}/2021/04/animatori-petreceri-copii-mickey-mouse-si-minnie-mouse.jpg`, alt: "Mickey Minnie Mouse", category: "personaje" },
  // Decor & extra (5)
  { src: `${BASE}/2023/08/arcada-baloane-superparty.jpg`, alt: "Arcadă baloane SuperParty", category: "decor" },
  { src: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`, alt: "Decorațiuni baloane", category: "decor" },
  { src: `${BASE}/2022/08/baloane-cu-heliu-superparty.jpg`, alt: "Baloane cu heliu", category: "decor" },
  { src: `${BASE}/2023/08/decoratiuni-baloane-aranjamente.jpg`, alt: "Aranjamente baloane", category: "decor" },
  { src: `${BASE}/2025/01/baloane-heliu.jpg`, alt: "Baloane heliu 2025", category: "decor" },
  // Vată, popcorn, piniată, ursitoare (5)
  { src: `${BASE}/2021/04/vata-de-zahar-1.jpg`, alt: "Vată de zahăr petreceri", category: "extra" },
  { src: `${BASE}/2021/04/popcorn-1.jpg`, alt: "Popcorn petreceri copii", category: "extra" },
  { src: `${BASE}/2021/04/piniata-superparty-1.jpg`, alt: "Piniată SuperParty", category: "extra" },
  { src: `${BASE}/2025/01/ursitoare-la-botez.jpg`, alt: "Ursitoare la botez", category: "extra" },
  { src: `${BASE}/2022/08/ursitoare-botez-bucuresti-superparty.jpg`, alt: "Ursitoare botez București", category: "extra" },
] as const;

// ─── Product images mapping (Super 1-7) ──────────────────────────────────────
export const productImages: Record<string, string> = {
  super1: `${BASE}/2022/09/animatori-petreceri-copii-bucuresti.jpg`,
  super2: `${BASE}/2022/09/animatori-petreceri-copii.jpg`,
  super3: `${BASE}/2023/08/animatori-petreceri-copii-super-party-1.jpg`,
  super4: `${BASE}/2021/04/animatori-petreceri-copii-superparty-2.jpg`,
  super5: `${BASE}/2021/04/vata-de-zahar-1.jpg`,
  super6: `${BASE}/2022/08/decoratiuni-baloane-superparty.jpg`,
  super7: `${BASE}/2025/01/ursitoare-la-botez.jpg`,
};

// ─── Slider images for "Cum arată o petrecere" section (8-12) ─────────────────
export const sliderImages = heroImages.slice(0, 10);
