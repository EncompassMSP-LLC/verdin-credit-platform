export type PricingTier = {
  id: string;
  name: string;
  price: string;
  cadence: string;
  description: string;
  highlighted?: boolean;
  features: string[];
  cta: { label: string; href: string };
};

export const pricingTiers: PricingTier[] = [
  {
    id: 'operator',
    name: 'Operator',
    price: '$2,400',
    cadence: 'per month, billed annually',
    description:
      'For credit services firms productizing mortgage readiness for lender and realtor partners.',
    features: [
      'Operator workbench for case and readiness workflows',
      'Partner status timelines and next-best actions',
      'Readiness summary exports for lender review',
      'Role-based access and audit event history',
      'Partner kit templates for realtor enablement',
      'Standard implementation playbook and training',
    ],
    cta: { label: 'Talk with partnerships', href: '/contact?intent=operator' },
  },
  {
    id: 'lender',
    name: 'Lender',
    price: '$4,800',
    cadence: 'per month, billed annually',
    description:
      'For mid-market lenders reducing credit-related fallout while protecting underwriting integrity.',
    highlighted: true,
    features: [
      'Everything in Operator, plus lender workspace',
      'Near-miss pipeline views across partner channels',
      'Explainable readiness signals for credit and ops',
      'Compliance review pack and trust overview',
      'Dedicated success manager for pilot and rollout',
      'SSO-ready enterprise authentication options',
    ],
    cta: { label: 'Book a lender briefing', href: '/contact?intent=lender' },
  },
  {
    id: 'network',
    name: 'Network',
    price: 'Custom',
    cadence: 'annual platform agreement',
    description:
      'For multi-branch lenders, credit unions, and regional partner networks that need governed scale.',
    features: [
      'Multi-org partner network controls',
      'Custom readiness stage definitions',
      'Advanced reporting and export governance',
      'Security questionnaire and vendor due diligence support',
      'Priority roadmap collaboration',
      'Volume-based commercial terms',
    ],
    cta: { label: 'Request enterprise pricing', href: '/contact?intent=network' },
  },
];
