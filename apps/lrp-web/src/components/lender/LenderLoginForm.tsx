'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import { useLenderAuth } from '@/lib/lender/auth';

export function LenderLoginForm() {
  const { login } = useLenderAuth();
  const router = useRouter();
  const search = useSearchParams();
  const [email, setEmail] = useState('owner@verdin.demo');
  const [password, setPassword] = useState('changeme123');
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
    const redirect = search.get('redirect') || '/lender/dashboard';
    router.replace(redirect);
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label htmlFor="lender-email" className="block text-sm font-medium">
          Work email
        </label>
        <input
          id="lender-email"
          type="email"
          autoComplete="username"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
        />
      </div>
      <div>
        <label htmlFor="lender-password" className="block text-sm font-medium">
          Password
        </label>
        <input
          id="lender-password"
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
        {pending ? 'Signing in…' : 'Sign in to lender workspace'}
      </button>
      <div className="space-y-1 text-xs text-slate-500">
        <p>
          Platform staff (interim): <code>owner@verdin.demo</code> / <code>changeme123</code>
        </p>
        <p>
          Demo LO fallback: <code>lo@lrp.lender</code> / <code>admin@lrp.lender</code> —{' '}
          <code>changeme123</code>
        </p>
        <p>Partner-member JWT is deferred (mortgage_partner realm).</p>
      </div>
    </form>
  );
}
