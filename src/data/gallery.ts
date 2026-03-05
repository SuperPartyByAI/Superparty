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

/** Galerie extinsă — animatori + personaje + decor + vată + ursitoare */
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

    // ── Personaje animatori reali (5) ────────────────────────────────────────────
    { url: `${BASE}/2025/01/animator-spiderman.jpg`, alt: 'Animator Spiderman petreceri', category: 'personaje' },
    { url: `${BASE}/2021/04/spiderman.jpg`, alt: 'Spiderman la petrecere', category: 'personaje' },
    { url: `${BASE}/2021/04/batman.jpg`, alt: 'Batman animatori copii', category: 'personaje' },
    { url: `${BASE}/2021/04/superman.jpg`, alt: 'Superman petreceri copii', category: 'personaje' },
    { url: `${BASE}/2021/04/testoasele-ninja.jpg`, alt: 'Testoasele Ninja', category: 'personaje' },

    // ── Petreceri cu personaje — imagini AI (30) ──────────────────────────────────
    { url: `${BASE}/generated/party_aurora_1772697306142.png`, alt: 'Aurora la petrecere copii cu baloane și decor', category: 'personaje' },
    { url: `${BASE}/generated/party_catboy_1772696769977.png`, alt: 'Catboy PJ Masks la petrecere copii', category: 'personaje' },
    { url: `${BASE}/generated/party_chase_paw_patrol_1772696788849.png`, alt: 'Chase PAW Patrol la petrecere copii', category: 'personaje' },
    { url: `${BASE}/generated/party_creeper_1772696805101.png`, alt: 'Creeper Minecraft la petrecere copii veseli', category: 'personaje' },
    { url: `${BASE}/generated/party_hello_kitty_1772697405648.png`, alt: 'Hello Kitty la petrecere fetite cu baloane roz', category: 'personaje' },
    { url: `${BASE}/generated/party_jasmine_1772697185539.png`, alt: 'Printesa Jasmine la petrecere copii', category: 'personaje' },
    { url: `${BASE}/generated/party_jerry_1772696831890.png`, alt: 'Jerry Tom and Jerry la petrecere copii', category: 'personaje' },
    { url: `${BASE}/generated/party_ladybug_1772697235867.png`, alt: 'Ladybug Miraculous la petrecere supereroina', category: 'personaje' },
    { url: `${BASE}/generated/party_luigi_1772696850411.png`, alt: 'Luigi Super Mario la petrecere copii', category: 'personaje' },
    { url: `${BASE}/generated/party_marshall_1772696866254.png`, alt: 'Marshall PAW Patrol la petrecere baieti', category: 'personaje' },
    { url: `${BASE}/generated/party_masha_1772697323772.png`, alt: 'Masha la petrecere copii zgarcie-branza', category: 'personaje' },
    { url: `${BASE}/generated/party_merida_1772697374252.png`, alt: 'Merida Brave la petrecere printesa curajoasa', category: 'personaje' },
    { url: `${BASE}/generated/party_minion_1772696909706.png`, alt: 'Minion Despicable Me la petrecere copii haios', category: 'personaje' },
    { url: `${BASE}/generated/party_mulan_1772697439176.png`, alt: 'Mulan la petrecere copii dans razboinic', category: 'personaje' },
    { url: `${BASE}/generated/party_pikachu_1772696930559.png`, alt: 'Pikachu Pokemon la petrecere copii', category: 'personaje' },
    { url: `${BASE}/generated/party_pirate_1772696983702.png`, alt: 'Pirat la petrecere copii aventura', category: 'personaje' },
    { url: `${BASE}/generated/party_princess_peach_1772697000751.png`, alt: 'Princess Peach Mario la petrecere fetite', category: 'personaje' },
    { url: `${BASE}/generated/party_pumpkin_1772697484876.png`, alt: 'Dovleac la petrecere Halloween copii', category: 'personaje' },
    { url: `${BASE}/generated/party_rocky_paw_1772697033025.png`, alt: 'Rocky PAW Patrol la petrecere copii', category: 'personaje' },
    { url: `${BASE}/generated/party_scorpion_1772697202670.png`, alt: 'Scorpion Mortal Kombat la petrecere baieti', category: 'personaje' },
    { url: `${BASE}/generated/party_snow_white_1772697257789.png`, alt: 'Alba ca Zapada la petrecere fetite printesa', category: 'personaje' },
    { url: `${BASE}/generated/party_sofia_1772697389928.png`, alt: 'Sofia Intai la petrecere printesa mica', category: 'personaje' },
    { url: `${BASE}/generated/party_sonic_1772697050530.png`, alt: 'Sonic Hedgehog la petrecere copii rapid', category: 'personaje' },
    { url: `${BASE}/generated/party_spiderman_1772697170534.png`, alt: 'Spiderman la petrecere copii supererou', category: 'personaje' },
    { url: `${BASE}/generated/party_tinkerbell_1772697066743.png`, alt: 'Tinkerbell zanuta la petrecere fetite cu sclipici', category: 'personaje' },
    { url: `${BASE}/generated/party_tom_cat_1772697102222.png`, alt: 'Tom pisica Tom and Jerry la petrecere', category: 'personaje' },
    { url: `${BASE}/generated/party_unicorn_colorful_1772697119156.png`, alt: 'Unicorn curcubeu la petrecere fetite magica', category: 'personaje' },
    { url: `${BASE}/generated/party_unicorn_myp_1772697467861.png`, alt: 'Unicorn My Little Pony la petrecere copii', category: 'personaje' },
    { url: `${BASE}/generated/party_venom_1772697340461.png`, alt: 'Venom Marvel la petrecere baieti antierou', category: 'personaje' },
    { url: `${BASE}/generated/party_wednesday_1772697272978.png`, alt: 'Wednesday Addams la petrecere tematica gotik', category: 'personaje' },

    // ── Catalog personaje (105 costume) ──────────────────────────────────
    { url: `${CAT}/catalog_batman_v2.png`, alt: 'catalog batman v2 costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_catboy_v2.png`, alt: 'catalog catboy v2 costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_chase_v2.png`, alt: 'catalog chase v2 costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_creeper_mascot_white_bg_1772227659492.png`, alt: 'catalog creeper mascot white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_jerry_white_socks_1772227473767.png`, alt: 'catalog jerry white socks costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_luigi_white_bg_1772228548656.png`, alt: 'catalog luigi white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_marshall_white_bg_1772228862325.png`, alt: 'catalog marshall white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_mickey_minnie_white_socks_1772227498889.png`, alt: 'catalog mickey minnie white socks costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_minion_white_bg_1772228616789.png`, alt: 'catalog minion white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_minnie_pink_white_bg_1772228695778.png`, alt: 'catalog minnie pink white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_pikachu_white_bg_1772227634017.png`, alt: 'catalog pikachu white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_pirate_boy_white_bg_1772228804806.png`, alt: 'catalog pirate boy white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_princess_peach_white_bg_1772228877627.png`, alt: 'catalog princess peach white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_rocky_white_bg_1772228534226.png`, alt: 'catalog rocky white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_scorpion_mk_white_bg_1772228793685.png`, alt: 'catalog scorpion mk white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_sonic_white_bg_1772227646947.png`, alt: 'catalog sonic white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_tinkerbel_white_bg_1772228708465.png`, alt: 'catalog tinkerbel white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_tom_white_socks_1772227485311.png`, alt: 'catalog tom white socks costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_unicorn_colorful_white_bg_1772228722896.png`, alt: 'catalog unicorn colorful white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/catalog_unicorn_myp_white_bg_1772228631877.png`, alt: 'catalog unicorn myp white bg costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch10_bluedress_1772215071081.png`, alt: 'costume batch10 bluedress costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch10_eskimo_1772215058099.png`, alt: 'costume batch10 eskimo costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch10_masha_1772215116705.png`, alt: 'costume batch10 masha costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch11_aurora_1772215399839.png`, alt: 'costume batch11 aurora costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch11_pumpkin_1772215414307.png`, alt: 'costume batch11 pumpkin costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch1_auto_red_1772209420014.png`, alt: 'costume batch1 auto red costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch1_dress_fixed_female_1772209865078.png`, alt: 'costume batch1 dress fixed female costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch2_bluegirl_mannequin_1772212488357.png`, alt: 'costume batch2 bluegirl mannequin costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch2_descendant1_newface_1772211504838.png`, alt: 'costume batch2 descendant1 newface costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch2_descendant2_mannequin_1772212475119.png`, alt: 'costume batch2 descendant2 mannequin costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch2_minnie_newface_1772211520039.png`, alt: 'costume batch2 minnie newface costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch3_jerry_mascot_1772212671486.png`, alt: 'costume batch3 jerry mascot costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch3_mickey_minnie_2_1772212656634.png`, alt: 'costume batch3 mickey minnie 2 costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch3_tom_mascot_1772212686119.png`, alt: 'costume batch3 tom mascot costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch4_creeper_fullmask_1772212839126.png`, alt: 'costume batch4 creeper fullmask costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch4_creeper_halfmask_1772212825095.png`, alt: 'costume batch4 creeper halfmask costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch4_hellokitty_1772212797344.png`, alt: 'costume batch4 hellokitty costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch4_jasmine_1772212853290.png`, alt: 'costume batch4 jasmine costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch4_mulan_1772212812179.png`, alt: 'costume batch4 mulan costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch5_elsa_1772213409395.png`, alt: 'costume batch5 elsa costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch5_pikachu_1772213423723.png`, alt: 'costume batch5 pikachu costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch5_reddress_1772213384176.png`, alt: 'costume batch5 reddress costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch5_snowwhite_1772213370870.png`, alt: 'costume batch5 snowwhite costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch5_wednesday_1772213396565.png`, alt: 'costume batch5 wednesday costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch6_ladybug_1772214058802.png`, alt: 'costume batch6 ladybug costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch6_merida_1772213602484.png`, alt: 'costume batch6 merida costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch6_pinksequin_1772213615852.png`, alt: 'costume batch6 pinksequin costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch6_sofia_1772214073648.png`, alt: 'costume batch6 sofia costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch6_spiderman_1772213573063.png`, alt: 'costume batch6 spiderman costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch6_venom_1772213587896.png`, alt: 'costume batch6 venom costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch7_blackcat_1772214200017.png`, alt: 'costume batch7 blackcat costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch7_flamenco_1772214259643.png`, alt: 'costume batch7 flamenco costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch7_jasmine2_1772214233283.png`, alt: 'costume batch7 jasmine2 costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch7_peterpan_1772214274029.png`, alt: 'costume batch7 peterpan costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch7_pinkcorset_1772214247078.png`, alt: 'costume batch7 pinkcorset costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch7_yellowpolka_1772214219742.png`, alt: 'costume batch7 yellowpolka costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch8_bear_1772214408538.png`, alt: 'costume batch8 bear costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch8_gekko_1772214422596.png`, alt: 'costume batch8 gekko costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch8_redtribal_1772214476863.png`, alt: 'costume batch8 redtribal costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch8_snowwhite2_1772214450347.png`, alt: 'costume batch8 snowwhite2 costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch8_thor_1772214436421.png`, alt: 'costume batch8 thor costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch8_unicorn_1772214464372.png`, alt: 'costume batch8 unicorn costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch9_belle1_1772214848662.png`, alt: 'costume batch9 belle1 costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch9_bumblebee_1772214657489.png`, alt: 'costume batch9 bumblebee costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch9_pinkpilot_1772214832999.png`, alt: 'costume batch9 pinkpilot costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch9_scoobydoo_1772214630626.png`, alt: 'costume batch9 scoobydoo costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/costume_batch9_stitch_1772214614523.png`, alt: 'costume batch9 stitch costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/elsa_costume_catalog_1772206309861.png`, alt: 'elsa costume catalog costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_aurora_white_1772225092224.png`, alt: 'mascot costume aurora white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_bear_white_1772225190711.png`, alt: 'mascot costume bear white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_blackcat_white_1772224975564.png`, alt: 'mascot costume blackcat white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_flamenco_white_1772225105790.png`, alt: 'mascot costume flamenco white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_gekko_white_1772225205388.png`, alt: 'mascot costume gekko white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_jasmine2_white_1772225079275.png`, alt: 'mascot costume jasmine2 white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_jasmine_white_1772224614593.png`, alt: 'mascot costume jasmine white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_merida_white_1772224857225.png`, alt: 'mascot costume merida white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_peterpan_white_1772225178461.png`, alt: 'mascot costume peterpan white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_pinksequin_white_1772224869867.png`, alt: 'mascot costume pinksequin white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_racer95_white_1772224769235.png`, alt: 'mascot costume racer95 white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_snowwhite_white_1772224648255.png`, alt: 'mascot costume snowwhite white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_sofia2_white_1772224961264.png`, alt: 'mascot costume sofia2 white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_spiderman_white_1772224741705.png`, alt: 'mascot costume spiderman white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_thor_white_1772225256564.png`, alt: 'mascot costume thor white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_venom_white_1772224755742.png`, alt: 'mascot costume venom white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_costume_yellowpolka_white_1772224988054.png`, alt: 'mascot costume yellowpolka white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_batman_complete_1772226133987.png`, alt: 'mascot full batman complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_bear_complete_1772225967671.png`, alt: 'mascot full bear complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_chase_complete_1772226336829.png`, alt: 'mascot full chase complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_creeper_white_1772224420251.png`, alt: 'mascot full creeper white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_dragon_complete_1772225953904.png`, alt: 'mascot full dragon complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_jerry_white_1772224378701.png`, alt: 'mascot full jerry white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_luigi_complete_1772225937108.png`, alt: 'mascot full luigi complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_mario_complete_1772226280709.png`, alt: 'mascot full mario complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_marshall_complete_1772226030085.png`, alt: 'mascot full marshall complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_masha_complete_1772225981575.png`, alt: 'mascot full masha complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_mickey_complete_1772226091838.png`, alt: 'mascot full mickey complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_mickey_minnie_white_1772224484868.png`, alt: 'mascot full mickey minnie white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_rocky_complete_1772226121720.png`, alt: 'mascot full rocky complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_rubble_white_1772224471361.png`, alt: 'mascot full rubble white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_skye_complete_1772226367099.png`, alt: 'mascot full skye complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_sonic_white_1772224406477.png`, alt: 'mascot full sonic white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_spiderman_head_complete_1772226264996.png`, alt: 'mascot full spiderman head complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_tom_white_1772224395592.png`, alt: 'mascot full tom white costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mascot_full_unicorn_complete_1772226353060.png`, alt: 'mascot full unicorn complete costume petreceri copii', category: 'personaje' },
    { url: `${CAT}/mickey_costume_edit_1772208351182.png`, alt: 'mickey costume edit costume petreceri copii', category: 'personaje' },

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
