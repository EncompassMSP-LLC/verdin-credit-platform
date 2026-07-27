'use client';

import {
  canShowDemoActions,
  generateSampleBorrowers,
  getOrganizationContext,
  type OrganizationContext,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { useCrmAuth } from '@/lib/crm/auth';

export function useOrganizationContext() {
  const { authMode, isAuthenticated } = useCrmAuth();
  const enabled = authMode === 'platform' && isAuthenticated;

  return useQuery({
    queryKey: ['org-context', authMode, isAuthenticated],
    queryFn: getOrganizationContext,
    enabled,
    staleTime: 60_000,
  });
}

export function useCanShowDemoActions(): boolean {
  const { authMode } = useCrmAuth();
  const ctxQuery = useOrganizationContext();
  if (authMode === 'demo') return true;
  if (authMode !== 'platform') return false;
  return canShowDemoActions(ctxQuery.data as OrganizationContext | undefined);
}

export function useGenerateSampleBorrowers() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (count: number) => generateSampleBorrowers(count),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['crm-clients'] });
      await queryClient.invalidateQueries({ queryKey: ['org-context'] });
    },
  });
}
