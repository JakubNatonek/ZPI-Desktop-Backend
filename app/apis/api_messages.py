from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user, user_has_role
from app.core.database import get_db
from app.models.chat.model_conversation_member import ConversationMember
from app.models.chat.model_message import Message
from app.schemas.chat.chat import MessageResponse
from app.models.model_user import User


router = APIRouter()


def _isoformat_or_none(value) -> str | None:
    return value.isoformat() if value else None


@router.get(
    "/messages",
    response_model=List[MessageResponse],
    summary="Pobierz wszystkie wiadomości związane z danym użytkownikiem (bez odszyfrowania)",
)
def get_messages_for_user(
    user_id: int = Query(..., description="ID użytkownika, dla którego pobieramy wiadomości"),
    since: str | None = Query(
        None,
        description="Opcjonalny filtr ISO 8601 — zwraca tylko wiadomości z created_at > since (do pollingu)",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MessageResponse]:
    """
    Zwraca wiadomości dla konwersacji, w których uczestniczy `user_id`.
    Endpoint nie deszyfruje danych — zwraca dokładnie to, co jest zapisane w bazie.

    Gdy podano parametr ``since`` (ISO 8601), zwracane są wyłącznie wiadomości
    utworzone po tej dacie — co pozwala na efektywny polling co X sekund.

    Uprawnienia: użytkownik może pobrać swoje wiadomości; użytkownik z rolą 'admin' może pobrać dowolnego.
    """
    # Permission check: allow self or admin
    if current_user.user_id != user_id and not user_has_role(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Brak dostępu do żądanych wiadomości")

    # Parse optional `since` filter
    since_dt: datetime | None = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            raise HTTPException(status_code=400, detail="Nieprawidłowy format daty 'since'. Oczekiwano ISO 8601.")

    conversation_ids = [
        conversation_id
        for (conversation_id,) in (
            db.query(ConversationMember.conversation_id)
            .filter(ConversationMember.user_id == user_id)
            .distinct()
            .all()
        )
    ]

    if not conversation_ids:
        return []

    query = (
        db.query(Message)
        .filter(Message.conversation_id.in_(conversation_ids))
    )

    if since_dt is not None:
        query = query.filter(Message.created_at > since_dt)

    messages = query.order_by(Message.created_at.asc()).all()

    return [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            sender_id=m.sender_id,
            encrypted_message=(ciphertext := getattr(m, "ciphertext", None)),
            encrypted_aes_key=(wrapped_key := getattr(m, "wrapped_key", None)),
            content=m.content,
            ciphertext=ciphertext,
            iv=getattr(m, "iv", None),
            wrapped_key=wrapped_key,
            created_at=m.created_at.isoformat(),
            delivered_at=_isoformat_or_none(m.delivered_at),
            is_read=m.is_read,
            read_at=_isoformat_or_none(m.read_at),
        )
        for m in messages
    ]
