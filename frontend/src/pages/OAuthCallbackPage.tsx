import { useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import toast from 'react-hot-toast'
import { GitBranch } from 'lucide-react'
import { authService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import type { Platform } from '../types'

export default function OAuthCallbackPage() {
  const { platform } = useParams<{ platform: string }>()
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const done = useRef(false)

  useEffect(() => {
    if (done.current) return
    done.current = true

    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    const state = params.get('state')
    const error = params.get('error')

    if (error) {
      toast.error(`OAuth error: ${error}`)
      navigate('/login')
      return
    }

    if (!code || !platform) {
      toast.error('Invalid OAuth response.')
      navigate('/login')
      return
    }

    authService
      .exchangeCode(platform as Platform, code, state || '')
      .then(({ user, access_token, refresh_token }) => {
        setAuth(user, access_token, refresh_token)
        toast.success(`Connected to ${platform}!`)
        navigate('/dashboard')
      })
      .catch((err) => {
        const msg = err?.response?.data?.error || 'Authentication failed.'
        toast.error(msg)
        navigate('/login')
      })
  }, [])

  return (
    <div className="min-h-screen bg-surface-950 flex flex-col items-center justify-center gap-6">
      <div className="w-14 h-14 rounded-2xl bg-brand-600 flex items-center justify-center shadow-2xl shadow-brand-900/50 animate-pulse-slow">
        <GitBranch className="w-7 h-7 text-white" />
      </div>
      <div className="text-center">
        <p className="font-display font-bold text-xl text-white mb-1">Connecting…</p>
        <p className="text-slate-500 text-sm capitalize">Authenticating with {platform}</p>
      </div>
      <div className="flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full bg-brand-500 animate-bounce"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  )
}
