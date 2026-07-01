import { expect, test, type Route } from '@playwright/test';

const currentUser = {
  id: 'user-001',
  email: 'owner@verdin.demo',
  first_name: 'Olivia',
  last_name: 'Owner',
  role: 'owner',
  is_active: true,
  organization_id: 'org-001',
  created_at: '2026-08-15T12:00:00Z',
  updated_at: '2026-08-15T12:00:00Z',
};

const accountId = 'account-001';

const accountRecord = {
  id: accountId,
  organization_id: 'org-001',
  case_id: 'case-001',
  bureau: 'equifax',
  creditor_name: 'Example National Bank',
  original_creditor: 'Example National Bank',
  account_number_masked: '****4521',
  account_type: 'credit_card',
  account_status: 'open',
  payment_status: 'late_60',
  balance: '2450.00',
  past_due_amount: '420.00',
  date_opened: '2019-03-15',
  date_reported: '2026-05-01',
  date_last_activity: null,
  date_first_delinquency: null,
  dispute_status: 'ready_for_dispute',
  investigation_status: 'none',
  dispute_round: 0,
  last_dispute_date: null,
  next_eligible_dispute_date: null,
  response_received: false,
  cra_dispute: false,
  risk_score: 55,
  readiness_score: 90,
  ai_recommended_next_action: 'Prepare and send dispute letter to CRA',
  created_at: '2026-08-15T12:00:00Z',
  updated_at: '2026-08-15T12:00:00Z',
  deleted_at: null,
  created_by_id: 'user-001',
  updated_by_id: 'user-001',
};

const disputeDraft = {
  account_id: accountId,
  case_id: 'case-001',
  bureau: 'equifax',
  recipient_type: 'credit_bureau',
  template_id: 'cra-tradeline-investigation-v1',
  subject: 'Request for investigation of inaccurate tradeline reporting',
  body: 'Please investigate the reporting for Example National Bank account ending in 4521.',
  disputed_items: ['Balance reported inaccurately'],
  dispute_reason_suggestions: [],
  requested_action: 'Delete or correct the tradeline within 30 days.',
  evidence_checklist: ['Government-issued ID'],
  compliance_notes: ['FCRA Section 611 applies.'],
  evidence_ready: true,
  missing_evidence: [],
  generated_by: 'rules',
  readiness_score: 90,
  risk_score: 55,
};

type LetterStatus = 'draft' | 'review' | 'approved' | 'sent';

function buildLetter(status: LetterStatus) {
  return {
    id: 'letter-001',
    organization_id: 'org-001',
    case_id: 'case-001',
    account_id: accountId,
    recipient_type: 'credit_bureau',
    status,
    template_id: disputeDraft.template_id,
    subject: disputeDraft.subject,
    body: disputeDraft.body,
    disputed_items: disputeDraft.disputed_items,
    requested_action: disputeDraft.requested_action,
    evidence_checklist: disputeDraft.evidence_checklist,
    compliance_notes: disputeDraft.compliance_notes,
    generated_by: 'rules',
    generated_at: '2026-08-15T12:00:00Z',
    sent_at: status === 'sent' ? '2026-08-15T12:30:00Z' : null,
    created_at: '2026-08-15T12:00:00Z',
    updated_at: '2026-08-15T12:00:00Z',
    deleted_at: null,
    created_by_id: 'user-001',
    updated_by_id: 'user-001',
  };
}

function fulfillJson(route: Route, body: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  });
}

test.describe('Dispute letter account detail', () => {
  test('walks saved letter through approve and send', async ({ page }) => {
    let savedLetters: ReturnType<typeof buildLetter>[] = [buildLetter('review')];

    await page.addInitScript(() => {
      window.localStorage.setItem('verdin_access_token', 'test-access-token');
      window.localStorage.setItem('verdin_refresh_token', 'test-refresh-token');
    });

    await page.route('**/api/v1/**', async (route) => {
      const path = new URL(route.request().url()).pathname;

      if (path === '/api/v1/auth/me') {
        await fulfillJson(route, currentUser);
        return;
      }

      if (path === `/api/v1/accounts/${accountId}`) {
        await fulfillJson(route, accountRecord);
        return;
      }

      if (path.startsWith(`/api/v1/accounts/${accountId}/dispute-draft`)) {
        await fulfillJson(route, disputeDraft);
        return;
      }

      if (route.request().method() === 'GET' && path.endsWith('/dispute-letters')) {
        await fulfillJson(route, savedLetters);
        return;
      }

      if (
        route.request().method() === 'POST' &&
        path.endsWith('/dispute-letters/letter-001/approve')
      ) {
        savedLetters = [buildLetter('approved')];
        await fulfillJson(route, savedLetters[0]);
        return;
      }

      if (
        route.request().method() === 'POST' &&
        path.endsWith('/dispute-letters/letter-001/send')
      ) {
        savedLetters = [buildLetter('sent')];
        await fulfillJson(route, savedLetters[0]);
        return;
      }

      if (route.request().method() === 'GET' && path.endsWith('/dispute-letters/letter-001')) {
        await fulfillJson(route, savedLetters[0] ?? buildLetter('review'));
        return;
      }

      await route.continue();
    });

    await page.goto(`/accounts/${accountId}`);

    await expect(page.getByRole('heading', { name: accountRecord.creditor_name })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Saved drafts' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Approve letter' })).toBeVisible();

    await page.getByRole('button', { name: 'Approve letter' }).click();
    await expect(page.getByRole('button', { name: 'Mark as sent' })).toBeVisible();

    await page.getByRole('button', { name: 'Mark as sent' }).click();
    await expect(page.getByText('Sent')).toBeVisible();
  });
});
