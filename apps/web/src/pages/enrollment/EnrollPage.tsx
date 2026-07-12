import { useMemo, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  ApiClientError,
  getClientEnrollmentStatus,
  registerClientEnrollment,
  startClientEnrollmentCheckout,
} from '@verdin/api-client';
import type { ClientEnrollmentIntakeInput } from '@verdin/validation';
import { Button, Card } from '@verdin/ui';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { z } from 'zod';

import { LanguageSwitcher } from '../../components/LanguageSwitcher';
import { establishPortalSession } from '../../lib/portal-auth';
import { featureFlags } from '../../lib/feature-flags';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function EnrollPage() {
  const { t } = useTranslation('enrollment');
  const navigate = useNavigate();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const intakeSchema = useMemo(
    () =>
      z.object({
        email: z.string().email(t('validation.invalidEmail')),
        password: z.string().min(8, t('validation.passwordMin')).max(72),
        first_name: z.string().min(1, t('validation.firstNameRequired')).max(100),
        last_name: z.string().min(1, t('validation.lastNameRequired')).max(100),
        phone: z.string().max(50).optional().or(z.literal('')),
        mailing_address_line1: z.string().min(1, t('validation.streetRequired')).max(255),
        mailing_address_line2: z.string().max(255).optional().or(z.literal('')),
        mailing_city: z.string().min(1, t('validation.cityRequired')).max(100),
        mailing_state: z.string().min(1, t('validation.stateRequired')).max(50),
        mailing_postal_code: z.string().min(1, t('validation.zipRequired')).max(20),
      }),
    [t],
  );

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
    resolver: zodResolver(intakeSchema),
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
      setSubmitError(error instanceof ApiClientError ? error.message : t('enrollmentFailed'));
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
      setSubmitError(error instanceof ApiClientError ? error.message : t('enrollmentFailed'));
    },
  });

  if (!featureFlags.enableClientEnrollment) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <Card className="max-w-lg p-8 text-center">
          <div className="mb-4 flex justify-end">
            <LanguageSwitcher compact />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{t('unavailableTitle')}</h1>
          <p className="mt-2 text-sm text-gray-600">{t('unavailableBody')}</p>
          <Link
            to="/portal/login"
            className="mt-6 inline-block text-sm text-brand-600 hover:underline"
          >
            {t('portalSignInLink')}
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
        <div className="mb-4 flex justify-end">
          <LanguageSwitcher compact />
        </div>
        <div className="mb-8 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
            {t('brand')}
          </p>
          <h1 className="mt-2 text-3xl font-bold text-gray-900">{t('title')}</h1>
          <p className="mt-2 text-sm text-gray-600">{t('subtitle')}</p>
        </div>

        {statusQuery.isError || (status && !status.ready) ? (
          <Card className="mb-6 border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
            <p className="font-medium">{t('notReadyTitle')}</p>
            {status?.blockers.length ? (
              <ul className="mt-2 list-disc space-y-1 pl-5">
                {status.blockers.map((blocker) => (
                  <li key={blocker}>{blocker}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-2">{t('notReadyFallback')}</p>
            )}
          </Card>
        ) : null}

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="p-6 lg:col-span-2">
            <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    {t('firstName')}
                  </label>
                  <input className={inputClass} {...register('first_name')} />
                  {errors.first_name ? (
                    <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
                  ) : null}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">{t('lastName')}</label>
                  <input className={inputClass} {...register('last_name')} />
                  {errors.last_name ? (
                    <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
                  ) : null}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">{t('email')}</label>
                <input type="email" className={inputClass} {...register('email')} />
                {errors.email ? (
                  <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                ) : null}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">{t('password')}</label>
                <input type="password" className={inputClass} {...register('password')} />
                {errors.password ? (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                ) : null}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">{t('phone')}</label>
                <input className={inputClass} {...register('phone')} />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  {t('mailingAddress')}
                </label>
                <input
                  className={inputClass}
                  placeholder={t('streetPlaceholder')}
                  {...register('mailing_address_line1')}
                />
                <input
                  className={`${inputClass} mt-2`}
                  placeholder={t('aptPlaceholder')}
                  {...register('mailing_address_line2')}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div className="sm:col-span-1">
                  <label className="block text-sm font-medium text-gray-700">{t('city')}</label>
                  <input className={inputClass} {...register('mailing_city')} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">{t('state')}</label>
                  <input className={inputClass} {...register('mailing_state')} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">{t('zip')}</label>
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
                {useCheckout ? t('submitCheckout') : t('submitRegister')}
              </Button>
            </form>
          </Card>

          <Card className="p-6">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
              {t('nextTitle')}
            </h2>
            <ol className="mt-4 list-decimal space-y-3 pl-5 text-sm text-gray-700">
              <li>{useCheckout ? t('nextPay') : t('nextCreate')}</li>
              <li>{t('nextSign')}</li>
              <li>
                {t('nextPull')}{' '}
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
              <li>{t('nextUpload')}</li>
            </ol>
            <p className="mt-6 text-xs text-gray-500">
              {t('alreadyEnrolled')}{' '}
              <Link to="/portal/login" className="text-brand-600 hover:underline">
                {t('signInPortal')}
              </Link>
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
