from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


# Semestr schemas
class SemestrBase(BaseModel):
    data_rozpoczecia: date
    data_zakonczenia: date
    nazwa: str = Field(min_length=1, max_length=100)


class SemestrCreate(SemestrBase):
    pass


class SemestrResponse(SemestrBase):
    id: int

    class Config:
        from_attributes = True


class SemestrListResponse(BaseModel):
    items: List[SemestrResponse]


# Dezyderata schemas
class DezyderataEntryCreate(BaseModel):
    day_id: int = Field(ge=1, le=7)
    from_hour: int = Field(ge=0, le=23)
    to_hour: int = Field(ge=0, le=23)
    is_available: bool


class DezyderataCreate(BaseModel):
    data_od: date
    data_do: date
    semestr_id: int
    entries: List[DezyderataEntryCreate] = Field(default_factory=list)


class DezyderataResponse(BaseModel):
    id: int
    user_id: int
    data_od: date
    data_do: date
    semestr_id: int
    day_id: int
    from_hour: int
    to_hour: int
    is_available: bool
    day_name: Optional[str] = None
    semestr_nazwa: Optional[str] = None

    class Config:
        from_attributes = True


class DezyderataListResponse(BaseModel):
    items: List[DezyderataResponse]


class DezyderataWithSemestrResponse(BaseModel):
    id: int
    user_id: int
    data_od: date
    data_do: date
    semestr_id: int
    day_id: int
    from_hour: int
    to_hour: int
    is_available: bool
    semestr: SemestrResponse

    class Config:
        from_attributes = True
