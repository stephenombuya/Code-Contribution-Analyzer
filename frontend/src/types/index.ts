// ── Auth ──────────────────────────────────────────────────────────────────────

export type Platform = 'github' | 'gitlab' | 'bitbucket'

export interface PlatformAccount {
  id: number
  platform: Platform
  username: string
  avatar_url: string | null
  profile_url: string | null
}

export interface User {
  id: number
  email: string | null
  name: string | null
  avatar_url: string | null
  created_at: string
  platforms: Platform[]
  accounts?: PlatformAccount[]
}

// ── Analysis ──────────────────────────────────────────────────────────────────

export type AnalysisStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface MonthlyActivity {
  month: string
  commits: number
  additions: number
  deletions: number
}

export interface RepoResult {
  platform: Platform
  owner: string
  name: string
  full_name: string
  description: string
  language: string
  languages: Record<string, { bytes?: number; pct?: number } | number>
  stars: number
  forks: number
  is_private: boolean
  created_at: string
  updated_at: string
  clone_url: string
  total_commits: number
  user_commits: number
  user_additions: number
  user_deletions: number
  weekly_stats: MonthlyActivity[]
}

export interface AnalysisResult {
  platform: Platform
  username: string
  total_repos: number
  total_commits: number
  total_additions: number
  total_deletions: number
  net_lines: number
  languages: Record<string, number>
  repos: RepoResult[]
  monthly_activity: MonthlyActivity[]
  top_repos: RepoResult[]
}

export interface Analysis {
  id: number
  platform: Platform
  username: string
  status: AnalysisStatus
  since: string | null
  until: string | null
  created_at: string
  completed_at: string | null
  error: string | null
  result?: AnalysisResult
}

export interface CombinedSummary {
  total_repos: number
  total_commits: number
  total_additions: number
  total_deletions: number
  net_lines: number
  top_languages: Record<string, number>
  platforms_analyzed: Platform[]
}

// ── Repos ─────────────────────────────────────────────────────────────────────

export interface Repo {
  id: string | number
  name: string
  full_name: string
  owner: string
  description: string
  language: string
  languages: Record<string, number | { bytes?: number; pct?: number }>
  stars: number
  forks: number
  is_private: boolean
  url: string
  clone_url: string
  created_at: string
  updated_at: string
  platform: Platform
}

// ── UI Helpers ────────────────────────────────────────────────────────────────

export interface NavItem {
  label: string
  href: string
  icon?: React.FC<{ className?: string }>
}
