'use client';

import { useState } from 'react';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { useCrmAuth } from '@/lib/crm/auth';
import { nurtureDemoEnrollments } from '@/lib/crm/data';
import {
  useCreateNurtureEnrollment,
  useNurtureEnrollments,
  useNurturePrograms,
  useProcessNurtureDue,
  useUpdateNurtureEnrollment,
} from '@/lib/crm/partner-hooks';
import type { NurtureEnrollment } from '@verdin/api-client';

type NurtureRow = {
  id: string;
  contactName: string;
  contactEmail: string;
  status: string;
  currentStepOrder: number;
  nextRunAt: string | null;
  marketingOptIn: boolean;
  programName: string;
};

function mapEnrollment(row: NurtureEnrollment, programName: string): NurtureRow {
  return {
    id: row.id,
    contactName: row.contact_name,
    contactEmail: row.contact_email ?? row.contact_phone ?? '—',
    status: row.status,
    currentStepOrder: row.current_step_order,
    nextRunAt: row.next_run_at,
    marketingOptIn: row.marketing_opt_in,
    programName,
  };
}

export default function CrmNurturePage() {
  const { authMode, can } = useCrmAuth();
  const programsQuery = useNurturePrograms();
  const enrollmentsQuery = useNurtureEnrollments();
  const createEnrollment = useCreateNurtureEnrollment();
  const updateEnrollment = useUpdateNurtureEnrollment();
  const processDue = useProcessNurtureDue();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [optIn, setOptIn] = useState(true);

  const programNameById = new Map((programsQuery.data ?? []).map((p) => [p.id, p.name] as const));
  const defaultProgram = programsQuery.data?.[0];

  const liveRows =
    authMode === 'platform' && enrollmentsQuery.data
      ? enrollmentsQuery.data.map((row) =>
          mapEnrollment(row, programNameById.get(row.program_id) ?? 'Nurture program'),
        )
      : null;
  const rows = liveRows ?? nurtureDemoEnrollments;
  const usingDemo = liveRows === null;

  return (
    <RoleGate
      permission="nurture.view"
      fallback={<p className="text-sm text-slate-500">No access to nurture drips.</p>}
    >
      <PageHeader
        eyebrow="Engagement"
        title="Partner nurture"
        description="Claim-safe lender drip with marketing opt-in, TCPA-gated SMS, and idempotent step delivery (LRP-206)."
      />
      {usingDemo ? (
        <p className="mb-3 text-xs text-slate-500">
          Showing demo enrollments — sign in with platform auth for live nurture programs.
        </p>
      ) : null}
      {programsQuery.isError || enrollmentsQuery.isError ? (
        <p className="mb-3 text-sm text-red-600">Could not load nurture data.</p>
      ) : null}

      {!usingDemo && can('nurture.manage') ? (
        <div className="mb-6 space-y-4 rounded-md border border-navy-900/10 bg-white p-4 dark:border-white/10 dark:bg-navy-800">
          <div className="flex flex-wrap items-end gap-3">
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-slate-600">Contact name</span>
              <input
                className="rounded-md border border-navy-900/15 px-2 py-1.5 dark:border-white/15 dark:bg-navy-900"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-slate-600">Email</span>
              <input
                type="email"
                className="rounded-md border border-navy-900/15 px-2 py-1.5 dark:border-white/15 dark:bg-navy-900"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <input type="checkbox" checked={optIn} onChange={(e) => setOptIn(e.target.checked)} />
              Marketing opt-in
            </label>
            <button
              type="button"
              className="rounded-md border border-navy-900/15 px-3 py-1.5 text-sm font-medium hover:bg-slate-50 disabled:opacity-50 dark:border-white/15 dark:hover:bg-navy-700"
              disabled={
                createEnrollment.isPending ||
                !defaultProgram ||
                !name.trim() ||
                !email.trim() ||
                !optIn
              }
              onClick={() => {
                if (!defaultProgram) return;
                createEnrollment.mutate(
                  {
                    program_id: defaultProgram.id,
                    contact_name: name.trim(),
                    contact_email: email.trim(),
                    marketing_opt_in: optIn,
                    tcpa_consent: false,
                  },
                  {
                    onSuccess: () => {
                      setName('');
                      setEmail('');
                      setOptIn(true);
                    },
                  },
                );
              }}
            >
              {createEnrollment.isPending ? 'Enrolling…' : 'Enroll contact'}
            </button>
            <button
              type="button"
              className="rounded-md border border-navy-900/15 px-3 py-1.5 text-sm font-medium hover:bg-slate-50 disabled:opacity-50 dark:border-white/15 dark:hover:bg-navy-700"
              disabled={processDue.isPending}
              onClick={() => processDue.mutate()}
            >
              {processDue.isPending ? 'Processing…' : 'Process due steps'}
            </button>
          </div>
          {defaultProgram ? (
            <p className="text-xs text-slate-500">
              Program: {defaultProgram.name} · {defaultProgram.steps.length} steps · lifecycle{' '}
              {defaultProgram.enrollment_lifecycle_stage}
            </p>
          ) : null}
          {processDue.isSuccess ? (
            <p className="text-xs text-slate-500">
              Processed {processDue.data.processed_count} delivery run(s).
            </p>
          ) : null}
          {createEnrollment.isError || processDue.isError ? (
            <p className="text-xs text-red-600">Could not complete nurture action.</p>
          ) : null}
        </div>
      ) : null}

      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={rows}
          columns={[
            {
              key: 'contact',
              header: 'Contact',
              cell: (r) => (
                <div>
                  <p className="font-medium">{r.contactName}</p>
                  <p className="text-xs text-slate-500">{r.contactEmail}</p>
                </div>
              ),
            },
            { key: 'program', header: 'Program', cell: (r) => r.programName },
            {
              key: 'status',
              header: 'Status',
              cell: (r) =>
                !usingDemo &&
                can('nurture.manage') &&
                (r.status === 'active' || r.status === 'paused') ? (
                  <button
                    type="button"
                    className="text-sm underline decoration-slate-300 underline-offset-2"
                    disabled={updateEnrollment.isPending}
                    onClick={() =>
                      updateEnrollment.mutate({
                        enrollmentId: r.id,
                        body: { status: r.status === 'active' ? 'paused' : 'active' },
                      })
                    }
                  >
                    {r.status}
                  </button>
                ) : (
                  r.status
                ),
            },
            {
              key: 'step',
              header: 'Step',
              cell: (r) => String(r.currentStepOrder),
            },
            {
              key: 'next',
              header: 'Next run',
              cell: (r) => (r.nextRunAt ? new Date(r.nextRunAt).toLocaleString() : '—'),
            },
            {
              key: 'optIn',
              header: 'Opt-in',
              cell: (r) => (r.marketingOptIn ? 'Yes' : 'No'),
            },
            {
              key: 'actions',
              header: '',
              cell: (r) =>
                !usingDemo &&
                can('nurture.manage') &&
                r.status !== 'exited' &&
                r.status !== 'completed' ? (
                  <button
                    type="button"
                    className="text-xs text-red-700 underline decoration-red-200 underline-offset-2"
                    disabled={updateEnrollment.isPending}
                    onClick={() =>
                      updateEnrollment.mutate({
                        enrollmentId: r.id,
                        body: { status: 'exited', exit_reason: 'manual_exit' },
                      })
                    }
                  >
                    Remove
                  </button>
                ) : (
                  '—'
                ),
            },
          ]}
        />
      </div>
    </RoleGate>
  );
}
