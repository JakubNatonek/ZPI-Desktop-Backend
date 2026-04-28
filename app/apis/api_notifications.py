from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_notifications import (
    get_unread_notifications_for_user,
    get_all_notifications_for_user,
    get_notification_by_id,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    count_unread_notifications,
)
from app.models.model_user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkAsRead,
)


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="Pobierz powiadomienia użytkownika",
)
def get_notifications(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationListResponse:
    """
    Zwraca powiadomienia dla zalogowanego użytkownika.

    Query parameters:
    - limit: maksymalna liczba rezultatów (default: 50, max: 200)
    - offset: liczba powiadomień do pominięcia dla paginacji
    - unread_only: jeśli True, zwraca tylko nieprzeczytane (default: False)

    Dostęp: zalogowany użytkownik
    """
    if unread_only:
        unread = get_unread_notifications_for_user(db, current_user.user_id)
        unread_count = len(unread)
        items = [NotificationResponse.model_validate(n) for n in unread[offset : offset + limit]]
    else:
        notifications, total_count = get_all_notifications_for_user(
            db,
            current_user.user_id,
            limit=limit,
            offset=offset,
        )
        items = [NotificationResponse.model_validate(n) for n in notifications]
        unread_count = count_unread_notifications(db, current_user.user_id)

    return NotificationListResponse(
        items=items,
        unread_count=unread_count,
    )


@router.get(
    "/unread/count",
    response_model=dict,
    summary="Pobierz liczbę nieprzeczytanych powiadomień",
)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Zwraca liczbę nieprzeczytanych powiadomień dla zalogowanego użytkownika.
    Przydatne do wyświetlania badge'u na ikonie powiadomień.
    Dostęp: zalogowany użytkownik
    """
    count = count_unread_notifications(db, current_user.user_id)
    return {"unread_count": count}


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Pobierz szczegóły powiadomienia",
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    """
    Zwraca szczegóły konkretnego powiadomienia.
    Użytkownik może zobaczyć tylko swoje powiadomienia.
    Dostęp: zalogowany użytkownik
    """
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Powiadomienie o ID {notification_id} nie znalezione",
        )

    # Sprawdź uprawnienia
    if notification.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak dostępu do tego powiadomienia",
        )

    return NotificationResponse.model_validate(notification)


@router.put(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Oznacz powiadomienie jako przeczytane",
)
def mark_as_read(
    notification_id: int,
    payload: NotificationMarkAsRead = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    """
    Oznacza powiadomienie jako przeczytane.
    Użytkownik może oznaczyć tylko swoje powiadomienia.
    Dostęp: zalogowany użytkownik
    """
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Powiadomienie o ID {notification_id} nie znalezione",
        )

    # Sprawdź uprawnienia
    if notification.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak dostępu do tego powiadomienia",
        )

    marked = mark_notification_as_read(db, notification_id)
    return NotificationResponse.model_validate(marked)


@router.post(
    "/read-all",
    response_model=dict,
    summary="Oznacz wszystkie powiadomienia jako przeczytane",
)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Oznacza wszystkie powiadomienia zalogowanego użytkownika jako przeczytane.
    Dostęp: zalogowany użytkownik
    """
    count = mark_all_notifications_as_read(db, current_user.user_id)
    return {
        "message": f"Zaznaczono {count} powiadomień jako przeczytane",
        "updated_count": count,
    }
