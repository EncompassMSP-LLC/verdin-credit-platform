import Link from 'next/link';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_LONG, ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { createMetadata } from '@/lib/seo';
import { siteConfig } from '@/lib/site';

export const metadata = createMetadata({
  title: 'Mortgage Partnership Guide',
  description:
    'Lending Readiness Partners Mortgage Partnership Guide — institutional narrative for lender meetings.',
  path: '/resources/partner-kit/guide',
});

const chapters = [
  {
    title: 'Cover',
    body: 'Mortgage Partnership Guide · Helping More Borrowers Become Lending Ready.',
  },
  {
    title: 'Letter from partnerships',
    body: 'We extend your team for advisory readiness support—not underwriting. Invite a briefing.',
  },
  {
    title: 'Who we are',
    body: 'Mortgage Readiness Solutions for lenders, LOs, operators, and realtors—unlike guarantee-culture mills.',
  },
  {
    title: 'The problem',
    body: 'Near-miss borrowers stall when status is tribal and “not yet” has no plan.',
  },
  {
    title: 'Partnership model',
    body: 'Referral → plan → updates → advisory Lending Ready signal → return to the loan officer.',
  },
  {
    title: 'What partners see',
    body: 'Pipeline, referral status, digests, and borrower portal progress—scoped and auditable.',
  },
  {
    title: 'Borrower experience',
    body: 'Clarity, education, tasks, and staff-mediated dispute support with dignity-first language.',
  },
  {
    title: 'Lending Readiness Score™',
    body: ADVISORY_DISCLAIMER_SHORT,
  },
  {
    title: 'Compliance posture',
    body: 'Staff-mediated high-risk actions, claim library, no unsupervised bureau filing, audit trails.',
  },
  {
    title: 'LO benefits',
    body: 'Specialist, intake review, portal, progress reports, rescore prep support, flexible terms.',
  },
  {
    title: 'Production focus',
    body: 'Fallout visibility and relationship retention—directional metrics, not guaranteed pull-through.',
  },
  {
    title: 'Credit & underwriting stakeholders',
    body: 'Explainability and non-guarantee framing that respect overlays and judgment.',
  },
  {
    title: 'Realtor co-channel',
    body: 'Keep buyers engaged with shared readiness stages—no shame narratives.',
  },
  {
    title: 'Referral SLA',
    body: 'Accept/decline cadence, update rhythm, escalation path, PII minimization.',
  },
  {
    title: 'Security & data',
    body: 'Tenant isolation, portal auth, and document controls—see trust overview for diligence.',
  },
  {
    title: 'Onboarding',
    body: 'Kickoff → partnership record → LO seats → first referrals → digest cadence.',
  },
  {
    title: 'Process vignette',
    body: 'Anonymized process story only—never fabricated score before/after claims.',
  },
  {
    title: 'FAQ',
    body: 'Timeline varies; we support education for FHA/Conventional paths; lenders decide eligibility.',
  },
  {
    title: 'How to start',
    body: 'Contact partnerships, open the lender workspace, or request the designed PDF pack.',
  },
  {
    title: 'Contacts',
    body: `${siteConfig.email} · ${siteConfig.phone} · ${siteConfig.url}`,
  },
];

export default function PartnershipGuidePage() {
  return (
    <>
      <PageHero
        eyebrow="Partnership Guide"
        title="Mortgage Partnership Guide"
        description="Twenty-page manuscript for lender meetings. Export to designed PDF from the Build Bible Phase 2 kit."
        tone="sand"
        actions={
          <>
            <Button href="/contact?intent=lender&resource=partnership-guide" variant="primary">
              Request designed PDF
            </Button>
            <Button href="/resources/partner-kit/phase-2" variant="secondary">
              Phase 2 hub
            </Button>
          </>
        }
      />

      <Section tone="white" className="print:py-4">
        <p className="mb-8 max-w-3xl text-sm text-ink-700 print:mb-4">{ADVISORY_DISCLAIMER_LONG}</p>
        <ol className="space-y-8 print:space-y-6">
          {chapters.map((chapter, index) => (
            <li
              key={chapter.title}
              className="break-inside-avoid rounded-lg border border-navy-900/10 bg-sand-50 p-6 print:border-navy-900/20 print:bg-white"
            >
              <p className="font-mono text-xs font-semibold text-gold-700">
                Page {String(index + 1).padStart(2, '0')}
              </p>
              <h2 className="mt-2 font-display text-2xl text-navy-900">{chapter.title}</h2>
              <p className="mt-3 text-sm leading-relaxed text-ink-700">{chapter.body}</p>
            </li>
          ))}
        </ol>
        <p className="mt-10 text-sm print:hidden">
          <Link
            href="/resources/partner-kit/phase-2"
            className="font-medium text-teal-700 hover:underline"
          >
            ← Phase 2 hub
          </Link>
        </p>
      </Section>
    </>
  );
}
