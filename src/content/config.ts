import { z, defineCollection } from 'astro:content';

const seoArticlesCollection = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        description: z.string(),
        pubDate: z.date().optional(),
        heroImage: z.string().optional(),
        keywords: z.string().optional(),
    }),
});

export const collections = {
    'seo-articles': seoArticlesCollection,
};
