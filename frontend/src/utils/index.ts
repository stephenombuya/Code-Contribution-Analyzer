// ── Number formatting ─────────────────────────────────────────────────────────

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toLocaleString()
}

export function formatLines(n: number): string {
  const abs = Math.abs(n)
  const prefix = n < 0 ? '-' : '+'
  return `${prefix}${formatNumber(abs)}`
}

// ── Date formatting ───────────────────────────────────────────────────────────

export function formatDate(iso: string): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

export function formatMonth(ym: string): string {
  if (!ym || ym === 'unknown') return ym
  const [y, m] = ym.split('-')
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  return `${months[parseInt(m) - 1]} ${y}`
}

// ── Language colors ───────────────────────────────────────────────────────────

const LANG_COLORS: Record<string, string> = {
  Python: '#3b82f6',
  JavaScript: '#f59e0b',
  TypeScript: '#60a5fa',
  Java: '#f97316',
  'C++': '#a855f7',
  'C#': '#22c55e',
  C: '#6b7280',
  Go: '#06b6d4',
  Rust: '#ef4444',
  Ruby: '#ec4899',
  PHP: '#8b5cf6',
  Swift: '#f97316',
  Kotlin: '#a78bfa',
  Scala: '#dc2626',
  HTML: '#f87171',
  CSS: '#38bdf8',
  SCSS: '#f472b6',
  Shell: '#4ade80',
  Dockerfile: '#0ea5e9',
  Markdown: '#94a3b8',
  YAML: '#fbbf24',
  SQL: '#34d399',
  R: '#2563eb',
  Dart: '#22d3ee',
  Elixir: '#a855f7',
  Lua: '#6366f1',
  Haskell: '#7c3aed',
}

export function getLangColor(lang: string): string {
  return LANG_COLORS[lang] || '#64748b'
}

// ── Platform helpers ──────────────────────────────────────────────────────────

export const PLATFORM_INFO = {
  github: {
    label: 'GitHub',
    color: '#f0f0f0',
    bg: 'bg-slate-800',
    icon: '🐙',
  },
  gitlab: {
    label: 'GitLab',
    color: '#fc6d26',
    bg: 'bg-orange-900/40',
    icon: '🦊',
  },
  bitbucket: {
    label: 'Bitbucket',
    color: '#2684ff',
    bg: 'bg-blue-900/40',
    icon: '🪣',
  },
} as const

// ── Class name helper ─────────────────────────────────────────────────────────

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ')
}
