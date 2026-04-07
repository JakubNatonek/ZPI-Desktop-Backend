from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.current_user import get_current_user
from app.core.database import get_db
from app.cruds.crud_dezyderata import (
    create_semestr,
    delete_dezyderata,
    delete_semestr,
    get_current_semestr,
    get_dezyderata_by_id,
    get_dezyderaty,
    get_semestr_by_id,
    get_semestry,
    get_valid_day_ids,
    map_dezyderata_to_response,
    map_semestr_to_response,
    replace_dezyderata_for_week,
)
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


def _require_lecturer_or_admin(current_user: User = Depends(get_current_user)) -> User:
    role_value = current_user.role.name if current_user.role else str(current_user.role)
    role_lower = role_value.lower() if role_value else ""
    allowed_roles = ("admin", "wykładowca", "lecturer", "wykladowca", "planner")
    if role_lower not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user


def _require_admin(current_user: User = Depends(get_current_user)) -> User:
    role_value = current_user.role.name if current_user.role else str(current_user.role)
    role_lower = role_value.lower() if role_value else ""
    if role_lower != "admin":
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
    _: User = Depends(_require_admin),
) -> SemestrResponse:
    created = create_semestr(db, payload)
    return SemestrResponse(**map_semestr_to_response(created))


@router.delete("/semestry/{semestr_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Usuń semestr")
def delete_semestr_entry(
    semestr_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
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
    role_value = current_user.role.name if current_user.role else str(current_user.role)
    role_lower = role_value.lower() if role_value else ""

    # Wykładowca widzi tylko swoje dezyderaty
    if role_lower in ("wykładowca", "wykladowca", "lecturer"):
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

    role_value = current_user.role.name if current_user.role else str(current_user.role)
    role_lower = role_value.lower() if role_value else ""
    if role_lower in ("wykładowca", "wykladowca", "lecturer") and dezyderata.user_id != current_user.user_id:
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

    role_value = current_user.role.name if current_user.role else str(current_user.role)
    role_lower = role_value.lower() if role_value else ""
    if role_lower in ("wykładowca", "wykladowca", "lecturer") and dezyderata.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    delete_dezyderata(db, dezyderata)
