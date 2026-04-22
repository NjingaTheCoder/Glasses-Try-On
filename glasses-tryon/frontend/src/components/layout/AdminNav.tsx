import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { cn } from '@/lib/cn'

export function AdminNav() {
  const { logout } = useAuthStore()
  const navigate = useNavigate()
  const { pathname } = useLocation()

  async function handleLogout() {
    await logout()
    navigate('/admin/login')
  }

  return (
    <header className="sticky top-0 z-40 bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link to="/" className="font-bold text-white">👓 GlassTry</Link>
          <span className="text-gray-400 text-sm">Admin</span>
          <AdminNavLink to="/admin" active={pathname === '/admin'}>Dashboard</AdminNavLink>
          <AdminNavLink to="/admin/products/new" active={pathname === '/admin/products/new'}>
            + New Product
          </AdminNavLink>
        </div>
        <button onClick={handleLogout} className="text-sm text-gray-300 hover:text-white transition-colors">
          Sign out
        </button>
      </div>
    </header>
  )
}

function AdminNavLink({ to, active, children }: { to: string; active: boolean; children: React.ReactNode }) {
  return (
    <Link
      to={to}
      className={cn(
        'text-sm transition-colors',
        active ? 'text-white font-medium' : 'text-gray-400 hover:text-white',
      )}
    >
      {children}
    </Link>
  )
}
