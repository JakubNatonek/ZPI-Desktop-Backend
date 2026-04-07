from pydantic import BaseModel

class DepartmentCreate(BaseModel):
    name: str
    abbreviation: str

class DepartmentResponse(BaseModel):
    id: int
    name: str
    abbreviation: str
