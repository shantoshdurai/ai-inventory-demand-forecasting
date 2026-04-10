export default function Nav({ page, setPage, health, panelOpen, setPanelOpen }) {
  const links = [
    { id: 'dashboard', label: 'Dashboard', icon: '▦' },
    { id: 'input',     label: 'Input Data', icon: '⊕' },
    { id: 'forecast',  label: 'Forecast',   icon: '◎' },
    { id: 'simulator', label: 'Simulator',  icon: '⊘' },
  ]

  const isLive = health?.api_key_configured

  return (
    <nav className="topnav">
      <a className="nav-brand" onClick={() => setPage('dashboard')}>
        <div className="nav-logo">◆</div>
        <span className="nav-name">StockSense</span>
      </a>

      <div className="nav-links">
        {links.map(l => (
          <button key={l.id} className={`nav-link${page === l.id ? ' active' : ''}`} onClick={() => setPage(l.id)}>
            <span style={{ fontSize: 14 }}>{l.icon}</span>
            <span>{l.label}</span>
          </button>
        ))}
      </div>

      <div className="nav-right">
        {isLive
          ? <span className="badge badge-live"><span className="badge-dot" />Live AI</span>
          : <span className="badge badge-demo"><span className="badge-dot" />Demo</span>
        }
        <button
          className={`panel-toggle${panelOpen ? ' active' : ''}`}
          onClick={() => setPanelOpen(o => !o)}
          title={panelOpen ? 'Close AI panel' : 'Open AI panel'}
        >
          ◈
        </button>
      </div>
    </nav>
  )
}
