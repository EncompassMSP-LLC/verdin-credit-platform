'use client';

import { listClients, type Client, type ClientStatus } from '@verdin/api-client';
import { useQuery } from '@tanstack/react-query';
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

export type { Client, ClientStatus };
