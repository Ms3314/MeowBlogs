import { cn } from '../../lib/utils'

export default function Input({ className = '', ...props }) {
  return <input className={cn('input', className)} {...props} />
}
