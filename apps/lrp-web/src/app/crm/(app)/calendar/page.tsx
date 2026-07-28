'use client';

import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { useCrmAuth } from '@/lib/crm/auth';
import { calendarEvents } from '@/lib/crm/data';
import { useCrmAppointments, useProcessAppointmentReminders } from '@/lib/crm/partner-hooks';
import type { CalendarEvent, CalendarEventType } from '@/lib/crm/types';
import type { CrmAppointment } from '@verdin/api-client';

function mapAppointment(row: CrmAppointment): CalendarEvent {
  const type = (
    row.appointment_type === 'consultation' ? 'consultation' : row.appointment_type
  ) as CalendarEventType;
  return {
    id: row.id,
    title: row.title,
    startsAt: row.starts_at,
    endsAt: row.ends_at,
    type,
    relatedName: row.related_name || row.borrower_name || '—',
    ownerName: row.owner_user_id ? 'Assigned staff' : 'Unassigned',
    location: row.location || row.meeting_url,
  };
}

export default function CrmCalendarPage() {
  const { authMode, can } = useCrmAuth();
  const appointmentsQuery = useCrmAppointments();
  const processReminders = useProcessAppointmentReminders();

  const liveRows =
    authMode === 'platform' && appointmentsQuery.data
      ? appointmentsQuery.data.map(mapAppointment)
      : null;
  const rows = [...(liveRows ?? calendarEvents)].sort(
    (a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime(),
  );
  const usingDemo = liveRows === null;

  return (
    <RoleGate
      permission="calendar.view"
      fallback={<p className="text-sm text-slate-500">No access to calendar.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Calendar"
        description="Consultations and follow-ups with T-24h / T-1h reminders (LRP-205). SMS requires TCPA consent."
      />
      {usingDemo ? (
        <p className="mb-3 text-xs text-slate-500">
          Showing demo events — sign in with platform auth for live appointments.
        </p>
      ) : null}
      {!usingDemo && can('calendar.manage') ? (
        <div className="mb-4">
          <button
            type="button"
            className="rounded-md border border-navy-900/15 px-3 py-1.5 text-sm font-medium hover:bg-slate-50 disabled:opacity-50 dark:border-white/15 dark:hover:bg-navy-700"
            disabled={processReminders.isPending}
            onClick={() => processReminders.mutate()}
          >
            {processReminders.isPending ? 'Processing…' : 'Process due reminders'}
          </button>
          {processReminders.isSuccess ? (
            <p className="mt-2 text-xs text-slate-500">
              Processed {processReminders.data.processed_count} reminder run(s).
            </p>
          ) : null}
          {processReminders.isError ? (
            <p className="mt-2 text-xs text-red-600">Could not process reminders.</p>
          ) : null}
        </div>
      ) : null}
      <ul className="space-y-3">
        {rows.map((event) => (
          <li
            key={event.id}
            className="flex flex-col gap-2 rounded-md border border-navy-900/10 bg-white p-4 sm:flex-row sm:items-center sm:justify-between dark:border-white/10 dark:bg-navy-800"
          >
            <div>
              <p className="text-[0.65rem] font-semibold uppercase tracking-wider text-gold-600">
                {event.type.replace('_', ' ')}
              </p>
              <h2 className="mt-1 font-semibold">{event.title}</h2>
              <p className="mt-1 text-sm text-slate-600 dark:text-white/65">
                {event.relatedName} · {event.ownerName}
                {event.location ? ` · ${event.location}` : ''}
              </p>
            </div>
            <p className="shrink-0 text-sm font-medium">
              {new Date(event.startsAt).toLocaleString()}
            </p>
          </li>
        ))}
      </ul>
    </RoleGate>
  );
}
