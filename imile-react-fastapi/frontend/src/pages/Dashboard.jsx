/**
 * pages/Dashboard.jsx — Dashboard completo
 * KPIs, filtro por DS, comparativo D-1, gráficos, ranking, download Excel
 */
import { useState, useEffect, useMemo } from 'react'
import api from '../lib/api'
import { useAuth } from '../lib/AuthContext'
import { PageHeader, KpiCard, SectionHeader, Card, RankingRow, Alert, Skeleton } from '../components/ui'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, Label,
} from 'recharts'
import { RefreshCw, Download, Filter } from 'lucide-react'

const COLORS_BAR = { recebido: '#2563eb', expedido: '#f97316', entregas: '#10b981' }
const COLORS_PIE = ['#2563eb', '#e2e8f0']

export default function Dashboard() {
  const { isAdmin } = useAuth()
  const [datas, setDatas] = useState([])
  const [dataSel, setDataSel] = useState(null)
  const [dsSel, setDsSel] = useState([])
  const [data, setData] = useState(null)
  const [charts, setCharts] = useState(null)
  const [ontem, setOntem] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/dashboard/datas').then(res => {
      setDatas(res.data)
      if (res.data.length > 0) setDataSel(res.data[0])
    }).catch(() => {})
  }, [])

  useEffect(() => {
    if (!dataSel) return
    setLoading(true)
    const fetches = [
      api.get(`/api/dashboard/dia/${dataSel}`),
      api.get(`/api/dashboard/charts/${dataSel}`),
    ]
    // Comparativo D-1
    const d = new Date(dataSel + 'T12:00:00')
    d.setDate(d.getDate() - 1)
    const ontemStr = d.toISOString().slice(0, 10)
    fetches.push(api.get(`/api/dashboard/dia/${ontemStr}`).catch(() => ({ data: { kpis: {} } })))

    Promise.all(fetches).then(([dia, ch, ont]) => {
      setData(dia.data)
      setCharts(ch.data)
      setOntem(ont.data?.kpis || {})
    }).catch(() => {})
      .finally(() => setLoading(false))
  }, [dataSel])

  // Filtro por DS
  const filtered = useMemo(() => {
    if (!data || !dsSel.length) return data
    const stations = data.stations.filter(s => dsSel.includes(s.scan_station))
    const rec = stations.reduce((a, s) => a + s.recebido, 0)
    const exp = stations.reduce((a, s) => a + s.expedido, 0)
    const ent = stations.reduce((a, s) => a + s.entregas, 0)
    const nOk = stations.filter(s => s.atingiu_meta).length
    return {
      ...data,
      kpis: {
        recebido: rec, expedido: exp, entregas: ent,
        taxa_exp: rec ? Math.round(exp / rec * 10000) / 10000 : 0,
        taxa_ent: rec ? Math.round(ent / rec * 10000) / 10000 : 0,
        n_ds: stations.length, n_ok: nOk, n_abaixo: stations.length - nOk,
      },
      stations,
    }
  }, [data, dsSel])

  const filteredCharts = useMemo(() => {
    if (!charts || !dsSel.length) return charts
    return {
      ...charts,
      volume_ds: charts.volume_ds.filter(d => dsSel.includes(d.ds)),
      taxa_ds: charts.taxa_ds.filter(d => dsSel.includes(d.ds)),
    }
  }, [charts, dsSel])

  const fmtDate = (d) => { const [y, m, day] = d.split('-'); return `${day}/${m}/${y}` }
  const fmtNum = (n) => n?.toLocaleString('pt-BR') || '0'
  const fmtPct = (n) => `${(n * 100).toFixed(1)}%`

  const handleExcel = async () => {
    try {
      const res = await api.get(`/api/excel/dashboard/${dataSel}`, { responseType: 'blob' })
      const url = URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a'); a.href = url
      a.download = `Dashboard_${dataSel}.xlsx`; a.click()
    } catch { alert('Erro ao gerar Excel') }
  }

  const d = filtered || data

  if (!datas.length) {
    return (
      <div>
        <PageHeader icon="📊" title="Dashboard" subtitle="Visão consolidada por dia" />
        <Alert type="info">Nenhum dado no histórico ainda. Processe os arquivos via processar.py.</Alert>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between">
        <PageHeader icon="📊" title="Dashboard" subtitle="Visão consolidada por dia · atualização automática" />
        <div className="flex gap-2">
          <button onClick={handleExcel}
            className="flex items-center gap-2 px-4 py-2 bg-navy-900 text-white rounded-lg text-sm font-medium hover:bg-navy-800 transition-colors">
            <Download size={14} /> Excel
          </button>
          <button onClick={() => { setLoading(true); setDataSel(ds => ds) }}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50 transition-colors">
            <RefreshCw size={14} /> Atualizar
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-slate-100 rounded-xl p-4 mb-6 border border-slate-200">
        <div className="flex items-center gap-2 mb-3">
          <Filter size={14} className="text-slate-500" />
          <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Filtros</span>
        </div>
        <div className="flex flex-wrap gap-4">
          <select value={dataSel || ''} onChange={(e) => { setDataSel(e.target.value); setDsSel([]) }}
            className="px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm">
            {datas.map(d => <option key={d} value={d}>{fmtDate(d)}</option>)}
          </select>
          <select multiple value={dsSel}
            onChange={(e) => setDsSel(Array.from(e.target.selectedOptions, o => o.value))}
            className="px-3 py-2 rounded-lg border border-slate-200 bg-white text-sm min-w-[200px] max-h-[120px]">
            {data?.ds_disponiveis?.map(ds => <option key={ds} value={ds}>{ds}</option>)}
          </select>
          {dsSel.length > 0 && (
            <button onClick={() => setDsSel([])}
              className="px-3 py-2 text-xs text-red-600 hover:bg-red-50 rounded-lg transition-colors">
              Limpar filtro ({dsSel.length} selecionadas)
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-24 rounded-xl" />)}
        </div>
      ) : d && (
        <>
          {/* Alertas */}
          {d.alertas?.length > 0 && (
            <Alert type="warning">
              ⚠️ <strong>{d.alertas.length} DS abaixo da meta:</strong> {d.alertas.slice(0, 5).join(', ')}
              {d.alertas.length > 5 && ' e outros...'}
            </Alert>
          )}

          {/* KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-4">
            <KpiCard label="Recebido"   value={fmtNum(d.kpis.recebido)}  sub="waybills no dia"                          color="blue" />
            <KpiCard label="Em Rota"    value={fmtNum(d.kpis.expedido)}  sub={`taxa ${fmtPct(d.kpis.taxa_exp)}`}        color="orange" />
            <KpiCard label="Entregas"   value={fmtNum(d.kpis.entregas)}  sub={d.kpis.entregas ? `taxa ${fmtPct(d.kpis.taxa_ent)}` : 'sem dados'} color="violet" />
            <KpiCard label="DS na Meta" value={d.kpis.n_ok}              sub={`de ${d.kpis.n_ds} bases`}                 color="green" />
            <KpiCard label="DS Abaixo"  value={d.kpis.n_abaixo}          sub="precisam atenção"                          color="red" />
          </div>

          {/* Comparativo D-1 */}
          {ontem?.recebido > 0 && (
            <div className="grid grid-cols-3 gap-4 mt-4">
              {[
                { label: 'Recebido', val: d.kpis.recebido - ontem.recebido },
                { label: 'Expedido', val: d.kpis.expedido - ontem.expedido },
                { label: 'Taxa',     val: d.kpis.taxa_exp - (ontem.taxa_exp || 0), pct: true },
              ].map(({ label, val, pct }) => (
                <div key={label} className="bg-white rounded-xl border border-slate-200 p-4 text-center">
                  <p className="text-xs text-slate-500">{label} vs ontem</p>
                  <p className={`text-lg font-bold font-mono ${val >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                    {val >= 0 ? '+' : ''}{pct ? fmtPct(val) : fmtNum(val)}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* Charts */}
          {(filteredCharts || charts) && (() => {
            const ch = filteredCharts || charts
            return (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-6">
                <Card className="lg:col-span-2">
                  <h3 className="text-sm font-semibold text-slate-700 mb-4">Volume por DS</h3>
                  <ResponsiveContainer width="100%" height={340}>
                    <BarChart data={ch.volume_ds.slice(0, 20)} margin={{ bottom: 60 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="ds" tick={{ fontSize: 10 }} angle={-40} textAnchor="end" />
                      <YAxis tick={{ fontSize: 11 }} tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
                      <Tooltip formatter={(v) => fmtNum(v)} />
                      <Legend />
                      <Bar dataKey="recebido" fill={COLORS_BAR.recebido} name="Recebido" radius={[3,3,0,0]} />
                      <Bar dataKey="expedido" fill={COLORS_BAR.expedido} name="Expedido" radius={[3,3,0,0]} />
                      <Bar dataKey="entregas" fill={COLORS_BAR.entregas} name="Entregas" radius={[3,3,0,0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </Card>

                <Card>
                  <h3 className="text-sm font-semibold text-slate-700 mb-4">Proporção de Expedição</h3>
                  <ResponsiveContainer width="100%" height={340}>
                    <PieChart>
                      <Pie data={[
                        { name: 'Expedido', value: ch.donut.expedido },
                        { name: 'Backlog',  value: ch.donut.backlog },
                      ]} cx="50%" cy="50%" innerRadius={80} outerRadius={110} paddingAngle={2} dataKey="value">
                        {COLORS_PIE.map((c, i) => <Cell key={i} fill={c} />)}
                        <Label value={fmtPct(ch.donut.taxa)} position="center" className="text-2xl font-bold" fill="#0f172a" />
                      </Pie>
                      <Tooltip formatter={(v) => fmtNum(v)} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </Card>
              </div>
            )
          })()}

          {/* Taxa por DS — horizontal bar */}
          <SectionHeader title="Taxa de Expedição por DS" />
          <Card>
            <ResponsiveContainer width="100%" height={Math.max(300, (d.stations?.length || 0) * 28 + 60)}>
              <BarChart data={d.stations?.slice().sort((a, b) => a.taxa_exp - b.taxa_exp)} layout="vertical" margin={{ left: 80, right: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" tickFormatter={v => `${(v*100).toFixed(0)}%`} domain={[0, 1.1]} />
                <YAxis type="category" dataKey="scan_station" tick={{ fontSize: 11 }} width={75} />
                <Tooltip formatter={v => fmtPct(v)} />
                <Bar dataKey="taxa_exp" name="Taxa Exp." radius={[0,4,4,0]}
                  fill="#10b981"
                  label={{ position: 'right', formatter: v => `${(v*100).toFixed(1)}%`, fontSize: 10 }}
                />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Ranking */}
          <SectionHeader title="Ranking por Taxa de Expedição" />
          <Card>
            <div className="max-h-[500px] overflow-y-auto">
              {d.stations?.map((s, i) => (
                <RankingRow key={s.scan_station} pos={i + 1} ds={s.scan_station}
                  taxa={s.taxa_exp} meta={s.meta} atingiu={s.atingiu_meta} />
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  )
}
