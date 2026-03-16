from sqlalchemy.orm import Session
from app.models.chat.model_message import Message


def get_messages_for_conversation(db: Session, conversation_id: int) -> list[Message]:
    """
    Pobierz wszystkie wiadomości dla danej rozmowy.
    """
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
