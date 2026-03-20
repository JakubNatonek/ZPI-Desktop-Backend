from sqlalchemy.orm import Session
from app.models.chat.model_conversation import Conversation, ConversationTypeEnum
from app.models.chat.model_conversation_member import ConversationMember


def create_group_conversation(db: Session, name: str, user_ids: list[int]) -> Conversation:
    conv = Conversation(type=ConversationTypeEnum.GROUP, name=name)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    for uid in user_ids:
        db.add(ConversationMember(conversation_id=conv.id, user_id=uid))
    db.commit()
    return conv
