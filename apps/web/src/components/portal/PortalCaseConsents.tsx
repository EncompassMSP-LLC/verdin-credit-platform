import { useEffect, useMemo, useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  downloadPortalConsentPreview,
  getAccessToken,
  listPortalCaseConsents,
  signPortalCaseConsent,
  type ConsentDocumentTemplateKey,
} from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { usePortalAuth } from '../../lib/portal-auth';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

const ATTESTATION_TEXT: Record<ConsentDocumentTemplateKey, string> = {
  croa_disclosure:
    'I have read the CROA disclosure statement above and acknowledge my right to cancel within three business days.',
  croa_service_agreement:
    'I have read and agree to the credit repair services agreement, including fees, services, and cancellation terms.',
  fcra_authorization:
    'I authorize the organization to obtain and dispute information in my consumer credit reports on my behalf.',
};

function openBlobInNewTab(blob: Blob) {
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank', 'noopener,noreferrer');
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

interface PortalCaseConsentsProps {
  caseId: string;
}

export function PortalCaseConsents({ caseId }: PortalCaseConsentsProps) {
  const queryClient = useQueryClient();
  const { isAuthenticated, isLoading: authLoading } = usePortalAuth();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [activeKey, setActiveKey] = useState<ConsentDocumentTemplateKey | null>(null);
  const [signerName, setSignerName] = useState('');
  const [attestationAccepted, setAttestationAccepted] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const authReady = isAuthenticated && !authLoading && Boolean(getAccessToken());

  const consentsQuery = useQuery({
    queryKey: ['portal-case-consents', caseId],
    queryFn: () => listPortalCaseConsents(caseId),
    enabled: authReady,
    retry: (failureCount, queryError) => {
      if (queryError instanceof ApiClientError && queryError.status === 401) {
        return failureCount < 2;
      }
      return failureCount < 1;
    },
  });

  const previewQuery = useQuery({
    queryKey: ['portal-consent-preview', caseId, activeKey],
    queryFn: () => downloadPortalConsentPreview(caseId, activeKey!),
    enabled: authReady && Boolean(activeKey),
  });

  const previewBlob = previewQuery.data?.blob ?? null;
  const previewObjectUrl = useMemo(
    () => (previewBlob ? URL.createObjectURL(previewBlob) : null),
    [previewBlob],
  );

  useEffect(() => {
    return () => {
      if (previewObjectUrl) {
        URL.revokeObjectURL(previewObjectUrl);
      }
    };
  }, [previewObjectUrl]);

  const signMutation = useMutation({
    mutationFn: async () => {
      if (!activeKey) throw new Error('Select a document to sign');
      if (!signerName.trim()) throw new Error('Enter your full legal name');
      if (!attestationAccepted) throw new Error('Accept the attestation to continue');

      let signatureFile: File | null = null;
      const canvas = canvasRef.current;
      if (canvas) {
        const blob = await new Promise<Blob | null>((resolve) =>
          canvas.toBlob((value) => resolve(value), 'image/png'),
        );
        if (blob && blob.size > 0) {
          signatureFile = new File([blob], 'signature.png', { type: 'image/png' });
        }
      }

      return signPortalCaseConsent(caseId, {
        template_key: activeKey,
        signer_name: signerName.trim(),
        attestation_accepted: true,
        signature_file: signatureFile,
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['portal-case-consents', caseId] });
      setSuccess('Document signed successfully. A PDF copy has been saved to your case file.');
      setError(null);
      setAttestationAccepted(false);
      setActiveKey(null);
      clearSignature();
    },
    onError: (err: Error) => {
      setSuccess(null);
      setError(err.message);
    },
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext('2d');
    if (!context) return;
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.strokeStyle = '#111827';
    context.lineWidth = 2;
    context.lineCap = 'round';
  }, [activeKey]);

  const getCanvasPoint = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
  };

  const startDrawing = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext('2d');
    if (!canvas || !context) return;
    const point = getCanvasPoint(event);
    context.beginPath();
    context.moveTo(point.x, point.y);
    setIsDrawing(true);
    canvas.setPointerCapture(event.pointerId);
  };

  const draw = (event: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    const context = canvas?.getContext('2d');
    if (!context) return;
    const point = getCanvasPoint(event);
    context.lineTo(point.x, point.y);
    context.stroke();
  };

  const stopDrawing = (event: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    canvas?.releasePointerCapture(event.pointerId);
    setIsDrawing(false);
  };

  const clearSignature = () => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext('2d');
    if (!canvas || !context) return;
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, canvas.width, canvas.height);
  };

  const items = consentsQuery.data?.items ?? [];
  const allSigned = items.length > 0 && items.every((item) => item.is_signed);
  const activeItem = items.find((item) => item.template_key === activeKey);

  return (
    <div className="mt-8 border-t border-gray-200 pt-8">
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
          Required agreements
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Review and sign each document below before dispute mail can be prepared for your case.
        </p>
        {consentsQuery.data?.legal_review_notice ? (
          <p className="mt-2 rounded-md bg-amber-50 p-3 text-xs text-amber-900">
            {consentsQuery.data.legal_review_notice}
          </p>
        ) : null}
      </div>

      {authLoading || (authReady && consentsQuery.isLoading) ? (
        <p className="mt-4 text-sm text-gray-500">Loading agreement status…</p>
      ) : null}

      {consentsQuery.isError ? (
        <div className="mt-4 space-y-3">
          <p className="text-sm text-red-600">Failed to load required agreements.</p>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={() => void consentsQuery.refetch()}
          >
            Retry
          </Button>
        </div>
      ) : null}

      {items.length > 0 ? (
        <ul className="mt-4 space-y-2">
          {items.map((item) => (
            <li
              key={item.template_key}
              className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-gray-200 px-4 py-3 text-sm"
            >
              <div>
                <span className="font-medium text-gray-900">{item.label}</span>
                <p className="text-xs text-gray-500">{item.title}</p>
              </div>
              <span
                className={
                  item.is_signed
                    ? 'rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700'
                    : 'rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-800'
                }
              >
                {item.is_signed ? 'Signed' : 'Required'}
              </span>
            </li>
          ))}
        </ul>
      ) : null}

      {allSigned ? (
        <p className="mt-4 text-sm text-green-700">
          All required agreements are on file. Your case team can proceed with dispute mail.
        </p>
      ) : (
        <Card className="mt-4 p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Document to sign</label>
              <select
                className={inputClass}
                value={activeKey ?? ''}
                onChange={(event) => {
                  setActiveKey((event.target.value || null) as ConsentDocumentTemplateKey | null);
                  setSuccess(null);
                  setError(null);
                }}
              >
                <option value="">Select document…</option>
                {items
                  .filter((item) => !item.is_signed)
                  .map((item) => (
                    <option key={item.template_key} value={item.template_key}>
                      {item.label}
                    </option>
                  ))}
              </select>
            </div>

            {activeKey ? (
              <div className="space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-medium text-gray-900">
                    {activeItem?.title ?? 'Document preview'}
                  </p>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    disabled={!previewQuery.data?.blob || previewQuery.isFetching}
                    onClick={() => {
                      if (previewQuery.data?.blob) {
                        openBlobInNewTab(previewQuery.data.blob);
                      }
                    }}
                  >
                    Open full PDF preview
                  </Button>
                </div>
                {previewQuery.isLoading || previewQuery.isFetching ? (
                  <p className="text-sm text-gray-500">Loading document preview…</p>
                ) : null}
                {previewQuery.isError ? (
                  <div className="space-y-2">
                    <p className="text-sm text-red-600">
                      {previewQuery.error instanceof Error
                        ? previewQuery.error.message
                        : 'Failed to load document preview.'}
                    </p>
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => void previewQuery.refetch()}
                    >
                      Retry preview
                    </Button>
                  </div>
                ) : null}
                {previewObjectUrl ? (
                  <iframe
                    title={`Preview ${activeItem?.title ?? activeKey}`}
                    src={previewObjectUrl}
                    className="h-96 w-full rounded-md border border-gray-300 bg-white"
                  />
                ) : null}
                <p className="rounded-md bg-gray-50 p-3 text-sm text-gray-700">
                  {ATTESTATION_TEXT[activeKey]}
                </p>
              </div>
            ) : null}

            <div>
              <label className="block text-sm font-medium text-gray-700">Full legal name</label>
              <input
                className={inputClass}
                value={signerName}
                onChange={(event) => setSignerName(event.target.value)}
                placeholder="Type your name as it appears on your ID"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Signature (optional)
              </label>
              <canvas
                ref={canvasRef}
                width={480}
                height={140}
                className="mt-2 w-full rounded-md border border-gray-300 bg-white touch-none"
                onPointerDown={startDrawing}
                onPointerMove={draw}
                onPointerUp={stopDrawing}
                onPointerLeave={stopDrawing}
              />
              <Button type="button" variant="secondary" className="mt-2" onClick={clearSignature}>
                Clear signature
              </Button>
            </div>

            <label className="flex items-start gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={attestationAccepted}
                onChange={(event) => setAttestationAccepted(event.target.checked)}
                className="mt-1"
              />
              <span>
                I have reviewed the document above and agree to sign electronically. A signed PDF
                will be generated and stored with my case.
              </span>
            </label>

            {error ? <p className="text-sm text-red-600">{error}</p> : null}
            {success ? <p className="text-sm text-green-700">{success}</p> : null}

            <Button
              type="button"
              disabled={!activeKey || signMutation.isPending}
              onClick={() => signMutation.mutate()}
            >
              {signMutation.isPending ? 'Signing…' : 'Sign document'}
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
