import { useState, useEffect, useMemo } from 'react'
import {
  Search, Star, GitFork, Lock, Globe,
  BookOpen, ChevronDown, ExternalLink
} from 'lucide-react'
import { reposService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { PageHeader, EmptyState, SkeletonCard, Badge } from '../components/shared/StatCard'
import { getLangColor, formatDate, PLATFORM_INFO } from '../utils'
import type { Platform, Repo } from '../types'

export default function RepositoriesPage() {
  const [repos, setRepos] = useState<Repo[]>([])
  const [loading, setLoading] = useState(false)
  const [platform, setPlatform] = useState<Platform>('github')
  const [search, setSearch] = useState('')
  const [langFilter, setLangFilter] = useState('')
  const [sortBy, setSortBy] = useState<'updated' | 'stars' | 'name'>('updated')
  const user = useAuthStore((s) => s.user)
  const connectedPlatforms = user?.platforms || []

  useEffect(() => {
    if (connectedPlatforms.includes(platform)) fetchRepos()
  }, [platform])

  const fetchRepos = async () => {
    setLoading(true)
    try {
      const { repos } = await reposService.list(platform)
      setRepos(repos)
    } catch {
      setRepos([])
    } finally {
      setLoading(false)
    }
  }

  const allLanguages = useMemo(() => {
    const langs = new Set(repos.map((r) => r.language).filter(Boolean))
    return Array.from(langs).sort()
  }, [repos])

  const filtered = useMemo(() => {
    let r = repos
    if (search) {
      const q = search.toLowerCase()
      r = r.filter(
        (repo) =>
          repo.name.toLowerCase().includes(q) ||
          repo.description?.toLowerCase().includes(q)
      )
    }
    if (langFilter) r = r.filter((repo) => repo.language === langFilter)

    r = [...r].sort((a, b) => {
      if (sortBy === 'stars') return b.stars - a.stars
      if (sortBy === 'name') return a.name.localeCompare(b.name)
      return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    })
    return r
  }, [repos, search, langFilter, sortBy])

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto">
      <PageHeader
        title="Repositories"
        description="Browse and filter your connected repositories."
      />

      {/* Platform selector */}
      <div className="flex gap-2 mb-6">
        {(['github', 'gitlab', 'bitbucket'] as Platform[]).map((p) => {
          const connected = connectedPlatforms.includes(p)
          const info = PLATFORM_INFO[p]
          return (
            <button
              key={p}
              onClick={() => connected && setPlatform(p)}
              disabled={!connected}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-xl text-sm border transition-all
                ${platform === p && connected
                  ? 'bg-brand-600/15 border-brand-500/50 text-brand-300'
                  : connected
                    ? 'bg-slate-800/40 border-slate-700/50 text-slate-400 hover:text-white'
                    : 'opacity-40 cursor-not-allowed bg-slate-900/30 border-slate-800/30 text-slate-600'
                }
              `}
            >
              <span>{info.icon}</span>
              {info.label}
              {!connected && <span className="text-xs text-slate-600">(not connected)</span>}
            </button>
          )
        })}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search repositories…"
            className="input pl-9"
          />
        </div>

        {allLanguages.length > 0 && (
          <div className="relative">
            <select
              value={langFilter}
              onChange={(e) => setLangFilter(e.target.value)}
              className="input pr-8 appearance-none min-w-[140px]"
            >
              <option value="">All languages</option>
              {allLanguages.map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
          </div>
        )}

        <div className="relative">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="input pr-8 appearance-none min-w-[140px]"
          >
            <option value="updated">Sort: Updated</option>
            <option value="stars">Sort: Stars</option>
            <option value="name">Sort: Name</option>
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
        </div>
      </div>

      {/* Results count */}
      {!loading && repos.length > 0 && (
        <p className="text-xs text-slate-500 mb-4">
          Showing {filtered.length} of {repos.length} repositories
        </p>
      )}

      {/* Grid */}
      {loading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 9 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : !connectedPlatforms.includes(platform) ? (
        <EmptyState
          icon={<BookOpen className="w-7 h-7" />}
          title={`${PLATFORM_INFO[platform].label} not connected`}
          description="Connect this platform in Settings to see your repositories."
        />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={<Search className="w-7 h-7" />}
          title="No repositories found"
          description={search || langFilter ? 'Try adjusting your filters.' : 'No repositories available.'}
        />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((repo) => (
            <RepoCard key={`${repo.platform}-${repo.id}`} repo={repo} />
          ))}
        </div>
      )}
    </div>
  )
}

function RepoCard({ repo }: { repo: Repo }) {
  return (
    <div className="card p-5 flex flex-col gap-3 hover:border-slate-700 transition-all duration-200 group">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-1">
            {repo.is_private ? (
              <Lock className="w-3 h-3 text-slate-500 flex-shrink-0" />
            ) : (
              <Globe className="w-3 h-3 text-slate-500 flex-shrink-0" />
            )}
            <p className="font-medium text-white text-sm truncate">{repo.name}</p>
          </div>
          <p className="text-xs text-slate-500 truncate">{repo.owner}</p>
        </div>
        {repo.url && (
          <a
            href={repo.url}
            target="_blank"
            rel="noopener noreferrer"
            className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-brand-400 transition-all"
            onClick={(e) => e.stopPropagation()}
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}
      </div>

      {repo.description && (
        <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
          {repo.description}
        </p>
      )}

      <div className="flex items-center gap-3 mt-auto">
        {repo.language && repo.language !== 'Unknown' && (
          <div className="flex items-center gap-1.5">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: getLangColor(repo.language) }}
            />
            <span className="text-xs text-slate-400">{repo.language}</span>
          </div>
        )}
        <div className="flex items-center gap-1 text-xs text-slate-500 ml-auto">
          <Star className="w-3 h-3" />
          {repo.stars}
        </div>
        <div className="flex items-center gap-1 text-xs text-slate-500">
          <GitFork className="w-3 h-3" />
          {repo.forks}
        </div>
      </div>

      <p className="text-xs text-slate-600">Updated {formatDate(repo.updated_at)}</p>
    </div>
  )
}
