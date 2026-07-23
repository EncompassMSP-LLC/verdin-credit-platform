'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import { useCrmAuth } from '@/lib/crm/auth';

export function CrmLoginForm() {
  const { login } = useCrmAuth();
  const router = useRouter();
  const search = useSearchParams();
  const [email, setEmail] = useState('lo@lrp.crm');
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
          className="mt-1.5 w-full rounded-md border border-navy-900/15 bg-white px-3 py-2.5 text-sm dark:border-white/15 dark:bg-navy-900"
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
          className="mt-1.5 w-full rounded-md border border-navy-900/15 bg-white px-3 py-2.5 text-sm dark:border-white/15 dark:bg-navy-900"
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
        className="w-full rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-700 disabled:opacity-60 dark:bg-gold-500 dark:text-navy-900"
      >
        {pending ? 'Signing in…' : 'Sign in to CRM'}
      </button>
      <p className="text-xs text-slate-500 dark:text-white/55">
        Demo: <code>admin@lrp.crm</code> / <code>lo@lrp.crm</code> / <code>partners@lrp.crm</code> /{' '}
        <code>ops@lrp.crm</code> — password <code>changeme123</code>
      </p>
    </form>
  );
}
