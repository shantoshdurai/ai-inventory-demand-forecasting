import { useState, useRef, useEffect } from 'react'
import { api } from '../api'

const LANGUAGES = [
  { code: 'English', label: 'English' },
  { code: 'Tamil',   label: 'தமிழ்' },
  { code: 'Hindi',   label: 'हिंदी' },
]

function renderMd(text) {
  if (!text) return null
  return text.split('\n').map((line, i) => {
    if (!line.trim()) return <div key={i} style={{ height: 5 }} />
    if (line.startsWith('### ')) return <div key={i} style={{ fontWeight: 700, color: 'var(--text)', fontSize: 13, marginTop: 8, marginBottom: 2 }}>{line.slice(4)}</div>
    if (line.startsWith('## '))  return <div key={i} style={{ fontWeight: 700, color: 'var(--text)', fontSize: 13.5, marginTop: 10, marginBottom: 3 }}>{line.slice(3)}</div>
    if (line.startsWith('**') && line.endsWith('**')) return <div key={i} style={{ fontWeight: 700, color: 'var(--purple)', marginTop: 6 }}>{line.slice(2, -2)}</div>
    if (line.match(/^[-*] /)) return (
      <div key={i} style={{ display: 'flex', gap: 6, marginBottom: 2 }}>
        <span style={{ color: 'var(--purple)', flexShrink: 0 }}>•</span>
        <span dangerouslySetInnerHTML={{ __html: bold(line.slice(2)) }} />
      </div>
    )
    if (line.match(/^\d+\. /)) return (
      <div key={i} style={{ marginBottom: 2 }} dangerouslySetInnerHTML={{ __html: bold(line) }} />
    )
    return <div key={i} style={{ marginBottom: 3 }} dangerouslySetInnerHTML={{ __html: bold(line) }} />
  })
}

function bold(s) {
  return s.replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--purple)">$1</strong>')
}

