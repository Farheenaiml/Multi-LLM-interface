import React from 'react';
import { useAppStore } from '../store';
import './History.css';

export const History: React.FC = () => {
  const { conversationHistory, sessions } = useAppStore();

  return (
    <div className="history-page">
      <div className="page-header">
        <h2>Conversation History</h2>
        <p>Browse and manage your previous conversations and sessions.</p>
      </div>

      <div className="history-content">
        <div className="history-section">
          <h3>Recent Sessions</h3>
          {sessions.length === 0 ? (
            <div className="empty-state">
              <p>No sessions found. Start a new broadcast to create your first session.</p>
            </div>
          ) : (
            <div className="session-list">
              {sessions.map(session => (
                <div key={session.id} className="session-card">
                  <div className="session-header">
                    <h4>{session.name}</h4>
                    <span className={`session-status status-${session.status}`}>
                      {session.status}
                    </span>
                  </div>
                  <div className="session-details">
                    <div className="session-meta">
                      <span>Created: {session.createdAt.toLocaleDateString()}</span>
                      <span>Panes: {session.panes.length}</span>
                      <span>Cost: ${session.totalCost.toFixed(4)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="history-section">
          <h3>Conversation Archive</h3>
          {conversationHistory.length === 0 ? (
            <div className="empty-state">
              <p>No archived conversations yet.</p>
            </div>
          ) : (
            <div className="conversation-list">
              {conversationHistory.map(history => (
                <div key={history.sessionId} className="conversation-card">
                  <h4>{history.name}</h4>
                  <div className="conversation-meta">
                    <span>{history.timestamp.toLocaleDateString()}</span>
                    <span>{history.messageCount} messages</span>
                    <span>${history.totalCost.toFixed(4)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};