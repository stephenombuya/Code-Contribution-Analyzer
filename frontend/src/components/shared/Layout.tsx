import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, GitBranch, BookOpen, History,
  Settings, LogOut, Menu, X, ChevronRight, Zap
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { cn, PLATFORM_INFO } from '../../utils'

const NAV = [
  { label: 'Dashboard',    href: '/dashboard',    icon: LayoutDashboard },
  { label: 'Run Analysis', href: '/analysis',     icon: Zap },
  { label: 'Repositories', href: '/repositories', icon: BookOpen },
  { label: 'History',      href: '/history',      icon: History },
  { label: 'Settings',     href: '/settings',     icon: Settings },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-surface-950">
      {/* ── Sidebar ──────────────────────────────────────────────────── */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col w-64 bg-surface-900 border-r border-slate-800/60',
          'transition-transform duration-300 lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-800/60">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center shadow-lg shadow-brand-900/50">
            <GitBranch className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="font-display font-bold text-sm text-white leading-none">CodeAnalyzer</p>
            <p className="text-xs text-slate-500 mt-0.5">Contribution Insights</p>
          </div>
          <button
            onClick={() => setOpen(false)}
            className="ml-auto lg:hidden text-slate-500 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV.map(({ label, href, icon: Icon }) => (
            <NavLink
              key={href}
              to={href}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all duration-200 group',
                  isActive
                    ? 'bg-brand-600/15 text-brand-400 font-medium'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={cn('w-4 h-4 flex-shrink-0', isActive ? 'text-brand-400' : 'text-slate-500 group-hover:text-slate-300')} />
                  <span className="flex-1">{label}</span>
                  {isActive && <ChevronRight className="w-3 h-3 text-brand-500" />}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Connected Platforms */}
        {user && user.platforms && user.platforms.length > 0 && (
          <div className="px-4 py-3 mx-3 mb-3 rounded-xl bg-slate-800/40 border border-slate-700/30">
            <p className="text-xs text-slate-500 font-medium mb-2">Connected</p>
            <div className="flex gap-2">
              {user.platforms.map((p) => (
                <span
                  key={p}
                  className="text-xs px-2 py-1 rounded-lg bg-slate-700/60 text-slate-300 capitalize"
                >
                  {PLATFORM_INFO[p]?.icon} {PLATFORM_INFO[p]?.label}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* User */}
        <div className="border-t border-slate-800/60 p-4">
          <div className="flex items-center gap-3">
            {user?.avatar_url ? (
              <img
                src={user.avatar_url}
                alt={user.name || ''}
                className="w-8 h-8 rounded-full ring-2 ring-brand-500/30"
              />
            ) : (
              <div className="w-8 h-8 rounded-full bg-brand-700 flex items-center justify-center text-white text-xs font-bold">
                {(user?.name || user?.email || '?')[0].toUpperCase()}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.name || 'User'}</p>
              <p className="text-xs text-slate-500 truncate">{user?.email || ''}</p>
            </div>
            <button
              onClick={handleLogout}
              className="text-slate-500 hover:text-red-400 transition-colors"
              title="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* ── Main ────────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col lg:ml-64 min-h-0">
        {/* Mobile header */}
        <header className="lg:hidden flex items-center gap-4 px-4 py-3 bg-surface-900 border-b border-slate-800/60">
          <button
            onClick={() => setOpen(true)}
            className="text-slate-400 hover:text-white"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <GitBranch className="w-4 h-4 text-brand-400" />
            <span className="font-display font-bold text-sm">CodeAnalyzer</span>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
