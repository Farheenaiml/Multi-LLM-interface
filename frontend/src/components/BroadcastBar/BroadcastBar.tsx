import React, { useState } from 'react';
import { ModelInfo, ModelSelection } from '../../types';
import './BroadcastBar.css';

export interface BroadcastBarProps {
  onBroadcast: (prompt: string, models: ModelSelection[]) => void;
  availableModels: ModelInfo[];
  isStreaming: boolean;
}

export const BroadcastBar: React.FC<BroadcastBarProps> = ({
  onBroadcast,
  availableModels,
  isStreaming
}) => {
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState<ModelSelection[]>([]);
  const [showModelSelector, setShowModelSelector] = useState(false);

  const handleModelToggle = (model: ModelInfo) => {
    const modelId = `${model.provider}:${model.id}`;
    const isSelected = selectedModels.some(m => `${m.providerId}:${m.modelId}` === modelId);
    
    if (isSelected) {
      setSelectedModels(prev => 
        prev.filter(m => `${m.providerId}:${m.modelId}` !== modelId)
      );
    } else {
      const newSelection: ModelSelection = {
        providerId: model.provider,
        modelId: model.id,
        temperature: 0.7,
        maxTokens: model.maxTokens
      };
      setSelectedModels(prev => [...prev, newSelection]);
    }
  };

  const handleBroadcast = () => {
    if (prompt.trim() && selectedModels.length > 0) {
      onBroadcast(prompt, selectedModels);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleBroadcast();
    }
  };

  // Estimate tokens (rough approximation: 1 token ≈ 4 characters)
  const estimateTokens = (text: string) => Math.ceil(text.length / 4);

  // Calculate cost estimates
  const getEstimates = () => {
    const promptTokens = estimateTokens(prompt);
    const estimatedResponseTokens = 150; // Default estimate
    const totalTokens = promptTokens + estimatedResponseTokens;
    
    const totalCost = selectedModels.reduce((sum, selection) => {
      const model = availableModels.find(m => 
        m.provider === selection.providerId && m.id === selection.modelId
      );
      return sum + ((totalTokens / 1000) * (model?.costPer1kTokens || 0));
    }, 0);

    return {
      promptTokens,
      estimatedResponseTokens,
      totalTokens,
      totalCost,
      modelsCount: selectedModels.length
    };
  };

  const canBroadcast = prompt.trim().length > 0 && selectedModels.length > 0 && !isStreaming;

  return (
    <div className="broadcast-bar">
      <div className="broadcast-input-section">
        <div className="prompt-input-container">
          <textarea
            className="prompt-input"
            placeholder="Enter your prompt here... (Ctrl+Enter to broadcast)"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={isStreaming}
            rows={3}
          />
          <div className="input-actions">
            <button
              className="model-selector-btn"
              onClick={() => setShowModelSelector(!showModelSelector)}
              disabled={isStreaming}
            >
              Models ({selectedModels.length})
            </button>
            {selectedModels.length > 0 && prompt.trim() && (
              <div className="cost-estimate">
                <span className="estimate-tokens">~{getEstimates().totalTokens} tokens</span>
                <span className="estimate-cost">${getEstimates().totalCost.toFixed(4)}</span>
              </div>
            )}
            <button
              className={`broadcast-btn ${canBroadcast ? 'ready' : 'disabled'}`}
              onClick={handleBroadcast}
              disabled={!canBroadcast}
            >
              {isStreaming ? 'Broadcasting...' : 'Broadcast'}
            </button>
          </div>
        </div>
      </div>

      {showModelSelector && (
        <div className="model-selector">
          <div className="model-selector-header">
            <h3>Select Models to Broadcast To</h3>
            <button 
              className="close-selector"
              onClick={() => setShowModelSelector(false)}
            >
              ×
            </button>
          </div>
          
          <div className="model-grid">
            {availableModels.map((model) => {
              const modelId = `${model.provider}:${model.id}`;
              const isSelected = selectedModels.some(m => `${m.providerId}:${m.modelId}` === modelId);
              
              return (
                <div
                  key={modelId}
                  className={`model-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleModelToggle(model)}
                >
                  <div className="model-header">
                    <div className="model-name">{model.name}</div>
                    <div className="model-provider">{model.provider}</div>
                  </div>
                  <div className="model-details">
                    <div className="model-detail">
                      <span className="detail-label">Max Tokens:</span>
                      <span className="detail-value">{model.maxTokens.toLocaleString()}</span>
                    </div>
                    <div className="model-detail">
                      <span className="detail-label">Cost/1K:</span>
                      <span className="detail-value">${model.costPer1kTokens.toFixed(4)}</span>
                    </div>
                    <div className="model-detail">
                      <span className="detail-label">Streaming:</span>
                      <span className="detail-value">
                        {model.supportsStreaming ? '✓' : '✗'}
                      </span>
                    </div>
                  </div>
                  {isSelected && (
                    <div className="selection-indicator">✓</div>
                  )}
                </div>
              );
            })}
          </div>

          {selectedModels.length > 0 && (
            <div className="selected-models-summary">
              <h4>Selected Models ({selectedModels.length})</h4>
              <div className="selected-models-list">
                {selectedModels.map((selection, index) => (
                  <div key={index} className="selected-model">
                    <span className="selected-model-name">
                      {selection.providerId}:{selection.modelId}
                    </span>
                    <div className="model-config">
                      <label>
                        Temp: 
                        <input
                          type="number"
                          min="0"
                          max="2"
                          step="0.1"
                          value={selection.temperature || 0.7}
                          onChange={(e) => {
                            const newTemp = parseFloat(e.target.value);
                            setSelectedModels(prev => 
                              prev.map((m, i) => 
                                i === index ? { ...m, temperature: newTemp } : m
                              )
                            );
                          }}
                        />
                      </label>
                      <label>
                        Max Tokens:
                        <input
                          type="number"
                          min="1"
                          max={selection.maxTokens || 4000}
                          value={selection.maxTokens || 1000}
                          onChange={(e) => {
                            const newMax = parseInt(e.target.value);
                            setSelectedModels(prev => 
                              prev.map((m, i) => 
                                i === index ? { ...m, maxTokens: newMax } : m
                              )
                            );
                          }}
                        />
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {selectedModels.length > 0 && !showModelSelector && (
        <div className="selected-models-bar">
          <span className="selected-count">
            {selectedModels.length} model{selectedModels.length !== 1 ? 's' : ''} selected:
          </span>
          <div className="selected-models-chips">
            {selectedModels.map((selection, index) => (
              <div key={index} className="model-chip">
                {selection.providerId}:{selection.modelId}
                <button
                  className="remove-model"
                  onClick={() => {
                    setSelectedModels(prev => prev.filter((_, i) => i !== index));
                  }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};