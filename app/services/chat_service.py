"""
Chat service - contains business logic and helper functions for chat operations.
Centralizes repeated operations and keeps the API layer clean.
"""

from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.model_user import User
from app.models.chat.model_conversation_member import ConversationMember
from app.schemas.chat import MessageStatusResponse, UserPresenceResponse, TypingIndicatorResponse


# Constants
TYPING_INDICATOR_MIN_TTL = 3
TYPING_INDICATOR_MAX_TTL = 30
MIN_GROUP_MEMBERS = 2
MIN_SEARCH_QUERY_LENGTH = 2

# Error messages
ERROR_USER_NOT_FOUND = "Użytkownik nie istnieje."
ERROR_NO_CONVERSATION_ACCESS = "Nie masz dostępu do tej rozmowy."
ERROR_MESSAGE_NOT_FOUND = "Wiadomość nie istnieje lub brak dostępu."
ERROR_CANNOT_MARK_OWN_MESSAGE = "Nadawca nie może oznaczyć własnej wiadomości."
ERROR_EMPTY_MESSAGE = "Treść wiadomości nie może być pusta."
ERROR_EMPTY_GROUP_NAME = "Nazwa grupy nie może być pusta."
ERROR_INSUFFICIENT_GROUP_MEMBERS = f"Grupa musi zawierać co najmniej {MIN_GROUP_MEMBERS} użytkowników."
ERROR_USERS_NOT_FOUND = "Nie znaleziono użytkowników o ID: {}."
ERROR_SAME_USER_CONVERSATION = "Nie możesz rozpocząć rozmowy z samym sobą."


# Global state for typing indicators
class _TypingState:
    """Thread-safe storage for typing indicator state."""
    def __init__(self):
        self._state: dict[tuple[int, int], datetime] = {}
        self._lock = Lock()
    
    def set_typing(self, conversation_id: int, user_id: int, ttl_seconds: int) -> None:
        """Set user as typing in conversation for specified duration."""
        expires_at = self._now_utc() + timedelta(seconds=ttl_seconds)
        with self._lock:
            self._state[(conversation_id, user_id)] = expires_at
    
    def clear_typing(self, conversation_id: int, user_id: int) -> None:
        """Clear typing indicator for user in conversation."""
        with self._lock:
            self._state.pop((conversation_id, user_id), None)
    
    def get_typing_users(self, conversation_id: int) -> list[int]:
        """Get list of users currently typing in conversation (non-expired entries)."""
        now = self._now_utc()
        self._cleanup_expired(now)
        
        with self._lock:
            return [
                user_id
                for (conv_id, user_id), expires_at in self._state.items()
                if conv_id == conversation_id and expires_at > now
            ]
    
    def _cleanup_expired(self, now: datetime) -> None:
        """Remove expired entries from typing state."""
        with self._lock:
            expired_keys = [
                key for key, expires_at in self._state.items()
                if expires_at <= now
            ]
            for key in expired_keys:
                self._state.pop(key, None)
    
    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(timezone.utc)


# Singleton instance
typing_state = _TypingState()


# Database queries utilities
def get_user_or_raise(db: Session, user_id: int) -> User:
    """Fetch user from database or raise 404 if not found."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
    return user


def ensure_conversation_member(db: Session, conversation_id: int, user_id: int) -> None:
    """Verify user is member of conversation or raise 403."""
    member = (
        db.query(ConversationMember)
        .filter(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail=ERROR_NO_CONVERSATION_ACCESS)


# Response builders
def build_message_status_response(message) -> MessageStatusResponse:
    """Convert message model to status response schema."""
    return MessageStatusResponse(
        message_id=message.id,
        sent=True,
        delivered=message.delivered_at is not None,
        read=bool(message.is_read),
        sent_at=message.created_at.isoformat(),
        delivered_at=message.delivered_at.isoformat() if message.delivered_at else None,
        read_at=message.read_at.isoformat() if message.read_at else None,
    )


def build_presence_response(user: User) -> UserPresenceResponse:
    """Convert user model to presence response schema."""
    return UserPresenceResponse(
        user_id=user.user_id,
        last_seen_at=_to_iso(user.last_seen_at),
    )


def build_typing_response(conversation_id: int, typing_user_ids: list[int]) -> TypingIndicatorResponse:
    """Build typing indicator response."""
    return TypingIndicatorResponse(
        conversation_id=conversation_id,
        typing_user_ids=typing_user_ids,
    )


# Utility functions
def _to_iso(value: datetime | None) -> str | None:
    """Convert datetime to ISO format string, or None if value is None."""
    return value.isoformat() if value else None


def validate_ttl_seconds(ttl_seconds: int) -> int:
    """Validate and normalize typing indicator TTL (time-to-live)."""
    return max(TYPING_INDICATOR_MIN_TTL, min(ttl_seconds, TYPING_INDICATOR_MAX_TTL))
