'use client';

import {
  getAccessToken,
  getDocumentDownloadUrl,
  listDocuments,
  uploadDocument,
  type Document,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { useCrmAuth } from '@/lib/crm/auth';

export function useCrmCaseDocuments(caseId: string | undefined) {
  const { isAuthenticated, authMode } = useCrmAuth();
  return useQuery({
    queryKey: ['crm', 'case-documents', caseId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(caseId),
    queryFn: () =>
      listDocuments({
        case_id: caseId,
        page: 1,
        page_size: 50,
        sort_by: 'updated_at',
        sort_order: 'desc',
      }),
  });
}

export function useCrmUploadCaseDocument(caseId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: { file: File; title?: string }) => {
      if (!caseId) throw new Error('No case linked');
      const title = input.title?.trim() || input.file.name;
      return uploadDocument({
        file: input.file,
        title,
        case_id: caseId,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['crm', 'case-documents', caseId] });
    },
  });
}

export async function downloadCrmDocument(doc: Document): Promise<void> {
  const token = getAccessToken();
  const url = getDocumentDownloadUrl(doc.id);
  const response = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) {
    throw new Error('Download failed');
  }
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = objectUrl;
  anchor.download = doc.file_name || doc.title || 'document';
  anchor.click();
  URL.revokeObjectURL(objectUrl);
}
