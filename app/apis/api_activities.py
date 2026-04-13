from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_activity import (
    create_activity,
    delete_activity,
    get_activity_by_id,
    get_activity_by_name,
    get_all_activities,
    update_activity,
)
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityUpdate


router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/list", response_model=List[ActivityResponse], summary="Lista aktywnosci")
def list_activities(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> List[ActivityResponse]:
    activities = get_all_activities(db)
    return [ActivityResponse(id=cast(int, activity.id), name=cast(str, activity.name)) for activity in activities]


@router.get("/{activity_id}", response_model=ActivityResponse, summary="Szczegoly aktywnosci")
def get_activity_entry(
    activity_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> ActivityResponse:
    activity = get_activity_by_id(db, activity_id)
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    return ActivityResponse(id=cast(int, activity.id), name=cast(str, activity.name))


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED, summary="Dodaj aktywnosc")
def create_activity_entry(
    payload: ActivityCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> ActivityResponse:
    cleaned_name = payload.name.strip()
    if not cleaned_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Activity name cannot be empty")

    if get_activity_by_name(db, cleaned_name) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Activity already exists")

    activity = create_activity(db, cleaned_name)
    db.commit()
    db.refresh(activity)
    return ActivityResponse(id=cast(int, activity.id), name=cast(str, activity.name))


@router.put("/{activity_id}", response_model=ActivityResponse, summary="Edytuj aktywnosc")
def update_activity_entry(
    activity_id: int,
    payload: ActivityUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> ActivityResponse:
    try:
        activity = update_activity(db, activity_id, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    return ActivityResponse(id=cast(int, activity.id), name=cast(str, activity.name))


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usun aktywnosc")
def delete_activity_entry(
    activity_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    try:
        deleted = delete_activity(db, activity_id)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Activity is used by rooms and cannot be deleted",
        ) from exc

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
