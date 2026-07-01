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

const caseRecord = {
  id: 'case-001',
  organization_id: 'org-001',
  case_number: 'CASE-001',
  title: 'Avery Morgan Credit Repair',
  client_name: 'Avery J. Morgan',
  client_email: 'avery@example.test',
  status: 'open',
  stage: 'review',
  priority: 'medium',
  assigned_user_id: 'user-001',
  summary: null,
  notes: null,
  opened_at: '2026-08-15T12:00:00Z',
  closed_at: null,
  created_at: '2026-08-15T12:00:00Z',
  updated_at: '2026-08-15T12:00:00Z',
  deleted_at: null,
  created_by_id: 'user-001',
  updated_by_id: 'user-001',
};

const importedDocument = {
  id: 'doc-import-001',
  organization_id: 'org-001',
  case_id: caseRecord.id,
  account_id: null,
  title: 'Equifax credit report',
  description: 'Imported via Credit Report Import Wizard',
  file_name: 'equifax-report.pdf',
  mime_type: 'application/pdf',
  file_size: 2048,
  file_hash: 'fixture-hash',
  version_number: 1,
  is_duplicate: false,
  duplicate_of_id: null,
  processing_status: 'completed',
  ocr_processed_at: '2026-08-15T12:01:00Z',
  ocr_version_number: 1,
  document_type: 'credit_report',
  confidence_score: 0.98,
  classified_at: '2026-08-15T12:01:00Z',
  metadata_status: 'extracted',
  created_at: '2026-08-15T12:00:00Z',
  updated_at: '2026-08-15T12:01:00Z',
  deleted_at: null,
  created_by_id: 'user-001',
  updated_by_id: 'user-001',
};

const ocrResult = {
  document_id: importedDocument.id,
  processing_status: 'completed',
  ocr_text:
    'EQUIFAX Consumer Credit File\nCONSUMER INFORMATION\nTRADELINES\nFurnisher: Summit Retail Bank',
  ocr_error: null,
  ocr_processed_at: '2026-08-15T12:01:00Z',
  ocr_version_number: 1,
};

const metadata = {
  document_id: importedDocument.id,
  consumer_name: 'Avery J. Morgan',
  bureau: 'equifax',
  creditor: 'Summit Retail Bank',
  collection_agency: null,
  account_number_masked: '************3344',
  report_date: '08/15/2026',
  open_date: '04/18/2018',
  balance: 1875.5,
  payment_status: 'Late 30 Days',
  addresses: [],
  phone_numbers: [],
  ssn_masked: '***-**-9012',
  confidence_score: 0.96,
  extraction_method: 'parser',
  metadata_status: 'extracted',
  extracted_at: '2026-08-15T12:01:30Z',
  extraction_error: null,
};

const parsedCreditReport = {
  document_id: importedDocument.id,
  schema_version: '1.0',
  bureau: 'equifax',
  parser_name: 'equifax',
  parser_confidence: 0.99,
  parsed_report: {
    accounts: [
      {
        creditor_name: 'Summit Retail Bank',
        account_number_masked: '************3344',
        balance: 1875.5,
        payment_status: 'Late 30 Days',
        open_date: '04/18/2018',
        date_reported: '08/01/2026',
      },
      {
        creditor_name: 'Metro Auto Finance',
        account_number_masked: '************1122',
        balance: 9420,
        payment_status: 'Current',
        open_date: '09/22/2020',
        date_reported: '08/01/2026',
      },
    ],
  },
  is_partial: false,
  warnings: [],
  parsed_at: '2026-08-15T12:01:15Z',
};

const resolutions = {
  document_id: importedDocument.id,
  resolutions: [
    {
      id: 'resolution-001',
      document_id: importedDocument.id,
      entity_type: 'case',
      matched_entity_id: caseRecord.id,
      confidence_score: 0.94,
      resolution_status: 'matched',
      resolution_method: 'automatic',
      reasoning: 'Consumer name matched the selected case.',
      candidate_entity_ids: [caseRecord.id],
      reviewed_at: null,
      reviewed_by_id: null,
    },
  ],
};

function fulfillJson(route: Route, body: unknown) {
  return route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify(body),
  });
}

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.setItem('verdin_access_token', 'test-access-token');
    window.localStorage.setItem('verdin_refresh_token', 'test-refresh-token');
  });

  await page.route('**/api/v1/auth/me', (route) => fulfillJson(route, currentUser));
  await page.route('**/api/v1/cases**', (route) =>
    fulfillJson(route, {
      items: [caseRecord],
      total: 1,
      page: 1,
      page_size: 100,
      pages: 1,
    }),
  );
  await page.route('**/api/v1/documents', (route) => fulfillJson(route, importedDocument));
  await page.route('**/api/v1/documents/doc-import-001/ocr', (route) =>
    fulfillJson(route, ocrResult),
  );
  await page.route('**/api/v1/documents/doc-import-001/metadata', (route) =>
    fulfillJson(route, metadata),
  );
  await page.route('**/api/v1/documents/doc-import-001/parsed-credit-report', (route) =>
    fulfillJson(route, parsedCreditReport),
  );
  await page.route('**/api/v1/documents/doc-import-001/resolutions', (route) =>
    fulfillJson(route, resolutions),
  );
  await page.route('**/api/v1/documents/doc-import-001', (route) =>
    fulfillJson(route, importedDocument),
  );
});

test('completes the credit report import wizard with parsed tradelines', async ({ page }) => {
  await page.goto('/imports/credit-report?case_id=case-001');

  await expect(page.getByRole('heading', { name: 'Credit Report Import Wizard' })).toBeVisible();
  await expect(page.getByText('Importing into Avery Morgan Credit Repair')).toBeVisible();

  await page.getByLabel('Title').fill('Equifax credit report');
  await page.getByLabel('Credit report PDF').setInputFiles({
    name: 'equifax-report.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('%PDF-1.4\n% sanitized test fixture\n'),
  });
  await page.getByRole('button', { name: 'Start import' }).click();

  await expect(page.getByText('Uploaded equifax-report.pdf.')).toBeVisible();
  await expect(page.getByText('OCR completed with')).toBeVisible();
  await expect(page.getByText('Parsed by equifax (equifax)')).toBeVisible();
  await expect(page.getByText('99% confidence')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Extracted tradelines' })).toBeVisible();
  await expect(page.getByRole('cell', { name: 'Summit Retail Bank' })).toBeVisible();
  await expect(page.getByRole('cell', { name: '$1,875.50' })).toBeVisible();
  await expect(page.getByText('via parser')).toBeVisible();
  await expect(page.getByText('case match (94%)')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Import complete' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Start new import' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'View document' }).first()).toHaveAttribute(
    'href',
    '/documents/doc-import-001',
  );
  await expect(page.getByRole('link', { name: 'View case' })).toHaveAttribute(
    'href',
    '/cases/case-001',
  );
});
