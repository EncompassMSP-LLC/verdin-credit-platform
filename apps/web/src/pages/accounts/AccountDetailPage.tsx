import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  approveAccountDisputeLetter,
  createAccountDisputeDraftReviewTask,
  createAccountDisputeLetterDraft,
  createAccountDisputeLetterReviewTask,
  deleteAccount,
  getAccount,
  getAccountDisputeDraft,
  getAccountDisputeLetter,
  listAccountDisputeLetters,
  markAccountAwaitingDisputeResponse,
  sendAccountDisputeLetter,
  voidAccountDisputeLetter,
  type DisputeLetter,
} from '@verdin/api-client';
import { ACCOUNT_TYPE_LABELS, DISPUTE_STATUS_LABELS, PAYMENT_STATUS_LABELS } from '@verdin/shared';
import { Button, Card } from '@verdin/ui';
import { AccountDeleteDialog } from '../../components/accounts/AccountDeleteDialog';
import {
  AccountStatusChip,
  BureauBadge,
  DisputeStatusChip,
  ScoreDisplay,
} from '../../components/accounts/AccountBadges';

function formatCurrency(value: string | null) {
  if (!value) return '—';
  const num = Number(value);
  if (Number.isNaN(num)) return value;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}

function formatDate(value: string | null) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
}

function EmptyListText({ children }: { children: string }) {
  return <p className="text-sm text-gray-500">{children}</p>;
}

