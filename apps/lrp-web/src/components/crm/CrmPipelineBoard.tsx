import { PIPELINE_BOARD_STAGES, STAGE_LABELS } from '@/lib/crm/nav';
import type { PipelineCard } from '@/lib/crm/types';
import { cn } from '@/lib/utils';

export function CrmPipelineBoard({ cards }: { cards: PipelineCard[] }) {
  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {PIPELINE_BOARD_STAGES.map((stage) => {
        const column = cards.filter((c) => c.stage === stage);
        return (
          <section
            key={stage}
            className="w-[15.5rem] shrink-0 rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800"
          >
            <header className="flex items-center justify-between border-b border-navy-900/10 px-3 py-2.5 dark:border-white/10">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-white/55">
                {STAGE_LABELS[stage]}
              </h2>
              <span className="rounded bg-sand-100 px-1.5 py-0.5 text-[0.65rem] font-semibold text-navy-900 dark:bg-white/10 dark:text-white">
                {column.length}
              </span>
            </header>
            <ul className="space-y-2 p-2">
              {column.map((card) => (
                <li
                  key={card.id}
                  className={cn(
                    'rounded-md border border-navy-900/8 bg-[#F8FAFC] p-3 dark:border-white/10 dark:bg-navy-900/50',
                  )}
                >
                  <p className="text-sm font-semibold text-navy-900 dark:text-white">
                    {card.borrowerName}
                  </p>
                  <p className="mt-1 text-xs text-slate-500 dark:text-white/55">
                    {card.partnerName} · {card.loName}
                  </p>
                  <div className="mt-2 flex items-center justify-between text-xs">
                    <span className="font-medium text-gold-700 dark:text-gold-400">
                      Score {card.readinessScore}
                    </span>
                    <span className="text-slate-500 dark:text-white/50">{card.daysInStage}d</span>
                  </div>
                </li>
              ))}
              {!column.length ? (
                <li className="px-2 py-6 text-center text-xs text-slate-400">Empty</li>
              ) : null}
            </ul>
          </section>
        );
      })}
    </div>
  );
}
