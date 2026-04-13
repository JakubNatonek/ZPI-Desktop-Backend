from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_special_equipment import (
    create_special_equipment,
    delete_special_equipment,
    get_all_special_equipment,
    get_special_equipment_by_id,
    get_special_equipment_by_name,
    update_special_equipment,
)
from app.dependencies.auth import require_role
from app.models.model_user import User
from app.schemas.special_equipment import (
    SpecialEquipmentCreate,
    SpecialEquipmentResponse,
    SpecialEquipmentUpdate,
)


router = APIRouter(prefix="/special-equipment", tags=["special-equipment"])


@router.get("/list", response_model=List[SpecialEquipmentResponse], summary="Lista wyposazenia specjalnego")
def list_special_equipment(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> List[SpecialEquipmentResponse]:
    items = get_all_special_equipment(db)
    return [SpecialEquipmentResponse(id=cast(int, item.id), name=cast(str, item.name)) for item in items]


@router.get("/{special_equipment_id}", response_model=SpecialEquipmentResponse, summary="Szczegoly wyposazenia")
def get_special_equipment_entry(
    special_equipment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SpecialEquipmentResponse:
    item = get_special_equipment_by_id(db, special_equipment_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Special equipment not found")

    return SpecialEquipmentResponse(id=cast(int, item.id), name=cast(str, item.name))


@router.post("", response_model=SpecialEquipmentResponse, status_code=status.HTTP_201_CREATED, summary="Dodaj wyposazenie")
def create_special_equipment_entry(
    payload: SpecialEquipmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SpecialEquipmentResponse:
    cleaned_name = payload.name.strip()
    if not cleaned_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Special equipment name cannot be empty")

    if get_special_equipment_by_name(db, cleaned_name) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Special equipment already exists")

    item = create_special_equipment(db, cleaned_name)
    db.commit()
    db.refresh(item)
    return SpecialEquipmentResponse(id=cast(int, item.id), name=cast(str, item.name))


@router.put("/{special_equipment_id}", response_model=SpecialEquipmentResponse, summary="Edytuj wyposazenie")
def update_special_equipment_entry(
    special_equipment_id: int,
    payload: SpecialEquipmentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> SpecialEquipmentResponse:
    try:
        item = update_special_equipment(db, special_equipment_id, payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Special equipment not found")

    return SpecialEquipmentResponse(id=cast(int, item.id), name=cast(str, item.name))


@router.delete("/{special_equipment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usun wyposazenie")
def delete_special_equipment_entry(
    special_equipment_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> None:
    try:
        deleted = delete_special_equipment(db, special_equipment_id)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Special equipment is used by rooms and cannot be deleted",
        ) from exc

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Special equipment not found")
