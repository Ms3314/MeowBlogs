import { cn } from '../lib/utils'

function StatusIcon({ status }) {
  if (status === 'done') {
    return (
      <span className="grid h-7 w-7 place-items-center rounded-full bg-emerald-100 text-emerald-600 ring-1 ring-emerald-200">
        <svg viewBox="0 0 20 20" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="M4 10.5l4 4 8-9" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
    )
  }
  if (status === 'active') {
    return (
      <span className="grid h-7 w-7 place-items-center rounded-full bg-orange-100 ring-1 ring-orange-300">
        <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-orange-400/40 border-t-orange-500" />
      </span>
    )
  }
  if (status === 'error') {
    return (
      <span className="grid h-7 w-7 place-items-center rounded-full bg-rose-100 text-sm font-bold text-rose-600 ring-1 ring-rose-200">
        !
      </span>
    )
  }
  return (
    <span className="grid h-7 w-7 place-items-center rounded-full bg-slate-100 ring-1 ring-slate-200">
      <span className="h-2 w-2 rounded-full bg-slate-300" />
    </span>
  )
}

export default function ProgressTimeline({ steps }) {
  return (
    <ol className="space-y-1">
      {steps.map((step, idx) => (
        <li key={step.key} className="flex items-start gap-3">
          <div className="flex flex-col items-center">
            <StatusIcon status={step.status} />
            {idx < steps.length - 1 && (
              <span
                className={cn(
                  'my-0.5 h-6 w-px',
                  step.status === 'done' ? 'bg-emerald-200' : 'bg-slate-200',
                )}
              />
            )}
          </div>
          <div className="pb-1 pt-0.5">
            <p
              className={cn(
                'text-sm font-medium',
                step.status === 'active'
                  ? 'text-slate-900'
                  : step.status === 'done'
                    ? 'text-slate-700'
                    : step.status === 'error'
                      ? 'text-rose-600'
                      : 'text-slate-400',
              )}
            >
              {step.label}
            </p>
            {step.detail && (
              <p className="mt-0.5 text-xs text-slate-400">{step.detail}</p>
            )}
          </div>
        </li>
      ))}
    </ol>
  )
}
