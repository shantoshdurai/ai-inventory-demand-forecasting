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
    try { setResult(await api.simulate({ product_id: parseInt(productId), discount_percent: discount, period_days: period })) }
    catch (e) { setError(e.message) }
    setLoading(false)
  }

  const sel = products.find(p => String(p.id) === productId)

  return (
    <div className="page">
      <div className="page-title">What-If Simulator</div>
      <div className="page-desc">Simulate price discounts and see the impact on demand and revenue.</div>

      <div className="grid-1-2">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div className="form-group">
            <label className="form-label">Product</label>
            <select className="select" value={productId} onChange={e => setProductId(e.target.value)}>
              {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          {sel && (
            <div className="card">
              <div className="card-label">Current Price</div>
              <div className="card-value purple" style={{ fontSize: 22 }}>₹{sel.price}</div>
              <div style={{ height: 10 }} />
              <div className="card-label">Stock on Hand</div>
              <div className="card-value green" style={{ fontSize: 22 }}>{Math.round(sel.stock)}</div>
            </div>
          )}
          <div className="form-group">
            <label className="form-label">Discount: {discount}%{sel ? ` → ₹${(sel.price*(1-discount/100)).toFixed(1)}` : ''}</label>
            <input type="range" min={0} max={50} step={5} value={discount} onChange={e => setDiscount(+e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Period: {period} days</label>
            <input type="range" min={7} max={30} value={period} onChange={e => setPeriod(+e.target.value)} />
          </div>
          <button className="btn btn-primary btn-full" onClick={run} disabled={!productId || loading}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} />Computing...</> : 'Run Simulation'}
          </button>
        </div>

        <div>
          {error && <div className="alert alert-error">{error}</div>}
          {!result && !loading && (
            <div className="empty-state" style={{ minHeight: 260 }}>
              <div className="empty-state-icon">⊘</div>
              <div className="empty-state-title">Configure and run a simulation</div>
              <div className="empty-state-sub">Results appear here</div>
            </div>
          )}
          {result && (
            <>
              <div className="sh2">{result.product_name} · {discount}% off for {period} days</div>
              <div className="grid-2" style={{ marginBottom: 14 }}>
                {[
                  { label: 'Baseline Units', value: result.base_demand.toLocaleString(), sub: `@ ₹${result.current_price}`, cls: '' },
                  { label: 'Simulated Units', value: result.simulated_demand.toLocaleString(), sub: `+${result.delta_demand} extra`, cls: 'purple' },
                  { label: 'Baseline Revenue', value: `₹${result.base_revenue.toLocaleString('en-IN')}`, sub: '', cls: '' },
                  { label: 'Simulated Revenue', value: `₹${result.simulated_revenue.toLocaleString('en-IN')}`,
                    sub: `${result.delta_revenue >= 0 ? '▲' : '▼'} ₹${Math.abs(result.delta_revenue).toLocaleString('en-IN')}`,
                    cls: 'purple', subCls: result.delta_revenue >= 0 ? 'green' : 'red' },
                ].map(s => (
                  <div key={s.label} className="card">
                    <div className="card-label">{s.label}</div>
                    <div className={`card-value ${s.cls}`} style={{ fontSize: 20 }}>{s.value}</div>
                    {s.sub && <div className="card-sub" style={s.subCls ? { color: `var(--${s.subCls})` } : {}}>{s.sub}</div>}
                  </div>
                ))}
              </div>
              <div className="card" style={{ padding: '14px 14px 8px', marginBottom: 14 }}>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={[
                    { name: 'Baseline', v: result.base_demand },
                    { name: `${discount}% Off`, v: result.simulated_demand }
                  ]} barSize={55}>
                    <XAxis dataKey="name" tick={{ fill: '#999', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#444', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(124,110,240,0.3)', borderRadius: 8, fontSize: 12 }} />
                    <Bar dataKey="v" radius={[5, 5, 0, 0]}>
                      <Cell fill="rgba(255,255,255,0.08)" /><Cell fill="#7c6ef0" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {result.stockout_risk?.has_risk
                ? <div className="alert alert-error">⚠ Stockout in ~{result.stockout_risk.days_until_stockout} days. Need {result.stockout_risk.shortage_units} more units.</div>
                : <div className="alert alert-success">✓ Stock sufficient — {Math.round(result.current_stock - result.simulated_demand)} units surplus after {period} days.</div>
              }
            </>
          )}
        </div>
      </div>
    </div>
  )
}
