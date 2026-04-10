import { useState, useEffect } from 'react'
import Nav from './components/Nav'
import SidePanel from './components/SidePanel'
import Dashboard from './pages/Dashboard'
import InputData from './pages/InputData'
import Forecast from './pages/Forecast'
import Simulator from './pages/Simulator'
import { api } from './api'
import { TRANSLATIONS } from './i18n'

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [health, setHealth] = useState(null)
  const [panelOpen, setPanelOpen] = useState(true)
  const [uiLang, setUiLang] = useState(() => localStorage.getItem('uiLang') || 'English')

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: 'error' }))
  }, [])

  const changeUiLang = (lang) => {
    setUiLang(lang)
    localStorage.setItem('uiLang', lang)
  }

  const t = TRANSLATIONS[uiLang] || TRANSLATIONS.English
  const pages = { dashboard: Dashboard, input: InputData, forecast: Forecast, simulator: Simulator }
  const Page = pages[page] || Dashboard

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Nav page={page} setPage={setPage} health={health} panelOpen={panelOpen} setPanelOpen={setPanelOpen} t={t} uiLang={uiLang} setUiLang={changeUiLang} />
      <div className="body-wrap">
        <main className="main-content">
          <Page t={t} />
        </main>
        <SidePanel open={panelOpen} onClose={() => setPanelOpen(false)} t={t} />
      </div>
    </div>
  )
}
