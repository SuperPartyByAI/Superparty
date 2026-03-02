# Action Plan Prioritar (Site: superparty)

- Total analizat: 500
- Ready To Index: 21
- Doorways / Risc ridicat (>85% sim): 18
- Fara testimoniale alocate: 450

## Top Remedieri Imediate
1. **Frontmatter lipsa:** Update YAML pe fisiere adaugand locale, author, image URL si datePublished native.
2. **Canonical & NOINDEX:** Cele ~300 fisiere raportate ca `high risk` in superparty_top_risk.csv trebuie puse noindex.
3. **JSON-LD Schema Integration:** Injecteaza datele generate in `[slug].astro` in tag-ul <head>.
4. **Testimoniale:** Populeaza `src/data/superparty_testimonials.json` pentru slugurile listate in `superparty_testimonials_missing.csv`.

