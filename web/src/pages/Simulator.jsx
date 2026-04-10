import { useState, useEffect } from 'react'
import { api } from '../api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function Simulator({ t }) {
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
      <div className="page-title">{t.sim_title}</div>
      <div className="page-desc">{t.sim_desc}</div>

      <div className="grid-1-2">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div className="form-group">
            <label className="form-label">{t.sim_product}</label>
            <select className="select" value={productId} onChange={e => setProductId(e.target.value)}>
              {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          {sel && (
            <div className="card card-clay-purple">
              <div className="card-label">{t.sim_current_price}</div>
              <div className="card-value purple" style={{ fontSize: 22 }}>₹{sel.price}</div>
              <div style={{ height: 10 }} />
              <div className="card-label">{t.sim_stock}</div>
              <div className="card-value green" style={{ fontSize: 22 }}>{Math.round(sel.stock)}</div>
            </div>
          )}
          <div className="form-group">
            <label className="form-label">{t.sim_discount(discount, sel ? (sel.price*(1-discount/100)).toFixed(1) : null)}</label>
            <input type="range" min={0} max={50} step={5} value={discount} onChange={e => setDiscount(+e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">{t.sim_period(period)}</label>
            <input type="range" min={7} max={30} value={period} onChange={e => setPeriod(+e.target.value)} />
          </div>
          <button className="btn btn-primary btn-full" onClick={run} disabled={!productId || loading}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} />{t.sim_running}</> : t.sim_run}
          </button>
        </div>

        <div>
          {error && <div className="alert alert-error">{error}</div>}
          {!result && !loading && (
            <div className="empty-state" style={{ minHeight: 260 }}>
              <div className="empty-state-icon">⊘</div>
              <div className="empty-state-title">{t.sim_configure}</div>
              <div className="empty-state-sub">{t.sim_results_here}</div>
            </div>
          )}
          {result && (
            <>
              <div className="sh2">{result.product_name} · {discount}% — {period} {t.dash_col_date}</div>
              <div className="grid-2" style={{ marginBottom: 14 }}>
                {[
                  { label: t.sim_baseline_units, value: result.base_demand.toLocaleString(), sub: `@ ₹${result.current_price}`, cls: '', clay: '' },
                  { label: t.sim_simulated_units, value: result.simulated_demand.toLocaleString(), sub: t.sim_extra(result.delta_demand), cls: 'purple', clay: 'card-clay-purple' },
                  { label: t.sim_baseline_rev, value: `₹${result.base_revenue.toLocaleString('en-IN')}`, sub: '', cls: '', clay: '' },
                  { label: t.sim_simulated_rev, value: `₹${result.simulated_revenue.toLocaleString('en-IN')}`,
                    sub: `${result.delta_revenue >= 0 ? '▲' : '▼'} ₹${Math.abs(result.delta_revenue).toLocaleString('en-IN')}`,
                    cls: 'purple', clay: 'card-clay-purple',
                    subCls: result.delta_revenue >= 0 ? 'green' : 'red' },
                ].map(s => (
                  <div key={s.label} className={`card ${s.clay}`}>
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
                    <YAxis tick={{ fill: '#999', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ background: 'white', border: '1.5px solid rgba(99,102,241,0.15)', borderRadius: 12, fontSize: 12, boxShadow: '0 4px 16px rgba(99,102,241,0.12)' }} />
                    <Bar dataKey="v" radius={[6, 6, 0, 0]}>
                      <Cell fill="rgba(99,102,241,0.12)" /><Cell fill="#6366f1" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {result.stockout_risk?.has_risk
                ? <div className="alert alert-error">{t.sim_stockout(result.stockout_risk.days_until_stockout, result.stockout_risk.shortage_units)}</div>
                : <div className="alert alert-success">{t.sim_surplus(Math.round(result.current_stock - result.simulated_demand), period)}</div>
              }
            </>
          )}
        </div>
      </div>
    </div>
  )
}
