import { apiPath, request, uploadRequest } from './http';

export type MessageSenderRole = 'portal_client' | 'staff';

export type MessageAttachmentScanStatus = 'pending' | 'clean' | 'rejected' | 'failed';

export interface MessageAttachment {
  id: string;
  message_id: string | null;
  document_id: string;
  display_filename: string;
  mime_type: string;
  byte_size: number;
  scan_status: MessageAttachmentScanStatus;
  scan_detail: string | null;
  downloadable: boolean;
  created_at: string;
}

export interface ThreadMessage {
  id: string;
  thread_id: string;
  sender_role: MessageSenderRole;
  portal_user_id: string | null;
  staff_user_id: string | null;
  body: string;
  created_at: string;
  attachments?: MessageAttachment[];
}

export interface CaseMessageThread {
  case_id: string;
  thread_id: string | null;
  client_id: string | null;
  status: 'open' | 'closed' | null;
  messages: ThreadMessage[];
}

export interface MessagingCenterStatus {
  secure_messaging_enabled: boolean;
  thread_per_case: boolean;
  capabilities: string[];
  deferred_capabilities: string[];
}

export interface SendMessageInput {
  body: string;
  attachment_ids?: string[];
  idempotency_key?: string;
}

export async function getMessagingCenterStatus(): Promise<MessagingCenterStatus> {
  return request<MessagingCenterStatus>(apiPath('/messaging/status'));
}

export async function getCaseMessageThread(caseId: string): Promise<CaseMessageThread> {
  return request<CaseMessageThread>(apiPath(`/cases/${caseId}/message-thread`));
}

export async function postCaseMessageThreadReply(
  caseId: string,
  input: SendMessageInput,
): Promise<ThreadMessage> {
  return request<ThreadMessage>(apiPath(`/cases/${caseId}/message-thread/messages`), {
    method: 'POST',
    body: input,
  });
}

export async function uploadCaseMessageAttachment(
  caseId: string,
  file: File | Blob,
  filename?: string,
): Promise<MessageAttachment> {
  const form = new FormData();
  form.append('file', file, filename);
  return uploadRequest<MessageAttachment>(
    apiPath(`/cases/${caseId}/message-thread/attachments`),
    form,
  );
}

export async function deleteCaseMessageAttachment(
  caseId: string,
  attachmentId: string,
): Promise<void> {
  await request<void>(apiPath(`/cases/${caseId}/message-thread/attachments/${attachmentId}`), {
    method: 'DELETE',
  });
}

export function caseMessageAttachmentDownloadUrl(caseId: string, attachmentId: string): string {
  return apiPath(`/cases/${caseId}/message-thread/attachments/${attachmentId}/download`);
}
