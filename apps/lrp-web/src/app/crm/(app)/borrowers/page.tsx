'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { useCrmAuth } from '@/lib/crm/auth';
import { useCrmClients, type ClientStatus } from '@/lib/crm/client-hooks';
import { borrowers as seedBorrowers } from '@/lib/crm/data';
import { STAGE_LABELS } from '@/lib/crm/nav';
import { formatDate } from '@/lib/utils';

type BorrowerRow = {
  id: string;
  displayName: string;
  statusLabel: string;
  email: string;
  updatedAt: string;
};

/**
 * Spec: Vol 21 · pages/borrowers.md
 * Platform auth → GET /clients; demo → seed rows. Readiness band deferred to workspace slice.
 */
export default function CrmBorrowersPage() {
  const { authMode } = useCrmAuth();
  const isDemo = authMode === 'demo';

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<ClientStatus | ''>('');
  const [page, setPage] = useState(1);

  const clientsQuery = useCrmClients({
    page,
    search,
    status: statusFilter,
  });

  const searchTooShort = search.trim().length === 1;

  const rows = useMemo((): BorrowerRow[] => {
    if (isDemo) {
      const q = search.trim().toLowerCase();
      return seedBorrowers
        .filter((b) => {
          if (!q) return true;
          return (
            b.displayName.toLowerCase().includes(q) ||
            b.email.toLowerCase().includes(q) ||
            (STAGE_LABELS[b.stage] ?? b.stage).toLowerCase().includes(q)
          );
        })
        .map((b) => ({
          id: b.id,
          displayName: b.displayName,
          statusLabel: STAGE_LABELS[b.stage] ?? b.stage,
          email: b.email,
          updatedAt: b.estimatedReadyDate ?? new Date().toISOString(),
        }));
    }
    return (clientsQuery.data?.items ?? []).map((c) => ({
      id: c.id,
      displayName: c.display_name,
      statusLabel: c.status,
      email: c.email ?? '—',
      updatedAt: c.updated_at,
    }));
  }, [isDemo, search, clientsQuery.data?.items]);

  const totalPages = isDemo
    ? 1
    : Math.max(
        1,
        Math.ceil((clientsQuery.data?.total ?? 0) / (clientsQuery.data?.page_size ?? 20)),
      );

  let loading = false;
  let errorMessage: string | null = null;
  if (!isDemo) {
    if (searchTooShort) {
      errorMessage = 'Enter at least 2 characters to search, or clear the search box.';
    } else if (clientsQuery.isLoading) {
      loading = true;
    } else if (clientsQuery.isError) {
      errorMessage = 'Could not load clients. Confirm the API is running and you are signed in.';
    }
  }

  return (
    <RoleGate
      permission="borrowers.view"
      fallback={<p className="text-sm text-slate-500">No access to borrowers.</p>}
    >
      <PageHeader
        eyebrow="Relationships"
        title="Borrowers"
        description={`${ADVISORY_DISCLAIMER_SHORT} List shows least PII needed (name + status). Maps to platform Clients.`}
      />

      {isDemo ? (
        <p className="mb-4 rounded-brand border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900">
          Demo mode — showing sample borrowers. Sign in with a platform staff account to load live
          clients.
        </p>
      ) : null}

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input
          type="search"
          placeholder="Search borrowers…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="rounded-md border border-navy-900/15 bg-white px-3 py-1.5 text-sm"
        />
        {!isDemo ? (
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as ClientStatus | '');
              setPage(1);
            }}
            className="rounded-md border border-navy-900/15 bg-white px-3 py-1.5 text-sm"
          >
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        ) : null}
      </div>

      <div className="rounded-md border border-navy-900/10 bg-white">
        {loading ? (
          <p className="p-4 text-sm text-slate-500">Loading borrowers…</p>
        ) : errorMessage ? (
          <p className="m-4 rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
            {errorMessage}
          </p>
        ) : (
          <>
            <DataTable
              rows={rows}
              empty="No borrowers match your filters."
              columns={[
                {
                  key: 'name',
                  header: 'Borrower',
                  cell: (r) => (
                    <Link
                      href={`/crm/borrowers/${r.id}`}
                      className="font-medium text-gold-700 hover:underline"
                    >
                      {r.displayName}
                    </Link>
                  ),
                },
                {
                  key: 'status',
                  header: 'Status',
                  cell: (r) => <span className="capitalize">{r.statusLabel}</span>,
                },
                {
                  key: 'email',
                  header: 'Email',
                  cell: (r) => r.email,
                },
                {
                  key: 'updated',
                  header: 'Updated',
                  cell: (r) => formatDate(r.updatedAt),
                },
                {
                  key: 'band',
                  header: 'Readiness band',
                  cell: () => <span className="text-slate-400">—</span>,
                },
              ]}
            />
            {!isDemo && totalPages > 1 ? (
              <div className="flex items-center justify-between border-t border-navy-900/10 px-4 py-3 text-sm">
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="rounded-md border border-navy-900/15 px-3 py-1 disabled:opacity-40"
                >
                  Previous
                </button>
                <span className="text-slate-600">
                  Page {page} of {totalPages}
                </span>
                <button
                  type="button"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="rounded-md border border-navy-900/15 px-3 py-1 disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            ) : null}
          </>
        )}
      </div>
    </RoleGate>
  );
}
