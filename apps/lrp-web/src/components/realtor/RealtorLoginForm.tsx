'use client';

import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import { isDemoAuthEnabled } from '@/lib/auth/realms';
import { useRealtorAuth } from '@/lib/realtor/auth';

export function RealtorLoginForm() {
  const { login } = useRealtorAuth();
  const router = useRouter();
  const search = useSearchParams();
  const demoAuth = isDemoAuthEnabled('realtor');
  const [email, setEmail] = useState(demoAuth ? 'agent@lrp.realtor' : '');
  const [password, setPassword] = useState(demoAuth ? 'changeme123' : '');
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    const result = await login(email, password);
    setPending(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    const redirect = search.get('redirect') || '/realtor/dashboard';
    router.replace(redirect);
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label htmlFor="realtor-email" className="block text-sm font-medium">
          Work email
        </label>
        <input
          id="realtor-email"
          type="email"
          autoComplete="username"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
        />
      </div>
      <div>
        <label htmlFor="realtor-password" className="block text-sm font-medium">
          Password
        </label>
        <input
          id="realtor-password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
        />
      </div>
      {error ? (
        <p className="rounded-md border border-critical/30 bg-critical/10 px-3 py-2 text-sm text-critical">
          {error}
        </p>
      ) : null}
      <button
        type="submit"
        disabled={pending}
        className="w-full rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-700 disabled:opacity-60"
      >
        {pending ? 'Signing in…' : 'Sign in to realtor workspace'}
      </button>
      <div className="space-y-1 text-xs text-slate-500">
        <p>Sign in with an invited realtor account (API required).</p>
        {demoAuth ? (
          <p>
            Demo fallback: <code>agent@lrp.realtor</code> / <code>changeme123</code>
          </p>
        ) : null}
        <p>
          <Link
            href="/realtor/forgot-password"
            className="font-medium text-gold-700 hover:underline"
          >
            Forgot password?
          </Link>
          {' · '}
          <Link href="/realtor/activate" className="font-medium text-gold-700 hover:underline">
            Activate invite
          </Link>
        </p>
        <p>Lender, borrower portal, and CRM shells are not available in this realm.</p>
      </div>
    </form>
  );
}
