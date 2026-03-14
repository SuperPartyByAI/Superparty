import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import tailwind from '@astrojs/tailwind';
// Sitemap temporarily disabled — @astrojs/sitemap@3.7.1 crashes on Vercel
// with "Cannot read properties of undefined (reading 'reduce')"
// TODO: upgrade @astrojs/sitemap or fix after money page is live with index,follow

// https://astro.build/config
export default defineConfig({
    site: 'https://www.superparty.ro',
    trailingSlash: 'ignore',
    integrations: [mdx(), tailwind()],
});
