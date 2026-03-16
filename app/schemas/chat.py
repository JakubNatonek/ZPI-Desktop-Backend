from pydantic import BaseModel

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    content: str
    created_at: str
    is_read: bool

class ConversationStartResponse(BaseModel):
    """Odpowiedź na rozpoczęcie rozmowy z użytkownikiem."""
    conversation_id: int
    user_a_id: int
    user_b_id: int
