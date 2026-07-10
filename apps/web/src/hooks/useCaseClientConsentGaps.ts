import { useQuery } from '@tanstack/react-query';
import { getCase, getClientConsentGaps } from '@verdin/api-client';

export function useCaseClientConsentGaps(caseId: string | undefined) {
  const caseQuery = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => getCase(caseId!),
    enabled: Boolean(caseId),
  });

  const clientId = caseQuery.data?.client_id ?? null;

  const gapsQuery = useQuery({
    queryKey: ['client-consent-gaps', clientId],
    queryFn: () => getClientConsentGaps(clientId!),
    enabled: Boolean(clientId),
  });

  const missingTemplateKeys = gapsQuery.data?.missing_template_keys ?? [];
  const missingTemplateLabels = gapsQuery.data?.missing_template_labels ?? [];
  const missingConsentTypes = gapsQuery.data?.missing_consent_types ?? [];
  const hasGaps = missingTemplateKeys.length > 0;
  const requiresConsent = Boolean(clientId);

  return {
    clientId,
    missingTemplateKeys,
    missingTemplateLabels,
    missingConsentTypes,
    hasGaps,
    requiresConsent,
    isLoading: caseQuery.isLoading || (Boolean(clientId) && gapsQuery.isLoading),
    isReady: !caseQuery.isLoading && (!clientId || !gapsQuery.isLoading),
  };
}
