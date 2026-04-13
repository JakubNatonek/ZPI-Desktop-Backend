from pydantic import BaseModel


class SpecialEquipmentCreate(BaseModel):
    name: str


class SpecialEquipmentUpdate(BaseModel):
    name: str


class SpecialEquipmentResponse(BaseModel):
    id: int
    name: str
