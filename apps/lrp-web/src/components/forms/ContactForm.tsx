'use client';

import { useMemo, useState, type FormEvent, type ReactNode } from 'react';
import { useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { siteConfig } from '@/lib/site';

const intents = [
  { value: 'lender', label: 'Lender briefing' },
  { value: 'operator', label: 'Operator partnership' },
  { value: 'realtor', label: 'Realtor partner program' },
  { value: 'network', label: 'Network / enterprise' },
  { value: 'general', label: 'General inquiry' },
] as const;

export function ContactForm() {
  const searchParams = useSearchParams();
  const initialIntent = useMemo(() => {
    const intent = searchParams.get('intent');
    const resource = searchParams.get('resource');
    if (intent && intents.some((item) => item.value === intent)) return intent;
    if (resource) return 'general';
    return 'lender';
  }, [searchParams]);

  const [status, setStatus] = useState<'idle' | 'submitted'>('idle');
  const [form, setForm] = useState({
    name: '',
    email: '',
    organization: '',
    role: '',
    intent: initialIntent,
    message: searchParams.get('resource')
      ? `Please send the resource: ${searchParams.get('resource')}`
      : '',
  });

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus('submitted');
  }

  if (status === 'submitted') {
    return (
      <div
        className="rounded-lg border border-teal-600/30 bg-teal-600/5 p-6"
        role="status"
        aria-live="polite"
      >
        <h2 className="font-display text-2xl text-navy-900">Briefing request received</h2>
        <p className="mt-3 text-ink-700">
          Thank you, {form.name.split(' ')[0] || 'there'}. Our partnerships team will respond at{' '}
          <strong>{form.email}</strong> within one business day. For urgent matters, email{' '}
          <a className="text-teal-700 underline" href={`mailto:${siteConfig.email}`}>
            {siteConfig.email}
          </a>
          .
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="space-y-5" noValidate>
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Full name" id="name" required>
          <input
            id="name"
            name="name"
            required
            autoComplete="name"
            value={form.name}
            onChange={(e) => update('name', e.target.value)}
            className={inputClass}
          />
        </Field>
        <Field label="Work email" id="email" required>
          <input
            id="email"
            name="email"
            type="email"
            required
            autoComplete="email"
            value={form.email}
            onChange={(e) => update('email', e.target.value)}
            className={inputClass}
          />
        </Field>
      </div>
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Organization" id="organization" required>
          <input
            id="organization"
            name="organization"
            required
            autoComplete="organization"
            value={form.organization}
            onChange={(e) => update('organization', e.target.value)}
            className={inputClass}
          />
        </Field>
        <Field label="Role" id="role" required>
          <input
            id="role"
            name="role"
            required
            value={form.role}
            onChange={(e) => update('role', e.target.value)}
            className={inputClass}
          />
        </Field>
      </div>
      <Field label="Partnership type" id="intent" required>
        <select
          id="intent"
          name="intent"
          required
          value={form.intent}
          onChange={(e) => update('intent', e.target.value)}
          className={inputClass}
        >
          {intents.map((intent) => (
            <option key={intent.value} value={intent.value}>
              {intent.label}
            </option>
          ))}
        </select>
      </Field>
      <Field label="How can we help?" id="message" required>
        <textarea
          id="message"
          name="message"
          required
          rows={5}
          value={form.message}
          onChange={(e) => update('message', e.target.value)}
          className={inputClass}
          placeholder="Share volume context, fallout challenges, or the stakeholders you want in a briefing."
        />
      </Field>
      <p className="text-xs leading-relaxed text-slate-500">
        By submitting, you agree we may contact you about Lending Readiness Partners services. We do
        not sell your information. This form does not create a lending relationship or guarantee
        funding outcomes.
      </p>
      <Button type="submit" size="lg">
        Request briefing
      </Button>
    </form>
  );
}

function Field({
  label,
  id,
  required,
  children,
}: {
  label: string;
  id: string;
  required?: boolean;
  children: ReactNode;
}) {
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-navy-900">
        {label}
        {required ? (
          <span className="text-critical" aria-hidden>
            {' '}
            *
          </span>
        ) : null}
      </label>
      {children}
    </div>
  );
}

const inputClass =
  'w-full rounded-md border border-navy-900/15 bg-white px-3.5 py-2.5 text-sm text-ink-900 shadow-sm placeholder:text-slate-400 focus:border-teal-600 focus:outline-none focus:ring-2 focus:ring-teal-600/30';
