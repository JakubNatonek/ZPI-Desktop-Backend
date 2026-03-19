from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    room_number: str = Field(min_length=1, max_length=64)
    seats_count: int = Field(ge=1, le=1000)
    room_type: str = Field(min_length=1, max_length=64)
    special_equipment: str = Field(default="", max_length=4000)
    activities: list[str] = Field(default_factory=list)


class RoomCreate(RoomBase):
    pass


class RoomUpdate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int
    building: str


class RoomListResponse(BaseModel):
    items: list[RoomResponse]
