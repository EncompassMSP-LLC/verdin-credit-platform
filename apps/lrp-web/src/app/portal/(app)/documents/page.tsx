'use client';

import { useState, type ChangeEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { uploadPortalCaseDocument, uploadPortalCaseIdentityDocument } from '@verdin/api-client';
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
  const [uploadingId, setUploadingId] = useState(false);

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

  async function onIdUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !primary) return;
    setUploadingId(true);
    setError(null);
    setNotice(null);
    try {
      await uploadPortalCaseIdentityDocument(primary.id, { file });
      setNotice(`${file.name} saved as your photo ID for this case.`);
      await queryClient.invalidateQueries({ queryKey: ['portal', 'documents', primary.id] });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Photo ID upload failed.');
    } finally {
      setUploadingId(false);
      event.target.value = '';
    }
  }

  return (
    <div>
      <PageHeader
        eyebrow="Documents"
        title="Documents"
        description="Upload your photo ID and supporting files requested for your readiness file. Do not upload others’ documents."
        actions={
          <label
            className={`inline-flex cursor-pointer rounded-brand border border-navy-900/15 bg-white px-4 py-2.5 text-sm font-semibold uppercase tracking-wide text-navy-900 hover:bg-sand-50 dark:border-white/15 dark:bg-navy-900 dark:text-white ${
              !primary || uploading ? 'pointer-events-none opacity-50' : ''
            }`}
          >
            {uploading ? 'Uploading…' : 'Upload other file'}
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
        title="Photo ID / driver’s license"
        description="Required for dispute mail packets. Clear photo or scan of a government-issued ID."
        className="mb-6"
      >
        <label
          className={`inline-flex cursor-pointer rounded-brand bg-gold-500 px-4 py-2.5 text-sm font-semibold uppercase tracking-wide text-navy-900 hover:bg-gold-400 ${
            !primary || uploadingId ? 'pointer-events-none opacity-50' : ''
          }`}
        >
          {uploadingId ? 'Uploading ID…' : 'Upload photo ID'}
          <input
            type="file"
            className="sr-only"
            accept=".pdf,.jpg,.jpeg,.png,.heic,.webp"
            capture="environment"
            onChange={onIdUpload}
            disabled={!primary || uploadingId}
          />
        </label>
      </PortalCard>

      <PortalCard
        title={primary ? `Case: ${primary.title}` : 'Documents'}
        description="Source: GET/POST /portal/cases/{id}/documents · POST …/identity-document"
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
                  <th className="px-2 py-3 font-semibold">Type</th>
                  <th className="px-2 py-3 font-semibold">Size</th>
                  <th className="px-2 py-3 font-semibold">Status</th>
                  <th className="px-2 py-3 font-semibold">Uploaded</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-900/5 dark:divide-white/5">
                {docsQuery.data.map((doc) => (
                  <tr key={doc.id}>
                    <td className="px-2 py-3">
                      <p className="font-medium text-navy-900 dark:text-white">{doc.title}</p>
                      <p className="text-xs text-slate-500">{doc.file_name}</p>
                    </td>
                    <td className="px-2 py-3 text-xs text-slate-600 dark:text-white/70">
                      {doc.document_type === 'identity_document' ? 'Photo ID' : 'Supporting'}
                    </td>
                    <td className="px-2 py-3 text-slate-600 dark:text-white/70">
                      {formatBytes(doc.file_size)}
                    </td>
                    <td className="px-2 py-3">
                      <StatusPill tone="neutral">{doc.processing_status}</StatusPill>
                    </td>
                    <td className="px-2 py-3 text-slate-600 dark:text-white/70">
                      {formatDate(doc.created_at)}
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
