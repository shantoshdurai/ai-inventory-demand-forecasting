import { useState, useEffect } from 'react'
import { api } from '../api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#1a1a2e', border: '1px solid rgba(124,110,240,0.3)', borderRadius: 8, padding: '8px 14px', fontSize: 13 }}>
      <div style={{ color: '#999', marginBottom: 4 }}>{label}</div>
      <div style={{ color: '#f0eff5', fontWeight: 700 }}>{payload[0]?.value} units</div>
    </div>
  )
}

const SEVERITY_ICON = { critical: '⚠', warning: '●', info: '↗' }

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.dashboard().then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  if (loading) return (
    <div className="page"><div className="loading-row" style={{ marginTop: 60 }}><div className="spinner" /><span>Loading dashboard...</span></div></div>
  )

  if (!data) return (
    <div className="page">
      <div className="alert alert-error">Could not connect to server. Make sure the API is running on port 8000.</div>
    </div>
  )

  const { stats, insights, sales_trend, recent_transactions, stock_levels } = data

  return (
    <div className="page">
      <div className="page-title">Dashboard</div>
      <div className="page-desc">Live overview of your Kirana shop inventory and performance.</div>

      {/* Stats */}
      <div className="grid-4">
        {[
          { label: 'Products', value: stats.total_items, cls: '' },
          { label: 'Low Stock Alerts', value: stats.low_stock_alerts, cls: 'amber' },
          { label: 'Inventory Value', value: `₹${stats.inventory_value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`, cls: 'purple' },
          { label: 'Total Units', value: stats.total_units.toLocaleString(), cls: '' },
        ].map(s => (
          <div key={s.label} className="card">
            <div className="card-label">{s.label}</div>
            <div className={`card-value ${s.cls}`}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* AI Insights */}
      {insights?.length > 0 && (
        <>
          <div className="sh">AI Insights</div>
          <div className="grid-3" style={{ marginBottom: 28 }}>
            {insights.slice(0, 3).map((ins, i) => (
              <div key={i} className={`insight-card ${ins.severity}`}>
                <div>
                  <div className="insight-title">
                    <span style={{ color: ins.severity === 'critical' ? 'var(--red)' : ins.severity === 'warning' ? 'var(--amber)' : 'var(--purple)' }}>
                      {SEVERITY_ICON[ins.severity] || '●'}
                    </span>
                    {ins.title}
                  </div>
                  <div className="insight-detail">{ins.detail}</div>
                </div>
                <div className="insight-metric">{ins.metric}</div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Charts row */}
      <div className="grid-2">
        <div className="card" style={{ padding: '20px 20px 12px' }}>
          <div className="sh">Sales Trend · 60 Days</div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={sales_trend}>
              <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="date" tick={{ fill: '#666', fontSize: 10 }} tickLine={false} axisLine={false}
                tickFormatter={v => v?.slice(5)} interval="preserveStartEnd" />
              <YAxis tick={{ fill: '#666', fontSize: 10 }} tickLine={false} axisLine={false} width={30} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="sales" stroke="#7c6ef0" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="sh">Recent Transactions</div>
          <table style={{ width: '100%', fontSize: 13 }}>
            <thead>
              <tr>
                <th>Item</th><th>Qty</th><th>Type</th><th>Date</th>
              </tr>
            </thead>
            <tbody>
              {recent_transactions?.slice(0, 8).map((t, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{t.item}</td>
                  <td style={{ fontFamily: 'var(--mono)' }}>{t.qty}</td>
                  <td><span className={`badge badge-${t.type}`}>{t.type}</span></td>
                  <td style={{ color: 'var(--text-3)', fontSize: 12 }}>{t.date?.slice(5)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Stock levels */}
      <div className="card" style={{ padding: '20px 20px 12px', marginBottom: 28 }}>
        <div className="sh">Stock Levels by Product</div>
        <ResponsiveContainer width="100%" height={Math.max(stock_levels.length * 32, 200)}>
          <BarChart data={stock_levels} layout="vertical" margin={{ left: 10, right: 50 }}>
            <XAxis type="number" tick={{ fill: '#555', fontSize: 10 }} tickLine={false} axisLine={false} />
            <YAxis type="category" dataKey="item" width={130} tick={{ fill: '#ccc', fontSize: 12 }} tickLine={false} axisLine={false} />
            <Tooltip content={({ active, payload }) => active && payload?.length
              ? <div style={{ background: '#1a1a2e', border: '1px solid rgba(124,110,240,0.3)', borderRadius: 8, padding: '8px 14px', fontSize: 13 }}>
                  <strong style={{ color: '#f0eff5' }}>{payload[0].payload.item}</strong>
                  <div style={{ color: '#7c6ef0' }}>{payload[0].value} units</div>
                  <div style={{ color: '#999', fontSize: 11, marginTop: 2 }}>{payload[0].payload.status}</div>
                </div>
              : null}
            />
            <Bar dataKey="stock" radius={[0, 5, 5, 0]}
              fill="#7c6ef0"
              cell={(entry) => {
                const c = entry.status === 'critical' ? '#f87171' : entry.status === 'low' ? '#fbbf24' : '#7c6ef0'
                return <rect fill={c} />
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Product table */}
      <div className="sh">All Products</div>
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Product</th><th>Category</th><th>Price</th><th>Stock</th><th>Status</th></tr>
            </thead>
            <tbody>
              {stock_levels?.slice().reverse().map((p, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{p.item}</td>
                  <td style={{ color: 'var(--text-2)' }}>{p.category}</td>
                  <td style={{ fontFamily: 'var(--mono)' }}>₹{p.price}</td>
                  <td style={{ fontFamily: 'var(--mono)', fontWeight: 600 }}>{Math.round(p.stock)}</td>
                  <td><span className={`badge badge-${p.status}`}>{p.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 16 }}>
        <button className="btn btn-ghost btn-sm" onClick={load}>↻ Refresh</button>
      </div>
    </div>
  )
}
