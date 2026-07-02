import { apiPath, request } from './http';

export type MessageSenderRole = 'portal_client' | 'staff';

export interface ThreadMessage {
  id: string;
  thread_id: string;
  sender_role: MessageSenderRole;
  portal_user_id: string | null;
  staff_user_id: string | null;
  body: string;
  created_at: string;
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
