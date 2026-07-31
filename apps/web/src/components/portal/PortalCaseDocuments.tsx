import { useId, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  listPortalCaseDocuments,
  uploadPortalCaseDocument,
  uploadPortalCaseIdentityDocument,
  uploadPortalCaseProofOfAddressDocument,
  type PortalDocument,
} from '@verdin/api-client';
import type { DocumentProcessingStatus } from '@verdin/shared';
import { Button, Card } from '@verdin/ui';
import { useTranslation } from 'react-i18next';
import { DocumentProcessingBadge } from '../documents/DocumentProcessingBadge';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

function formatFileSize(bytes: number | null, empty: string) {
  if (!bytes) return empty;
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value: string, locale: string) {
  return new Date(value).toLocaleDateString(locale);
}

function isProcessingStatus(value: string): value is DocumentProcessingStatus {
  return ['pending', 'queued', 'processing', 'completed', 'failed', 'skipped'].includes(value);
}

function FileChooseControl({
  id,
  accept,
  capture,
  file,
  onChange,
  chooseLabel,
  noFileLabel,
}: {
  id: string;
  accept: string;
  capture?: boolean | 'user' | 'environment';
  file: File | null;
  onChange: (file: File | null) => void;
  chooseLabel: string;
  noFileLabel: string;
}) {
  return (
    <div className="mt-1 flex flex-wrap items-center gap-3">
      <input
        id={id}
        type="file"
        className="sr-only"
        accept={accept}
        capture={capture}
        onChange={(event) => onChange(event.target.files?.[0] ?? null)}
      />
      <Button
        type="button"
        variant="secondary"
        onClick={() => document.getElementById(id)?.click()}
      >
        {chooseLabel}
      </Button>
      <span className="text-sm text-gray-600">{file ? file.name : noFileLabel}</span>
    </div>
  );
}

interface PortalCaseDocumentsProps {
  caseId: string;
}

