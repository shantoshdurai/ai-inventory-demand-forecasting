export default function Nav({ page, setPage, health }) {
  const links = [
    { id: 'dashboard', label: 'Dashboard', icon: '▦' },
    { id: 'advisor', label: 'AI Advisor', icon: '◈' },
    { id: 'input', label: 'Input Data', icon: '⊕' },
    { id: 'forecast', label: 'Forecast', icon: '◎' },
    { id: 'simulator', label: 'Simulator', icon: '⊘' },
  ]

  const isLive = health?.api_key_configured
  const isDemo = health && !health.api_key_configured

  return (
    <nav className="topnav">
      <a className="nav-brand" onClick={() => setPage('dashboard')} style={{ cursor: 'pointer' }}>
        <div className="nav-logo">◆</div>
        <span className="nav-name">StockSense</span>
      </a>

      <div className="nav-links">
        {links.map(l => (
          <button key={l.id} className={`nav-link${page === l.id ? ' active' : ''}`} onClick={() => setPage(l.id)}>
            <span style={{ fontSize: 15 }}>{l.icon}</span>
            <span>{l.label}</span>
          </button>
        ))}
      </div>

      <div className="nav-badge">
        {isLive && <span className="live-badge">● LIVE AI</span>}
        {isDemo && <span className="demo-badge">DEMO MODE</span>}
      </div>
    </nav>
  )
}
