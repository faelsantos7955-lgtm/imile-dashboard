/**
 * pages/Historico.jsx — Evolução por período
 */
import { useState, useEffect } from 'react'
import api from '../lib/api'
import { PageHeader, KpiCard, SectionHeader, Card, Alert } from '../components/ui'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, ComposedChart,
} from 'recharts'

export default function Historico() {
  const today = new Date().toISOString().slice(0, 10)
  const d30 = new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10)

  const [ini, setIni] = useState(d30)
  const [fim, setFim] = useState(today)
  const [data, setData] = useState(null)
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

  return (
    <div>
      <PageHeader icon="📅" title="Histórico" subtitle="Todos os dias processados" />

      <div className="flex gap-4 mb-6">
        <input type="date" value={ini} onChange={(e) => setIni(e.target.value)}
          className="px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm" />
        <input type="date" value={fim} onChange={(e) => setFim(e.target.value)}
          className="px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm" />
      </div>

      {!data?.resumo?.recebido ? (
        <Alert type="info">Nenhum dado no período selecionado.</Alert>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KpiCard label="Total Recebido" value={fmtNum(data.resumo.recebido)} color="blue" />
            <KpiCard label="Total Expedido" value={fmtNum(data.resumo.expedido)} color="orange" />
            <KpiCard label="Taxa Média"     value={fmtPct(data.resumo.taxa_exp)} color="green" />
            <KpiCard label="Dias"           value={data.resumo.dias}              color="slate" />
          </div>

          <SectionHeader title="Evolução Diária" />
          <Card>
            <ResponsiveContainer width="100%" height={380}>
              <ComposedChart data={data.por_dia} margin={{ bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="data_ref" tick={{ fontSize: 11 }} angle={-30} textAnchor="end"
                  tickFormatter={(d) => d.slice(5).replace('-', '/')} />
                <YAxis yAxisId="vol" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="taxa" orientation="right" tick={{ fontSize: 11 }} tickFormatter={(v) => `${(v*100).toFixed(0)}%`} />
                <Tooltip formatter={(v, n) => n === 'taxa_exp' ? fmtPct(v) : fmtNum(v)} />
                <Legend />
                <Bar yAxisId="vol" dataKey="recebido" fill="#60a5fa" opacity={0.6} name="Recebido" />
                <Bar yAxisId="vol" dataKey="expedido" fill="#f97316" opacity={0.6} name="Expedido" />
                <Line yAxisId="taxa" dataKey="taxa_exp" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} name="Taxa Exp." />
              </ComposedChart>
            </ResponsiveContainer>
          </Card>
        </>
      )}
    </div>
  )
}
