/**
 * pages/Triagem.jsx — Triagem DC×DS com gráficos e download
 */
import { useState, useEffect } from 'react'
import api from '../lib/api'
import { PageHeader, KpiCard, SectionHeader, Card, Alert } from '../components/ui'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell,
} from 'recharts'
import { Download } from 'lucide-react'

export default function Triagem() {
  const [uploads, setUploads] = useState([])
  const [sel, setSel] = useState(null)
  const [detail, setDetail] = useState(null)

  useEffect(() => {
    api.get('/api/triagem/uploads').then(r => {
      setUploads(r.data)
      if (r.data.length) setSel(r.data[0].id)
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (!sel) return
    api.get(`/api/triagem/upload/${sel}`).then(r => setDetail(r.data)).catch(() => {})
  }, [sel])

  const u = uploads.find(x => x.id === sel)
  const fmtNum = (n) => n?.toLocaleString('pt-BR') || '0'

  const handleExcel = async () => {
    try {
      const res = await api.get(`/api/excel/triagem/${sel}`, { responseType: 'blob' })
      const url = URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a'); a.href = url
      a.download = `Triagem_${u?.data_ref || 'relatorio'}.xlsx`; a.click()
    } catch { alert('Erro ao gerar Excel') }
  }

  return (
    <div>
      <PageHeader icon="🔀" title="Triagem DC×DS" subtitle="Análise de erros de expedição — OUT BOUND" />

      {!uploads.length ? <Alert type="info">Nenhum dado disponível.</Alert> : (
        <>
          <div className="flex items-center gap-4 mb-6">
            <select value={sel || ''} onChange={(e) => setSel(Number(e.target.value))}
              className="px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm flex-1 max-w-md">
              {uploads.map(u => (
                <option key={u.id} value={u.id}>
                  {u.data_ref} — {fmtNum(u.qtd_ok)}/{fmtNum(u.total)} OK ({u.taxa}%)
                </option>
              ))}
            </select>
            <button onClick={handleExcel}
              className="flex items-center gap-2 px-4 py-2 bg-navy-900 text-white rounded-lg text-sm font-medium hover:bg-navy-800 transition-colors">
              <Download size={14} /> Excel
            </button>
          </div>

          {/* KPIs */}
          {u && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <KpiCard label="Total Expedido" value={fmtNum(u.total)}    color="blue" />
              <KpiCard label="Triagem OK"     value={fmtNum(u.qtd_ok)}   sub={`${u.taxa}%`} color="green" />
              <KpiCard label="Erros"          value={fmtNum(u.qtd_erro)} color="red" />
              <KpiCard label="Fora Abrangência" value={fmtNum(u.total - u.qtd_ok - u.qtd_erro)} color="slate" />
            </div>
          )}

          {detail && (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Gráfico stacked OK × NOK por DS */}
                <Card>
                  <h3 className="text-sm font-semibold text-slate-700 mb-4">OK × Erro por DS</h3>
                  <ResponsiveContainer width="100%" height={Math.max(280, (detail.por_ds?.length || 0) * 28 + 60)}>
                    <BarChart data={detail.por_ds?.sort((a, b) => b.total - a.total).slice(0, 15)} layout="vertical" margin={{ left: 80, right: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis type="number" />
                      <YAxis type="category" dataKey="ds" tick={{ fontSize: 11 }} width={75} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="ok" stackId="a" fill="#10b981" name="OK" />
                      <Bar dataKey="nok" stackId="a" fill="#ef4444" name="Erro" />
                      <Bar dataKey="fora" stackId="a" fill="#f59e0b" name="Fora" />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>

                {/* Top 5 erros */}
                <Card>
                  <h3 className="text-sm font-semibold text-slate-700 mb-4">Top 5 DS com mais erros</h3>
                  {detail.top5?.length > 0 ? (
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={detail.top5} layout="vertical" margin={{ left: 80, right: 40 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis type="number" />
                        <YAxis type="category" dataKey="ds" tick={{ fontSize: 11 }} width={75} />
                        <Tooltip />
                        <Bar dataKey="total_erros" name="Erros" radius={[0,4,4,0]}
                          label={{ position: 'right', fontSize: 11, fontWeight: 600 }}>
                          {detail.top5.map((_, i) => (
                            <Cell key={i} fill={['#dc2626','#ef4444','#f87171','#fca5a5','#fecaca'][i]} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-sm text-emerald-600 text-center py-8">Nenhum erro encontrado! 🎉</p>
                  )}
                </Card>
              </div>

              {/* Tabela por DS */}
              <SectionHeader title="Resultado por DS" />
              <Card>
                <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-slate-100">
                      <tr className="text-xs uppercase text-slate-600">
                        <th className="px-3 py-2 text-left">DS</th>
                        <th className="px-3 py-2 text-right">Total</th>
                        <th className="px-3 py-2 text-right">OK</th>
                        <th className="px-3 py-2 text-right">NOK</th>
                        <th className="px-3 py-2 text-right">Fora</th>
                        <th className="px-3 py-2 text-right">Taxa</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detail.por_ds?.sort((a, b) => a.taxa - b.taxa).map((r, i) => (
                        <tr key={i} className="border-t border-slate-100 hover:bg-slate-50">
                          <td className="px-3 py-2 font-medium">{r.ds}</td>
                          <td className="px-3 py-2 text-right font-mono">{fmtNum(r.total)}</td>
                          <td className="px-3 py-2 text-right font-mono text-emerald-600">{fmtNum(r.ok)}</td>
                          <td className="px-3 py-2 text-right font-mono text-red-600">{fmtNum(r.nok)}</td>
                          <td className="px-3 py-2 text-right font-mono text-amber-600">{fmtNum(r.fora)}</td>
                          <td className={`px-3 py-2 text-right font-mono font-semibold ${r.taxa >= 95 ? 'text-emerald-600' : 'text-red-600'}`}>
                            {r.taxa?.toFixed(1)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>

              {/* Por Supervisor */}
              {detail.por_supervisor?.length > 0 && (
                <>
                  <SectionHeader title="Por Supervisor" />
                  <Card>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-slate-100">
                          <tr className="text-xs uppercase text-slate-600">
                            <th className="px-3 py-2 text-left">Supervisor</th>
                            <th className="px-3 py-2 text-right">Total</th>
                            <th className="px-3 py-2 text-right">OK</th>
                            <th className="px-3 py-2 text-right">NOK</th>
                            <th className="px-3 py-2 text-right">Taxa</th>
                          </tr>
                        </thead>
                        <tbody>
                          {detail.por_supervisor.sort((a, b) => a.taxa - b.taxa).map((r, i) => (
                            <tr key={i} className="border-t border-slate-100 hover:bg-slate-50">
                              <td className="px-3 py-2 font-medium">{r.supervisor}</td>
                              <td className="px-3 py-2 text-right font-mono">{fmtNum(r.total)}</td>
                              <td className="px-3 py-2 text-right font-mono text-emerald-600">{fmtNum(r.ok)}</td>
                              <td className="px-3 py-2 text-right font-mono text-red-600">{fmtNum(r.nok)}</td>
                              <td className={`px-3 py-2 text-right font-mono font-semibold ${r.taxa >= 95 ? 'text-emerald-600' : 'text-red-600'}`}>
                                {r.taxa?.toFixed(1)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </Card>
                </>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}
