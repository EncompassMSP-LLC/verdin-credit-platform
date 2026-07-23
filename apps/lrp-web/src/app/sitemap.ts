import type { MetadataRoute } from 'next';
import { blogPosts } from '@/content/blog';
import { siteConfig } from '@/lib/site';

const staticRoutes = [
  '/',
  '/about',
  '/borrowers',
  '/lenders',
  '/realtors',
  '/partners',
  '/services',
  '/technology',
  '/pricing',
  '/resources',
  '/blog',
  '/faqs',
  '/contact',
];

export default function sitemap(): MetadataRoute.Sitemap {
  const base = siteConfig.url.replace(/\/$/, '');
  const now = new Date();

  return [
    ...staticRoutes.map((route) => ({
      url: `${base}${route}`,
      lastModified: now,
      changeFrequency: route === '/' ? ('weekly' as const) : ('monthly' as const),
      priority: route === '/' ? 1 : 0.7,
    })),
    ...blogPosts.map((post) => ({
      url: `${base}/blog/${post.slug}`,
      lastModified: new Date(post.date),
      changeFrequency: 'monthly' as const,
      priority: 0.6,
    })),
  ];
}
