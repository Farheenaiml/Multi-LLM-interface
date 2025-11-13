import React, { useState } from 'react';
import { ChatPane, SelectedContent, TransferContent } from '../../types';
import './SendToMenu.css';

export interface SendToMenuProps {
  sourcePane: string;
  selectedContent: SelectedContent;
  availableTargets: ChatPane[];
  onSendTo: (targetPaneId: string, content: TransferContent, options: {
    transferMode: 'append' | 'replace' | 'summarize';
    additionalContext?: string;
    preserveRoles: boolean;
    summaryInstructions?: string;
  }) => void;
  onClose: () => void;
  isVisible: boolean;
}

export const SendToMenu: React.FC<SendToMenuProps> = ({
  sourcePane,
  selectedContent,
  availableTargets,
  onSendTo,
  onClose,
  isVisible
}) => {
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null);
  const [transferMode, setTransferMode] = useState<'append' | 'replace' | 'summarize'>('append');
  const [preserveRoles, setPreserveRoles] = useState(true);
  const [additionalContext, setAdditionalContext] = useState('');
  const [summaryInstructions, setSummaryInstructions] = useState('');
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  if (!isVisible) return null;

  const sourcePaneInfo = availableTargets.find(p => p.id === sourcePane);
  const targetPanes = availableTargets.filter(p => p.id !== sourcePane);
  const selectedTargetPane = targetPanes.find(p => p.id === selectedTarget);

  const handleSendTo = async () => {
    if (!selectedTarget || !sourcePaneInfo) return;
    
    // Show loading state for summarize mode
    if (transferMode === 'summarize') {
      setIsGeneratingSummary(true);
    }

    // Get the actual messages from the source pane
    const sourceMessages = sourcePaneInfo.messages.filter(m => 
      selectedContent.messageIds.includes(m.id)
    );

    // If no messages selected and not in summarize mode, show error
    if (sourceMessages.length === 0 && transferMode !== 'summarize') {
      alert('Please select messages first or use "Summarize conversation" mode.');
      return;
    }

    let messagesToTransfer;

    if (transferMode === 'summarize') {
      // For summarize mode, we send the selected messages to backend
      // Backend will generate the summary using source pane's model
      // and transfer only the summary (not the conversation or prompt)
      messagesToTransfer = sourceMessages.map(msg => ({
        ...msg,
        id: `${msg.id}-summary-source-${Date.now()}`,
        provenance: {
          sourceModel: sourcePaneInfo.modelInfo.name,
          sourcePaneId: sourcePane,
          transferTimestamp: new Date(),
          contentHash: btoa(msg.content).substring(0, 8)
        }
      }));
    } else {
      // Original transfer logic for append/replace modes
      messagesToTransfer = sourceMessages.map(msg => ({
        ...msg,
        id: `${msg.id}-transfer-${Date.now()}`, // Generate new ID for transferred message
        provenance: {
          sourceModel: sourcePaneInfo.modelInfo.name,
          sourcePaneId: sourcePane,
          transferTimestamp: new Date(),
          contentHash: btoa(msg.content).substring(0, 8) // Simple hash for tracking
        }
      }));

      // Add additional context as a system message if provided
      if (additionalContext.trim()) {
        const contextMessage = {
          id: `context-${Date.now()}`,
          role: 'system' as const,
          content: additionalContext.trim(),
          timestamp: new Date(),
          provenance: {
            sourceModel: 'user-context',
            sourcePaneId: sourcePane,
            transferTimestamp: new Date(),
            contentHash: btoa(additionalContext).substring(0, 8)
          }
        };
        messagesToTransfer = [contextMessage, ...messagesToTransfer];
      }
    }

    // Create transfer content with provenance
    const transferContent: TransferContent = {
      messages: messagesToTransfer,
      provenance: {
        sourceModel: sourcePaneInfo.modelInfo.name,
        sourcePaneId: sourcePane,
        transferTimestamp: new Date(),
        contentHash: btoa(selectedContent.text + additionalContext).substring(0, 8)
      }
    };

    try {
      await onSendTo(selectedTarget, transferContent, {
        transferMode,
        additionalContext: additionalContext.trim() || undefined,
        preserveRoles,
        summaryInstructions: summaryInstructions.trim() || undefined
      });
      onClose();
    } catch (error) {
      console.error('Transfer failed:', error);
      alert('Failed to transfer messages. Please try again.');
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  const getPreviewText = (text: string, maxLength: number = 200) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const canSend = selectedTarget; // Allow sending even with no messages selected

  return (
    <div className="send-to-overlay">
      <div className="send-to-menu">
        <div className="menu-header">
          <h3>Send Messages to Another Pane</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="menu-content">
          {/* Source Information */}
          <div className="source-section">
            <h4>From</h4>
            <div className="source-info">
              <div className="pane-identifier">
                {sourcePaneInfo ? (
                  <>
                    <span className="pane-model">
                      {sourcePaneInfo.modelInfo.provider}:{sourcePaneInfo.modelInfo.name}
                    </span>
                    <span className="message-count">
                      {selectedContent.messageIds.length} message{selectedContent.messageIds.length !== 1 ? 's' : ''} selected
                    </span>
                  </>
                ) : (
                  <span className="error">Source pane not found</span>
                )}
              </div>
            </div>

            {selectedContent.messageIds.length === 0 ? (
              <div className="no-selection-message">
                <p>💡 No messages selected. Go back and select messages first, or choose "Summarize" mode to create a summary prompt.</p>
              </div>
            ) : selectedContent.text && (
              <div className="content-preview">
                <h5>Content Preview</h5>
                <div className="preview-text">
                  {getPreviewText(selectedContent.text)}
                </div>
              </div>
            )}
          </div>

          {/* Target Selection */}
          <div className="target-section">
            <h4>To</h4>
            {targetPanes.length === 0 ? (
              <div className="no-targets">
                <p>No other panes available. Create more panes to transfer content.</p>
              </div>
            ) : (
              <div className="target-list">
                {targetPanes.map(pane => (
                  <div
                    key={pane.id}
                    className={`target-option ${selectedTarget === pane.id ? 'selected' : ''}`}
                    onClick={() => setSelectedTarget(pane.id)}
                  >
                    <div className="target-info">
                      <div className="target-model">
                        {pane.modelInfo.provider}:{pane.modelInfo.name}
                      </div>
                      <div className="target-stats">
                        {pane.messages.length} messages
                      </div>
                      {pane.isStreaming && (
                        <div className="streaming-warning">
                          ⚠️ Currently streaming
                        </div>
                      )}
                    </div>
                    {selectedTarget === pane.id && (
                      <div className="selection-indicator">✓</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Transfer Options */}
          {selectedTarget && (
            <div className="options-section">
              <h4>Transfer Options</h4>
              
              <div className="option-group">
                <label className="option-label">Transfer Mode</label>
                <div className="radio-group">
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="transferMode"
                      value="append"
                      checked={transferMode === 'append'}
                      onChange={(e) => setTransferMode(e.target.value as 'append' | 'replace' | 'summarize')}
                    />
                    <span>Append to conversation</span>
                    <small>Add messages to the end of the target conversation</small>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="transferMode"
                      value="replace"
                      checked={transferMode === 'replace'}
                      onChange={(e) => setTransferMode(e.target.value as 'append' | 'replace' | 'summarize')}
                    />
                    <span>Replace conversation</span>
                    <small>Clear target pane and add these messages</small>
                  </label>
                  <label className="radio-option">
                    <input
                      type="radio"
                      name="transferMode"
                      value="summarize"
                      checked={transferMode === 'summarize'}
                      onChange={(e) => setTransferMode(e.target.value as 'append' | 'replace' | 'summarize')}
                    />
                    <span>Summarize conversation</span>
                    <small>Generate a summary of the selected messages and append it</small>
                  </label>
                </div>
              </div>

              {/* Summary Instructions - only show when summarize mode is selected */}
              {transferMode === 'summarize' && (
                <div className="option-group">
                  <label className="option-label">Summary Instructions (Optional)</label>
                  <textarea
                    className="summary-instructions-input"
                    placeholder="Specify how you want the conversation summarized (e.g., 'Focus on key decisions', 'Include action items', 'Highlight technical details', etc.)"
                    value={summaryInstructions}
                    onChange={(e) => setSummaryInstructions(e.target.value)}
                    rows={2}
                  />
                  <small>Provide specific instructions for how the summary should be generated</small>
                </div>
              )}

              <div className="option-group">
                <label className="checkbox-option">
                  <input
                    type="checkbox"
                    checked={preserveRoles}
                    onChange={(e) => setPreserveRoles(e.target.checked)}
                  />
                  <span>Preserve message roles</span>
                  <small>Keep original user/assistant/system roles intact</small>
                </label>
              </div>

              <div className="option-group">
                <label className="option-label">Additional Context (Optional)</label>
                <textarea
                  className="context-input"
                  placeholder="Add extra context, instructions, or information to include with the transferred messages..."
                  value={additionalContext}
                  onChange={(e) => setAdditionalContext(e.target.value)}
                  rows={3}
                />
                <small>This context will be added as a system message before the transferred content</small>
              </div>

              {selectedTargetPane && (
                <div className="target-preview">
                  <h5>Target Pane Preview</h5>
                  <div className="target-details">
                    <div className="detail-row">
                      <span className="detail-label">Current messages:</span>
                      <span className="detail-value">{selectedTargetPane.messages.length}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">After transfer:</span>
                      <span className="detail-value">
                        {transferMode === 'replace' 
                          ? selectedContent.messageIds.length
                          : transferMode === 'summarize'
                          ? selectedTargetPane.messages.length + 1
                          : selectedTargetPane.messages.length + selectedContent.messageIds.length
                        } messages
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Estimated cost impact:</span>
                      <span className="detail-value">
                        +${(selectedContent.text.length * (selectedTargetPane.modelInfo.costPer1kTokens || 0) / 4000).toFixed(4)}
                      </span>
                    </div>

                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="menu-actions">
          <button
            className="cancel-btn"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className={`send-btn ${canSend && !isGeneratingSummary ? 'enabled' : 'disabled'}`}
            onClick={handleSendTo}
            disabled={!canSend || isGeneratingSummary}
          >
            {isGeneratingSummary ? (
              <>
                <span className="loading-spinner">⏳</span>
                Generating Summary...
              </>
            ) : (
              transferMode === 'append' ? 'Send Messages' : 
              transferMode === 'replace' ? 'Replace & Send' : 
              'Generate Summary'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};