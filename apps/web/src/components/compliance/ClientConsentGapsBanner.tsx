import { Link } from 'react-router-dom';
import { useCaseClientConsentGaps } from '../../hooks/useCaseClientConsentGaps';

interface ClientConsentGapsBannerProps {
  caseId: string | undefined;
  className?: string;
}

export function ClientConsentGapsBanner({ caseId, className = '' }: ClientConsentGapsBannerProps) {
  const { clientId, missingTemplateLabels, hasGaps, requiresConsent, isLoading, isReady } =
    useCaseClientConsentGaps(caseId);

  if (isLoading || !isReady) {
    return null;
  }

  if (!requiresConsent) {
    return (
      <div
        className={`rounded-md border border-gray-200 bg-gray-50 p-4 text-sm text-gray-700 ${className}`}
      >
        <p className="font-medium text-gray-900">No client linked to this case</p>
        <p className="mt-1">
          Link a client to the case before exporting dispute mail packets or collecting signed
          consents.
        </p>
        {caseId ? (
          <Link
            to={`/cases/${caseId}/edit`}
            className="mt-2 inline-block text-sm font-medium text-brand-600 hover:underline"
          >
            Edit case →
          </Link>
        ) : null}
      </div>
    );
  }

  if (!hasGaps) {
    return null;
  }

  const labels = missingTemplateLabels;

  return (
    <div
      className={`rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 ${className}`}
    >
      <p className="font-medium">Signed client consent required</p>
      <p className="mt-1 text-amber-800">
        Before exporting dispute mail packets or report page previews, collect signed consent for:
      </p>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-amber-900">
        {labels.map((label) => (
          <li key={label}>{label}</li>
        ))}
      </ul>
      <div className="mt-3 flex flex-wrap gap-4 text-sm font-medium">
        <Link to="/compliance" className="text-brand-700 hover:underline">
          Upload signed forms in Compliance →
        </Link>
        {clientId ? (
          <Link to={`/clients/${clientId}`} className="text-brand-700 hover:underline">
            Client profile (portal signing) →
          </Link>
        ) : null}
      </div>
    </div>
  );
}
