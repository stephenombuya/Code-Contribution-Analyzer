import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GitBranch, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import { authService } from '../services/api'
import type { Platform } from '../types'

const PLATFORMS: { id: Platform; label: string; icon: string; color: string; border: string }[] = [
  {
    id: 'github',
    label: 'Continue with GitHub',
    icon: '🐙',
    color: 'bg-slate-800 hover:bg-slate-700',
    border: 'border-slate-700 hover:border-slate-500',
  },
  {
    id: 'gitlab',
    label: 'Continue with GitLab',
    icon: '🦊',
    color: 'bg-orange-950/40 hover:bg-orange-900/40',
    border: 'border-orange-800/40 hover:border-orange-600/60',
  },
  {
    id: 'bitbucket',
    label: 'Continue with Bitbucket',
    icon: '🪣',
    color: 'bg-blue-950/40 hover:bg-blue-900/40',
    border: 'border-blue-800/40 hover:border-blue-600/60',
  },
]

export default function LoginPage() {
  const [loading, setLoading] = useState<Platform | null>(null)
  const navigate = useNavigate()

  const handleConnect = async (platform: Platform) => {
    setLoading(platform)
    try {
      const url = await authService.getAuthorizeUrl(platform)
      window.location.href = url
    } catch (err: any) {
      toast.error(err?.response?.data?.error || `Could not connect to ${platform}`)
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-surface-950 grid-bg flex items-center justify-center px-4">
      {/* Glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[500px] h-[500px] rounded-full bg-brand-600/8 blur-[100px]" />
      </div>

      <div className="relative w-full max-w-md">
        {/* Back */}
        <button
          onClick={() => navigate('/')}
          className="btn-ghost mb-8 text-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Back to home
        </button>

        <div className="card border-gradient p-8">
          {/* Header */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center shadow-lg shadow-brand-900/50">
              <GitBranch className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-display font-bold text-xl text-white">Sign in</h1>
              <p className="text-xs text-slate-500">Connect your code platforms</p>
            </div>
          </div>

          <p className="text-slate-400 text-sm mb-6">
            Select a platform to authenticate via OAuth. You can connect multiple
            platforms after signing in.
          </p>

          <div className="space-y-3">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                onClick={() => handleConnect(p.id)}
                disabled={loading !== null}
                className={`
                  w-full flex items-center gap-4 px-5 py-3.5 rounded-xl border
                  transition-all duration-200 text-left
                  ${p.color} ${p.border}
                  ${loading === p.id ? 'opacity-70 cursor-wait' : ''}
                  ${loading !== null && loading !== p.id ? 'opacity-40 cursor-not-allowed' : ''}
                `}
              >
                <span className="text-xl">{p.icon}</span>
                <span className="flex-1 font-medium text-slate-200 text-sm">{p.label}</span>
                {loading === p.id && (
                  <div className="w-4 h-4 border-2 border-slate-400/30 border-t-slate-300 rounded-full animate-spin" />
                )}
              </button>
            ))}
          </div>

          <p className="text-xs text-slate-600 text-center mt-6 leading-relaxed">
            By signing in you agree to our Terms of Service.
            We never store your source code — only contribution metadata.
          </p>
        </div>
      </div>
    </div>
  )
}
