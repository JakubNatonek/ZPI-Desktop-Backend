from pydantic import BaseModel

class DepartmentCreate(BaseModel):
    name: str

class RoleCreate(BaseModel):
    name: str

class DepartmentResponse(BaseModel):
    id: int
    name: str

class RoleResponse(BaseModel):
    id: int
    name: str
