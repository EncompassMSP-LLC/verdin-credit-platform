import type { Metadata } from 'next';
import { absoluteUrl } from '@/lib/utils';
import { siteConfig } from '@/lib/site';

export function createMetadata({
  title,
  description,
  path = '/',
  noIndex = false,
}: {
  title?: string;
  description?: string;
  path?: string;
  noIndex?: boolean;
}): Metadata {
  const pageTitle = title
    ? `${title} | ${siteConfig.name}`
    : `${siteConfig.name} | ${siteConfig.tagline.replace(/\.$/, '')}`;
  const desc = description ?? siteConfig.description;
  const url = absoluteUrl(path);

  return {
    title: pageTitle,
    description: desc,
    alternates: { canonical: url },
    robots: noIndex ? { index: false, follow: false } : { index: true, follow: true },
    openGraph: {
      title: pageTitle,
      description: desc,
      url,
      siteName: siteConfig.name,
      locale: 'en_US',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: pageTitle,
      description: desc,
    },
  };
}
