import React, { useState } from 'react';
import { ModelInfo } from '../../types';
import './FloatingModelSelector.css';

export interface FloatingModelSelectorProps {
  availableModels: ModelInfo[];
  onModelSelect: (model: ModelInfo, prompt: string) => void;
  onMultiModelSelect?: (models: ModelInfo[], prompt: string) => void;
  isStreaming: boolean;
}

export const FloatingModelSelector: React.FC<FloatingModelSelectorProps> = ({
  availableModels,
  onModelSelect,
  onMultiModelSelect,
  isStreaming
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState<Set<string>>(new Set());

  // Token estimation function (rough approximation)
  const estimateTokens = (text: string): number => {
    // Rough estimation: ~4 characters per token for English text
    return Math.ceil(text.length / 4);
  };

  // Calculate cost and token estimates
  const getEstimates = (models: ModelInfo[]) => {
    const promptTokens = estimateTokens(prompt);
    const estimatedResponseTokens = Math.min(promptTokens * 2, 500); // Rough estimate
    const totalTokens = promptTokens + estimatedResponseTokens;
    
    const totalCost = models.reduce((sum, model) => {
      return sum + ((totalTokens / 1000) * (model.costPer1kTokens || 0));
    }, 0);

    return {
      promptTokens,
      estimatedResponseTokens,
      totalTokens,
      totalCost,
      modelsCount: models.length
    };
  };

  // Get warning level based on cost
  const getWarningLevel = (cost: number): 'none' | 'low' | 'medium' | 'high' => {
    if (cost < 0.01) return 'none';
    if (cost < 0.05) return 'low';
    if (cost < 0.20) return 'medium';
    return 'high';
  };

  const handleModelToggle = (model: ModelInfo) => {
    const modelKey = `${model.provider}:${model.id}`;
    const newSelected = new Set(selectedModels);
    
    if (newSelected.has(modelKey)) {
      newSelected.delete(modelKey);
    } else {
      newSelected.add(modelKey);
    }
    
    setSelectedModels(newSelected);
  };

  const handleSingleModelClick = (model: ModelInfo) => {
    if (prompt.trim()) {
      onModelSelect(model, prompt);
      setPrompt('');
      setIsExpanded(false);
      setSelectedModels(new Set());
    }
  };

  const handleBroadcastSelected = () => {
    if (prompt.trim() && selectedModels.size > 0) {
      const modelsToSend = availableModels.filter(model => 
        selectedModels.has(`${model.provider}:${model.id}`)
      );
      
      if (onMultiModelSelect) {
        onMultiModelSelect(modelsToSend, prompt);
      } else {
        // Fallback to individual calls
        modelsToSend.forEach(model => onModelSelect(model, prompt));
      }
      
      setPrompt('');
      setIsExpanded(false);
      setSelectedModels(new Set());
    }
  };

  const handleBroadcastAll = () => {
    if (prompt.trim()) {
      if (onMultiModelSelect) {
        onMultiModelSelect(availableModels, prompt);
      } else {
        // Fallback to individual calls
        availableModels.forEach(model => onModelSelect(model, prompt));
      }
      
      setPrompt('');
      setIsExpanded(false);
      setSelectedModels(new Set());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && prompt.trim()) {
      e.preventDefault(); // Prevent form submission
      // If only one model available, use it directly
      if (availableModels.length === 1) {
        onModelSelect(availableModels[0], prompt);
        setPrompt('');
      } else {
        setIsExpanded(true);
      }
    }
  };

  return (
    <div className="floating-model-selector">
      <div className="selector-main">
        <div className="prompt-section">
          <input
            type="text"
            className="floating-prompt-input"
            placeholder="Enter prompt and select model..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={isStreaming}
          />
          <button
            className="expand-btn"
            onClick={() => setIsExpanded(!isExpanded)}
            disabled={!prompt.trim() || isStreaming}
            title="Select model"
          >
            {isStreaming ? '⏳' : '🤖'}
          </button>
        </div>

        {isExpanded && prompt.trim() && (
          <div className="model-dropdown">
            <div className="dropdown-header">
              <span>Select Models for: "{prompt.length > 30 ? prompt.substring(0, 30) + '...' : prompt}"</span>
              <div className="selection-controls">
                <button
                  className="select-all-btn"
                  onClick={() => setSelectedModels(new Set(availableModels.map(m => `${m.provider}:${m.id}`)))}
                  disabled={isStreaming}
                >
                  Select All
                </button>
                <button
                  className="clear-all-btn"
                  onClick={() => setSelectedModels(new Set())}
                  disabled={isStreaming}
                >
                  Clear
                </button>
              </div>
            </div>
            
            <div className="model-list">
              {availableModels.map((model) => {
                const modelKey = `${model.provider}:${model.id}`;
                const isSelected = selectedModels.has(modelKey);
                
                return (
                  <div
                    key={modelKey}
                    className={`model-option ${isSelected ? 'selected' : ''}`}
                  >
                    <label className="model-checkbox">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleModelToggle(model)}
                        disabled={isStreaming}
                      />
                      <div className="model-info">
                        <div className="model-name">{model.name}</div>
                        <div className="model-provider">{model.provider}</div>
                      </div>
                      <div className="model-cost">
                        ${(model.costPer1kTokens || 0).toFixed(4)}/1K
                      </div>

                    </label>
                    
                    <button
                      className="single-send-btn"
                      onClick={() => handleSingleModelClick(model)}
                      disabled={isStreaming}
                      title="Send to this model only"
                    >
                      →
                    </button>
                  </div>
                );
              })}
            </div>
            
            <div className="dropdown-footer">
              {/* Token Warning/Info */}
              {prompt.trim() && (
                <div className="token-info">
                  {selectedModels.size > 0 && (
                    <div className="token-estimate selected">
                      {(() => {
                        const selectedModelsList = availableModels.filter(m => 
                          selectedModels.has(`${m.provider}:${m.id}`)
                        );
                        const estimates = getEstimates(selectedModelsList);
                        const warningLevel = getWarningLevel(estimates.totalCost);
                        
                        return (
                          <div className={`estimate-card ${warningLevel}`}>
                            <span className="estimate-icon">
                              {warningLevel === 'high' ? '⚠️' : warningLevel === 'medium' ? '💰' : '💡'}
                            </span>
                            <span className="estimate-label">Selected ({estimates.modelsCount})</span>
                            <span className="estimate-cost">${estimates.totalCost.toFixed(4)}</span>

                          </div>
                        );
                      })()}
                    </div>
                  )}
                  
                  <div className="token-estimate all">
                    {(() => {
                      const estimates = getEstimates(availableModels);
                      const warningLevel = getWarningLevel(estimates.totalCost);
                      
                      return (
                        <div className={`estimate-card ${warningLevel}`}>
                          <span className="estimate-icon">
                            {warningLevel === 'high' ? '⚠️' : warningLevel === 'medium' ? '💰' : '📊'}
                          </span>
                          <span className="estimate-label">All ({estimates.modelsCount})</span>
                          <span className="estimate-cost">${estimates.totalCost.toFixed(4)}</span>

                        </div>
                      );
                    })()}
                  </div>
                </div>
              )}

              <div className="broadcast-actions">
                <button
                  className="broadcast-selected-btn"
                  onClick={handleBroadcastSelected}
                  disabled={isStreaming || selectedModels.size === 0}
                >
                  🚀 Send to Selected ({selectedModels.size})
                </button>
                <button
                  className="broadcast-all-btn"
                  onClick={handleBroadcastAll}
                  disabled={isStreaming}
                >
                  📡 Broadcast to All ({availableModels.length})
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {isStreaming && (
        <div className="streaming-status">
          <div className="streaming-dots">
            <span></span><span></span><span></span>
          </div>
          <span>Broadcasting...</span>
        </div>
      )}
    </div>
  );
};