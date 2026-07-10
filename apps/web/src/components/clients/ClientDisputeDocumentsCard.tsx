import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  listCases,
  uploadClientIdentityDocument,
  uploadClientProofOfAddressDocument,
} from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

const fileAccept = 'application/pdf,image/jpeg,image/png,image/tiff';

interface ClientDisputeDocumentsCardProps {
  clientId: string;
  identityDocumentId: string | null;
  proofOfAddressDocumentId: string | null;
}

function DocumentStatus({ onFile }: { onFile: boolean }) {
  return (
    <span
      className={
        onFile
          ? 'rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700'
          : 'rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600'
      }
    >
      {onFile ? 'On file' : 'Not uploaded'}
    </span>
  );
}

export function ClientDisputeDocumentsCard({
  clientId,
  identityDocumentId,
  proofOfAddressDocumentId,
}: ClientDisputeDocumentsCardProps) {
  const queryClient = useQueryClient();
  const [documentCaseId, setDocumentCaseId] = useState('');
  const [identityFile, setIdentityFile] = useState<File | null>(null);
  const [proofOfAddressFile, setProofOfAddressFile] = useState<File | null>(null);
  const [identityError, setIdentityError] = useState<string | null>(null);
  const [proofError, setProofError] = useState<string | null>(null);
  const [identitySuccess, setIdentitySuccess] = useState<string | null>(null);
  const [proofSuccess, setProofSuccess] = useState<string | null>(null);

  const clientCasesQuery = useQuery({
    queryKey: ['client-cases', clientId],
    queryFn: () => listCases({ client_id: clientId, page_size: 50 }),
  });

  const cases = clientCasesQuery.data?.items ?? [];
  const canUpload = Boolean(documentCaseId);

  const invalidateClient = () => {
    void queryClient.invalidateQueries({ queryKey: ['client', clientId] });
    void queryClient.invalidateQueries({ queryKey: ['clients'] });
  };

  const identityUploadMutation = useMutation({
    mutationFn: () => {
      if (!documentCaseId || !identityFile) {
        throw new Error('Select a case and choose a file first.');
      }
      return uploadClientIdentityDocument(
        clientId,
        documentCaseId,
        identityFile,
        "Driver's license",
      );
    },
    onSuccess: () => {
      setIdentityFile(null);
      setIdentityError(null);
      setIdentitySuccess("Driver's license uploaded.");
      invalidateClient();
    },
    onError: (err: Error) => {
      setIdentitySuccess(null);
      setIdentityError(err.message);
    },
  });

  const proofUploadMutation = useMutation({
    mutationFn: () => {
      if (!documentCaseId || !proofOfAddressFile) {
        throw new Error('Select a case and choose a file first.');
      }
      return uploadClientProofOfAddressDocument(
        clientId,
        documentCaseId,
        proofOfAddressFile,
        'Proof of mailing address',
      );
    },
    onSuccess: () => {
      setProofOfAddressFile(null);
      setProofError(null);
      setProofSuccess('Proof of mailing address uploaded.');
      invalidateClient();
    },
    onError: (err: Error) => {
      setProofSuccess(null);
      setProofError(err.message);
    },
  });

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-gray-900">Dispute mail packet documents</h2>
      <p className="mt-2 text-sm text-gray-600">
        Upload a government-issued photo ID and proof of current mailing address. These attach
        automatically when you export dispute mail packets.
      </p>

      {clientCasesQuery.isLoading ? (
        <p className="mt-4 text-sm text-gray-500">Loading cases…</p>
      ) : cases.length === 0 ? (
        <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <p>This client has no cases yet. Create a case before uploading documents.</p>
          <Link
            to={`/cases/new?client_id=${clientId}`}
            className="mt-2 inline-block font-medium text-brand-600 hover:underline"
          >
            Create a case for this client →
          </Link>
        </div>
      ) : (
        <div className="mt-4 space-y-5">
          <div>
            <label className="text-sm font-medium text-gray-700">Case</label>
            <p className="mt-1 text-xs text-gray-500">
              Documents are stored on the client and linked to the selected case.
            </p>
            <select
              className={inputClass}
              value={documentCaseId}
              onChange={(event) => {
                setDocumentCaseId(event.target.value);
                setIdentitySuccess(null);
                setProofSuccess(null);
              }}
            >
              <option value="">Select a case…</option>
              {cases.map((caseItem) => (
                <option key={caseItem.id} value={caseItem.id}>
                  {caseItem.title}
                </option>
              ))}
            </select>
          </div>

          <div className="rounded-md border border-gray-200 bg-gray-50 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <label className="text-sm font-medium text-gray-700">
                Driver&apos;s license copy
              </label>
              <DocumentStatus onFile={Boolean(identityDocumentId)} />
            </div>
            <input
              type="file"
              accept={fileAccept}
              className="mt-3 block w-full text-sm text-gray-700"
              disabled={!canUpload}
              onChange={(event) => {
                setIdentityFile(event.target.files?.[0] ?? null);
                setIdentitySuccess(null);
                setIdentityError(null);
              }}
            />
            {identityError ? <p className="mt-2 text-sm text-red-600">{identityError}</p> : null}
            {identitySuccess ? (
              <p className="mt-2 text-sm text-green-700">{identitySuccess}</p>
            ) : null}
            <Button
              type="button"
              className="mt-3"
              disabled={!canUpload || !identityFile || identityUploadMutation.isPending}
              onClick={() => identityUploadMutation.mutate()}
            >
              {identityUploadMutation.isPending ? 'Uploading…' : 'Upload ID'}
            </Button>
          </div>

          <div className="rounded-md border border-gray-200 bg-gray-50 p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <label className="text-sm font-medium text-gray-700">
                Proof of current mailing address
              </label>
              <DocumentStatus onFile={Boolean(proofOfAddressDocumentId)} />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Utility bill, bank statement, or other document showing the consumer&apos;s current
              address.
            </p>
            <input
              type="file"
              accept={fileAccept}
              className="mt-3 block w-full text-sm text-gray-700"
              disabled={!canUpload}
              onChange={(event) => {
                setProofOfAddressFile(event.target.files?.[0] ?? null);
                setProofSuccess(null);
                setProofError(null);
              }}
            />
            {proofError ? <p className="mt-2 text-sm text-red-600">{proofError}</p> : null}
            {proofSuccess ? <p className="mt-2 text-sm text-green-700">{proofSuccess}</p> : null}
            <Button
              type="button"
              className="mt-3"
              disabled={!canUpload || !proofOfAddressFile || proofUploadMutation.isPending}
              onClick={() => proofUploadMutation.mutate()}
            >
              {proofUploadMutation.isPending ? 'Uploading…' : 'Upload proof of address'}
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
}
