from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class UnavailabilityNoteCreate(BaseModel):
    """Schema do tworzenia notatki o niedostępności."""
    start_date: date = Field(description="Data początkowa niedostępności")
    end_date: Optional[date] = Field(None, description="Data końcowa (nullable dla jednodniowych)")
    description: Optional[str] = Field(None, max_length=1000, description="Powód/opis niedostępności")
    note_type: str = Field(description="Typ notatki: 'request' lub 'forced'")

    @field_validator("note_type")
    @classmethod
    def validate_note_type(cls, v: str) -> str:
        if v not in ("request", "forced"):
            raise ValueError("note_type musi być 'request' lub 'forced'")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        start_date = info.data.get("start_date")
        if v and start_date and v < start_date:
            raise ValueError("end_date nie może być wcześniejsza niż start_date")
        return v


class UnavailabilityNoteUpdate(BaseModel):
    """Schema do aktualizacji statusu notatki (dostęp: Admin)."""
    status: str = Field(description="Nowy status: 'pending', 'accepted', 'rejected', 'acknowledged'")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = ("pending", "accepted", "rejected", "acknowledged")
        if v not in valid_statuses:
            raise ValueError(f"status musi być jednym z: {valid_statuses}")
        return v


class UnavailabilityNoteResponse(BaseModel):
    """Response schema dla notatki o niedostępności."""
    id: int
    user_id: int
    start_date: date
    end_date: Optional[date]
    description: Optional[str]
    note_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UnavailabilityNoteListResponse(BaseModel):
    """Response dla listy notatek z informacją o autorze."""
    id: int
    user_id: int
    first_name: str  # Imię autora
    last_name: str   # Nazwisko autora
    start_date: date
    end_date: Optional[date]
    description: Optional[str]
    note_type: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
