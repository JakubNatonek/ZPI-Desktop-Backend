from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


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
    start_time: time
    end_time: time
    is_available: bool

    @field_validator("start_time", "end_time", mode="after")
    @classmethod
    def round_to_five_minutes(cls, value: time) -> time:
        total_seconds = value.hour * 3600 + value.minute * 60 + value.second
        rounded_seconds = int((total_seconds + 150) // 300) * 300
        if rounded_seconds >= 24 * 3600:
            rounded_seconds = 23 * 3600 + 55 * 60

        rounded_hour, remainder = divmod(rounded_seconds, 3600)
        rounded_minute, rounded_second = divmod(remainder, 60)
        return time(hour=rounded_hour, minute=rounded_minute, second=rounded_second)


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
    start_time: time
    end_time: time
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
    start_time: time
    end_time: time
    is_available: bool
    semestr: SemestrResponse

    class Config:
        from_attributes = True
