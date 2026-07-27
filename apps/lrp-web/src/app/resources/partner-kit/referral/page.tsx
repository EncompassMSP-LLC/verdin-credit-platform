'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  ApiClientError,
  configureApiClient,
  getReferralIntakeStatus,
  submitReferralIntake,
} from '@verdin/api-client';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { getApiBaseUrl } from '@/lib/platform/config';

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
  const searchParams = useSearchParams();
  const partnershipId = searchParams.get('partnership_id');

  const [form, setForm] = useState<FormState>(initial);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [intakeReady, setIntakeReady] = useState<boolean | null>(null);

  useEffect(() => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
    let cancelled = false;
    getReferralIntakeStatus()
      .then((status) => {
        if (!cancelled) setIntakeReady(status.referral_intake_enabled);
      })
      .catch(() => {
        if (!cancelled) setIntakeReady(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function onSubmit(event: FormEvent) {
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
    if (!form.borrowerEmail.trim() && !form.borrowerPhone.trim()) {
      setError('Borrower email or phone is required.');
      return;
    }
    if (!form.consent) {
      setError('Borrower consent attestation is required before submitting a referral.');
      return;
    }
    if (intakeReady === false) {
      setError('Referral intake is temporarily unavailable. Please try again later.');
      return;
    }

    setSubmitting(true);
    try {
      const result = await submitReferralIntake({
        partner_org_name: form.partnerOrg.trim(),
        lo_name: form.loName.trim(),
        lo_email: form.loEmail.trim(),
        lo_phone: form.loPhone.trim() || null,
        borrower_name: form.borrowerName.trim(),
        borrower_email: form.borrowerEmail.trim() || null,
        borrower_phone: form.borrowerPhone.trim() || null,
        product_intent: form.intent.trim() || null,
        known_gaps: form.gaps.trim() || null,
        notes: form.notes.trim() || null,
        consent_attested: true,
        partnership_id: partnershipId,
      });
      const params = new URLSearchParams({
        intake_id: result.intake_id,
        status: result.status,
        message: result.message,
      });
      router.push(`/resources/partner-kit/referral/thanks?${params.toString()}`);
    } catch (err) {
      const message =
        err instanceof ApiClientError
          ? err.message
          : 'Could not submit referral. Confirm the API is running and try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
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
        {intakeReady === false ? (
          <p className="mb-4 rounded-md border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900">
            Live intake is offline for this environment. Form submission will be blocked until
            referral intake is enabled on the API.
          </p>
        ) : null}
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
            <Button type="submit" variant="primary" disabled={submitting || intakeReady === false}>
              {submitting ? 'Submitting…' : 'Submit referral request'}
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
