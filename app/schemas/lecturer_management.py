from pydantic import BaseModel, EmailStr, Field


class LecturerListItemResponse(BaseModel):
    user_id: int
    last_name: str
    first_name: str
    email: str
    title: str
    department_name: str
    is_blocked: bool


class LecturerBlockRequest(BaseModel):
    blocked: bool


class LecturerUpdateRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    title: str | None = None
    department_id: int | None = None
