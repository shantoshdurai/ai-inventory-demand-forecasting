import { useState, useEffect } from 'react'
import Nav from './components/Nav'
import Dashboard from './pages/Dashboard'
import Advisor from './pages/Advisor'
import InputData from './pages/InputData'
import Forecast from './pages/Forecast'
import Simulator from './pages/Simulator'
import { api } from './api'

export default function App() {
  const [page, setPage] = useState('dashboard')
  const [health, setHealth] = useState(null)

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: 'error' }))
  }, [])

  const pages = { dashboard: Dashboard, advisor: Advisor, input: InputData, forecast: Forecast, simulator: Simulator }
  const Page = pages[page] || Dashboard

  return (
    <div className="app">
      <Nav page={page} setPage={setPage} health={health} />
      <Page />
    </div>
  )
}
