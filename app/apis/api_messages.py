from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.chat.model_conversation_member import ConversationMember
from app.models.chat.model_message import Message
from app.schemas.chat.chat import MessageResponse
from app.auth.current_user import get_current_user
from app.models.model_user import User
from app.dependencies.auth import require_admin


router = APIRouter()


@router.get(
    "/messages",
    response_model=List[MessageResponse],
    summary="Pobierz wszystkie wiadomości związane z danym użytkownikiem (bez odszyfrowania)",
)
def get_messages_for_user(
    user_id: int = Query(..., description="ID użytkownika, dla którego pobieramy wiadomości"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MessageResponse]:
    """
    Zwraca wiadomości dla konwersacji, w których uczestniczy `user_id`.
    Endpoint nie deszyfruje danych — zwraca dokładnie to, co jest zapisane w bazie.

    Uprawnienia: użytkownik może pobrać swoje wiadomości; użytkownik z rolą 'admin' może pobrać dowolnego.
    """
    # Permission check: allow self or admin
    if current_user.user_id != user_id and getattr(current_user.role, "name", None) != "admin":
        raise HTTPException(status_code=403, detail="Brak dostępu do żądanych wiadomości")

    conv_rows = db.query(ConversationMember.conversation_id).filter(ConversationMember.user_id == user_id).distinct().all()
    conversation_ids = [r[0] for r in conv_rows]

    if not conversation_ids:
        return []

    messages = (
        db.query(Message)
        .filter(Message.conversation_id.in_(conversation_ids))
        .order_by(Message.created_at.asc())
        .all()
    )

    result: List[MessageResponse] = []
    for m in messages:
        result.append(
            MessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                sender_id=m.sender_id,
                encrypted_message=getattr(m, "ciphertext", None),
                encrypted_aes_key=getattr(m, "wrapped_key", None),
                content=m.content,
                ciphertext=getattr(m, "ciphertext", None),
                iv=getattr(m, "iv", None),
                wrapped_key=getattr(m, "wrapped_key", None),
                created_at=m.created_at.isoformat(),
                delivered_at=m.delivered_at.isoformat() if m.delivered_at else None,
                is_read=m.is_read,
                read_at=m.read_at.isoformat() if m.read_at else None,
            )
        )

    return result
