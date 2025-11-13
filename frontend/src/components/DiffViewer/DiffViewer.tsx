import React, { useMemo, useState } from 'react';
import { computeTextDiff, getPaneContentForComparison } from '../../utils/textDiff';
import './DiffViewer.css';

interface Message {
  id: string;
  role: string;
  content: string;
  timestamp: Date;
}

interface Pane {
  id: string;
  modelInfo: {
    name: string;
    provider: string;
  };
  messages: Message[];
}

interface DiffViewerProps {
  panes: Pane[];
  selectedPanes: [string, string] | null;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({
  panes,
  selectedPanes
}) => {
  // State for what content to compare
  const [comparisonContentMode, setComparisonContentMode] = useState<'latest' | 'all-assistant' | 'full-conversation'>('latest');
  // Get the selected panes for comparison
  const selectedPaneData = useMemo(() => {
    console.log('DiffViewer: selectedPanes changed', selectedPanes);
    console.log('DiffViewer: available panes', panes.map(p => ({ id: p.id, name: p.modelInfo?.name })));
    
    if (!selectedPanes || !panes || panes.length === 0) {
      console.log('DiffViewer: No selectedPanes or no panes available');
      return [];
    }
    
    const filtered = panes.filter(pane => selectedPanes.includes(pane.id));
    console.log('DiffViewer: filtered panes', filtered.map(p => ({ id: p.id, name: p.modelInfo?.name, messageCount: p.messages?.length })));
    return filtered;
  }, [panes, selectedPanes]);

  // Compute diff between the first two selected panes
  const diffResult = useMemo(() => {
    // console.log('DiffViewer: Computing diff, selectedPaneData.length:', selectedPaneData.length);
    
    if (selectedPaneData.length < 2) {
      console.log('DiffViewer: Not enough panes for comparison');
      return null;
    }
    
    const content1 = getPaneContentForComparison(selectedPaneData[0], comparisonContentMode);
    const content2 = getPaneContentForComparison(selectedPaneData[1], comparisonContentMode);
    
    // console.log('DiffViewer: Extracted content lengths:', { content1: content1?.length, content2: content2?.length });
    
    // Always compute diff, even if one or both contents are empty
    // The computeTextDiff function handles empty strings properly
    
    try {
      console.log('DiffViewer: Computing diff...');
      const result = computeTextDiff(content1, content2);
      console.log('DiffViewer: Diff result:', { segmentCount: result.segments.length, similarity: result.similarity });
      return result;
    } catch (error) {
      console.error('DiffViewer: Error computing diff', error);
      return null;
    }
  }, [selectedPaneData, comparisonContentMode]);



  if (!selectedPanes || selectedPanes.length < 2) {
    return (
      <div className="diff-viewer">
        <div className="diff-empty-state">
          <div className="empty-icon">⚖️</div>
          <h3>Select 2 panes to compare</h3>
          <p>Choose panes from the CompareBar to see differences between model responses.</p>
        </div>
      </div>
    );
  }

  if (!diffResult) {
    return (
      <div className="diff-viewer">
        <div className="diff-empty-state">
          <div className="empty-icon">📝</div>
          <h3>Error computing comparison</h3>
          <p>There was an error computing the diff. Check the console for details.</p>
        </div>
      </div>
    );
  }

  const renderSideBySideComparison = () => {
    const pane1 = selectedPaneData[0];
    const pane2 = selectedPaneData[1];
    const content1 = getPaneContentForComparison(pane1, comparisonContentMode);
    const content2 = getPaneContentForComparison(pane2, comparisonContentMode);

    return (
      <div className="side-by-side-comparison">
        <div className="comparison-pane">
          <div className="comparison-pane-header">
            <span className="comparison-model-name">{pane1.modelInfo.name}</span>
            <span className="comparison-provider">{pane1.modelInfo.provider}</span>
          </div>
          <div className="comparison-content">
            {content1 || <span className="no-content">No response available</span>}
          </div>
        </div>
        
        <div className="comparison-pane">
          <div className="comparison-pane-header">
            <span className="comparison-model-name">{pane2.modelInfo.name}</span>
            <span className="comparison-provider">{pane2.modelInfo.provider}</span>
          </div>
          <div className="comparison-content">
            {content2 || <span className="no-content">No response available</span>}
          </div>
        </div>
      </div>
    );
  };



  return (
    <div className="diff-viewer">
      <div className="diff-viewer-header">
        <div className="diff-title">
          <h3>Response Comparison</h3>
          <p>Comparing responses from {selectedPaneData[0]?.modelInfo.name} and {selectedPaneData[1]?.modelInfo.name}</p>
        </div>
        
        <div className="diff-controls">
          <div className="diff-mode-selector">
            <button
              className="mode-btn active"
              disabled
            >
              <span>📊</span>
              Side by Side
            </button>
          </div>
          
          <div className="content-mode-selector">
            <label className="content-mode-label">Compare:</label>
            <select 
              className="content-mode-select"
              value={comparisonContentMode}
              onChange={(e) => setComparisonContentMode(e.target.value as 'latest' | 'all-assistant' | 'full-conversation')}
            >
              <option value="latest">Latest Response Only</option>
              <option value="all-assistant">All Assistant Responses</option>
              <option value="full-conversation">Full Conversation</option>
            </select>
          </div>
          
          <div className="diff-info">
            {diffResult && (
              <span className="similarity-badge">
                {Math.round(diffResult.similarity * 100)}% similar
              </span>
            )}
          </div>
        </div>
      </div>
      
      <div className="diff-content">
        {renderSideBySideComparison()}
      </div>
    </div>
  );
};