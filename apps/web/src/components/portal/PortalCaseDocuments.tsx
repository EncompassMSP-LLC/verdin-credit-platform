import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listPortalCaseDocuments,
  uploadPortalCaseDocument,
  type PortalDocument,
} from '@verdin/api-client';
import type { DocumentProcessingStatus } from '@verdin/shared';
import { Button, Card } from '@verdin/ui';
import { DocumentProcessingBadge } from '../documents/DocumentProcessingBadge';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

function formatFileSize(bytes: number | null) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString();
}

function isProcessingStatus(value: string): value is DocumentProcessingStatus {
  return ['pending', 'queued', 'processing', 'completed', 'failed', 'skipped'].includes(value);
}

interface PortalCaseDocumentsProps {
  caseId: string;
}

export function PortalCaseDocuments({ caseId }: PortalCaseDocumentsProps) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const documentsQuery = useQuery({
    queryKey: ['portal-case-documents', caseId],
    queryFn: () => listPortalCaseDocuments(caseId),
  });

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!file || !title.trim()) {
        throw new Error('Title and file are required');
      }
      return uploadPortalCaseDocument(caseId, {
        file,
        title: title.trim(),
        description: description.trim() || null,
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['portal-case-documents', caseId] });
      setTitle('');
      setDescription('');
      setFile(null);
      setShowForm(false);
      setError(null);
    },
    onError: (err: Error) => setError(err.message),
  });

  const items = documentsQuery.data?.items ?? [];

  return (
    <div className="mt-8 border-t border-gray-200 pt-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
            Your documents
          </h2>
          <p className="mt-1 text-sm text-gray-600">
            Upload evidence and supporting files for this case.
          </p>
        </div>
        <Button
          type="button"
          variant="secondary"
          onClick={() => {
            setShowForm((current) => !current);
            setError(null);
          }}
        >
          {showForm ? 'Cancel upload' : 'Upload document'}
        </Button>
      </div>

      {showForm ? (
        <Card className="mt-4 p-6">
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              setError(null);
              uploadMutation.mutate();
            }}
          >
            <div>
              <label htmlFor="portal-doc-title" className="block text-sm font-medium text-gray-700">
                Title
              </label>
              <input
                id="portal-doc-title"
                className={inputClass}
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                required
              />
            </div>

            <div>
              <label
                htmlFor="portal-doc-description"
                className="block text-sm font-medium text-gray-700"
              >
                Description
              </label>
              <textarea
                id="portal-doc-description"
                rows={3}
                className={inputClass}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
              />
            </div>

            <div>
              <label htmlFor="portal-doc-file" className="block text-sm font-medium text-gray-700">
                File
              </label>
              <input
                id="portal-doc-file"
                type="file"
                className={inputClass}
                accept=".pdf,.jpg,.jpeg,.png,.tiff,.txt"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                required
              />
              <p className="mt-1 text-xs text-gray-500">PDF, JPG, PNG, TIFF, or TXT up to 25 MB.</p>
            </div>

            {error ? (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
            ) : null}

            <Button type="submit" loading={uploadMutation.isPending}>
              Submit document
            </Button>
          </form>
        </Card>
      ) : null}

      {documentsQuery.isLoading ? (
        <p className="mt-4 text-sm text-gray-500">Loading documents…</p>
      ) : null}

      {documentsQuery.isError ? (
        <p className="mt-4 text-sm text-red-600">
          Failed to load documents:{' '}
          {documentsQuery.error instanceof Error ? documentsQuery.error.message : 'Unknown error'}
        </p>
      ) : null}

      {!documentsQuery.isLoading && !documentsQuery.isError && items.length === 0 ? (
        <p className="mt-4 text-sm text-gray-500">
          No documents uploaded yet. Use Upload document to share files with your case team.
        </p>
      ) : null}

      {items.length > 0 ? (
        <ul className="mt-4 space-y-3">
          {items.map((document) => (
            <PortalDocumentRow key={document.id} document={document} />
          ))}
        </ul>
      ) : null}
    </div>
  );
}

function PortalDocumentRow({ document }: { document: PortalDocument }) {
  return (
    <li className="rounded-md border border-gray-200 px-4 py-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="font-medium text-gray-900">{document.title}</p>
          <p className="text-sm text-gray-500">{document.file_name}</p>
          {document.description ? (
            <p className="mt-1 text-sm text-gray-600">{document.description}</p>
          ) : null}
          <p className="mt-2 text-xs text-gray-400">
            Uploaded {formatDate(document.created_at)} · {formatFileSize(document.file_size)}
          </p>
        </div>
        {isProcessingStatus(document.processing_status) ? (
          <DocumentProcessingBadge status={document.processing_status} />
        ) : (
          <span className="text-sm capitalize text-gray-600">
            {document.processing_status.replace('_', ' ')}
          </span>
        )}
      </div>
    </li>
  );
}
