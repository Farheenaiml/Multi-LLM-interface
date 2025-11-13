import React from 'react';
import { useAppStore } from '../store';
import './Templates.css';

export const Templates: React.FC = () => {
  const { pipelineTemplates, removeTemplate } = useAppStore();

  const handleDeleteTemplate = (templateId: string) => {
    if (window.confirm('Are you sure you want to delete this template?')) {
      removeTemplate(templateId);
    }
  };

  return (
    <div className="templates-page">
      <div className="page-header">
        <h2>Pipeline Templates</h2>
        <p>Manage and organize your reusable workflow templates.</p>
      </div>

      <div className="templates-content">
        {pipelineTemplates.length === 0 ? (
          <div className="empty-state">
            <div className="empty-message">
              <h3>No Pipeline Templates Yet</h3>
              <p>Create templates from your conversation sequences to quickly recreate effective workflows.</p>
              <div className="template-info">
                <h4>How to create templates:</h4>
                <ol>
                  <li>Complete a successful conversation sequence across multiple panes</li>
                  <li>Select the interactions you want to save</li>
                  <li>Click "Create Template" to save the workflow</li>
                  <li>Reuse templates to quickly recreate similar conversations</li>
                </ol>
              </div>
            </div>
          </div>
        ) : (
          <div className="template-grid">
            {pipelineTemplates.map(template => (
              <div key={template.id} className="template-card">
                <div className="template-header">
                  <h3>{template.name}</h3>
                  <div className="template-actions">
                    <button 
                      className="action-btn use-btn"
                      title="Use Template"
                    >
                      ▶️ Use
                    </button>
                    <button 
                      className="action-btn edit-btn"
                      title="Edit Template"
                    >
                      ✏️ Edit
                    </button>
                    <button 
                      className="action-btn delete-btn"
                      onClick={() => handleDeleteTemplate(template.id)}
                      title="Delete Template"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
                
                {template.description && (
                  <p className="template-description">{template.description}</p>
                )}
                
                <div className="template-details">
                  <div className="template-meta">
                    <span className="meta-item">
                      <strong>Steps:</strong> {template.steps.length}
                    </span>
                    <span className="meta-item">
                      <strong>Models:</strong> {template.modelConfigurations.length}
                    </span>
                    <span className="meta-item">
                      <strong>Used:</strong> {template.usageCount} times
                    </span>
                  </div>
                  
                  <div className="template-created">
                    Created: {template.createdAt.toLocaleDateString()}
                  </div>
                </div>
                
                <div className="template-preview">
                  <h4>Steps Preview:</h4>
                  <ol className="step-list">
                    {template.steps.slice(0, 3).map(step => (
                      <li key={step.order} className="step-item">
                        <span className="step-prompt">
                          {step.prompt.length > 60 
                            ? `${step.prompt.substring(0, 60)}...` 
                            : step.prompt
                          }
                        </span>
                        <span className="step-models">
                          → {step.targetModels.join(', ')}
                        </span>
                      </li>
                    ))}
                    {template.steps.length > 3 && (
                      <li className="step-item more-steps">
                        ... and {template.steps.length - 3} more steps
                      </li>
                    )}
                  </ol>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};