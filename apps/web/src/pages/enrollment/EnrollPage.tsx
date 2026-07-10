import { useMutation, useQuery } from '@tanstack/react-query';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  ApiClientError,
  getClientEnrollmentStatus,
  registerClientEnrollment,
  startClientEnrollmentCheckout,
} from '@verdin/api-client';
import { clientEnrollmentIntakeSchema, type ClientEnrollmentIntakeInput } from '@verdin/validation';
import { Button, Card } from '@verdin/ui';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';

import { establishPortalSession } from '../../lib/portal-auth';
import { featureFlags } from '../../lib/feature-flags';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function EnrollPage() {
  const navigate = useNavigate();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const statusQuery = useQuery({
    queryKey: ['client-enrollment-status'],
    queryFn: getClientEnrollmentStatus,
    enabled: featureFlags.enableClientEnrollment,
    retry: false,
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ClientEnrollmentIntakeInput>({
    resolver: zodResolver(clientEnrollmentIntakeSchema),
    defaultValues: {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      phone: '',
      mailing_address_line1: '',
      mailing_address_line2: '',
      mailing_city: '',
      mailing_state: 'GA',
      mailing_postal_code: '',
    },
  });

  const checkoutMutation = useMutation({
    mutationFn: startClientEnrollmentCheckout,
    onSuccess: (result) => {
      window.location.href = result.checkout_url;
    },
    onError: (error) => {
      setSubmitError(error instanceof ApiClientError ? error.message : 'Enrollment failed');
    },
  });

  const registerMutation = useMutation({
    mutationFn: registerClientEnrollment,
    onSuccess: async (result) => {
      await establishPortalSession(result.portal);
      if (result.enrollment.case_id) {
        navigate(`/portal/cases/${result.enrollment.case_id}`, { replace: true });
        return;
      }
      navigate('/portal', { replace: true });
    },
    onError: (error) => {
      setSubmitError(error instanceof ApiClientError ? error.message : 'Enrollment failed');
    },
  });

  if (!featureFlags.enableClientEnrollment) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <Card className="max-w-lg p-8 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Enrollment unavailable</h1>
          <p className="mt-2 text-sm text-gray-600">
            Online enrollment is not enabled in this environment.
          </p>
          <Link
            to="/portal/login"
            className="mt-6 inline-block text-sm text-brand-600 hover:underline"
          >
            Client portal sign in
          </Link>
        </Card>
      </div>
    );
  }

  const status = statusQuery.data;
  const useCheckout = Boolean(status?.checkout_available);
  const annualCreditReportUrl =
    status?.annual_credit_report_url ?? 'https://www.annualcreditreport.com/index.action';

  const onSubmit = (values: ClientEnrollmentIntakeInput) => {
    setSubmitError(null);
    const payload = {
      ...values,
      phone: values.phone?.trim() || null,
      mailing_address_line2: values.mailing_address_line2?.trim() || null,
    };
    if (useCheckout) {
      checkoutMutation.mutate(payload);
      return;
    }
    registerMutation.mutate(payload);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="mx-auto max-w-3xl">
        <div className="mb-8 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
            Ultimate Credit Repair LLC
          </p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">Start your credit repair case</h1>
          <p className="mt-2 text-sm text-gray-600">
            Create your client portal account, complete intake, and get instructions to pull your
            free credit reports.
          </p>
        </div>

        {statusQuery.isError || (status && !status.ready) ? (
          <Card className="mb-6 border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
            <p className="font-medium">Enrollment is not ready yet</p>
            {status?.blockers.length ? (
              <ul className="mt-2 list-disc space-y-1 pl-5">
                {status.blockers.map((blocker) => (
                  <li key={blocker}>{blocker}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-2">Check API configuration and try again later.</p>
            )}
          </Card>
        ) : null}

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="p-6 lg:col-span-2">
            <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">First name</label>
                  <input className={inputClass} {...register('first_name')} />
                  {errors.first_name ? (
                    <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
                  ) : null}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Last name</label>
                  <input className={inputClass} {...register('last_name')} />
                  {errors.last_name ? (
                    <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
                  ) : null}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input type="email" className={inputClass} {...register('email')} />
                {errors.email ? (
                  <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                ) : null}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Portal password</label>
                <input type="password" className={inputClass} {...register('password')} />
                {errors.password ? (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                ) : null}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Phone (optional)</label>
                <input className={inputClass} {...register('phone')} />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Mailing address</label>
                <input
                  className={inputClass}
                  placeholder="Street address"
                  {...register('mailing_address_line1')}
                />
                <input
                  className={`${inputClass} mt-2`}
                  placeholder="Apt / suite (optional)"
                  {...register('mailing_address_line2')}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div className="sm:col-span-1">
                  <label className="block text-sm font-medium text-gray-700">City</label>
                  <input className={inputClass} {...register('mailing_city')} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">State</label>
                  <input className={inputClass} {...register('mailing_state')} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ZIP</label>
                  <input className={inputClass} {...register('mailing_postal_code')} />
                </div>
              </div>

              {submitError ? (
                <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{submitError}</p>
              ) : null}

              <Button
                type="submit"
                loading={isSubmitting || checkoutMutation.isPending || registerMutation.isPending}
                disabled={!status?.ready}
              >
                {useCheckout ? 'Continue to secure payment' : 'Create my account'}
              </Button>
            </form>
          </Card>

          <Card className="p-6">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
              What happens next
            </h2>
            <ol className="mt-4 list-decimal space-y-3 pl-5 text-sm text-gray-700">
              <li>
                {useCheckout
                  ? 'Pay your enrollment fee securely with Stripe.'
                  : 'Create your portal account.'}
              </li>
              <li>Sign required compliance documents in the portal.</li>
              <li>
                Pull your free reports from{' '}
                <a
                  className="font-medium text-brand-600 hover:text-brand-700"
                  href={annualCreditReportUrl}
                  rel="noreferrer"
                  target="_blank"
                >
                  annualcreditreport.com
                </a>
                .
              </li>
              <li>Upload Experian, Equifax, and TransUnion PDFs to your case.</li>
            </ol>
            <p className="mt-6 text-xs text-gray-500">
              Already enrolled?{' '}
              <Link to="/portal/login" className="text-brand-600 hover:underline">
                Sign in to the client portal
              </Link>
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
