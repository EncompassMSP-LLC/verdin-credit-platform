import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Container } from '@/components/ui/Container';
import { blogPosts, getPost } from '@/content/blog';
import { createMetadata } from '@/lib/seo';
import { siteConfig } from '@/lib/site';

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return blogPosts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const post = getPost(slug);
  if (!post) return {};
  return createMetadata({
    title: post.title,
    description: post.description,
    path: `/blog/${post.slug}`,
  });
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;
  const post = getPost(slug);
  if (!post) notFound();

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    datePublished: post.date,
    description: post.description,
    author: { '@type': 'Organization', name: siteConfig.name },
    publisher: { '@type': 'Organization', name: siteConfig.name },
  };

  return (
    <article>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <header className="border-b border-navy-900/8 bg-sand-100">
        <Container className="py-14 sm:py-16">
          <p className="text-sm">
            <Link href="/blog" className="font-medium text-teal-700 hover:underline">
              ← Blog
            </Link>
          </p>
          <p className="eyebrow mt-6">{post.category}</p>
          <h1 className="mt-3 max-w-3xl font-display text-4xl font-medium tracking-tight text-navy-900 sm:text-5xl">
            {post.title}
          </h1>
          <p className="mt-5 max-w-2xl text-lg text-ink-700">{post.description}</p>
          <div className="mt-6 flex flex-wrap gap-4 text-sm text-slate-500">
            <span>{post.author}</span>
            <time dateTime={post.date}>
              {new Date(post.date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </time>
            <span>{post.readingMinutes} min read</span>
          </div>
        </Container>
      </header>
      <Container className="py-12 sm:py-16">
        <div className="prose-lrp mx-auto max-w-prose">
          {post.content.map((paragraph) => (
            <p key={paragraph.slice(0, 32)}>{paragraph}</p>
          ))}
        </div>
        <div className="mx-auto mt-12 max-w-prose border-t border-navy-900/10 pt-8">
          <p className="text-sm text-ink-700">
            Ready to apply these ideas in your channel?{' '}
            <Link href="/contact" className="font-medium text-teal-700 hover:underline">
              Book a readiness briefing
            </Link>
            .
          </p>
        </div>
      </Container>
    </article>
  );
}
