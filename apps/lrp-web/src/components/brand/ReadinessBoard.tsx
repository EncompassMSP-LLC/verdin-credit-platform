'use client';

import { motion, useReducedMotion } from 'framer-motion';

/** Product-context visual: readiness path board used as hero anchor. */
export function ReadinessBoard({ className }: { className?: string }) {
  const reduce = useReducedMotion();

  return (
    <div
      className={className}
      role="img"
      aria-label="Illustration of a lending readiness board showing diagnose, orchestrate, signal, and advance stages"
    >
      <div className="relative overflow-hidden rounded-lg bg-white/95 p-5 shadow-soft ring-1 ring-navy-900/10 sm:p-6">
        <div className="flex items-center justify-between gap-4 border-b border-navy-900/8 pb-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">
              Readiness summary
            </p>
            <p className="mt-1 font-sans text-xl font-semibold uppercase tracking-wide text-navy-900">
              Near-miss pipeline
            </p>
          </div>
          <span className="rounded-brand bg-gold-500/15 px-2.5 py-1 text-xs font-semibold text-gold-700">
            3 active stages
          </span>
        </div>

        <ol className="mt-5 space-y-3">
          {[
            { label: 'Diagnose', detail: 'Credit & file blockers identified', state: 'complete' },
            { label: 'Orchestrate', detail: 'Staff-mediated work in progress', state: 'active' },
            { label: 'Signal', detail: 'Partner-ready status pending export', state: 'next' },
            { label: 'Advance', detail: 'Lender review handoff', state: 'next' },
          ].map((step, index) => (
            <li key={step.label} className="flex items-start gap-3">
              <motion.span
                className={
                  step.state === 'complete'
                    ? 'mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-[0.65rem] font-bold text-white'
                    : step.state === 'active'
                      ? 'mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-navy-900 text-[0.65rem] font-bold text-white'
                      : 'mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-sand-200 text-[0.65rem] font-bold text-slate-500'
                }
                initial={reduce ? false : { scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.15 * index, duration: 0.35 }}
                aria-hidden
              >
                {index + 1}
              </motion.span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium text-navy-900">{step.label}</p>
                  <span className="text-xs text-slate-500">
                    {step.state === 'complete'
                      ? 'Complete'
                      : step.state === 'active'
                        ? 'In progress'
                        : 'Queued'}
                  </span>
                </div>
                <p className="mt-0.5 text-sm text-ink-700">{step.detail}</p>
                {step.state === 'active' ? (
                  <motion.div
                    className="mt-2 h-1 overflow-hidden rounded-full bg-sand-200"
                    initial={false}
                  >
                    <motion.div
                      className="h-full origin-left bg-progress-accent"
                      initial={reduce ? { scaleX: 0.62 } : { scaleX: 0 }}
                      animate={{ scaleX: 0.62 }}
                      transition={{ delay: 0.4, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                    />
                  </motion.div>
                ) : null}
              </div>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
