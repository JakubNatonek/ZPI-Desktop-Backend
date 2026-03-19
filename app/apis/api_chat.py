from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from typing import List, Optional
from datetime import datetime, timedelta, timezone
from threading import Lock
from sqlalchemy import or_
from app.core.database import get_db
from app.models.model_user import User
from app.schemas.user import UserNameResponse
from app.schemas.chat import (
    ConversationStartResponse,
    MessageResponse,
    ConversationListItemResponse,
    MessageStatusResponse,
    UserPresenceResponse,
    TypingIndicatorRequest,
    TypingIndicatorResponse,
)
from app.schemas.chat_send import SendMessageRequest
from app.schemas.chat_group import CreateGroupRequest, CreateGroupResponse
from app.auth.current_user import get_current_user
from app.cruds.chat.crud_conversation import get_or_create_direct_conversation, get_conversations_for_user
from app.cruds.chat.crud_message import (
    get_messages_for_conversation,
    get_message_for_user,
    mark_message_delivered,
    mark_message_read,
)
from app.cruds.chat.crud_message_send import save_message
from app.cruds.crud_group_conversation import create_group_conversation
from app.models.chat.model_conversation_member import ConversationMember

router = APIRouter(prefix="/api/chat", tags=["chat"])
_typing_state: dict[tuple[int, int], datetime] = {}
_typing_state_lock = Lock()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _ensure_conversation_member(db: Session, conversation_id: int, user_id: int) -> None:
    member = (
        db.query(ConversationMember)
        .filter(
            ConversationMember.conversation_id == conversation_id,
            ConversationMember.user_id == user_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Nie masz dostępu do tej rozmowy.")


def _cleanup_typing_state(now: datetime) -> None:
    expired = [
        key
        for key, expires_at in _typing_state.items()
        if expires_at <= now
    ]
    for key in expired:
        _typing_state.pop(key, None)


def _typing_users_for_conversation(conversation_id: int, now: datetime) -> list[int]:
    _cleanup_typing_state(now)
    return [
        user_id
        for (conv_id, user_id), expires_at in _typing_state.items()
        if conv_id == conversation_id and expires_at > now
    ]


def _message_status_response(message) -> MessageStatusResponse:
    return MessageStatusResponse(
        message_id=message.id,
        sent=True,
        delivered=message.delivered_at is not None,
        read=bool(message.is_read),
        sent_at=message.created_at.isoformat(),
        delivered_at=message.delivered_at.isoformat() if message.delivered_at else None,
        read_at=message.read_at.isoformat() if message.read_at else None,
    )


def _presence_response(user: User) -> UserPresenceResponse:
    return UserPresenceResponse(
        user_id=user.user_id,
        is_online=bool(user.is_online),
        last_seen_at=_to_iso(user.last_seen_at),
    )


@router.post(
    "/presence/online",
    response_model=UserPresenceResponse,
    summary="Ustaw status użytkownika na online",
)
def set_online(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> UserPresenceResponse:
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje.")
    user.is_online = True
    db.commit()
    db.refresh(user)
    return _presence_response(user)


@router.post(
    "/presence/offline",
    response_model=UserPresenceResponse,
    summary="Ustaw status użytkownika na offline i zapisz ostatnio widziany",
)
def set_offline(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> UserPresenceResponse:
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje.")
    user.is_online = False
    user.last_seen_at = _now_utc()
    db.commit()
    db.refresh(user)
    return _presence_response(user)


@router.get(
    "/presence/{user_id}",
    response_model=UserPresenceResponse,
    summary="Pobierz status online/offline i ostatnio widziany użytkownika",
)
def get_user_presence(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> UserPresenceResponse:
    _ = current_user
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje.")
    return _presence_response(user)


@router.post(
    "/{conversation_id}/typing",
    response_model=TypingIndicatorResponse,
    summary="Ustaw wskaźnik pisania dla konwersacji",
)
def set_typing_indicator(
    conversation_id: int,
    payload: TypingIndicatorRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> TypingIndicatorResponse:
    _ensure_conversation_member(db, conversation_id, current_user.user_id)
    now = _now_utc()
    ttl = max(3, min(payload.ttl_seconds, 30))
    key = (conversation_id, current_user.user_id)
    with _typing_state_lock:
        if payload.is_typing:
            _typing_state[key] = now + timedelta(seconds=ttl)
        else:
            _typing_state.pop(key, None)
        typing_user_ids = _typing_users_for_conversation(conversation_id, now)
    return TypingIndicatorResponse(
        conversation_id=conversation_id,
        typing_user_ids=typing_user_ids,
    )


@router.get(
    "/{conversation_id}/typing",
    response_model=TypingIndicatorResponse,
    summary="Pobierz aktywnych użytkowników, którzy piszą w konwersacji",
)
def get_typing_indicator(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> TypingIndicatorResponse:
    _ensure_conversation_member(db, conversation_id, current_user.user_id)
    now = _now_utc()
    with _typing_state_lock:
        typing_user_ids = _typing_users_for_conversation(conversation_id, now)
    return TypingIndicatorResponse(
        conversation_id=conversation_id,
        typing_user_ids=typing_user_ids,
    )


@router.get(
    "/conversations",
    response_model=List[ConversationListItemResponse],
    summary="Pobierz listę konwersacji użytkownika",
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> List[ConversationListItemResponse]:
    conversations = get_conversations_for_user(db, current_user.user_id)
    return [
        ConversationListItemResponse(
            id=conv.id,
            type=conv.type.value if hasattr(conv.type, "value") else str(conv.type),
            created_at=conv.created_at.isoformat(),
            member_ids=[member.user_id for member in conv.members],
        )
        for conv in conversations
    ]


@router.get(
    "/messages/{message_id}/status",
    response_model=MessageStatusResponse,
    summary="Pobierz status wiadomości (wysłana/dostarczona/przeczytana)",
)
def get_message_status(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> MessageStatusResponse:
    message = get_message_for_user(db, message_id, current_user.user_id)
    if not message:
        raise HTTPException(status_code=404, detail="Wiadomość nie istnieje lub brak dostępu.")
    return _message_status_response(message)


@router.post(
    "/messages/{message_id}/delivered",
    response_model=MessageStatusResponse,
    summary="Oznacz wiadomość jako dostarczoną",
)
def acknowledge_message_delivered(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> MessageStatusResponse:
    message = get_message_for_user(db, message_id, current_user.user_id)
    if not message:
        raise HTTPException(status_code=404, detail="Wiadomość nie istnieje lub brak dostępu.")
    if message.sender_id == current_user.user_id:
        raise HTTPException(status_code=403, detail="Nadawca nie może oznaczyć własnej wiadomości jako dostarczonej.")
    message = mark_message_delivered(db, message)
    return _message_status_response(message)


@router.post(
    "/messages/{message_id}/read",
    response_model=MessageStatusResponse,
    summary="Oznacz wiadomość jako przeczytaną",
)
def acknowledge_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> MessageStatusResponse:
    message = get_message_for_user(db, message_id, current_user.user_id)
    if not message:
        raise HTTPException(status_code=404, detail="Wiadomość nie istnieje lub brak dostępu.")
    if message.sender_id == current_user.user_id:
        raise HTTPException(status_code=403, detail="Nadawca nie może oznaczyć własnej wiadomości jako przeczytanej.")
    message = mark_message_read(db, message)
    return _message_status_response(message)

# Wyszukiwanie użytkowników po imieniu lub nazwisku (do search bara)
@router.get(
    "/search-users",
    response_model=List[UserNameResponse],
    summary="Wyszukaj użytkowników po imieniu lub nazwisku"
)
def search_users(
    q: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[UserNameResponse]:
    """Wyszukaj użytkowników po imieniu lub nazwisku (case-insensitive, partial match)."""
    query = db.query(User)
    if q:
        if len(q) >= 2:
            query = query.filter(
                or_(User.imie.ilike(f"{q}%"), User.nazwisko.ilike(f"{q}%"))
            )
        else:
            query = query.filter(
                or_(User.imie.ilike(f"%{q}%"), User.nazwisko.ilike(f"%{q}%"))
            )
    users = query.order_by(User.nazwisko.asc(), User.imie.asc()).all()
    return [UserNameResponse(user_id=u.user_id, imie=u.imie, nazwisko=u.nazwisko) for u in users]

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
    _ensure_conversation_member(db, conversation_id, current_user.user_id)
    messages = get_messages_for_conversation(db, conversation_id)
    return [
        MessageResponse(
            id=m.id,
            sender_id=m.sender_id,
            content=m.content,
            created_at=m.created_at.isoformat(),
            delivered_at=m.delivered_at.isoformat() if m.delivered_at else None,
            is_read=m.is_read,
            read_at=m.read_at.isoformat() if m.read_at else None,
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
    _ensure_conversation_member(db, conversation_id, current_user.user_id)
    msg = save_message(db, conversation_id, current_user.user_id, payload.content)
    return MessageResponse(
        id=msg.id,
        sender_id=msg.sender_id,
        content=msg.content,
        created_at=msg.created_at.isoformat(),
        delivered_at=msg.delivered_at.isoformat() if msg.delivered_at else None,
        is_read=msg.is_read,
        read_at=msg.read_at.isoformat() if msg.read_at else None,
    )
