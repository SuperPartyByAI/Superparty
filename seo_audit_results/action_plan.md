# Action Plan Prioritar

- Total analizat: 500
- Ready To Index: 0
- Doorways / Risc ridicat (>85% sim): 377

## Top Remedieri Imediate
1. **Frontmatter lipsa:** Update YAML pe fisiere adaugand locale, author, image URL si datePublished native.
2. **Canonical & NOINDEX:** Cele ~300 fisiere raportate ca `high risk` in top_risk.csv trebuie puse noindex pana cand echipa modifica contentul pentru a-i reduce similaritatea TF-IDF sub 70%.
3. **JSON-LD Schema Integration:** Injecteaza datele generate in `[slug].astro` in tag-ul <head>.

## 10) Cod Snippet Implementare Astro
```javascript
export async function getStaticPaths() {
  const modules = import.meta.glob('../../content/seo-articles/*.mdx', { eager: true });
  return Object.keys(modules).map(path => {
    const slug = path.split('/').pop().replace('.mdx','');
    return { params: { slug } };
  });
}
```
