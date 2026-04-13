from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.room.crud_room_type import (
    create_room_type,
    delete_room_type,
    get_all_room_types,
    get_room_type_by_id,
    get_room_type_by_name,
    update_room_type,
)
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.room_type import RoomTypeCreate, RoomTypeResponse, RoomTypeUpdate


router = APIRouter(prefix="/room-types", tags=["room-types"])


@router.get("/list", response_model=List[RoomTypeResponse], summary="Lista typow sal")
def list_room_types(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> List[RoomTypeResponse]:
    room_types = get_all_room_types(db)
    return [
        RoomTypeResponse(
            id=cast(int, room_type.id),
            name=cast(str, room_type.type),
            abbreviation=cast(str, room_type.abbreviation),
        )
        for room_type in room_types
    ]


@router.get("/{room_type_id}", response_model=RoomTypeResponse, summary="Szczegoly typu sali")
def get_room_type_entry(
    room_type_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> RoomTypeResponse:
    room_type = get_room_type_by_id(db, room_type_id)
    if room_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room type not found")

    return RoomTypeResponse(
        id=cast(int, room_type.id),
        name=cast(str, room_type.type),
        abbreviation=cast(str, room_type.abbreviation),
    )


@router.post("", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED, summary="Dodaj typ sali")
def create_room_type_entry(
    payload: RoomTypeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> RoomTypeResponse:
    cleaned_name = payload.name.strip()
    cleaned_abbreviation = payload.abbreviation.strip()

    if not cleaned_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room type name cannot be empty")
    if not cleaned_abbreviation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room type abbreviation cannot be empty")

    if get_room_type_by_name(db, cleaned_name) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room type already exists")

    room_type = create_room_type(db, cleaned_name, cleaned_abbreviation)
    return RoomTypeResponse(
        id=cast(int, room_type.id),
        name=cast(str, room_type.type),
        abbreviation=cast(str, room_type.abbreviation),
    )


@router.put("/{room_type_id}", response_model=RoomTypeResponse, summary="Edytuj typ sali")
def update_room_type_entry(
    room_type_id: int,
    payload: RoomTypeUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> RoomTypeResponse:
    cleaned_name = payload.name.strip()
    cleaned_abbreviation = payload.abbreviation.strip()

    if not cleaned_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room type name cannot be empty")
    if not cleaned_abbreviation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room type abbreviation cannot be empty")

    existing = get_room_type_by_name(db, cleaned_name)
    if existing is not None and existing.id != room_type_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room type already exists")

    room_type = update_room_type(
        db,
        room_type_id=room_type_id,
        room_type_name=cleaned_name,
        abbreviation=cleaned_abbreviation,
    )
    if room_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room type not found")

    return RoomTypeResponse(
        id=cast(int, room_type.id),
        name=cast(str, room_type.type),
        abbreviation=cast(str, room_type.abbreviation),
    )


@router.delete("/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usun typ sali")
def delete_room_type_entry(
    room_type_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    try:
        deleted = delete_room_type(db, room_type_id)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room type is used by rooms and cannot be deleted",
        ) from exc

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room type not found")
