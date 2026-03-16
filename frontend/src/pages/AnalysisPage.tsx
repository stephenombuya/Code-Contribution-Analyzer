import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, AlertCircle, CheckCircle2, Loader2, ChevronDown } from 'lucide-react'
import toast from 'react-hot-toast'
import { analysisService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import {
  PageHeader, StatCard,
} from '../components/shared/StatCard'
import { LanguageDonut, ActivityChart, TopReposChart } from '../components/charts/Charts'
import { formatNumber, PLATFORM_INFO } from '../utils'
import type { Platform, AnalysisResult } from '../types'

type FormState = {
  platform: Platform
  since: string
  until: string
  max_repos: number
  include_private: boolean
}

const DEFAULT_FORM: FormState = {
  platform: 'github',
  since: '',
  until: '',
  max_repos: 50,
  include_private: true,
}

export default function AnalysisPage() {
  const [form, setForm] = useState<FormState>(DEFAULT_FORM)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const user = useAuthStore((s) => s.user)
  const navigate = useNavigate()

  const connectedPlatforms = user?.platforms || []

  const handleRun = async () => {
    if (!connectedPlatforms.includes(form.platform)) {
      toast.error(`${form.platform} is not connected. Go to Settings to connect it.`)
      return
    }
    setRunning(true)
    setError(null)
    setResult(null)

    try {
      const res = await analysisService.run({
        platform: form.platform,
        since: form.since || undefined,
        until: form.until || undefined,
        max_repos: form.max_repos,
        include_private: form.include_private,
      })
      setResult(res.result)
      toast.success('Analysis complete!')
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Analysis failed.'
      setError(msg)
      toast.error(msg)
    } finally {
      setRunning(false)
    }
  }

  const set = (key: keyof FormState, value: any) =>
    setForm((f) => ({ ...f, [key]: value }))

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto">
      <PageHeader
        title="Run Analysis"
        description="Analyze your contributions across repositories."
      />

      {/* ── Config Card ────────────────────────────────────────────── */}
      <div className="card p-6 mb-8 max-w-2xl">
        <h2 className="font-semibold text-white mb-5">Configuration</h2>

        <div className="grid sm:grid-cols-2 gap-5">
          {/* Platform */}
          <div className="sm:col-span-2">
            <label className="block text-xs text-slate-400 mb-2 font-medium uppercase tracking-wide">
              Platform
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['github', 'gitlab', 'bitbucket'] as Platform[]).map((p) => {
                const connected = connectedPlatforms.includes(p)
                const info = PLATFORM_INFO[p]
                return (
                  <button
                    key={p}
                    onClick={() => set('platform', p)}
                    disabled={!connected}
                    title={!connected ? `${info.label} not connected` : undefined}
                    className={`
                      relative flex flex-col items-center gap-1.5 py-3 px-2 rounded-xl border text-xs font-medium
                      transition-all duration-200
                      ${form.platform === p && connected
                        ? 'bg-brand-600/15 border-brand-500/50 text-brand-300'
                        : connected
                          ? 'bg-slate-800/40 border-slate-700/60 text-slate-400 hover:text-white hover:border-slate-600'
                          : 'bg-slate-900/40 border-slate-800/40 text-slate-600 cursor-not-allowed opacity-50'
                      }
                    `}
                  >
                    <span className="text-lg">{info.icon}</span>
                    {info.label}
                    {!connected && (
                      <span className="absolute -top-1.5 -right-1.5 text-[9px] bg-slate-700 text-slate-400 px-1 rounded">
                        not connected
                      </span>
                    )}
                  </button>
                )
              })}
            </div>
            {connectedPlatforms.length === 0 && (
              <p className="text-xs text-amber-400 mt-2">
                No platforms connected.{' '}
                <button onClick={() => navigate('/settings')} className="underline">
                  Go to Settings
                </button>{' '}
                to connect one.
              </p>
            )}
          </div>

          {/* Date range */}
          <div>
            <label className="block text-xs text-slate-400 mb-2 font-medium uppercase tracking-wide">
              Since (optional)
            </label>
            <input
              type="date"
              value={form.since}
              onChange={(e) => set('since', e.target.value)}
              className="input"
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-2 font-medium uppercase tracking-wide">
              Until (optional)
            </label>
            <input
              type="date"
              value={form.until}
              onChange={(e) => set('until', e.target.value)}
              className="input"
            />
          </div>

          {/* Max repos */}
          <div>
            <label className="block text-xs text-slate-400 mb-2 font-medium uppercase tracking-wide">
              Max Repositories
            </label>
            <div className="relative">
              <select
                value={form.max_repos}
                onChange={(e) => set('max_repos', Number(e.target.value))}
                className="input appearance-none pr-8"
              >
                {[10, 25, 50, 100].map((v) => (
                  <option key={v} value={v}>{v} repos</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
            </div>
          </div>

          {/* Include private */}
          <div className="flex items-center gap-3">
            <label className="relative inline-flex items-center cursor-pointer mt-5">
              <input
                type="checkbox"
                checked={form.include_private}
                onChange={(e) => set('include_private', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-10 h-5 bg-slate-700 peer-focus:ring-2 peer-focus:ring-brand-500/30
                              rounded-full peer peer-checked:after:translate-x-5
                              after:content-[''] after:absolute after:top-0.5 after:left-0.5
                              after:bg-white after:rounded-full after:h-4 after:w-4
                              after:transition-all peer-checked:bg-brand-600" />
              <span className="ml-3 text-sm text-slate-400">Include private repos</span>
            </label>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-3">
          <button
            onClick={handleRun}
            disabled={running || connectedPlatforms.length === 0}
            className="btn-primary min-w-[140px] justify-center"
          >
            {running ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing…
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                Run Analysis
              </>
            )}
          </button>
          {running && (
            <p className="text-xs text-slate-500">
              This may take a minute for large accounts…
            </p>
          )}
        </div>
      </div>

      {/* ── Error ──────────────────────────────────────────────────── */}
      {error && (
        <div className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 mb-8 max-w-2xl">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-300">Analysis failed</p>
            <p className="text-xs text-red-400/80 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* ── Results ────────────────────────────────────────────────── */}
      {result && (
        <div className="space-y-8 animate-fade-up">
          <div className="flex items-center gap-3 text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
            <p className="font-medium">
              Analysis complete for @{result.username} on {result.platform}
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            <StatCard label="Repos" value={formatNumber(result.total_repos)} accent="violet" />
            <StatCard label="Commits" value={formatNumber(result.total_commits)} accent="brand" />
            <StatCard label="Net Lines" value={formatNumber(result.net_lines)} accent={result.net_lines >= 0 ? 'emerald' : 'red'} />
            <StatCard label="Additions" value={`+${formatNumber(result.total_additions)}`} accent="emerald" />
            <StatCard label="Deletions" value={`-${formatNumber(result.total_deletions)}`} accent="red" />
          </div>

          {/* Charts */}
          <div className="grid lg:grid-cols-2 gap-6">
            {Object.keys(result.languages).length > 0 && (
              <div className="card p-6">
                <h3 className="font-semibold text-white mb-5">Language Breakdown</h3>
                <LanguageDonut languages={result.languages} />
              </div>
            )}
            {result.monthly_activity.length > 0 && (
              <div className="card p-6">
                <h3 className="font-semibold text-white mb-5">Activity Over Time</h3>
                <ActivityChart data={result.monthly_activity} />
              </div>
            )}
          </div>

          {/* Top repos */}
          {result.top_repos.length > 0 && (
            <div className="card p-6">
              <h3 className="font-semibold text-white mb-5">Top Repositories</h3>
              <TopReposChart repos={result.top_repos} height={320} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
