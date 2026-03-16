from sqlalchemy.orm import Session
from app.models.chat.model_conversation import Conversation, ConversationTypeEnum
from app.models.chat.model_conversation_member import ConversationMember


def get_or_create_direct_conversation(db: Session, user_a_id: int, user_b_id: int) -> Conversation:
    """
    Znajdź lub utwórz rozmowę typu 'direct' między dwoma użytkownikami.
    """
    # Szukaj istniejącej rozmowy direct z dokładnie tymi dwoma członkami
    q = db.query(Conversation).filter(Conversation.type == ConversationTypeEnum.DIRECT)
    for conv in q.all():
        member_ids = {m.user_id for m in conv.members}
        if member_ids == {user_a_id, user_b_id}:
            return conv
    # Nie znaleziono, utwórz
    conv = Conversation(type=ConversationTypeEnum.DIRECT)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    db.add(ConversationMember(conversation_id=conv.id, user_id=user_a_id))
    db.add(ConversationMember(conversation_id=conv.id, user_id=user_b_id))
    db.commit()
    return conv
