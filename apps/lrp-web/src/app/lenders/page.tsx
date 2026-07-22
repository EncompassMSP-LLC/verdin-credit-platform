import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'For Lenders',
  description:
    'Reduce credit-related fallout and fund more near-miss borrowers with evidenced lending readiness from Lending Readiness Partners.',
  path: '/lenders',
});

export default function LendersPage() {
  return (
    <>
      <PageHero
        eyebrow="For lenders"
        title="Reduce credit fallout. Protect underwriting integrity."
        description="Give production teams visibility into borrower readiness—and give credit risk the explainability it requires. Fund more of the borrowers you already want, without approval theater."
        actions={
          <>
            <Button href="/contact?intent=lender" variant="inverse" size="lg">
              Schedule a lender briefing
            </Button>
            <Button href="/lender/login" variant="secondary" size="lg">
              Open lender workspace
            </Button>
            <Button
              href="/pricing"
              variant="ghost"
              size="lg"
              className="text-white hover:bg-white/10"
            >
              View lender packaging
            </Button>
          </>
        }
      />

      <Section tone="white">
        <SectionHeading
          eyebrow="Business outcomes"
          title="Pull-through improves when readiness is operational."
          description="Near-miss files stall when status is tribal knowledge. LRP gives your ecosystem a controlled rhythm for diagnosis, remediation, and partner handoff."
        />
        <ul className="mt-10 grid gap-4 sm:grid-cols-2">
          {[
            'Pipeline views for near-miss and in-remediation files',
            'Readiness summaries suitable for partner and credit review',
            'Controls designed for mediated, auditable operations',
            'Shared definitions that reduce status chaos across channels',
            'Pilot framing tied to fallout and cycle-time metrics',
            'Trust collateral ready for compliance and vendor management',
          ].map((item) => (
            <li
              key={item}
              className="flex gap-3 rounded-lg bg-sand-100 px-4 py-4 text-sm text-ink-700"
            >
              <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-teal-600" aria-hidden />
              {item}
            </li>
          ))}
        </ul>
      </Section>

      <Section>
        <SectionHeading eyebrow="Stakeholders" title="Built for the full buying committee." />
        <div className="mt-10 grid gap-6 lg:grid-cols-3">
          {[
            {
              title: 'Production',
              body: 'Rescue near-miss borrowers before they churn. Give LOs a credible readiness story rooted in evidenced progress.',
            },
            {
              title: 'Underwriting & credit',
              body: 'Explainable signals, audit trails, and explicit non-guarantee framing that respect overlays and judgment.',
            },
            {
              title: 'Compliance & risk',
              body: 'Mediated high-risk actions, claim guardrails, and vendor due diligence materials that survive scrutiny.',
            },
          ].map((item) => (
            <article key={item.title} className="rounded-lg bg-white p-6 ring-1 ring-navy-900/8">
              <h3 className="font-display text-xl text-navy-900">{item.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-700">{item.body}</p>
            </article>
          ))}
        </div>
      </Section>

      <Section tone="white">
        <div className="rounded-lg border border-warning/30 bg-warning/5 p-6">
          <h2 className="font-display text-2xl text-navy-900">Important disclaimer</h2>
          <p className="mt-3 text-sm leading-relaxed text-ink-700 sm:text-base">
            Lending Readiness Partners does not guarantee loan approval or funding decisions. Lender
            underwriting and applicable guidelines always govern. We help make readiness visible and
            actionable—never a substitute for credit policy.
          </p>
        </div>
      </Section>

      <CtaBand
        title="Run a 60-day near-miss pilot."
        description="Define segments, stages, and success metrics with production, ops, and compliance in the room."
        primaryHref="/contact?intent=lender"
        primaryLabel="Book a lender briefing"
      />
    </>
  );
}
