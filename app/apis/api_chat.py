from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.chat.crud_conversation import get_or_create_direct_conversation, get_conversations_for_user
from app.cruds.chat.crud_group_conversation import create_group_conversation
from app.cruds.chat.crud_message import (
    get_message_for_user,
    get_messages_for_conversation,
    mark_message_delivered,
    mark_message_read,
)
from app.cruds.chat.crud_message_send import save_message
from app.models.model_user import User
from app.schemas.chat import (
    ConversationListItemResponse,
    ConversationStartResponse,
    MessageResponse,
    MessageStatusResponse,
    TypingIndicatorRequest,
    TypingIndicatorResponse,
    UserPresenceResponse,
)
from app.schemas.chat_group import CreateGroupRequest, CreateGroupResponse
from app.schemas.chat_send import SendMessageRequest
from app.schemas.user import UserNameResponse
from app.services.chat_service import (
    ERROR_CANNOT_MARK_OWN_MESSAGE,
    ERROR_EMPTY_GROUP_NAME,
    ERROR_EMPTY_MESSAGE,
    ERROR_INSUFFICIENT_GROUP_MEMBERS,
    ERROR_MESSAGE_NOT_FOUND,
    ERROR_SAME_USER_CONVERSATION,
    ERROR_USERS_NOT_FOUND,
    MIN_GROUP_MEMBERS,
    MIN_SEARCH_QUERY_LENGTH,
    build_message_status_response,
    build_presence_response,
    build_typing_response,
    ensure_conversation_member,
    get_user_or_raise,
    typing_state,
    validate_ttl_seconds,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _get_message_or_404(db: Session, message_id: int, current_user: User):
    message = get_message_for_user(db, message_id, current_user.user_id)
    if not message:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGE_NOT_FOUND)
    return message


def _filter_users_by_query(query, search_term: str | None):
    if not search_term:
        return query

    trimmed = search_term.strip()
    if not trimmed:
        return query

    pattern = trimmed + "%" if len(trimmed) >= MIN_SEARCH_QUERY_LENGTH else f"%{trimmed}%"
    return query.filter(
        or_(
            User.first_name.ilike(pattern),
            User.last_name.ilike(pattern),
        )
    )


def _validate_group_members(db: Session, member_ids: set[int]) -> None:
    existing_user_ids = {
        row[0]
        for row in db.query(User.user_id).filter(User.user_id.in_(member_ids)).all()
    }

    missing_ids = sorted(member_ids - existing_user_ids)
    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail=ERROR_USERS_NOT_FOUND.format(
                ", ".join(str(uid) for uid in missing_ids)
            ),
        )


