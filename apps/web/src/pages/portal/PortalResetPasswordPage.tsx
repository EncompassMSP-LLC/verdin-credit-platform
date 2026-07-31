import { useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@verdin/ui';
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom';
import { portalResetPassword } from '@verdin/api-client';
import { LanguageSwitcher } from '../../components/LanguageSwitcher';
import { usePortalAuth } from '../../lib/portal-auth';
import { featureFlags } from '../../lib/feature-flags';

const resetSchema = z
  .object({
    token: z.string().min(1, 'Reset token is required'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm: z.string().min(8, 'Confirm your password'),
  })
  .refine((data) => data.password === data.confirm, {
    message: 'Passwords do not match',
    path: ['confirm'],
  });

type ResetForm = z.infer<typeof resetSchema>;

export function PortalResetPasswordPage() {
  const { establishSession, isAuthenticated } = usePortalAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  const defaultToken = useMemo(() => searchParams.get('token') ?? '', [searchParams]);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetForm>({
    resolver: zodResolver(resetSchema),
    defaultValues: { token: defaultToken, password: '', confirm: '' },
  });

  if (!featureFlags.enableClientPortal) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <div className="w-full max-w-md rounded-lg border border-gray-200 bg-white p-8 text-center shadow-sm">
          <h1 className="text-xl font-semibold text-gray-900">Portal unavailable</h1>
          <p className="mt-2 text-sm text-gray-500">Client portal is not enabled.</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/portal" replace />;
  }

  const onSubmit = async (data: ResetForm) => {
    setError(null);
    try {
      const tokens = await portalResetPassword({
        token: data.token.trim(),
        password: data.password,
      });
      await establishSession(tokens.access_token, tokens.refresh_token);
      navigate('/portal');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Password reset failed.');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md rounded-lg border border-gray-200 bg-white p-8 shadow-sm">
        <div className="mb-4 flex justify-end">
          <LanguageSwitcher compact />
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Choose a new password</h1>
        <p className="mt-1 text-sm text-gray-500">
          Paste the reset token from your email and set a new password.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-4">
          <div>
            <label htmlFor="token" className="block text-sm font-medium text-gray-700">
              Reset token
            </label>
            <input
              id="token"
              {...register('token')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            {errors.token ? (
              <p className="mt-1 text-sm text-red-600">{errors.token.message}</p>
            ) : null}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              New password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              {...register('password')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            {errors.password ? (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            ) : null}
          </div>

          <div>
            <label htmlFor="confirm" className="block text-sm font-medium text-gray-700">
              Confirm password
            </label>
            <input
              id="confirm"
              type="password"
              autoComplete="new-password"
              {...register('confirm')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            {errors.confirm ? (
              <p className="mt-1 text-sm text-red-600">{errors.confirm.message}</p>
            ) : null}
          </div>

          {error ? <p className="text-sm text-red-600">{error}</p> : null}

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? 'Saving…' : 'Update password and continue'}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500">
          <Link to="/portal/login" className="text-brand-600 underline">
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
