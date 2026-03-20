"""
WebSocket manager for real-time chat messaging.
Handles connections, message broadcasting, and chat state management.
"""

from typing import Callable, Dict, Set
from datetime import datetime, timezone
from dataclasses import dataclass
import json


@dataclass
class ChatMessage:
    """Represents a chat message for WebSocket events."""
    message_id: int
    sender_id: int
    conversation_id: int
    content: str
    created_at: str


class ChatWebSocketManager:
    """Manages WebSocket connections and chat events for real-time communication."""
    
    def __init__(self):
        """Initialize connection tracking."""
        # Maps user_id -> set of sid (socket.io session IDs)
        self.user_connections: Dict[int, Set[str]] = {}
        # Maps sid -> user_id
        self.connection_user: Dict[str, int] = {}

    def connect(self, sid: str, user_id: int) -> None:
        """Register a new WebSocket connection."""
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        
        self.user_connections[user_id].add(sid)
        self.connection_user[sid] = user_id
        print(f"✓ User {user_id} connected (sid: {sid})")

    def disconnect(self, sid: str) -> None:
        """Unregister a WebSocket connection."""
        if sid not in self.connection_user:
            return
        
        user_id = self.connection_user[sid]
        del self.connection_user[sid]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(sid)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        print(f"✗ User {user_id} disconnected (sid: {sid})")

    def get_user_sids(self, user_id: int) -> Set[str]:
        """Get all socket IDs for a specific user."""
        return self.user_connections.get(user_id, set())

    def is_user_online(self, user_id: int) -> bool:
        """Check if user has any active connections."""
        return user_id in self.user_connections and len(self.user_connections[user_id]) > 0

    def get_online_users(self) -> list[int]:
        """Get list of all online users."""
        return list(self.user_connections.keys())

    def get_conversation_users(self, conversation_members: list[int]) -> list[int]:
        """Get which conversation members are currently online."""
        return [uid for uid in conversation_members if self.is_user_online(uid)]


# Global WebSocket manager instance
chat_ws_manager = ChatWebSocketManager()
