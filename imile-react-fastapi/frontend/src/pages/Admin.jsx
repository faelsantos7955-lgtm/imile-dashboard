/**
 * pages/Admin.jsx — Painel administrativo completo
 * Tabs: Solicitações, Usuários, Motoristas
 */
import { useState, useEffect } from 'react'
import api from '../lib/api'
import { PageHeader, Card, Alert, SectionHeader } from '../components/ui'
import { Check, X, UserPlus, Truck, Shield } from 'lucide-react'

const ROLES = [
  { value: 'viewer',     label: '👁️ Viewer' },
  { value: 'operador',   label: '🔧 Operador' },
  { value: 'supervisor', label: '📋 Supervisor' },
  { value: 'admin',      label: '🔑 Admin' },
]

export default function Admin() {
  const [tab, setTab] = useState('solicitacoes')

  const TABS = [
    { key: 'solicitacoes', label: '⏳ Solicitações', icon: UserPlus },
    { key: 'usuarios',     label: '👤 Usuários',     icon: Shield },
    { key: 'motoristas',   label: '🚗 Motoristas',   icon: Truck },
  ]

  return (
    <div>
      <PageHeader icon="⚙️" title="Administração" subtitle="Gestão de usuários, motoristas e configurações" />

      <div className="flex gap-1 bg-slate-100 rounded-lg p-1 w-fit mb-6">
        {TABS.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
              tab === t.key ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
            }`}>
            <t.icon size={16} /> {t.label}
          </button>
        ))}
      </div>

      {tab === 'solicitacoes' && <Solicitacoes />}
      {tab === 'usuarios' && <Usuarios />}
      {tab === 'motoristas' && <Motoristas />}
    </div>
  )
}


function Solicitacoes() {
  const [sols, setSols] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.get('/api/admin/solicitacoes?status=pendente')
      .then(r => setSols(r.data)).catch(() => {})
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const aprovar = async (id, role) => {
    await api.post(`/api/admin/solicitacoes/${id}/aprovar?role=${role}`)
    load()
  }
  const rejeitar = async (id) => {
    await api.post(`/api/admin/solicitacoes/${id}/rejeitar`)
    load()
  }

  if (!sols.length) return <Alert type="success">Nenhuma solicitação pendente!</Alert>

  return (
    <div className="space-y-4">
      <Alert type="info"><strong>{sols.length}</strong> solicitação(ões) aguardando aprovação</Alert>
      {sols.map(s => (
        <Card key={s.id}>
          <div className="flex items-start justify-between">
            <div>
              <p className="font-semibold text-slate-900">{s.nome}</p>
              <p className="text-sm text-slate-500">{s.email}</p>
              {s.motivo && <p className="text-sm text-slate-600 mt-2 bg-slate-50 px-3 py-2 rounded-lg">"{s.motivo}"</p>}
              <p className="text-xs text-slate-400 mt-2">Solicitado em: {s.criado_em?.slice(0, 10)}</p>
            </div>
            <div className="flex items-center gap-2">
              <select id={`role-${s.id}`} defaultValue="viewer"
                className="px-2 py-1 text-xs rounded border border-slate-200">
                {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
              <button onClick={() => aprovar(s.id, document.getElementById(`role-${s.id}`).value)}
                className="p-2 bg-emerald-100 text-emerald-700 rounded-lg hover:bg-emerald-200 transition-colors">
                <Check size={16} />
              </button>
              <button onClick={() => rejeitar(s.id)}
                className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors">
                <X size={16} />
              </button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}


function Usuarios() {
  const [users, setUsers] = useState([])
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.get('/api/admin/usuarios').then(r => setUsers(r.data)).catch(() => {})
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const salvar = async (uid) => {
    const el = (id) => document.getElementById(id)?.value
    await api.put(`/api/admin/usuarios/${uid}`, {
      role: el(`role-${uid}`) || 'viewer',
      ativo: el(`ativo-${uid}`) === 'true',
      bases: [],
      paginas: [],
    })
    setEditing(null)
    load()
  }

  return (
    <div>
      <p className="text-sm text-slate-500 mb-4">{users.length} usuário(s) cadastrado(s)</p>
      <div className="space-y-3">
        {users.map(u => (
          <Card key={u.id}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`w-2.5 h-2.5 rounded-full ${u.ativo ? 'bg-emerald-500' : 'bg-red-500'}`} />
                <div>
                  <p className="font-medium text-slate-900">{u.nome || u.email}</p>
                  <p className="text-xs text-slate-500">{u.email} · <code className="bg-slate-100 px-1 rounded">{u.role}</code></p>
                </div>
              </div>

              {editing === u.id ? (
                <div className="flex items-center gap-2">
                  <select id={`role-${u.id}`} defaultValue={u.role}
                    className="px-2 py-1 text-xs rounded border border-slate-200">
                    {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                  </select>
                  <select id={`ativo-${u.id}`} defaultValue={String(u.ativo)}
                    className="px-2 py-1 text-xs rounded border border-slate-200">
                    <option value="true">Ativo</option>
                    <option value="false">Inativo</option>
                  </select>
                  <button onClick={() => salvar(u.id)}
                    className="px-3 py-1 text-xs bg-imile-500 text-white rounded-lg hover:bg-imile-600">
                    Salvar
                  </button>
                  <button onClick={() => setEditing(null)}
                    className="px-3 py-1 text-xs text-slate-500 hover:text-slate-700">
                    Cancelar
                  </button>
                </div>
              ) : (
                <button onClick={() => setEditing(u.id)}
                  className="text-xs text-imile-500 hover:underline">
                  Editar
                </button>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}


function Motoristas() {
  const [motoristas, setMotoristas] = useState([])
  const [form, setForm] = useState({ id_motorista: '', nome_motorista: '', ativo: true, motivo: '' })
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.get('/api/reclamacoes/motoristas').then(r => setMotoristas(r.data)).catch(() => {})
      .finally(() => setLoading(false))
  }
  useEffect(load, [])

  const salvar = async (e) => {
    e.preventDefault()
    if (!form.id_motorista.trim()) return
    await api.post('/api/admin/motoristas', form)
    setForm({ id_motorista: '', nome_motorista: '', ativo: true, motivo: '' })
    load()
  }

  const toggle = async (m) => {
    await api.post('/api/admin/motoristas', {
      id_motorista: m.id_motorista,
      nome_motorista: m.nome_motorista,
      ativo: !m.ativo,
      motivo: m.motivo || '',
    })
    load()
  }

  const ativos = motoristas.filter(m => m.ativo !== false)
  const inativos = motoristas.filter(m => m.ativo === false)

  return (
    <div>
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card><p className="text-xs text-slate-500">Total</p><p className="text-xl font-bold font-mono">{motoristas.length}</p></Card>
        <Card><p className="text-xs text-slate-500">Ativos</p><p className="text-xl font-bold font-mono text-emerald-600">{ativos.length}</p></Card>
        <Card><p className="text-xs text-slate-500">Inativos</p><p className="text-xl font-bold font-mono text-red-600">{inativos.length}</p></Card>
      </div>

      {/* Formulário */}
      <SectionHeader title="Cadastrar / Atualizar motorista" />
      <Card>
        <form onSubmit={salvar} className="grid grid-cols-2 md:grid-cols-5 gap-3 items-end">
          <div>
            <label className="text-[10px] font-semibold uppercase text-slate-500">ID Motorista *</label>
            <input value={form.id_motorista} onChange={e => setForm({...form, id_motorista: e.target.value})}
              placeholder="DRV001" className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 text-sm" />
          </div>
          <div>
            <label className="text-[10px] font-semibold uppercase text-slate-500">Nome</label>
            <input value={form.nome_motorista} onChange={e => setForm({...form, nome_motorista: e.target.value})}
              placeholder="João Silva" className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 text-sm" />
          </div>
          <div>
            <label className="text-[10px] font-semibold uppercase text-slate-500">Status</label>
            <select value={form.ativo} onChange={e => setForm({...form, ativo: e.target.value === 'true'})}
              className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 text-sm">
              <option value="true">Ativo</option>
              <option value="false">Inativo</option>
            </select>
          </div>
          <div>
            <label className="text-[10px] font-semibold uppercase text-slate-500">Motivo</label>
            <input value={form.motivo} onChange={e => setForm({...form, motivo: e.target.value})}
              placeholder="Afastado, desligado..." className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 text-sm" />
          </div>
          <button type="submit" className="px-4 py-2 bg-imile-500 text-white rounded-lg text-sm font-medium hover:bg-imile-600">
            Salvar
          </button>
        </form>
      </Card>

      {/* Lista */}
      <SectionHeader title="Motoristas cadastrados" />
      <Card>
        <div className="max-h-[400px] overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-slate-100">
              <tr className="text-xs uppercase text-slate-600">
                <th className="px-3 py-2 text-left">ID</th>
                <th className="px-3 py-2 text-left">Nome</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2 text-left">Motivo</th>
                <th className="px-3 py-2">Ação</th>
              </tr>
            </thead>
            <tbody>
              {motoristas.map(m => (
                <tr key={m.id_motorista} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="px-3 py-2 font-mono text-xs">{m.id_motorista}</td>
                  <td className="px-3 py-2">{m.nome_motorista || '—'}</td>
                  <td className="px-3 py-2 text-center">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                      m.ativo !== false ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
                    }`}>{m.ativo !== false ? 'Ativo' : 'Inativo'}</span>
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-500">{m.motivo || '—'}</td>
                  <td className="px-3 py-2 text-center">
                    <button onClick={() => toggle(m)}
                      className={`text-xs font-medium ${m.ativo !== false ? 'text-red-600 hover:underline' : 'text-emerald-600 hover:underline'}`}>
                      {m.ativo !== false ? 'Desativar' : 'Reativar'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
