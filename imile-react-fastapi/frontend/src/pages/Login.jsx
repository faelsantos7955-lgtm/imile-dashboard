/**
 * pages/Login.jsx — Tela de login corporativa
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/AuthContext'
import { Truck, Eye, EyeOff } from 'lucide-react'
import api from '../lib/api'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [tab, setTab] = useState('login')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')

  // Registro
  const [regNome, setRegNome] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regMotivo, setRegMotivo] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    if (!email || !senha) { setError('Preencha email e senha.'); return }
    setLoading(true)
    try {
      await login(email.trim(), senha)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Email ou senha incorretos.')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError(''); setSuccess('')
    if (!regNome || !regEmail) { setError('Nome e email são obrigatórios.'); return }
    setLoading(true)
    try {
      await api.post('/api/auth/register', {
        nome: regNome.trim(),
        email: regEmail.trim(),
        motivo: regMotivo.trim(),
      })
      setSuccess('Solicitação enviada! Aguarde aprovação do administrador.')
      setRegNome(''); setRegEmail(''); setRegMotivo('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao enviar.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-blue-50 to-slate-100 relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-[0.03]"
        style={{ backgroundImage: 'radial-gradient(circle, #2563eb 1px, transparent 1px)', backgroundSize: '24px 24px' }}
      />

      <div className="relative z-10 w-full max-w-md px-4">
        {/* Logo */}
        <div className="text-center mb-8">
          <Truck size={48} className="mx-auto text-imile-500 mb-3" />
          <h1 className="text-2xl font-bold text-imile-700">
            iMile <span className="text-imile-500">Delivery</span>
          </h1>
          <div className="w-32 h-0.5 bg-imile-500 mx-auto mt-2 rounded-full" />
          <p className="text-[11px] tracking-[3px] text-slate-500 uppercase mt-2">
            Portal Operacional · Brasil
          </p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">

          {/* Tab login / registro */}
          {tab === 'login' ? (
            <form onSubmit={handleLogin} className="p-8">
              <h2 className="text-xl font-bold text-slate-900">Bem-vindo de volta</h2>
              <p className="text-sm text-slate-500 mt-1">Acesso restrito à equipe iMile Brasil</p>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Email</label>
                  <input
                    type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                    placeholder="seu@email.com"
                    className="mt-1 w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-imile-500/20 focus:border-imile-500 transition-all"
                  />
                </div>

                <div>
                  <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Senha</label>
                  <div className="relative mt-1">
                    <input
                      type={showPw ? 'text' : 'password'} value={senha} onChange={(e) => setSenha(e.target.value)}
                      placeholder="••••••••"
                      className="w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-imile-500/20 focus:border-imile-500 transition-all pr-11"
                    />
                    <button type="button" onClick={() => setShowPw(!showPw)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                      {showPw ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>
              </div>

              {error && <p className="mt-4 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>}

              <button type="submit" disabled={loading}
                className="mt-6 w-full py-3 rounded-lg bg-imile-500 text-white font-semibold text-sm hover:bg-imile-600 active:scale-[0.98] transition-all disabled:opacity-50 shadow-lg shadow-imile-500/25">
                {loading ? 'Entrando...' : 'Entrar no portal →'}
              </button>

              <div className="mt-4 text-center">
                <div className="text-xs text-slate-400 mb-2">ou</div>
                <button type="button" onClick={() => { setTab('register'); setError('') }}
                  className="w-full py-2.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 transition-colors">
                  Solicitar acesso
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="p-8">
              <h2 className="text-xl font-bold text-slate-900">Solicitar Acesso</h2>
              <p className="text-sm text-slate-500 mt-1">O administrador receberá sua solicitação.</p>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Nome completo</label>
                  <input type="text" value={regNome} onChange={(e) => setRegNome(e.target.value)}
                    placeholder="João Silva"
                    className="mt-1 w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-imile-500/20 focus:border-imile-500" />
                </div>
                <div>
                  <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Email corporativo</label>
                  <input type="email" value={regEmail} onChange={(e) => setRegEmail(e.target.value)}
                    placeholder="joao.silva@imile.com"
                    className="mt-1 w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-imile-500/20 focus:border-imile-500" />
                </div>
                <div>
                  <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Motivo</label>
                  <textarea value={regMotivo} onChange={(e) => setRegMotivo(e.target.value)}
                    placeholder="Área de atuação, região, motivo do acesso..."
                    rows={3}
                    className="mt-1 w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-imile-500/20 focus:border-imile-500 resize-none" />
                </div>
              </div>

              {error && <p className="mt-4 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>}
              {success && <p className="mt-4 text-sm text-emerald-700 bg-emerald-50 px-3 py-2 rounded-lg">{success}</p>}

              <button type="submit" disabled={loading}
                className="mt-6 w-full py-3 rounded-lg bg-imile-500 text-white font-semibold text-sm hover:bg-imile-600 transition-all disabled:opacity-50">
                {loading ? 'Enviando...' : 'Enviar solicitação'}
              </button>

              <button type="button" onClick={() => { setTab('login'); setError(''); setSuccess('') }}
                className="mt-3 w-full py-2.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 transition-colors">
                ← Voltar ao login
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
