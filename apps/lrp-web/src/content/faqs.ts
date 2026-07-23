import type { FaqItem } from '@/components/ui/FaqAccordion';

export const faqs: FaqItem[] = [
  {
    question: 'What is lending readiness?',
    answer:
      'Lending readiness is the operational state in which a borrower’s credit posture, documentation quality, and partner workflows are clear enough for a lender to evaluate funding eligibility with confidence. It is a system outcome—not a single bureau score or a guarantee of approval.',
  },
  {
    question: 'Does Lending Readiness Partners guarantee loan approval?',
    answer:
      'No. We never guarantee approval or funding. Lender underwriting, overlays, and applicable guidelines always govern. Our role is to make readiness visible, auditable, and actionable so qualified borrowers can move forward with fewer surprises.',
  },
  {
    question: 'Who is the platform built for?',
    answer:
      'Primary buyers are mid-market mortgage lenders and credit services operators. Realtors participate through preferred-partner programs. Borrowers are supported through advisors—not through aggressive direct-to-consumer credit hype.',
  },
  {
    question: 'How do you handle compliance-sensitive credit actions?',
    answer:
      'High-risk actions are designed to be staff-mediated with audit trails and role-based controls. We do not market unsupervised dispute filing or black-box automation that bypasses professional judgment.',
  },
  {
    question: 'Can LRP replace our LOS or underwriting stack?',
    answer:
      'No. Lending Readiness Partners complements your loan origination and credit decisioning stack by coordinating readiness workflows and partner signals. Underwriting judgment remains with the lender.',
  },
  {
    question: 'How does pricing work?',
    answer:
      'We offer Operator, Lender, and Network packages with annual platform fees and implementation support. Enterprise and multi-region deployments are scoped through a readiness briefing. See the Pricing page for package details.',
  },
  {
    question: 'What does an implementation typically include?',
    answer:
      'A typical pilot defines near-miss segments, readiness stages, partner handoffs, success metrics, and training for production, operations, and compliance stakeholders. Most design partners run a 60-day controlled pilot before broader rollout.',
  },
  {
    question: 'Is borrower data shared across tenants or sold?',
    answer:
      'No. We do not sell borrower data and we do not expose unrestricted cross-tenant PII. Any aggregate insight programs require explicit governance and consent boundaries.',
  },
  {
    question: 'How do realtors use Lending Readiness Partners?',
    answer:
      'Realtors typically adopt LRP through preferred lender and operator partnerships. They receive plain-language readiness stages and expectation-setting guidance—without being asked to sell credit-repair claims.',
  },
  {
    question: 'Where do I start?',
    answer:
      'Book a readiness briefing from the Contact page. Bring production, operations, and compliance stakeholders so we can scope a pilot against your fallout and cycle-time realities.',
  },
];
