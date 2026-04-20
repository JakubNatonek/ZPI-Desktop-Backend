from pydantic import BaseModel, EmailStr, Field


class StudentListItemResponse(BaseModel):
    user_id: int
    last_name: str
    first_name: str
    album_number: str
    email: str
    studies_type: str
    average_grade: float
    department_name: str
    department_id: int | None = None
    specialization_name: str = ""
    specialization_id: int | None = None
    is_blocked: bool


class StudentBlockRequest(BaseModel):
    blocked: bool


class StudentUpdateRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    album_number: str = Field(min_length=1, max_length=10)
    department_id: int | None = None
    studies_type: str | None = None


class StudentBlockRequest(BaseModel):
    blocked: bool
