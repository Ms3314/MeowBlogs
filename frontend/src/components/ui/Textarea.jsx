import { cn } from '../../lib/utils'

export default function Textarea({ className = '', ...props }) {
  return <textarea className={cn('input resize-none', className)} {...props} />
}
