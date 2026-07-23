import Link from 'next/link';
import { PageHero } from '@/components/sections/PageHero';
import { Section, SectionHeading } from '@/components/ui/Section';
import { resources } from '@/content/resources';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Resources',
  description:
    'Lender one-pagers, operator guides, realtor kits, trust overviews, and pilot playbooks from Lending Readiness Partners.',
  path: '/resources',
});

export default function ResourcesPage() {
  return (
    <>
      <PageHero
        eyebrow="Resources"
        title="Practical materials for serious partners."
        description="Briefing collateral, enablement kits, and trust documentation—written for production, operations, compliance, and channel leaders."
        tone="sand"
      />

      <Section tone="white">
        <SectionHeading
          title="Request curated resources"
          description="Select a resource to prefill a briefing request. Our team will send the latest version and answer fit questions."
        />
        <div className="mt-10 grid gap-6 md:grid-cols-2">
          {resources.map((resource) => (
            <article
              key={resource.title}
              className="flex h-full flex-col rounded-lg border border-navy-900/10 bg-sand-50 p-6"
            >
              <p className="text-xs font-medium uppercase tracking-eyebrow text-teal-700">
                {resource.audience}
              </p>
              <h2 className="mt-3 font-display text-2xl text-navy-900">{resource.title}</h2>
              <p className="mt-3 flex-1 text-sm leading-relaxed text-ink-700">
                {resource.description}
              </p>
              <Link
                href={resource.href}
                className="mt-6 text-sm font-medium text-teal-700 hover:underline"
              >
                Request this resource →
              </Link>
            </article>
          ))}
        </div>
      </Section>
    </>
  );
}
