'use client';

import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { calendarEvents } from '@/lib/crm/data';

export default function CrmCalendarPage() {
  const sorted = [...calendarEvents].sort(
    (a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime(),
  );

  return (
    <RoleGate
      permission="calendar.view"
      fallback={<p className="text-sm text-slate-500">No access to calendar.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Calendar"
        description="Meetings, calls, deadlines, and follow-ups across partners and borrowers."
      />
      <ul className="space-y-3">
        {sorted.map((event) => (
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