export default function SidePanel({ open, onClose, t }) {
  const [language, setLanguage] = useState('English')
  const [msgs, setMsgs] = useState([{ role: 'ai', content: null }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [listening, setListening] = useState(false)
  const [imgFile, setImgFile] = useState(null)
  const [imgPreview, setImgPreview] = useState(null)
  const bottomRef = useRef(null)
  const recRef = useRef(null)
  const fileRef = useRef(null)
  const inputRef = useRef(null)

  // Update welcome message when t (ui language) changes
  useEffect(() => {
    setMsgs([{ role: 'ai', content: t.panel_welcome }])
  }, [t.panel_welcome])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [msgs, loading])

  const handleLanguageChange = (lang) => {
    setLanguage(lang)
    setMsgs([{ role: 'ai', content: t.panel_welcome }])
  }

  const send = async (text, image) => {
    const txt = (text || '').trim()
    if (!txt && !image) return
    setLoading(true)

    const userMsg = { role: 'user', content: txt || t.panel_img_attached, img: imgPreview }
    setMsgs(m => [...m, userMsg])
    setInput('')
    setImgFile(null)
    setImgPreview(null)

    try {
      let response
      if (image) {
        const { items } = await api.parseImage(image)
        if (items?.[0]?.error) {
          response = t.panel_img_error(items[0].error)
        } else if (items?.length) {
          const summary = items.map(it => `• ${it.item}: ${it.qty} (${it.type})`).join('\n')
          response = `${t.panel_img_found(items.length)}\n\n${summary}\n\n${t.panel_img_ask}`
          setMsgs(m => [...m, { role: 'ai', content: response, parsedItems: items }])
          setLoading(false)
          return
        } else {
          response = t.panel_img_unclear
        }
      } else {
        const { response: r } = await api.chat(txt, msgs.filter(m => m.role !== 'system'), language)
        response = r
      }
      setMsgs(m => [...m, { role: 'ai', content: response }])
    } catch (e) {
      setMsgs(m => [...m, { role: 'ai', content: t.panel_error(e.message) }])
    }
    setLoading(false)
  }

  const saveItems = async (items) => {
    const txns = items.map(it => ({
      product_name: it.item, qty: it.qty,
      type: it.type || 'sale', date: it.date || null, source: 'photo'
    }))
    try {
      const { saved } = await api.logBulk(txns)
      setMsgs(m => [...m, { role: 'ai', content: t.panel_saved(saved) }])
    } catch (e) {
      setMsgs(m => [...m, { role: 'ai', content: t.panel_save_failed(e.message) }])
    }
  }

  const VOICE_LANG = { English: 'en-IN', Tamil: 'ta-IN', Hindi: 'hi-IN' }

  const startVoice = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { alert('Voice not supported. Please use Chrome.'); return }
    const rec = new SR()
    rec.lang = VOICE_LANG[language] || 'en-IN'; rec.continuous = false; rec.interimResults = false
    rec.onstart = () => setListening(true)
    rec.onresult = e => { setInput(e.results[0][0].transcript); setListening(false) }
    rec.onerror = () => setListening(false)
    rec.onend = () => setListening(false)
    rec.start(); recRef.current = rec
  }

  const stopVoice = () => { recRef.current?.stop(); setListening(false) }

  const handleImg = (file) => {
    if (!file) return
    setImgFile(file)
    setImgPreview(URL.createObjectURL(file))
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input, imgFile) }
  }

  return (
    <aside className={`side-panel${open ? '' : ' closed'}`}>
      {/* Header */}
      <div className="panel-header">
        <div className="panel-header-icon">◈</div>
        <div style={{ flex: 1 }}>
          <div className="panel-title">{t.panel_title}</div>
          <div className="panel-subtitle">{t.panel_subtitle_prefix} {language}</div>
        </div>
        <div className="panel-lang-pills">
          {LANGUAGES.map(l => (
            <button
              key={l.code}
              className={`lang-pill${language === l.code ? ' active' : ''}`}
              onClick={() => handleLanguageChange(l.code)}
              title={`Switch AI to ${l.code}`}
            >
              {l.label}
            </button>
          ))}
        </div>
        <button className="panel-close" onClick={onClose} title={t.settings_close}>✕</button>
      </div>

      {/* Quick chips */}
      <div className="panel-chips">
        {t.panel_chips.map((c, i) => (
          <button key={i} className="chip" onClick={() => send(c, null)}>{c}</button>
        ))}
      </div>

      {/* Messages */}
      <div className="panel-msgs">
        {msgs.map((m, i) => (
          <div key={i} className={`pmsg ${m.role === 'user' ? 'user' : 'ai'}`}>
            <div className="pmsg-bubble">
              {m.img && (
                <img src={m.img} alt="attached" style={{ width: '100%', maxHeight: 120, objectFit: 'cover', borderRadius: 9, marginBottom: 6 }} />
              )}
              {m.role === 'user'
                ? <span>{m.content}</span>
                : <div>{renderMd(m.content)}</div>
              }
              {m.parsedItems && (
                <button
                  className="btn btn-primary btn-sm"
                  style={{ marginTop: 8, fontSize: 11 }}
                  onClick={() => saveItems(m.parsedItems)}
                >
                  {t.panel_save_inventory}
                </button>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="pmsg ai">
            <div className="pmsg-bubble">
              <div style={{ display: 'flex', gap: 6, alignItems: 'center', color: 'var(--text2)', fontSize: 12 }}>
                <div className="spinner" style={{ width: 13, height: 13 }} />
                <span>{t.panel_thinking}</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="panel-input-area">
        {imgPreview && (
          <div className="panel-img-preview">
            <img src={imgPreview} alt="preview" />
            <span style={{ flex: 1 }}>{t.panel_img_attached}</span>
            <button onClick={() => { setImgFile(null); setImgPreview(null) }}>✕</button>
          </div>
        )}
        {listening && (
          <div style={{ fontSize: 11, color: 'var(--red)', marginBottom: 5, display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ animation: 'vring 1s infinite', display: 'inline-block', width: 6, height: 6, borderRadius: '50%', background: 'var(--red)' }} />
            {t.panel_listening(language)}
          </div>
        )}
        <div className="panel-input-row">
          <button className="panel-img-btn" onClick={() => fileRef.current?.click()} title="Attach image">
            🖼
          </button>
          <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={e => handleImg(e.target.files[0])} />

          <textarea
            ref={inputRef}
            className="panel-input"
            rows={1}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder={t.panel_placeholder}
            style={{ lineHeight: 1.5 }}
          />

          <button
            className={`voice-ring ${listening ? 'on' : 'idle'}`}
            onClick={listening ? stopVoice : startVoice}
            title={listening ? 'Stop' : 'Voice input'}
          >
            🎙
          </button>

          <button
            className="panel-send"
            onClick={() => send(input, imgFile)}
            disabled={(!input.trim() && !imgFile) || loading}
          >
            ➤
          </button>
        </div>
      </div>
    </aside>
  )
}
