import React, { useState } from 'react';
import { ChatPane } from '../../types';
import './CompareBar.css';

export interface CompareBarProps {
  availablePanes: ChatPane[];
  selectedPanes: [string, string] | null;
  onCompareToggle: (paneIds: [string, string] | null) => void;
  isComparing: boolean;
}

export const CompareBar: React.FC<CompareBarProps> = ({
  availablePanes,
  selectedPanes,
  onCompareToggle,
  isComparing
}) => {
  const [showPaneSelector, setShowPaneSelector] = useState(false);
  const [tempSelection, setTempSelection] = useState<{
    first: string | null;
    second: string | null;
  }>({
    first: selectedPanes?.[0] || null,
    second: selectedPanes?.[1] || null
  });

  const handlePaneSelect = (paneId: string, position: 'first' | 'second') => {
    setTempSelection(prev => ({
      ...prev,
      [position]: paneId
    }));
  };

  const applyComparison = () => {
    if (tempSelection.first && tempSelection.second && tempSelection.first !== tempSelection.second) {
      onCompareToggle([tempSelection.first, tempSelection.second]);
      setShowPaneSelector(false);
    }
  };

  const clearComparison = () => {
    onCompareToggle(null);
    setTempSelection({ first: null, second: null });
    setShowPaneSelector(false);
  };

  const toggleCompareMode = () => {
    if (isComparing) {
      clearComparison();
    } else {
      if (availablePanes.length >= 2) {
        setShowPaneSelector(true);
      }
    }
  };

  const getSelectedPaneInfo = (paneId: string) => {
    const pane = availablePanes.find(p => p.id === paneId);
    return pane ? `${pane.modelInfo.provider}:${pane.modelInfo.name}` : 'Unknown';
  };

  const canCompare = availablePanes.length >= 2;
  const hasValidSelection = tempSelection.first && tempSelection.second && 
                           tempSelection.first !== tempSelection.second;

  return (
    <div className="compare-bar">
      <div className="compare-controls">
        <div className="compare-status">
          <h3>Compare Responses</h3>
          {isComparing && selectedPanes ? (
            <div className="active-comparison">
              <span className="comparison-info">
                Comparing: <strong>{getSelectedPaneInfo(selectedPanes[0])}</strong> vs{' '}
                <strong>{getSelectedPaneInfo(selectedPanes[1])}</strong>
              </span>
            </div>
          ) : (
            <span className="comparison-hint">
              {canCompare 
                ? 'Select two panes to compare their responses'
                : `Need at least 2 panes (${availablePanes.length} available)`
              }
            </span>
          )}
        </div>

        <div className="compare-actions">
          <button
            className={`compare-btn ${isComparing ? 'active' : ''}`}
            onClick={toggleCompareMode}
            disabled={!canCompare}
            title={canCompare ? 'Toggle comparison mode' : 'Need at least 2 panes to compare'}
          >
            {isComparing ? '✓ Comparing' : '⚖️ Compare'}
          </button>

          {isComparing && (
            <button
              className="clear-btn"
              onClick={clearComparison}
              title="Clear comparison"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {showPaneSelector && (
        <div className="pane-selector">
          <div className="selector-header">
            <h4>Select Panes to Compare</h4>
            <button 
              className="close-selector"
              onClick={() => setShowPaneSelector(false)}
            >
              ×
            </button>
          </div>

          <div className="selection-grid">
            <div className="selection-column">
              <h5>First Pane</h5>
              <div className="pane-options">
                {availablePanes.map(pane => (
                  <div
                    key={`first-${pane.id}`}
                    className={`pane-option ${
                      tempSelection.first === pane.id ? 'selected' : ''
                    } ${tempSelection.second === pane.id ? 'disabled' : ''}`}
                    onClick={() => {
                      if (tempSelection.second !== pane.id) {
                        handlePaneSelect(pane.id, 'first');
                      }
                    }}
                  >
                    <div className="pane-info">
                      <div className="pane-model">
                        {pane.modelInfo.provider}:{pane.modelInfo.name}
                      </div>
                      <div className="pane-stats">
                        {pane.messages.length} messages • {pane.metrics.tokenCount} tokens
                      </div>
                    </div>
                    {tempSelection.first === pane.id && (
                      <div className="selection-indicator">✓</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="selection-divider">
              <div className="vs-indicator">VS</div>
            </div>

            <div className="selection-column">
              <h5>Second Pane</h5>
              <div className="pane-options">
                {availablePanes.map(pane => (
                  <div
                    key={`second-${pane.id}`}
                    className={`pane-option ${
                      tempSelection.second === pane.id ? 'selected' : ''
                    } ${tempSelection.first === pane.id ? 'disabled' : ''}`}
                    onClick={() => {
                      if (tempSelection.first !== pane.id) {
                        handlePaneSelect(pane.id, 'second');
                      }
                    }}
                  >
                    <div className="pane-info">
                      <div className="pane-model">
                        {pane.modelInfo.provider}:{pane.modelInfo.name}
                      </div>
                      <div className="pane-stats">
                        {pane.messages.length} messages • {pane.metrics.tokenCount} tokens
                      </div>
                    </div>
                    {tempSelection.second === pane.id && (
                      <div className="selection-indicator">✓</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="selector-actions">
            <button
              className="apply-btn"
              onClick={applyComparison}
              disabled={!hasValidSelection}
            >
              Start Comparison
            </button>
            <button
              className="cancel-btn"
              onClick={() => setShowPaneSelector(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {isComparing && (
        <div className="comparison-legend">
          <div className="legend-item">
            <span className="legend-color added"></span>
            <span className="legend-text">Added in second pane</span>
          </div>
          <div className="legend-item">
            <span className="legend-color removed"></span>
            <span className="legend-text">Removed from first pane</span>
          </div>
          <div className="legend-item">
            <span className="legend-color unchanged"></span>
            <span className="legend-text">Unchanged content</span>
          </div>
        </div>
      )}
    </div>
  );
};