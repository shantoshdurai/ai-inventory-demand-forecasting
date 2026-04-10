import { useState } from 'react'
import { LANG_OPTIONS } from '../i18n'

export default function Nav({ page, setPage, health, panelOpen, setPanelOpen, t, uiLang, setUiLang }) {
  const [langOpen, setLangOpen] = useState(false)

  const links = [
    { id: 'dashboard', label: t.nav_dashboard, icon: '▦' },
    { id: 'input',     label: t.nav_input,     icon: '⊕' },
    { id: 'forecast',  label: t.nav_forecast,  icon: '◎' },
    { id: 'simulator', label: t.nav_simulator, icon: '⊘' },
  ]

  const isLive = health?.api_key_configured
  const currentLang = LANG_OPTIONS.find(l => l.code === uiLang) || LANG_OPTIONS[0]

  return (
    <nav className="topnav">
      <a className="nav-brand" onClick={() => setPage('dashboard')}>
        <div className="nav-logo">◆</div>
        <span className="nav-name">{t.nav_brand}</span>
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
          ? <span className="badge badge-live"><span className="badge-dot" />{t.nav_live}</span>
          : <span className="badge badge-demo"><span className="badge-dot" />{t.nav_demo}</span>
        }

        {/* Language switcher */}
        <div style={{ position: 'relative' }}>
          <button
            className="nav-lang-btn"
            onClick={() => setLangOpen(o => !o)}
            title="Change UI language"
          >
            <span style={{ fontSize: 13 }}>🌐</span>
            <span>{currentLang.native}</span>
            <span style={{ fontSize: 10, opacity: 0.6 }}>▾</span>
          </button>

          {langOpen && (
            <>
              <div className="lang-backdrop" onClick={() => setLangOpen(false)} />
              <div className="lang-dropdown">
                <div className="lang-dropdown-title">{t.settings_title}</div>
                <div className="lang-dropdown-desc">{t.settings_desc}</div>
                {LANG_OPTIONS.map(l => (
                  <button
                    key={l.code}
                    className={`lang-option${uiLang === l.code ? ' active' : ''}`}
                    onClick={() => { setUiLang(l.code); setLangOpen(false) }}
                  >
                    <span className="lang-option-native">{l.native}</span>
                    <span className="lang-option-label">{l.label}</span>
                    {uiLang === l.code && <span className="lang-check">✓</span>}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>

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
