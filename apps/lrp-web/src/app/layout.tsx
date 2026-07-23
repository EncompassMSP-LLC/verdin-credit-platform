import type { Metadata } from 'next';
import { Libre_Baskerville, Montserrat } from 'next/font/google';
import { SiteChrome } from '@/components/layout/SiteChrome';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { siteConfig } from '@/lib/site';
import { absoluteUrl } from '@/lib/utils';
import './globals.css';

const sans = Montserrat({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
  weight: ['400', '500', '600', '700'],
});

const display = Libre_Baskerville({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
  weight: ['400', '700'],
  style: ['normal', 'italic'],
});

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: `${siteConfig.name} | ${siteConfig.tagline.replace(/\.$/, '')}`,
    template: `%s | ${siteConfig.name}`,
  },
  description: siteConfig.description,
  applicationName: siteConfig.name,
  keywords: [
    'lending readiness',
    'mortgage readiness',
    'premium financial technology',
    'borrower portal',
    'lender partnerships',
  ],
  authors: [{ name: siteConfig.name }],
  creator: siteConfig.name,
  icons: {
    icon: [{ url: '/favicon.png', type: 'image/png' }],
    apple: [{ url: '/apple-touch-icon.png' }],
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: absoluteUrl('/'),
    siteName: siteConfig.name,
    title: siteConfig.name,
    description: siteConfig.description,
    images: [{ url: '/brand/logo-stacked.png', width: 1280, height: 1680, alt: siteConfig.name }],
  },
  twitter: {
    card: 'summary_large_image',
    title: siteConfig.name,
    description: siteConfig.description,
  },
  robots: {
    index: true,
    follow: true,
  },
};

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: siteConfig.name,
  url: siteConfig.url,
  description: siteConfig.description,
  email: siteConfig.email,
  telephone: siteConfig.phone,
  logo: absoluteUrl('/brand/logo-stacked.png'),
  address: {
    '@type': 'PostalAddress',
    streetAddress: siteConfig.address.line1,
    addressLocality: siteConfig.address.city,
    addressRegion: siteConfig.address.state,
    postalCode: siteConfig.address.postal,
    addressCountry: siteConfig.address.country,
  },
  sameAs: [siteConfig.social.linkedin],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable}`} suppressHydrationWarning>
      <body className="min-h-screen font-sans">
        <ThemeProvider>
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
          />
          <SiteChrome>{children}</SiteChrome>
        </ThemeProvider>
      </body>
    </html>
  );
}
