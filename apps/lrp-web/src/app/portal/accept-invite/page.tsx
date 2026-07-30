'use client';

import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Suspense, useState, type FormEvent } from 'react';
import { ApiClientError, configureApiClient, portalAcceptInvite } from '@verdin/api-client';
import { AuthShell } from '@/components/portal/AuthShell';
import { usePlatformAuth } from '@/lib/platform/auth';
import { getApiBaseUrl } from '@/lib/platform/config';

const inputClass =
  'w-full rounded-brand border border-navy-900/15 bg-white px-3.5 py-2.5 text-sm text-navy-900 shadow-sm focus:border-gold-500 focus:outline-none focus:ring-2 focus:ring-gold-500/30 dark:border-white/15 dark:bg-navy-900 dark:text-white';

function AcceptInviteForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tokenFromQuery = searchParams.get('token') ?? '';
  const { establishSession } = usePlatformAuth();

  const [token, setToken] = useState(tokenFromQuery);
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    setLoading(true);
    try {
      configureApiClient({ baseUrl: getApiBaseUrl() });
      const tokens = await portalAcceptInvite({ token: token.trim(), password });
      await establishSession(tokens.access_token, tokens.refresh_token);
      router.push('/portal/dashboard');
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Invite activation failed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4" noValidate>
      <h1 className="text-2xl font-semibold text-navy-900 dark:text-white">Activate your portal</h1>
      <p className="text-sm text-slate-500 dark:text-white/65">
        Use the invite link from your readiness partner to choose a password. No temporary password
        was emailed.
      </p>
      <div>
        <label htmlFor="token" className="mb-1.5 block text-sm font-medium">
          Invite token
        </label>
        <input
          id="token"
          required
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className={inputClass}
        />
      </div>
      <div>
        <label htmlFor="password" className="mb-1.5 block text-sm font-medium">
          New password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={inputClass}
        />
      </div>
      <div>
        <label htmlFor="confirm" className="mb-1.5 block text-sm font-medium">
          Confirm password
        </label>
        <input
          id="confirm"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          className={inputClass}
        />
      </div>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <button
        type="submit"
        disabled={loading}
        className="inline-flex w-full justify-center rounded-brand bg-gold-500 px-4 py-3 text-sm font-semibold uppercase tracking-wide text-navy-900 hover:bg-gold-400 disabled:opacity-60"
      >
        {loading ? 'Activating…' : 'Set password and continue'}
      </button>
      <Link href="/portal/login" className="block text-center text-sm text-slate-500 underline">
        Already activated? Sign in
      </Link>
    </form>
  );
}

export default function AcceptInvitePage() {
  return (
    <AuthShell title="Portal invite" subtitle="Complete your borrower portal activation.">
      <Suspense fallback={<p className="text-sm text-slate-500">Loading…</p>}>
        <AcceptInviteForm />
      </Suspense>
    </AuthShell>
  );
}
