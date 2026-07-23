'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { ApiClientError } from '@verdin/api-client';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { useCrmAuth } from '@/lib/crm/auth';
import {
  useCreateCrmCreditAnalysis,
  useCrmClient,
  useCrmClientCases,
  useCrmLatestAnalysis,
} from '@/lib/crm/client-hooks';
import { borrowers, notes, tasks, documents } from '@/lib/crm/data';
import { STAGE_LABELS } from '@/lib/crm/nav';
import { formatDate } from '@/lib/utils';

/**
 * Spec: Vol 21 · pages/borrower-workspace.md (overview + run_analysis / publish_score)
 * Platform: getClient + cases + latest credit-analysis; POST compose+publish.
 * Demo: seed borrower. Tasks/docs/notes remain demo-linked until later slices.
 */
export default function CrmBorrowerDetailPage() {
  const params = useParams();
  const id = String(params.id);
  const { authMode, can } = useCrmAuth();
  const isDemo = authMode === 'demo';

  const clientQuery = useCrmClient(isDemo ? undefined : id);
  const casesQuery = useCrmClientCases(isDemo ? undefined : id);
  const primaryCase = casesQuery.data?.[0];
  const analysisQuery = useCrmLatestAnalysis(primaryCase?.id);
  const runAnalysis = useCreateCrmCreditAnalysis(primaryCase?.id);
  const canRunAnalysis = can('borrowers.manage');

  if (isDemo) {
    const borrower = borrowers.find((b) => b.id === id);
    if (!borrower) {
      return (
        <p className="text-sm text-slate-500">
          Borrower not found. <Link href="/crm/borrowers">Back to list</Link>
        </p>
      );
    }

    const relatedNotes = notes.filter((n) => n.relatedId === id);
    const relatedTasks = tasks.filter((t) => t.relatedId === id);
    const relatedDocs = documents.filter((d) => d.relatedName === borrower.displayName);

    return (
      <RoleGate
        permission="borrowers.view"
        fallback={<p className="text-sm text-slate-500">No access.</p>}
      >
        <PageHeader
          eyebrow="Borrower"
          title={borrower.displayName}
          description={`${borrower.email} · ${borrower.phone} · ${borrower.loanGoal}`}
          actions={
            <Link
              href="/crm/borrowers"
              className="text-sm font-medium text-gold-700 hover:underline"
            >
              ← All borrowers
            </Link>
          }
        />
        <p className="mb-4 rounded-brand border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900">
          Demo mode — sample workspace. Platform auth loads live client + case readiness.
        </p>
        <DemoWorkspace
          stage={STAGE_LABELS[borrower.stage] ?? borrower.stage}
          readiness={`${borrower.readinessScore} · ${borrower.readinessBand}`}
          lender={borrower.lenderName ?? '—'}
          realtor={borrower.realtorName ?? '—'}
          estReady={borrower.estimatedReadyDate ?? 'TBD'}
          source={borrower.source}
          blockers={borrower.blockers}
          tasks={relatedTasks.map((t) => ({ id: t.id, title: t.title, status: t.status }))}
          docs={relatedDocs.map((d) => ({ id: d.id, name: d.name, status: d.status }))}
          notes={relatedNotes.map((n) => ({ id: n.id, body: n.body, author: n.authorName }))}
        />
      </RoleGate>
    );
  }

  if (clientQuery.isLoading || casesQuery.isLoading) {
    return <p className="text-sm text-slate-500">Loading borrower workspace…</p>;
  }

  if (clientQuery.isError || !clientQuery.data) {
    return (
      <p className="text-sm text-slate-500">
        Borrower not found. <Link href="/crm/borrowers">Back to list</Link>
      </p>
    );
  }

  const client = clientQuery.data;
  const mailing = [client.mailing_city, client.mailing_state].filter(Boolean).join(', ') || '—';
  const analysis = analysisQuery.data;
  const readinessLabel = analysis
    ? `${analysis.band}${analysis.borrower_readiness_score != null ? ` · score ${analysis.borrower_readiness_score}` : ''}`
    : analysisQuery.isLoading
      ? 'Loading…'
      : 'No published analysis';

  const runError =
    runAnalysis.error instanceof ApiClientError
      ? runAnalysis.error.message
      : runAnalysis.error
        ? 'Could not run credit analysis.'
        : null;

  return (
    <RoleGate
      permission="borrowers.view"
      fallback={<p className="text-sm text-slate-500">No access.</p>}
    >
      <PageHeader
        eyebrow="Borrower"
        title={client.display_name}
        description={`${client.email ?? 'No email'} · ${client.phone ?? 'No phone'} · ${mailing}`}
        actions={
          <Link href="/crm/borrowers" className="text-sm font-medium text-gold-700 hover:underline">
            ← All borrowers
          </Link>
        }
      />
      <p className="mb-4 text-sm text-slate-600">
        {ADVISORY_DISCLAIMER_SHORT} Staff-mediated disputes only — human approval required before
        send.
      </p>

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="rounded-md border border-navy-900/10 bg-white p-5 lg:col-span-2">
          <dl className="grid gap-4 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Client status</dt>
              <dd className="mt-1 font-medium capitalize">{client.status}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Primary case</dt>
              <dd className="mt-1 font-medium">
                {primaryCase
                  ? `${primaryCase.title} · ${primaryCase.stage.replace(/_/g, ' ')}`
                  : 'No case linked'}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Readiness band</dt>
              <dd className="mt-1 font-medium capitalize">{readinessLabel}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">
                Mortgage readiness
              </dt>
              <dd className="mt-1 font-medium">
                {analysis?.mortgage_readiness_score != null
                  ? analysis.mortgage_readiness_score
                  : '—'}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Last run</dt>
              <dd className="mt-1 font-medium">
                {analysis?.generated_at ? formatDate(analysis.generated_at) : '—'}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Case updated</dt>
              <dd className="mt-1 font-medium">
                {primaryCase ? formatDate(primaryCase.updated_at) : '—'}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-xs uppercase tracking-wider text-slate-500">Notes</dt>
              <dd className="mt-1 font-medium whitespace-pre-wrap">
                {client.notes?.trim() || '—'}
              </dd>
            </div>
          </dl>
          {casesQuery.data && casesQuery.data.length > 1 ? (
            <div className="mt-5">
              <h2 className="text-sm font-semibold">All cases</h2>
              <ul className="mt-2 space-y-1 text-sm text-slate-600">
                {casesQuery.data.map((c) => (
                  <li key={c.id}>
                    {c.title}{' '}
                    <span className="text-xs text-slate-400">
                      ({c.stage.replace(/_/g, ' ')} · {c.status})
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>

        <section className="space-y-4">
          <div className="rounded-md border border-navy-900/10 bg-white p-4">
            <h2 className="text-sm font-semibold">Credit analysis</h2>
            <p className="mt-2 text-sm text-slate-500">
              Queue a deterministic Lending Readiness compose. Latest run is what the borrower
              portal can see (advisory band only).
            </p>
            {!primaryCase ? (
              <p className="mt-3 text-sm text-amber-800">Link a case before running analysis.</p>
            ) : canRunAnalysis ? (
              <button
                type="button"
                className="mt-3 inline-flex items-center justify-center rounded-md bg-navy-900 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
                disabled={runAnalysis.isPending}
                onClick={() => runAnalysis.mutate()}
              >
                {runAnalysis.isPending ? 'Running…' : 'Run / publish readiness'}
              </button>
            ) : (
              <p className="mt-3 text-sm text-slate-500">
                Requires borrowers.manage to queue analysis.
              </p>
            )}
            {runAnalysis.isSuccess ? (
              <p className="mt-2 text-sm text-teal-800">
                Published band {runAnalysis.data.band}
                {runAnalysis.data.borrower_readiness_score != null
                  ? ` · score ${runAnalysis.data.borrower_readiness_score}`
                  : ''}
                .
              </p>
            ) : null}
            {runError ? <p className="mt-2 text-sm text-red-700">{runError}</p> : null}
          </div>
          <div className="rounded-md border border-navy-900/10 bg-white p-4">
            <h2 className="text-sm font-semibold">Tasks</h2>
            <p className="mt-2 text-sm text-slate-500">
              Live task queue lands in a later CRM slice.
            </p>
          </div>
          <div className="rounded-md border border-navy-900/10 bg-white p-4">
            <h2 className="text-sm font-semibold">Documents</h2>
            <p className="mt-2 text-sm text-slate-500">
              Live document queue lands in a later CRM slice.
            </p>
          </div>
          <div className="rounded-md border border-navy-900/10 bg-white p-4">
            <h2 className="text-sm font-semibold">Activity</h2>
            <p className="mt-2 text-sm text-slate-500">
              Notes / timeline land in a later CRM slice.
            </p>
          </div>
        </section>
      </div>
    </RoleGate>
  );
}

function DemoWorkspace({
  stage,
  readiness,
  lender,
  realtor,
  estReady,
  source,
  blockers,
  tasks,
  docs,
  notes,
}: {
  stage: string;
  readiness: string;
  lender: string;
  realtor: string;
  estReady: string;
  source: string;
  blockers: string[];
  tasks: { id: string; title: string; status: string }[];
  docs: { id: string; name: string; status: string }[];
  notes: { id: string; body: string; author: string }[];
}) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <section className="rounded-md border border-navy-900/10 bg-white p-5 lg:col-span-2">
        <dl className="grid gap-4 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-xs uppercase tracking-wider text-slate-500">Stage</dt>
            <dd className="mt-1 font-medium">{stage}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-slate-500">Readiness</dt>
            <dd className="mt-1 font-medium">{readiness}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-slate-500">Lender</dt>
            <dd className="mt-1 font-medium">{lender}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-slate-500">Realtor</dt>
            <dd className="mt-1 font-medium">{realtor}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-slate-500">Est. ready</dt>
            <dd className="mt-1 font-medium">{estReady}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-slate-500">Source</dt>
            <dd className="mt-1 font-medium">{source}</dd>
          </div>
        </dl>
        {blockers.length ? (
          <div className="mt-5">
            <h2 className="text-sm font-semibold">Blockers</h2>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
              {blockers.map((b) => (
                <li key={b}>{b}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="mt-5 text-sm text-slate-500">No open blockers.</p>
        )}
      </section>
      <section className="space-y-4">
        <div className="rounded-md border border-navy-900/10 bg-white p-4">
          <h2 className="text-sm font-semibold">Tasks</h2>
          <ul className="mt-2 space-y-2 text-sm">
            {tasks.length ? (
              tasks.map((t) => (
                <li key={t.id}>
                  <span className="font-medium">{t.title}</span>
                  <span className="block text-xs text-slate-500">{t.status}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-500">None linked</li>
            )}
          </ul>
        </div>
        <div className="rounded-md border border-navy-900/10 bg-white p-4">
          <h2 className="text-sm font-semibold">Documents</h2>
          <ul className="mt-2 space-y-2 text-sm">
            {docs.map((d) => (
              <li key={d.id}>
                {d.name} <span className="text-xs text-slate-500">({d.status})</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-md border border-navy-900/10 bg-white p-4">
          <h2 className="text-sm font-semibold">Notes</h2>
          <ul className="mt-2 space-y-3 text-sm">
            {notes.length ? (
              notes.map((n) => (
                <li key={n.id} className="text-slate-600">
                  {n.body}
                  <span className="mt-1 block text-xs text-slate-400">— {n.author}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-500">No notes</li>
            )}
          </ul>
        </div>
      </section>
    </div>
  );
}
