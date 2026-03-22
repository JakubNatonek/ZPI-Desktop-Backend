from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_login import get_all_users, get_user_by_id
from app.schemas.user import UserNameResponse
from app.auth.current_user import get_current_user
from app.cruds.chat.crud_conversation import get_or_create_direct_conversation

router = APIRouter(prefix="/users", tags=["users"])

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


