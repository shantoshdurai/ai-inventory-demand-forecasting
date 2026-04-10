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
    try {
      const data = await api.forecast({ product_id: parseInt(productId), days, engine })
      setResult(data)
    } catch (e) { setError(e.message) }
    setLoading(false)
  }

  const today = new Date().toISOString().slice(0, 10)

  const chartData = result ? [
    ...result.historical.slice(-60).map(h => ({ date: h.date?.slice(5), hist: h.qty, forecast: null })),
    ...result.forecast.map(f => ({ date: f.date?.slice(5), hist: null, forecast: f.predicted_qty }))
  ] : []

  return (
    <div className="page">
      <div className="page-title">Forecast</div>
      <div className="page-desc">ML-powered demand predictions using XGBoost and Prophet.</div>

      {/* Controls */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr auto', gap: 16, alignItems: 'end' }}>
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
            <div style={{ display: 'flex', gap: 6 }}>
              {['xgboost', 'prophet'].map(e => (
                <button key={e} className={`btn btn-sm ${engine === e ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setEngine(e)}>
                  {e === 'xgboost' ? 'XGBoost' : 'Prophet'}
                </button>
              ))}
            </div>
          </div>
          <button className="btn btn-primary" onClick={run} disabled={!productId || loading}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} /> Running...</> : 'Generate Forecast'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 20 }}>{error}</div>}

      {!result && !loading && (
        <div className="empty-state">
          <div className="empty-state-icon">◎</div>
          <div className="empty-state-title">Select a product and run forecast</div>
          <div className="empty-state-sub">XGBoost needs 30+ days · Prophet needs 14+ days of sales data</div>
        </div>
      )}

      {result && (
        <>
          <div className="sh2">{result.product_name} — {days}-day outlook via {result.engine}</div>

          <div className="card" style={{ padding: '20px 16px 12px', marginBottom: 24 }}>
            <ResponsiveContainer width="100%" height={340}>
              <LineChart data={chartData}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="date" tick={{ fill: '#555', fontSize: 10 }} tickLine={false} axisLine={false} interval="preserveStartEnd" />
                <YAxis tick={{ fill: '#555', fontSize: 10 }} tickLine={false} axisLine={false} width={28} />
                <Tooltip
                  contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(124,110,240,0.3)', borderRadius: 8, fontSize: 13 }}
                  labelStyle={{ color: '#999' }}
                  itemStyle={{ color: '#f0eff5' }}
                />
                <Line type="monotone" dataKey="hist" name="Historical" stroke="rgba(255,255,255,0.2)" strokeWidth={2} dot={false} connectNulls={false} />
                <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#7c6ef0" strokeWidth={3} dot={{ fill: '#7c6ef0', r: 3 }} connectNulls={false} />
                <ReferenceLine x={today.slice(5)} stroke="rgba(248,113,113,0.3)" strokeDasharray="4 4" label={{ value: 'today', fill: '#f87171', fontSize: 11 }} />
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
                <div className={`card-value ${s.cls}`} style={{ fontSize: 24 }}>{s.value}</div>
              </div>
            ))}
          </div>

          <div className="sh">Day-by-Day Breakdown</div>
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

          <div className="alert alert-info" style={{ marginTop: 16 }}>
            Ensure you have at least <strong>{result.stats.total_projected} units</strong> of {result.product_name} to cover {days} days.
          </div>
        </>
      )}
    </div>
  )
}
