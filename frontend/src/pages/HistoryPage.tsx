import { useState, useEffect } from 'react'
import { Download, Trash2, ChevronDown, RefreshCw, History } from 'lucide-react'
import toast from 'react-hot-toast'
import { analysisService, reportsService } from '../services/api'
import { PageHeader, EmptyState, Badge } from '../components/shared/StatCard'
import { formatDate, formatNumber, PLATFORM_INFO } from '../utils'
import type { Analysis, Platform } from '../types'

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState<number | null>(null)
  const [deleting, setDeleting] = useState<number | null>(null)
  const [expanded, setExpanded] = useState<number | null>(null)
  const [platformFilter, setPlatformFilter] = useState<Platform | ''>('')

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const { analyses } = await analysisService.list(undefined, 1, 50)
      setAnalyses(analyses)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (id: number, fmt: 'json' | 'csv' | 'pdf') => {
    setDownloading(id)
    try {
      await reportsService.download(id, fmt)
      toast.success(`Downloaded ${fmt.toUpperCase()}`)
    } catch {
      toast.error('Download failed.')
    } finally {
      setDownloading(null)
    }
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this analysis?')) return
    setDeleting(id)
    try {
      await analysisService.delete(id)
      setAnalyses((prev) => prev.filter((a) => a.id !== id))
      toast.success('Analysis deleted.')
    } catch {
      toast.error('Delete failed.')
    } finally {
      setDeleting(null)
    }
  }

  const filtered = platformFilter
    ? analyses.filter((a) => a.platform === platformFilter)
    : analyses

  return (
    <div className="p-6 lg:p-8 max-w-5xl mx-auto">
      <PageHeader
        title="Analysis History"
        description="Browse and download past analyses."
        action={
          <button onClick={loadHistory} className="btn-ghost text-sm">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        }
      />

      {/* Filter */}
      <div className="flex gap-2 mb-6">
        {(['' , 'github', 'gitlab', 'bitbucket'] as const).map((p) => (
          <button
            key={p}
            onClick={() => setPlatformFilter(p as any)}
            className={`px-3 py-1.5 rounded-lg text-xs border transition-all ${
              platformFilter === p
                ? 'bg-brand-600/15 border-brand-500/40 text-brand-300'
                : 'bg-slate-800/40 border-slate-700/40 text-slate-400 hover:text-white'
            }`}
          >
            {p === '' ? 'All' : `${PLATFORM_INFO[p].icon} ${PLATFORM_INFO[p].label}`}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card p-5 shimmer-line h-20" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<History className="w-7 h-7" />}
          title="No analyses yet"
          description="Run your first analysis from the Analysis page."
        />
      ) : (
        <div className="space-y-3">
          {filtered.map((analysis) => (
            <div key={analysis.id} className="card overflow-hidden">
              {/* Header row */}
              <div
                className="flex items-center gap-4 p-5 cursor-pointer hover:bg-slate-800/30 transition-colors"
                onClick={() =>
                  analysis.status === 'completed' &&
                  setExpanded(expanded === analysis.id ? null : analysis.id)
                }
              >
                <span className="text-2xl flex-shrink-0">
                  {PLATFORM_INFO[analysis.platform]?.icon}
                </span>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-white text-sm capitalize">
                      {analysis.platform}
                    </span>
                    <span className="text-slate-500 text-sm">@{analysis.username}</span>
                    <Badge
                      variant={
                        analysis.status === 'completed' ? 'success' :
                        analysis.status === 'failed' ? 'error' :
                        analysis.status === 'running' ? 'info' : 'default'
                      }
                    >
                      {analysis.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
                    <span>{formatDate(analysis.created_at)}</span>
                    {analysis.since && <span>From {analysis.since}</span>}
                    {analysis.result && (
                      <>
                        <span>{formatNumber(analysis.result.total_repos)} repos</span>
                        <span>{formatNumber(analysis.result.total_commits)} commits</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {analysis.status === 'completed' && (
                    <>
                      <div className="flex gap-1">
                        {(['json', 'csv', 'pdf'] as const).map((fmt) => (
                          <button
                            key={fmt}
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDownload(analysis.id, fmt)
                            }}
                            disabled={downloading === analysis.id}
                            className="btn-ghost py-1 px-2 text-xs border border-slate-700/60"
                          >
                            {downloading === analysis.id ? (
                              <RefreshCw className="w-3 h-3 animate-spin" />
                            ) : (
                              <Download className="w-3 h-3" />
                            )}
                            {fmt.toUpperCase()}
                          </button>
                        ))}
                      </div>
                      <ChevronDown
                        className={`w-4 h-4 text-slate-500 transition-transform ${
                          expanded === analysis.id ? 'rotate-180' : ''
                        }`}
                      />
                    </>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(analysis.id)
                    }}
                    disabled={deleting === analysis.id}
                    className="text-slate-600 hover:text-red-400 transition-colors p-1"
                  >
                    {deleting === analysis.id ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Trash2 className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Expanded result summary */}
              {expanded === analysis.id && analysis.result && (
                <div className="border-t border-slate-800/60 px-5 pb-5 pt-4">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                    {[
                      { label: 'Repos', value: analysis.result.total_repos },
                      { label: 'Commits', value: analysis.result.total_commits },
                      { label: '+Lines', value: analysis.result.total_additions },
                      { label: '-Lines', value: analysis.result.total_deletions },
                    ].map(({ label, value }) => (
                      <div key={label} className="text-center bg-slate-800/40 rounded-xl py-3">
                        <p className="font-bold text-lg text-white">{formatNumber(value)}</p>
                        <p className="text-xs text-slate-500">{label}</p>
                      </div>
                    ))}
                  </div>

                  {/* Top langs */}
                  <div>
                    <p className="text-xs text-slate-500 mb-2">Top Languages</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(analysis.result.languages)
                        .sort(([, a], [, b]) => b - a)
                        .slice(0, 8)
                        .map(([lang, lines]) => (
                          <span
                            key={lang}
                            className="text-xs px-2.5 py-1 rounded-lg bg-slate-800/60 text-slate-300"
                          >
                            {lang}: {formatNumber(lines)}
                          </span>
                        ))}
                    </div>
                  </div>
                </div>
              )}

              {analysis.status === 'failed' && analysis.error && (
                <div className="border-t border-red-900/30 px-5 py-3 bg-red-500/5">
                  <p className="text-xs text-red-400">{analysis.error}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
