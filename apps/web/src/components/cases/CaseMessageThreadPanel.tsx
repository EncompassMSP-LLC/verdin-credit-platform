import { useId, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  caseMessageAttachmentDownloadUrl,
  deleteCaseMessageAttachment,
  getAccessToken,
  getCaseMessageThread,
  postCaseMessageThreadReply,
  uploadCaseMessageAttachment,
  type MessageAttachment,
  type ThreadMessage,
} from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

const ACCEPTED =
  '.pdf,.jpg,.jpeg,.png,.tif,.tiff,.doc,.docx,.txt,application/pdf,image/png,image/jpeg';

function formatTimestamp(value: string) {
  return new Date(value).toLocaleString();
}

interface CaseMessageThreadPanelProps {
  caseId: string;
}

export function CaseMessageThreadPanel({ caseId }: CaseMessageThreadPanelProps) {
  const queryClient = useQueryClient();
  const fileInputId = useId();
  const [body, setBody] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [pendingAttachments, setPendingAttachments] = useState<MessageAttachment[]>([]);
  const [uploading, setUploading] = useState(false);

  const threadQuery = useQuery({
    queryKey: ['case-message-thread', caseId],
    queryFn: () => getCaseMessageThread(caseId),
  });

  const hasPendingScan = pendingAttachments.some((a) => a.scan_status === 'pending');
  const hasRejected = pendingAttachments.some(
    (a) => a.scan_status === 'rejected' || a.scan_status === 'failed',
  );

  const sendMutation = useMutation({
    mutationFn: () => {
      const trimmed = body.trim();
      if (!trimmed) {
        throw new Error('Message cannot be empty');
      }
      if (hasPendingScan || hasRejected) {
        throw new Error('Resolve attachment scan issues before sending');
      }
      return postCaseMessageThreadReply(caseId, {
        body: trimmed,
        attachment_ids: pendingAttachments.map((item) => item.id),
        idempotency_key:
          typeof crypto !== 'undefined' && 'randomUUID' in crypto
            ? crypto.randomUUID()
            : `staff-${Date.now()}`,
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['case-message-thread', caseId] });
      setBody('');
      setPendingAttachments([]);
      setError(null);
    },
    onError: (err: Error) => setError(err.message),
  });

  async function onPickFile(fileList: FileList | null) {
    if (!fileList?.length) return;
    setUploading(true);
    setError(null);
    try {
      for (const file of Array.from(fileList)) {
        const uploaded = await uploadCaseMessageAttachment(caseId, file, file.name);
        setPendingAttachments((prev) => [...prev, uploaded]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Attachment upload failed');
    } finally {
      setUploading(false);
    }
  }

  async function removePending(attachmentId: string) {
    try {
      await deleteCaseMessageAttachment(caseId, attachmentId);
      setPendingAttachments((prev) => prev.filter((item) => item.id !== attachmentId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not remove attachment');
    }
  }

  async function downloadAttachment(attachment: MessageAttachment) {
    if (!attachment.downloadable) return;
    const token = getAccessToken();
    const response = await fetch(caseMessageAttachmentDownloadUrl(caseId, attachment.id), {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) throw new Error('Download failed');
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = attachment.display_filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  const messages = threadQuery.data?.messages ?? [];
  const threadClosed = threadQuery.data?.status === 'closed';
  const canSend =
    Boolean(body.trim()) &&
    !sendMutation.isPending &&
    !uploading &&
    !hasPendingScan &&
    !hasRejected;

  return (
    <Card title="Client messages" className="lg:col-span-3">
      <p className="text-sm text-gray-600">
        Secure thread with the linked portal client. Attachments are policy-scanned before send.
      </p>

      {threadQuery.isLoading ? (
        <p className="mt-4 text-sm text-gray-500">Loading messages…</p>
      ) : null}

      {threadQuery.isError ? (
        <p className="mt-4 text-sm text-red-600">
          Failed to load messages:{' '}
          {threadQuery.error instanceof Error ? threadQuery.error.message : 'Unknown error'}
        </p>
      ) : null}

      {!threadQuery.isLoading && !threadQuery.isError ? (
        <div className="mt-4 space-y-3">
          {messages.length === 0 ? (
            <p className="text-sm text-gray-500">
              No messages yet. Send the first message to the portal client below.
            </p>
          ) : (
            messages.map((message) => (
              <StaffMessageBubble
                key={message.id}
                message={message}
                onDownload={(attachment) =>
                  void downloadAttachment(attachment).catch(() => setError('Download failed'))
                }
              />
            ))
          )}
        </div>
      ) : null}

      {threadClosed ? (
        <p className="mt-4 rounded-md bg-gray-100 px-4 py-3 text-sm text-gray-600">
          This message thread is closed.
        </p>
      ) : (
        <form
          className="mt-4 space-y-3"
          onSubmit={(event) => {
            event.preventDefault();
            setError(null);
            sendMutation.mutate();
          }}
        >
          <div>
            <label htmlFor="staff-message-body" className="block text-sm font-medium text-gray-700">
              Reply to client
            </label>
            <textarea
              id="staff-message-body"
              rows={4}
              className={inputClass}
              value={body}
              onChange={(event) => setBody(event.target.value)}
              placeholder="Write your message…"
              disabled={sendMutation.isPending}
            />
          </div>

          {pendingAttachments.length ? (
            <ul className="flex flex-wrap gap-2">
              {pendingAttachments.map((attachment) => (
                <li
                  key={attachment.id}
                  className="inline-flex items-center gap-2 rounded-md border border-gray-200 px-2 py-1 text-xs"
                >
                  <span>
                    {attachment.display_filename} · {attachment.scan_status}
                  </span>
                  <button
                    type="button"
                    className="font-semibold text-red-600"
                    onClick={() => void removePending(attachment.id)}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          ) : null}

          <p className="text-xs text-gray-500">
            Allowed: PDF, JPEG, PNG, TIFF, DOC/DOCX, TXT. Send is disabled while scans are pending
            or rejected.
          </p>

          <div className="flex flex-wrap items-center gap-2">
            <input
              id={fileInputId}
              type="file"
              accept={ACCEPTED}
              className="sr-only"
              multiple
              onChange={(e) => {
                void onPickFile(e.target.files);
                e.target.value = '';
              }}
            />
            <label
              htmlFor={fileInputId}
              className="inline-flex cursor-pointer rounded-md border border-gray-300 px-3 py-2 text-sm font-medium"
            >
              {uploading ? 'Uploading…' : 'Attach file'}
            </label>
            <Button type="submit" loading={sendMutation.isPending} disabled={!canSend}>
              Send message
            </Button>
          </div>

          {error ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          ) : null}
        </form>
      )}
    </Card>
  );
}

function StaffMessageBubble({
  message,
  onDownload,
}: {
  message: ThreadMessage;
  onDownload: (attachment: MessageAttachment) => void;
}) {
  const isStaff = message.sender_role === 'staff';

  return (
    <div className={`flex ${isStaff ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] rounded-lg px-4 py-3 text-sm ${
          isStaff ? 'bg-brand-600 text-white' : 'border border-gray-200 bg-white text-gray-900'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.body}</p>
        {message.attachments?.length ? (
          <ul className="mt-2 space-y-1 text-xs">
            {message.attachments.map((attachment) => (
              <li key={attachment.id}>
                <button
                  type="button"
                  className="underline underline-offset-2 disabled:no-underline disabled:opacity-60"
                  disabled={!attachment.downloadable}
                  onClick={() => onDownload(attachment)}
                >
                  {attachment.display_filename}
                </button>
              </li>
            ))}
          </ul>
        ) : null}
        <p className={`mt-2 text-xs ${isStaff ? 'text-brand-100' : 'text-gray-400'}`}>
          {isStaff ? 'You' : 'Client'} · {formatTimestamp(message.created_at)}
        </p>
      </div>
    </div>
  );
}
