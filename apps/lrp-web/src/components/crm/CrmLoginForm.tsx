'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import { isDemoAuthEnabled } from '@/lib/auth/realms';
import { useCrmAuth } from '@/lib/crm/auth';

export function CrmLoginForm() {
  const { login } = useCrmAuth();
  const router = useRouter();
  const search = useSearchParams();
  const demoAuth = isDemoAuthEnabled('crm');
  const [email, setEmail] = useState(demoAuth ? 'owner@verdin.demo' : '');
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
    const redirect = search.get('redirect') || '/crm/dashboard';
    router.replace(redirect);
    router.refresh();
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label htmlFor="crm-email" className="block text-sm font-medium">
          Work email
        </label>
        <input
          id="crm-email"
          type="email"
          autoComplete="username"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
        />
      </div>
      <div>
        <label htmlFor="crm-password" className="block text-sm font-medium">
          Password
        </label>
        <input
          id="crm-password"
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
        {pending ? 'Signing in…' : 'Sign in to CRM'}
      </button>
      <div className="space-y-1 text-xs text-slate-500">
        <p>Sign in with a platform staff account (API required).</p>
        {demoAuth ? (
          <>
            <p>
              Local seed: <code>owner@verdin.demo</code> / <code>changeme123</code>
            </p>
            <p>
              Demo fallback: <code>admin@lrp.crm</code> / <code>lo@lrp.crm</code> — password{' '}
              <code>changeme123</code>
            </p>
          </>
        ) : null}
      </div>
    </form>
  );
}
