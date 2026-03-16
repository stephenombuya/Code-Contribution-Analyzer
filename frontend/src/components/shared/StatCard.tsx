import { cn } from '../../utils'

// ── StatCard ──────────────────────────────────────────────────────────────────

interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  icon?: React.ReactNode
  trend?: { direction: 'up' | 'down' | 'neutral'; label: string }
  accent?: string
  className?: string
}

export function StatCard({ label, value, sub, icon, trend, accent = 'brand', className }: StatCardProps) {
  const accentMap: Record<string, string> = {
    brand: 'text-brand-400 bg-brand-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
    red: 'text-red-400 bg-red-500/10',
    violet: 'text-violet-400 bg-violet-500/10',
    sky: 'text-sky-400 bg-sky-500/10',
  }
  const colors = accentMap[accent] || accentMap.brand

  return (
    <div className={cn('stat-card animate-fade-up', className)}>
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
        {icon && (
          <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', colors)}>
            {icon}
          </div>
        )}
      </div>
      <p className="font-display font-bold text-3xl text-white mt-2">{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
      {trend && (
        <div className={cn(
          'inline-flex items-center gap-1 text-xs font-medium mt-2 px-2 py-0.5 rounded-full',
          trend.direction === 'up' ? 'text-emerald-400 bg-emerald-500/10' :
          trend.direction === 'down' ? 'text-red-400 bg-red-500/10' :
          'text-slate-400 bg-slate-700/40'
        )}>
          {trend.direction === 'up' ? '↑' : trend.direction === 'down' ? '↓' : '→'} {trend.label}
        </div>
      )}
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────

export function SkeletonStatCard() {
  return (
    <div className="stat-card">
      <div className="shimmer-line w-20 mb-3" />
      <div className="shimmer-line w-28 h-8 mb-2" />
      <div className="shimmer-line w-16 h-3" />
    </div>
  )
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('card p-6 space-y-3', className)}>
      <div className="shimmer-line w-32 h-5" />
      <div className="shimmer-line w-full h-4" />
      <div className="shimmer-line w-3/4 h-4" />
      <div className="shimmer-line w-1/2 h-4" />
    </div>
  )
}

// ── Empty State ───────────────────────────────────────────────────────────────

interface EmptyStateProps {
  icon: React.ReactNode
  title: string
  description: string
  action?: React.ReactNode
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center px-6">
      <div className="w-16 h-16 rounded-2xl bg-slate-800/60 border border-slate-700/40 flex items-center justify-center mb-5 text-slate-500">
        {icon}
      </div>
      <h3 className="font-semibold text-white mb-2">{title}</h3>
      <p className="text-slate-400 text-sm max-w-xs mb-6">{description}</p>
      {action}
    </div>
  )
}

// ── Badge ─────────────────────────────────────────────────────────────────────

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
  className?: string
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  const variants = {
    default: 'bg-slate-700/60 text-slate-300',
    success: 'bg-emerald-500/15 text-emerald-400',
    warning: 'bg-amber-500/15 text-amber-400',
    error: 'bg-red-500/15 text-red-400',
    info: 'bg-brand-500/15 text-brand-400',
  }
  return (
    <span className={cn('badge', variants[variant], className)}>
      {children}
    </span>
  )
}

// ── Section header ────────────────────────────────────────────────────────────

export function SectionHeader({
  title,
  description,
  action,
}: {
  title: string
  description?: string
  action?: React.ReactNode
}) {
  return (
    <div className="flex items-start justify-between gap-4 mb-6">
      <div>
        <h2 className="font-display font-bold text-xl text-white">{title}</h2>
        {description && <p className="text-sm text-slate-400 mt-0.5">{description}</p>}
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  )
}

// ── Page header ───────────────────────────────────────────────────────────────

export function PageHeader({
  title,
  description,
  action,
}: {
  title: string
  description?: string
  action?: React.ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-4 mb-8">
      <div>
        <h1 className="font-display font-bold text-2xl text-white">{title}</h1>
        {description && <p className="text-slate-400 text-sm mt-1">{description}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
