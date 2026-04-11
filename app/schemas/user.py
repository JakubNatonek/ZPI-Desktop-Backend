
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AdminUserCreate(BaseModel):
    """Data for creating a new user by admin."""
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role_id: int = Field(gt=0)
    department_id: int = Field(gt=0)


class UserCreatedResponse(BaseModel):
    """Response after user creation."""
    user_id: int
    album_number: str
    login: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str  # role name
    department: str  # department name


class AdminUserListResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    album_number: str
    login: str
    email: str
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


class AdminResetPasswordRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)


class RoleOptionResponse(BaseModel):
    id: int
    name: str


class DepartmentOptionResponse(BaseModel):
    id: int
    name: str



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
class UserProfileResponse(BaseModel):
    """Profile data for the currently logged-in user."""
    status: str
    album_number: str
    year: str
    semester: str
    major: str
    faculty: str
    study_track: str
    study_mode: str
    title: str
    groups: list[str]
