interface PortalEnrollmentOnboardingProps {
  annualCreditReportUrl: string;
}

export function PortalEnrollmentOnboarding({
  annualCreditReportUrl,
}: PortalEnrollmentOnboardingProps) {
  return (
    <div className="mt-8 rounded-lg border border-brand-200 bg-brand-50 p-6">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-700">
        Getting started
      </h2>
      <p className="mt-2 text-sm text-brand-900">
        Follow these steps so we can review your credit reports and start your dispute strategy.
      </p>
      <ol className="mt-4 list-decimal space-y-3 pl-5 text-sm text-brand-900">
        <li>
          Review and e-sign the compliance documents below (CROA disclosure, service agreement, and
          FCRA authorization).
        </li>
        <li>
          Visit{' '}
          <a
            className="font-medium underline"
            href={annualCreditReportUrl}
            rel="noreferrer"
            target="_blank"
          >
            annualcreditreport.com
          </a>{' '}
          to request your free reports from Experian, Equifax, and TransUnion. You are entitled to
          one free report from each bureau every 12 months.
        </li>
        <li>
          Download each bureau report as a PDF, then upload all three under{' '}
          <strong>Your documents</strong> on this page.
        </li>
        <li>We will notify you when analysis and dispute preparation begin.</li>
      </ol>
      <p className="mt-4 text-xs text-brand-800">
        Tip: use the official site only (
        <a className="underline" href={annualCreditReportUrl} rel="noreferrer" target="_blank">
          annualcreditreport.com
        </a>
        ). Avoid look-alike sites that charge unnecessary fees.
      </p>
    </div>
  );
}
