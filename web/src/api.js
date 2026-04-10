const BASE = '/api'

async function req(path, opts = {}) {
  const res = await fetch(BASE + path, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  health: () => req('/health'),
  dashboard: () => req('/dashboard'),
  products: () => req('/products'),
  insights: () => req('/insights'),

  logTransaction: (txn) => req('/transactions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(txn) }),
  logBulk: (items) => req('/transactions/bulk', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(items) }),

  parseText: (text) => req('/ai/parse/text', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) }),
  parseVoice: (transcribed_text) => req('/ai/parse/voice', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ transcribed_text }) }),
  parseImage: (file) => {
    const fd = new FormData(); fd.append('file', file)
    return req('/ai/parse/image', { method: 'POST', body: fd })
  },
  importFile: (file) => {
    const fd = new FormData(); fd.append('file', file)
    return req('/import/file', { method: 'POST', body: fd })
  },

  chat: (message, chat_history, language = 'English') => req('/ai/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, chat_history, language }) }),
  performance: () => req('/ai/performance'),

  forecast: (body) => req('/forecast', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
  simulate: (body) => req('/simulator', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),

  seedDemo: () => req('/demo/seed', { method: 'POST' }),
}
