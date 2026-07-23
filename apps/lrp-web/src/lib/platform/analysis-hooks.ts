'use client';

import { getPortalCaseCreditAnalysis, type PortalCreditAnalysis } from '@verdin/api-client';
import { useQuery } from '@tanstack/react-query';
import { usePlatformAuth } from '@/lib/platform/auth';

export function usePortalCreditAnalysis(caseId: string | undefined) {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'credit-analysis', caseId],
    enabled: isAuthenticated && Boolean(caseId),
    queryFn: () => getPortalCaseCreditAnalysis(caseId!),
    retry: false,
  });
}

export type { PortalCreditAnalysis };
