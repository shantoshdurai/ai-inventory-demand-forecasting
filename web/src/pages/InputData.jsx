import { useState, useRef } from 'react'
import { api } from '../api'

function ParsedItems({ items, onSave, source }) {
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  if (!items?.length) return null
  const hasError = items[0]?.error
  if (hasError) return <div className="alert alert-error">{items[0].error}</div>

  const save = async () => {
    setSaving(true)
    const txns = items.map(it => ({
      product_name: it.item, qty: it.qty, type: it.type || 'sale',
      date: it.date || null, source, price: it.price || null
    }))
    await api.logBulk(txns)
    setSaving(false)
    setSaved(true)
  }

  return (
    <div style={{ marginTop: 16 }}>
      <div className="sh">Extracted — {items.length} item(s)</div>
      <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 14 }}>
        <table>
          <thead><tr><th>Item</th><th>Qty</th><th>Type</th><th>Date</th></tr></thead>
          <tbody>
            {items.map((it, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600 }}>{it.item}</td>
                <td style={{ fontFamily: 'var(--mono)' }}>{it.qty}</td>
                <td><span className={`badge badge-${it.type || 'sale'}`}>{it.type || 'sale'}</span></td>
                <td style={{ color: 'var(--text-3)' }}>{it.date || 'today'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {saved
        ? <div className="alert alert-success">✓ Saved {items.length} transactions to inventory.</div>
        : <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saving ? <><div className="spinner" style={{ width: 14, height: 14 }} /> Saving...</> : `Confirm & Save ${items.length} items`}
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
  const [importResult, setImportResult] = useState(null)
  const recognitionRef = useRef(null)
  const fileRef = useRef(null)
  const imgRef = useRef(null)

  const process = async (inputText, source) => {
    setLoading(true); setItems(null)
    try {
      const fn = source === 'voice' ? api.parseVoice : api.parseText
      const key = source === 'voice' ? 'transcribed_text' : 'text'
      const { items: parsed } = source === 'voice'
        ? await api.parseVoice(inputText)
        : await api.parseText(inputText)
      setItems(parsed)
    } catch (e) { setItems([{ error: e.message }]) }
    setLoading(false)
  }

  const startVoice = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { alert('Voice not supported. Use Chrome.'); return }
    const rec = new SR()
    rec.lang = 'en-IN'; rec.continuous = false; rec.interimResults = false
    rec.onstart = () => setListening(true)
    rec.onresult = (e) => {
      const t = e.results[0][0].transcript
      setText(t); setListening(false)
      process(t, 'voice')
    }
    rec.onerror = () => setListening(false)
    rec.onend = () => setListening(false)
    rec.start(); recognitionRef.current = rec
  }

  const handleImage = async (file) => {
    setLoading(true); setItems(null)
    try {
      const { items: parsed } = await api.parseImage(file)
      setItems(parsed)
    } catch (e) { setItems([{ error: e.message }]) }
    setLoading(false)
  }

  const handleImport = async (file) => {
    setLoading(true); setImportResult(null)
    try {
      const result = await api.importFile(file)
      setImportResult(result)
    } catch (e) { setImportResult({ success: false, error: e.message }) }
    setLoading(false)
  }

  return (
    <div className="page">
      <div className="page-title">Input Data</div>
      <div className="page-desc">Log inventory changes by voice, text, photo, or spreadsheet.</div>

      <div className="tabs">
        {[['voice', '🎙 Voice'], ['text', '✏ Text'], ['photo', '📷 Photo'], ['csv', '📄 Spreadsheet']].map(([id, label]) => (
          <button key={id} className={`tab${tab === id ? ' active' : ''}`} onClick={() => { setTab(id); setItems(null); setImportResult(null) }}>{label}</button>
        ))}
      </div>

      {/* Voice tab */}
      {tab === 'voice' && (
        <div>
          <div className="card" style={{ marginBottom: 20 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Speak your transactions in Hindi or English</div>
            <div style={{ fontSize: 13, color: 'var(--text-2)', lineHeight: 1.7 }}>
              Examples:<br />
              <span style={{ color: 'var(--purple)', fontStyle: 'italic' }}>"Aaj 10 packet Maggi becha aur 5 kg atta aaya"</span><br />
              <span style={{ color: 'var(--purple)', fontStyle: 'italic' }}>"Sold 20 Parle-G biscuits, restocked 100 Amul milk packets"</span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
            <button
              className={`voice-btn ${listening ? 'listening' : 'idle'}`}
              style={{ width: 56, height: 56, fontSize: 22 }}
              onClick={listening ? () => { recognitionRef.current?.stop(); setListening(false) } : startVoice}
            >
              {listening ? '◉' : '🎙'}
            </button>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>{listening ? 'Listening...' : 'Tap to speak'}</div>
              <div style={{ fontSize: 12, color: 'var(--text-3)' }}>{listening ? 'Speak clearly, then stop' : 'Voice input (Hindi/English)'}</div>
            </div>
          </div>

          {text && (
            <div style={{ marginBottom: 12 }}>
              <div className="sh">Transcribed</div>
              <div className="card" style={{ fontStyle: 'italic', color: 'var(--text-2)' }}>"{text}"</div>
            </div>
          )}

          {loading && <div className="loading-row"><div className="spinner" /><span>Parsing with Gemma AI...</span></div>}
          {items && <ParsedItems items={items} source="voice" />}
        </div>
      )}

      {/* Text tab */}
      {tab === 'text' && (
        <div>
          <div className="card" style={{ marginBottom: 20 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Type your transactions in plain language</div>
            <div style={{ fontSize: 13, color: 'var(--text-2)', fontStyle: 'italic', color: 'var(--purple)' }}>
              "Sold 5 strips of Dolo 650 and received 100 Crocin from distributor"
            </div>
          </div>
          <div className="form-group" style={{ marginBottom: 14 }}>
            <textarea className="textarea" rows={4} value={text} onChange={e => setText(e.target.value)}
              placeholder="e.g. Aaj 20 kg chawal becha, 50 liter tel aaya distributor se..." />
          </div>
          <button className="btn btn-primary" onClick={() => process(text, 'text')} disabled={!text.trim() || loading}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} /> Parsing...</> : 'Parse with AI'}
          </button>
          {items && <ParsedItems items={items} source="text" />}
        </div>
      )}

      {/* Photo tab */}
      {tab === 'photo' && (
        <div>
          <div
            className={`upload-zone${dragover ? ' dragover' : ''}`}
            style={{ marginBottom: 20 }}
            onClick={() => imgRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragover(true) }}
            onDragLeave={() => setDragover(false)}
            onDrop={e => { e.preventDefault(); setDragover(false); const f = e.dataTransfer.files[0]; if (f) handleImage(f) }}
          >
            <div className="upload-zone-icon">📷</div>
            <div className="upload-zone-text">Upload receipt, bill, or shelf photo</div>
            <div className="upload-zone-sub">Gemma 4 vision will extract all items automatically · JPG, PNG, WebP</div>
            <input ref={imgRef} type="file" accept="image/*" style={{ display: 'none' }}
              onChange={e => { const f = e.target.files[0]; if (f) handleImage(f) }} />
          </div>
          {loading && <div className="loading-row"><div className="spinner" /><span>Analyzing image with Gemma 4 vision...</span></div>}
          {items && <ParsedItems items={items} source="photo" />}
        </div>
      )}

      {/* CSV tab */}
      {tab === 'csv' && (
        <div>
          <div
            className={`upload-zone${dragover ? ' dragover' : ''}`}
            style={{ marginBottom: 20 }}
            onClick={() => fileRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragover(true) }}
            onDragLeave={() => setDragover(false)}
            onDrop={e => { e.preventDefault(); setDragover(false); const f = e.dataTransfer.files[0]; if (f) handleImport(f) }}
          >
            <div className="upload-zone-icon">📄</div>
            <div className="upload-zone-text">Upload CSV or Excel file</div>
            <div className="upload-zone-sub">Columns: item/product, qty/quantity, type (sale/restock), date · Auto-detected</div>
            <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls" style={{ display: 'none' }}
              onChange={e => { const f = e.target.files[0]; if (f) handleImport(f) }} />
          </div>
          {loading && <div className="loading-row"><div className="spinner" /><span>Importing file...</span></div>}
          {importResult && (
            importResult.success
              ? <div className="alert alert-success">✓ Imported {importResult.count} records successfully.</div>
              : <div className="alert alert-error">Import failed: {importResult.error}</div>
          )}
        </div>
      )}
    </div>
  )
}
