# Superparty SEO Query Ownership & Anti-Cannibalization Policy

**Document status:** Final
**Scope:** Protejarea paginilor Tier A (Pilon, Hub-uri) și Tier B (Sectoare, Localități Ilfov aprobate) împotriva canibalizării, definirea owner-ului clar pentru query-urile "money".

Acest document reprezintă **Sursa de Adevăr (Single Source of Truth)** pentru intenția locală și rutele sistemului automatizat Superparty SEO Agent. Orice experiment sau optimizare on-page trebuie să respecte acest ownership.

## 1. Query Ownership (Money Queries)

Fiecare cluster de căutare este asignat unui **singur URL owner**. Agentul SEO (worker-ul de `apply` și `plan`) nu are voie să optimizeze o pagină secundară pentru un query deținut de owner-ul principal.

### Tier A (Active Critice)

| Query Target (Money) | Owner URL (Path) | Observații / Guards |
| :--- | :--- | :--- |
| **"animatori petreceri copii" (general, București & Ilfov)** | `/animatori-petreceri-copii` (Pilon) | Nicio altă pagină nu are voie să targeteze "animatori petreceri copii" ca root focus. Este protejat de `PILLAR_LOCK` în caz de fluctuații. |
| **"animatori copii bucurești"**, "petreceri copii bucurești" | `/petreceri/bucuresti` (Hub București) | Acoperă strict căutările cu intenție de "București" general. |
| **"animatori copii ilfov"**, "petreceri copii ilfov" | `/petreceri/ilfov` (Hub Ilfov) | Acoperă strict căutările cu intenție de "Ilfov" general. |

### Tier B (Coverage Local)

| Query Target (Money) | Owner URL (Path) | Observații / Guards |
| :--- | :--- | :--- |
| **"animatori copii sector X"** (1-6) | `/petreceri/sector-X` | Focus doar pe sectorul vizat. Nu concurează cu Hub-ul București, îl susține prin link intern (Coverage). |
| **"animatori copii [Localitate]"** (ex: Voluntari, Bragadiru) | `/petreceri/[slug-localitate]` | Strict localitățile din `indexing_manifest.json` aprobate (Tier B). Nu concurează cu Hub-ul Ilfov. |

---

## 2. Anti-Cannibalization Guards

Sistemul implementează reguli stricte pentru a preveni canibalizarea:

1. **Deduplicarea prin Planner (`seo_plan_task`)**: 
   - Fiecare query din GSC este trecut prin funcția de `local_intent_score`.
   - Scorurile favorizează URL-urile owner (ex: dacă query-ul conține "sector 3", scorul va bate absolut orice altă pagină pentru a asigna acel query paginii `/petreceri/sector-3`).

2. **Cross-Linking Obligatoriu**:
   - Paginile Tier B (Sectoare, Localități) **trebuie** să includă în secțiunea de SEO text logistic un link către Hub-ul părinte (`/petreceri/bucuresti` sau `/petreceri/ilfov`).
   - Block-urile injectate de AI prin `apply` sunt respinse la Quality Gate dacă nu conțin link-ul către Pilon (`/animatori-petreceri-copii`) și Arie Acoperire.

3. **Interdicțiile de Root**:
   - Nicio pagină Tier B nu primește titlul "Animatori București". Doar "Animatori [Zona/Sector]".
   - Fallback-ul logistic este de tipul *"Ne deplasăm în [Sect/Loc] și zonele limitrofe"*, nu la nivel general de județ, pentru a păstra relevanța de nișă geografică.

## 3. Policy Execution (Agent Runtime)

Dacă un experiment CTR sau un Runbook (ex: `rank_drop`) detectează un drift, intervenția va asuma întotdeauna că:
* **Pilonul** trebuie susținut cu trafic (nu deviat către hub-uri nenecesare).
* **Hub-urile** captează traficul indecis ("zona Ilfov").
* **Tier B** captează long-tail strict.
