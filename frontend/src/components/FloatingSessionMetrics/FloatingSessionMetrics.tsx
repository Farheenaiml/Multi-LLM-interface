import React, { useState } from 'react';
import { useAppStore } from '../../store';
import './FloatingSessionMetrics.css';

export interface FloatingSessionMetricsProps {
  isVisible: boolean;
  onToggle: () => void;
}

export const FloatingSessionMetrics: React.FC<FloatingSessionMetricsProps> = ({
  isVisible,
  onToggle
}) => {
  const { activePanes } = useAppStore();
  const [sessionStartTime] = useState(new Date());

  if (!isVisible) return null;

  const totalPanes = Object.keys(activePanes).length;
  const totalMessages = Object.values(activePanes).reduce((sum, pane) => sum + pane.messages.length, 0);

  const totalCost = Object.values(activePanes).reduce((sum, pane) => sum + pane.metrics.cost, 0);
  const avgLatency = totalPanes > 0
    ? Object.values(activePanes).reduce((sum, pane) => sum + pane.metrics.latency, 0) / totalPanes
    : 0;

  const activeProviders = [...new Set(Object.values(activePanes).map(pane => pane.modelInfo.provider))];
  const streamingPanes = Object.values(activePanes).filter(pane => pane.isStreaming).length;

  return (
    <div className="floating-session-metrics">
      <div className="metrics-header">
        <div className="metrics-title">
          <span className="metrics-icon">📊</span>
          <span>Session Metrics</span>
        </div>
        <div className="metrics-controls">
          <button
            className="close-btn"
            onClick={onToggle}
            title="Close"
          >
            ×
          </button>
        </div>
      </div>

      <div className="metrics-content">
        <div className="metrics-content">
          <div className="metrics-section">
            <h4>Active Session</h4>
            <div className="metrics-grid">
              <div className="metric-item">
                <span className="metric-label">Active Panes</span>
                <span className="metric-value">{totalPanes}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Total Messages</span>
                <span className="metric-value">{totalMessages}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Streaming</span>
                <span className="metric-value streaming">
                  {streamingPanes > 0 ? `${streamingPanes} active` : 'None'}
                </span>
              </div>
            </div>
          </div>

          <div className="metrics-section">
            <h4>Usage Statistics</h4>
            <div className="metrics-grid">
              {/* <div className="metric-item">
                <span className="metric-label">Total Tokens</span>
                <span className="metric-value">{totalTokens.toLocaleString()}</span>
              </div> */}
              <div className="metric-item">
                <span className="metric-label">Total Cost</span>
                <span className="metric-value cost">${totalCost.toFixed(4)}</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">Avg Latency</span>
                <span className="metric-value">{avgLatency.toFixed(0)}ms</span>
              </div>
            </div>
          </div>

          <div className="metrics-section">
            <h4>Providers</h4>
            <div className="providers-list">
              {activeProviders.length > 0 ? (
                activeProviders.map(provider => (
                  <div key={provider} className="provider-tag">
                    {provider}
                  </div>
                ))
              ) : (
                <span className="no-providers">No active providers</span>
              )}
            </div>
          </div>

          <div className="metrics-section">
            <h4>Session Info</h4>
            <div className="session-info">
              <div className="info-item">
                <span className="info-label">Started:</span>
                <span className="info-value">
                  {sessionStartTime.toLocaleTimeString()}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Duration:</span>
                <span className="info-value">
                  {Math.floor((Date.now() - sessionStartTime.getTime()) / 60000) + 'm'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};