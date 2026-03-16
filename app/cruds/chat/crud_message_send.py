from sqlalchemy.orm import Session
from app.models.chat.model_message import Message
from datetime import datetime, timezone


def save_message(db: Session, conversation_id: int, sender_id: int, content: str) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content,
        created_at=datetime.now(timezone.utc),
        is_read=False,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
