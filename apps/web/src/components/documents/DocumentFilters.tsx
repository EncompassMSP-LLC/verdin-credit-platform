import type { ClassificationStatus, DocumentType } from '@verdin/shared';
import {
  DOCUMENT_TYPES,
  DOCUMENT_TYPE_LABELS,
  CLASSIFICATION_STATUSES,
  CLASSIFICATION_STATUS_LABELS,
} from '@verdin/shared';

export interface DocumentFiltersValue {
  search: string;
  case_id: string;
  is_duplicate: '' | 'true';
  processing_status: '' | 'pending' | 'queued' | 'processing' | 'completed' | 'failed' | 'skipped';
  document_type: '' | DocumentType;
  classification_status: '' | ClassificationStatus;
  sort_by: string;
  sort_order: 'asc' | 'desc';
}

interface DocumentFiltersProps {
  value: DocumentFiltersValue;
  onChange: (value: DocumentFiltersValue) => void;
}

const inputClass =
  'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function DocumentFilters({ value, onChange }: DocumentFiltersProps) {
  const update = (patch: Partial<DocumentFiltersValue>) => onChange({ ...value, ...patch });

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-6">
      <div className="lg:col-span-2">
        <label htmlFor="doc-search" className="mb-1 block text-sm font-medium text-gray-700">
          Search
        </label>
        <input
          id="doc-search"
          type="search"
          placeholder="Title, file name..."
          className={inputClass}
          value={value.search}
          onChange={(e) => update({ search: e.target.value })}
        />
      </div>
      <div>
        <label htmlFor="doc-duplicate" className="mb-1 block text-sm font-medium text-gray-700">
          Duplicate filter
        </label>
        <select
          id="doc-duplicate"
          className={inputClass}
          value={value.is_duplicate}
          onChange={(e) => update({ is_duplicate: e.target.value as '' | 'true' })}
        >
          <option value="">All documents</option>
          <option value="true">Duplicates only</option>
        </select>
      </div>
      <div>
        <label htmlFor="doc-ocr" className="mb-1 block text-sm font-medium text-gray-700">
          OCR status
        </label>
        <select
          id="doc-ocr"
          className={inputClass}
          value={value.processing_status}
          onChange={(e) =>
            update({
              processing_status: e.target.value as DocumentFiltersValue['processing_status'],
            })
          }
        >
          <option value="">All statuses</option>
          <option value="queued">Queued</option>
          <option value="processing">Processing</option>
          <option value="completed">OCR complete</option>
          <option value="failed">OCR failed</option>
          <option value="skipped">Skipped</option>
        </select>
      </div>
      <div>
        <label htmlFor="doc-type" className="mb-1 block text-sm font-medium text-gray-700">
          Document type
        </label>
        <select
          id="doc-type"
          className={inputClass}
          value={value.document_type}
          onChange={(e) => update({ document_type: e.target.value as '' | DocumentType })}
        >
          <option value="">All types</option>
          {DOCUMENT_TYPES.map((type) => (
            <option key={type} value={type}>
              {DOCUMENT_TYPE_LABELS[type]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label
          htmlFor="doc-classification"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          Classification
        </label>
        <select
          id="doc-classification"
          className={inputClass}
          value={value.classification_status}
          onChange={(e) =>
            update({
              classification_status: e.target.value as '' | ClassificationStatus,
            })
          }
        >
          <option value="">All</option>
          {CLASSIFICATION_STATUSES.map((status) => (
            <option key={status} value={status}>
              {CLASSIFICATION_STATUS_LABELS[status]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="doc-sort" className="mb-1 block text-sm font-medium text-gray-700">
          Sort
        </label>
        <select
          id="doc-sort"
          className={inputClass}
          value={`${value.sort_by}:${value.sort_order}`}
          onChange={(e) => {
            const [sort_by, sort_order] = e.target.value.split(':');
            update({ sort_by, sort_order: sort_order as 'asc' | 'desc' });
          }}
        >
          <option value="created_at:desc">Newest first</option>
          <option value="title:asc">Title A–Z</option>
          <option value="file_size:desc">Largest first</option>
        </select>
      </div>
    </div>
  );
}
