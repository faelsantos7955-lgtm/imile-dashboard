/**
 * components/ui.jsx — Componentes reutilizáveis
 */
import clsx from 'clsx'

// ── KPI Card ──────────────────────────────────────────────────
const COLORS = {
  blue:   'border-l-blue-500',
  orange: 'border-l-orange-500',
  green:  'border-l-emerald-500',
  red:    'border-l-red-500',
  violet: 'border-l-violet-500',
  slate:  'border-l-slate-400',
}

export function KpiCard({ label, value, sub, color = 'blue' }) {
  return (
    <div className={clsx(
      'bg-white rounded-xl border border-slate-200 border-l-4 p-5 shadow-sm animate-in',
      COLORS[color] || COLORS.blue
    )}>
      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="text-2xl font-bold font-mono text-slate-900 mt-1">{value}</p>
      {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
    </div>
  )
}

// ── Page Header ───────────────────────────────────────────────
export function PageHeader({ icon, title, subtitle }) {
  return (
    <div className="flex items-center gap-3 mb-6">
      {icon && <span className="text-3xl">{icon}</span>}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">{title}</h1>
        {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
    </div>
  )
}

// ── Section Header ────────────────────────────────────────────
export function SectionHeader({ title }) {
  return (
    <h3 className="text-[11px] font-bold uppercase tracking-widest text-slate-500 mt-8 mb-3 pb-2 border-b-2 border-slate-200">
      {title}
    </h3>
  )
}

// ── Card wrapper ──────────────────────────────────────────────
export function Card({ children, className = '' }) {
  return (
    <div className={clsx('bg-white rounded-xl border border-slate-200 shadow-sm p-5 animate-in', className)}>
      {children}
    </div>
  )
}

// ── Ranking Row ───────────────────────────────────────────────
export function RankingRow({ pos, ds, taxa, meta, atingiu }) {
  return (
    <div className="flex items-center justify-between py-3 px-4 border-b border-slate-100 last:border-b-0 hover:bg-slate-50 transition-colors">
      <div className="flex items-center gap-3">
        <span className={clsx(
          'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold',
          pos <= 3 ? 'bg-imile-500 text-white' : 'bg-slate-100 text-slate-500'
        )}>
          {pos}
        </span>
        <span className="text-sm font-medium text-slate-800">{ds}</span>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm font-mono font-semibold text-slate-700">
          {(taxa * 100).toFixed(1)}%
        </span>
        <span className={clsx(
          'w-2.5 h-2.5 rounded-full',
          atingiu ? 'bg-emerald-500' : 'bg-red-500'
        )} />
      </div>
    </div>
  )
}

// ── Loading skeleton ──────────────────────────────────────────
export function Skeleton({ className = 'h-4 w-full' }) {
  return (
    <div className={clsx('animate-pulse rounded bg-slate-200', className)} />
  )
}

// ── Alert bar ─────────────────────────────────────────────────
export function Alert({ type = 'warning', children }) {
  const styles = {
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    error:   'bg-red-50 border-red-200 text-red-800',
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    info:    'bg-blue-50 border-blue-200 text-blue-800',
  }
  return (
    <div className={clsx('px-4 py-3 rounded-lg border text-sm', styles[type])}>
      {children}
    </div>
  )
}
