import { cn } from '../../lib/utils'

const TONES = {
  default: 'border-slate-200 bg-slate-50 text-slate-600',
  brand: 'border-orange-200 bg-orange-50 text-orange-700',
  green: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  amber: 'border-amber-200 bg-amber-50 text-amber-700',
  sky: 'border-violet-200 bg-violet-50 text-violet-700',
}

export default function Badge({ tone = 'default', className = '', children }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium',
        TONES[tone] || TONES.default,
        className,
      )}
    >
      {children}
    </span>
  )
}
