from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.room.crud_room import (
    create_room,
    delete_room,
    get_room_by_id,
    get_room_by_number,
    get_rooms,
    map_room_to_response,
    update_room,
)
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.room import RoomCreate, RoomListResponse, RoomResponse, RoomUpdate


router = APIRouter(prefix="/rooms", tags=["rooms"])
ROOM_NOT_FOUND_DETAIL = "Room not found"


def _to_room_response(room) -> RoomResponse:
    return RoomResponse(**map_room_to_response(room))


def _get_room_or_404(db: Session, room_id: int):
    room = get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ROOM_NOT_FOUND_DETAIL)
    return room


# def _require_admin(current_user: User = Depends(get_current_user)) -> User:
#     role_value = current_user.role.name if current_user.role else str(current_user.role)
#     if role_value != "admin":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
#     return current_user


@router.get("/list", response_model=RoomListResponse, summary="Pobierz listę sal")
def list_rooms(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> RoomListResponse:
    rooms = get_rooms(db)
    return RoomListResponse(items=[_to_room_response(room) for room in rooms])


@router.get("/{room_id}", response_model=RoomResponse, summary="Pobierz szczegóły sali")
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> RoomResponse:
    room = _get_room_or_404(db, room_id)
    return _to_room_response(room)


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED, summary="Utwórz salę")
def create_room_entry(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> RoomResponse:
    existing = get_room_by_number(db, payload.room_number)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room number already exists")

    created = create_room(db, payload)
    return _to_room_response(created)


@router.put("/{room_id}", response_model=RoomResponse, summary="Edytuj salę")
def update_room_entry(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> RoomResponse:
    room = _get_room_or_404(db, room_id)

    existing = get_room_by_number(db, payload.room_number)
    if existing is not None and existing.id != room_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room number already exists")

    updated = update_room(db, room, payload)
    return _to_room_response(updated)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń salę")
def delete_room_entry(
    room_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    room = _get_room_or_404(db, room_id)
    delete_room(db, room)
