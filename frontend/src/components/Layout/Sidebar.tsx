import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAppStore } from '../../store';
import './Sidebar.css';

export const Sidebar: React.FC = () => {
  const { activePanes, currentSession } = useAppStore();
  const paneCount = Object.keys(activePanes).length;

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <NavLink 
          to="/" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          🏠 Workspace
        </NavLink>
        
        <NavLink 
          to="/history" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          📚 History
        </NavLink>
        
        <NavLink 
          to="/templates" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          🔧 Templates
        </NavLink>
      </nav>
      
      <div className="session-summary">
        <h3>Current Session</h3>
        {currentSession ? (
          <div className="session-details">
            <p className="session-name">{currentSession.name}</p>
            <div className="session-stats">
              <div className="stat">
                <span className="stat-label">Panes:</span>
                <span className="stat-value">{paneCount}</span>
              </div>

              <div className="stat">
                <span className="stat-label">Status:</span>
                <span className={`stat-value status-${currentSession.status}`}>
                  {currentSession.status}
                </span>
              </div>
            </div>
          </div>
        ) : (
          <p className="no-session">No active session</p>
        )}
      </div>
      
      {paneCount > 0 && (
        <div className="active-panes">
          <h4>Active Panes ({paneCount})</h4>
          <div className="pane-list">
            {Object.values(activePanes).map(pane => (
              <div key={pane.id} className="pane-item">
                <div className="pane-model">
                  {pane.modelInfo.provider}:{pane.modelInfo.name}
                </div>
                <div className="pane-status">
                  {pane.isStreaming ? (
                    <span className="streaming">🔄 Streaming</span>
                  ) : (
                    <span className="idle">⏸️ Idle</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
};