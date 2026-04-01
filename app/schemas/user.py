
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AdminUserCreate(BaseModel):
    """Data for creating a new user by admin."""
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    one_time_password: str = Field(min_length=8, max_length=128)
    role_id: int = Field(gt=0)
    department_id: int = Field(gt=0)


class UserCreatedResponse(BaseModel):
    """Response after user creation — contains generated login and password."""
    user_id: int
    album_number: str
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str  # role name
    department: str  # department name
    one_time_password: str


class AdminUserListResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    album_number: str
    login: str
    email: EmailStr
    role: str
    department: str
    must_change_password: bool


class AdminUserUpdate(BaseModel):
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    login: str = Field(min_length=3, max_length=64)
    email: EmailStr
    role_id: int = Field(gt=0)
    department_id: int = Field(gt=0)


class AdminResetOneTimePasswordRequest(BaseModel):
    one_time_password: str = Field(min_length=8, max_length=128)


class RoleOptionResponse(BaseModel):
    id: int
    name: str


class DepartmentOptionResponse(BaseModel):
    id: int
    name: str



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
