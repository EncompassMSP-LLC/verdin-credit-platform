'use client';

import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';

type FormState = {
  partnerOrg: string;
  loName: string;
  loEmail: string;
  loPhone: string;
  borrowerName: string;
  borrowerEmail: string;
  borrowerPhone: string;
  intent: string;
  gaps: string;
  notes: string;
  consent: boolean;
};

const initial: FormState = {
  partnerOrg: '',
  loName: '',
  loEmail: '',
  loPhone: '',
  borrowerName: '',
  borrowerEmail: '',
  borrowerPhone: '',
  intent: '',
  gaps: '',
  notes: '',
  consent: false,
};

export default function ReferralFormPage() {
  const router = useRouter();
  const [form, setForm] = useState<FormState>(initial);
  const [error, setError] = useState<string | null>(null);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    if (
      !form.partnerOrg.trim() ||
      !form.loName.trim() ||
      !form.loEmail.trim() ||
      !form.borrowerName.trim()
    ) {
      setError('Please complete all required fields.');
      return;
    }
    if (!form.consent) {
      setError('Borrower consent attestation is required before submitting a referral.');
      return;
    }

    const params = new URLSearchParams({
      intent: 'lender',
      resource: 'referral',
      partner: form.partnerOrg.trim(),
      lo: form.loName.trim(),
      email: form.loEmail.trim(),
      borrower: form.borrowerName.trim(),
      message: [
        `Partner: ${form.partnerOrg}`,
        `LO: ${form.loName} <${form.loEmail}> ${form.loPhone}`,
        `Borrower: ${form.borrowerName}`,
        form.borrowerEmail ? `Borrower email: ${form.borrowerEmail}` : null,
        form.borrowerPhone ? `Borrower phone: ${form.borrowerPhone}` : null,
        form.intent ? `Intent: ${form.intent}` : null,
        form.gaps ? `Known gaps: ${form.gaps}` : null,
        form.notes ? `Notes: ${form.notes}` : null,
        'Consent: partner attested borrower consented to referral contact.',
      ]
        .filter(Boolean)
        .join('\n'),
    });
    router.push(`/contact?${params.toString()}`);
  }

  const fieldClass =
    'mt-1 w-full rounded-md border border-navy-900/15 bg-white px-3 py-2 text-sm text-navy-900';

  return (
    <>
      <PageHero
        eyebrow="Referral form"
        title="Mortgage partner referral"
        description="Submit a referral request for follow-up. This is not an underwriting decision."
        tone="sand"
        actions={
          <Button type="button" variant="secondary" onClick={() => window.print()}>
            Print form
          </Button>
        }
      />

      <Section tone="white">
        <p className="mb-6 text-sm text-ink-700 print:mb-4">{ADVISORY_DISCLAIMER_SHORT}</p>
        {error ? (
          <p className="mb-4 rounded-md border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical print:hidden">
            {error}
          </p>
        ) : null}

        <form onSubmit={onSubmit} className="mx-auto max-w-2xl space-y-5 print:max-w-none">
          <fieldset className="space-y-4 rounded-lg border border-navy-900/10 p-5">
            <legend className="px-1 text-sm font-semibold text-navy-900">Partner / LO</legend>
            <label className="block text-sm">
              Partner / branch name *
              <input
                className={fieldClass}
                value={form.partnerOrg}
                onChange={(e) => update('partnerOrg', e.target.value)}
                required
              />
            </label>
            <label className="block text-sm">
              Loan officer name *
              <input
                className={fieldClass}
                value={form.loName}
                onChange={(e) => update('loName', e.target.value)}
                required
              />
            </label>
            <label className="block text-sm">
              LO email *
              <input
                type="email"
                className={fieldClass}
                value={form.loEmail}
                onChange={(e) => update('loEmail', e.target.value)}
                required
              />
            </label>
            <label className="block text-sm">
              LO phone
              <input
                className={fieldClass}
                value={form.loPhone}
                onChange={(e) => update('loPhone', e.target.value)}
              />
            </label>
          </fieldset>

          <fieldset className="space-y-4 rounded-lg border border-navy-900/10 p-5">
            <legend className="px-1 text-sm font-semibold text-navy-900">Borrower</legend>
            <label className="block text-sm">
              Borrower name *
              <input
                className={fieldClass}
                value={form.borrowerName}
                onChange={(e) => update('borrowerName', e.target.value)}
                required
              />
            </label>
            <label className="block text-sm">
              Borrower email
              <input
                type="email"
                className={fieldClass}
                value={form.borrowerEmail}
                onChange={(e) => update('borrowerEmail', e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Borrower phone
              <input
                className={fieldClass}
                value={form.borrowerPhone}
                onChange={(e) => update('borrowerPhone', e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Mortgage intent notes
              <textarea
                className={fieldClass}
                rows={2}
                value={form.intent}
                onChange={(e) => update('intent', e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Known credit / documentation gaps
              <textarea
                className={fieldClass}
                rows={3}
                value={form.gaps}
                onChange={(e) => update('gaps', e.target.value)}
              />
            </label>
            <label className="block text-sm">
              Internal notes
              <textarea
                className={fieldClass}
                rows={2}
                value={form.notes}
                onChange={(e) => update('notes', e.target.value)}
              />
            </label>
          </fieldset>

          <label className="flex items-start gap-3 text-sm text-ink-700">
            <input
              type="checkbox"
              className="mt-1"
              checked={form.consent}
              onChange={(e) => update('consent', e.target.checked)}
            />
            <span>
              I attest the borrower consented to be contacted by Lending Readiness Partners
              regarding this referral. *
            </span>
          </label>

          <div className="flex flex-wrap gap-3 print:hidden">
            <Button type="submit" variant="primary">
              Submit referral request
            </Button>
            <Button type="button" variant="secondary" onClick={() => window.print()}>
              Print
            </Button>
          </div>
        </form>
      </Section>
    </>
  );
}
