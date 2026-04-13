from pydantic import BaseModel


class ActivityCreate(BaseModel):
    name: str


class ActivityUpdate(BaseModel):
    name: str


class ActivityResponse(BaseModel):
    id: int
    name: str
