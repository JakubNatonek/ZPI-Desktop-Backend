from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    room_number: str = Field(min_length=1, max_length=64)
    seats_count: int = Field(ge=1, le=1000)
    room_type_id: int = Field(ge=1)
    special_equipment: str = Field(default="", max_length=4000)
    activities: list[int] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "room_number": "1263",
                "seats_count": 30,
                "room_type_id": 1,
                "special_equipment": "Projektor, ekran, nagłośnienie",
                "activities": [1, 2],
            }
        }
    }


class RoomCreate(RoomBase):
    pass


class RoomUpdate(RoomBase):
    pass


class RoomResponse(BaseModel):
    id: int
    building: str
    room_number: str
    seats_count: int
    room_type: str
    special_equipment: str
    activities: list[int]


class RoomListResponse(BaseModel):
    items: list[RoomResponse]
