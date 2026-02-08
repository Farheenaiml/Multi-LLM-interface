import React, { useEffect, useRef, useState } from 'react';
import { createRoot, Root } from 'react-dom/client';
import { useAppStore } from '../../store';
import './PaneGrid.css';
import '../ChatPane/ChatPane.css';

// New imports
import { ChatPane } from '../ChatPane';
import { SelectedContent } from '../../types';

// Import WinBox CSS
import 'winbox/dist/css/winbox.min.css';

// WinBox constructor type
interface WinBoxConstructor {
  new(options: any): any;
}

// Use a simple approach - load WinBox from the installed npm package
let WinBoxConstructor: WinBoxConstructor | null = null;

// Initialize WinBox on first use
const initWinBox = async (): Promise<WinBoxConstructor | null> => {
  if (WinBoxConstructor) {
    return WinBoxConstructor;
  }

  try {
    // Use dynamic import which should work better with Vite
    const winboxModule = await import('winbox');

    // Log what we got to debug
    console.log('WinBox module imported:', winboxModule);

    // Try to find the constructor in different places
    const possibleConstructors = [
      winboxModule.default,
      winboxModule,
      (winboxModule as any).WinBox,
      (window as any).WinBox
    ];

    for (const constructor of possibleConstructors) {
      if (constructor && typeof constructor === 'function') {
        console.log('Found WinBox constructor:', constructor);
        WinBoxConstructor = constructor as WinBoxConstructor;
        return WinBoxConstructor;
      }
    }

    console.error('No valid WinBox constructor found in:', possibleConstructors);
    return null;
  } catch (error) {
    console.error('Failed to import WinBox:', error);
    return null;
  }
};

export interface WindowManagerConfig {
  layout: 'grid' | 'tabs' | 'split';
  resizable: boolean;
  closable: boolean;
  draggable: boolean;
}

export interface PaneGridProps {
  windowManagerConfig?: WindowManagerConfig;
  onPaneAction?: (action: PaneAction) => void;
  onSendMessage?: (paneId: string, message: string, images?: string[]) => void;
  isCompareMode?: boolean;
  selectedPanes?: [string, string] | null;
  onArrangeWindows?: () => void;
  onMinimizeAll?: () => void;
  onCloseAll?: () => void;
}

export interface PaneAction {
  type: 'close' | 'select' | 'sendTo';
  paneId: string;
  data?: any;
}

interface PaneWindowContentProps {
  pane: any;
  onSendMessage?: (paneId: string, message: string, images?: string[]) => void;
  onPaneAction?: (action: PaneAction) => void;
  isCompareMode?: boolean;
}

const PaneWindowContent: React.FC<PaneWindowContentProps> = ({
  pane,
  onSendMessage,
  onPaneAction,
  isCompareMode
}) => {
  const [currentSelection, setCurrentSelection] = useState<SelectedContent>({ messageIds: [], text: '' });

  const handleSelectContent = (content: SelectedContent) => {
    setCurrentSelection(content);
    // Optional: propagate selection change if needed
    // onPaneAction?.({ type: 'select', paneId: pane.id, data: content });
  };

  const handleSendTo = (paneId: string) => {
    onPaneAction?.({
      type: 'sendTo',
      paneId: paneId,
      data: currentSelection
    });
  };

  return (
    <ChatPane
      pane={pane}
      onSendMessage={onSendMessage}
      onSelectContent={handleSelectContent}
      onSendTo={handleSendTo}
      isCompareMode={isCompareMode}
    />
  );
};

