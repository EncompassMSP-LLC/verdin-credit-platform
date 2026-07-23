export const siteConfig = {
  name: 'Lending Readiness Partners',
  shortName: 'LRP',
  tagline: 'Helping More Borrowers Become Lending Ready.',
  subtitle: 'Premium Financial Technology',
  motto: 'Readiness is the strategy. Partnership is the advantage.',
  description:
    'Premium financial technology helping borrowers become lending ready while partnering with mortgage lenders, banks, credit unions, Realtors, and financial professionals.',
  url: process.env.NEXT_PUBLIC_SITE_URL ?? 'https://lendingreadinesspartners.com',
  portalUrl: process.env.NEXT_PUBLIC_PORTAL_URL ?? '/portal/login',
  email: 'briefings@lendingreadinesspartners.com',
  phone: '+1 (800) 555-0179',
  address: {
    line1: '1200 Harbor Avenue, Suite 400',
    city: 'Charlotte',
    state: 'NC',
    postal: '28202',
    country: 'United States',
  },
  social: {
    linkedin: 'https://www.linkedin.com/company/lending-readiness-partners',
  },
} as const;

export type NavItem = {
  href: string;
  label: string;
  description?: string;
};

export const primaryNav: NavItem[] = [
  { href: '/about', label: 'About' },
  { href: '/borrowers', label: 'Borrowers' },
  { href: '/lenders', label: 'Lenders' },
  { href: '/realtors', label: 'Realtors' },
  { href: '/partners', label: 'Partners' },
  { href: '/services', label: 'Services' },
  { href: '/technology', label: 'Technology' },
  { href: '/pricing', label: 'Pricing' },
  { href: '/resources', label: 'Resources' },
];

export const secondaryNav: NavItem[] = [
  { href: '/blog', label: 'Blog' },
  { href: '/faqs', label: 'FAQs' },
  { href: '/contact', label: 'Contact' },
];

export const footerNav = {
  platform: [
    { href: '/technology', label: 'Technology' },
    { href: '/services', label: 'Services' },
    { href: '/pricing', label: 'Pricing' },
    { href: '/portal/login', label: 'Portal login' },
  ],
  audiences: [
    { href: '/lenders', label: 'For lenders' },
    { href: '/partners', label: 'For operators' },
    { href: '/realtors', label: 'For realtors' },
    { href: '/borrowers', label: 'For borrowers' },
  ],
  company: [
    { href: '/about', label: 'About' },
    { href: '/resources', label: 'Resources' },
    { href: '/blog', label: 'Blog' },
    { href: '/faqs', label: 'FAQs' },
    { href: '/contact', label: 'Contact' },
  ],
} as const;
