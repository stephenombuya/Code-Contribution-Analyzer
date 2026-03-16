import { useNavigate } from 'react-router-dom'
import { GitBranch, BarChart2, Globe, Download, ArrowRight, Zap, Shield, TrendingUp } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

const FEATURES = [
  {
    icon: Globe,
    title: 'Multi-Platform',
    desc: 'Connect GitHub, GitLab, and Bitbucket in one unified dashboard.',
    color: 'text-brand-400',
    bg: 'bg-brand-500/10',
  },
  {
    icon: BarChart2,
    title: 'Deep Analytics',
    desc: 'Lines of code, language breakdown, monthly trends, and top repos.',
    color: 'text-violet-400',
    bg: 'bg-violet-500/10',
  },
  {
    icon: TrendingUp,
    title: 'Progress Tracking',
    desc: 'Visualize your growth with interactive charts and time-series data.',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
  },
  {
    icon: Download,
    title: 'Export Reports',
    desc: 'Download polished PDF, CSV or JSON reports anytime.',
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
  },
  {
    icon: Shield,
    title: 'Secure OAuth',
    desc: "Your tokens stay private — we never store your repo's source code.",
    color: 'text-sky-400',
    bg: 'bg-sky-500/10',
  },
  {
    icon: Zap,
    title: 'Instant Insights',
    desc: 'Run an analysis in seconds. No setup, no CLI required.',
    color: 'text-pink-400',
    bg: 'bg-pink-500/10',
  },
]

const STATS = [
  { label: 'Platforms Supported', value: '3' },
  { label: 'Languages Detected', value: '60+' },
  { label: 'Export Formats', value: '3' },
  { label: 'Repos per Analysis', value: '50+' },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  return (
    <div className="min-h-screen bg-surface-950 text-slate-100 overflow-x-hidden">
      {/* ── Navbar ──────────────────────────────────────────────────── */}
      <nav className="fixed top-0 inset-x-0 z-50 flex items-center justify-between px-6 py-4 border-b border-slate-800/40 backdrop-blur-md bg-surface-950/80">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center shadow-lg shadow-brand-900/50">
            <GitBranch className="w-4 h-4 text-white" />
          </div>
          <span className="font-display font-bold text-white">CodeAnalyzer</span>
        </div>
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <button onClick={() => navigate('/dashboard')} className="btn-primary text-sm">
              Dashboard <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <>
              <button onClick={() => navigate('/login')} className="btn-ghost text-sm">
                Sign in
              </button>
              <button onClick={() => navigate('/login')} className="btn-primary text-sm">
                Get Started <ArrowRight className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </nav>

      {/* ── Hero ────────────────────────────────────────────────────── */}
      <section className="relative pt-32 pb-24 px-6 grid-bg">
        {/* Glow blobs */}
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-brand-600/10 blur-[120px] pointer-events-none" />
        <div className="absolute top-40 left-1/4 w-64 h-64 rounded-full bg-violet-600/8 blur-[80px] pointer-events-none" />

        <div className="relative max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-brand-500/30 bg-brand-500/8 text-brand-300 text-sm font-medium mb-8 animate-fade-up">
            <span className="glow-dot" />
            Open Source · Multi-Platform · No Tracking
          </div>

          <h1 className="font-display font-extrabold text-5xl sm:text-6xl lg:text-7xl leading-[1.08] mb-6 animate-fade-up animate-delay-100">
            Understand your<br />
            <span className="text-gradient">coding impact</span>
          </h1>

          <p className="text-slate-400 text-lg sm:text-xl max-w-2xl mx-auto mb-10 animate-fade-up animate-delay-200">
            Connect GitHub, GitLab, and Bitbucket to get a complete picture of your
            contributions — lines written, languages used, activity trends, and more.
          </p>

          <div className="flex items-center justify-center gap-4 animate-fade-up animate-delay-300">
            <button
              onClick={() => navigate(isAuthenticated ? '/dashboard' : '/login')}
              className="btn-primary px-8 py-3 text-base shadow-xl shadow-brand-900/50"
            >
              Start Analyzing <ArrowRight className="w-5 h-5" />
            </button>
            <a
              href="https://github.com/stephenombuya/Code-Contribution-Analyzer"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-ghost px-6 py-3 text-base border border-slate-700/60"
            >
              View on GitHub
            </a>
          </div>
        </div>

        {/* Stats bar */}
        <div className="relative max-w-3xl mx-auto mt-20 grid grid-cols-2 sm:grid-cols-4 gap-px bg-slate-800/40 rounded-2xl overflow-hidden border border-slate-800/60 animate-fade-up animate-delay-400">
          {STATS.map(({ label, value }) => (
            <div key={label} className="bg-surface-900/80 px-6 py-5 text-center">
              <p className="font-display font-bold text-3xl text-white">{value}</p>
              <p className="text-xs text-slate-500 mt-1">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ────────────────────────────────────────────────── */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display font-bold text-4xl text-white mb-4">
              Everything you need
            </h2>
            <p className="text-slate-400 text-lg max-w-xl mx-auto">
              A production-grade analytics platform built for developers who care about their craft.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map(({ icon: Icon, title, desc, color, bg }) => (
              <div
                key={title}
                className="card p-6 hover:border-slate-700 transition-all duration-300 group hover:-translate-y-0.5"
              >
                <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center mb-4`}>
                  <Icon className={`w-5 h-5 ${color}`} />
                </div>
                <h3 className="font-semibold text-white mb-2">{title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────────────── */}
      <section className="py-24 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <div className="card border-gradient p-12">
            <h2 className="font-display font-bold text-4xl text-white mb-4">
              Ready to explore your code?
            </h2>
            <p className="text-slate-400 mb-8">
              Connect your first platform account and get insights in under a minute.
            </p>
            <button
              onClick={() => navigate(isAuthenticated ? '/dashboard' : '/login')}
              className="btn-primary px-10 py-3.5 text-base shadow-xl shadow-brand-900/60"
            >
              Get Started Free <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────── */}
      <footer className="border-t border-slate-800/60 py-8 px-6 text-center text-slate-500 text-sm">
        <div className="flex items-center justify-center gap-2 mb-2">
          <GitBranch className="w-4 h-4 text-brand-500" />
          <span className="font-display font-semibold text-slate-300">CodeAnalyzer</span>
        </div>
        <p>Built with ❤️ by Stephen Ombuya · MIT License</p>
      </footer>
    </div>
  )
}
