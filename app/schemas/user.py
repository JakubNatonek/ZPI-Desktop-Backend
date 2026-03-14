
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


class AuthResponse(BaseModel):
    user_id: int
    login: str
    email: EmailStr
    access_token: str
    token_type: str = "bearer"
    access_token_expires_in: int


class CurrentUserResponse(BaseModel):
    user_id: int
    login: str
    email: EmailStr
    role: RolaEnum
    dzial: DzialEnum
