from pydantic import BaseModel, Field


class SpecializationCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=200)
    department_id: int


class SpecializationResponse(BaseModel):
    id: int
    code: str
    name: str
    department_id: int | None
    department_name: str
