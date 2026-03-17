import { z, defineCollection } from 'astro:content';

const seoArticlesCollection = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        description: z.string(),
        pubDate: z.date().optional(),
        heroImage: z.string().optional(),
        keywords: z.string().optional(),
        indexStatus: z.enum(['ready', 'revise', 'hold']).optional(),
        canonical: z.string().optional(),
    }),
});

const blogCollection = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        description: z.string(),
        pubDate: z.date().optional(),
        updatedDate: z.date().optional(),
        heroImage: z.string().optional(),
        author: z.string().default('Echipa Superparty'),
        tags: z.array(z.string()).default([]),
    }),
});

export const collections = {
    'seo-articles': seoArticlesCollection,
    'blog': blogCollection,
};