function SavedDisputeLetterRow({
  accountId,
  letter,
  onLetterUpdated,
}: {
  accountId: string;
  letter: DisputeLetter;
  onLetterUpdated: () => void;
}) {
  const [detailsOpen, setDetailsOpen] = useState(false);

  const detailQuery = useQuery({
    queryKey: ['account-dispute-letter', accountId, letter.id],
    queryFn: () => getAccountDisputeLetter(accountId, letter.id),
    enabled: detailsOpen,
  });

  const reviewTaskMutation = useMutation({
    mutationFn: () => createAccountDisputeLetterReviewTask(accountId, letter.id),
    onSuccess: () => {
      onLetterUpdated();
    },
  });

  const approveMutation = useMutation({
    mutationFn: () => approveAccountDisputeLetter(accountId, letter.id),
    onSuccess: () => {
      onLetterUpdated();
    },
  });

  const sendMutation = useMutation({
    mutationFn: () => sendAccountDisputeLetter(accountId, letter.id),
    onSuccess: () => {
      onLetterUpdated();
    },
  });

  const voidMutation = useMutation({
    mutationFn: () => voidAccountDisputeLetter(accountId, letter.id),
    onSuccess: () => {
      onLetterUpdated();
    },
  });

  const canVoid =
    letter.status === 'draft' || letter.status === 'review' || letter.status === 'approved';

  return (
    <li className="rounded-lg border border-gray-200 p-3">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-gray-900">{letter.subject}</p>
          <p className="text-xs text-gray-500">
            {letter.status}
            {letter.sent_at ? ` · sent ${new Date(letter.sent_at).toLocaleString()}` : null}
            {' · '}
            {new Date(letter.generated_at).toLocaleString()}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-gray-500">{letter.template_id}</span>
          <Button size="sm" variant="secondary" onClick={() => setDetailsOpen((open) => !open)}>
            {detailsOpen ? 'Hide details' : 'View details'}
          </Button>
          {letter.status === 'review' ? (
            <Button
              size="sm"
              onClick={() => approveMutation.mutate()}
              loading={approveMutation.isPending}
              disabled={approveMutation.isPending}
            >
              Approve letter
            </Button>
          ) : null}
          {letter.status === 'approved' ? (
            <Button
              size="sm"
              onClick={() => sendMutation.mutate()}
              loading={sendMutation.isPending}
              disabled={sendMutation.isPending}
            >
              Mark as sent
            </Button>
          ) : null}
          {letter.status === 'sent' ? (
            <span className="text-xs font-medium text-blue-700">Sent</span>
          ) : null}
          {letter.status === 'void' ? (
            <span className="text-xs font-medium text-gray-600">Voided</span>
          ) : null}
          {canVoid ? (
            <Button
              size="sm"
              variant="secondary"
              onClick={() => voidMutation.mutate()}
              loading={voidMutation.isPending}
              disabled={voidMutation.isPending}
            >
              Void letter
            </Button>
          ) : null}
          {reviewTaskMutation.data ? (
            <Link to={`/tasks/${reviewTaskMutation.data.id}`}>
              <Button size="sm" variant="secondary">
                View review task
              </Button>
            </Link>
          ) : letter.status === 'draft' || letter.status === 'review' ? (
            <Button
              size="sm"
              variant="secondary"
              onClick={() => reviewTaskMutation.mutate()}
              loading={reviewTaskMutation.isPending}
              disabled={reviewTaskMutation.isPending}
            >
              Create review task
            </Button>
          ) : null}
        </div>
      </div>
      {reviewTaskMutation.isError ? (
        <p className="mt-2 w-full text-xs text-red-600">
          Failed to create review task for this draft.
        </p>
      ) : null}
      {approveMutation.isError ? (
        <p className="mt-2 w-full text-xs text-red-600">Failed to approve this dispute letter.</p>
      ) : null}
      {sendMutation.isError ? (
        <p className="mt-2 w-full text-xs text-red-600">
          Failed to mark this dispute letter as sent.
        </p>
      ) : null}
      {voidMutation.isError ? (
        <p className="mt-2 w-full text-xs text-red-600">Failed to void this dispute letter.</p>
      ) : null}
      {detailsOpen ? (
        <div className="mt-4 space-y-4 border-t border-gray-100 pt-4">
          {detailQuery.isLoading ? (
            <p className="text-sm text-gray-500">Loading letter details...</p>
          ) : null}
          {detailQuery.isError ? (
            <p className="text-sm text-red-600">Failed to load dispute letter details.</p>
          ) : null}
          {detailQuery.data ? (
            <>
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Disputed items
                </h4>
                {detailQuery.data.disputed_items.length > 0 ? (
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-gray-700">
                    {detailQuery.data.disputed_items.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <EmptyListText>No disputed items.</EmptyListText>
                )}
              </div>
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Letter body
                </h4>
                <pre className="mt-2 whitespace-pre-wrap rounded-md bg-gray-50 p-3 text-sm text-gray-800">
                  {detailQuery.data.body}
                </pre>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Evidence checklist
                  </h4>
                  {detailQuery.data.evidence_checklist.length > 0 ? (
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-gray-700">
                      {detailQuery.data.evidence_checklist.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <EmptyListText>No evidence checklist items.</EmptyListText>
                  )}
                </div>
                <div>
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                    Compliance notes
                  </h4>
                  {detailQuery.data.compliance_notes.length > 0 ? (
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-gray-700">
                      {detailQuery.data.compliance_notes.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <EmptyListText>No compliance notes.</EmptyListText>
                  )}
                </div>
              </div>
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Requested action
                </h4>
                <p className="mt-2 text-sm text-gray-700">{detailQuery.data.requested_action}</p>
              </div>
            </>
          ) : null}
        </div>
      ) : null}
    </li>
  );
}

export function AccountDetailPage() {
  const { accountId } = useParams<{ accountId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [deleteOpen, setDeleteOpen] = useState(false);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['account', accountId],
    queryFn: () => getAccount(accountId!),
    enabled: Boolean(accountId),
  });

  const disputeDraftQuery = useQuery({
    queryKey: ['account-dispute-draft', accountId],
    queryFn: () => getAccountDisputeDraft(accountId!),
    enabled: Boolean(accountId),
  });

  const disputeLettersQuery = useQuery({
    queryKey: ['account-dispute-letters', accountId],
    queryFn: () => listAccountDisputeLetters(accountId!),
    enabled: Boolean(accountId),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteAccount(accountId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['accounts-intelligence'] });
      navigate('/accounts');
    },
  });

  const reviewTaskMutation = useMutation({
    mutationFn: () => createAccountDisputeDraftReviewTask(accountId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const saveDraftMutation = useMutation({
    mutationFn: () => createAccountDisputeLetterDraft(accountId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['account-dispute-letters', accountId] });
    },
  });

  const awaitingResponseMutation = useMutation({
    mutationFn: () => markAccountAwaitingDisputeResponse(accountId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['account', accountId] });
      queryClient.invalidateQueries({ queryKey: ['accounts-intelligence'] });
    },
  });

  if (!accountId) return null;

  if (isLoading) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading account...</p>
        </Card>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-8">
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Account not found'}
            </p>
            <Link
              to="/accounts"
              className="mt-4 inline-block text-sm text-brand-600 hover:underline"
            >
              Back to accounts
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/accounts" className="text-sm text-brand-600 hover:underline">
            ← Back to accounts
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{data.creditor_name}</h1>
          <div className="mt-2 flex flex-wrap gap-2">
            <BureauBadge bureau={data.bureau} />
            <AccountStatusChip status={data.account_status} />
            <DisputeStatusChip status={data.dispute_status} />
          </div>
        </div>
        <div className="flex gap-2">
          <Link to={`/accounts/${accountId}/edit`}>
            <Button variant="secondary">Edit</Button>
          </Link>
          <Button variant="danger" onClick={() => setDeleteOpen(true)}>
            Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card title="Intelligence scores" className="lg:col-span-1">
          <div className="flex gap-8">
            <ScoreDisplay label="Risk score" score={data.risk_score} variant="risk" />
            <ScoreDisplay
              label="Readiness score"
              score={data.readiness_score}
              variant="readiness"
            />
          </div>
          {data.ai_recommended_next_action ? (
            <p className="mt-4 text-sm text-gray-600">
              <span className="font-medium text-gray-900">Next action:</span>{' '}
              {data.ai_recommended_next_action}
            </p>
          ) : null}
        </Card>

        <Card title="Financial details" className="lg:col-span-2">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-xs text-gray-500">Balance</dt>
              <dd className="text-sm font-medium text-gray-900">{formatCurrency(data.balance)}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Past due</dt>
              <dd className="text-sm font-medium text-gray-900">
                {formatCurrency(data.past_due_amount)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Account type</dt>
              <dd className="text-sm text-gray-900">{ACCOUNT_TYPE_LABELS[data.account_type]}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Payment status</dt>
              <dd className="text-sm text-gray-900">
                {PAYMENT_STATUS_LABELS[data.payment_status]}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Date reported</dt>
              <dd className="text-sm text-gray-900">{formatDate(data.date_reported)}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Next eligible dispute</dt>
              <dd className="text-sm text-gray-900">
                {formatDate(data.next_eligible_dispute_date)}
              </dd>
            </div>
          </dl>
        </Card>

        <Card title="Dispute workflow" className="lg:col-span-3">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <dt className="text-xs text-gray-500">Dispute status</dt>
              <dd className="mt-1">
                <DisputeStatusChip status={data.dispute_status} />
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Dispute round</dt>
              <dd className="text-sm text-gray-900">{data.dispute_round}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Status label</dt>
              <dd className="text-sm text-gray-900">
                {DISPUTE_STATUS_LABELS[data.dispute_status]}
              </dd>
            </div>
          </dl>
          {data.dispute_status === 'dispute_sent' ? (
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <Button
                size="sm"
                onClick={() => awaitingResponseMutation.mutate()}
                loading={awaitingResponseMutation.isPending}
                disabled={awaitingResponseMutation.isPending}
              >
                Mark awaiting response
              </Button>
              {awaitingResponseMutation.isError ? (
                <p className="text-xs text-red-600">Failed to update dispute status.</p>
              ) : null}
            </div>
          ) : null}
          <div className="mt-4">
            <Link to={`/cases/${data.case_id}`} className="text-sm text-brand-600 hover:underline">
              View linked case →
            </Link>
          </div>
        </Card>

        <Card title="Dispute draft preview" className="lg:col-span-3">
          {disputeDraftQuery.isLoading ? (
            <p className="py-6 text-center text-sm text-gray-500">Loading dispute draft...</p>
          ) : null}

          {disputeDraftQuery.isError ? (
            <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              Failed to load the dispute draft preview.
            </div>
          ) : null}

          {disputeDraftQuery.data ? (
            <div className="space-y-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                    {disputeDraftQuery.data.template_id}
                  </p>
                  <h3 className="mt-1 text-base font-semibold text-gray-900">
                    {disputeDraftQuery.data.subject}
                  </h3>
                </div>
                <span className="inline-flex w-fit rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                  {disputeDraftQuery.data.generated_by === 'rules'
                    ? 'Rule-based draft'
                    : 'Generated draft'}
                </span>
              </div>

              <div className="flex flex-col gap-3 rounded-md border border-blue-100 bg-blue-50 p-4 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm text-blue-900">
                  Create a task to review this draft, confirm evidence, and prepare the next dispute
                  action.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => saveDraftMutation.mutate()}
                    loading={saveDraftMutation.isPending}
                    disabled={saveDraftMutation.isPending}
                  >
                    Save draft
                  </Button>
                  {reviewTaskMutation.data ? (
                    <Link to={`/tasks/${reviewTaskMutation.data.id}`}>
                      <Button size="sm">View review task</Button>
                    </Link>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => reviewTaskMutation.mutate()}
                      loading={reviewTaskMutation.isPending}
                      disabled={reviewTaskMutation.isPending}
                    >
                      Create review task
                    </Button>
                  )}
                </div>
              </div>

              {saveDraftMutation.isSuccess ? (
                <div className="rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-700">
                  Draft saved for later review.
                </div>
              ) : null}

              {saveDraftMutation.isError ? (
                <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  Failed to save the dispute draft.
                </div>
              ) : null}

              {reviewTaskMutation.isError ? (
                <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  Failed to create the dispute draft review task.
                </div>
              ) : null}

              <div>
                <h4 className="text-sm font-semibold text-gray-900">Suggested dispute reasons</h4>
                {disputeDraftQuery.data.dispute_reason_suggestions.length > 0 ? (
                  <ul className="mt-2 space-y-3">
                    {disputeDraftQuery.data.dispute_reason_suggestions.map((suggestion) => (
                      <li
                        key={suggestion.code}
                        className="rounded-md border border-gray-200 bg-white p-3"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <p className="text-sm font-medium text-gray-900">{suggestion.title}</p>
                          <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-gray-500">
                            <span>{suggestion.category}</span>
                            <span>{suggestion.severity}</span>
                          </div>
                        </div>
                        <p className="mt-2 text-sm text-gray-700">{suggestion.description}</p>
                        {suggestion.requires_evidence.length > 0 ? (
                          <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-gray-600">
                            {suggestion.requires_evidence.map((item) => (
                              <li key={item}>{item}</li>
                            ))}
                          </ul>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <EmptyListText>No dispute reason suggestions generated.</EmptyListText>
                )}
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900">Disputed items</h4>
                {disputeDraftQuery.data.disputed_items.length > 0 ? (
                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-gray-700">
                    {disputeDraftQuery.data.disputed_items.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <EmptyListText>No disputed items generated.</EmptyListText>
                )}
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900">Draft body</h4>
                <pre className="mt-2 whitespace-pre-wrap rounded-md border border-gray-200 bg-gray-50 p-4 text-sm leading-6 text-gray-800">
                  {disputeDraftQuery.data.body}
                </pre>
              </div>

              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">Evidence checklist</h4>
                  {disputeDraftQuery.data.evidence_checklist.length > 0 ? (
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-gray-700">
                      {disputeDraftQuery.data.evidence_checklist.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <EmptyListText>No evidence checklist generated.</EmptyListText>
                  )}
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">Compliance notes</h4>
                  {disputeDraftQuery.data.compliance_notes.length > 0 ? (
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-gray-700">
                      {disputeDraftQuery.data.compliance_notes.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <EmptyListText>No compliance notes generated.</EmptyListText>
                  )}
                </div>
              </div>

              <div className="rounded-md border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
                {disputeDraftQuery.data.requested_action}
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-900">Saved drafts</h4>
                {disputeLettersQuery.isLoading ? (
                  <p className="mt-2 text-sm text-gray-500">Loading saved drafts...</p>
                ) : null}
                {disputeLettersQuery.data && disputeLettersQuery.data.length > 0 ? (
                  <ul className="mt-2 divide-y divide-gray-200 rounded-md border border-gray-200">
                    {disputeLettersQuery.data.map((letter) => (
                      <SavedDisputeLetterRow
                        key={letter.id}
                        accountId={accountId!}
                        letter={letter}
                        onLetterUpdated={() => {
                          queryClient.invalidateQueries({
                            queryKey: ['account-dispute-letters', accountId],
                          });
                          queryClient.invalidateQueries({ queryKey: ['account', accountId] });
                          queryClient.invalidateQueries({ queryKey: ['accounts-intelligence'] });
                          queryClient.invalidateQueries({ queryKey: ['tasks'] });
                        }}
                      />
                    ))}
                  </ul>
                ) : null}
                {disputeLettersQuery.data?.length === 0 ? (
                  <EmptyListText>No saved drafts yet.</EmptyListText>
                ) : null}
              </div>
            </div>
          ) : null}
        </Card>
      </div>

      <AccountDeleteDialog
        creditorName={data.creditor_name}
        open={deleteOpen}
        loading={deleteMutation.isPending}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteOpen(false)}
      />
    </div>
  );
}
