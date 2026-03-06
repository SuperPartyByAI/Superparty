/**
 * gallery_images.ts — Imagini AI generate din public/wp-content/uploads/generated/
 * Toate căile 2021-2025 *.jpg returnau HTTP 308→/ (soft-404 Vercel).
 * Înlocuite cu imagini generate local, verificate HTTP 200.
 */

const BASE = "/wp-content/uploads";
const GEN = `${BASE}/generated`;

// ─── Hero images (12) — toate AI generate, verificate 200 ────────────────────
export const heroImages = [
  { src: `${GEN}/hero-coperta.jpg`, alt: "Echipa SuperParty — Animatori Petreceri Copii București" },
  { src: `${GEN}/party2_bear_1772698449725.png`, alt: "Animatori pentru copii" },
  { src: `${GEN}/party_batman_1772696670487.png`, alt: "Batman la petrecere copii" },
  { src: `${GEN}/party_pikachu_1772696930559.png`, alt: "Pikachu la petrecere copii" },
  { src: `${GEN}/party_spiderman_1772697170534.png`, alt: "Spiderman la petrecere" },
  { src: `${GEN}/party_aurora_1772697306142.png`, alt: "Elsa, Ana si Olaf la petrecere" },
  { src: `${GEN}/party2_mario_1772698389935.png`, alt: "Mario la petrecere copii" },
  { src: `${GEN}/party2_skye_1772698531817.png`, alt: "Skye PAW Patrol la petrecere" },
  { src: `${GEN}/party_sonic_1772697050530.png`, alt: "Sonic la petrecere copii" },
  { src: `${GEN}/party_tinkerbell_1772697066743.png`, alt: "Tinkerbell la petrecere" },
  { src: `${GEN}/party2_dragon_1772698409388.png`, alt: "Dragon la petrecere copii" },
  { src: `${GEN}/party_snow_white_1772697257789.png`, alt: "Cenusareasa la petrecere" },
] as const;

// ─── Gallery images — toate AI generate, verificate 200 ──────────────────────
export const galleryImages = [
  // Animatori
  { src: `${GEN}/party_masha_1772697323772.png`, alt: "Animatori profesionisti", category: "animatori" },
  { src: `${GEN}/party2_bear_1772698449725.png`, alt: "Animatori copii", category: "animatori" },
  { src: `${GEN}/party2_masha_mascot_1772698602775.png`, alt: "Animatori la domiciliu", category: "animatori" },
  { src: `${GEN}/party2_mario_1772698389935.png`, alt: "SuperParty animatori", category: "animatori" },
  { src: `${GEN}/party_snow_white_1772697257789.png`, alt: "Cenusareasa si Printul", category: "animatori" },
  { src: `${GEN}/party_aurora_1772697306142.png`, alt: "Printesele Disney", category: "animatori" },
  { src: `${GEN}/party2_chase_mascot_1772698662873.png`, alt: "Mascote petreceri copii", category: "animatori" },
  // Personaje — imagini AI
  { src: `${GEN}/party_batman_1772696670487.png`, alt: "Batman la petrecere cu copii", category: "personaje" },
  { src: `${GEN}/party_spiderman_1772697170534.png`, alt: "Spiderman la petrecere copii", category: "personaje" },
  { src: `${GEN}/party_pikachu_1772696930559.png`, alt: "Pikachu la petrecere", category: "personaje" },
  { src: `${GEN}/party_sonic_1772697050530.png`, alt: "Sonic la petrecere copii", category: "personaje" },
  { src: `${GEN}/party2_mario_1772698389935.png`, alt: "Mario la petrecere", category: "personaje" },
  { src: `${GEN}/party_ladybug_1772697235867.png`, alt: "Ladybug la petrecere", category: "personaje" },
  { src: `${GEN}/party_tinkerbell_1772697066743.png`, alt: "Tinkerbell la petrecere", category: "personaje" },
  { src: `${GEN}/party2_belle_1772698205454.png`, alt: "Belle la petrecere", category: "personaje" },
  { src: `${GEN}/party2_blackcat_1772698166362.png`, alt: "Superman petreceri copii", category: "personaje" },
  { src: `${GEN}/party_tinkerbell_1772697066743.png`, alt: "Elsa Ana Olaf 2025", category: "personaje" },
  // Decor
  { src: `${GEN}/party2_belle_1772698205454.png`, alt: "Arcada baloane", category: "decor" },
  { src: `${GEN}/party2_pinksequin_1772698747291.png`, alt: "Decoratiuni baloane", category: "decor" },
  { src: `${GEN}/party2_dragon_1772698409388.png`, alt: "Baloane cu heliu", category: "decor" },
  { src: `${GEN}/party2_skye_1772698531817.png`, alt: "Decoratiuni baloane petrecere", category: "decor" },
  // Extra
  { src: `${GEN}/party_pumpkin_1772697484876.png`, alt: "Vata de zahar", category: "extra" },
  { src: `${GEN}/party2_bumblebee_1772698238726.png`, alt: "Popcorn petreceri", category: "extra" },
  { src: `${GEN}/party_pirate_1772696983702.png`, alt: "Piniata SuperParty", category: "extra" },
  { src: `${GEN}/party2_sofia_1772697389928.png`, alt: "Ursitoare la botez", category: "extra" },
  { src: `${GEN}/party_mulan_1772697439176.png`, alt: "Ursitoare botez Bucuresti", category: "extra" },
] as const;

// ─── Product images (Super 1–7) ───────────────────────────────────────────────
export const productImages: Record<string, string> = {
  super1: `${GEN}/party_masha_1772697323772.png`,
  super2: `${GEN}/party2_bear_1772698449725.png`,
  super3: `${GEN}/party2_mario_1772698389935.png`,
  super4: `${GEN}/party2_peterpan_1772698184131.png`,
  super5: `${GEN}/party_pumpkin_1772697484876.png`,
  super6: `${GEN}/party2_pinksequin_1772698747291.png`,
  super7: `${GEN}/party2_sofia_1772697389928.png`,
};

// ─── Slider images (10 cele mai bune) ─────────────────────────────────────────
export const sliderImages = heroImages.slice(0, 10);
