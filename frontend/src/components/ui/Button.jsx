import { cn } from '../../lib/utils'

const VARIANTS = {
  primary: 'btn-primary',
  ghost: 'btn-ghost',
  solid: 'btn bg-slate-900 text-white hover:bg-slate-800',
}

export default function Button({ variant = 'primary', className = '', ...props }) {
  return <button className={cn(VARIANTS[variant] || VARIANTS.primary, className)} {...props} />
}