export const PaneGrid: React.FC<PaneGridProps> = ({
  onPaneAction,
  onSendMessage,
  isCompareMode = false,
  selectedPanes = null,
  onArrangeWindows,
  onMinimizeAll,
  onCloseAll
}) => {
  const {
    activePanes,
    registerWindow,
    unregisterWindow,
    removePane
  } = useAppStore();

  const containerRef = useRef<HTMLDivElement>(null);
  const windowsRef = useRef<Map<string, any>>(new Map());
  const rootsRef = useRef<Map<string, Root>>(new Map());

  useEffect(() => {
    const initializeWindows = async () => {
      // Create windows for new panes
      for (const pane of Object.values(activePanes)) {
        if (!windowsRef.current.has(pane.id)) {
          await createWindow(pane);
        }
      }

      // Remove windows for deleted panes
      windowsRef.current.forEach((window, paneId) => {
        if (!activePanes[paneId]) {
          window.close();
          const root = rootsRef.current.get(paneId);
          if (root) {
            root.unmount();
            rootsRef.current.delete(paneId);
          }
          windowsRef.current.delete(paneId);
          unregisterWindow(paneId);
        }
      });
    };

    initializeWindows();
  }, [activePanes, unregisterWindow]);

  const createWindow = async (pane: any) => {
    if (!containerRef.current) return;

    const WinBoxConstructor = await initWinBox();
    if (!WinBoxConstructor) {
      console.error('WinBox constructor not available');
      return;
    }

    const windowCount = windowsRef.current.size;
    const offsetX = (windowCount % 3) * 50;
    const offsetY = Math.floor(windowCount / 3) * 50;

    // Create a container div for the React component
    const contentDiv = document.createElement('div');
    contentDiv.style.height = '100%';
    contentDiv.style.overflow = 'hidden';

    // Create React root
    const root = createRoot(contentDiv);
    rootsRef.current.set(pane.id, root);

    const winbox = new WinBoxConstructor({
      title: `${pane.modelInfo?.provider || 'Unknown'}:${pane.modelInfo?.name || 'Unknown'} `,
      width: 450,
      height: 600,
      x: 100 + offsetX,
      y: 100 + offsetY,
      root: containerRef.current,
      class: ['chat-pane-window', isCompareMode ? 'compare-mode' : ''].filter(Boolean),
      mount: contentDiv,
      onclose: () => {
        const root = rootsRef.current.get(pane.id);
        if (root) {
          root.unmount();
          rootsRef.current.delete(pane.id);
        }
        windowsRef.current.delete(pane.id);
        unregisterWindow(pane.id);
        removePane(pane.id);
        onPaneAction?.({ type: 'close', paneId: pane.id });
        return false; // Prevent default close behavior
      },
      onresize: (_width: number, _height: number) => {
        // Handle window resize if needed
      },
      onmove: (_x: number, _y: number) => {
        // Handle window move if needed
      },
      onmaximize: () => {
        // Custom maximize behavior - resize to 1/3 of screen instead of full screen
        const containerRect = containerRef.current?.getBoundingClientRect();
        if (containerRect) {
          const targetWidth = Math.floor(containerRect.width / 3);
          const targetHeight = Math.floor(containerRect.height * 0.8); // 80% of height
          const targetX = 50;
          const targetY = 50;

          // Resize and position the window
          winbox.resize(targetWidth, targetHeight);
          winbox.move(targetX, targetY);
        }
        return false; // Prevent default maximize behavior
      }
    });

    // Render React component into the content div
    // Render React component into the content div
    renderPaneContent(pane);

    windowsRef.current.set(pane.id, winbox);
    registerWindow(pane.id, winbox);
  };

  const renderPaneContent = (pane: any) => {
    const root = rootsRef.current.get(pane.id);
    if (!root) return;

    root.render(
      <PaneWindowContent
        pane={pane}
        onSendMessage={onSendMessage}
        onPaneAction={onPaneAction}
        isCompareMode={isCompareMode}
      />
    );
  };





  // Expose functions to window for button clicks


  // Update window content when pane data changes
  useEffect(() => {
    console.log('🔄 PaneGrid: useEffect triggered! activePanes:', Object.keys(activePanes).length);
    console.log('🔄 Available pane IDs:', Object.keys(activePanes));
    console.log('🔄 Window IDs:', Array.from(windowsRef.current.keys()));

    // Force update all windows
    Object.values(activePanes).forEach(pane => {
      const window = windowsRef.current.get(pane.id);
      if (window && window.body) {
        console.log('✅ PaneGrid: Updating pane', pane.id, 'with', pane.messages.length, 'messages');
        console.log('📝 Messages:', pane.messages.map(m => `${m.role}: ${m.content.substring(0, 30)}...`));
        renderPaneContent(pane);
      } else {
        console.log('❌ PaneGrid: Window not found for pane', pane.id);
      }
    });
  }, [activePanes, isCompareMode, selectedPanes]);



  // Update window styling for compare mode
  useEffect(() => {
    windowsRef.current.forEach((window, paneId) => {
      const isInCompare = selectedPanes?.includes(paneId) || false;
      const windowElement = window.dom;

      if (windowElement) {
        if (isInCompare) {
          windowElement.classList.add('compare-mode');
        } else {
          windowElement.classList.remove('compare-mode');
        }
      }
    });
  }, [selectedPanes]);

  // Window management functions
  const arrangeWindows = () => {
    const windows = Array.from(windowsRef.current.values());
    const cols = Math.ceil(Math.sqrt(windows.length));
    const rows = Math.ceil(windows.length / cols);
    const windowWidth = Math.floor((window.innerWidth - 100) / cols);
    const windowHeight = Math.floor((window.innerHeight - 100) / rows);

    windows.forEach((winbox, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      const x = 50 + col * windowWidth;
      const y = 50 + row * windowHeight;

      winbox.resize(windowWidth - 20, windowHeight - 20);
      winbox.move(x, y);
    });
  };

  const minimizeAllWindows = () => {
    windowsRef.current.forEach(winbox => {
      winbox.minimize();
    });
  };

  const closeAllWindows = () => {
    windowsRef.current.forEach(winbox => {
      winbox.close();
    });
  };

  // Expose window management functions
  useEffect(() => {
    if (onArrangeWindows) {
      (window as any).arrangeWindows = arrangeWindows;
    }
    if (onMinimizeAll) {
      (window as any).minimizeAllWindows = minimizeAllWindows;
    }
    if (onCloseAll) {
      (window as any).closeAllWindows = closeAllWindows;
    }

    return () => {
      delete (window as any).arrangeWindows;
      delete (window as any).minimizeAllWindows;
      delete (window as any).closeAllWindows;
    };
  }, [onArrangeWindows, onMinimizeAll, onCloseAll]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      windowsRef.current.forEach(window => {
        window.close();
      });
      windowsRef.current.clear();
    };
  }, []);

  const paneCount = Object.keys(activePanes).length;

  return (
    <div className="pane-grid">
      <div
        ref={containerRef}
        className="window-manager-container"
        style={{
          width: '100%',
          height: '100%',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {paneCount === 0 && (
          <div className="no-panes-message">
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <h3>No Active Panes</h3>
              <p>Start a broadcast to create chat panes and see responses from multiple LLMs.</p>
              <div className="empty-hint">
                <small>Use the Broadcast Bar above to select models and send your first prompt.</small>
              </div>
            </div>
          </div>
        )}
      </div>

      {isCompareMode && selectedPanes && (
        <div className="compare-mode-indicator">
          <div className="compare-status">
            <span className="compare-icon">⚖️</span>
            <span className="compare-text">
              Comparing {selectedPanes.length} panes
            </span>
          </div>
        </div>
      )}


    </div>
  );
};