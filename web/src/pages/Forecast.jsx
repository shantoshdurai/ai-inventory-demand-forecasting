import { useState, useEffect } from 'react'
import { api } from '../api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'

export default function Forecast() {
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
      <div className="page-title">Forecast</div>
      <div className="page-desc">ML demand predictions using XGBoost and Prophet.</div>

      <div className="card" style={{ marginBottom: 22 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr auto', gap: 14, alignItems: 'end' }}>
          <div className="form-group">
            <label className="form-label">Product</label>
            <select className="select" value={productId} onChange={e => setProductId(e.target.value)}>
              {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Days: {days}</label>
            <input type="range" min={7} max={30} value={days} onChange={e => setDays(+e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Engine</label>
            <div style={{ display: 'flex', gap: 5 }}>
              {['xgboost','prophet'].map(e => (
                <button key={e} className={`btn btn-sm ${engine===e?'btn-primary':'btn-ghost'}`} onClick={() => setEngine(e)}>
                  {e==='xgboost'?'XGBoost':'Prophet'}
                </button>
              ))}
            </div>
          </div>
          <button className="btn btn-primary" onClick={run} disabled={!productId || loading}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} />Running...</> : 'Generate'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}

      {!result && !loading && (
        <div className="empty-state">
          <div className="empty-state-icon">◎</div>
          <div className="empty-state-title">Select a product and run the forecast</div>
          <div className="empty-state-sub">XGBoost requires 30+ days · Prophet requires 14+ days of sales data</div>
        </div>
      )}

      {result && (
        <>
          <div className="sh2">{result.product_name} — {days}-day outlook ({result.engine})</div>
          <div className="card" style={{ padding: '14px 14px 8px', marginBottom: 20 }}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: '#444', fontSize: 10 }} tickLine={false} axisLine={false} interval="preserveStartEnd" />
                <YAxis tick={{ fill: '#444', fontSize: 10 }} tickLine={false} axisLine={false} width={28} />
                <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(124,110,240,0.3)', borderRadius: 8, fontSize: 12 }} />
                <Line type="monotone" dataKey="hist" name="Historical" stroke="rgba(255,255,255,0.18)" strokeWidth={2} dot={false} connectNulls={false} />
                <Line type="monotone" dataKey="fc" name="Forecast" stroke="#7c6ef0" strokeWidth={2.5} dot={{ fill: '#7c6ef0', r: 3 }} connectNulls={false} />
                <ReferenceLine x={today} stroke="rgba(248,113,113,0.3)" strokeDasharray="3 3" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="grid-3">
            {[
              { label: 'Total Projected', value: result.stats.total_projected.toLocaleString(), cls: 'purple' },
              { label: 'Average / Day', value: result.stats.average_per_day, cls: '' },
              { label: 'Peak Day', value: result.stats.peak_date, cls: '' },
            ].map(s => (
              <div key={s.label} className="card">
                <div className="card-label">{s.label}</div>
                <div className={`card-value ${s.cls}`} style={{ fontSize: 22 }}>{s.value}</div>
              </div>
            ))}
          </div>

          <div className="sh">Day-by-Day</div>
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <table>
              <thead><tr><th>Date</th><th>Projected Demand</th></tr></thead>
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
            Stock at least <strong>{result.stats.total_projected} units</strong> of {result.product_name} for {days}-day coverage.
          </div>
        </>
      )}
    </div>
  )
}
