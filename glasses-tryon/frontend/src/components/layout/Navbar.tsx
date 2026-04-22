import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/cn'

export function Navbar() {
  const { pathname } = useLocation()

  return (
    <header className="sticky top-0 z-40 bg-brand-900 border-b border-brand-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-gold-400 flex items-center justify-center shadow-gold transition-transform group-hover:scale-105">
            <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-white" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="7" cy="12" r="3" />
              <circle cx="17" cy="12" r="3" />
              <path d="M10 12h4" />
              <path d="M4 12H2" />
              <path d="M22 12h-2" />
            </svg>
          </div>
          <div className="flex flex-col leading-none">
            <span className="font-bold text-base text-white tracking-widest uppercase">Humaine</span>
            <span className="text-[10px] text-gold-300 tracking-[0.2em] uppercase font-medium">Optical</span>
          </div>
        </Link>

        {/* Nav */}
        <nav className="flex items-center gap-1">
          <NavLink to="/" active={pathname === '/'}>Collection</NavLink>
          <NavLink to="/try-on" active={pathname.startsWith('/try-on')}>Virtual Try-On</NavLink>
        </nav>
      </div>
    </header>
  )
}

function NavLink({ to, active, children }: { to: string; active: boolean; children: React.ReactNode }) {
  return (
    <Link
      to={to}
      className={cn(
        'px-4 py-2 rounded-lg text-sm font-medium transition-all',
        active
          ? 'bg-gold-400 text-white shadow-gold'
          : 'text-brand-200 hover:text-white hover:bg-brand-800',
      )}
    >
      {children}
    </Link>
  )
}
