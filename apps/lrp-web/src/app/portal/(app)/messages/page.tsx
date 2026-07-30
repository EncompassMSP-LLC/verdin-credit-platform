'use client';

import { useId, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
  deletePortalMessageAttachment,
  getAccessToken,
  portalMessageAttachmentDownloadUrl,
  sendPortalCaseMessage,
  uploadPortalMessageAttachment,
  type MessageAttachment,
} from '@verdin/api-client';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { usePrimaryCase, usePortalMessages } from '@/lib/platform/hooks';
import { cn, formatDate } from '@/lib/utils';

const ACCEPTED =
  '.pdf,.jpg,.jpeg,.png,.tif,.tiff,.doc,.docx,.txt,application/pdf,image/png,image/jpeg';

export default function MessagesPage() {
  const queryClient = useQueryClient();
  const fileInputId = useId();
  const { primary } = usePrimaryCase();
  const messagesQuery = usePortalMessages(primary?.id);
  const [draft, setDraft] = useState('');
  const [pendingAttachments, setPendingAttachments] = useState<MessageAttachment[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);

  const hasPendingScan = pendingAttachments.some((a) => a.scan_status === 'pending');
  const hasRejected = pendingAttachments.some(
    (a) => a.scan_status === 'rejected' || a.scan_status === 'failed',
  );
  const canSend =
    Boolean(draft.trim()) &&
    !sending &&
    !uploading &&
    !hasPendingScan &&
    !hasRejected &&
    pendingAttachments.every((a) => a.scan_status === 'clean' || a.downloadable);

  async function onPickFile(fileList: FileList | null) {
    if (!primary || !fileList?.length) return;
    setUploading(true);
    setError(null);
    try {
      for (const file of Array.from(fileList)) {
        const uploaded = await uploadPortalMessageAttachment(primary.id, file, file.name);
        setPendingAttachments((prev) => [...prev, uploaded]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Attachment upload failed.');
    } finally {
      setUploading(false);
    }
  }

  async function removePending(attachmentId: string) {
    if (!primary) return;
    setError(null);
    try {
      await deletePortalMessageAttachment(primary.id, attachmentId);
      setPendingAttachments((prev) => prev.filter((item) => item.id !== attachmentId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not remove attachment.');
    }
  }

  async function downloadAttachment(attachment: MessageAttachment) {
    if (!primary || !attachment.downloadable) return;
    const token = getAccessToken();
    const response = await fetch(portalMessageAttachmentDownloadUrl(primary.id, attachment.id), {
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

  async function send() {
    if (!draft.trim() || !primary || !canSend) return;
    setSending(true);
    setError(null);
    try {
      await sendPortalCaseMessage(primary.id, {
        body: draft.trim(),
        attachment_ids: pendingAttachments.map((item) => item.id),
        idempotency_key:
          typeof crypto !== 'undefined' && 'randomUUID' in crypto
            ? crypto.randomUUID()
            : `portal-${Date.now()}`,
      });
      setDraft('');
      setPendingAttachments([]);
      await queryClient.invalidateQueries({ queryKey: ['portal', 'messages', primary.id] });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message.');
    } finally {
      setSending(false);
    }
  }

  const messages = messagesQuery.data?.messages ?? [];

  return (
    <div>
      <PageHeader
        eyebrow="Messages"
        title="Case messaging"
        description="Secure thread on your primary case. Attach PDF, image, or Word files (scanned before send)."
      />

      {!primary ? (
        <p className="rounded-brand border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning">
          No case available for messaging yet.
        </p>
      ) : (
        <PortalCard
          title={primary.title}
          description={`Source: /portal/cases/${primary.id}/messages`}
        >
          {error ? <p className="mb-3 text-sm text-critical">{error}</p> : null}
          <div className="flex max-h-[28rem] flex-col gap-3 overflow-y-auto">
            {messagesQuery.isLoading ? (
              <p className="text-sm text-slate-500">Loading messages…</p>
            ) : !messages.length ? (
              <p className="text-sm text-slate-500">No messages yet. Start the conversation.</p>
            ) : (
              messages.map((message) => {
                const mine = message.sender_role === 'portal_client';
                return (
                  <div
                    key={message.id}
                    className={cn(
                      'max-w-[90%] rounded-brand px-3 py-2 text-sm',
                      mine
                        ? 'ml-auto bg-navy-900 text-white dark:bg-gold-500 dark:text-navy-900'
                        : 'bg-sand-100 text-navy-900 dark:bg-navy-900/60 dark:text-white',
                    )}
                  >
                    <p className="text-[0.65rem] font-medium uppercase opacity-70">
                      {mine ? 'You' : 'Staff'}
                    </p>
                    <p className="mt-1">{message.body}</p>
                    {message.attachments?.length ? (
                      <ul className="mt-2 space-y-1">
                        {message.attachments.map((attachment) => (
                          <li key={attachment.id}>
                            <button
                              type="button"
                              className="underline underline-offset-2 disabled:no-underline disabled:opacity-60"
                              disabled={!attachment.downloadable}
                              onClick={() =>
                                void downloadAttachment(attachment).catch(() =>
                                  setError('Download failed.'),
                                )
                              }
                            >
                              {attachment.display_filename}
                              {!attachment.downloadable ? ` (${attachment.scan_status})` : ''}
                            </button>
                          </li>
                        ))}
                      </ul>
                    ) : null}
                    <p className="mt-1 text-[0.65rem] opacity-70">
                      {formatDate(message.created_at, {
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                );
              })
            )}
          </div>
          <div className="mt-4 space-y-3 border-t border-navy-900/8 pt-4 dark:border-white/10">
            {pendingAttachments.length ? (
              <ul className="flex flex-wrap gap-2">
                {pendingAttachments.map((attachment) => (
                  <li
                    key={attachment.id}
                    className="inline-flex items-center gap-2 rounded-brand border border-navy-900/15 px-2 py-1 text-xs dark:border-white/15"
                  >
                    <span>
                      {attachment.display_filename} · {attachment.scan_status}
                    </span>
                    <button
                      type="button"
                      className="font-semibold text-critical"
                      onClick={() => void removePending(attachment.id)}
                      aria-label={`Remove ${attachment.display_filename}`}
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
            <p className="text-xs text-slate-500">
              Allowed: PDF, JPEG, PNG, TIFF, DOC/DOCX, TXT · max size matches document uploads.
            </p>
            <div className="flex flex-col gap-2 sm:flex-row">
              <label htmlFor="draft" className="sr-only">
                Message
              </label>
              <input
                id="draft"
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Write a message…"
                className="flex-1 rounded-brand border border-navy-900/15 bg-white px-3 py-2 text-sm dark:border-white/15 dark:bg-navy-900"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    void send();
                  }
                }}
              />
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
                className="inline-flex cursor-pointer items-center justify-center rounded-brand border border-navy-900/15 px-3 py-2 text-sm font-medium dark:border-white/15"
              >
                {uploading ? 'Uploading…' : 'Attach'}
              </label>
              <button
                type="button"
                onClick={() => void send()}
                disabled={!canSend}
                className="rounded-brand bg-gold-500 px-4 py-2 text-sm font-semibold text-navy-900 hover:bg-gold-400 disabled:opacity-50"
              >
                Send
              </button>
            </div>
          </div>
        </PortalCard>
      )}
    </div>
  );
}
