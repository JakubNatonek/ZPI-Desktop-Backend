
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AdminUserCreate(BaseModel):
    """Data for creating a new user by admin."""
    first_name: str
    last_name: str
    email: EmailStr
    role: str  # role name
    department: str  # department name


class UserCreatedResponse(BaseModel):
    """Response after user creation — contains generated login and password."""
    user_id: int
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str  # role name
    department: str  # department name
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
    """Current logged-in user data."""
    user_id: int
    login: str
    email: EmailStr
    role: str  # role name
    department: str  # department name



class UserNameResponse(BaseModel):
    """Basic user data for listing and editing."""
    user_id: int
    first_name: str
    last_name: str


class PublicKeyResponse(BaseModel):
    """Public key response for a user."""
    user_id: int
    public_key: Optional[str] = None


class PublicKeyUpdate(BaseModel):
    """Payload for updating a user's public key."""
    public_key: str
