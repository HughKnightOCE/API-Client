import { useState } from 'react'
import './Sidebar.css'
import InfoPage from './InfoPage'

function Sidebar({
  darkMode,
  setDarkMode,
  savedRequests,
  history,
  onLoadRequest,
  onDeleteRequest,
}) {
  const [activeTab, setActiveTab] = useState('saved')

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>ApiClient</h1>
        <button
          className={`theme-toggle ${darkMode ? 'dark' : 'light'}`}
          onClick={() => setDarkMode(!darkMode)}
          title={darkMode ? 'Light mode' : 'Dark mode'}
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'saved' ? 'active' : ''}`}
          onClick={() => setActiveTab('saved')}
        >
          Saved
        </button>
        <button
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          History
        </button>
        <button
          className={`tab ${activeTab === 'info' ? 'active' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          Info
        </button>
      </div>

      <div className="sidebar-content">
        {activeTab === 'saved' && (
          <div className="request-list">
            {savedRequests.length === 0 ? (
              <p className="empty-message">No saved requests</p>
            ) : (
              savedRequests.map((req) => (
                <div key={req.name} className="request-item">
                  <button
                    className="request-name"
                    onClick={() => onLoadRequest(req)}
                  >
                    <span className="method-badge">{req.method}</span>
                    {req.name}
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => {
                      if (confirm(`Delete request "${req.name}"?`)) {
                        onDeleteRequest(req.name)
                      }
                    }}
                    title="Delete request"
                  >
                    ✕
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-list">
            {history.length === 0 ? (
              <p className="empty-message">No history</p>
            ) : (
              history
                .slice()
                .reverse()
                .map((item, idx) => (
                  <div key={idx} className="history-item">
                    <span className="method-badge">{item.method}</span>
                    <span className="url" title={item.url}>
                      {item.url}
                    </span>
                  </div>
                ))
            )}
          </div>
        )}

        {activeTab === 'info' && (
          <InfoPage />
        )}
      </div>
    </div>
  )
}

export default Sidebar
