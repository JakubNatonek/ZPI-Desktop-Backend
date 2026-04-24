from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_announcement import (
    create_announcement,
    format_announcement_datetime,
    list_announcements_for_user,
    mark_announcement_seen,
)
from app.models.model_role import Role
from app.models.model_user import User
from app.schemas.announcement import AnnouncementCreateRequest, AnnouncementResponse, AnnouncementSeenResponse


router = APIRouter(prefix="/announcements", tags=["announcements"])

ONLY_LECTURERS_CAN_CREATE = "Only lecturers can create announcements"
ANNOUNCEMENT_NOT_FOUND = "Announcement not found"


def _to_announcement_response(created: Any) -> AnnouncementResponse:
    return AnnouncementResponse(
        id=created.id,
        subject=created.subject,
        content=created.content,
        seen=False,
        created_at=format_announcement_datetime(created.created_at),
        author_id=created.author_id,
    )


def _is_lecturer(user: User, db: Session) -> bool:
    user_role_ids = [role_for_user.role_id for role_for_user in user.roles_for_user]
    if not user_role_ids:
        return False

    return bool(
        db.query(Role.id)
        .filter(Role.id.in_(user_role_ids))
        .filter(Role.is_lecturer.is_(True))
        .first()
    )


@router.get("/list", response_model=list[AnnouncementResponse], summary="List announcements with user seen flags")
def list_announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AnnouncementResponse]:
    return [AnnouncementResponse(**row) for row in list_announcements_for_user(db, current_user.user_id)]


@router.post("", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED, summary="Create announcement")
def create_announcement_entry(
    payload: AnnouncementCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnnouncementResponse:
    if not _is_lecturer(current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ONLY_LECTURERS_CAN_CREATE)

    created = create_announcement(
        db,
        author_id=current_user.user_id,
        subject=payload.subject,
        content=payload.content,
    )

    return _to_announcement_response(created)


@router.post("/{announcement_id}/seen", response_model=AnnouncementSeenResponse, summary="Mark announcement as seen")
def mark_seen(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnnouncementSeenResponse:
    ok = mark_announcement_seen(db, announcement_id, current_user.user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ANNOUNCEMENT_NOT_FOUND)

    return AnnouncementSeenResponse(announcement_id=announcement_id, seen=True)
