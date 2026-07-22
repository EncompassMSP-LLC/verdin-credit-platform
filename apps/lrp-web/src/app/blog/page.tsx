import Link from 'next/link';
import { PageHero } from '@/components/sections/PageHero';
import { Section } from '@/components/ui/Section';
import { blogPosts } from '@/content/blog';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Blog',
  description:
    'Insights on lending readiness, pipeline fallout, partner enablement, and compliance-minded operations.',
  path: '/blog',
});

export default function BlogPage() {
  const posts = [...blogPosts].sort((a, b) => b.date.localeCompare(a.date));

  return (
    <>
      <PageHero
        eyebrow="Blog"
        title="Insights for partners who take readiness seriously."
        description="Operational perspectives on near-miss fallout, mediated controls, and shared readiness language across lenders, operators, and realtors."
        tone="sand"
      />
      <Section tone="white">
        <ul className="grid gap-6 lg:grid-cols-2">
          {posts.map((post) => (
            <li key={post.slug}>
              <article className="flex h-full flex-col rounded-lg border border-navy-900/10 bg-sand-50 p-6">
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                  <span className="font-medium uppercase tracking-eyebrow text-teal-700">
                    {post.category}
                  </span>
                  <time dateTime={post.date}>
                    {new Date(post.date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </time>
                  <span>{post.readingMinutes} min read</span>
                </div>
                <h2 className="mt-3 font-display text-2xl text-navy-900">
                  <Link href={`/blog/${post.slug}`} className="hover:text-teal-700">
                    {post.title}
                  </Link>
                </h2>
                <p className="mt-3 flex-1 text-sm leading-relaxed text-ink-700">
                  {post.description}
                </p>
                <Link
                  href={`/blog/${post.slug}`}
                  className="mt-6 text-sm font-medium text-teal-700 hover:underline"
                >
                  Read article →
                </Link>
              </article>
            </li>
          ))}
        </ul>
      </Section>
    </>
  );
}
