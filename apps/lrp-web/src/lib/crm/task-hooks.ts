'use client';

import { getDailyTaskDigest, listTasks, type ListTasksParams } from '@verdin/api-client';
import { useQuery } from '@tanstack/react-query';

import { useCrmAuth } from '@/lib/crm/auth';

export function useCrmTasks(params: ListTasksParams = {}) {
  const { authMode, isAuthenticated } = useCrmAuth();
  const enabled = authMode === 'platform' && isAuthenticated;

  return useQuery({
    queryKey: ['crm-tasks', params],
    queryFn: () => listTasks(params),
    enabled,
  });
}

export function useCrmDailyTaskDigest() {
  const { authMode, isAuthenticated } = useCrmAuth();
  const enabled = authMode === 'platform' && isAuthenticated;

  return useQuery({
    queryKey: ['crm-tasks-digest'],
    queryFn: getDailyTaskDigest,
    enabled,
    staleTime: 30_000,
  });
}
