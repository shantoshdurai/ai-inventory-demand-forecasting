import { useState, useEffect } from 'react'
import { api } from '../api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function Simulator() {
  const [products, setProducts] = useState([])
  const [productId, setProductId] = useState('')
  const [discount, setDiscount] = useState(10)
  const [period, setPeriod] = useState(14)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.products().then(p => { setProducts(p); if (p.length) setProductId(String(p[0].id)) })
  }, [])

  const run = async () => {
    setLoading(true); setError(null); setResult(null)
    try {
      const data = await api.simulate({ product_id: parseInt(productId), discount_percent: discount, period_days: period })
      setResult(data)
    } catch (e) { setError(e.message) }
    setLoading(false)
  }

  const sel = products.find(p => String(p.id) === productId)

  return (
    <div className="page">
      <div className="page-title">What-If Simulator</div>
      <div className="page-desc">See how price discounts affect demand and revenue before committing.</div>

      <div className="grid-1-2">
        {/* Left config */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="form-group">
            <label className="form-label">Product</label>
            <select className="select" value={productId} onChange={e => setProductId(e.target.value)}>
              {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>

          {sel && (
            <div className="card">
              <div className="card-label">Current Price</div>
              <div className="card-value purple" style={{ fontSize: 24 }}>₹{sel.price}</div>
              <div style={{ height: 12 }} />
              <div className="card-label">Stock on Hand</div>
              <div className="card-value green" style={{ fontSize: 24 }}>{Math.round(sel.stock)}</div>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Discount: {discount}%</label>
            <input type="range" min={0} max={50} step={5} value={discount} onChange={e => setDiscount(+e.target.value)} />
            {sel && <div style={{ fontSize: 12, color: 'var(--text-2)', marginTop: 4 }}>New price: ₹{(sel.price * (1 - discount/100)).toFixed(2)}</div>}
          </div>

          <div className="form-group">
            <label className="form-label">Period: {period} days</label>
            <input type="range" min={7} max={30} value={period} onChange={e => setPeriod(+e.target.value)} />
          </div>

          <button className="btn btn-primary btn-full" onClick={run} disabled={!productId || loading}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} /> Computing...</> : 'Run Simulation'}
          </button>
        </div>

        {/* Right results */}
        <div>
          {error && <div className="alert alert-error">{error}</div>}

          {!result && !loading && (
            <div className="empty-state" style={{ height: '100%', minHeight: 300 }}>
              <div className="empty-state-icon">⊘</div>
              <div className="empty-state-title">Configure and run a simulation</div>
              <div className="empty-state-sub">Results will appear here</div>
            </div>
          )}

          {result && (
            <div>
              <div className="sh2">{result.product_name} — {discount}% discount for {period} days</div>

              <div className="grid-2" style={{ marginBottom: 16 }}>
                <div className="card">
                  <div className="card-label">Baseline Units</div>
                  <div className="card-value">{result.base_demand.toLocaleString()}</div>
                  <div className="card-sub">at ₹{result.current_price}</div>
                </div>
                <div className="card">
                  <div className="card-label">Simulated Units</div>
                  <div className="card-value purple">{result.simulated_demand.toLocaleString()}</div>
                  <div className="card-sub" style={{ color: 'var(--green)' }}>+{result.delta_demand} units</div>
                </div>
                <div className="card">
                  <div className="card-label">Baseline Revenue</div>
                  <div className="card-value" style={{ fontSize: 22 }}>₹{result.base_revenue.toLocaleString('en-IN')}</div>
                </div>
                <div className="card">
                  <div className="card-label">Simulated Revenue</div>
                  <div className="card-value purple" style={{ fontSize: 22 }}>₹{result.simulated_revenue.toLocaleString('en-IN')}</div>
                  <div className="card-sub" style={{ color: result.delta_revenue >= 0 ? 'var(--green)' : 'var(--red)' }}>
                    {result.delta_revenue >= 0 ? '▲' : '▼'} ₹{Math.abs(result.delta_revenue).toLocaleString('en-IN')}
                  </div>
                </div>
              </div>

              <div className="card" style={{ padding: '16px 16px 8px', marginBottom: 16 }}>
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart data={[
                    { name: 'Baseline', value: result.base_demand },
                    { name: `${discount}% Off`, value: result.simulated_demand }
                  ]} barSize={60}>
                    <XAxis dataKey="name" tick={{ fill: '#999', fontSize: 13 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#555', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(124,110,240,0.3)', borderRadius: 8, fontSize: 13 }} />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                      <Cell fill="rgba(255,255,255,0.1)" />
                      <Cell fill="#7c6ef0" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {result.stockout_risk?.has_risk
                ? <div className="alert alert-error">⚠ Stockout in ~{result.stockout_risk.days_until_stockout} days. Need {result.stockout_risk.shortage_units} more units for the full promotion period.</div>
                : <div className="alert alert-success">✓ Stock sufficient. Surplus of {Math.round(result.current_stock - result.simulated_demand)} units after {period} days.</div>
              }
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
