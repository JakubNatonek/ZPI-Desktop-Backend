from pydantic import BaseModel, Field


class SubjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    activity_id: int = Field(ge=1)
    type_display: str | None = None
    room_properties: str | None = None
    blocked: bool = False
    periodic: bool = False


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(SubjectBase):
    pass


class SubjectResponse(BaseModel):
    id: int
    name: str
    type_id: int | None = None
    activity_id: int | None = None
    activity_name: str | None = None
    type_display: str | None = None
    room_properties: str | None = None
    blocked: bool
    periodic: bool


class SubjectListResponse(BaseModel):
    items: list[SubjectResponse]
