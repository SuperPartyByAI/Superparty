# Technical Stability Checklist

## Daily Technical Checks — All 3 Brands

### A. HTTP Status (all must be 200)
```
python scripts/daily_monitor.py
```

| URL | Expected | Actual | OK? |
|-----|----------|--------|-----|
| superparty.ro/ | 200 | | |
| superparty.ro/animatori-petreceri-copii/ | 200 | | |
| superparty.ro/sitemap.xml | 200 | | |
| animatopia.ro/ | 200 | | |
| animatopia.ro/mascote-si-personaje/ | 200 | | |
| animatopia.ro/petreceri-tematice/ | 200 | | |
| animatopia.ro/petreceri-acasa/ | 200 | | |
| animatopia.ro/sitemap.xml | 200 | | |
| wowparty.ro/ | 200 | | |
| wowparty.ro/servicii/ | 200 | | |
| wowparty.ro/pachete/ | 200 | | |
| wowparty.ro/faq/ | 200 | | |
| wowparty.ro/despre-noi/ | 200 | | |
| wowparty.ro/contact/ | 200 | | |
| wowparty.ro/sitemap.xml | 200 | | |

### B. Robots Tags
- [ ] SP owner page: `index, follow`
- [ ] AN pages: `index, follow`
- [ ] WP pages: `index, follow`

### C. Canonical Tags
- [ ] All canonical tags present and pointing to correct self-referencing URLs
- [ ] No canonical pointing to a different domain
- [ ] No missing canonical tags

### D. Sitemaps
- [ ] SP: sitemap.xml contains 13 URLs, valid XML
- [ ] AN: sitemap.xml loads, valid XML
- [ ] WP: sitemap.xml contains 6 URLs, valid XML

### E. Deploy Status
- [ ] SP: Vercel deployment healthy
- [ ] AN: Vercel deployment healthy
- [ ] WP: Vercel deployment healthy
- [ ] No blocked deployments

### F. No Regressions
- [ ] No accidental 307/301 redirects on monitored pages
- [ ] No new `noindex` on pages that should be indexed
- [ ] No canonical changes
- [ ] No title/H1 changes on protected pages
