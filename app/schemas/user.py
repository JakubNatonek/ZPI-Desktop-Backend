
from pydantic import BaseModel, EmailStr

from app.models.model_user import DzialEnum, RolaEnum


class AdminUserCreate(BaseModel):
    login: str
    email: EmailStr
    password_hash: str
    rola: RolaEnum
    dzial: DzialEnum


class UserLogin(BaseModel):
    login: str
    password: str
