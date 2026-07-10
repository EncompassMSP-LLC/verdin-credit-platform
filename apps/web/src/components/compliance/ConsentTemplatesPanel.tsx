import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  getAccessToken,
  listConsentDocumentTemplates,
  updateConsentDocumentTemplate,
  type ConsentDocumentTemplate,
  type ConsentDocumentTemplateKey,
} from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { useAuth } from '../../lib/auth';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-mono shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

const TEMPLATE_ORDER: ConsentDocumentTemplateKey[] = [
  'croa_disclosure',
  'croa_service_agreement',
  'fcra_authorization',
];

type TemplateDraft = {
  title: string;
  bodyText: string;
  legalReviewStatus: string;
  mergeFieldsJson: string;
};

const emptyDraft: TemplateDraft = {
  title: '',
  bodyText: '',
  legalReviewStatus: 'draft',
  mergeFieldsJson: '{}',
};

function templateToDraft(template: ConsentDocumentTemplate): TemplateDraft {
  return {
    title: template.title,
    bodyText: template.body_text,
    legalReviewStatus: template.legal_review_status,
    mergeFieldsJson: JSON.stringify(template.merge_field_defaults ?? {}, null, 2),
  };
}

export function ConsentTemplatesPanel() {
  const queryClient = useQueryClient();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [activeKey, setActiveKey] = useState<ConsentDocumentTemplateKey>('croa_disclosure');
  const [drafts, setDrafts] = useState<Partial<Record<ConsentDocumentTemplateKey, TemplateDraft>>>(
    {},
  );
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const authReady = isAuthenticated && !authLoading && Boolean(getAccessToken());

  const templatesQuery = useQuery({
    queryKey: ['consent-document-templates'],
    queryFn: listConsentDocumentTemplates,
    enabled: authReady,
    retry: (failureCount, queryError) => {
      if (queryError instanceof ApiClientError && queryError.status === 401) {
        return failureCount < 2;
      }
      return failureCount < 1;
    },
  });

  const selectedTemplate = templatesQuery.data?.find((item) => item.template_key === activeKey);
  const draft =
    drafts[activeKey] ?? (selectedTemplate ? templateToDraft(selectedTemplate) : emptyDraft);

  const updateDraft = (patch: Partial<TemplateDraft>) => {
    setDrafts((current) => ({
      ...current,
      [activeKey]: { ...draft, ...patch },
    }));
  };

  const selectTemplate = (key: ConsentDocumentTemplateKey) => {
    setActiveKey(key);
    setError(null);
    setSuccess(null);
  };

  const saveMutation = useMutation({
    mutationFn: async () => {
      let mergeFieldDefaults: Record<string, string> | null = null;
      try {
        const parsed = JSON.parse(draft.mergeFieldsJson) as Record<string, string>;
        mergeFieldDefaults = Object.keys(parsed).length ? parsed : null;
      } catch {
        throw new Error('Merge field defaults must be valid JSON');
      }
      return updateConsentDocumentTemplate(activeKey, {
        title: draft.title.trim(),
        body_text: draft.bodyText,
        merge_field_defaults: mergeFieldDefaults,
        legal_review_status: draft.legalReviewStatus,
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['consent-document-templates'] });
      setDrafts((current) => {
        const next = { ...current };
        delete next[activeKey];
        return next;
      });
      setSuccess('Template saved for your organization.');
      setError(null);
    },
    onError: (err: Error) => {
      setSuccess(null);
      setError(err.message);
    },
  });

  const loadErrorMessage =
    templatesQuery.error instanceof ApiClientError && templatesQuery.error.status === 401
      ? 'Could not load templates. Your session may have expired — try Retry or log in again.'
      : templatesQuery.error instanceof Error
        ? templatesQuery.error.message
        : 'Failed to load consent templates.';

  return (
    <div className="space-y-6">
      <Card title="Consent & contract templates (legal review)">
        <p className="mb-4 text-sm text-gray-600">
          These are starter CROA disclosure, service agreement, and FCRA authorization templates.
          Edit the text below for your organization, then have counsel review before clients sign.
          Use merge fields like <code className="text-xs">{'{{organization_name}}'}</code> and{' '}
          <code className="text-xs">{'{{client_name}}'}</code> — defaults can be set in the JSON
          block.
        </p>

        {authLoading || (authReady && templatesQuery.isLoading) ? (
          <p className="text-sm text-gray-500">Loading templates…</p>
        ) : null}

        {templatesQuery.isError ? (
          <div className="space-y-3">
            <p className="text-sm text-red-600">{loadErrorMessage}</p>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => void templatesQuery.refetch()}
            >
              Retry
            </Button>
          </div>
        ) : null}

        {templatesQuery.data ? (
          <>
            <div className="mb-4 flex flex-wrap gap-2">
              {TEMPLATE_ORDER.map((key) => {
                const template = templatesQuery.data.find((item) => item.template_key === key);
                return (
                  <Button
                    key={key}
                    type="button"
                    variant={activeKey === key ? 'primary' : 'secondary'}
                    onClick={() => selectTemplate(key)}
                  >
                    {template?.title ?? key}
                  </Button>
                );
              })}
            </div>

            <form
              className="space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                saveMutation.mutate();
              }}
            >
              <div>
                <label className="block text-sm font-medium text-gray-700">Title</label>
                <input
                  className={inputClass}
                  value={draft.title}
                  onChange={(event) => updateDraft({ title: event.target.value })}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Legal review status
                </label>
                <select
                  className={inputClass}
                  value={draft.legalReviewStatus}
                  onChange={(event) => updateDraft({ legalReviewStatus: event.target.value })}
                >
                  <option value="draft">Draft — pending counsel review</option>
                  <option value="approved">Approved by counsel</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Merge field defaults (JSON)
                </label>
                <textarea
                  rows={6}
                  className={inputClass}
                  value={draft.mergeFieldsJson}
                  onChange={(event) => updateDraft({ mergeFieldsJson: event.target.value })}
                />
                <p className="mt-1 text-xs text-gray-500">
                  Override placeholders such as organization address, fee schedule, and governing
                  state.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Document body</label>
                <textarea
                  rows={24}
                  className={inputClass}
                  value={draft.bodyText}
                  onChange={(event) => updateDraft({ bodyText: event.target.value })}
                  required
                />
              </div>

              {error ? <p className="text-sm text-red-600">{error}</p> : null}
              {success ? <p className="text-sm text-green-700">{success}</p> : null}

              <Button type="submit" loading={saveMutation.isPending}>
                Save template for organization
              </Button>
            </form>
          </>
        ) : null}
      </Card>
    </div>
  );
}
