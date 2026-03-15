from pydantic import BaseModel, EmailStr, Field

from app.models.model_user import DzialEnum, RolaEnum


class AdminUserCreate(BaseModel):
    """Dane do utworzenia nowego użytkownika przez administratora."""

    imie: str = Field(description="Imię użytkownika")
    nazwisko: str = Field(description="Nazwisko użytkownika")
    email: EmailStr = Field(description="Adres e-mail użytkownika")
    rola: RolaEnum = Field(description="Rola użytkownika (wybierz z listy)")
    dzial: DzialEnum = Field(description="Dział użytkownika (wybierz z listy)")


class UserCreatedResponse(BaseModel):
    """Odpowiedź po utworzeniu użytkownika — zawiera wygenerowany login i hasło."""

    user_id: int
    login: str
    email: EmailStr
    imie: str
    nazwisko: str
    rola: RolaEnum
    dzial: DzialEnum
    one_time_password: str = Field(description="Jednorazowe hasło do pierwszego logowania")


class UserCredentialsResponse(BaseModel):
    """Dane logowania użytkownika (login + jednorazowe hasło)."""

    user_id: int
    login: str
    one_time_password: str | None = Field(description="Jednorazowe hasło (null jeśli już zmienione)")


class UserLogin(BaseModel):
    """Dane logowania — login i hasło."""

    login: str = Field(
        description="Login użytkownika (np. j.kowalski1234)",
        examples=["j.kowalski1234"],
    )
    password: str = Field(
        description="Hasło użytkownika",
        examples=["abc123"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "login": "j.kowalski1234",
                    "password": "abc123",
                }
            ]
        }
    }


class ChangePasswordRequest(BaseModel):
    """Dane do zmiany hasła użytkownika."""

    new_password: str = Field(min_length=6, description="Nowe hasło")
    confirm_new_password: str = Field(min_length=6, description="Potwierdzenie nowego hasła")


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
    access_token_expires_in: int = Field(description="Czas ważności tokenu w sekundach")
    must_change_password: bool = Field(description="Czy użytkownik musi zmienić hasło")


class CurrentUserResponse(BaseModel):
    """Dane aktualnie zalogowanego użytkownika."""

    user_id: int
    login: str
    email: EmailStr
    role: RolaEnum = Field(description="Rola użytkownika")
    dzial: DzialEnum = Field(description="Dział użytkownika")
