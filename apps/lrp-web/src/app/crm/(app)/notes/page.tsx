'use client';

import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { notes } from '@/lib/crm/data';
import { cn } from '@/lib/utils';

export default function CrmNotesPage() {
  const sorted = [...notes].sort((a, b) => Number(b.pinned) - Number(a.pinned));

  return (
    <RoleGate
      permission="notes.view"
      fallback={<p className="text-sm text-slate-500">No access to notes.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Notes"
        description="Pinned and timeline notes across partners, borrowers, and internal holds."
      />
      <ul className="space-y-3">
        {sorted.map((note) => (
          <li
            key={note.id}
            className={cn(
              'rounded-md border bg-white p-4 dark:bg-navy-800',
              note.pinned
                ? 'border-gold-500/50 dark:border-gold-500/40'
                : 'border-navy-900/10 dark:border-white/10',
            )}
          >
            <div className="flex flex-wrap items-center gap-2 text-xs">
              {note.pinned ? (
                <span className="rounded bg-gold-500/20 px-1.5 py-0.5 font-semibold text-gold-800 dark:text-gold-300">
                  Pinned
                </span>
              ) : null}
              <span className="uppercase tracking-wider text-slate-500">
                {note.relatedType} · {note.relatedName}
              </span>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-navy-900 dark:text-white/90">
              {note.body}
            </p>
            <p className="mt-2 text-xs text-slate-500">
              {note.authorName} · {new Date(note.createdAt).toLocaleString()}
            </p>
          </li>
        ))}
      </ul>
    </RoleGate>
  );
}
