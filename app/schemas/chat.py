from pydantic import BaseModel

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    content: str
    created_at: str
    delivered_at: str | None = None
    is_read: bool
    read_at: str | None = None

class ConversationStartResponse(BaseModel):
    """Odpowiedź na rozpoczęcie rozmowy z użytkownikiem."""
    conversation_id: int
    user_a_id: int
    user_b_id: int


class ConversationListItemResponse(BaseModel):
    id: int
    type: str
    created_at: str
    member_ids: list[int]


class MessageStatusResponse(BaseModel):
    message_id: int
    sent: bool
    delivered: bool
    read: bool
    sent_at: str
    delivered_at: str | None = None
    read_at: str | None = None


class UserPresenceResponse(BaseModel):
    user_id: int
    is_online: bool
    last_seen_at: str | None = None


class TypingIndicatorRequest(BaseModel):
    is_typing: bool
    ttl_seconds: int = 8


class TypingIndicatorResponse(BaseModel):
    conversation_id: int
    typing_user_ids: list[int]
