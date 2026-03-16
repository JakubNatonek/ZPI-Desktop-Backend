from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.cruds.crud_login import get_all_users
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
    return [UserNameResponse(user_id=user.user_id, imie=user.imie, nazwisko=user.nazwisko) for user in users]


