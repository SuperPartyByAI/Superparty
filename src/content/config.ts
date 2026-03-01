import { z, defineCollection } from 'astro:content';

const blog = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        description: z.string(),
        category: z.string().optional(),
        date: z.string().optional(),
    }),
});

export const collections = { blog };
