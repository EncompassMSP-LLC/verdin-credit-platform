import type { PaginatedResponse } from '@verdin/shared';

import { apiPath, request } from './http';

export interface TimelineEvent {
  id: string;
  organization_id: string;
  case_id: string | null;
  account_id: string | null;
  document_id: string | null;
  event_type: string;
  event_category: string;
  title: string;
  description: string | null;
  metadata: Record<string, unknown>;
  performed_by: string | null;
  source_module: string;
  occurred_at: string;
  created_at: string;
}

export interface ListTimelineParams {
  page?: number;
  page_size?: number;
  case_id?: string;
  account_id?: string;
  document_id?: string;
  event_type?: string;
  event_category?: string;
  performed_by?: string;
  occurred_from?: string;
  occurred_to?: string;
  sort_by?: 'occurred_at' | 'created_at' | 'event_type';
  sort_order?: 'asc' | 'desc';
}

function buildQuery(params: Record<string, unknown>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function listTimelineEvents(
  params: ListTimelineParams = {},
): Promise<PaginatedResponse<TimelineEvent>> {
  return request<PaginatedResponse<TimelineEvent>>(
    `${apiPath('/timeline')}${buildQuery(params as Record<string, unknown>)}`,
  );
}

export async function getTimelineEvent(eventId: string): Promise<TimelineEvent> {
  return request<TimelineEvent>(apiPath(`/timeline/${eventId}`));
}
