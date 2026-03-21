// build: 2026-03-21T20:40
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import tailwind from '@astrojs/tailwind';
// Partytown removed — caused deprecated API warnings (SharedStorage, AttributionReporting)
// Sitemap temporarily disabled — @astrojs/sitemap@3.7.1 crashes on Vercel

// https://astro.build/config
export default defineConfig({
    site: 'https://www.superparty.ro',
    trailingSlash: 'ignore',
    integrations: [mdx({ extendMarkdown: false }), tailwind()],
    build: {
      inlineStylesheets: 'always'
    }
});