'use client';

import {
  ApiClientError,
  createCreditAnalysisRun,
  getClient,
  getLatestCreditAnalysisRun,
  listCases,
  listClients,
  type Case,
  type Client,
  type ClientStatus,
  type CreditAnalysisRun,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useCrmAuth } from '@/lib/crm/auth';

export function useCrmClients(params: {
  page: number;
  pageSize?: number;
  search?: string;
  status?: ClientStatus | '';
}) {
  const { isAuthenticated, authMode } = useCrmAuth();
  const search = params.search?.trim() ?? '';
  const enabledSearch = search.length === 0 || search.length >= 2;

  return useQuery({
    queryKey: [
      'crm',
      'clients',
      params.page,
      params.pageSize ?? 20,
      search,
      params.status || 'all',
    ],
    enabled: isAuthenticated && authMode === 'platform' && enabledSearch,
    queryFn: () =>
      listClients({
        page: params.page,
        page_size: params.pageSize ?? 20,
        search: search || undefined,
        status: params.status || undefined,
        sort_by: 'updated_at',
        sort_order: 'desc',
      }),
  });
}

export function useCrmClient(clientId: string | undefined) {
  const { isAuthenticated, authMode } = useCrmAuth();
  return useQuery({
    queryKey: ['crm', 'client', clientId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(clientId),
    queryFn: () => getClient(clientId!),
    retry: (count, error) => {
      if (error instanceof ApiClientError && error.status === 404) return false;
      return count < 2;
    },
  });
}

export function useCrmClientCases(clientId: string | undefined) {
  const { isAuthenticated, authMode } = useCrmAuth();
  return useQuery({
    queryKey: ['crm', 'client-cases', clientId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(clientId),
    queryFn: async () => {
      const response = await listCases({
        client_id: clientId,
        page: 1,
        page_size: 10,
        sort_by: 'updated_at',
        sort_order: 'desc',
      });
      return response.items;
    },
  });
}

export function useCrmLatestAnalysis(caseId: string | undefined) {
  const { isAuthenticated, authMode } = useCrmAuth();
  return useQuery({
    queryKey: ['crm', 'credit-analysis-latest', caseId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(caseId),
    queryFn: () => getLatestCreditAnalysisRun(caseId!),
    retry: (count, error) => {
      if (error instanceof ApiClientError && error.status === 404) return false;
      return count < 2;
    },
  });
}

/** Spec: Vol 21 · run_analysis / publish_score — POST compose + publish (Vol 22). */
export function useCreateCrmCreditAnalysis(caseId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => {
      if (!caseId) {
        throw new Error('A primary case is required to run credit analysis');
      }
      return createCreditAnalysisRun(caseId);
    },
    onSuccess: () => {
      if (caseId) {
        void queryClient.invalidateQueries({
          queryKey: ['crm', 'credit-analysis-latest', caseId],
        });
      }
    },
  });
}

export type { Case, Client, ClientStatus, CreditAnalysisRun };
