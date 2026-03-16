/**
 * components/Layout.jsx — Sidebar escura + área de conteúdo clara
 */
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/AuthContext'
import {
  LayoutDashboard, CalendarDays, BarChart3,
  GitBranch, FileWarning, Upload, Users, Settings,
  LogOut, Truck, Bell, HelpCircle, Search
} from 'lucide-react'
import clsx from 'clsx'

const NAV_ITEMS = [
  { to: '/',             icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/historico',    icon: CalendarDays,    label: 'Histórico' },
  { to: '/comparativos', icon: BarChart3,       label: 'Comparativos' },
  { to: '/triagem',      icon: GitBranch,       label: 'Triagem DC×DS' },
  { to: '/reclamacoes',  icon: FileWarning,     label: 'Reclamações' },
]

const ADMIN_ITEMS = [
  { to: '/admin',        icon: Upload,          label: 'Upload / Processar' },
  { to: '/admin/users',  icon: Users,           label: 'Solicitações' },
  { to: '/admin/config', icon: Settings,        label: 'Configurações' },
]

function SideLink({ to, icon: Icon, label }) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      className={({ isActive }) => clsx(
        'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
        isActive
          ? 'bg-imile-500 text-white shadow-lg shadow-imile-500/25'
          : 'text-slate-400 hover:text-white hover:bg-white/5'
      )}
    >
      <Icon size={18} strokeWidth={1.8} />
      <span>{label}</span>
    </NavLink>
  )
}

export default function Layout() {
  const { user, logout, isAdmin } = useAuth()
  const firstName = user?.nome?.split(' ')[0] || user?.email?.split('@')[0] || ''

  return (
    <div className="flex h-screen overflow-hidden">

      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className="w-64 bg-navy-950 flex flex-col shrink-0 border-r border-white/5">

        {/* Logo */}
        <div className="px-6 py-5 border-b border-white/5">
          <div className="flex items-center gap-2">
            <Truck size={28} className="text-imile-500" />
            <span className="text-lg font-bold text-white tracking-tight">
              iMile <span className="text-imile-500">Delivery</span>
            </span>
          </div>
        </div>

        {/* User info */}
        <div className="px-6 py-4">
          <p className="text-xs text-slate-500">Olá,</p>
          <p className="text-sm font-semibold text-white">{firstName}</p>
          {isAdmin && (
            <span className="inline-block mt-1 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-imile-500/20 text-imile-500 rounded-full">
              Admin
            </span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
          <p className="px-4 pt-2 pb-1 text-[10px] font-bold uppercase tracking-widest text-slate-600">
            Navegação
          </p>
          {NAV_ITEMS.map((item) => (
            <SideLink key={item.to} {...item} />
          ))}

          {isAdmin && (
            <>
              <div className="my-3 border-t border-white/5" />
              <p className="px-4 pb-1 text-[10px] font-bold uppercase tracking-widest text-red-400/70">
                Administração
              </p>
              {ADMIN_ITEMS.map((item) => (
                <SideLink key={item.to} {...item} />
              ))}
            </>
          )}
        </nav>

        {/* Logout */}
        <div className="p-3 border-t border-white/5">
          <button
            onClick={logout}
            className="flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm text-red-400 hover:bg-red-500/10 transition-colors"
          >
            <LogOut size={18} />
            <span>Sair</span>
          </button>
        </div>
      </aside>

      {/* ── Content Area ────────────────────────────────────── */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Top bar */}
        <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-end px-6 gap-3 shrink-0">
          <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <Bell size={18} />
          </button>
          <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <HelpCircle size={18} />
          </button>
          <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <Search size={18} />
          </button>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-imile-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
            {firstName[0]?.toUpperCase() || '?'}
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-slate-50 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
