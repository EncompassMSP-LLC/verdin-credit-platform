'use client';

import {
  completePortalLearningModule,
  getPortalCaseInsights,
  getPortalCaseReadiness,
  listPortalCaseChecklist,
  listPortalLearningModules,
  reopenPortalLearningModule,
  updatePortalChecklistItem,
  type PortalCaseInsights,
  type PortalCaseReadiness,
  type PortalChecklistItem,
  type PortalLearningModule,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { usePlatformAuth } from '@/lib/platform/auth';
import { usePrimaryCase } from '@/lib/platform/hooks';

export function usePortalReadiness(caseId: string | undefined) {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'readiness', caseId],
    enabled: isAuthenticated && Boolean(caseId),
    queryFn: () => getPortalCaseReadiness(caseId!),
  });
}

export function usePortalInsights(caseId: string | undefined) {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'insights', caseId],
    enabled: isAuthenticated && Boolean(caseId),
    queryFn: () => getPortalCaseInsights(caseId!),
  });
}

export function usePortalChecklist(caseId: string | undefined) {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'checklist', caseId],
    enabled: isAuthenticated && Boolean(caseId),
    queryFn: async () => {
      const response = await listPortalCaseChecklist(caseId!);
      return response.items;
    },
  });
}

export function useUpdatePortalChecklistItem(caseId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ itemId, status }: { itemId: string; status: 'open' | 'done' }) =>
      updatePortalChecklistItem(itemId, status),
    onSuccess: () => {
      if (caseId) {
        void queryClient.invalidateQueries({ queryKey: ['portal', 'checklist', caseId] });
      }
    },
  });
}

export function usePortalLearningModules() {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'learning'],
    enabled: isAuthenticated,
    queryFn: async () => {
      const response = await listPortalLearningModules();
      return response.items;
    },
  });
}

export function useTogglePortalLearningModule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (module: PortalLearningModule) => {
      if (module.completed) {
        return reopenPortalLearningModule(module.id);
      }
      return completePortalLearningModule(module.id);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['portal', 'learning'] });
    },
  });
}

export function usePrimaryCaseReadinessSurfaces() {
  const { primary, ...casesQuery } = usePrimaryCase();
  const readiness = usePortalReadiness(primary?.id);
  const insights = usePortalInsights(primary?.id);
  const checklist = usePortalChecklist(primary?.id);
  return {
    casesQuery,
    primary,
    readiness,
    insights,
    checklist,
  };
}

export type { PortalCaseInsights, PortalCaseReadiness, PortalChecklistItem, PortalLearningModule };
