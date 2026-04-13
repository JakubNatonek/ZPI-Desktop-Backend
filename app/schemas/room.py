from pydantic import BaseModel, Field


class RoomBase(BaseModel):
    room_number: str = Field(min_length=1, max_length=64)
    seats_count: int = Field(ge=1, le=1000)
    room_type_id: int = Field(ge=1)
    special_equipment: list[int] = Field(default_factory=list)
    activities: list[int] = Field(default_factory=list)
    departments: list[int] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "room_number": "1263",
                "seats_count": 30,
                "room_type_id": 1,
                "special_equipment": [1, 2, 3],
                "activities": [1, 2],
                "departments": [1, 2],
            }
        }
    }


class RoomCreate(RoomBase):
    pass


class RoomUpdate(RoomBase):
    pass


class RoomResponse(BaseModel):
    id: int
    room_number: str
    seats_count: int
    room_type_id: int | None = None
    room_type: str
    special_equipment: list[int]
    special_equipment_names: list[str] = Field(default_factory=list)
    activities: list[int]
    activity_names: list[str] = Field(default_factory=list)
    departments: list[int]
    department_names: list[str] = Field(default_factory=list)


class RoomListResponse(BaseModel):
    items: list[RoomResponse]
