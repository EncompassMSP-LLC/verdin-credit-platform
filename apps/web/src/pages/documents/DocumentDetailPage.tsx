import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  deleteDocument,
  getDocument,
  getAccessToken,
  getDocumentDownloadUrl,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { DocumentDeleteDialog } from '../../components/documents/DocumentDeleteDialog';

function formatFileSize(bytes: number | null) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

export function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [deleteOpen, setDeleteOpen] = useState(false);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => getDocument(documentId!),
    enabled: Boolean(documentId),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteDocument(documentId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      navigate('/documents');
    },
  });

  if (!documentId) return null;

  if (isLoading) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading document...</p>
        </Card>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-8">
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Document not found'}
            </p>
            <Link
              to="/documents"
              className="mt-4 inline-block text-sm text-brand-600 hover:underline"
            >
              Back to documents
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  const downloadUrl = getDocumentDownloadUrl(documentId);
  const token = getAccessToken();

  const handleDownload = () => {
    if (!token) return;
    fetch(downloadUrl, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = data.file_name;
        anchor.click();
        URL.revokeObjectURL(url);
      });
  };

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/documents" className="text-sm text-brand-600 hover:underline">
            ← Back to documents
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{data.title}</h1>
          <p className="text-sm text-gray-500">{data.file_name}</p>
          <div className="mt-2 flex gap-2">
            {data.is_duplicate ? (
              <Badge variant="warning">Duplicate</Badge>
            ) : (
              <Badge variant="success">Original</Badge>
            )}
            <Badge variant="info">v{data.version_number}</Badge>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={handleDownload}>
            Download
          </Button>
          <Button variant="danger" onClick={() => setDeleteOpen(true)}>
            Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card title="Metadata" className="lg:col-span-1">
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-gray-500">File size</dt>
              <dd>{formatFileSize(data.file_size)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">MIME type</dt>
              <dd>{data.mime_type ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">SHA-256</dt>
              <dd className="break-all font-mono text-xs">{data.file_hash}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Uploaded</dt>
              <dd>{formatDateTime(data.created_at)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Case</dt>
              <dd>
                <Link to={`/cases/${data.case_id}`} className="text-brand-600 hover:underline">
                  View case
                </Link>
              </dd>
            </div>
          </dl>
          {data.description ? (
            <p className="mt-4 text-sm text-gray-600">{data.description}</p>
          ) : null}
        </Card>

        <Card title="Preview" className="lg:col-span-2">
          <div className="flex min-h-[240px] items-center justify-center rounded-md border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
            <div>
              <p className="text-sm font-medium text-gray-700">Preview coming in Milestone 2+</p>
              <p className="mt-1 text-sm text-gray-500">
                OCR and inline preview will be available after the document processing pipeline
                ships.
              </p>
            </div>
          </div>
        </Card>

        {data.versions && data.versions.length > 0 ? (
          <Card title="Version history" className="lg:col-span-3">
            <ul className="divide-y divide-gray-100">
              {data.versions.map((version) => (
                <li key={version.id} className="flex items-center justify-between py-3 text-sm">
                  <div>
                    <p className="font-medium text-gray-900">
                      v{version.version_number} — {version.file_name}
                    </p>
                    <p className="text-gray-500">{formatDateTime(version.created_at)}</p>
                  </div>
                  <p className="text-gray-600">{formatFileSize(version.file_size)}</p>
                </li>
              ))}
            </ul>
          </Card>
        ) : null}
      </div>

      <DocumentDeleteDialog
        title={data.title}
        open={deleteOpen}
        loading={deleteMutation.isPending}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteOpen(false)}
      />
    </div>
  );
}
