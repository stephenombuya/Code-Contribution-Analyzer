import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  BarChart, Bar,
} from 'recharts'
import { getLangColor, formatNumber, formatMonth } from '../../utils'
import type { MonthlyActivity } from '../../types'

// ── Language Donut ────────────────────────────────────────────────────────────

interface LanguageDonutProps {
  languages: Record<string, number>
}

export function LanguageDonut({ languages }: LanguageDonutProps) {
  const sorted = Object.entries(languages)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)

  const total = sorted.reduce((s, [, v]) => s + v, 0) || 1
  const data = sorted.map(([name, value]) => ({
    name,
    value,
    pct: ((value / total) * 100).toFixed(1),
  }))

  return (
    <div className="flex flex-col lg:flex-row items-center gap-6">
      <div className="w-52 h-52 flex-shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map(({ name }) => (
                <Cell key={name} fill={getLangColor(name)} stroke="transparent" />
              ))}
            </Pie>
            <Tooltip
              content={({ payload }) => {
                if (!payload?.[0]) return null
                const d = payload[0].payload
                return (
                  <div className="card-glass px-3 py-2 text-xs">
                    <p className="font-semibold text-white">{d.name}</p>
                    <p className="text-slate-400">{formatNumber(d.value)} lines ({d.pct}%)</p>
                  </div>
                )
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-2 w-full">
        {data.map(({ name, pct }) => (
          <div key={name} className="flex items-center gap-2.5">
            <div
              className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
              style={{ backgroundColor: getLangColor(name) }}
            />
            <span className="text-sm text-slate-300 truncate flex-1">{name}</span>
            <span className="text-xs text-slate-500 font-mono">{pct}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Activity Area Chart ───────────────────────────────────────────────────────

interface ActivityChartProps {
  data: MonthlyActivity[]
  height?: number
}

export function ActivityChart({ data, height = 260 }: ActivityChartProps) {
  const formatted = data.map((d) => ({
    ...d,
    month: formatMonth(d.month),
  }))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={formatted} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="addGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="delGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.07)" />
        <XAxis
          dataKey="month"
          tick={{ fill: '#64748b', fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fill: '#64748b', fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => formatNumber(v)}
          width={45}
        />
        <Tooltip
          content={({ payload, label }) => {
            if (!payload?.length) return null
            return (
              <div className="card-glass px-3 py-2.5 text-xs space-y-1 min-w-[140px]">
                <p className="font-semibold text-white mb-1">{label}</p>
                {payload.map((p: any) => (
                  <div key={p.dataKey} className="flex justify-between gap-4">
                    <span style={{ color: p.color }}>{p.name}</span>
                    <span className="text-slate-300 font-mono">{formatNumber(p.value)}</span>
                  </div>
                ))}
              </div>
            )
          }}
        />
        <Area
          type="monotone"
          dataKey="additions"
          name="Additions"
          stroke="#6366f1"
          strokeWidth={2}
          fill="url(#addGrad)"
          dot={false}
          activeDot={{ r: 4, fill: '#6366f1' }}
        />
        <Area
          type="monotone"
          dataKey="deletions"
          name="Deletions"
          stroke="#f43f5e"
          strokeWidth={2}
          fill="url(#delGrad)"
          dot={false}
          activeDot={{ r: 4, fill: '#f43f5e' }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

// ── Commits Bar Chart ─────────────────────────────────────────────────────────

export function CommitsBarChart({ data, height = 200 }: ActivityChartProps) {
  const formatted = data.map((d) => ({
    ...d,
    month: formatMonth(d.month).split(' ')[0], // just month name
  }))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={formatted} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.07)" vertical={false} />
        <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fill: '#64748b', fontSize: 10 }} tickLine={false} axisLine={false} />
        <Tooltip
          cursor={{ fill: 'rgba(99,102,241,0.06)' }}
          content={({ payload, label }) => {
            if (!payload?.length) return null
            return (
              <div className="card-glass px-3 py-2 text-xs">
                <p className="font-semibold text-white mb-1">{label}</p>
                <p className="text-brand-300">{payload[0]?.value} commits</p>
              </div>
            )
          }}
        />
        <Bar dataKey="commits" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={28} />
      </BarChart>
    </ResponsiveContainer>
  )
}

// ── Top Repos Bar Chart ───────────────────────────────────────────────────────

interface TopReposChartProps {
  repos: { name: string; user_commits: number; user_additions: number }[]
  height?: number
}

export function TopReposChart({ repos, height = 280 }: TopReposChartProps) {
  const data = repos.slice(0, 8).map((r) => ({
    name: r.name.length > 16 ? r.name.slice(0, 14) + '…' : r.name,
    commits: r.user_commits,
    additions: r.user_additions,
  }))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 0, right: 10, left: 0, bottom: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.07)" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fill: '#64748b', fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={formatNumber}
        />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          width={100}
        />
        <Tooltip
          cursor={{ fill: 'rgba(99,102,241,0.06)' }}
          content={({ payload, label }) => {
            if (!payload?.length) return null
            return (
              <div className="card-glass px-3 py-2 text-xs space-y-1">
                <p className="font-semibold text-white">{label}</p>
                {payload.map((p: any) => (
                  <div key={p.dataKey} className="flex justify-between gap-3">
                    <span style={{ color: p.color }}>{p.name}</span>
                    <span className="font-mono">{formatNumber(p.value)}</span>
                  </div>
                ))}
              </div>
            )
          }}
        />
        <Bar dataKey="commits" name="Commits" fill="#6366f1" radius={[0, 4, 4, 0]} maxBarSize={16} />
      </BarChart>
    </ResponsiveContainer>
  )
}
