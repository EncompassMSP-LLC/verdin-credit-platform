'use client';

import { useSearchParams } from 'next/navigation';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';

export default function ReferralThanksPage() {
  const params = useSearchParams();
  const intakeId = params.get('intake_id');
  const status = params.get('status');
  const message =
    params.get('message') ||
    'Referral received. Our team will follow up — this is not an underwriting decision.';

  return (
    <>
      <PageHero eyebrow="Referral received" title="Thank you" description={message} tone="sand" />
      <Section tone="white">
        <p className="mb-4 text-sm text-ink-700">{ADVISORY_DISCLAIMER_SHORT}</p>
        {intakeId ? (
          <p className="mb-2 text-sm text-slate-600">
            Reference: <span className="font-mono text-navy-900">{intakeId}</span>
          </p>
        ) : null}
        {status ? (
          <p className="mb-6 text-sm text-slate-600">
            Status: <span className="font-medium uppercase tracking-wide">{status}</span>
          </p>
        ) : null}
        <Button href="/resources/partner-kit" variant="secondary">
          Back to partner kit
        </Button>
      </Section>
    </>
  );
}
