import { PageHero } from '@/components/sections/PageHero';
import { CtaBand } from '@/components/sections/CtaBand';
import { FaqAccordion } from '@/components/ui/FaqAccordion';
import { Section } from '@/components/ui/Section';
import { faqs } from '@/content/faqs';
import { createMetadata } from '@/lib/seo';
import { siteConfig } from '@/lib/site';

export const metadata = createMetadata({
  title: 'FAQs',
  description:
    'Frequently asked questions about Lending Readiness Partners, lending readiness, compliance controls, and pricing.',
  path: '/faqs',
});

export default function FaqsPage() {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer,
      },
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <PageHero
        eyebrow="FAQs"
        title="Answers for lenders, operators, and advisors."
        description={`Common questions about ${siteConfig.name}, how readiness works, and what we will—and will not—claim.`}
        tone="sand"
      />
      <Section tone="white">
        <FaqAccordion items={faqs} />
      </Section>
      <CtaBand
        title="Didn’t find your question?"
        description="Send it with your briefing request—we’ll address it with the right stakeholders on the call."
      />
    </>
  );
}
