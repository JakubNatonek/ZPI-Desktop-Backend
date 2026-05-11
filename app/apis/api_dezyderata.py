from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_dezyderata import (
    delete_dezyderata,
    get_dezyderata_by_id,
    get_dezyderaty,
    map_dezyderata_to_response,
    map_semestr_to_response,
    replace_dezyderata_for_week,
)
from app.cruds.crud_day import get_valid_day_ids
from app.cruds.crud_semester import create_semestr, delete_semestr, get_current_semestr, get_semestr_by_id, get_semestry
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.cruds.crud_audit import log_change
from app.models.model_user import User
from app.schemas.dezyderata import (
    DezyderataCreate,
    DezyderataListResponse,
    DezyderataResponse,
    SemestrCreate,
    SemestrListResponse,
    SemestrResponse,
)


router = APIRouter(prefix="/dezyderaty", tags=["dezyderaty"])

ADMIN_ROLE_IDS = {1}
ADMIN_ROLE_NAMES = {"admin", "rapla_editor", "wykladowca_rapla_editor"}
LECTURER_ROLE_IDS = {2}
LECTURER_ROLE_NAMES = {"wykładowca", "wykladowca", "lecturer"}


def _user_role_ids_and_names(db: Session, current_user: User) -> tuple[set[int], set[str]]:
    roles = get_roles_for_user(db, current_user.user_id)
    role_ids = {role.id for role in roles}
    role_names = {role.name.strip().lower() for role in roles if role.name}
    return role_ids, role_names


def _user_has_admin_access(db: Session, current_user: User) -> bool:
    role_ids, role_names = _user_role_ids_and_names(db, current_user)
    return bool(role_ids.intersection(ADMIN_ROLE_IDS) or role_names.intersection(ADMIN_ROLE_NAMES))


def _user_has_lecturer_access(db: Session, current_user: User) -> bool:
    role_ids, role_names = _user_role_ids_and_names(db, current_user)
    return bool(role_ids.intersection(LECTURER_ROLE_IDS) or role_names.intersection(LECTURER_ROLE_NAMES))


