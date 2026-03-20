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
        robots: z.string().optional(),
    }),
});

const ghidCollection = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        description: z.string(),
        pubDate: z.date().optional(),
        heroImage: z.string().optional(),
        coverImage: z.string().optional(),
        category: z.string().optional(),
        author: z.string().default('Echipa SuperParty'),
        readTime: z.string().optional(),
    }),
});

export const collections = {
    'seo-articles': seoArticlesCollection,
    'ghid': ghidCollection,
};
