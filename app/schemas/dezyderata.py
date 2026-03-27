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
class DezyderataBase(BaseModel):
    data_od: date
    data_do: date
    godziny: str  # JSON string z listą slotów, np. "2026-03-27-14,2026-03-27-15"
    semestr_id: int


class DezyderataCreate(DezyderataBase):
    pass


class DezyderataUpdate(DezyderataBase):
    pass


class DezyderataResponse(DezyderataBase):
    id: int
    user_id: int
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
    godziny: str
    semestr_id: int
    semestr: SemestrResponse

    class Config:
        from_attributes = True
