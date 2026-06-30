import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { listCases, uploadDocument } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function DocumentUploadPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [caseId, setCaseId] = useState(searchParams.get('case_id') ?? '');
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const casesQuery = useQuery({
    queryKey: ['cases-for-document-upload'],
    queryFn: () => listCases({ page_size: 100 }),
  });

  const mutation = useMutation({
    mutationFn: () => {
      if (!file || !caseId || !title.trim()) {
        throw new Error('Title, case, and file are required');
      }
      return uploadDocument({
        file,
        title: title.trim(),
        case_id: caseId,
        description: description.trim() || null,
      });
    },
    onSuccess: (result) => navigate(`/documents/${result.id}`),
    onError: (err: Error) => setError(err.message),
  });

  return (
    <div className="p-8">
      <div className="mb-8">
        <Link to="/documents" className="text-sm text-brand-600 hover:underline">
          ← Back to documents
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-gray-900">Upload document</h1>
      </div>

      <Card className="max-w-2xl">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            setError(null);
            mutation.mutate();
          }}
        >
          <div>
            <label htmlFor="doc-title" className="block text-sm font-medium text-gray-700">
              Title
            </label>
            <input
              id="doc-title"
              className={inputClass}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="doc-case" className="block text-sm font-medium text-gray-700">
              Case
            </label>
            <select
              id="doc-case"
              className={inputClass}
              value={caseId}
              onChange={(e) => setCaseId(e.target.value)}
              required
            >
              <option value="">Select a case</option>
              {casesQuery.data?.items.map((caseItem) => (
                <option key={caseItem.id} value={caseItem.id}>
                  {caseItem.title} ({caseItem.client_name})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="doc-description" className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              id="doc-description"
              rows={3}
              className={inputClass}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="doc-file" className="block text-sm font-medium text-gray-700">
              File
            </label>
            <input
              id="doc-file"
              type="file"
              className={inputClass}
              accept=".pdf,.jpg,.jpeg,.png,.tiff,.txt"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              required
            />
            <p className="mt-1 text-xs text-gray-500">PDF, JPG, PNG, TIFF, or TXT up to 25 MB.</p>
          </div>

          {error ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          ) : null}

          <div className="flex gap-2 pt-2">
            <Button type="submit" loading={mutation.isPending}>
              Upload
            </Button>
            <Link to="/documents">
              <Button type="button" variant="secondary">
                Cancel
              </Button>
            </Link>
          </div>
        </form>
      </Card>
    </div>
  );
}
