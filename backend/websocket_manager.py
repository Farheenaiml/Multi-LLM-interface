"""
Enhanced WebSocket connection manager with error handling and reconnection logic
Manages real-time streaming connections with graceful degradation
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, Any, Callable
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from models import StreamEvent
from error_handler import error_handler


class ConnectionInfo:
    """Information about a WebSocket connection"""
    
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.connected_at = datetime.now()
        self.last_ping = datetime.now()
        self.failed_sends = 0
        self.is_alive = True


class EnhancedConnectionManager:
    """
    Enhanced WebSocket connection manager with error handling,
    heartbeat monitoring, and graceful degradation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connections: Dict[str, ConnectionInfo] = {}
        self.session_connections: Dict[str, Set[str]] = {}  # session_id -> connection_ids
        self.heartbeat_interval = 30  # seconds
        self.max_failed_sends = 3
        self.cleanup_interval = 300  # 5 minutes
        self._background_tasks_started = False
    
    def _start_background_tasks(self):
        """Start background tasks if not already started"""
        if not self._background_tasks_started:
            asyncio.create_task(self._heartbeat_monitor())
            asyncio.create_task(self._cleanup_stale_connections())
            self._background_tasks_started = True
    
    async def connect(self, websocket: WebSocket, session_id: str) -> str:
        """
        Accept WebSocket connection and register it.
        
        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            
        Returns:
            str: Connection ID
        """
        try:
            await websocket.accept()
            
            # Start background tasks on first connection
            self._start_background_tasks()
            
            connection_id = str(uuid4())
            connection_info = ConnectionInfo(websocket, session_id)
            
            self.connections[connection_id] = connection_info
            
            if session_id not in self.session_connections:
                self.session_connections[session_id] = set()
            self.session_connections[session_id].add(connection_id)
            
            error_handler._log_structured(
                "info",
                "WebSocket connected",
                session_id=session_id,
                connection_id=connection_id,
                total_connections=len(self.connections)
            )
            
            return connection_id
            
        except Exception as e:
            error_handler._log_structured(
                "error",
                f"Failed to accept WebSocket connection: {str(e)}",
                session_id=session_id
            )
            raise
    
    def disconnect(self, connection_id: str, reason: str = "client_disconnect"):
        """
        Disconnect and clean up a WebSocket connection.
        
        Args:
            connection_id: Connection identifier
            reason: Reason for disconnection
        """
        if connection_id not in self.connections:
            return
        
        connection_info = self.connections[connection_id]
        session_id = connection_info.session_id
        
        # Remove from connections
        del self.connections[connection_id]
        
        # Remove from session connections
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        error_handler._log_structured(
            "info",
            "WebSocket disconnected",
            session_id=session_id,
            connection_id=connection_id,
            reason=reason,
            duration=(datetime.now() - connection_info.connected_at).total_seconds()
        )
    
    async def send_event(self, session_id: str, event: StreamEvent) -> bool:
        """
        Send event to all connections for a session with error handling.
        
        Args:
            session_id: Session identifier
            event: Event to send
            
        Returns:
            bool: True if sent to at least one connection
        """
        print(f"🚀 Attempting to send event: {event.type} to session: {session_id}")
        
        if session_id not in self.session_connections:
            print(f"❌ No connections found for session: {session_id}")
            print(f"📋 Available sessions: {list(self.session_connections.keys())}")
            error_handler._log_structured(
                "warning",
                "No connections found for session",
                session_id=session_id,
                event_type=event.type
            )
            return False
        
        connection_ids = list(self.session_connections[session_id])
        successful_sends = 0
        failed_connections = []
        
        for connection_id in connection_ids:
            if connection_id not in self.connections:
                failed_connections.append(connection_id)
                continue
            
            connection_info = self.connections[connection_id]
            
            try:
                event_data = event.model_dump_json()
                print(f"📤 Sending WebSocket event: {event_data[:100]}...")
                await connection_info.websocket.send_text(event_data)
                
                # Reset failed sends counter on success
                connection_info.failed_sends = 0
                successful_sends += 1
                
                print(f"✅ Event sent successfully to connection: {connection_id}")
                
                error_handler._log_structured(
                    "debug",
                    "Event sent successfully",
                    session_id=session_id,
                    connection_id=connection_id,
                    event_type=event.type,
                    pane_id=event.pane_id
                )
                
            except WebSocketDisconnect:
                error_handler._log_structured(
                    "info",
                    "WebSocket disconnected during send",
                    session_id=session_id,
                    connection_id=connection_id
                )
                failed_connections.append(connection_id)
                
            except Exception as e:
                connection_info.failed_sends += 1
                
                error_handler._log_structured(
                    "warning",
                    f"Failed to send event: {str(e)}",
                    session_id=session_id,
                    connection_id=connection_id,
                    event_type=event.type,
                    failed_sends=connection_info.failed_sends
                )
                
                # Mark connection as dead if too many failures
                if connection_info.failed_sends >= self.max_failed_sends:
                    connection_info.is_alive = False
                    failed_connections.append(connection_id)
        
        # Clean up failed connections
        for connection_id in failed_connections:
            self.disconnect(connection_id, "send_failure")
        
        if successful_sends == 0 and connection_ids:
            error_handler._log_structured(
                "error",
                "Failed to send event to any connection",
                session_id=session_id,
                event_type=event.type,
                attempted_connections=len(connection_ids)
            )
        
        return successful_sends > 0
    
    async def send_to_connection(self, connection_id: str, data: Dict[str, Any]) -> bool:
        """
        Send data to a specific connection.
        
        Args:
            connection_id: Connection identifier
            data: Data to send
            
        Returns:
            bool: True if sent successfully
        """
        if connection_id not in self.connections:
            return False
        
        connection_info = self.connections[connection_id]
        
        try:
            await connection_info.websocket.send_text(json.dumps(data))
            connection_info.failed_sends = 0
            return True
            
        except Exception as e:
            connection_info.failed_sends += 1
            
            error_handler._log_structured(
                "warning",
                f"Failed to send to connection: {str(e)}",
                connection_id=connection_id,
                session_id=connection_info.session_id,
                failed_sends=connection_info.failed_sends
            )
            
            if connection_info.failed_sends >= self.max_failed_sends:
                self.disconnect(connection_id, "send_failure")
            
            return False
    
    async def broadcast_to_all(self, data: Dict[str, Any]) -> int:
        """
        Broadcast data to all active connections.
        
        Args:
            data: Data to broadcast
            
        Returns:
            int: Number of successful sends
        """
        successful_sends = 0
        failed_connections = []
        
        for connection_id, connection_info in self.connections.items():
            try:
                await connection_info.websocket.send_text(json.dumps(data))
                successful_sends += 1
                
            except Exception:
                failed_connections.append(connection_id)
        
        # Clean up failed connections
        for connection_id in failed_connections:
            self.disconnect(connection_id, "broadcast_failure")
        
        return successful_sends
    
    async def ping_connection(self, connection_id: str) -> bool:
        """
        Send ping to a specific connection.
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            bool: True if ping sent successfully
        """
        ping_data = {
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }
        
        success = await self.send_to_connection(connection_id, ping_data)
        
        if success and connection_id in self.connections:
            self.connections[connection_id].last_ping = datetime.now()
        
        return success
    
    def get_session_connections(self, session_id: str) -> int:
        """Get number of active connections for a session"""
        return len(self.session_connections.get(session_id, set()))
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        total_connections = len(self.connections)
        active_sessions = len(self.session_connections)
        
        # Calculate connection health
        healthy_connections = sum(
            1 for conn in self.connections.values()
            if conn.is_alive and conn.failed_sends == 0
        )
        
        return {
            "total_connections": total_connections,
            "healthy_connections": healthy_connections,
            "active_sessions": active_sessions,
            "unhealthy_connections": total_connections - healthy_connections,
            "average_connection_age": self._calculate_average_connection_age()
        }
    
    def _calculate_average_connection_age(self) -> float:
        """Calculate average connection age in seconds"""
        if not self.connections:
            return 0.0
        
        now = datetime.now()
        total_age = sum(
            (now - conn.connected_at).total_seconds()
            for conn in self.connections.values()
        )
        
        return total_age / len(self.connections)
    
    async def _heartbeat_monitor(self):
        """Background task to monitor connection health"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                stale_connections = []
                now = datetime.now()
                
                for connection_id, connection_info in self.connections.items():
                    # Check if connection is stale
                    time_since_ping = (now - connection_info.last_ping).total_seconds()
                    
                    if time_since_ping > self.heartbeat_interval * 2:
                        # Try to ping the connection
                        if not await self.ping_connection(connection_id):
                            stale_connections.append(connection_id)
                
                # Clean up stale connections
                for connection_id in stale_connections:
                    self.disconnect(connection_id, "heartbeat_timeout")
                
                if stale_connections:
                    error_handler._log_structured(
                        "info",
                        f"Cleaned up {len(stale_connections)} stale connections",
                        stale_count=len(stale_connections)
                    )
                
            except Exception as e:
                error_handler._log_structured(
                    "error",
                    f"Heartbeat monitor error: {str(e)}"
                )
    
    async def _cleanup_stale_connections(self):
        """Background task to clean up stale connection data"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Clean up empty session connection sets
                empty_sessions = [
                    session_id for session_id, conn_set in self.session_connections.items()
                    if not conn_set
                ]
                
                for session_id in empty_sessions:
                    del self.session_connections[session_id]
                
                if empty_sessions:
                    error_handler._log_structured(
                        "info",
                        f"Cleaned up {len(empty_sessions)} empty session connection sets",
                        cleaned_sessions=len(empty_sessions)
                    )
                
            except Exception as e:
                error_handler._log_structured(
                    "error",
                    f"Cleanup task error: {str(e)}"
                )


# Global connection manager instance
connection_manager = EnhancedConnectionManager()