@router.post(
    "/presence/online",
    response_model=UserPresenceResponse,
    summary="Ustaw status użytkownika na online",
)
def set_online(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPresenceResponse:
    """Mark the current user as online."""
    user = get_user_or_raise(db, current_user.user_id)
    db.commit()
    db.refresh(user)
    return build_presence_response(user)


@router.post(
    "/presence/offline",
    response_model=UserPresenceResponse,
    summary="Ustaw status użytkownika na offline i zapisz ostatnio widziany",
)
def set_offline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPresenceResponse:
    """Mark the current user as offline and record current timestamp."""
    from datetime import datetime, timezone
    user = get_user_or_raise(db, current_user.user_id)
    user.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return build_presence_response(user)


@router.get(
    "/presence/{user_id}",
    response_model=UserPresenceResponse,
    summary="Pobierz status online/offline i ostatnio widziany użytkownika",
)
def get_user_presence(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPresenceResponse:
    """Get online status and last seen timestamp for specified user."""
    user = get_user_or_raise(db, user_id)
    return build_presence_response(user)


@router.post(
    "/{conversation_id}/typing",
    response_model=TypingIndicatorResponse,
    summary="Ustaw wskaźnik pisania dla konwersacji",
)
def set_typing_indicator(
    conversation_id: int,
    payload: TypingIndicatorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TypingIndicatorResponse:
    """Update typing indicator for current user in conversation."""
    ensure_conversation_member(db, conversation_id, current_user.user_id)
    
    ttl = validate_ttl_seconds(payload.ttl_seconds)
    if payload.is_typing:
        typing_state.set_typing(conversation_id, current_user.user_id, ttl)
    else:
        typing_state.clear_typing(conversation_id, current_user.user_id)
    
    typing_user_ids = typing_state.get_typing_users(conversation_id)
    return build_typing_response(conversation_id, typing_user_ids)


@router.get(
    "/{conversation_id}/typing",
    response_model=TypingIndicatorResponse,
    summary="Pobierz aktywnych użytkowników, którzy piszą w konwersacji",
)
def get_typing_indicator(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TypingIndicatorResponse:
    """Get current typing users in conversation."""
    ensure_conversation_member(db, conversation_id, current_user.user_id)
    typing_user_ids = typing_state.get_typing_users(conversation_id)
    return build_typing_response(conversation_id, typing_user_ids)


@router.get(
    "/conversations",
    response_model=List[ConversationListItemResponse],
    summary="Pobierz listę konwersacji użytkownika",
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ConversationListItemResponse]:
    """Get all conversations for the current user."""
    conversations = get_conversations_for_user(db, current_user.user_id)
    return [
        ConversationListItemResponse(
            id=conv.id,
            type=conv.type.value if hasattr(conv.type, "value") else str(conv.type),
            name=conv.name,
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
    current_user: User = Depends(get_current_user),
) -> MessageStatusResponse:
    """Get delivery and read status for a message."""
    message = _get_message_or_404(db, message_id, current_user)
    return build_message_status_response(message)


@router.post(
    "/messages/{message_id}/delivered",
    response_model=MessageStatusResponse,
    summary="Oznacz wiadomość jako dostarczoną",
)
def acknowledge_message_delivered(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageStatusResponse:
    """Mark message as delivered."""
    message = _get_message_or_404(db, message_id, current_user)
    if message.sender_id == current_user.user_id:
        raise HTTPException(status_code=403, detail=ERROR_CANNOT_MARK_OWN_MESSAGE)
    message = mark_message_delivered(db, message)
    return build_message_status_response(message)


@router.post(
    "/messages/{message_id}/read",
    response_model=MessageStatusResponse,
    summary="Oznacz wiadomość jako przeczytaną",
)
def acknowledge_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageStatusResponse:
    """Mark message as read."""
    message = _get_message_or_404(db, message_id, current_user)
    if message.sender_id == current_user.user_id:
        raise HTTPException(status_code=403, detail=ERROR_CANNOT_MARK_OWN_MESSAGE)
    message = mark_message_read(db, message)
    return build_message_status_response(message)

# Wyszukiwanie użytkowników po imieniu lub nazwisku (do search bara)
@router.get(
    "/search-users",
    response_model=List[UserNameResponse],
    summary="Wyszukaj użytkowników po imieniu lub nazwisku"
)
def search_users(
    q: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[UserNameResponse]:
    """
    Search for users by first or last name (case-insensitive, partial match).
    
    Args:
        q: Search query (minimum 2 chars for prefix match, shorter for contains match)
        limit: Maximum number of results to return
        db: Database session
        current_user: Current authenticated user (results exclude themselves)
    
    Returns:
        List of matching users sorted by last name then first name
    """
    query = db.query(User).filter(User.user_id != current_user.user_id)
    filtered_query = _filter_users_by_query(query, q)

    users = (
        filtered_query
        .order_by(User.last_name.asc(), User.first_name.asc())
        .limit(limit)
        .all()
    )
    
    return [
        UserNameResponse(user_id=u.user_id, first_name=u.first_name, last_name=u.last_name)
        for u in users
    ]

@router.post(
    "/create-group",
    response_model=CreateGroupResponse,
    summary="Utwórz rozmowę grupową",
)
def create_group(
    payload: CreateGroupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CreateGroupResponse:
    """
    Create a new group conversation.
    
    The current user is automatically added to the group if not already specified.
    Validates that all users exist and group has at least 2 members.
    """
    group_name = payload.name.strip()
    if not group_name:
        raise HTTPException(status_code=400, detail=ERROR_EMPTY_GROUP_NAME)

    user_ids = {int(uid) for uid in payload.user_ids}
    user_ids.add(current_user.user_id)
    
    if len(user_ids) < MIN_GROUP_MEMBERS:
        raise HTTPException(status_code=400, detail=ERROR_INSUFFICIENT_GROUP_MEMBERS)

    _validate_group_members(db, user_ids)

    sorted_user_ids = sorted(user_ids)
    conv = create_group_conversation(db, group_name, sorted_user_ids)
    return CreateGroupResponse(
        conversation_id=conv.id,
        name=group_name,
        members=sorted_user_ids,
    )

@router.post(
    "/start-conversation/{user_id}",
    response_model=ConversationStartResponse,
    summary="Rozpocznij rozmowę z wybranym użytkownikiem",
)
def start_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationStartResponse:
    """
    Start or get existing direct conversation with another user.
    
    If a direct conversation already exists, returns that; otherwise creates a new one.
    Validates that the target user exists and is not the current user.
    """
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail=ERROR_SAME_USER_CONVERSATION)
    
    get_user_or_raise(db, user_id)
    conv = get_or_create_direct_conversation(db, current_user.user_id, user_id)
    
    return ConversationStartResponse(
        conversation_id=conv.id,
        user_a_id=current_user.user_id,
        user_b_id=user_id,
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=List[MessageResponse],
    summary="Pobierz wiadomości dla rozmowy",
)
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MessageResponse]:
    """Get all messages for a conversation. Current user must be a member."""
    ensure_conversation_member(db, conversation_id, current_user.user_id)
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
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Send a message in a conversation. Current user must be a member."""
    ensure_conversation_member(db, conversation_id, current_user.user_id)
    
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail=ERROR_EMPTY_MESSAGE)
    
    msg = save_message(db, conversation_id, current_user.user_id, content)
    
    return MessageResponse(
        id=msg.id,
        sender_id=msg.sender_id,
        content=msg.content,
        created_at=msg.created_at.isoformat(),
        delivered_at=msg.delivered_at.isoformat() if msg.delivered_at else None,
        is_read=msg.is_read,
        read_at=msg.read_at.isoformat() if msg.read_at else None,
    )
