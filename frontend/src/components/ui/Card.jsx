import { cn } from '../../lib/utils'

export default function Card({ className = '', children, ...props }) {
  return (
    <div className={cn('card p-6', className)} {...props}>
      {children}
    </div>
  )
}
