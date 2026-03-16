/**
 * pages/Comparativos.jsx — Evolução por dia, semana, mês + DS lines
 */
import { useState, useEffect, useMemo } from 'react'
import api from '../lib/api'
import { PageHeader, KpiCard, SectionHeader, Card, Alert } from '../components/ui'
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart,
} from 'recharts'

export default function Comparativos() {
  const today = new Date().toISOString().slice(0, 10)
  const d90 = new Date(Date.now() - 90 * 86400000).toISOString().slice(0, 10)

  const [ini, setIni] = useState(d90)
  const [fim, setFim] = useState(today)
  const [data, setData] = useState(null)
  const [tab, setTab] = useState('dia')
  const [dsSel, setDsSel] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!ini || !fim) return
    setLoading(true)
    api.get('/api/historico/periodo', { params: { data_ini: ini, data_fim: fim } })
      .then(res => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [ini, fim])

  const fmtNum = (n) => n?.toLocaleString('pt-BR') || '0'
  const fmtPct = (n) => `${(n * 100).toFixed(1)}%`

  // Agregar por semana ou mês
  const aggregated = useMemo(() => {
    if (!data?.por_dia) return []
    const src = data.por_dia

    if (tab === 'dia') return src

    const groups = {}
    src.forEach(d => {
      let key
      if (tab === 'semana') {
        const dt = new Date(d.data_ref + 'T12:00:00')
        const week = Math.ceil((dt.getDate()) / 7)
        key = `S${String(week).padStart(2, '0')}/${d.data_ref.slice(5, 7)}`
      } else {
        key = d.data_ref.slice(0, 7) // YYYY-MM
      }
      if (!groups[key]) groups[key] = { periodo: key, recebido: 0, expedido: 0, entregas: 0 }
      groups[key].recebido += d.recebido
      groups[key].expedido += d.expedido
      groups[key].entregas += d.entregas
    })

    return Object.values(groups).map(g => ({
      ...g,
      taxa_exp: g.recebido > 0 ? Math.round(g.expedido / g.recebido * 10000) / 10000 : 0,
    }))
  }, [data, tab])

  // Top 10 DS para gráfico de evolução
  const dsOptions = useMemo(() => {
    if (!data?.por_ds) return []
    return data.por_ds.slice(0, 30).map(d => d.scan_station)
  }, [data])

  // Evolução por DS (raw data from por_dia is aggregated, we need per-DS data)
  // We'll use the por_ds for ranking chart instead
  const dsRanking = useMemo(() => {
    if (!data?.por_ds) return []
    return data.por_ds.slice(0, 15).map(d => ({
      ds: d.scan_station,
      recebido: d.recebido,
      expedido: d.expedido,
      taxa_exp: d.taxa_exp,
    }))
  }, [data])

  const TABS = [
    { key: 'dia', label: '📅 Diário' },
    { key: 'semana', label: '📆 Semanal' },
    { key: 'mes', label: '🗓️ Mensal' },
  ]

  return (
    <div>
      <PageHeader icon="📈" title="Comparativos" subtitle="Evolução por dia, semana e mês" />

      <div className="flex gap-4 mb-6">
        <div>
          <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">De</label>
          <input type="date" value={ini} onChange={(e) => setIni(e.target.value)}
            className="block mt-1 px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm" />
        </div>
        <div>
          <label className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Até</label>
          <input type="date" value={fim} onChange={(e) => setFim(e.target.value)}
            className="block mt-1 px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm" />
        </div>
      </div>

      {!data?.resumo?.recebido ? (
        <Alert type="info">Nenhum dado no período selecionado.</Alert>
      ) : (
        <>
          {/* KPIs do período */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <KpiCard label="Total Recebido" value={fmtNum(data.resumo.recebido)} color="blue" />
            <KpiCard label="Total Expedido" value={fmtNum(data.resumo.expedido)} color="orange" />
            <KpiCard label="Taxa Média"     value={fmtPct(data.resumo.taxa_exp)} color="green" />
            <KpiCard label="Dias"           value={data.resumo.dias}              color="slate" />
          </div>

          {/* Tabs */}
          <div className="flex gap-1 bg-slate-100 rounded-lg p-1 w-fit mb-6">
            {TABS.map(t => (
              <button key={t.key} onClick={() => setTab(t.key)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  tab === t.key ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}>
                {t.label}
              </button>
            ))}
          </div>

          {/* Chart principal */}
          <Card>
            <h3 className="text-sm font-semibold text-slate-700 mb-4">
              Comparativo — {TABS.find(t => t.key === tab)?.label}
            </h3>
            <ResponsiveContainer width="100%" height={400}>
              <ComposedChart data={aggregated} margin={{ bottom: 50 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey={tab === 'dia' ? 'data_ref' : 'periodo'}
                  tick={{ fontSize: 11 }} angle={-30} textAnchor="end"
                  tickFormatter={v => tab === 'dia' ? v.slice(5).replace('-', '/') : v} />
                <YAxis yAxisId="vol" tick={{ fontSize: 11 }}
                  tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
                <YAxis yAxisId="taxa" orientation="right" tick={{ fontSize: 11 }}
                  tickFormatter={v => `${(v*100).toFixed(0)}%`} domain={[0, 1.1]} />
                <Tooltip formatter={(v, n) => n === 'Taxa Exp.' ? fmtPct(v) : fmtNum(v)} />
                <Legend />
                <Bar yAxisId="vol" dataKey="recebido" fill="#2563eb" opacity={0.7} name="Recebido" radius={[3,3,0,0]} />
                <Bar yAxisId="vol" dataKey="expedido" fill="#f97316" opacity={0.7} name="Expedido" radius={[3,3,0,0]} />
                <Line yAxisId="taxa" dataKey="taxa_exp" stroke="#10b981" strokeWidth={3}
                  dot={{ r: 4, fill: '#10b981' }} name="Taxa Exp."
                  label={{ position: 'top', formatter: v => `${(v*100).toFixed(0)}%`, fontSize: 10, fill: '#10b981' }} />
              </ComposedChart>
            </ResponsiveContainer>
          </Card>

          {/* Ranking por DS no período */}
          <SectionHeader title="Ranking por DS no período" />
          <Card>
            <ResponsiveContainer width="100%" height={Math.max(300, dsRanking.length * 32 + 40)}>
              <ComposedChart data={dsRanking} layout="vertical" margin={{ left: 80, right: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
                <YAxis type="category" dataKey="ds" tick={{ fontSize: 11 }} width={75} />
                <Tooltip formatter={(v, n) => n === 'Taxa' ? fmtPct(v) : fmtNum(v)} />
                <Legend />
                <Bar dataKey="recebido" fill="#60a5fa" name="Recebido" opacity={0.6} />
                <Bar dataKey="expedido" fill="#10b981" name="Expedido" opacity={0.6} />
              </ComposedChart>
            </ResponsiveContainer>
          </Card>

          {/* Tabela resumo por dia */}
          <SectionHeader title="Resumo por dia" />
          <Card>
            <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-slate-100">
                  <tr className="text-xs uppercase text-slate-600">
                    <th className="px-3 py-2 text-left">Data</th>
                    <th className="px-3 py-2 text-right">Recebido</th>
                    <th className="px-3 py-2 text-right">Expedido</th>
                    <th className="px-3 py-2 text-right">Entregas</th>
                    <th className="px-3 py-2 text-right">Taxa Exp.</th>
                  </tr>
                </thead>
                <tbody>
                  {data.por_dia?.map((r, i) => (
                    <tr key={i} className="border-t border-slate-100 hover:bg-slate-50">
                      <td className="px-3 py-2 font-medium">{fmtDate(r.data_ref)}</td>
                      <td className="px-3 py-2 text-right font-mono">{fmtNum(r.recebido)}</td>
                      <td className="px-3 py-2 text-right font-mono">{fmtNum(r.expedido)}</td>
                      <td className="px-3 py-2 text-right font-mono">{fmtNum(r.entregas)}</td>
                      <td className="px-3 py-2 text-right font-mono">{fmtPct(r.taxa_exp)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  )
}

function fmtDate(d) {
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y}`
}
