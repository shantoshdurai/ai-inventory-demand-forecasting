import { useState, useRef, useEffect } from 'react'
import { api } from '../api'

const CHIPS = [
  'What to restock?',
  'Biggest risks?',
  'Performance report',
  'Trending products',
  'Forecast summary',
  'Slow movers?',
]

function renderMd(text) {
  if (!text) return null
  // Split into paragraphs/sections and render with basic markdown
  return text.split('\n').map((line, i) => {
    if (!line.trim()) return <div key={i} style={{ height: 5 }} />
    if (line.startsWith('### ')) return <div key={i} style={{ fontWeight: 700, color: 'var(--text)', fontSize: 13, marginTop: 8, marginBottom: 2 }}>{line.slice(4)}</div>
    if (line.startsWith('## ')) return <div key={i} style={{ fontWeight: 700, color: 'var(--text)', fontSize: 13.5, marginTop: 10, marginBottom: 3 }}>{line.slice(3)}</div>
    if (line.startsWith('**') && line.endsWith('**')) return <div key={i} style={{ fontWeight: 700, color: 'var(--text)', marginTop: 6 }}>{line.slice(2, -2)}</div>
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
  return s.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#f0eff5">$1</strong>')
}

export default function SidePanel({ open, onClose }) {
  const [msgs, setMsgs] = useState([
    { role: 'ai', content: 'Namaste! 👋 I\'m your StockSense AI advisor. Ask me anything about your inventory, restocking, or business performance — in English or Hindi. You can also send a photo of a bill or receipt and I\'ll analyze it.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [listening, setListening] = useState(false)
  const [imgFile, setImgFile] = useState(null)
  const [imgPreview, setImgPreview] = useState(null)
  const bottomRef = useRef(null)
  const recRef = useRef(null)
  const fileRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [msgs, loading])

  const send = async (text, image) => {
    const txt = (text || '').trim()
    if (!txt && !image) return
    setLoading(true)

    const userMsg = { role: 'user', content: txt || '(image attached)', img: imgPreview }
    setMsgs(m => [...m, userMsg])
    setInput('')
    setImgFile(null)
    setImgPreview(null)

    try {
      let response
      if (image) {
        // Parse image first, then optionally chat about it
        const { items } = await api.parseImage(image)
        if (items?.[0]?.error) {
          response = `Error analyzing image: ${items[0].error}`
        } else if (items?.length) {
          const summary = items.map(it => `• ${it.item}: ${it.qty} (${it.type})`).join('\n')
          response = `I found **${items.length} items** in your image:\n\n${summary}\n\nWould you like me to save these to your inventory?`
          setMsgs(m => [...m, { role: 'ai', content: response, parsedItems: items }])
          setLoading(false)
          return
        } else {
          response = "I couldn't extract any items from this image. Try a clearer photo of a bill, receipt, or stock register."
        }
      } else {
        const { response: r } = await api.chat(txt, msgs.filter(m => m.role !== 'system'))
        response = r
      }
      setMsgs(m => [...m, { role: 'ai', content: response }])
    } catch (e) {
      setMsgs(m => [...m, { role: 'ai', content: `Sorry, something went wrong: ${e.message}` }])
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
      setMsgs(m => [...m, { role: 'ai', content: `✓ Saved ${saved} transactions to your inventory.` }])
    } catch (e) {
      setMsgs(m => [...m, { role: 'ai', content: `Failed to save: ${e.message}` }])
    }
  }

  const startVoice = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { alert('Voice not supported. Please use Chrome.'); return }
    const rec = new SR()
    rec.lang = 'en-IN'; rec.continuous = false; rec.interimResults = false
    rec.onstart = () => setListening(true)
    rec.onresult = e => {
      const t = e.results[0][0].transcript
      setInput(t)
      setListening(false)
    }
    rec.onerror = () => setListening(false)
    rec.onend = () => setListening(false)
    rec.start(); recRef.current = rec
  }

  const stopVoice = () => { recRef.current?.stop(); setListening(false) }

  const handleImg = (file) => {
    if (!file) return
    setImgFile(file)
    const url = URL.createObjectURL(file)
    setImgPreview(url)
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input, imgFile) }
  }

  return (
    <aside className={`side-panel${open ? '' : ' closed'}`}>
      {/* Header */}
      <div className="panel-header">
        <div className="panel-header-icon">◈</div>
        <div>
          <div className="panel-title">AI Advisor</div>
          <div className="panel-subtitle">Gemma 4 · Hindi / English</div>
        </div>
        <button className="panel-close" onClick={onClose} title="Close panel">✕</button>
      </div>

      {/* Quick chips */}
      <div className="panel-chips">
        {CHIPS.map(c => (
          <button key={c} className="chip" onClick={() => send(c)}>{c}</button>
        ))}
      </div>

      {/* Messages */}
      <div className="panel-msgs">
        {msgs.map((m, i) => (
          <div key={i} className={`pmsg ${m.role === 'user' ? 'user' : 'ai'}`}>
            <div className="pmsg-bubble">
              {m.img && (
                <img src={m.img} alt="attached" style={{ width: '100%', maxHeight: 120, objectFit: 'cover', borderRadius: 7, marginBottom: 6 }} />
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
                  Save to inventory
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
                <span>Thinking...</span>
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
            <span style={{ flex: 1 }}>Image attached</span>
            <button onClick={() => { setImgFile(null); setImgPreview(null) }}>✕</button>
          </div>
        )}
        {listening && (
          <div style={{ fontSize: 11, color: 'var(--red)', marginBottom: 5, display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ animation: 'vring 1s infinite', display: 'inline-block', width: 6, height: 6, borderRadius: '50%', background: 'var(--red)' }} />
            Listening in Hindi / English...
          </div>
        )}
        <div className="panel-input-row">
          {/* Image attach */}
          <button className="panel-img-btn" onClick={() => fileRef.current?.click()} title="Attach image (bill, receipt, photo)">
            🖼
          </button>
          <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={e => handleImg(e.target.files[0])} />

          {/* Text input */}
          <textarea
            ref={inputRef}
            className="panel-input"
            rows={1}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask anything or attach an image..."
            style={{ lineHeight: 1.5 }}
          />

          {/* Voice */}
          <button
            className={`voice-ring ${listening ? 'on' : 'idle'}`}
            onClick={listening ? stopVoice : startVoice}
            title={listening ? 'Stop listening' : 'Voice input (Hindi/English)'}
          >
            🎙
          </button>

          {/* Send */}
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
