import { useState, useEffect } from 'react'
import { api } from '../api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'

export default function Forecast({ t }) {
  const [products, setProducts] = useState([])
  const [productId, setProductId] = useState('')
  const [days, setDays] = useState(14)
  const [engine, setEngine] = useState('xgboost')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.products().then(p => { setProducts(p); if (p.length) setProductId(String(p[0].id)) })
  }, [])

  const run = async () => {
    setLoading(true); setError(null); setResult(null)
    try { setResult(await api.forecast({ product_id: parseInt(productId), days, engine })) }
    catch (e) { setError(e.message) }
    setLoading(false)
  }

  const today = new Date().toISOString().slice(5, 10)
  const chartData = result ? [
    ...result.historical.slice(-60).map(h => ({ date: h.date?.slice(5), hist: h.qty, fc: null })),
    ...result.forecast.map(f => ({ date: f.date?.slice(5), hist: null, fc: f.predicted_qty }))
  ] : []

  return (
    <div className="page">
      <div className="page-title">{t.forecast_title}</div>
      <div className="page-desc">{t.forecast_desc}</div>

      <div className="card" style={{ marginBottom: 22 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr auto', gap: 14, alignItems: 'end' }}>
          <div className="form-group">
            <label className="form-label">{t.forecast_product}</label>
            <select className="select" value={productId} onChange={e => setProductId(e.target.value)}>
              {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">{t.forecast_days(days)}</label>
            <input type="range" min={7} max={30} value={days} onChange={e => setDays(+e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">{t.forecast_engine}</label>
            <div style={{ display: 'flex', gap: 5 }}>
              {['xgboost','prophet'].map(e => (
                <button key={e} className={`btn btn-sm ${engine===e?'btn-primary':'btn-ghost'}`} onClick={() => setEngine(e)}>
                  {e==='xgboost'?'XGBoost':'Prophet'}
                </button>
              ))}
            </div>
          </div>
          <button className="btn btn-primary" onClick={run} disabled={!productId || loading}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} />{t.forecast_running}</> : t.forecast_run}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}

      {!result && !loading && (
        <div className="empty-state">
          <div className="empty-state-icon">◎</div>
          <div className="empty-state-title">{t.forecast_configure}</div>
          <div className="empty-state-sub">{t.forecast_results_here}</div>
        </div>
      )}

      {result && (
        <>
          <div className="sh2">{result.product_name} — {days}-day ({result.engine})</div>
          <div className="card" style={{ padding: '14px 14px 8px', marginBottom: 20 }}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid stroke="rgba(99,102,241,0.07)" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: '#999', fontSize: 10 }} tickLine={false} axisLine={false} interval="preserveStartEnd" />
                <YAxis tick={{ fill: '#999', fontSize: 10 }} tickLine={false} axisLine={false} width={32} />
                <Tooltip contentStyle={{ background: 'white', border: '1.5px solid rgba(99,102,241,0.15)', borderRadius: 12, fontSize: 12, boxShadow: '0 4px 16px rgba(99,102,241,0.12)' }} />
                <Line type="monotone" dataKey="hist" name="Historical" stroke="rgba(99,102,241,0.2)" strokeWidth={2} dot={false} connectNulls={false} />
                <Line type="monotone" dataKey="fc" name={t.forecast_run} stroke="#6366f1" strokeWidth={2.5} dot={{ fill: '#6366f1', r: 3 }} connectNulls={false} />
                <ReferenceLine x={today} stroke="rgba(220,38,38,0.35)" strokeDasharray="3 3" label={{ value: t.forecast_today, fill: '#dc2626', fontSize: 10 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="grid-3">
            {[
              { label: t.forecast_total(result.stats.total_projected), value: result.stats.total_projected.toLocaleString(), cls: 'purple', clay: 'card-clay-purple' },
              { label: t.forecast_avg(result.stats.average_per_day), value: result.stats.average_per_day, cls: '', clay: '' },
              { label: 'Peak Day', value: result.stats.peak_date, cls: '', clay: '' },
            ].map(s => (
              <div key={s.label} className={`card ${s.clay}`}>
                <div className="card-label">{s.label}</div>
                <div className={`card-value ${s.cls}`} style={{ fontSize: 22 }}>{s.value}</div>
              </div>
            ))}
          </div>

          <div className="sh">{t.dash_col_date}</div>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <table>
              <thead><tr><th>{t.dash_col_date}</th><th>{t.forecast_total('')}</th></tr></thead>
              <tbody>
                {result.forecast.map((f, i) => (
                  <tr key={i}>
                    <td>{f.date}</td>
                    <td style={{ fontFamily: 'var(--mono)', fontWeight: 600, color: 'var(--purple)' }}>{f.predicted_qty}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="alert alert-info" style={{ marginTop: 14 }}>
            {t.forecast_total(result.stats.total_projected)} — {result.product_name}
          </div>
        </>
      )}
    </div>
  )
}
