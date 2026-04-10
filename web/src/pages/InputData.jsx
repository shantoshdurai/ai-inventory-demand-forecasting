import { useState, useRef } from 'react'
import { api } from '../api'

function ParsedTable({ items, onSave }) {
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  if (!items?.length) return null
  if (items[0]?.error) return <div className="alert alert-error" style={{ marginTop: 14 }}>{items[0].error}</div>

  const save = async () => {
    setSaving(true)
    await api.logBulk(items.map(it => ({
      product_name: it.item, qty: it.qty,
      type: it.type || 'sale', date: it.date || null, source: 'input'
    })))
    setSaving(false); setSaved(true)
    onSave?.()
  }

  return (
    <div style={{ marginTop: 16 }}>
      <div className="sh">{items.length} item(s) extracted</div>
      <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 12 }}>
        <table>
          <thead><tr><th>Item</th><th>Qty</th><th>Type</th><th>Date</th></tr></thead>
          <tbody>
            {items.map((it, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600 }}>{it.item}</td>
                <td style={{ fontFamily: 'var(--mono)' }}>{it.qty}</td>
                <td><span className={`tbadge tbadge-${it.type || 'sale'}`}>{it.type || 'sale'}</span></td>
                <td style={{ color: 'var(--text3)' }}>{it.date || 'today'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {saved
        ? <div className="alert alert-success">✓ Saved {items.length} transactions.</div>
        : <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saving ? <><div className="spinner" style={{ width: 14, height: 14 }} /> Saving...</> : `Save ${items.length} items to inventory`}
          </button>
      }
    </div>
  )
}

