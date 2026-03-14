# Site #4 — Page Registry (DRAFT)

> ⚠️ **DOCUMENT ONLY — No pages built until GO is approved.**

## Planned Page Structure

| Route | Purpose | Keyword Target | Priority |
|-------|---------|---------------|----------|
| `/` | Homepage | [TBD brand term] | Critical |
| `/servicii/` | Services overview | [TBD service term] | High |
| `/pachete/` or `/oferte/` | Pricing/packages | [TBD pricing term] | High |
| `/[primary-intent]/` | Money page (owner) | [TBD primary cluster] | Critical |
| `/contact/` | Contact/booking | [TBD] | Medium |
| `/faq/` | FAQ | [TBD] | Medium |
| `/despre-noi/` | About | [TBD] | Low |

## Differentiation Requirements per Page

### Homepage
- [ ] Unique H1 (not used by SP/AN/WP)
- [ ] Unique meta description
- [ ] Unique value proposition
- [ ] Different CTA style
- [ ] Different visual design

### Money Page
- [ ] Targets a cluster NOT owned by SP/AN/WP
- [ ] Unique title format
- [ ] Unique FAQ (60%+ different)
- [ ] Own pricing structure (not copy of SP/AN/WP)
- [ ] `index, follow` + correct canonical

### All Pages
- [ ] robots = `index, follow` on important pages
- [ ] Self-referencing canonical
- [ ] In sitemap.xml
- [ ] Unique content per uniqueness policy thresholds

## Technical Requirements
- Astro framework (consistent with portfolio)
- Vercel deployment
- GSC property added + verified
- Sitemap generated and submitted
- Git author = project owner (Hobby plan compatibility)
