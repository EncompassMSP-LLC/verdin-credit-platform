import type { Document, DocumentDuplicateGroup } from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';

function formatFileSize(bytes: number | null) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

export function hasDocumentDuplicates(
  currentDocument: Document,
  duplicateGroup?: DocumentDuplicateGroup,
): boolean {
  return currentDocument.is_duplicate || (duplicateGroup?.duplicate_count ?? 0) > 0;
}

export function DocumentDuplicateAlert({
  currentDocument,
  duplicateGroup,
}: {
  currentDocument: Document;
  duplicateGroup?: DocumentDuplicateGroup;
}) {
  if (!duplicateGroup || !hasDocumentDuplicates(currentDocument, duplicateGroup)) {
    return null;
  }

  return (
    <div className="rounded-md border border-yellow-200 bg-yellow-50 p-3 text-sm text-yellow-900">
      {currentDocument.is_duplicate ? (
        <p>
          This file is an exact duplicate of{' '}
          <Link
            to={`/documents/${duplicateGroup.canonical_document.id}`}
            className="font-medium text-yellow-950 underline"
          >
            {duplicateGroup.canonical_document.title}
          </Link>
          . Review the original import before creating accounts or disputes from this copy.
        </p>
      ) : (
        <p>
          This is the canonical copy for {duplicateGroup.duplicate_count} duplicate re-import
          {duplicateGroup.duplicate_count === 1 ? '' : 's'}. Staff may have uploaded the same PDF
          more than once.
        </p>
      )}
      <p className="mt-2">
        <Link
          to={`/documents/${currentDocument.id}`}
          className="font-medium text-yellow-950 underline"
        >
          Open duplicate review
        </Link>
      </p>
    </div>
  );
}

function DuplicateDocumentRow({ document, label }: { document: Document; label: string }) {
  return (
    <li className="flex items-start justify-between gap-3 py-3">
      <div>
        <div className="flex items-center gap-2">
          <Badge variant={label === 'Canonical' ? 'success' : 'warning'}>{label}</Badge>
          <Link
            to={`/documents/${document.id}`}
            className="font-medium text-brand-600 hover:underline"
          >
            {document.title}
          </Link>
        </div>
        <p className="mt-1 text-gray-500">
          {document.file_name} · {formatFileSize(document.file_size)} ·{' '}
          {formatDateTime(document.created_at)}
        </p>
      </div>
      <Badge variant="info">v{document.version_number}</Badge>
    </li>
  );
}

export function DocumentDuplicatePanel({
  currentDocument,
  duplicateGroup,
  className,
}: {
  currentDocument: Document;
  duplicateGroup?: DocumentDuplicateGroup;
  className?: string;
}) {
  if (!duplicateGroup || !hasDocumentDuplicates(currentDocument, duplicateGroup)) {
    return null;
  }

  return (
    <Card title="Duplicate review" className={className}>
      <DocumentDuplicateAlert currentDocument={currentDocument} duplicateGroup={duplicateGroup} />
      <ul className="mt-3 divide-y divide-gray-100">
        <DuplicateDocumentRow document={duplicateGroup.canonical_document} label="Canonical" />
        {duplicateGroup.duplicate_documents.map((document) => (
          <DuplicateDocumentRow key={document.id} document={document} label="Duplicate" />
        ))}
      </ul>
    </Card>
  );
}
