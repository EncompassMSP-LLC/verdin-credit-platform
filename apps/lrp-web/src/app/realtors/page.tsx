import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'For Realtors',
  description:
    'Protect closings with plain-language lending readiness stages and preferred-partner programs from Lending Readiness Partners.',
  path: '/realtors',
});

export default function RealtorsPage() {
  return (
    <>
      <PageHero
        eyebrow="For realtors"
        title="Fewer credit surprises. Stronger closings."
        description="Know when a buyer is timeline-viable—and communicate next steps without overpromising. Preferred-partner programs your agents can trust and your clients can understand."
        actions={
          <Button href="/contact?intent=realtor" variant="inverse" size="lg">
            Explore partner programs
          </Button>
        }
      />

      <Section tone="white">
        <SectionHeading
          eyebrow="Why agents adopt LRP ecosystems"
          title="Honest stages beat vague credit updates."
        />
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            {
              title: 'Timeline clarity',
              body: 'Replace “we’re disputing” with shared readiness stages that set contract expectations ethically.',
            },
            {
              title: 'Client trust',
              body: 'Keep dignity at the center. No shame narratives. No miracle claims agents have to unsell later.',
            },
            {
              title: 'Saved transactions',
              body: 'Stay attached through longer readiness arcs with professional updates instead of radio silence.',
            },
          ].map((item) => (
            <article key={item.title} className="rounded-lg bg-sand-100 p-6">
              <h3 className="font-display text-xl text-navy-900">{item.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-700">{item.body}</p>
            </article>
          ))}
        </div>
      </Section>

      <Section>
        <SectionHeading
          title="How realtor partnerships work"
          description="Realtors typically adopt Lending Readiness Partners through preferred lenders and credit operators—not as a DIY credit tool."
        />
        <ol className="mt-10 space-y-4">
          {[
            'Introduce your preferred lender or credit operator to an LRP briefing.',
            'Align on readiness stage language and weekly update cadence.',
            'Equip agents with expectation-setting scripts from the Partner Kit.',
            'Track saved-deal stories ethically—never at a borrower’s expense.',
          ].map((step, index) => (
            <li key={step} className="flex gap-4 rounded-lg bg-white p-5 ring-1 ring-navy-900/8">
              <span className="font-mono text-sm font-semibold text-teal-700">0{index + 1}</span>
              <p className="text-sm text-ink-700 sm:text-base">{step}</p>
            </li>
          ))}
        </ol>
      </Section>

      <CtaBand
        title="Give your team a partner standard they can defend."
        description="We’ll help you connect with operators and lenders who run readiness with institutional discipline."
        primaryHref="/contact?intent=realtor"
        primaryLabel="Talk with partnerships"
      />
    </>
  );
}
