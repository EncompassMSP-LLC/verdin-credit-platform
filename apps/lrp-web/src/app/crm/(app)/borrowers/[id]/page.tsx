'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { borrowers, notes, tasks, documents } from '@/lib/crm/data';
import { STAGE_LABELS } from '@/lib/crm/nav';

export default function CrmBorrowerDetailPage() {
  const params = useParams();
  const id = String(params.id);
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
            className="text-sm font-medium text-gold-700 hover:underline dark:text-gold-400"
          >
            ← All borrowers
          </Link>
        }
      />

      <div className="grid gap-4 lg:grid-cols-3">
        <section className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800 lg:col-span-2">
          <dl className="grid gap-4 sm:grid-cols-2 text-sm">
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Stage</dt>
              <dd className="mt-1 font-medium">{STAGE_LABELS[borrower.stage]}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Readiness</dt>
              <dd className="mt-1 font-medium">
                {borrower.readinessScore} · {borrower.readinessBand}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Lender</dt>
              <dd className="mt-1 font-medium">{borrower.lenderName ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Realtor</dt>
              <dd className="mt-1 font-medium">{borrower.realtorName ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Est. ready</dt>
              <dd className="mt-1 font-medium">{borrower.estimatedReadyDate ?? 'TBD'}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wider text-slate-500">Source</dt>
              <dd className="mt-1 font-medium">{borrower.source}</dd>
            </div>
          </dl>
          {borrower.blockers.length ? (
            <div className="mt-5">
              <h2 className="text-sm font-semibold">Blockers</h2>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600 dark:text-white/70">
                {borrower.blockers.map((b) => (
                  <li key={b}>{b}</li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="mt-5 text-sm text-slate-500">No open blockers.</p>
          )}
        </section>

        <section className="space-y-4">
          <div className="rounded-md border border-navy-900/10 bg-white p-4 dark:border-white/10 dark:bg-navy-800">
            <h2 className="text-sm font-semibold">Tasks</h2>
            <ul className="mt-2 space-y-2 text-sm">
              {relatedTasks.length ? (
                relatedTasks.map((t) => (
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
          <div className="rounded-md border border-navy-900/10 bg-white p-4 dark:border-white/10 dark:bg-navy-800">
            <h2 className="text-sm font-semibold">Documents</h2>
            <ul className="mt-2 space-y-2 text-sm">
              {relatedDocs.map((d) => (
                <li key={d.id}>
                  {d.name} <span className="text-xs text-slate-500">({d.status})</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-md border border-navy-900/10 bg-white p-4 dark:border-white/10 dark:bg-navy-800">
            <h2 className="text-sm font-semibold">Notes</h2>
            <ul className="mt-2 space-y-3 text-sm">
              {relatedNotes.length ? (
                relatedNotes.map((n) => (
                  <li key={n.id} className="text-slate-600 dark:text-white/70">
                    {n.body}
                    <span className="mt-1 block text-xs text-slate-400">— {n.authorName}</span>
                  </li>
                ))
              ) : (
                <li className="text-slate-500">No notes</li>
              )}
            </ul>
          </div>
        </section>
      </div>
    </RoleGate>
  );
}
