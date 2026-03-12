from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.cruds.crud_login import (
    authenticate_user,
    create_user_by_admin,
    get_user_by_email,
    get_user_by_login,
)
from app.database import get_db
from app.schemas.user import AdminUserCreate, UserLogin


router = APIRouter(prefix="/login", tags=["login"])


@router.post("/create", status_code=201)
def create_user(payload: AdminUserCreate, db: Session = Depends(get_db)) -> dict[str, str | int]:
    existing_login = get_user_by_login(db, payload.login)
    if existing_login is not None:
        raise HTTPException(status_code=409, detail="User with this login already exists")

    existing_email = get_user_by_email(db, payload.email)
    if existing_email is not None:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    user = create_user_by_admin(
        db,
        payload.login,
        payload.email,
        payload.password_hash,
        payload.rola,
        payload.dzial,
    )

    return {
        "user_id": user.user_id,
        "login": user.login,
        "email": user.email,
        "message": "User created",
    }


@router.post("/")
def login(payload: UserLogin, db: Session = Depends(get_db)) -> dict[str, str | int]:
    user = authenticate_user(db, payload.login, payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid login or password")

    return {
        "user_id": user.user_id,
        "login": user.login,
        "email": user.email,
        "message": "Login successful",
    }
