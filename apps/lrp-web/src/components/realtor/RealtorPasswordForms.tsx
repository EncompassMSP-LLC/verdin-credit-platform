'use client';

import {
  configureApiClient,
  confirmRealtorPasswordReset,
  requestRealtorPasswordReset,
} from '@verdin/api-client';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useRealtorAuth } from '@/lib/realtor/auth';
import { getApiBaseUrl } from '@/lib/platform/config';

export function RealtorForgotPasswordForm() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [devToken, setDevToken] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
  }, []);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setPending(true);
    setMessage(null);
    setDevToken(null);
    try {
      const result = await requestRealtorPasswordReset(email.trim());
      setMessage(result.detail);
      if (result.reset_token) setDevToken(result.reset_token);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Request failed.');
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label htmlFor="reset-email" className="block text-sm font-medium">
          Work email
        </label>
        <input
          id="reset-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
        />
      </div>
      {message ? <p className="text-sm text-slate-600">{message}</p> : null}
      {devToken ? (
        <p className="break-all rounded-md border border-lrp-border bg-lrp-surface px-3 py-2 text-xs text-slate-500">
          Dev/test reset token:{' '}
          <Link
            href={`/realtor/reset-password?token=${encodeURIComponent(devToken)}`}
            className="font-medium text-gold-700 hover:underline"
          >
            continue reset
          </Link>
        </p>
      ) : null}
      <button
        type="submit"
        disabled={pending}
        className="w-full rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-700 disabled:opacity-60"
      >
        {pending ? 'Sending…' : 'Request reset'}
      </button>
      <Link
        href="/realtor/login"
        className="inline-block text-sm font-medium text-gold-700 hover:underline"
      >
        ← Back to sign in
      </Link>
    </form>
  );
}

export function RealtorResetPasswordForm() {
  const router = useRouter();
  const search = useSearchParams();
  const { applySessionTokens } = useRealtorAuth();
  const [token, setToken] = useState(search.get('token') || '');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
  }, []);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setPending(true);
    setError(null);
    try {
      const result = await confirmRealtorPasswordReset(token.trim(), password);
      applySessionTokens(result.access_token, result.refresh_token, result.realtor);
      router.replace('/realtor/dashboard');
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Reset failed.');
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label htmlFor="reset-token" className="block text-sm font-medium">
          Reset token
        </label>
        <input
          id="reset-token"
          required
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
        />
      </div>
      <div>
        <label htmlFor="new-password" className="block text-sm font-medium">
          New password
        </label>
        <input
          id="new-password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
        />
      </div>
      <div>
        <label htmlFor="confirm-password" className="block text-sm font-medium">
          Confirm password
        </label>
        <input
          id="confirm-password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
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
        {pending ? 'Updating…' : 'Update password'}
      </button>
    </form>
  );
}
