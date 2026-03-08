from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db


router = APIRouter(prefix="/login", tags=["login"])


# TODO: Replace placeholder schemas with real fields and validation
class LoginCreatePlaceholder(BaseModel):
    pass  # Empty for now - add fields like username, password, etc.


class LoginUpdatePlaceholder(BaseModel):
    pass  # Empty for now - add fields to update


# TODO: Replace placeholders with real request/response schemas and CRUD calls.
@router.get("/")
def list_logins(_db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="TODO: implement list_logins")


@router.get("/{login_id}")
def get_login(login_id: int, _db: Session = Depends(get_db)):
    _ = login_id
    raise HTTPException(status_code=501, detail="TODO: implement get_login")


@router.post("/", status_code=501)
def create_login(payload: LoginCreatePlaceholder, _db: Session = Depends(get_db)):
    _ = payload
    raise HTTPException(status_code=501, detail="TODO: implement create_login")


@router.put("/{login_id}", status_code=501)
def update_login(login_id: int, payload: LoginUpdatePlaceholder, _db: Session = Depends(get_db)):
    _ = (login_id, payload)
    raise HTTPException(status_code=501, detail="TODO: implement update_login")


@router.delete("/{login_id}", status_code=501)
def delete_login(login_id: int, _db: Session = Depends(get_db)) -> None:
    _ = login_id
    raise HTTPException(status_code=501, detail="TODO: implement delete_login")
