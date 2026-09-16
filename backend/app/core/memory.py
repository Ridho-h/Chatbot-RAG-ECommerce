"""
Per-session conversation memory manager.
Stores conversation history per session with TTL-based cleanup.
Uses langchain_core message types for compatibility with LangGraph agents.
"""

import time
import threading
from typing import Optional

import structlog
from langchain_core.messages import HumanMessage, AIMessage

from app.config import settings

logger = structlog.get_logger(__name__)


class SessionMemoryManager:
    """
    Manages per-session conversation memory with automatic TTL expiry.

    Each session stores a windowed list of HumanMessage/AIMessage objects.
    Sessions expire after SESSION_TTL_SECONDS of inactivity.
    """

    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._window_size = settings.MEMORY_WINDOW_SIZE
        self._ttl = settings.SESSION_TTL_SECONDS

    def get_messages(self, session_id: str) -> list:
        """
        Get conversation message history for a session.

        Args:
            session_id: Unique session identifier.

        Returns:
            List of HumanMessage/AIMessage objects (windowed).
        """
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id]["last_access"] = time.time()
                return list(self._sessions[session_id]["messages"])

            # Create new session
            self._sessions[session_id] = {
                "messages": [],
                "last_access": time.time(),
                "created_at": time.time(),
            }
            logger.info("session_created", session_id=session_id)
            return []

    def add_exchange(self, session_id: str, user_msg: str, ai_msg: str) -> None:
        """
        Add a user/AI message pair to the session history.
        Maintains a sliding window of the last N exchanges.

        Args:
            session_id: Unique session identifier.
            user_msg: The user's message text.
            ai_msg: The AI's response text.
        """
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {
                    "messages": [],
                    "last_access": time.time(),
                    "created_at": time.time(),
                }

            messages = self._sessions[session_id]["messages"]
            messages.append(HumanMessage(content=user_msg))
            messages.append(AIMessage(content=ai_msg))

            # Keep only the last N exchanges (N * 2 messages)
            max_messages = self._window_size * 2
            if len(messages) > max_messages:
                self._sessions[session_id]["messages"] = messages[-max_messages:]

            self._sessions[session_id]["last_access"] = time.time()

    def clear_session(self, session_id: str) -> None:
        """Remove a specific session's memory."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                logger.info("session_cleared", session_id=session_id)

    def cleanup_expired(self) -> int:
        """
        Remove sessions that have been inactive beyond the TTL.

        Returns:
            Number of sessions removed.
        """
        now = time.time()
        expired = []

        with self._lock:
            for sid, data in self._sessions.items():
                if now - data["last_access"] > self._ttl:
                    expired.append(sid)

            for sid in expired:
                del self._sessions[sid]

        if expired:
            logger.info("sessions_expired", count=len(expired))

        return len(expired)

    def get_active_session_count(self) -> int:
        """Return the number of active sessions."""
        with self._lock:
            return len(self._sessions)

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get metadata about a session (for admin endpoints)."""
        with self._lock:
            if session_id not in self._sessions:
                return None
            data = self._sessions[session_id]
            return {
                "session_id": session_id,
                "created_at": data["created_at"],
                "last_access": data["last_access"],
                "message_count": len(data["messages"]),
            }

    def get_all_sessions_info(self) -> list[dict]:
        """Get info for all active sessions (admin endpoint)."""
        with self._lock:
            return [
                {
                    "session_id": sid,
                    "created_at": data["created_at"],
                    "last_access": data["last_access"],
                    "message_count": len(data["messages"]),
                }
                for sid, data in self._sessions.items()
            ]


# Singleton instance
memory_manager = SessionMemoryManager()
