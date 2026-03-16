import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  GitCommit, Code2, TrendingUp, TrendingDown,
  BookOpen, Zap, Download, RefreshCw, ChevronRight
} from 'lucide-react'
import toast from 'react-hot-toast'
import { analysisService, reportsService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import {
  StatCard, SkeletonStatCard, SkeletonCard,
  EmptyState, SectionHeader, PageHeader, Badge
} from '../components/shared/StatCard'
import { LanguageDonut, ActivityChart, TopReposChart } from '../components/charts/Charts'
import { formatNumber, formatDate, PLATFORM_INFO } from '../utils'
import type { Analysis, CombinedSummary } from '../types'

export default function DashboardPage() {
  const [combined, setCombined] = useState<CombinedSummary | null>(null)
  const [latestAnalyses, setLatestAnalyses] = useState<Analysis[]>([])
  const [downloading, setDownloading] = useState(false)
  const [loading, setLoading] = useState(true)
  const user = useAuthStore((s) => s.user)
  const navigate = useNavigate()

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    setLoading(true)
    try {
      const [summaryResult, historyResult] = await Promise.allSettled([
        analysisService.getCombinedSummary(),
        analysisService.list(undefined, 1, 6),
      ])

      if (summaryResult.status === 'fulfilled') setCombined(summaryResult.value)
      if (historyResult.status === 'fulfilled') {
        setLatestAnalyses(
          historyResult.value.analyses.filter((a) => a.status === 'completed')
        )
      }
    } catch {
      // silently handle — no analyses yet is valid
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (analysisId: number, fmt: 'json' | 'csv' | 'pdf') => {
    setDownloading(true)
    try {
      await reportsService.download(analysisId, fmt)
      toast.success(`Report downloaded as ${fmt.toUpperCase()}`)
    } catch {
      toast.error('Download failed.')
    } finally {
      setDownloading(false)
    }
  }

  const latestCompleted = latestAnalyses[0]

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto">
      <PageHeader
        title={`Welcome back${user?.name ? `, ${user.name.split(' ')[0]}` : ''} 👋`}
        description="Here's an overview of your coding contributions."
        action={
          <button
            onClick={() => navigate('/analysis')}
            className="btn-primary text-sm"
          >
            <Zap className="w-4 h-4" /> Run Analysis
          </button>
        }
      />

      {/* ── Summary Stats ──────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonStatCard key={i} />)
        ) : combined ? (
          <>
            <StatCard
              label="Total Commits"
              value={formatNumber(combined.total_commits)}
              icon={<GitCommit className="w-4 h-4" />}
              accent="brand"
            />
            <StatCard
              label="Lines Added"
              value={`+${formatNumber(combined.total_additions)}`}
              icon={<TrendingUp className="w-4 h-4" />}
              accent="emerald"
            />
            <StatCard
              label="Lines Removed"
              value={`-${formatNumber(combined.total_deletions)}`}
              icon={<TrendingDown className="w-4 h-4" />}
              accent="red"
            />
            <StatCard
              label="Repositories"
              value={formatNumber(combined.total_repos)}
              icon={<BookOpen className="w-4 h-4" />}
              accent="violet"
            />
          </>
        ) : (
          <div className="col-span-4">
            <EmptyState
              icon={<Code2 className="w-7 h-7" />}
              title="No analyses yet"
              description="Connect a platform and run your first analysis to see stats here."
              action={
                <button onClick={() => navigate('/analysis')} className="btn-primary">
                  <Zap className="w-4 h-4" /> Run First Analysis
                </button>
              }
            />
          </div>
        )}
      </div>

      {combined && (
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Language Breakdown */}
          <div className="lg:col-span-1 card p-6">
            <SectionHeader title="Languages" description="By net lines of code" />
            {Object.keys(combined.top_languages).length > 0 ? (
              <LanguageDonut languages={combined.top_languages} />
            ) : (
              <p className="text-slate-500 text-sm">No language data yet.</p>
            )}
          </div>

          {/* Activity Timeline */}
          {latestCompleted?.result?.monthly_activity && (
            <div className="lg:col-span-2 card p-6">
              <SectionHeader
                title="Activity Timeline"
                description="Additions & deletions over time"
              />
              <ActivityChart data={latestCompleted.result.monthly_activity} />
            </div>
          )}
        </div>
      )}

      {/* ── Latest Analyses ────────────────────────────────────────── */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent runs */}
        <div className="card p-6">
          <SectionHeader
            title="Recent Analyses"
            action={
              <button onClick={() => navigate('/history')} className="btn-ghost text-xs">
                View all <ChevronRight className="w-3.5 h-3.5" />
              </button>
            }
          />
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="shimmer-line h-14 rounded-xl" />
              ))}
            </div>
          ) : latestAnalyses.length > 0 ? (
            <div className="space-y-2">
              {latestAnalyses.slice(0, 5).map((a) => (
                <div
                  key={a.id}
                  className="flex items-center gap-4 p-3 rounded-xl bg-slate-800/40 hover:bg-slate-800/60 transition-colors cursor-pointer"
                  onClick={() => navigate('/history')}
                >
                  <div className="text-xl flex-shrink-0">
                    {PLATFORM_INFO[a.platform]?.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white capitalize">
                      {a.platform} — @{a.username}
                    </p>
                    <p className="text-xs text-slate-500">{formatDate(a.completed_at || a.created_at)}</p>
                  </div>
                  <Badge variant={a.status === 'completed' ? 'success' : a.status === 'failed' ? 'error' : 'info'}>
                    {a.status}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500 py-6 text-center">No analyses yet.</p>
          )}
        </div>

        {/* Top repos + export */}
        {latestCompleted?.result?.top_repos && latestCompleted.result.top_repos.length > 0 ? (
          <div className="card p-6">
            <SectionHeader
              title="Top Repositories"
              description="By your commit count"
              action={
                <div className="flex gap-2">
                  {(['json', 'csv', 'pdf'] as const).map((fmt) => (
                    <button
                      key={fmt}
                      onClick={() => handleDownload(latestCompleted.id, fmt)}
                      disabled={downloading}
                      className="btn-ghost text-xs py-1 px-2.5 border border-slate-700/60"
                      title={`Download ${fmt.toUpperCase()}`}
                    >
                      {downloading ? (
                        <RefreshCw className="w-3 h-3 animate-spin" />
                      ) : (
                        <Download className="w-3 h-3" />
                      )}
                      {fmt.toUpperCase()}
                    </button>
                  ))}
                </div>
              }
            />
            <TopReposChart repos={latestCompleted.result.top_repos} />
          </div>
        ) : (
          !loading && combined && (
            <div className="card p-6">
              <SectionHeader title="Top Repositories" />
              <EmptyState
                icon={<BookOpen className="w-6 h-6" />}
                title="Run an analysis"
                description="Your top repositories will appear here after analysis."
              />
            </div>
          )
        )}
      </div>
    </div>
  )
}
