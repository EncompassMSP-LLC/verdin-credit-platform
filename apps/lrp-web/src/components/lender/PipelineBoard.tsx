'use client';

import Link from 'next/link';
import { StatusPill } from '@/components/portal/PortalCard';
import { PIPELINE_BOARD_STAGES, STAGE_LABELS } from '@/lib/lender/nav';
import type { PipelineCard, PipelineStage } from '@/lib/lender/types';
import { formatDate } from '@/lib/utils';

export function PipelineBoard({ cards }: { cards: PipelineCard[] }) {
  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {PIPELINE_BOARD_STAGES.map((stage) => {
        const column = cards.filter((c) => c.stage === (stage as PipelineStage));
        return (
          <section
            key={stage}
            className="w-64 shrink-0 rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800/80"
          >
            <header className="flex items-center justify-between border-b border-navy-900/8 px-3 py-2.5 dark:border-white/10">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-navy-900 dark:text-white">
                {STAGE_LABELS[stage]}
              </h3>
              <span className="tabular-nums text-xs text-slate-500">{column.length}</span>
            </header>
            <ul className="space-y-2 p-2">
              {column.length === 0 ? (
                <li className="px-2 py-6 text-center text-xs text-slate-400">Empty</li>
              ) : (
                column.map((card) => (
                  <li key={card.id}>
                    <Link
                      href={`/lender/borrowers/${card.borrowerId}`}
                      className="block rounded-md border border-navy-900/8 bg-[#F8FAFC] p-3 transition hover:border-gold-500/50 dark:border-white/10 dark:bg-navy-900/40"
                    >
                      <p className="text-sm font-semibold text-navy-900 dark:text-white">
                        {card.borrowerName}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">{card.loName}</p>
                      <div className="mt-2 flex items-center justify-between gap-2">
                        <StatusPill tone={card.readinessScore >= 85 ? 'good' : 'info'}>
                          {card.readinessScore || '—'}
                        </StatusPill>
                        <span className="text-[0.65rem] text-slate-500">
                          {card.daysInStage}d in stage
                        </span>
                      </div>
                      {card.estimatedReadyDate ? (
                        <p className="mt-2 text-[0.65rem] text-slate-500">
                          Est. ready {formatDate(card.estimatedReadyDate)}
                        </p>
                      ) : null}
                    </Link>
                  </li>
                ))
              )}
            </ul>
          </section>
        );
      })}
    </div>
  );
}
