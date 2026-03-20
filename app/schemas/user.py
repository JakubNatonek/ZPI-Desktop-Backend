from pydantic import BaseModel, EmailStr, Field
from app.models.model_user import DzialEnum, RolaEnum


class AdminUserCreate(BaseModel):
    """Dane do utworzenia nowego użytkownika przez administratora."""

    imie: str 
    nazwisko: str 
    email: EmailStr 
    rola: RolaEnum 
    dzial: DzialEnum 


class UserCreatedResponse(BaseModel):
    """Odpowiedź po utworzeniu użytkownika — zawiera wygenerowany login i hasło."""

    user_id: int
    login: str
    email: EmailStr
    imie: str
    nazwisko: str
    rola: RolaEnum
    dzial: DzialEnum
    one_time_password: str 


class UserCredentialsResponse(BaseModel):
    """Dane logowania użytkownika (login + jednorazowe hasło)."""

    user_id: int
    login: str
    one_time_password: str 


class UserLogin(BaseModel):
    """Dane logowania — login i hasło."""

    login: str 
    password: str 


class ChangePasswordRequest(BaseModel):
    """Dane do zmiany hasła użytkownika."""

    new_password: str
    confirm_new_password: str


class ChangePasswordResponse(BaseModel):
    """Odpowiedź po zmianie hasła."""

    message: str


class AuthResponse(BaseModel):
    """Odpowiedź po zalogowaniu — token dostępu."""

    user_id: int
    login: str
    email: EmailStr
    access_token: str
    token_type: str = "bearer"
    access_token_expires_in: int
    must_change_password: bool


class CurrentUserResponse(BaseModel):
    """Dane aktualnie zalogowanego użytkownika."""

    user_id: int
    login: str
    email: EmailStr
    role: RolaEnum
    dzial: DzialEnum


class UserNameResponse(BaseModel):
    """Podstawowe dane użytkownika do listowania i edycji."""

    user_id: int
    imie: str
    nazwisko: str