export function PortalCaseDocuments({ caseId }: PortalCaseDocumentsProps) {
  const { t, i18n } = useTranslation('portal');
  const { t: tCommon } = useTranslation('common');
  const queryClient = useQueryClient();
  const idInputId = useId();
  const addressInputId = useId();
  const otherFileInputId = useId();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [idFile, setIdFile] = useState<File | null>(null);
  const [addressFile, setAddressFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [idError, setIdError] = useState<string | null>(null);
  const [addressError, setAddressError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const documentsQuery = useQuery({
    queryKey: ['portal-case-documents', caseId],
    queryFn: () => listPortalCaseDocuments(caseId),
  });

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!file || !title.trim()) {
        throw new Error(t('documents.errors.titleAndFileRequired'));
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

  const idUploadMutation = useMutation({
    mutationFn: () => {
      if (!idFile) {
        throw new Error(t('documents.errors.idFileRequired'));
      }
      return uploadPortalCaseIdentityDocument(caseId, { file: idFile });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['portal-case-documents', caseId] });
      setIdFile(null);
      setIdError(null);
    },
    onError: (err: Error) => setIdError(err.message),
  });

  const addressUploadMutation = useMutation({
    mutationFn: () => {
      if (!addressFile) {
        throw new Error(t('documents.errors.addressFileRequired'));
      }
      return uploadPortalCaseProofOfAddressDocument(caseId, { file: addressFile });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['portal-case-documents', caseId] });
      setAddressFile(null);
      setAddressError(null);
    },
    onError: (err: Error) => setAddressError(err.message),
  });

  const items = documentsQuery.data?.items ?? [];
  const identityOnFile = Boolean(documentsQuery.data?.identity_document_on_file);
  const addressOnFile = Boolean(documentsQuery.data?.proof_of_address_on_file);

  return (
    <div className="mt-8 border-t border-gray-200 pt-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
            {t('documents.title')}
          </h2>
          <p className="mt-1 text-sm text-gray-600">{t('documents.subtitle')}</p>
        </div>
        <Button
          type="button"
          variant="secondary"
          onClick={() => {
            setShowForm((current) => !current);
            setError(null);
          }}
        >
          {showForm ? t('documents.cancelUpload') : t('documents.upload')}
        </Button>
      </div>

      <Card className="mt-4 p-6">
        <div>
          <h3 className="text-base font-semibold text-gray-900">{t('documents.idTitle')}</h3>
          <p className="mt-1 text-sm text-gray-600">{t('documents.idSubtitle')}</p>
          {identityOnFile ? (
            <p className="mt-2 text-sm font-medium text-emerald-700">{t('documents.idOnFile')}</p>
          ) : (
            <p className="mt-2 text-sm text-amber-700">{t('documents.idNeeded')}</p>
          )}
        </div>
        <form
          className="mt-4 space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            setIdError(null);
            idUploadMutation.mutate();
          }}
        >
          <div>
            <p className="block text-sm font-medium text-gray-700">{t('documents.idFileLabel')}</p>
            <FileChooseControl
              id={idInputId}
              accept=".pdf,.jpg,.jpeg,.png,.heic,.webp"
              capture="environment"
              file={idFile}
              onChange={setIdFile}
              chooseLabel={t('documents.chooseFile')}
              noFileLabel={t('documents.noFileChosen')}
            />
            <p className="mt-1 text-xs text-gray-500">{t('documents.idFileHint')}</p>
          </div>
          {idError ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{idError}</div>
          ) : null}
          <Button type="submit" loading={idUploadMutation.isPending} disabled={!idFile}>
            {identityOnFile ? t('documents.idReplaceSubmit') : t('documents.idSubmit')}
          </Button>
        </form>
      </Card>

      <Card className="mt-4 p-6">
        <div>
          <h3 className="text-base font-semibold text-gray-900">{t('documents.addressTitle')}</h3>
          <p className="mt-1 text-sm text-gray-600">{t('documents.addressSubtitle')}</p>
          {addressOnFile ? (
            <p className="mt-2 text-sm font-medium text-emerald-700">
              {t('documents.addressOnFile')}
            </p>
          ) : (
            <p className="mt-2 text-sm text-amber-700">{t('documents.addressNeeded')}</p>
          )}
        </div>
        <form
          className="mt-4 space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            setAddressError(null);
            addressUploadMutation.mutate();
          }}
        >
          <div>
            <p className="block text-sm font-medium text-gray-700">
              {t('documents.addressFileLabel')}
            </p>
            <FileChooseControl
              id={addressInputId}
              accept=".pdf,.jpg,.jpeg,.png,.heic,.webp"
              capture="environment"
              file={addressFile}
              onChange={setAddressFile}
              chooseLabel={t('documents.chooseFile')}
              noFileLabel={t('documents.noFileChosen')}
            />
            <p className="mt-1 text-xs text-gray-500">{t('documents.addressFileHint')}</p>
          </div>
          {addressError ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{addressError}</div>
          ) : null}
          <Button type="submit" loading={addressUploadMutation.isPending} disabled={!addressFile}>
            {addressOnFile ? t('documents.addressReplaceSubmit') : t('documents.addressSubmit')}
          </Button>
        </form>
      </Card>

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
                {t('documents.titleLabel')}
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
                {t('documents.descriptionLabel')}
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
              <p className="block text-sm font-medium text-gray-700">{t('documents.fileLabel')}</p>
              <FileChooseControl
                id={otherFileInputId}
                accept=".pdf,.jpg,.jpeg,.png,.tiff,.txt"
                file={file}
                onChange={setFile}
                chooseLabel={t('documents.chooseFile')}
                noFileLabel={t('documents.noFileChosen')}
              />
              <p className="mt-1 text-xs text-gray-500">{t('documents.fileHint')}</p>
            </div>

            {error ? (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
            ) : null}

            <Button type="submit" loading={uploadMutation.isPending} disabled={!file}>
              {t('documents.submit')}
            </Button>
          </form>
        </Card>
      ) : null}

      {documentsQuery.isLoading ? (
        <p className="mt-4 text-sm text-gray-500">{t('documents.loading')}</p>
      ) : null}

      {documentsQuery.isError ? (
        <p className="mt-4 text-sm text-red-600">
          {t('documents.loadError')}:{' '}
          {documentsQuery.error instanceof Error
            ? documentsQuery.error.message
            : tCommon('unknownError')}
        </p>
      ) : null}

      {!documentsQuery.isLoading && !documentsQuery.isError && items.length === 0 ? (
        <p className="mt-4 text-sm text-gray-500">{t('documents.empty')}</p>
      ) : null}

      {items.length > 0 ? (
        <ul className="mt-4 space-y-3">
          {items.map((document) => (
            <PortalDocumentRow
              key={document.id}
              document={document}
              locale={i18n.language}
              emptySize={tCommon('emDash')}
              photoIdLabel={t('documents.photoIdBadge')}
              addressLabel={t('documents.addressBadge')}
              uploadedLabel={(date, size) => t('documents.uploaded', { date, size })}
            />
          ))}
        </ul>
      ) : null}
    </div>
  );
}

function PortalDocumentRow({
  document,
  locale,
  emptySize,
  photoIdLabel,
  addressLabel,
  uploadedLabel,
}: {
  document: PortalDocument;
  locale: string;
  emptySize: string;
  photoIdLabel: string;
  addressLabel: string;
  uploadedLabel: (date: string, size: string) => string;
}) {
  const badge =
    document.document_type === 'identity_document'
      ? photoIdLabel
      : document.document_type === 'proof_of_address'
        ? addressLabel
        : null;
  return (
    <li className="rounded-md border border-gray-200 px-4 py-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <p className="font-medium text-gray-900">{document.title}</p>
            {badge ? (
              <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
                {badge}
              </span>
            ) : null}
          </div>
          <p className="text-sm text-gray-500">{document.file_name}</p>
          {document.description ? (
            <p className="mt-1 text-sm text-gray-600">{document.description}</p>
          ) : null}
          <p className="mt-2 text-xs text-gray-400">
            {uploadedLabel(
              formatDate(document.created_at, locale),
              formatFileSize(document.file_size, emptySize),
            )}
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
