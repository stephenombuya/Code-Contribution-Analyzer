import axios, { AxiosInstance, AxiosError } from 'axios'
import toast from 'react-hot-toast'
import type {
  User, Analysis, AnalysisResult, Repo, CombinedSummary, Platform
} from '../types'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

// ── Axios instance ────────────────────────────────────────────────────────────

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach access token on every request
api.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem('cca-auth')
    if (raw) {
      const parsed = JSON.parse(raw)
      const token = parsed?.state?.accessToken
      if (token) config.headers!['Authorization'] = `Bearer ${token}`
    }
  } catch {}
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as any
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const raw = localStorage.getItem('cca-auth')
        const refreshToken = raw ? JSON.parse(raw)?.state?.refreshToken : null
        if (refreshToken) {
          const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          })
          // Update stored token
          const stored = JSON.parse(localStorage.getItem('cca-auth') || '{}')
          stored.state.accessToken = data.access_token
          localStorage.setItem('cca-auth', JSON.stringify(stored))
          original.headers['Authorization'] = `Bearer ${data.access_token}`
          return api(original)
        }
      } catch {
        localStorage.removeItem('cca-auth')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authService = {
  getAuthorizeUrl: async (platform: Platform): Promise<string> => {
    const { data } = await api.get(`/auth/authorize/${platform}`)
    return data.url
  },

  exchangeCode: async (
    platform: Platform, code: string, state: string
  ): Promise<{ user: User; access_token: string; refresh_token: string }> => {
    const { data } = await api.post(`/auth/callback/${platform}`, { code, state })
    return data
  },

  getMe: async (): Promise<User> => {
    const { data } = await api.get('/auth/me')
    return data
  },

  disconnect: async (platform: Platform): Promise<void> => {
    await api.delete(`/auth/disconnect/${platform}`)
  },

  refresh: async (): Promise<string> => {
    const { data } = await api.post('/auth/refresh')
    return data.access_token
  },
}

// ── Analysis ──────────────────────────────────────────────────────────────────

export const analysisService = {
  run: async (params: {
    platform: Platform
    since?: string
    until?: string
    max_repos?: number
    include_private?: boolean
  }): Promise<{ analysis_id: number; status: string; result: AnalysisResult }> => {
    const { data } = await api.post('/analysis/run', params)
    return data
  },

  list: async (
    platform?: Platform, page = 1, perPage = 20
  ): Promise<{ analyses: Analysis[]; total: number; pages: number }> => {
    const params: Record<string, any> = { page, per_page: perPage }
    if (platform) params.platform = platform
    const { data } = await api.get('/analysis/', { params })
    return data
  },

  get: async (id: number, includeResult = true): Promise<Analysis> => {
    const { data } = await api.get(`/analysis/${id}`, {
      params: { include_result: includeResult }
    })
    return data
  },

  getLatest: async (platform: Platform): Promise<Analysis> => {
    const { data } = await api.get(`/analysis/latest/${platform}`)
    return data
  },

  getCombinedSummary: async (): Promise<CombinedSummary> => {
    const { data } = await api.get('/analysis/summary/all')
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/analysis/${id}`)
  },
}

// ── Repos ─────────────────────────────────────────────────────────────────────

export const reposService = {
  list: async (
    platform: Platform, includePrivate = true
  ): Promise<{ repos: Repo[]; total: number }> => {
    const { data } = await api.get(`/repos/${platform}`, {
      params: { include_private: includePrivate }
    })
    return data
  },

  get: async (platform: Platform, owner: string, name: string): Promise<Repo> => {
    const { data } = await api.get(`/repos/${platform}/${owner}/${name}`)
    return data
  },
}

// ── Reports ───────────────────────────────────────────────────────────────────

export const reportsService = {
  download: async (
    analysisId: number, format: 'json' | 'csv' | 'pdf'
  ): Promise<void> => {
    const response = await api.get(`/reports/${analysisId}/${format}`, {
      responseType: 'blob',
    })
    const mimes: Record<string, string> = {
      json: 'application/json',
      csv: 'text/csv',
      pdf: 'application/pdf',
    }
    const url = window.URL.createObjectURL(
      new Blob([response.data], { type: mimes[format] })
    )
    const link = document.createElement('a')
    link.href = url
    link.download = `contribution_report.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },
}

export default api
