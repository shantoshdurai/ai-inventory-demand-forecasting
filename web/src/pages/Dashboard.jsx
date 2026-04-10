import { useState, useEffect } from 'react'
import { api } from '../api'
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'

const TT = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: 'white', border: '1.5px solid rgba(99,102,241,0.15)', borderRadius: 12, padding: '8px 14px', fontSize: 12, boxShadow: '0 4px 16px rgba(99,102,241,0.12)' }}>
      <div style={{ color: '#888', marginBottom: 2 }}>{label}</div>
      <div style={{ color: '#1e1b4b', fontWeight: 700 }}>{payload[0]?.value}</div>
    </div>
  )
}

const SEV = { critical: 'var(--red)', warning: 'var(--amber)', info: 'var(--purple)' }
const ICON = { critical: '⚠', warning: '●', info: '↗' }

export default function Dashboard({ t }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState(null)

  const load = () => {
    setLoading(true); setErr(null)
    api.dashboard()
      .then(d => { setData(d); setLoading(false) })
      .catch(e => { setErr(e.message); setLoading(false) })
  }

  useEffect(() => { load() }, [])

  if (loading) return (
    <div className="page">
      <div className="loading-row" style={{ marginTop: 60, justifyContent: 'center' }}>
        <div className="spinner" />
        <span>{t.dash_loading}</span>
      </div>
    </div>
  )

  if (err) return (
    <div className="page">
      <div className="alert alert-error" style={{ marginTop: 20 }}>
        ⚠ {err}
        <button className="btn btn-ghost btn-sm" style={{ marginLeft: 12 }} onClick={load}>{t.dash_refresh}</button>
      </div>
    </div>
  )

  if (!data) return null

  const { stats, insights, sales_trend, recent_transactions, stock_levels } = data

  return (
    <div className="page">
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 4 }}>
        <div className="page-title">{t.dash_title}</div>
        <button className="btn btn-ghost btn-sm" onClick={load}>{t.dash_refresh}</button>
      </div>
      <div className="page-desc">{t.dash_desc}</div>

      {/* Stats */}
      <div className="grid-4">
        {[
          { label: t.dash_stat_products, value: stats.total_items, cls: '', clay: '' },
          { label: t.dash_stat_lowstock, value: stats.low_stock_alerts, cls: 'amber', clay: 'card-clay-amber' },
          { label: t.dash_stat_value, value: `₹${Math.round(stats.inventory_value).toLocaleString('en-IN')}`, cls: 'purple', clay: 'card-clay-purple' },
          { label: t.dash_stat_units, value: Math.round(stats.total_units).toLocaleString(), cls: '', clay: 'card-clay-blue' },
        ].map(s => (
          <div key={s.label} className={`card ${s.clay}`}>
            <div className="card-label">{s.label}</div>
            <div className={`card-value ${s.cls}`}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* AI Insights */}
      {insights?.length > 0 && (
        <>
          <div className="sh">{t.dash_insights}</div>
          <div className="grid-3" style={{ marginBottom: 24 }}>
            {insights.slice(0, 3).map((ins, i) => (
              <div key={i} className={`insight-card ${ins.severity}`}>
                <div>
                  <div className="insight-title">
                    <span style={{ color: SEV[ins.severity] }}>{ICON[ins.severity]}</span>
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

      {/* Chart + Recent */}
      <div className="grid-2">
        <div className="card" style={{ padding: '16px 16px 10px' }}>
          <div className="sh">{t.dash_sales_trend}</div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={sales_trend}>
              <CartesianGrid stroke="rgba(99,102,241,0.07)" vertical={false} />
              <XAxis dataKey="date" tick={{ fill: '#999', fontSize: 10 }} tickLine={false} axisLine={false}
                tickFormatter={v => v?.slice(5)} interval="preserveStartEnd" />
              <YAxis tick={{ fill: '#999', fontSize: 10 }} tickLine={false} axisLine={false} width={32} />
              <Tooltip content={<TT />} />
              <Line type="monotone" dataKey="sales" stroke="#6366f1" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="sh">{t.dash_recent}</div>
          <table style={{ width: '100%', fontSize: 12.5 }}>
            <thead>
              <tr>
                <th>{t.dash_col_item}</th>
                <th>{t.dash_col_qty}</th>
                <th>{t.dash_col_type}</th>
                <th>{t.dash_col_date}</th>
              </tr>
            </thead>
            <tbody>
              {recent_transactions?.slice(0, 8).map((tx, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{tx.item}</td>
                  <td style={{ fontFamily: 'var(--mono)' }}>{tx.qty}</td>
                  <td><span className={`tbadge tbadge-${tx.type}`}>{tx.type}</span></td>
                  <td style={{ color: 'var(--text3)', fontSize: 11 }}>{tx.date?.slice(5)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Stock bar chart */}
      <div className="card" style={{ padding: '16px 16px 10px', marginBottom: 24 }}>
        <div className="sh">{t.dash_stock_levels}</div>
        <ResponsiveContainer width="100%" height={Math.max((stock_levels?.length || 0) * 28, 160)}>
          <BarChart data={stock_levels} layout="vertical" margin={{ left: 0, right: 40 }}>
            <XAxis type="number" tick={{ fill: '#999', fontSize: 10 }} tickLine={false} axisLine={false} />
            <YAxis type="category" dataKey="item" width={130} tick={{ fill: '#666', fontSize: 11 }} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ background: 'white', border: '1.5px solid rgba(99,102,241,0.15)', borderRadius: 12, fontSize: 12, boxShadow: '0 4px 16px rgba(99,102,241,0.12)' }}
              formatter={(v, _, p) => [`${v} ${t.forecast_units} · ${p.payload.status}`, p.payload.item]}
              labelFormatter={() => ''}
            />
            <Bar dataKey="stock" radius={[0, 6, 6, 0]}
              fill="#6366f1"
              background={{ fill: 'rgba(99,102,241,0.06)', radius: [0, 6, 6, 0] }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Full product table */}
      <div className="sh">{t.dash_all_products}</div>
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t.dash_col_product}</th>
                <th>{t.dash_col_category}</th>
                <th>{t.dash_col_price}</th>
                <th>{t.dash_col_stock}</th>
                <th>{t.dash_col_status}</th>
              </tr>
            </thead>
            <tbody>
              {[...(stock_levels || [])].reverse().map((p, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600 }}>{p.item}</td>
                  <td style={{ color: 'var(--text2)' }}>{p.category}</td>
                  <td style={{ fontFamily: 'var(--mono)' }}>₹{p.price}</td>
                  <td style={{ fontFamily: 'var(--mono)', fontWeight: 600 }}>{Math.round(p.stock)}</td>
                  <td><span className={`tbadge tbadge-${p.status}`}>{p.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
