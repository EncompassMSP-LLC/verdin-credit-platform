import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'For Realtors — Keep Buyers Engaged',
  description:
    'Help buyers stay in the conversation while they become lending ready—with shared progress language from Lending Readiness Partners.',
  path: '/realtors',
});

export default function RealtorsPage() {
  return (
    <>
      <PageHero
        eyebrow="Realtor partnership"
        title="Help buyers stay in the conversation while they become lending ready."
        description="Reduce silent financing stalls. Share honest readiness stages, stay updated on progress, and protect trust—without overpromising closings."
        actions={
          <>
            <Button href="/contact?intent=realtor" variant="inverse" size="lg">
              Explore partner programs
            </Button>
            <Button
              href="/resources/partner-kit"
              variant="ghost"
              size="lg"
              className="text-white hover:bg-white/10"
            >
              Realtor kit materials
            </Button>
          </>
        }
      />

      <Section tone="white">
        <SectionHeading
          eyebrow="Why agents partner with LRP ecosystems"
          title="Honest stages beat vague credit updates."
          description={ADVISORY_DISCLAIMER_SHORT}
        />
        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[
            {
              title: 'Keep buyers engaged',
              body: 'When credit work is needed, give buyers a plan and a partner—not radio silence.',
            },
            {
              title: 'Reduce lost momentum',
              body: 'Stay attached through longer readiness arcs with professional updates agents can explain.',
            },
            {
              title: 'Shared progress language',
              body: 'Replace “we’re disputing” with readiness stages that set contract expectations ethically.',
            },
            {
              title: 'Educational resources',
              body: 'Share claim-safe materials from the Partner Kit with clients and preferred lenders.',
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
            'Track progress stories ethically—never at a borrower’s expense.',
          ].map((step, index) => (
            <li key={step} className="flex gap-4 rounded-lg bg-white p-5 ring-1 ring-navy-900/8">
              <span className="font-mono text-sm font-semibold text-gold-700">
                {String(index + 1).padStart(2, '0')}
              </span>
              <p className="text-sm text-ink-700 sm:text-base">{step}</p>
            </li>
          ))}
        </ol>
        <div className="mt-8">
          <Button href="/lenders" variant="secondary">
            See the lender partnership page
          </Button>
        </div>
      </Section>

      <Section tone="white">
        <div className="rounded-lg border border-gold-500/30 bg-gold-500/5 p-6">
          <h2 className="font-display text-2xl text-navy-900">Closing outcomes</h2>
          <p className="mt-3 text-sm leading-relaxed text-ink-700 sm:text-base">
            {ADVISORY_DISCLAIMER_SHORT} Closing outcomes depend on lender underwriting and contract
            terms. We help organize readiness—never guarantee a sale.
          </p>
        </div>
      </Section>

      <CtaBand
        title="Give your team a partner standard they can defend."
        description="Connect with operators and lenders who run readiness with institutional discipline."
        primaryHref="/contact?intent=realtor"
        primaryLabel="Talk with partnerships"
        secondaryHref="/resources/partner-kit"
        secondaryLabel="Open partner kit"
      />
    </>
  );
}