export default function InputData() {
  const [tab, setTab] = useState('voice')
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [items, setItems] = useState(null)
  const [listening, setListening] = useState(false)
  const [dragover, setDragover] = useState(false)
  const [importRes, setImportRes] = useState(null)
  const recRef = useRef(null)
  const fileRef = useRef(null)
  const imgRef = useRef(null)

  const reset = () => { setItems(null); setImportRes(null) }

  const parseText = async (t, src) => {
    if (!t.trim()) return
    setLoading(true); setItems(null)
    try {
      const fn = src === 'voice' ? api.parseVoice : api.parseText
      const { items: parsed } = await fn(t)
      setItems(parsed)
    } catch (e) { setItems([{ error: e.message }]) }
    setLoading(false)
  }

  const startVoice = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { alert('Use Chrome for voice support.'); return }
    const rec = new SR()
    rec.lang = 'en-IN'; rec.continuous = false; rec.interimResults = false
    rec.onstart = () => setListening(true)
    rec.onresult = e => { const t = e.results[0][0].transcript; setText(t); setListening(false); parseText(t, 'voice') }
    rec.onerror = () => setListening(false)
    rec.onend = () => setListening(false)
    rec.start(); recRef.current = rec
  }

  const handleImage = async (file) => {
    setLoading(true); setItems(null)
    try { const { items: p } = await api.parseImage(file); setItems(p) }
    catch (e) { setItems([{ error: e.message }]) }
    setLoading(false)
  }

  const handleImport = async (file) => {
    setLoading(true); setImportRes(null)
    try { setImportRes(await api.importFile(file)) }
    catch (e) { setImportRes({ success: false, error: e.message }) }
    setLoading(false)
  }

  return (
    <div className="page">
      <div className="page-title">Input Data</div>
      <div className="page-desc">Log inventory by speaking, typing, photographing a bill, or uploading a spreadsheet.</div>

      <div className="tabs">
        {[['voice','🎙 Voice'],['text','✏ Text'],['photo','📷 Photo'],['csv','📄 Spreadsheet']].map(([id, lbl]) => (
          <button key={id} className={`tab${tab===id?' active':''}`} onClick={() => { setTab(id); reset() }}>{lbl}</button>
        ))}
      </div>

      {/* VOICE */}
      {tab === 'voice' && (
        <div>
          <div className="card" style={{ marginBottom: 18 }}>
            <div style={{ fontWeight: 600, marginBottom: 6, fontSize: 14 }}>Speak your transactions in Hindi or English</div>
            <div style={{ fontSize: 13, color: 'var(--text2)', lineHeight: 1.8 }}>
              <span style={{ color: 'var(--purple)', fontStyle: 'italic' }}>"Aaj 10 packet Maggi becha aur 5 kg atta aaya"</span><br />
              <span style={{ color: 'var(--purple)', fontStyle: 'italic' }}>"Sold 20 Parle-G, restocked 100 Amul milk"</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 14, alignItems: 'center', marginBottom: 16 }}>
            <button
              onClick={listening ? () => { recRef.current?.stop(); setListening(false) } : startVoice}
              style={{ width: 60, height: 60, borderRadius: '50%', border: 'none', fontSize: 24, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                background: listening ? 'rgba(248,113,113,0.15)' : 'rgba(124,110,240,0.15)',
                color: listening ? 'var(--red)' : 'var(--purple)',
                animation: listening ? 'vring 1.5s infinite' : 'none',
                boxShadow: listening ? '0 0 0 0 rgba(248,113,113,0.3)' : 'none'
              }}
            >🎙</button>
            <div>
              <div style={{ fontWeight: 700, fontSize: 14 }}>{listening ? '● Listening...' : 'Tap to speak'}</div>
              <div style={{ fontSize: 12, color: 'var(--text3)' }}>{listening ? 'Speak clearly, then stop' : 'Hindi / English supported'}</div>
            </div>
          </div>
          {text && <div className="card" style={{ fontStyle: 'italic', color: 'var(--text2)', fontSize: 13, marginBottom: 12 }}>"{text}"</div>}
          {loading && <div className="loading-row"><div className="spinner" /><span>Parsing with Gemma AI...</span></div>}
          {items && <ParsedTable items={items} />}
        </div>
      )}

      {/* TEXT */}
      {tab === 'text' && (
        <div>
          <div className="form-group" style={{ marginBottom: 14 }}>
            <label className="form-label">Type in plain language (English or Hindi)</label>
            <textarea className="textarea" rows={4} value={text} onChange={e => setText(e.target.value)}
              placeholder="e.g. 20 kg chawal becha, 50 liter tel aaya distributor se, sold 5 soap bars..." />
          </div>
          <button className="btn btn-primary" onClick={() => parseText(text, 'text')} disabled={!text.trim() || loading}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} />Parsing...</> : 'Parse with Gemma AI'}
          </button>
          {items && <ParsedTable items={items} />}
        </div>
      )}

      {/* PHOTO */}
      {tab === 'photo' && (
        <div>
          <div
            className={`upload-zone${dragover ? ' dragover' : ''}`}
            style={{ marginBottom: 18 }}
            onClick={() => imgRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragover(true) }}
            onDragLeave={() => setDragover(false)}
            onDrop={e => { e.preventDefault(); setDragover(false); const f = e.dataTransfer.files[0]; if (f) handleImage(f) }}
          >
            <div style={{ fontSize: 36, marginBottom: 8 }}>📷</div>
            <div style={{ fontWeight: 500, color: 'var(--text2)' }}>Upload receipt, bill, or shelf photo</div>
            <div style={{ fontSize: 12, color: 'var(--text3)', marginTop: 4 }}>Gemma 4 vision extracts all items · JPG, PNG, WebP</div>
            <input ref={imgRef} type="file" accept="image/*" style={{ display: 'none' }}
              onChange={e => { const f = e.target.files[0]; if (f) handleImage(f) }} />
          </div>
          {loading && <div className="loading-row"><div className="spinner" /><span>Analyzing with Gemma 4 vision...</span></div>}
          {items && <ParsedTable items={items} />}
        </div>
      )}

      {/* CSV */}
      {tab === 'csv' && (
        <div>
          <div
            className={`upload-zone${dragover ? ' dragover' : ''}`}
            style={{ marginBottom: 18 }}
            onClick={() => fileRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragover(true) }}
            onDragLeave={() => setDragover(false)}
            onDrop={e => { e.preventDefault(); setDragover(false); const f = e.dataTransfer.files[0]; if (f) handleImport(f) }}
          >
            <div style={{ fontSize: 36, marginBottom: 8 }}>📄</div>
            <div style={{ fontWeight: 500, color: 'var(--text2)' }}>Upload CSV or Excel</div>
            <div style={{ fontSize: 12, color: 'var(--text3)', marginTop: 4 }}>Columns: item, qty, type (sale/restock), date · Auto-detected</div>
            <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls" style={{ display: 'none' }}
              onChange={e => { const f = e.target.files[0]; if (f) handleImport(f) }} />
          </div>
          {loading && <div className="loading-row"><div className="spinner" /><span>Importing...</span></div>}
          {importRes && (importRes.success
            ? <div className="alert alert-success">✓ Imported {importRes.count} records.</div>
            : <div className="alert alert-error">Failed: {importRes.error}</div>
          )}
        </div>
      )}
    </div>
  )
}
