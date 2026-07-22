'use client';

import { useState, type ChangeEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { uploadPortalCaseDocument } from '@verdin/api-client';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { usePrimaryCase, usePortalDocuments } from '@/lib/platform/hooks';
import { formatDate } from '@/lib/utils';

function formatBytes(value: number | null) {
  if (!value) return '—';
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${Math.round(value / 1024)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const { primary, isLoading: casesLoading } = usePrimaryCase();
  const docsQuery = usePortalDocuments(primary?.id);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  async function onUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !primary) return;
    setUploading(true);
    setError(null);
    setNotice(null);
    try {
      await uploadPortalCaseDocument(primary.id, {
        file,
        title: file.name.replace(/\.[^.]+$/, ''),
        description: 'Uploaded from LRP Borrower Portal',
      });
      setNotice(`${file.name} uploaded to your case on the shared platform.`);
      await queryClient.invalidateQueries({ queryKey: ['portal', 'documents', primary.id] });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Documents"
        title="Secure document vault"
        description="Files are stored on the Ultimate Credit Repair platform document store for your linked case."
        actions={
          <label
            className={`inline-flex cursor-pointer rounded-brand bg-gold-500 px-4 py-2.5 text-sm font-semibold uppercase tracking-wide text-navy-900 hover:bg-gold-400 ${
              !primary || uploading ? 'pointer-events-none opacity-50' : ''
            }`}
          >
            {uploading ? 'Uploading…' : 'Upload document'}
            <input
              type="file"
              className="sr-only"
              onChange={onUpload}
              disabled={!primary || uploading}
            />
          </label>
        }
      />

      {!primary && !casesLoading ? (
        <p className="mb-4 rounded-brand border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning">
          No case is available for document upload yet.
        </p>
      ) : null}
      {notice ? (
        <p className="mb-4 rounded-brand border border-emerald-600/30 bg-emerald-600/10 px-4 py-3 text-sm text-emerald-800 dark:text-emerald-300">
          {notice}
        </p>
      ) : null}
      {error ? (
        <p className="mb-4 rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
          {error}
        </p>
      ) : null}

      <PortalCard
        title={primary ? `Case: ${primary.title}` : 'Documents'}
        description="Source: GET/POST /portal/cases/{id}/documents"
      >
        {docsQuery.isLoading || casesLoading ? (
          <p className="text-sm text-slate-500">Loading documents…</p>
        ) : !docsQuery.data?.length ? (
          <p className="text-sm text-slate-500">No documents on this case yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-navy-900/10 text-xs uppercase tracking-wider text-slate-500 dark:border-white/10">
                <tr>
                  <th className="px-2 py-3 font-semibold">Document</th>
                  <th className="px-2 py-3 font-semibold">File</th>
                  <th className="px-2 py-3 font-semibold">Uploaded</th>
                  <th className="px-2 py-3 font-semibold">Size</th>
                  <th className="px-2 py-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-900/8 dark:divide-white/10">
                {docsQuery.data.map((doc) => (
                  <tr key={doc.id}>
                    <td className="px-2 py-3 font-medium">{doc.title}</td>
                    <td className="px-2 py-3 text-slate-500">{doc.file_name}</td>
                    <td className="px-2 py-3 text-slate-500">{formatDate(doc.created_at)}</td>
                    <td className="px-2 py-3 text-slate-500">{formatBytes(doc.file_size)}</td>
                    <td className="px-2 py-3">
                      <StatusPill tone={doc.processing_status === 'completed' ? 'good' : 'info'}>
                        {doc.processing_status}
                      </StatusPill>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </PortalCard>
    </div>
  );
}
