from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_login import get_all_users, get_user_by_id
from app.cruds.crud_department_role import create_department, create_role
from app.schemas.user import UserNameResponse, UserProfileResponse
from app.schemas.department_role import DepartmentCreate, RoleCreate, DepartmentResponse, RoleResponse
from app.auth.current_user import get_current_user
from app.cruds.chat.crud_conversation import get_or_create_direct_conversation
from app.models.model_user import User

router = APIRouter(prefix="/users", tags=["users"])


# Endpoint to add a department
@router.post("/add-department", response_model=DepartmentResponse, summary="Add a new department")
def add_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> DepartmentResponse:
    _ = current_user
    try:
        dep = create_department(db, department.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DepartmentResponse(id=dep.id, name=dep.name)


# Endpoint to add a role
@router.post("/add-role", response_model=RoleResponse, summary="Add a new role")
def add_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> RoleResponse:
    _ = current_user
    try:
        r = create_role(db, role.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RoleResponse(id=r.id, name=r.name)

@router.get(
    "",
    response_model=List[UserNameResponse],
    summary="Pobierz listę użytkowników (imię, nazwisko, user_id)",
)
def list_users(db: Session = Depends(get_db)) -> List[UserNameResponse]:
    users = get_all_users(db)
    return [UserNameResponse(user_id=user.user_id, first_name=user.first_name, last_name=user.last_name) for user in users]


@router.get(
    "/{user_id}/name",
    response_model=UserNameResponse,
    summary="Pobierz imię i nazwisko użytkownika po user_id",
)
def get_user_name(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> UserNameResponse:
    _ = current_user
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist.")
    return UserNameResponse(user_id=user.user_id, first_name=user.first_name, last_name=user.last_name)


@router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Pobierz profil zalogowanego użytkownika",
)
def get_my_profile(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    role_name = (current_user.role.name if current_user.role else "").lower()
    group_code = current_user.student_profile.group.code if current_user.student_profile and current_user.student_profile.group else None

    if role_name == "student":
        status = "Aktywny student"
    elif role_name in {"wykladowca", "lecturer"}:
        status = "Pracownik dydaktyczny"
    elif role_name in {"planista", "planner"}:
        status = "Planista"
    else:
        status = "Administrator systemu"

    return UserProfileResponse(
        status=status,
        album_number=current_user.student_profile.index_number if current_user.student_profile and current_user.student_profile.index_number else "Nie dotyczy",
        year=str(current_user.student_profile.group.year) if current_user.student_profile and current_user.student_profile.group else "Nie dotyczy",
        semester=str(current_user.student_profile.semester) if current_user.student_profile and current_user.student_profile.semester is not None else "Nie dotyczy",
        major=current_user.department.name if current_user.department else "Nie dotyczy",
        faculty=current_user.department.name if current_user.department else "Nie dotyczy",
        study_track="Ogolnoakademicki" if role_name == "student" else "Nie dotyczy",
        study_mode="Stacjonarne" if role_name == "student" else "Nie dotyczy",
        title=current_user.teacher_profile.title if current_user.teacher_profile and current_user.teacher_profile.title else "Nie dotyczy",
        groups=[group_code] if group_code else [],
    )


