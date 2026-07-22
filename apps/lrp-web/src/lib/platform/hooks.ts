'use client';

import {
  getPortalCase,
  listPortalCaseDocuments,
  listPortalCases,
  listPortalCaseMessages,
  type PortalCaseDetail,
  type PortalCaseSummary,
  type PortalDocument,
  type PortalCaseMessageThread,
} from '@verdin/api-client';
import { useQuery } from '@tanstack/react-query';
import { usePlatformAuth } from '@/lib/platform/auth';

export function usePortalCases() {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'cases'],
    enabled: isAuthenticated,
    queryFn: async () => {
      const response = await listPortalCases();
      return response.items;
    },
  });
}

export function usePrimaryCase() {
  const casesQuery = usePortalCases();
  const primary = casesQuery.data?.[0] ?? null;
  return { ...casesQuery, primary };
}

export function usePortalCaseDetail(caseId: string | undefined) {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'case', caseId],
    enabled: isAuthenticated && Boolean(caseId),
    queryFn: () => getPortalCase(caseId!),
  });
}

export function usePortalDocuments(caseId: string | undefined) {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'documents', caseId],
    enabled: isAuthenticated && Boolean(caseId),
    queryFn: async () => {
      const response = await listPortalCaseDocuments(caseId!);
      return response.items;
    },
  });
}

export function usePortalMessages(caseId: string | undefined) {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'messages', caseId],
    enabled: isAuthenticated && Boolean(caseId),
    queryFn: () => listPortalCaseMessages(caseId!),
  });
}

export type { PortalCaseDetail, PortalCaseSummary, PortalDocument, PortalCaseMessageThread };
