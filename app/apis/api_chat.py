from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from typing import List
from app.schemas.chat import ConversationStartResponse, MessageResponse
from app.auth.current_user import get_current_user
from app.cruds.chat.crud_conversation import get_or_create_direct_conversation
from app.cruds.chat.crud_message import get_messages_for_conversation
from app.cruds.chat.crud_message_send import save_message
from app.schemas.chat_send import SendMessageRequest
from app.schemas.chat_group import CreateGroupRequest, CreateGroupResponse
from app.cruds.crud_group_conversation import create_group_conversation
from app.models.chat.model_conversation_member import ConversationMember
from fastapi import HTTPException

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post(
    "/create-group",
    response_model=CreateGroupResponse,
    summary="Utwórz rozmowę grupową",
)
def create_group(
    payload: CreateGroupRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> CreateGroupResponse:
    # Dodaj aktualnego usera do grupy jeśli nie ma go na liście
    user_ids = set(payload.user_ids)
    user_ids.add(current_user.user_id)
    conv = create_group_conversation(db, payload.name, list(user_ids))
    return CreateGroupResponse(
        conversation_id=conv.id,
        name=payload.name,
        members=list(user_ids),
    )

@router.post(
    "/start-conversation/{user_id}",
    response_model=ConversationStartResponse,
    summary="Rozpocznij rozmowę z wybranym użytkownikiem",
)
def start_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> ConversationStartResponse:
    if user_id == current_user.user_id:
        return ConversationStartResponse(conversation_id=0, user_a_id=current_user.user_id, user_b_id=user_id)
    conv = get_or_create_direct_conversation(db, current_user.user_id, user_id)
    return ConversationStartResponse(conversation_id=conv.id, user_a_id=current_user.user_id, user_b_id=user_id)


@router.get(
    "/{conversation_id}/messages",
    response_model=List[MessageResponse],
    summary="Pobierz wiadomości dla rozmowy",
)

def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> List[MessageResponse]:
    # Kontrola bezpieczeństwa: czy user należy do rozmowy
    member = db.query(
        ConversationMember
    ).filter(
        ConversationMember.conversation_id == conversation_id,
        ConversationMember.user_id == current_user.user_id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Nie masz dostępu do tej rozmowy.")
    messages = get_messages_for_conversation(db, conversation_id)
    return [
        MessageResponse(
            id=m.id,
            sender_id=m.sender_id,
            content=m.content,
            created_at=m.created_at.isoformat(),
            is_read=m.is_read,
        )
        for m in messages
    ]


@router.post(
    "/{conversation_id}/send-message",
    response_model=MessageResponse,
    summary="Wyślij wiadomość w rozmowie",
)
def send_message(
    conversation_id: int,
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> MessageResponse:
    # Kontrola bezpieczeństwa: czy user należy do rozmowy
    member = db.query(
        ConversationMember
    ).filter(
        ConversationMember.conversation_id == conversation_id,
        ConversationMember.user_id == current_user.user_id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Nie masz dostępu do tej rozmowy.")
    msg = save_message(db, conversation_id, current_user.user_id, payload.content)
    return MessageResponse(
        id=msg.id,
        sender_id=msg.sender_id,
        content=msg.content,
        created_at=msg.created_at.isoformat(),
        is_read=msg.is_read,
    )
