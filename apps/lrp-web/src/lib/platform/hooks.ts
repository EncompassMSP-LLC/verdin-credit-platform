'use client';

import {
  getPortalCase,
  getPortalCaseTimeline,
  listPortalCaseDocuments,
  listPortalCases,
  listPortalCaseMessages,
  type PortalCaseDetail,
  type PortalCaseSummary,
  type PortalDocument,
  type PortalCaseMessageThread,
  type PortalTimelineEventType,
  type PortalTimelineItem,
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

export function usePortalTimeline(
  caseId: string | undefined,
  eventType?: PortalTimelineEventType | 'all',
) {
  const { isAuthenticated } = usePlatformAuth();
  const filter = eventType && eventType !== 'all' ? eventType : undefined;
  return useQuery({
    queryKey: ['portal', 'timeline', caseId, filter ?? 'all'],
    enabled: isAuthenticated && Boolean(caseId),
    queryFn: async () => {
      const response = await getPortalCaseTimeline(caseId!, {
        event_type: filter,
      });
      return response.items;
    },
  });
}

export type {
  PortalCaseDetail,
  PortalCaseSummary,
  PortalDocument,
  PortalCaseMessageThread,
  PortalTimelineItem,
  PortalTimelineEventType,
};
