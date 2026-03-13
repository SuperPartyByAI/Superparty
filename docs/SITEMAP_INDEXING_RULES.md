# SITEMAP & INDEXING RULES (FAIL-CLOSED)

## 1. Indexable Pages (`robots="index, follow"`)
A page is allowed to be indexable ONLY if it passes the following criteria:
1. Valid HTTP 200 explicitly rendered.
2. Canonical URL explicitly points to itself.
3. Passes the `uniqueness_validator` (content similarity under `< 55%` compared to others).
4. Is NOT marked as `offline-generation-draft` or `placeholder`.
5. Has at least 300 words of unique body text (excluding header/footer).
6. Required schema (if applicable) is strictly valid.

## 2. Noindex Pages (`robots="noindex, follow"`)
Pages fall into this category if:
1. They are auto-generated location pages (e.g., `animatori-copii-bragadiru`) lacking local reviews or custom local descriptions.
2. They are paginated archive pages (Page 2, 3...) where we don't want canonical confusion.
3. They share > 60% of text with a stronger parent page.

## 3. Sitemap Exclusion
Any page marked as `noindex` MUST be programmatically excluded from `sitemap.xml`.
- **Astro Config:** Ensure `@astrojs/sitemap` utilizes the `filter` function to drop any route matching blocked schemas or containing a designated `draft` flag in frontmatter.
- **Python Generators:** Scripts like `generate_hub_pages.py` must NOT output URLs to custom `.txt` sitemaps if `allow_index=False`.
