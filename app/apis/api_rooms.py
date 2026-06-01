from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_audit_logs import create_audit_log
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


# def _require_admin(current_user: User = Depends(get_current_user)) -> User:
#     role_value = current_user.role.name if current_user.role else str(current_user.role)
#     if role_value != "admin":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
#     return current_user


@router.get("/list", response_model=RoomListResponse, summary="Pobierz listę sal")
def list_rooms(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin", "rapla_editor", "lecturer_rapla_editor"])),
) -> RoomListResponse:
    rooms = get_rooms(db)
    return RoomListResponse(items=[RoomResponse(**map_room_to_response(room)) for room in rooms])


@router.get("/{room_id}", response_model=RoomResponse, summary="Pobierz szczegóły sali")
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(["admin", "rapla_editor", "lecturer_rapla_editor"])),
) -> RoomResponse:
    room = get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    return RoomResponse(**map_room_to_response(room))


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED, summary="Utwórz salę")
def create_room_entry(
    payload: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "rapla_editor", "lecturer_rapla_editor"])),
) -> RoomResponse:
    existing = get_room_by_number(db, payload.room_number)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room number already exists")

    created = create_room(db, payload)
    create_audit_log(
        db, "Room", int(created.id), "create",
        modified_by=current_user.user_id,
        modified_by_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        new_values=map_room_to_response(created),
    )
    return RoomResponse(**map_room_to_response(created))


@router.put("/{room_id}", response_model=RoomResponse, summary="Edytuj salę")
def update_room_entry(
    room_id: int,
    payload: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "rapla_editor", "lecturer_rapla_editor"])),
) -> RoomResponse:
    room = get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    existing = get_room_by_number(db, payload.room_number)
    if existing is not None and existing.id != room_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room number already exists")

    old_values = map_room_to_response(room)
    updated = update_room(db, room, payload)
    create_audit_log(
        db, "Room", room_id, "update",
        modified_by=current_user.user_id,
        modified_by_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        old_values=old_values,
        new_values=map_room_to_response(updated),
    )
    return RoomResponse(**map_room_to_response(updated))


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń salę")
def delete_room_entry(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "rapla_editor", "lecturer_rapla_editor"])),
) -> None:
    room = get_room_by_id(db, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    old_values = map_room_to_response(room)
    delete_room(db, room)
    create_audit_log(
        db, "Room", room_id, "delete",
        modified_by=current_user.user_id,
        modified_by_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        old_values=old_values,
    )
