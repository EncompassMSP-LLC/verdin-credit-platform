'use client';

import { useRef, useState } from 'react';
import { ApiClientError } from '@verdin/api-client';
import { formatDate } from '@/lib/utils';
import {
  downloadCrmDocument,
  useCrmCaseDocuments,
  useCrmUploadCaseDocument,
} from '@/lib/crm/document-hooks';

type Props = {
  caseId: string | undefined;
  canUpload: boolean;
};

export function CrmCaseDocumentsPanel({ caseId, canUpload }: Props) {
  const docsQuery = useCrmCaseDocuments(caseId);
  const uploadMutation = useCrmUploadCaseDocument(caseId);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const uploadError =
    uploadMutation.error instanceof ApiClientError
      ? uploadMutation.error.message
      : uploadMutation.error
        ? 'Upload failed.'
        : null;

  if (!caseId) {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Documents</h2>
        <p className="mt-2 text-sm text-amber-800">Link a case before managing documents.</p>
      </div>
    );
  }

  const items = docsQuery.data?.items ?? [];

  return (
    <div className="rounded-md border border-navy-900/10 bg-white p-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold">Documents</h2>
          <p className="mt-1 text-xs text-slate-500">
            Case-linked files from the platform Documents module.
          </p>
        </div>
        {canUpload ? (
          <>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={(event) => {
                const file = event.target.files?.[0];
                event.target.value = '';
                if (!file) return;
                uploadMutation.mutate({ file });
              }}
            />
            <button
              type="button"
              className="shrink-0 rounded-md bg-navy-900 px-2.5 py-1.5 text-xs font-medium text-white disabled:opacity-60"
              disabled={uploadMutation.isPending}
              onClick={() => fileInputRef.current?.click()}
            >
              {uploadMutation.isPending ? 'Uploading…' : 'Upload'}
            </button>
          </>
        ) : null}
      </div>

      {docsQuery.isLoading ? (
        <p className="mt-3 text-sm text-slate-500">Loading documents…</p>
      ) : null}
      {docsQuery.isError ? (
        <p className="mt-3 text-sm text-red-700">Could not load case documents.</p>
      ) : null}
      {uploadError ? <p className="mt-2 text-sm text-red-700">{uploadError}</p> : null}
      {downloadError ? <p className="mt-2 text-sm text-red-700">{downloadError}</p> : null}
      {uploadMutation.isSuccess ? (
        <p className="mt-2 text-sm text-teal-800">Uploaded {uploadMutation.data.title}.</p>
      ) : null}

      {!docsQuery.isLoading && !docsQuery.isError ? (
        <ul className="mt-3 space-y-2 text-sm">
          {items.length ? (
            items.map((doc) => (
              <li
                key={doc.id}
                className="flex items-start justify-between gap-2 border-b border-navy-900/8 pb-2 last:border-0"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium">{doc.title}</p>
                  <p className="text-xs text-slate-500">
                    {doc.file_name} · {doc.processing_status.replace(/_/g, ' ')}
                    {doc.updated_at ? ` · ${formatDate(doc.updated_at)}` : ''}
                  </p>
                </div>
                <button
                  type="button"
                  className="shrink-0 text-xs font-medium text-gold-700 hover:underline"
                  onClick={async () => {
                    setDownloadError(null);
                    try {
                      await downloadCrmDocument(doc);
                    } catch {
                      setDownloadError('Could not download document.');
                    }
                  }}
                >
                  Download
                </button>
              </li>
            ))
          ) : (
            <li className="text-slate-500">No documents on this case yet.</li>
          )}
        </ul>
      ) : null}
    </div>
  );
}
