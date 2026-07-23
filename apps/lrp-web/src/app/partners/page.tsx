import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'For Partners & Operators',
  description:
    'Productize mortgage readiness for lender and realtor channels with Lending Readiness Partners operator workflows.',
  path: '/partners',
});

export default function PartnersPage() {
  return (
    <>
      <PageHero
        eyebrow="For operators & partners"
        title="Productize mortgage readiness—without the chaos."
        description="Connect case work to partner-ready signals. Show lenders and realtors progress they can understand. Turn operational depth into a durable channel offering."
        actions={
          <>
            <Button href="/crm/login" variant="inverse" size="lg">
              Open enterprise CRM
            </Button>
            <Button
              href="/contact?intent=operator"
              variant="ghost"
              size="lg"
              className="text-white hover:bg-white/10"
            >
              Start an operator conversation
            </Button>
          </>
        }
      />

      <Section tone="white">
        <SectionHeading
          eyebrow="Operator outcomes"
          title="Make “mortgage ready” an operating product—not a spreadsheet."
        />
        <div className="mt-10 grid gap-6 md:grid-cols-2">
          {[
            {
              title: 'Workbench depth',
              body: 'Run credit and case workflows with ownership, status consistency, and readiness packaging designed for external partners.',
            },
            {
              title: 'Partner clarity',
              body: 'Replace ad-hoc status chasing with timelines and next actions lenders and realtors can trust.',
            },
            {
              title: 'Channel packaging',
              body: 'Use Partner Kits and stage glossaries to standardize BD conversations across your markets.',
            },
            {
              title: 'Compliance-minded process',
              body: 'Keep high-risk actions mediated and auditable so growth doesn’t outrun governance.',
            },
          ].map((item) => (
            <article key={item.title} className="rounded-lg bg-sand-100 p-6 ring-1 ring-navy-900/5">
              <h3 className="font-display text-xl text-navy-900">{item.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-700">{item.body}</p>
            </article>
          ))}
        </div>
      </Section>

      <Section>
        <SectionHeading
          title="Ideal partner profile"
          description="High-volume or multi-location credit services firms serving mortgage-intent borrowers, with case managers, reviewers, and a compliance lead who will not accept guarantee culture."
        />
        <ul className="mt-8 space-y-3 text-ink-700">
          {[
            'Realtor-fed or lender-fed pipeline looking for clearer ready-vs-not signals',
            'Need to reduce manual status reporting across cases',
            'Ambition to become the preferred readiness partner for local lenders',
            'Willingness to run staff-mediated workflows with audit discipline',
          ].map((item) => (
            <li key={item} className="flex gap-3">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-600" aria-hidden />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </Section>

      <CtaBand
        title="Become the readiness partner lenders prefer."
        description="We’ll help you package operations into partner-ready signals and a pilot your compliance team can defend."
        primaryHref="/contact?intent=operator"
        primaryLabel="Talk with partnerships"
      />
    </>
  );
}
