'use client';

import Link from 'next/link';
import { useState, type FormEvent } from 'react';
import { ApiClientError, configureApiClient, portalForgotPassword } from '@verdin/api-client';
import { AuthShell } from '@/components/portal/AuthShell';
import { getApiBaseUrl } from '@/lib/platform/config';

const inputClass =
  'w-full rounded-brand border border-navy-900/15 bg-white px-3.5 py-2.5 text-sm text-navy-900 shadow-sm focus:border-gold-500 focus:outline-none focus:ring-2 focus:ring-gold-500/30 dark:border-white/15 dark:bg-navy-900 dark:text-white';

export function ForgotPasswordForm() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<string | null>(null);
  const [devToken, setDevToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setDetail(null);
    setDevToken(null);
    setLoading(true);
    try {
      configureApiClient({ baseUrl: getApiBaseUrl() });
      const result = await portalForgotPassword(email.trim());
      setDetail(result.detail);
      if (result.reset_token) {
        setDevToken(result.reset_token);
      }
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Request failed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4" noValidate>
      <h1 className="text-2xl font-semibold text-navy-900 dark:text-white">Reset your password</h1>
      <p className="text-sm text-slate-500 dark:text-white/65">
        Enter the email on your borrower portal account. For privacy, we always show the same
        confirmation message whether or not an account exists.
      </p>
      <div>
        <label htmlFor="email" className="mb-1.5 block text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={inputClass}
        />
      </div>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {detail ? <p className="text-sm text-navy-900 dark:text-white/80">{detail}</p> : null}
      {devToken ? (
        <p className="rounded-brand border border-gold-500/40 bg-gold-500/10 px-3 py-2 text-xs">
          Dev/test reset token issued.{' '}
          <Link
            className="font-semibold text-gold-700 underline"
            href={`/portal/reset-password?token=${encodeURIComponent(devToken)}`}
          >
            Continue to set a new password
          </Link>
        </p>
      ) : null}
      <button
        type="submit"
        disabled={loading}
        className="inline-flex w-full justify-center rounded-brand bg-gold-500 px-4 py-3 text-sm font-semibold uppercase tracking-wide text-navy-900 hover:bg-gold-400 disabled:opacity-60"
      >
        {loading ? 'Sending…' : 'Request reset'}
      </button>
      <Link href="/portal/login" className="block text-center text-sm text-slate-500 underline">
        Back to sign in
      </Link>
    </form>
  );
}

export default function ForgotPasswordPageClient() {
  return (
    <AuthShell
      title="Password help"
      subtitle="Self-serve reset for your borrower portal account on the shared platform."
    >
      <ForgotPasswordForm />
    </AuthShell>
  );
}
