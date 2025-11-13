"""
Session Manager for handling session state and persistence
Manages active sessions, panes, and conversation history
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from models import Session, ChatPane, Message

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages session state and persistence.
    
    Handles creation, retrieval, and updates of sessions and their
    associated panes and conversation history.
    """
    
    def __init__(self):
        # In-memory storage (would be replaced with database in production)
        self.sessions: Dict[str, Session] = {}
        self.max_sessions = 1000  # Limit to prevent memory issues
    
    def create_session(self, session_id: Optional[str] = None, name: Optional[str] = None) -> Session:
        """
        Create a new session.
        
        Args:
            session_id: Optional session ID (generates UUID if not provided)
            name: Optional session name
            
        Returns:
            Created session
        """
        if not session_id:
            session_id = str(uuid4())
        
        session = Session(
            id=session_id,
            name=name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        self.sessions[session_id] = session
        
        # Clean up old sessions if we exceed the limit
        if len(self.sessions) > self.max_sessions:
            self._cleanup_old_sessions()
        
        logger.info(f"Created session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session if found, None otherwise
        """
        return self.sessions.get(session_id)
    
    def get_or_create_session(self, session_id: str, name: Optional[str] = None) -> Session:
        """
        Get existing session or create new one.
        
        Args:
            session_id: Session identifier
            name: Optional session name for new sessions
            
        Returns:
            Existing or newly created session
        """
        session = self.get_session(session_id)
        if session:
            return session
        
        return self.create_session(session_id, name)
    
    def update_session(self, session: Session) -> bool:
        """
        Update an existing session.
        
        Args:
            session: Session to update
            
        Returns:
            True if session was updated, False if not found
        """
        if session.id not in self.sessions:
            return False
        
        session.updated_at = datetime.now()
        self.sessions[session.id] = session
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        
        return False
    
    def list_sessions(self, limit: int = 50, offset: int = 0) -> List[Session]:
        """
        List sessions with pagination.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of sessions
        """
        all_sessions = list(self.sessions.values())
        
        # Sort by updated_at descending (most recent first)
        all_sessions.sort(key=lambda s: s.updated_at, reverse=True)
        
        return all_sessions[offset:offset + limit]
    
    def add_pane_to_session(self, session_id: str, pane: ChatPane) -> bool:
        """
        Add a pane to a session.
        
        Args:
            session_id: Session identifier
            pane: Pane to add
            
        Returns:
            True if pane was added, False if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.panes.append(pane)
        session.updated_at = datetime.now()
        
        return True
    
    def remove_pane_from_session(self, session_id: str, pane_id: str) -> bool:
        """
        Remove a pane from a session.
        
        Args:
            session_id: Session identifier
            pane_id: Pane identifier
            
        Returns:
            True if pane was removed, False if not found
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        original_count = len(session.panes)
        session.panes = [p for p in session.panes if p.id != pane_id]
        
        if len(session.panes) < original_count:
            session.updated_at = datetime.now()
            return True
        
        return False
    
    def get_pane(self, session_id: str, pane_id: str) -> Optional[ChatPane]:
        """
        Get a specific pane from a session.
        
        Args:
            session_id: Session identifier
            pane_id: Pane identifier
            
        Returns:
            Pane if found, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        return next((p for p in session.panes if p.id == pane_id), None)
    
    def add_message_to_pane(self, session_id: str, pane_id: str, message: Message) -> bool:
        """
        Add a message to a specific pane.
        
        Args:
            session_id: Session identifier
            pane_id: Pane identifier
            message: Message to add
            
        Returns:
            True if message was added, False if pane not found
        """
        pane = self.get_pane(session_id, pane_id)
        if not pane:
            return False
        
        pane.messages.append(message)
        
        # Update session timestamp
        session = self.get_session(session_id)
        if session:
            session.updated_at = datetime.now()
        
        return True
    
    def get_session_stats(self) -> Dict[str, int]:
        """
        Get statistics about managed sessions.
        
        Returns:
            Dictionary with session statistics
        """
        active_sessions = sum(1 for s in self.sessions.values() if s.status == "active")
        total_panes = sum(len(s.panes) for s in self.sessions.values())
        total_messages = sum(
            len(p.messages) for s in self.sessions.values() for p in s.panes
        )
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "total_panes": total_panes,
            "total_messages": total_messages
        }
    
    def _cleanup_old_sessions(self):
        """
        Clean up old sessions to prevent memory issues.
        Removes oldest sessions that are not active.
        """
        # Get sessions sorted by updated_at (oldest first)
        sessions_by_age = sorted(
            self.sessions.values(),
            key=lambda s: s.updated_at
        )
        
        # Remove oldest non-active sessions until we're under the limit
        sessions_to_remove = []
        for session in sessions_by_age:
            if len(self.sessions) - len(sessions_to_remove) <= self.max_sessions * 0.8:
                break
            
            if session.status != "active":
                sessions_to_remove.append(session.id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            logger.info(f"Cleaned up old session: {session_id}")
    
    def archive_session(self, session_id: str) -> bool:
        """
        Archive a session (mark as archived).
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was archived, False if not found
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.status = "archived"
        session.updated_at = datetime.now()
        
        logger.info(f"Archived session: {session_id}")
        return True
    
    def restore_session(self, session_id: str) -> bool:
        """
        Restore an archived session (mark as active).
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was restored, False if not found
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.status = "active"
        session.updated_at = datetime.now()
        
        logger.info(f"Restored session: {session_id}")
        return True