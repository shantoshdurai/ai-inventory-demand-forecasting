import { useState, useRef, useEffect } from 'react'
import { api } from '../api'

// Simple markdown-ish renderer
function Markdown({ text }) {
  if (!text) return null
  const lines = text.split('\n')
  const html = lines.map((line, i) => {
    if (line.startsWith('**') && line.endsWith('**')) return <strong key={i} style={{ display: 'block', color: 'var(--text)', marginTop: 8 }}>{line.slice(2, -2)}</strong>
    if (line.startsWith('### ')) return <h3 key={i} style={{ color: 'var(--text)', fontSize: 14, fontWeight: 700, marginTop: 12, marginBottom: 4 }}>{line.slice(4)}</h3>
    if (line.startsWith('## ')) return <h3 key={i} style={{ color: 'var(--text)', fontSize: 15, fontWeight: 700, marginTop: 14, marginBottom: 4 }}>{line.slice(3)}</h3>
    if (line.startsWith('- ') || line.startsWith('* ')) return <li key={i} style={{ marginLeft: 16, marginBottom: 2, color: 'rgba(240,238,250,0.85)' }} dangerouslySetInnerHTML={{ __html: bolden(line.slice(2)) }} />
    if (line.startsWith('| ')) return null // handle tables below
    if (line.trim() === '') return <div key={i} style={{ height: 6 }} />
    return <p key={i} style={{ marginBottom: 4, color: 'rgba(240,238,250,0.85)' }} dangerouslySetInnerHTML={{ __html: bolden(line) }} />
  })
  return <div className="prose">{html}</div>
}

function bolden(s) {
  return s.replace(/\*\*(.+?)\*\*/g, '<strong style="color:#f0eff5">$1</strong>')
}

const SUGGESTIONS = [
  'What should I restock this week?',
  'What are my biggest risks right now?',
  'Which products are trending up?',
  'Give me a full performance report',
]

export default function Advisor() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [listening, setListening] = useState(false)
  const [perfLoading, setPerfLoading] = useState(false)
  const bottomRef = useRef(null)
  const recognitionRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (text) => {
    if (!text.trim() || loading) return
    const userMsg = { role: 'user', content: text.trim() }
    const newHistory = [...messages, userMsg]
    setMessages(newHistory)
    setInput('')
    setLoading(true)
    try {
      const { response } = await api.chat(text.trim(), messages)
      setMessages([...newHistory, { role: 'assistant', content: response }])
    } catch (e) {
      setMessages([...newHistory, { role: 'assistant', content: `Error: ${e.message}` }])
    }
    setLoading(false)
  }

  const getPerformance = async () => {
    setPerfLoading(true)
    try {
      const { analysis } = await api.performance()
      setMessages(prev => [...prev,
        { role: 'user', content: 'Give me a full performance report' },
        { role: 'assistant', content: analysis }
      ])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${e.message}` }])
    }
    setPerfLoading(false)
  }

  const startVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) { alert('Voice not supported in this browser. Use Chrome.'); return }
    const rec = new SpeechRecognition()
    rec.lang = 'en-IN'
    rec.continuous = false
    rec.interimResults = false
    rec.onstart = () => setListening(true)
    rec.onresult = (e) => { setInput(e.results[0][0].transcript); setListening(false) }
    rec.onerror = () => setListening(false)
    rec.onend = () => setListening(false)
    rec.start()
    recognitionRef.current = rec
  }

  const stopVoice = () => { recognitionRef.current?.stop(); setListening(false) }

  return (
    <div className="page">
      <div className="page-title">AI Advisor</div>
      <div className="page-desc">Your Kirana shop business consultant — ask anything in English or Hindi. Powered by Gemma 4 31B.</div>

      {/* Quick actions */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
        <button className="btn btn-primary btn-sm" onClick={getPerformance} disabled={perfLoading}>
          {perfLoading ? <><div className="spinner" style={{ width: 14, height: 14 }} /> Loading...</> : '◈ Full Performance Report'}
        </button>
        <button className="btn btn-secondary btn-sm" onClick={() => setMessages([])}>Clear chat</button>
      </div>

      {/* Suggestions */}
      {messages.length === 0 && (
        <>
          <div className="sh">Try asking</div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 24 }}>
            {SUGGESTIONS.map(s => (
              <button key={s} className="btn btn-ghost btn-sm" onClick={() => send(s)}>{s}</button>
            ))}
          </div>
          <div className="empty-state">
            <div className="empty-state-icon">◈</div>
            <div className="empty-state-title">Ask your AI advisor</div>
            <div className="empty-state-sub">Type or speak your question about inventory, restocking, or performance</div>
          </div>
        </>
      )}

      {/* Chat */}
      {messages.length > 0 && (
        <div className="chat-wrap">
          {messages.map((m, i) => (
            <div key={i} className={`chat-msg ${m.role === 'user' ? 'user' : 'ai'}`}>
              <div className="chat-bubble">
                {m.role === 'user' ? m.content : <Markdown text={m.content} />}
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-msg ai">
              <div className="chat-bubble">
                <div className="loading-row"><div className="spinner" /><span>Thinking...</span></div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}

      {/* Input */}
      <div style={{ position: 'sticky', bottom: 24, background: 'var(--bg)', paddingTop: 12 }}>
        <div className="chat-input-row">
          <input
            className="input"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send(input)}
            placeholder="Ask about inventory, restocking, performance... (or press mic to speak)"
          />
          <button
            className={`voice-btn ${listening ? 'listening' : 'idle'}`}
            onClick={listening ? stopVoice : startVoice}
            title={listening ? 'Stop listening' : 'Start voice input'}
          >
            {listening ? '◉' : '🎙'}
          </button>
          <button className="btn btn-primary" onClick={() => send(input)} disabled={!input.trim() || loading}>
            Send
          </button>
        </div>
        {listening && <div style={{ fontSize: 12, color: 'var(--red)', marginTop: 6 }}>● Listening... speak now</div>}
      </div>
    </div>
  )
}
