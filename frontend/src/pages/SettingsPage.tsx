import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogOut, Link2, Link2Off, RefreshCw, User, Shield } from 'lucide-react'
import toast from 'react-hot-toast'
import { authService } from '../services/api'
import { useAuthStore } from '../store/authStore'
import { PageHeader, Badge } from '../components/shared/StatCard'
import { PLATFORM_INFO } from '../utils'
import type { Platform } from '../types'

export default function SettingsPage() {
  const { user, logout, updateUser } = useAuthStore()
  const navigate = useNavigate()
  const [connecting, setConnecting] = useState<Platform | null>(null)
  const [disconnecting, setDisconnecting] = useState<Platform | null>(null)

  const connectedPlatforms = user?.platforms || []

  const handleConnect = async (platform: Platform) => {
    setConnecting(platform)
    try {
      const url = await authService.getAuthorizeUrl(platform)
      window.location.href = url
    } catch {
      toast.error(`Could not connect to ${platform}`)
      setConnecting(null)
    }
  }

  const handleDisconnect = async (platform: Platform) => {
    if (!window.confirm(`Disconnect ${platform}? This won't delete your analyses.`)) return
    setDisconnecting(platform)
    try {
      await authService.disconnect(platform)
      const updated = await authService.getMe()
      updateUser(updated)
      toast.success(`Disconnected from ${platform}`)
    } catch {
      toast.error('Failed to disconnect.')
    } finally {
      setDisconnecting(null)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="p-6 lg:p-8 max-w-3xl mx-auto">
      <PageHeader title="Settings" description="Manage your account and connected platforms." />

      {/* ── Profile ──────────────────────────────────────────────── */}
      <div className="card p-6 mb-6">
        <div className="flex items-center gap-3 mb-5">
          <User className="w-4 h-4 text-slate-400" />
          <h2 className="font-semibold text-white text-sm">Profile</h2>
        </div>

        <div className="flex items-center gap-4">
          {user?.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={user.name || ''}
              className="w-14 h-14 rounded-xl ring-2 ring-brand-500/20"
            />
          ) : (
            <div className="w-14 h-14 rounded-xl bg-brand-700 flex items-center justify-center text-white text-xl font-bold">
              {(user?.name || user?.email || '?')[0].toUpperCase()}
            </div>
          )}
          <div>
            <p className="font-semibold text-white">{user?.name || 'No name'}</p>
            <p className="text-sm text-slate-400">{user?.email || 'No email'}</p>
            <p className="text-xs text-slate-600 mt-1">
              Member since {user?.created_at ? new Date(user.created_at).getFullYear() : '—'}
            </p>
          </div>
        </div>
      </div>

      {/* ── Connected Platforms ───────────────────────────────────── */}
      <div className="card p-6 mb-6">
        <div className="flex items-center gap-3 mb-5">
          <Shield className="w-4 h-4 text-slate-400" />
          <h2 className="font-semibold text-white text-sm">Connected Platforms</h2>
        </div>

        <div className="space-y-3">
          {(['github', 'gitlab', 'bitbucket'] as Platform[]).map((platform) => {
            const info = PLATFORM_INFO[platform]
            const isConnected = connectedPlatforms.includes(platform)
            const isConnecting = connecting === platform
            const isDisconnecting = disconnecting === platform
            const account = user?.accounts?.find((a) => a.platform === platform)

            return (
              <div
                key={platform}
                className="flex items-center justify-between gap-4 p-4 rounded-xl bg-slate-800/30 border border-slate-700/30"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{info.icon}</span>
                  <div>
                    <p className="font-medium text-white text-sm">{info.label}</p>
                    {isConnected && account ? (
                      <p className="text-xs text-slate-400">@{account.username}</p>
                    ) : (
                      <p className="text-xs text-slate-500">Not connected</p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Badge variant={isConnected ? 'success' : 'default'}>
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </Badge>
                  {isConnected ? (
                    <button
                      onClick={() => handleDisconnect(platform)}
                      disabled={isDisconnecting}
                      className="btn-ghost text-xs text-red-400 hover:text-red-300 border border-red-900/40 hover:border-red-800/60 py-1.5"
                    >
                      {isDisconnecting ? (
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <Link2Off className="w-3.5 h-3.5" />
                      )}
                      Disconnect
                    </button>
                  ) : (
                    <button
                      onClick={() => handleConnect(platform)}
                      disabled={isConnecting !== null}
                      className="btn-primary text-xs py-1.5"
                    >
                      {isConnecting ? (
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <Link2 className="w-3.5 h-3.5" />
                      )}
                      Connect
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Danger Zone ───────────────────────────────────────────── */}
      <div className="card p-6 border-red-900/30">
        <h2 className="font-semibold text-white text-sm mb-5">Danger Zone</h2>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-300">Sign out</p>
            <p className="text-xs text-slate-500">
              You'll be redirected to the login page.
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="btn-ghost text-sm text-red-400 hover:text-red-300 border border-red-900/40 hover:border-red-800/60"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </div>
    </div>
  )
}