def _require_lecturer_or_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    if not (_user_has_admin_access(db, current_user) or _user_has_lecturer_access(db, current_user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user

# NOTE: Why this and note use: from app.dependencies.auth import require_admin  _: User = Depends(require_admin),
def _require_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    if not _user_has_admin_access(db, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user


# ----- Semestr endpoints -----

@router.get("/semestry", response_model=SemestrListResponse, summary="Pobierz listę semestrów")
def list_semestry(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SemestrListResponse:
    semestry = get_semestry(db)
    return SemestrListResponse(items=[SemestrResponse(**map_semestr_to_response(s)) for s in semestry])


@router.get("/semestry/current", response_model=SemestrResponse, summary="Pobierz aktualny semestr")
def get_current_semestr_endpoint(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SemestrResponse:
    semestr = get_current_semestr(db)
    if semestr is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active semester found")
    return SemestrResponse(**map_semestr_to_response(semestr))


@router.get("/semestry/{semestr_id}", response_model=SemestrResponse, summary="Pobierz szczegóły semestru")
def get_semestr(
    semestr_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SemestrResponse:
    semestr = get_semestr_by_id(db, semestr_id)
    if semestr is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")
    return SemestrResponse(**map_semestr_to_response(semestr))


@router.post("/semestry", response_model=SemestrResponse, status_code=status.HTTP_201_CREATED, summary="Utwórz semestr")
def create_semestr_entry(
    payload: SemestrCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_require_lecturer_or_admin),
) -> SemestrResponse:
    created = create_semestr(db, payload)
    return SemestrResponse(**map_semestr_to_response(created))


@router.delete("/semestry/{semestr_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń semestr")
def delete_semestr_entry(
    semestr_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_require_lecturer_or_admin),
) -> None:
    semestr = get_semestr_by_id(db, semestr_id)
    if semestr is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")
    delete_semestr(db, semestr)


# ----- Dezyderata endpoints -----

@router.get("", response_model=DezyderataListResponse, summary="Pobierz listę dezyderat")
def list_dezyderaty(
    semestr_id: Optional[int] = Query(None, description="Filtruj po semestrze"),
    user_id: Optional[int] = Query(None, description="Filtruj po użytkowniku (tylko admin)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_lecturer_or_admin),
) -> DezyderataListResponse:
    # Wykładowca widzi tylko swoje dezyderaty
    if _user_has_lecturer_access(db, current_user):
        effective_user_id = current_user.user_id
    else:
        # Admin może filtrować po dowolnym użytkowniku
        effective_user_id = user_id

    dezyderaty = get_dezyderaty(db, user_id=effective_user_id, semestr_id=semestr_id)
    return DezyderataListResponse(
        items=[DezyderataResponse(**map_dezyderata_to_response(d)) for d in dezyderaty]
    )


@router.get("/my", response_model=DezyderataListResponse, summary="Pobierz własne dezyderaty")
def list_my_dezyderaty(
    semestr_id: Optional[int] = Query(None, description="Filtruj po semestrze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DezyderataListResponse:
    dezyderaty = get_dezyderaty(db, user_id=current_user.user_id, semestr_id=semestr_id)
    return DezyderataListResponse(
        items=[DezyderataResponse(**map_dezyderata_to_response(d)) for d in dezyderaty]
    )


@router.get("/{dezyderata_id}", response_model=DezyderataResponse, summary="Pobierz szczegóły dezyderaty")
def get_dezyderata(
    dezyderata_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_lecturer_or_admin),
) -> DezyderataResponse:
    dezyderata = get_dezyderata_by_id(db, dezyderata_id)
    if dezyderata is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dezyderata not found")

    # NOTE: Static data to chenge
    if _user_has_lecturer_access(db, current_user) and dezyderata.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return DezyderataResponse(**map_dezyderata_to_response(dezyderata))


@router.post("", response_model=DezyderataListResponse, status_code=status.HTTP_201_CREATED, summary="Utwórz lub zaktualizuj dezyderaty tygodniowe")
def create_or_update_dezyderata(
    payload: DezyderataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_lecturer_or_admin),
) -> DezyderataListResponse:
    # Sprawdź czy semestr istnieje
    semestr = get_semestr_by_id(db, payload.semestr_id)
    if semestr is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")

    if payload.data_do < payload.data_od:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="data_do cannot be earlier than data_od")

    valid_day_ids = get_valid_day_ids(db)
    if not valid_day_ids:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Days table is empty")

    for entry in payload.entries:
        if entry.day_id not in valid_day_ids:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid day_id: {entry.day_id}")
        if entry.to_hour < entry.from_hour:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="to_hour cannot be earlier than from_hour")

    created_items = replace_dezyderata_for_week(db, current_user.user_id, payload)
    
    log_change(
        db=db,
        entity_name="Dezyderata",
        entity_id=payload.semestr_id,
        action="UPDATE",
        old_values=None,
        new_values=[map_dezyderata_to_response(i) for i in created_items],
        user_id=current_user.user_id
    )
    
    return DezyderataListResponse(
        items=[DezyderataResponse(**map_dezyderata_to_response(item)) for item in created_items]
    )


@router.delete("/{dezyderata_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń dezyderatę")
def delete_dezyderata_entry(
    dezyderata_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_require_lecturer_or_admin),
) -> None:
    dezyderata = get_dezyderata_by_id(db, dezyderata_id)
    if dezyderata is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dezyderata not found")

    # NOTE: Why ststic data here
    if _user_has_lecturer_access(db, current_user) and dezyderata.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    old_values = map_dezyderata_to_response(dezyderata)
    delete_dezyderata(db, dezyderata)

    log_change(
        db=db,
        entity_name="Dezyderata",
        entity_id=dezyderata_id,
        action="DELETE",
        old_values=old_values,
        new_values=None,
        user_id=current_user.user_id
    )
