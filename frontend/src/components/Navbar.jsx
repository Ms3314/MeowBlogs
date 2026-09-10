import { Link, NavLink } from 'react-router-dom'
import { cn } from '../lib/utils'

function NavItem({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cn(
          'rounded-full px-4 py-1.5 text-sm font-medium transition',
          isActive ? 'bg-orange-100 text-orange-700' : 'text-slate-500 hover:text-slate-900',
        )
      }
    >
      {children}
    </NavLink>
  )
}

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 px-4 pt-4">
      <nav className="mx-auto flex max-w-5xl items-center justify-between gap-2 rounded-2xl border border-orange-100 bg-white/80 px-3 py-2 shadow-lg shadow-orange-900/5 backdrop-blur-xl">
        <Link to="/" className="flex items-center gap-2.5 rounded-full px-2 py-1">
          <span className="text-sm font-bold tracking-tight text-slate-900">MeowBlogs</span>
        </Link>

        <div className="flex items-center gap-1">
          <NavItem to="/">Home</NavItem>
          <NavItem to="/history">History</NavItem>
          <Link
            to="/generate"
            className="ml-1 rounded-full bg-orange-500 px-4 py-1.5 text-sm font-semibold text-white transition hover:bg-orange-600"
          >
            New blog
          </Link>
        </div>
      </nav>
    </header>
  )
}
