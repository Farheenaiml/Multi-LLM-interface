import { StreamEvent } from '../types';

export type WebSocketEventHandler = (event: StreamEvent) => void;
export type WebSocketStatusHandler = (status: 'connecting' | 'connected' | 'disconnected' | 'error') => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private sessionId: string;
  private eventHandlers: Set<WebSocketEventHandler> = new Set();
  private statusHandlers: Set<WebSocketStatusHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private reconnectTimer: number | null = null;
  private isManualClose = false;

  constructor(sessionId: string) {
    this.sessionId = sessionId;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.isManualClose = false;
        const wsUrl = this.getWebSocketUrl();
        this.ws = new WebSocket(wsUrl);
        
        this.notifyStatus('connecting');

        this.ws.onopen = () => {
          console.log(`WebSocket connected for session: ${this.sessionId}`);
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          this.notifyStatus('connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const streamEvent: StreamEvent = JSON.parse(event.data);
            // Convert timestamp string to Date object
            streamEvent.timestamp = new Date(streamEvent.timestamp);
            this.notifyEventHandlers(streamEvent);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log(`WebSocket closed for session: ${this.sessionId}`, event.code, event.reason);
          this.notifyStatus('disconnected');
          
          if (!this.isManualClose && this.shouldReconnect()) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error(`WebSocket error for session: ${this.sessionId}`, error);
          this.notifyStatus('error');
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.isManualClose = true;
    this.clearReconnectTimer();
    
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
  }

  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected. Cannot send data:', data);
    }
  }

  onEvent(handler: WebSocketEventHandler): () => void {
    this.eventHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.eventHandlers.delete(handler);
    };
  }

  onStatus(handler: WebSocketStatusHandler): () => void {
    this.statusHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.statusHandlers.delete(handler);
    };
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = import.meta.env.VITE_BACKEND_PORT || '5000'; // Fixed: backend runs on 5000
    return `${protocol}//${host}:${port}/ws/${this.sessionId}`;
  }

  private notifyEventHandlers(event: StreamEvent): void {
    this.eventHandlers.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        console.error('Error in WebSocket event handler:', error);
      }
    });
  }

  private notifyStatus(status: 'connecting' | 'connected' | 'disconnected' | 'error'): void {
    this.statusHandlers.forEach(handler => {
      try {
        handler(status);
      } catch (error) {
        console.error('Error in WebSocket status handler:', error);
      }
    });
  }

  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.maxReconnectAttempts;
  }

  private scheduleReconnect(): void {
    this.clearReconnectTimer();
    
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts), 30000);
    console.log(`Scheduling WebSocket reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);
    
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectAttempts++;
      this.connect().catch(error => {
        console.error('WebSocket reconnect failed:', error);
        if (this.shouldReconnect()) {
          this.scheduleReconnect();
        }
      });
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}

// WebSocket Manager for handling multiple sessions
export class WebSocketManager {
  private clients: Map<string, WebSocketClient> = new Map();

  getClient(sessionId: string): WebSocketClient {
    if (!this.clients.has(sessionId)) {
      const client = new WebSocketClient(sessionId);
      this.clients.set(sessionId, client);
    }
    return this.clients.get(sessionId)!;
  }

  async connectSession(sessionId: string): Promise<WebSocketClient> {
    const client = this.getClient(sessionId);
    if (!client.isConnected()) {
      await client.connect();
    }
    return client;
  }

  disconnectSession(sessionId: string): void {
    const client = this.clients.get(sessionId);
    if (client) {
      client.disconnect();
      this.clients.delete(sessionId);
    }
  }

  disconnectAll(): void {
    this.clients.forEach((client) => {
      client.disconnect();
    });
    this.clients.clear();
  }

  isSessionConnected(sessionId: string): boolean {
    const client = this.clients.get(sessionId);
    return client?.isConnected() ?? false;
  }
}

// Global WebSocket manager instance
export const wsManager = new WebSocketManager();