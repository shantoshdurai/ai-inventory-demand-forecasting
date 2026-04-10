import { useState, useRef } from 'react'
import { api } from '../api'

function ParsedTable({ items, t, onSave }) {
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
      <div className="sh">{t.input_extracted(items.length)}</div>
      <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 12 }}>
        <table>
          <thead><tr><th>{t.dash_col_item}</th><th>{t.dash_col_qty}</th><th>{t.dash_col_type}</th><th>{t.dash_col_date}</th></tr></thead>
          <tbody>
            {items.map((it, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600 }}>{it.item}</td>
                <td style={{ fontFamily: 'var(--mono)' }}>{it.qty}</td>
                <td><span className={`tbadge tbadge-${it.type || 'sale'}`}>{it.type || 'sale'}</span></td>
                <td style={{ color: 'var(--text3)' }}>{it.date || t.dash_col_date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {saved
        ? <div className="alert alert-success">{t.input_saved(items.length)}</div>
        : <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saving ? <><div className="spinner" style={{ width: 14, height: 14 }} />{t.input_saving}</> : t.input_save(items.length)}
          </button>
      }
    </div>
  )
}

export default function InputData({ t }) {
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

  const parseText = async (txt, src) => {
    if (!txt.trim()) return
    setLoading(true); setItems(null)
    try {
      const fn = src === 'voice' ? api.parseVoice : api.parseText
      const { items: parsed } = await fn(txt)
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
    rec.onresult = e => { const txt = e.results[0][0].transcript; setText(txt); setListening(false); parseText(txt, 'voice') }
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
      <div className="page-title">{t.input_title}</div>
      <div className="page-desc">{t.input_desc}</div>

      <div className="tabs">
        {[['voice', t.input_tab_voice], ['text', t.input_tab_text], ['photo', t.input_tab_photo], ['csv', t.input_tab_sheet]].map(([id, lbl]) => (
          <button key={id} className={`tab${tab===id?' active':''}`} onClick={() => { setTab(id); reset() }}>{lbl}</button>
        ))}
      </div>

      {/* VOICE */}
      {tab === 'voice' && (
        <div>
          <div className="card" style={{ marginBottom: 18 }}>
            <div style={{ fontWeight: 700, marginBottom: 6, fontSize: 14 }}>{t.input_voice_title}</div>
            <div style={{ fontSize: 13, color: 'var(--text2)', lineHeight: 1.8 }}>
              <span style={{ color: 'var(--purple)', fontStyle: 'italic' }}>{t.input_voice_ex1}</span><br />
              <span style={{ color: 'var(--purple)', fontStyle: 'italic' }}>{t.input_voice_ex2}</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 14, alignItems: 'center', marginBottom: 16 }}>
            <button
              onClick={listening ? () => { recRef.current?.stop(); setListening(false) } : startVoice}
              style={{
                width: 64, height: 64, borderRadius: '50%', border: 'none', fontSize: 26,
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                background: listening ? 'linear-gradient(135deg,#fca5a5,#f87171)' : 'linear-gradient(135deg,#ede9fe,#c4b5fd)',
                color: listening ? 'white' : 'var(--purple)',
                animation: listening ? 'vring 1.5s infinite' : 'none',
                boxShadow: listening ? '0 5px 0 rgba(220,38,38,0.25)' : '0 5px 0 rgba(99,102,241,0.2)',
              }}
            >🎙</button>
            <div>
              <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text)' }}>{listening ? t.input_voice_listening : t.input_voice_tap}</div>
              <div style={{ fontSize: 12, color: 'var(--text3)' }}>{listening ? t.input_voice_speak_clearly : t.input_voice_supported}</div>
            </div>
          </div>
          {text && <div className="card" style={{ fontStyle: 'italic', color: 'var(--text2)', fontSize: 13, marginBottom: 12 }}>"{text}"</div>}
          {loading && <div className="loading-row"><div className="spinner" /><span>{t.input_parsing}</span></div>}
          {items && <ParsedTable items={items} t={t} />}
        </div>
      )}

      {/* TEXT */}
      {tab === 'text' && (
        <div>
          <div className="form-group" style={{ marginBottom: 14 }}>
            <label className="form-label">{t.input_text_label}</label>
            <textarea className="textarea" rows={4} value={text} onChange={e => setText(e.target.value)}
              placeholder={t.input_text_placeholder} />
          </div>
          <button className="btn btn-primary" onClick={() => parseText(text, 'text')} disabled={!text.trim() || loading}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14 }} />{t.input_parsing}</> : t.input_parse_btn}
          </button>
          {items && <ParsedTable items={items} t={t} />}
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
            <div style={{ fontSize: 40, marginBottom: 8 }}>📷</div>
            <div style={{ fontWeight: 600, color: 'var(--text2)' }}>{t.input_photo_drop}</div>
            <div style={{ fontSize: 12, color: 'var(--text3)', marginTop: 4 }}>{t.input_photo_sub}</div>
            <input ref={imgRef} type="file" accept="image/*" style={{ display: 'none' }}
              onChange={e => { const f = e.target.files[0]; if (f) handleImage(f) }} />
          </div>
          {loading && <div className="loading-row"><div className="spinner" /><span>{t.input_analyzing}</span></div>}
          {items && <ParsedTable items={items} t={t} />}
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
            <div style={{ fontSize: 40, marginBottom: 8 }}>📄</div>
            <div style={{ fontWeight: 600, color: 'var(--text2)' }}>{t.input_sheet_drop}</div>
            <div style={{ fontSize: 12, color: 'var(--text3)', marginTop: 4 }}>{t.input_sheet_sub}</div>
            <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls" style={{ display: 'none' }}
              onChange={e => { const f = e.target.files[0]; if (f) handleImport(f) }} />
          </div>
          {loading && <div className="loading-row"><div className="spinner" /><span>{t.input_importing}</span></div>}
          {importRes && (importRes.success
            ? <div className="alert alert-success">{t.input_imported(importRes.count)}</div>
            : <div className="alert alert-error">{importRes.error}</div>
          )}
        </div>
      )}
    </div>
  )
}
