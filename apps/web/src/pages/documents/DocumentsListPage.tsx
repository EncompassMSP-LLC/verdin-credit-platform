import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listDocuments } from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import {
  DocumentFilters,
  type DocumentFiltersValue,
} from '../../components/documents/DocumentFilters';
import { DocumentProcessingBadge } from '../../components/documents/DocumentProcessingBadge';

const defaultFilters: DocumentFiltersValue = {
  search: '',
  case_id: '',
  is_duplicate: '',
  processing_status: '',
  sort_by: 'created_at',
  sort_order: 'desc',
};

function formatFileSize(bytes: number | null) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString();
}

export function DocumentsListPage() {
  const [filters, setFilters] = useState<DocumentFiltersValue>(defaultFilters);
  const [page, setPage] = useState(1);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      search: filters.search || undefined,
      case_id: filters.case_id || undefined,
      is_duplicate: filters.is_duplicate === 'true' ? true : undefined,
      processing_status: filters.processing_status || undefined,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
    }),
    [filters, page],
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['documents', queryParams],
    queryFn: () => listDocuments(queryParams),
  });

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="mt-1 text-gray-500">Secure document library for case evidence.</p>
        </div>
        <Link to="/documents/upload">
          <Button>Upload document</Button>
        </Link>
      </div>

      <Card className="mb-6">
        <DocumentFilters
          value={filters}
          onChange={(next) => {
            setFilters(next);
            setPage(1);
          }}
        />
      </Card>

      {isLoading ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading documents...</p>
        </Card>
      ) : null}

      {isError ? (
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Failed to load documents'}
            </p>
            <Button variant="secondary" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </Card>
      ) : null}

      {!isLoading && !isError && data?.items.length === 0 ? (
        <Card>
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">No documents found.</p>
            <Link to="/documents/upload" className="mt-4 inline-block">
              <Button>Upload your first document</Button>
            </Link>
          </div>
        </Card>
      ) : null}

      {data && data.items.length > 0 ? (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="px-4 py-3 font-medium">Title</th>
                  <th className="px-4 py-3 font-medium">File</th>
                  <th className="px-4 py-3 font-medium">Size</th>
                  <th className="px-4 py-3 font-medium">Version</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Uploaded</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.items.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="font-medium text-brand-600 hover:underline"
                      >
                        {doc.title}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-gray-700">{doc.file_name}</td>
                    <td className="px-4 py-3 text-gray-700">{formatFileSize(doc.file_size)}</td>
                    <td className="px-4 py-3 text-gray-700">v{doc.version_number}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {doc.is_duplicate ? (
                          <Badge variant="warning">Duplicate</Badge>
                        ) : (
                          <Badge variant="success">Original</Badge>
                        )}
                        <DocumentProcessingBadge status={doc.processing_status} />
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-700">{formatDate(doc.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.pages > 1 ? (
            <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-4">
              <p className="text-sm text-gray-500">
                Page {data.page} of {data.pages} ({data.total} total)
              </p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page >= data.pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          ) : null}
        </Card>
      ) : null}
    </div>
  );
}
