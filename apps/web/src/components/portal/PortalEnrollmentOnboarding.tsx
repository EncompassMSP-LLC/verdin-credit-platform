import { useTranslation } from 'react-i18next';

interface PortalEnrollmentOnboardingProps {
  annualCreditReportUrl: string;
}

export function PortalEnrollmentOnboarding({
  annualCreditReportUrl,
}: PortalEnrollmentOnboardingProps) {
  const { t } = useTranslation('portal');

  return (
    <div className="mt-8 rounded-lg border border-brand-200 bg-brand-50 p-6">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-700">
        {t('gettingStarted.title')}
      </h2>
      <p className="mt-2 text-sm text-brand-900">{t('gettingStarted.subtitle')}</p>
      <ol className="mt-4 list-decimal space-y-3 pl-5 text-sm text-brand-900">
        <li>{t('gettingStarted.step1')}</li>
        <li>
          {t('gettingStarted.step2Before')}{' '}
          <a
            className="font-medium underline"
            href={annualCreditReportUrl}
            rel="noreferrer"
            target="_blank"
          >
            annualcreditreport.com
          </a>{' '}
          {t('gettingStarted.step2After')}
        </li>
        <li>
          {t('gettingStarted.step3Before')} <strong>{t('gettingStarted.step3Strong')}</strong>{' '}
          {t('gettingStarted.step3After')}
        </li>
        <li>{t('gettingStarted.step4')}</li>
      </ol>
      <p className="mt-4 text-xs text-brand-800">
        {t('gettingStarted.tipBefore')}
        <a className="underline" href={annualCreditReportUrl} rel="noreferrer" target="_blank">
          annualcreditreport.com
        </a>
        {t('gettingStarted.tipAfter')}
      </p>
    </div>
  );
}
