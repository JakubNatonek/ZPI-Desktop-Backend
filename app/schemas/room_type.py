from pydantic import BaseModel


class RoomTypeCreate(BaseModel):
    name: str
    abbreviation: str


class RoomTypeUpdate(BaseModel):
    name: str
    abbreviation: str


class RoomTypeResponse(BaseModel):
    id: int
    name: str
    abbreviation: str
