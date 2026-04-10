import { useState, useEffect } from 'react'
import Nav from './components/Nav'
import SidePanel from './components/SidePanel'
import Dashboard from './pages/Dashboard'
import InputData from './pages/InputData'
import Forecast from './pages/Forecast'
import Simulator from './pages/Simulator'
import { api } from './api'
import { TRANSLATIONS } from './i18n'

function SplashScreen() {
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 50%, #ede9fe 100%)',
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 20,
    }}>
      <div style={{
        width: 64, height: 64, background: 'linear-gradient(135deg, #6366f1, #818cf8)',
        borderRadius: 20, display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 28, color: 'white',
        boxShadow: '0 8px 0 rgba(99,102,241,0.3), 0 16px 32px rgba(99,102,241,0.2)',
        animation: 'pulse 1.8s ease-in-out infinite',
      }}>◆</div>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 24, fontWeight: 800, color: '#1e1b4b', letterSpacing: '-0.5px' }}>StockSense</div>
        <div style={{ fontSize: 13, color: 'rgba(30,27,75,0.5)', marginTop: 4 }}>Loading your Kirana AI...</div>
      </div>
      <div style={{ display: 'flex', gap: 6 }}>
        {[0,1,2].map(i => (
          <div key={i} style={{
            width: 8, height: 8, borderRadius: '50%', background: '#6366f1',
            animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
            opacity: 0.7,
          }} />
        ))}
      </div>
      <style>{`
        @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.06)} }
        @keyframes bounce { 0%,100%{transform:translateY(0);opacity:0.4} 50%{transform:translateY(-8px);opacity:1} }
      `}</style>
    </div>
  )
}

function DemoBanner() {
  const [dismissed, setDismissed] = useState(false)
  if (dismissed) return null
  return (
    <div style={{
      background: 'linear-gradient(135deg, #fef3c7, #fde68a)',
      borderBottom: '1.5px solid rgba(245,158,11,0.25)',
      padding: '9px 20px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
      fontSize: 12.5, color: '#92400e', fontWeight: 500, flexShrink: 0,
    }}>
      <span>
        <strong>Demo Mode</strong> — AI chat is disabled. Dashboard, forecasts, and simulator all work with real ML.
        Add a <code style={{ background: 'rgba(0,0,0,0.08)', padding: '1px 5px', borderRadius: 4 }}>GEMINI_API_KEY</code> env variable to enable AI.
      </span>
      <button onClick={() => setDismissed(true)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 16, color: '#92400e', opacity: 0.6, lineHeight: 1 }}>✕</button>
    </div>
  )
}

function Footer() {
  return (
    <div style={{
      borderTop: '1px solid rgba(99,102,241,0.1)',
      background: 'rgba(255,255,255,0.6)',
      backdropFilter: 'blur(12px)',
      padding: '10px 24px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      fontSize: 11.5, color: 'rgba(30,27,75,0.4)', flexShrink: 0,
    }}>
      <span>Built by <a href="https://github.com/shantoshdurai" target="_blank" rel="noreferrer" style={{ color: '#6366f1', fontWeight: 700, textDecoration: 'none' }}>Santosh Durai</a></span>
      <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#4ade80', display: 'inline-block' }} />
        Powered by Gemma 4 · XGBoost · Prophet
      </span>
      <a href="https://github.com/shantoshdurai/ai-inventory-demand-forecasting" target="_blank" rel="noreferrer" style={{ color: '#6366f1', fontWeight: 600, textDecoration: 'none' }}>
        GitHub ↗
      </a>
    </div>
  )
}

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [health, setHealth] = useState(null)
  const [panelOpen, setPanelOpen] = useState(true)
  const [uiLang, setUiLang] = useState(() => localStorage.getItem('uiLang') || 'English')
  const [ready, setReady] = useState(false)

  useEffect(() => {
    api.health()
      .then(h => { setHealth(h); setReady(true) })
      .catch(() => { setHealth({ status: 'error' }); setReady(true) })
  }, [])

  const changeUiLang = (lang) => {
    setUiLang(lang)
    localStorage.setItem('uiLang', lang)
  }

  const t = TRANSLATIONS[uiLang] || TRANSLATIONS.English
  const pages = { dashboard: Dashboard, input: InputData, forecast: Forecast, simulator: Simulator }
  const Page = pages[page] || Dashboard
  const isDemo = health && !health.api_key_configured

  if (!ready) return <SplashScreen />

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Nav page={page} setPage={setPage} health={health} panelOpen={panelOpen} setPanelOpen={setPanelOpen} t={t} uiLang={uiLang} setUiLang={changeUiLang} />
      {isDemo && <DemoBanner />}
      <div className="body-wrap">
        <main className="main-content">
          <Page t={t} />
          <Footer />
        </main>
        <SidePanel open={panelOpen} onClose={() => setPanelOpen(false)} t={t} isDemo={isDemo} />
      </div>
    </div>
  )
}
