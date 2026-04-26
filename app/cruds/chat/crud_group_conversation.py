from sqlalchemy.orm import Session
from app.models.chat.model_conversation import Conversation, ConversationTypeEnum
from app.models.chat.model_conversation_member import ConversationMember
from app.models.model_user import User


def create_group_conversation(db: Session, name: str, user_ids: list[int]) -> Conversation:
    conv = Conversation(type=ConversationTypeEnum.GROUP, name=name)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    for uid in user_ids:
        db.add(ConversationMember(conversation_id=conv.id, user_id=uid))
    db.commit()
    return conv


def get_group_conversation_by_id(db: Session, conversation_id: int) -> Conversation | None:
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.type == ConversationTypeEnum.GROUP,
        )
        .first()
    )


def get_group_conversation_members(db: Session, conversation_id: int) -> list[User]:
    return (
        db.query(User)
        .join(ConversationMember, ConversationMember.user_id == User.user_id)
        .filter(ConversationMember.conversation_id == conversation_id)
        .order_by(User.last_name.asc(), User.first_name.asc())
        .all()
    )


def add_users_to_group_conversation(db: Session, conversation_id: int, user_ids: list[int]) -> Conversation | None:
    conv = get_group_conversation_by_id(db, conversation_id)
    if conv is None:
        return None

    existing_user_ids = {member.user_id for member in conv.members}
    new_user_ids = sorted({int(user_id) for user_id in user_ids} - existing_user_ids)

    for user_id in new_user_ids:
        db.add(ConversationMember(conversation_id=conv.id, user_id=user_id))

    if new_user_ids:
        db.commit()
        db.refresh(conv)

    return conv
