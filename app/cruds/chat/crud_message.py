from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.chat.model_message import Message
from app.models.chat.model_conversation_member import ConversationMember


def get_messages_for_conversation(db: Session, conversation_id: int, before_id: int | None = None, limit: int = 25) -> list[Message]:
    """
    Pobierz wiadomości dla danej rozmowy z obsługą paginacji (cursor-based).
    Zwraca najnowsze `limit` wiadomości, starsze niż `before_id` (jeśli podano).
    Wiadomości są zwracane w kolejności chronologicznej (od najstarszej do najnowszej w ramach paczki).
    """
    query = db.query(Message).filter(Message.conversation_id == conversation_id)
    
    if before_id is not None:
        query = query.filter(Message.id < before_id)
        
    # Pobieramy najnowsze przed `before_id` (dlatego desc())
    messages = query.order_by(Message.id.desc()).limit(limit).all()
    
    # Odwracamy z powrotem, aby frontend dostał chronologicznie (od góry do dołu)
    messages.reverse()
    return messages


def get_message_for_user(db: Session, message_id: int, user_id: int) -> Message | None:
    """Pobierz wiadomość, jeśli użytkownik należy do konwersacji."""
    return (
        db.query(Message)
        .join(
            ConversationMember,
            ConversationMember.conversation_id == Message.conversation_id,
        )
        .filter(
            Message.id == message_id,
            ConversationMember.user_id == user_id,
        )
        .first()
    )


def mark_message_delivered(db: Session, message: Message) -> Message:
    if message.delivered_at is None:
        message.delivered_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(message)
    return message


def mark_message_read(db: Session, message: Message) -> Message:
    now = datetime.now(timezone.utc)
    if message.delivered_at is None:
        message.delivered_at = now
    if not message.is_read:
        message.is_read = True
    if message.read_at is None:
        message.read_at = now
    db.commit()
    db.refresh(message)
    return message